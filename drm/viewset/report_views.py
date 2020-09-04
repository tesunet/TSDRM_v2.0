# 统计相关：流程报告、任务报告
import pdfkit

from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404, HttpResponse, JsonResponse
from django.http import StreamingHttpResponse
from django.template.response import TemplateResponse

from ..tasks import *
from drm.api.commvault.RestApi import *
from .public_func import *
from .basic_views import getpagefuns


def custom_pdf_report(request):
    """
    pip3 install pdfkit
    wkhtmltopdf安装文件已经在项目中static/pages/process
    """
    if request.user.is_authenticated():
        processrun_id = request.GET.get("processrunid", "")
        process_id = request.GET.get("processid", "")

        # 构造数据
        # 1.获取当前流程对象
        process_run_objs = ProcessRun.objects.filter(id=processrun_id)
        if process_run_objs:
            process_run_obj = process_run_objs[0]
        else:
            raise Http404()

        # 2.报表封页文字
        title_xml = "Oracle自动化恢复流程"
        abstract_xml = "恢复报告"

        # 3.章节名称
        ele_xml01 = "一、切换概述"
        ele_xml02 = "二、步骤详情"

        # 4.构造第一章数据: first_el_dict
        # 切换概述节点下内容,有序字典中存放
        first_el_dict = {}

        start_time = process_run_obj.starttime
        end_time = process_run_obj.endtime
        create_user = process_run_obj.creatuser
        users = User.objects.filter(username=create_user)
        if users:
            create_user = users[0].userinfo.fullname
        else:
            create_user = ""
        run_reason = process_run_obj.run_reason

        first_el_dict["start_time"] = r"{0}".format(
            start_time.strftime("%Y-%m-%d %H:%M:%S") if start_time else "")
        first_el_dict["end_time"] = r"{0}".format(
            end_time.strftime("%Y-%m-%d %H:%M:%S") if end_time else "")

        step_rto = get_process_run_rto(process_run_obj)

        m, s = divmod(step_rto, 60)
        h, m = divmod(m, 60)
        first_el_dict["rto"] = "%d时%02d分%02d秒" % (h, m, s)

        first_el_dict["create_user"] = r"{0}".format(create_user)

        task_sign_obj = ProcessTask.objects.filter(processrun_id=processrun_id).exclude(state="9").filter(
            type="SIGN")

        if task_sign_obj:
            receiveusers = ""
            for task in task_sign_obj:
                receiveuser = task.receiveuser

                users = User.objects.filter(username=receiveuser)
                if users:
                    receiveuser = users[0].userinfo.fullname

                if receiveuser:
                    receiveusers += receiveuser + "、"

            first_el_dict["receiveuser"] = r"{0}".format(receiveusers[:-1])

        all_steprun_objs = StepRun.objects.filter(processrun_id=processrun_id)
        operators = ""
        for steprun_obj in all_steprun_objs:
            if steprun_obj.operator:
                if steprun_obj.operator not in operators:
                    users = User.objects.filter(username=steprun_obj.operator)
                    if users:
                        operator = users[0].userinfo.fullname
                        if operator:
                            if operator not in operators:
                                operators += operator + "、"

        first_el_dict["operator"] = r"{0}".format(operators[:-1])
        first_el_dict["run_reason"] = r"{0}".format(run_reason)

        # 构造第二章数据: step_info_list
        step_info_list = []
        pnode_steplist = Step.objects.exclude(state="9").filter(process_id=process_id).order_by("sort").filter(
            pnode_id=None)
        for num, pstep in enumerate(pnode_steplist):
            second_el_dict = dict()
            step_name = "{0}.{1}".format(num + 1, pstep.name)
            second_el_dict["step_name"] = step_name

            pnode_steprun = StepRun.objects.exclude(state="9").filter(processrun_id=processrun_id).filter(
                step=pstep)
            if pnode_steprun:
                pnode_steprun = pnode_steprun[0]
                if pnode_steprun.step.rto_count_in == "0":
                    second_el_dict["start_time"] = ""
                    second_el_dict["end_time"] = ""
                    second_el_dict["rto"] = ""
                else:
                    second_el_dict["start_time"] = pnode_steprun.starttime.strftime("%Y-%m-%d %H:%M:%S") if \
                        pnode_steprun.starttime else ""
                    second_el_dict["end_time"] = pnode_steprun.endtime.strftime(
                        "%Y-%m-%d %H:%M:%S") if pnode_steprun.endtime else ""

                    if pnode_steprun.endtime and pnode_steprun.starttime:
                        end_time = pnode_steprun.endtime.strftime("%Y-%m-%d %H:%M:%S")
                        start_time = pnode_steprun.starttime.strftime("%Y-%m-%d %H:%M:%S")
                        delta_seconds = datetime.datetime.strptime(end_time,
                                                                   '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(
                            start_time, '%Y-%m-%d %H:%M:%S')
                        hour, minute, second = str(delta_seconds).split(":")

                        delta_time = "{0}时{1}分{2}秒".format(hour, minute, second)

                        second_el_dict["rto"] = delta_time
                    else:
                        second_el_dict["rto"] = ""

            # 步骤负责人
            try:
                users = User.objects.filter(username=pnode_steprun.operator)
            except:
                if users:
                    operator = users[0].userinfo.fullname
                    second_el_dict["operator"] = operator
                else:
                    second_el_dict["operator"] = ""

            # 当前步骤下脚本
            state_dict = {
                "DONE": "已完成",
                "EDIT": "未执行",
                "RUN": "执行中",
                "ERROR": "执行失败",
                "IGNORE": "忽略",
                "": "",
            }

            current_scripts = Script.objects.exclude(state="9").filter(step_id=pstep.id).order_by("sort")
            script_list_wrapper = []
            if current_scripts:
                for snum, current_script in enumerate(current_scripts):
                    script_el_dict = dict()
                    # title
                    script_name = "{0}.{1}".format("i" * (snum + 1), current_script.name)
                    script_el_dict["script_name"] = script_name
                    # content
                    steprun_id = pnode_steprun.id if pnode_steprun else None
                    script_id = current_script.id
                    current_scriptrun_obj = ScriptRun.objects.filter(steprun_id=steprun_id, script_id=script_id)
                    if current_scriptrun_obj:
                        current_scriptrun_obj = current_scriptrun_obj[0]
                        script_el_dict["start_time"] = current_scriptrun_obj.starttime.strftime(
                            "%Y-%m-%d %H:%M:%S") if current_scriptrun_obj.starttime else ""
                        script_el_dict["end_time"] = current_scriptrun_obj.endtime.strftime(
                            "%Y-%m-%d %H:%M:%S") if current_scriptrun_obj.endtime else ""

                        if current_scriptrun_obj.endtime and current_scriptrun_obj.starttime:
                            end_time = current_scriptrun_obj.endtime.strftime("%Y-%m-%d %H:%M:%S")
                            start_time = current_scriptrun_obj.starttime.strftime("%Y-%m-%d %H:%M:%S")
                            delta_seconds = datetime.datetime.strptime(end_time,
                                                                       '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(
                                start_time, '%Y-%m-%d %H:%M:%S')
                            hour, minute, second = str(delta_seconds).split(":")

                            delta_time = "{0}时{1}分{2}秒".format(hour, minute, second)

                            script_el_dict["rto"] = delta_time
                        else:
                            script_el_dict["rto"] = ""

                        state = current_scriptrun_obj.state
                        if state in state_dict.keys():
                            script_el_dict["state"] = state_dict[state]
                        else:
                            script_el_dict["state"] = ""
                        script_el_dict["explain"] = current_scriptrun_obj.explain

                    script_list_wrapper.append(script_el_dict)
                second_el_dict["script_list_wrapper"] = script_list_wrapper

            # 子步骤下相关内容
            p_id = pstep.id
            inner_steps = Step.objects.exclude(state="9").filter(process_id=process_id).order_by("sort").filter(
                pnode_id=p_id)

            inner_step_list = []
            if inner_steps:
                for num, step in enumerate(inner_steps):
                    inner_second_el_dict = dict()
                    step_name = "{0}){1}".format(num + 1, step.name)
                    inner_second_el_dict["step_name"] = step_name
                    steprun_obj = StepRun.objects.exclude(state="9").filter(processrun_id=processrun_id).filter(
                        step=step)
                    if steprun_obj:
                        steprun_obj = steprun_obj[0]
                        if steprun_obj.step.rto_count_in == "0":
                            inner_second_el_dict["start_time"] = ""
                            inner_second_el_dict["end_time"] = ""
                            inner_second_el_dict["rto"] = ""
                        else:
                            inner_second_el_dict["start_time"] = steprun_obj.starttime.strftime("%Y-%m-%d %H:%M:%S") if \
                                steprun_obj.starttime else ""
                            inner_second_el_dict["end_time"] = steprun_obj.endtime.strftime(
                                "%Y-%m-%d %H:%M:%S") if steprun_obj.endtime else ""

                            if steprun_obj.endtime and steprun_obj.starttime:
                                end_time = steprun_obj.endtime.strftime("%Y-%m-%d %H:%M:%S")
                                start_time = steprun_obj.starttime.strftime("%Y-%m-%d %H:%M:%S")
                                delta_seconds = datetime.datetime.strptime(end_time,
                                                                           '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(
                                    start_time, '%Y-%m-%d %H:%M:%S')
                                hour, minute, second = str(delta_seconds).split(":")

                                delta_time = "{0}时{1}分{2}秒".format(hour, minute, second)

                                inner_second_el_dict["rto"] = delta_time
                            else:
                                inner_second_el_dict["rto"] = ""

                        # 步骤负责人
                        users = User.objects.filter(username=steprun_obj.operator)
                        if users:
                            operator = users[0].userinfo.fullname
                            inner_second_el_dict["operator"] = operator
                        else:
                            inner_second_el_dict["operator"] = ""

                        # 当前步骤下脚本
                        current_scripts = Script.objects.exclude(state="9").filter(step_id=step.id).order_by("sort")

                        script_list_inner = []
                        if current_scripts:
                            for snum, current_script in enumerate(current_scripts):
                                script_el_dict_inner = dict()
                                # title
                                script_name = "{0}.{1}".format("i" * (snum + 1), current_script.name)
                                script_el_dict_inner["script_name"] = script_name

                                # content
                                steprun_id = steprun_obj.id
                                script_id = current_script.id
                                current_scriptrun_obj = ScriptRun.objects.filter(steprun_id=steprun_id,
                                                                                 script_id=script_id)
                                if current_scriptrun_obj:
                                    current_scriptrun_obj = current_scriptrun_obj[0]
                                    script_el_dict_inner["start_time"] = current_scriptrun_obj.starttime.strftime(
                                        "%Y-%m-%d %H:%M:%S") if current_scriptrun_obj.starttime else ""
                                    script_el_dict_inner["end_time"] = current_scriptrun_obj.endtime.strftime(
                                        "%Y-%m-%d %H:%M:%S") if current_scriptrun_obj.endtime else ""

                                    if current_scriptrun_obj.endtime and current_scriptrun_obj.starttime:
                                        end_time = current_scriptrun_obj.endtime.strftime("%Y-%m-%d %H:%M:%S")
                                        start_time = current_scriptrun_obj.starttime.strftime("%Y-%m-%d %H:%M:%S")
                                        delta_seconds = datetime.datetime.strptime(end_time,
                                                                                   '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(
                                            start_time, '%Y-%m-%d %H:%M:%S')
                                        hour, minute, second = str(delta_seconds).split(":")

                                        delta_time = "{0}时{1}分{2}秒".format(hour, minute, second)

                                        script_el_dict_inner["rto"] = delta_time
                                    else:
                                        script_el_dict_inner["rto"] = ""

                                    state = current_scriptrun_obj.state
                                    if state in state_dict.keys():
                                        script_el_dict_inner["state"] = state_dict[state]
                                    else:
                                        script_el_dict_inner["state"] = ""

                                    script_el_dict_inner["explain"] = current_scriptrun_obj.explain
                                else:
                                    pass
                                script_list_inner.append(script_el_dict_inner)
                        inner_second_el_dict["script_list_inner"] = script_list_inner
                    inner_step_list.append(inner_second_el_dict)
            second_el_dict['inner_step_list'] = inner_step_list
            step_info_list.append(second_el_dict)
        t = TemplateResponse(request, 'pdf.html',
                             {"step_info_list": step_info_list, "first_el_dict": first_el_dict, "ele_xml01": ele_xml01,
                              "ele_xml02": ele_xml02, "title_xml": title_xml, "abstract_xml": abstract_xml})
        t.render()
        current_path = os.getcwd()

        if sys.platform.startswith("win"):
            # 指定wkhtmltopdf运行程序路径
            wkhtmltopdf_path = current_path + os.sep + "drm" + os.sep + "static" + os.sep + "pages" + os.sep + "process" + os.sep + "wkhtmltopdf" + os.sep + "bin" + os.sep + "wkhtmltopdf.exe"
            config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
        else:
            config = None

        options = {
            'page-size': 'A3',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'no-outline': None
        }
        css_path = current_path + os.sep + "drm" + os.sep + "static" + os.sep + "assets" + os.sep + "global" + os.sep + "css" + os.sep + "bootstrap.css"
        css = [r"{0}".format(css_path)]

        pdfkit.from_string(t.content.decode(encoding="utf-8"), r"oracle.pdf", configuration=config,
                           options=options, css=css)

        the_file_name = "oracle.pdf"
        response = StreamingHttpResponse(file_iterator(the_file_name))
        response['Content-Type'] = 'application/octet-stream; charset=unicode'
        response['Content-Disposition'] = 'attachment;filename="{0}"'.format(the_file_name)
        return response


def restore_search(request, funid):
    if request.user.is_authenticated():
        runstate = request.GET.get("runstate", "")

        nowtime = datetime.datetime.now()
        endtime = nowtime.strftime("%Y-%m-%d")
        starttime = (nowtime - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
        all_processes = Process.objects.exclude(state="9").exclude(Q(type=None) | Q(type="")| Q(type="NODE")).filter(processtype="1").order_by("sort")
        processname_list = []
        for process in all_processes:
            processname_list.append(process.name)

        state_dict = {
            "DONE": "已完成",
            "EDIT": "未执行",
            "RUN": "执行中",
            "ERROR": "执行失败",
            "IGNORE": "忽略",
            "STOP": "终止",
            "PLAN": "计划",
            "SIGN": "签到",
        }
        return render(request, "restore_search.html",
                      {'username': request.user.userinfo.fullname, "starttime": starttime, "endtime": endtime,
                       "processname_list": processname_list, "state_dict": state_dict, "runstate": runstate,
                       "pagefuns": getpagefuns(funid, request=request)})
    else:
        return HttpResponseRedirect("/login")


def restore_search_data(request):
    """
    :param request: starttime, endtime, runperson, runstate
    :return: starttime,endtime,createuser,state,process_id,processrun_id,runreason
    """
    if request.user.is_authenticated():
        result = []
        referer = request.GET.get('referer', '')
        processname = request.GET.get('processname', '')
        runperson = request.GET.get('runperson', '')
        runstate = request.GET.get('runstate', '')
        startdate = request.GET.get('startdate', '')
        enddate = request.GET.get('enddate', '')
        start_time = datetime.datetime.strptime(startdate, '%Y-%m-%d').strftime('%Y-%m-%d %H:%M:%S')
        end_time = (datetime.datetime.strptime(enddate, '%Y-%m-%d') + datetime.timedelta(days=1) - datetime.timedelta(
            seconds=1)).strftime('%Y-%m-%d %H:%M:%S')

        cursor = connection.cursor()

        exec_sql = """
        select r.starttime, r.endtime, r.creatuser, r.state, r.process_id, r.id, r.run_reason, p.name, p.url from drm_processrun as r 
        left join drm_process as p on p.id = r.process_id where r.state != '9' and r.state!='REJECT' and r.starttime between '{0}' and '{1}' order by r.starttime desc;
        """.format(start_time, end_time)

        if runperson:
            user_info = UserInfo.objects.filter(fullname=runperson)
            if user_info:
                user_info = user_info[0]
                runperson = user_info.user.username
            else:
                runperson = ""

            if processname != "" and runstate != "":
                exec_sql = """
                select r.starttime, r.endtime, r.creatuser, r.state, r.process_id, r.id, r.run_reason, p.name, p.url from drm_processrun as r 
                left join drm_process as p on p.id = r.process_id where r.state != '9' and r.state!='REJECT' and p.name='{0}' and r.state='{1}' and r.creatuser='{2}' and r.starttime between '{3}' and '{4}'  order by r.starttime desc;
                """.format(processname, runstate, runperson, start_time, end_time)

            if processname == "" and runstate != "":
                exec_sql = """
                select r.starttime, r.endtime, r.creatuser, r.state, r.process_id, r.id, r.run_reason, p.name, p.url from drm_processrun as r 
                left join drm_process as p on p.id = r.process_id where r.state != '9' and r.state!='REJECT' and r.state='{0}' and r.creatuser='{1}' and r.starttime between '{2}' and '{3}'  order by r.starttime desc;
                """.format(runstate, runperson, start_time, end_time)

            if processname != "" and runstate == "":
                exec_sql = """
                select r.starttime, r.endtime, r.creatuser, r.state, r.process_id, r.id, r.run_reason, p.name, p.url from drm_processrun as r 
                left join drm_process as p on p.id = r.process_id where r.state != '9' and r.state!='REJECT' and p.name='{0}' and r.creatuser='{1}' and r.starttime between '{2}' and '{3}'  order by r.starttime desc;
                """.format(processname, runperson, start_time, end_time)
            if processname == "" and runstate == "":
                exec_sql = """
                select r.starttime, r.endtime, r.creatuser, r.state, r.process_id, r.id, r.run_reason, p.name, p.url from drm_processrun as r 
                left join drm_process as p on p.id = r.process_id where r.state != '9' and r.state!='REJECT' and r.creatuser='{0}' and r.starttime between '{1}' and '{2}'  order by r.starttime desc;
                """.format(runperson, start_time, end_time)

        else:
            if processname != "" and runstate != "":
                exec_sql = """
                select r.starttime, r.endtime, r.creatuser, r.state, r.process_id, r.id, r.run_reason, p.name, p.url from drm_processrun as r 
                left join drm_process as p on p.id = r.process_id where r.state != '9' and r.state!='REJECT' and p.name='{0}' and r.state='{1}' and r.starttime between '{2}' and '{3}'  order by r.starttime desc;
                """.format(processname, runstate, start_time, end_time)

            if processname == "" and runstate != "":
                if referer == "monitor" and runstate == "ERROR":
                    exec_sql = """
                        select r.starttime, r.endtime, r.creatuser, r.state, r.process_id, r.id, r.run_reason, p.name, p.url from drm_processrun as r 
                        left join drm_process as p on p.id = r.process_id where r.state != '9' and r.state!='REJECT' and r.state='ERROR' or r.state='STOP' and r.starttime between '{0}' and '{1}'  order by r.starttime desc;
                        """.format(start_time, end_time)
                else:
                    exec_sql = """
                        select r.starttime, r.endtime, r.creatuser, r.state, r.process_id, r.id, r.run_reason, p.name, p.url from drm_processrun as r 
                        left join drm_process as p on p.id = r.process_id where r.state != '9' and r.state!='REJECT' and r.state='{0}' and r.starttime between '{1}' and '{2}'  order by r.starttime desc;
                        """.format(runstate, start_time, end_time)

            if processname != "" and runstate == "":
                exec_sql = """
                    select r.starttime, r.endtime, r.creatuser, r.state, r.process_id, r.id, r.run_reason, p.name, p.url from drm_processrun as r 
                    left join drm_process as p on p.id = r.process_id where r.state != '9' and r.state!='REJECT' and p.name='{0}' and r.starttime between '{1}' and '{2}'  order by r.starttime desc;
                    """.format(processname, start_time, end_time)

        state_dict = {
            "DONE": "已完成",
            "EDIT": "未执行",
            "RUN": "执行中",
            "ERROR": "执行失败",
            "IGNORE": "忽略",
            "STOP": "终止",
            "PLAN": "计划",
            "REJECT": "取消",
            "SIGN": "签到",
            "": "",
        }
        cursor.execute(exec_sql)
        rows = cursor.fetchall()

        for processrun_obj in rows:
            create_users = processrun_obj[2] if processrun_obj[2] else ""
            create_user_objs = User.objects.filter(username=create_users)
            create_user_fullname = create_user_objs[0].userinfo.fullname if create_user_objs else ""

            result.append({
                "starttime": processrun_obj[0].strftime('%Y-%m-%d %H:%M:%S') if processrun_obj[0] else "",
                "endtime": processrun_obj[1].strftime('%Y-%m-%d %H:%M:%S') if processrun_obj[1] else "",
                "createuser": create_user_fullname,
                "state": state_dict["{0}".format(processrun_obj[3])] if processrun_obj[3] else "",
                "process_id": processrun_obj[4] if processrun_obj[4] else "",
                "processrun_id": processrun_obj[5] if processrun_obj[5] else "",
                "run_reason": processrun_obj[6][:20] if processrun_obj[6] else "",
                "process_name": processrun_obj[7] if processrun_obj[7] else "",
                "process_url": processrun_obj[8] if processrun_obj[8] else ""
            })
        return HttpResponse(json.dumps({"data": result}))


def tasksearch(request, funid):
    if request.user.is_authenticated():
        nowtime = datetime.datetime.now()
        endtime = nowtime.strftime("%Y-%m-%d")
        starttime = (nowtime - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
        all_processes = Process.objects.exclude(state="9").exclude(Q(type=None) | Q(type="")| Q(type="NODE")).filter(processtype="1")
        processname_list = []
        for process in all_processes:
            processname_list.append(process.name)

        return render(request, "tasksearch.html",
                      {'username': request.user.userinfo.fullname, "starttime": starttime, "endtime": endtime,
                       "processname_list": processname_list, "pagefuns": getpagefuns(funid, request=request)})
    else:
        return HttpResponseRedirect("/login")


def tasksearchdata(request):
    if request.user.is_authenticated():
        result = []
        task_type = request.GET.get('task_type', '')
        has_finished = request.GET.get('has_finished', '')
        startdate = request.GET.get('startdate', '')
        enddate = request.GET.get('enddate', '')
        start_time = datetime.datetime.strptime(startdate, '%Y-%m-%d').strftime('%Y-%m-%d %H:%M:%S')
        end_time = (datetime.datetime.strptime(enddate, '%Y-%m-%d') + datetime.timedelta(days=1) - datetime.timedelta(
            seconds=1)).strftime('%Y-%m-%d %H:%M:%S')

        cursor = connection.cursor()
        exec_sql = """
        select t.id, t.content, t.starttime, t.endtime, t.type, t.processrun_id, p.name, p.url, t.state from drm_processtask as t 
        left join drm_processrun as r on t.processrun_id = r.id left join drm_process as p on p.id = r.process_id where t.type!='INFO' and r.state!='9' and t.starttime between '{0}' and '{1}' order by t.starttime desc;
        """.format(start_time, end_time)

        if task_type != "" and has_finished != "":
            exec_sql = """
            select t.id, t.content, t.starttime, t.endtime, t.type, t.processrun_id, p.name, p.url, t.state from drm_processtask as t 
            left join drm_processrun as r on t.processrun_id = r.id left join drm_process as p on p.id = r.process_id where t.type='{0}' and r.state!='9' and t.state='{1}' and t.starttime between '{2}' and '{3}' order by t.starttime desc;
            """.format(task_type, has_finished, start_time, end_time)

        if task_type == "" and has_finished != "":
            exec_sql = """
            select t.id, t.content, t.starttime, t.endtime, t.type, t.processrun_id, p.name, p.url, t.state from drm_processtask as t 
            left join drm_processrun as r on t.processrun_id = r.id left join drm_process as p on p.id = r.process_id where  t.type!='INFO' and r.state!='9' and t.state='{0}' and t.starttime between '{1}' and '{2}' order by t.starttime desc;
            """.format(has_finished, start_time, end_time)

        if task_type != "" and has_finished == "":
            exec_sql = """
            select t.id, t.content, t.starttime, t.endtime, t.type, t.processrun_id, p.name, p.url, t.state from drm_processtask as t 
            left join drm_processrun as r on t.processrun_id = r.id left join drm_process as p on p.id = r.process_id where t.type='{0}' and r.state!='9' and t.starttime between '{1}' and '{2}' order by t.starttime desc;
            """.format(task_type, start_time, end_time)

        cursor.execute(exec_sql)
        rows = cursor.fetchall()
        type_dict = {
            "SIGN": "签到",
            "RUN": "操作",
            "ERROR": "错误",
            "": "",
        }

        has_finished_dict = {
            "1": "完成",
            "0": "未完成"
        }
        for task in rows:
            result.append({
                "task_id": task[0],
                "task_content": task[1],
                "starttime": task[2].strftime('%Y-%m-%d %H:%M:%S') if task[2] else "",
                "endtime": task[3].strftime('%Y-%m-%d %H:%M:%S') if task[3] else "",
                "type": type_dict["{0}".format(task[4])] if task[4] in type_dict.keys() else "",
                "processrun_id": task[5] if task[5] else "",
                "process_name": task[6] if task[6] else "",
                "process_url": task[7] if task[7] else "",
                "has_finished": has_finished_dict[
                    "{0}".format(task[8])] if task[8] in has_finished_dict.keys() else "",
            })
        return JsonResponse({"data": result})
