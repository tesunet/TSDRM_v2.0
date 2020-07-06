# 流程监控：流程启动、所有大屏、管理员界面、计划流程、邀请函
import uuid
import pdfkit

from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404, HttpResponse, JsonResponse
from django.http import StreamingHttpResponse
from django.template.response import TemplateResponse
from djcelery.models import CrontabSchedule, PeriodicTask

from ..tasks import *
from ..remote import ServerByPara
from drm.api.commvault.RestApi import *
from .public_func import *
from .basic_views import getpagefuns


######################
# 流程启动、所有大屏、管理员界面
######################
def oracle_restore(request, process_id):
    if request.user.is_authenticated():
        all_wrapper_steps = Step.objects.exclude(state="9").filter(process_id=process_id, pnode_id=None).order_by(
            "sort").prefetch_related("script_set", "verifyitems_set")
        wrapper_step_list = []
        num_to_char_choices = {
            "1": "一",
            "2": "二",
            "3": "三",
            "4": "四",
            "5": "五",
            "6": "六",
            "7": "七",
            "8": "八",
            "9": "九",
        }
        for num, wrapper_step in enumerate(all_wrapper_steps):
            wrapper_step_dict = {}
            wrapper_step_dict["wrapper_step_name"] = num_to_char_choices[
                                                         "{0}".format(str(num + 1))] + "." + wrapper_step.name
            wrapper_step_group_id = wrapper_step.group
            try:
                wrapper_step_group_id = int(wrapper_step_group_id)
            except:
                wrapper_step_group_id = None
            wrapper_step_group = Group.objects.filter(id=wrapper_step_group_id)
            if wrapper_step_group:
                wrapper_step_group_name = wrapper_step_group[0].name
            else:
                wrapper_step_group_name = ""
            wrapper_step_dict["wrapper_step_group_name"] = wrapper_step_group_name

            wrapper_script_list = []
            all_wrapper_scripts = wrapper_step.script_set.exclude(state="9").order_by("sort")
            for wrapper_script in all_wrapper_scripts:
                wrapper_script_dict = {
                    "wrapper_script_name": wrapper_script.name
                }
                wrapper_script_list.append(wrapper_script_dict)
                wrapper_step_dict["wrapper_script_list"] = wrapper_script_list

            wrapper_verify_list = []
            all_wrapper_verifys = wrapper_step.verifyitems_set.exclude(state="9")
            for wrapper_verify in all_wrapper_verifys:
                wrapper_verify_dict = {
                    "wrapper_verify_name": wrapper_verify.name
                }
                wrapper_verify_list.append(wrapper_verify_dict)
                wrapper_step_dict["wrapper_verify_list"] = wrapper_verify_list

            pnode_id = wrapper_step.id
            inner_step_list = []
            all_inner_steps = Step.objects.exclude(state="9").filter(process_id=process_id, pnode_id=pnode_id).order_by(
                "sort").prefetch_related("script_set", "verifyitems_set")
            for inner_step in all_inner_steps:
                inner_step_dict = {}
                inner_step_dict["inner_step_name"] = inner_step.name

                inner_step_group_id = inner_step.group
                try:
                    inner_step_group_id = int(inner_step_group_id)
                except:
                    inner_step_group_id = None
                inner_step_group = Group.objects.filter(id=inner_step_group_id)
                if inner_step_group:
                    inner_step_group_name = inner_step_group[0].name
                else:
                    inner_step_group_name = ""
                inner_step_dict["inner_step_group_name"] = inner_step_group_name

                inner_script_list = []
                all_inner_scripts = inner_step.script_set.exclude(state="9").order_by("sort")
                for inner_script in all_inner_scripts:
                    inner_script_dict = {
                        "inner_script_name": inner_script.name
                    }
                    inner_script_list.append(inner_script_dict)

                inner_verify_list = []
                all_inner_verifys = inner_step.verifyitems_set.exclude(state="9")
                for inner_verify in all_inner_verifys:
                    inner_verify_dict = {
                        "inner_verify_name": inner_verify.name
                    }
                    inner_verify_list.append(inner_verify_dict)

                inner_step_dict["inner_verify_list"] = inner_verify_list
                inner_step_dict["inner_script_list"] = inner_script_list
                inner_step_list.append(inner_step_dict)

            wrapper_step_dict["inner_step_list"] = inner_step_list

            wrapper_step_list.append(wrapper_step_dict)

        # 计划流程
        plan_process_run = ProcessRun.objects.filter(process_id=process_id, state="PLAN")
        if plan_process_run:
            plan_process_run = plan_process_run[0]
            plan_process_run_id = plan_process_run.id
        else:
            plan_process_run_id = ""

        # 根据url寻找到funid
        oracle_restore_url = "/oracle_restore/{0}".format(process_id)

        c_fun = Fun.objects.filter(url=oracle_restore_url)
        if c_fun.exists():
            c_fun = c_fun[0]
            funid = str(c_fun.id)
        else:
            return Http404()

        # commvault目标客户端
        all_targets = Target.objects.exclude(state="9")

        # commvault源客户端
        all_steps = Step.objects.exclude(state="9").filter(process_id=process_id).prefetch_related(
            "script_set", "script_set__origin", "script_set__origin__target")

        target_id = ""
        origin = ""
        data_path = ""
        copy_priority = ""
        db_open = ""
        for cur_step in all_steps:
            # all_scripts = Script.objects.filter(step_id=cur_step.id).exclude(state="9").select_related("origin")
            all_scripts = cur_step.script_set.exclude(state="9")
            for cur_script in all_scripts:
                if cur_script.origin:
                    origin = cur_script.origin
                    target_id = cur_script.origin.target.id
                    data_path = cur_script.origin.data_path
                    copy_priority = cur_script.origin.copy_priority
                    db_open = cur_script.origin.db_open
                    break
        return render(request, 'oracle_restore.html',
                      {'username': request.user.userinfo.fullname, "pagefuns": getpagefuns(funid, request=request),
                       "wrapper_step_list": wrapper_step_list, "process_id": process_id, "data_path": data_path,
                       "plan_process_run_id": plan_process_run_id, "all_targets": all_targets, "origin": origin,
                       "target_id": target_id, "copy_priority": copy_priority, "db_open": db_open})
    else:
        return HttpResponseRedirect("/login")


def oracle_restore_data(request):
    if request.user.is_authenticated():
        result = []
        process_id = request.GET.get("process_id", "")
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

        cursor = connection.cursor()

        exec_sql = """
        select r.starttime, r.endtime, r.creatuser, r.state, r.process_id, r.id, r.run_reason, p.name, p.url, p.type from drm_processrun as r 
        left join drm_process as p on p.id = r.process_id where r.state != '9' and r.state != 'REJECT' and r.process_id = {0} order by r.starttime desc;
        """.format(process_id)

        cursor.execute(exec_sql)
        rows = cursor.fetchall()
        for processrun_obj in rows:
            if processrun_obj[9] == "cv_oracle":
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

        return JsonResponse({"data": result})


def cv_oracle_run(request):
    if request.user.is_authenticated():
        result = {}
        processid = request.POST.get('processid', '')
        run_person = request.POST.get('run_person', '')
        run_time = request.POST.get('run_time', '')
        run_reason = request.POST.get('run_reason', '')

        target = request.POST.get('target', '')
        recovery_time = request.POST.get('recovery_time', '')
        browseJobId = request.POST.get('browseJobId', '')
        data_path = request.POST.get('data_path', '')
        copy_priority = request.POST.get('copy_priority', '')
        db_open = request.POST.get('db_open', '')

        origin = request.POST.get('origin', '')

        try:
            copy_priority = int(copy_priority)
        except ValueError as e:
            copy_priority = 1
        try:
            db_open = int(db_open)
        except ValueError as e:
            db_open = 1

        try:
            processid = int(processid)
        except:
            return JsonResponse({"res": "当前流程不存在。"})

        # if not data_path.strip():
        #     return JsonResponse({"res": "数据文件重定向路径不能为空。"})

        if not origin.strip():
            return JsonResponse({"res": "流程步骤中未添加Commvault接口，导致源客户端未空。"})

        try:
            target = int(target)
        except:
            return JsonResponse({"res": "目标客户端未选择。"})

        process = Process.objects.filter(id=processid).exclude(state="9").filter(type="cv_oracle")
        if (len(process) <= 0):
            result["res"] = '流程启动失败，该流程不存在。'
        else:
            running_process = ProcessRun.objects.filter(process=process[0], state__in=["RUN", "ERROR"])
            if (len(running_process) > 0):
                result["res"] = '流程启动失败，该流程正在进行中，请勿重复启动。'
            else:
                planning_process = ProcessRun.objects.filter(process=process[0], state="PLAN")
                if (len(planning_process) > 0):
                    result["res"] = '流程启动失败，计划流程未执行，务必先完成计划流程。'
                else:
                    myprocessrun = ProcessRun()
                    myprocessrun.process = process[0]
                    myprocessrun.starttime = datetime.datetime.now()
                    myprocessrun.creatuser = request.user.username
                    myprocessrun.run_reason = run_reason
                    myprocessrun.state = "RUN"
                    myprocessrun.target_id = target
                    myprocessrun.browse_job_id = browseJobId
                    myprocessrun.data_path = data_path
                    myprocessrun.copy_priority = copy_priority
                    myprocessrun.db_open = db_open
                    myprocessrun.origin = origin
                    myprocessrun.recover_time = datetime.datetime.strptime(recovery_time,
                                                                           "%Y-%m-%d %H:%M:%S") if recovery_time else None

                    myprocessrun.save()
                    mystep = process[0].step_set.exclude(state="9").order_by("sort")
                    if (len(mystep) <= 0):
                        result["res"] = '流程启动失败，没有找到可用步骤。'
                    else:
                        for step in mystep:
                            mysteprun = StepRun()
                            mysteprun.step = step
                            mysteprun.processrun = myprocessrun
                            mysteprun.state = "EDIT"
                            mysteprun.save()

                            myscript = step.script_set.exclude(state="9").order_by("sort")
                            for script in myscript:
                                myscriptrun = ScriptRun()
                                myscriptrun.script = script
                                myscriptrun.steprun = mysteprun
                                myscriptrun.state = "EDIT"
                                myscriptrun.save()

                            myverifyitems = step.verifyitems_set.exclude(state="9")
                            for verifyitems in myverifyitems:
                                myverifyitemsrun = VerifyItemsRun()
                                myverifyitemsrun.verify_items = verifyitems
                                myverifyitemsrun.steprun = mysteprun
                                myverifyitemsrun.save()

                        allgroup = process[0].step_set.exclude(state="9").exclude(Q(group="") | Q(group=None)).values(
                            "group").distinct()  # 过滤出需要签字的组,但一个对象只发送一次task

                        if process[0].sign == "1" and len(allgroup) > 0:  # 如果流程需要签字,发送签字tasks
                            # 将当前流程改成SIGN
                            c_process_run_id = myprocessrun.id
                            c_process_run = ProcessRun.objects.filter(id=c_process_run_id)
                            if c_process_run:
                                c_process_run = c_process_run[0]
                                c_process_run.state = "SIGN"
                                c_process_run.save()

                            for group in allgroup:
                                try:
                                    signgroup = Group.objects.get(id=int(group["group"]))
                                    groupname = signgroup.name
                                    myprocesstask = ProcessTask()
                                    myprocesstask.processrun = myprocessrun
                                    myprocesstask.starttime = datetime.datetime.now()
                                    myprocesstask.senduser = request.user.username
                                    myprocesstask.receiveauth = group["group"]
                                    myprocesstask.type = "SIGN"
                                    myprocesstask.state = "0"
                                    myprocesstask.content = "流程即将启动”，请" + groupname + "签到。"
                                    myprocesstask.save()
                                except:
                                    pass
                            result["res"] = "新增成功。"
                            result["data"] = "/"

                        else:
                            prosssigns = ProcessTask.objects.filter(processrun=myprocessrun, state="0")
                            if len(prosssigns) <= 0:
                                myprocess = myprocessrun.process
                                myprocesstask = ProcessTask()
                                myprocesstask.processrun = myprocessrun
                                myprocesstask.starttime = datetime.datetime.now()
                                myprocesstask.type = "INFO"
                                myprocesstask.logtype = "START"
                                myprocesstask.state = "1"
                                myprocesstask.senduser = request.user.username
                                myprocesstask.content = "流程已启动。"
                                myprocesstask.save()

                                exec_process.delay(myprocessrun.id)
                                result["res"] = "新增成功。"
                                result["data"] = "/processindex/" + str(myprocessrun.id)

        return HttpResponse(json.dumps(result))


def cv_oracle(request, offset, funid):
    if request.user.is_authenticated():
        id = 0
        try:
            id = int(offset)
        except:
            raise Http404()

        # 查看当前流程状态
        current_process_run = ProcessRun.objects.filter(id=offset)
        if current_process_run:
            current_process_run = current_process_run[0]
            current_run_state = current_process_run.state
        else:
            current_run_state = ""

        return render(request, 'cv_oracle.html',
                      {'username': request.user.userinfo.fullname, "process": id,
                       "current_run_state": current_run_state,
                       "pagefuns": getpagefuns(funid, request)})
    else:
        return HttpResponseRedirect("/index")


def save_invitation(request):
    if request.user.is_authenticated():
        result = {}
        process_id = request.POST.get("process_id", "")
        start_time = request.POST.get("start_time", "")
        purpose = request.POST.get("purpose", "")
        end_time = request.POST.get("end_time", "")

        # 准备流程PLAN
        try:
            process_id = int(process_id)
        except:
            raise Http404()

        if start_time:
            if end_time:
                process = Process.objects.filter(id=process_id).exclude(
                    state="9").filter(type="cv_oracle")
                if (len(process) <= 0):
                    result["res"] = '流程计划失败，该流程不存在。'
                else:

                    planning_process = ProcessRun.objects.filter(
                        process=process[0], state="PLAN")
                    if (len(planning_process) > 0):
                        result["res"] = '流程计划失败，已经存在计划流程，务必先完成该计划流程。'
                    else:
                        curprocessrun = ProcessRun.objects.filter(
                            process=process[0], state__in=["RUN", "ERROR"])
                        if (len(curprocessrun) > 0):
                            result["res"] = '流程计划失败，有流程正在进行中，请勿重复启动。'
                        else:
                            myprocessrun = ProcessRun()
                            myprocessrun.process = process[0]
                            myprocessrun.state = "PLAN"
                            myprocessrun.starttime = datetime.datetime.now()
                            myprocessrun.save()
                            current_process_run_id = myprocessrun.id

                            process = Process.objects.filter(id=process_id).exclude(
                                state="9").filter(type="cv_oracle")
                            mystep = process[0].step_set.exclude(state="9")
                            if (len(mystep) <= 0):
                                result["res"] = '流程启动失败，没有找到可用步骤。'
                            else:
                                for step in mystep:
                                    mysteprun = StepRun()
                                    mysteprun.step = step
                                    mysteprun.processrun = myprocessrun
                                    mysteprun.state = "EDIT"
                                    mysteprun.save()

                                    myscript = step.script_set.exclude(
                                        state="9")
                                    for script in myscript:
                                        myscriptrun = ScriptRun()
                                        myscriptrun.script = script
                                        myscriptrun.steprun = mysteprun
                                        myscriptrun.state = "EDIT"
                                        myscriptrun.save()

                                    myverifyitems = step.verifyitems_set.exclude(
                                        state="9")
                                    for verifyitems in myverifyitems:
                                        myverifyitemsrun = VerifyItemsRun()
                                        myverifyitemsrun.verify_items = verifyitems
                                        myverifyitemsrun.steprun = mysteprun
                                        myverifyitemsrun.save()

                            # 保存邀请函
                            current_invitation = Invitation()
                            current_invitation.process_run_id = current_process_run_id
                            current_invitation.start_time = start_time
                            current_invitation.end_time = end_time
                            current_invitation.purpose = purpose
                            current_invitation.current_time = datetime.datetime.now()
                            current_invitation.save()

                            # 生成邀请任务信息
                            myprocesstask = ProcessTask()
                            myprocesstask.processrun_id = current_process_run_id
                            myprocesstask.starttime = datetime.datetime.now()
                            myprocesstask.senduser = request.user.username
                            myprocesstask.type = "INFO"
                            myprocesstask.logtype = "PLAN"
                            myprocesstask.state = "1"
                            myprocesstask.content = "创建演练计划。"
                            myprocesstask.save()

                            result["data"] = current_process_run_id
                            result["res"] = "流程计划成功，待开启流程。"
            else:
                result["res"] = "演练结束时间必须填写！"
        else:
            result["res"] = "演练开始时间必须填写！"

        return JsonResponse(result)


def cv_oracle_run_invited(request):
    if request.user.is_authenticated():
        result = {}
        process_id = request.POST.get('processid', '')
        run_person = request.POST.get('run_person', '')
        run_time = request.POST.get('run_time', '')
        run_reason = request.POST.get('run_reason', '')
        plan_process_run_id = request.POST.get('plan_process_run_id', '')

        current_process_run = ProcessRun.objects.filter(id=plan_process_run_id)

        target = request.POST.get('target', '')
        recovery_time = request.POST.get('recovery_time', '')
        browseJobId = request.POST.get('browseJobId', '')

        data_path = request.POST.get('data_path', '')

        origin = request.POST.get('origin', '')

        if not data_path.strip():
            return JsonResponse({"res": "数据文件重定向路径不能为空。"})

        if not origin.strip():
            return JsonResponse({"res": "流程步骤中未添加Commvault接口，导致源客户端未空。"})

        try:
            target = int(target)
        except:
            return JsonResponse({"res": "目标客户端未选择。"})

        if current_process_run:
            current_process_run = current_process_run[0]

            if current_process_run.state == "RUN":
                result["res"] = '请勿重复启动该流程。'
            else:
                current_process_run.starttime = datetime.datetime.now()
                current_process_run.creatuser = request.user.username
                current_process_run.run_reason = run_reason
                current_process_run.state = "RUN"
                current_process_run.target_id = target
                current_process_run.recover_time = datetime.datetime.strptime(recovery_time,
                                                                              "%Y-%m-%d %H:%M:%S") if recovery_time else None
                current_process_run.browse_job_id = browseJobId
                current_process_run.data_path = data_path
                current_process_run.origin = origin

                current_process_run.save()

                process = Process.objects.filter(id=process_id).exclude(
                    state="9").filter(type="cv_oracle")

                allgroup = process[0].step_set.exclude(state="9").exclude(Q(group="") | Q(group=None)).values(
                    "group").distinct()  # 过滤出需要签字的组,但一个对象只发送一次task

                # 如果流程需要签字,发送签字tasks
                if process[0].sign == "1" and len(allgroup) > 0:
                    # 将当前流程改成SIGN
                    c_process_run_id = current_process_run.id
                    c_process_run = ProcessRun.objects.filter(
                        id=c_process_run_id)
                    if c_process_run:
                        c_process_run = c_process_run[0]
                        c_process_run.state = "SIGN"
                        c_process_run.save()
                    for group in allgroup:
                        try:
                            signgroup = Group.objects.get(
                                id=int(group["group"]))
                            groupname = signgroup.name
                            myprocesstask = ProcessTask()
                            myprocesstask.processrun = current_process_run
                            myprocesstask.starttime = datetime.datetime.now()
                            myprocesstask.senduser = request.user.username
                            myprocesstask.receiveauth = group["group"]
                            myprocesstask.type = "SIGN"
                            myprocesstask.state = "0"
                            myprocesstask.content = "流程即将启动”，请" + groupname + "签到。"
                            myprocesstask.save()
                        except:
                            pass
                    result["res"] = "新增成功。"
                    result["data"] = "/"

                else:
                    prosssigns = ProcessTask.objects.filter(
                        processrun=current_process_run, state="0")
                    if len(prosssigns) <= 0:
                        myprocesstask = ProcessTask()
                        myprocesstask.processrun = current_process_run
                        myprocesstask.starttime = datetime.datetime.now()
                        myprocesstask.type = "INFO"
                        myprocesstask.logtype = "START"
                        myprocesstask.state = "1"
                        myprocesstask.senduser = request.user.username
                        myprocesstask.content = "流程已启动。"
                        myprocesstask.save()

                        exec_process.delay(current_process_run.id)
                        result["res"] = "新增成功。"
                        result["data"] = process[0].url + \
                            "/" + str(current_process_run.id)
        else:
            result["res"] = '流程启动异常，请联系客服。'

        return HttpResponse(json.dumps(result))


def fill_with_invitation(request):
    if request.user.is_authenticated():
        plan_process_run_id = request.POST.get("plan_process_run_id", "")
        current_invitation = Invitation.objects.filter(
            process_run_id=plan_process_run_id)
        if current_invitation:
            current_invitation = current_invitation[0]
            start_time = current_invitation.start_time
            end_time = current_invitation.end_time
            purpose = current_invitation.purpose
            return JsonResponse({
                "start_time": start_time.strftime('%Y-%m-%d %H:%M:%S') if start_time else "",
                "end_time": end_time.strftime('%Y-%m-%d %H:%M:%S') if end_time else "",
                "purpose": purpose,
            })


def save_modify_invitation(request):
    if request.user.is_authenticated():
        result = {}
        plan_process_run_id = request.POST.get("plan_process_run_id", "")
        start_time = request.POST.get("start_date_modify", "")
        purpose = request.POST.get("purpose_modify", "")
        end_time = request.POST.get("end_date_modify", "")

        try:
            plan_process_run_id = int(plan_process_run_id)
        except:
            raise Http404()

        if start_time:
            if end_time:
                current_invitation = Invitation.objects.filter(
                    process_run_id=plan_process_run_id)
                if current_invitation:
                    current_invitation = current_invitation[0]

                    current_invitation.start_time = start_time
                    current_invitation.end_time = end_time
                    current_invitation.purpose = purpose
                    current_invitation.save()

                    # 生成邀请任务信息
                    myprocesstask = ProcessTask()
                    myprocesstask.processrun_id = plan_process_run_id
                    myprocesstask.starttime = datetime.datetime.now()
                    myprocesstask.senduser = request.user.username
                    myprocesstask.type = "INFO"
                    myprocesstask.logtype = "PLAN"
                    myprocesstask.state = "1"
                    myprocesstask.content = "修改演练计划。"
                    myprocesstask.save()

                    result["data"] = plan_process_run_id
                    result["res"] = "修改流程计划成功，待开启流程。"
                else:
                    result["res"] = "演练计划不存在，请联系客服！"
            else:
                result["res"] = "演练结束时间必须填写！"
        else:
            result["res"] = "演练开始时间必须填写！"

        return JsonResponse(result)


def getrunsetps(request):
    if request.user.is_authenticated():
        if request.method == 'POST':
            processresult = {}
            result = []
            process_name = ""
            process_state = ""
            process_starttime = ""
            process_endtime = ""
            process_note = ""
            process_rto = ""
            processrun = request.POST.get('process', '')
            try:
                processrun = int(processrun)
            except:
                raise Http404()
            processruns = ProcessRun.objects.exclude(
                state="9").filter(id=processrun)
            if len(processruns) > 0:
                process_name = processruns[0].process.name
                process_state = processruns[0].state
                process_note = processruns[0].note
                try:
                    process_starttime = processruns[0].starttime.strftime(
                        "%Y-%m-%d %H:%M:%S")
                except:
                    pass
                try:
                    process_endtime = processruns[0].endtime.strftime(
                        "%Y-%m-%d %H:%M:%S")
                except:
                    pass
                if process_state == "DONE" or process_state == "STOP":
                    try:
                        current_delta_time = (
                            processruns[0].endtime - processruns[0].starttime).total_seconds()
                        m, s = divmod(current_delta_time, 60)
                        h, m = divmod(m, 60)
                        process_rto = "%d时%02d分%02d秒" % (h, m, s)
                    except:
                        pass
                else:
                    start_time = processruns[0].starttime.replace(tzinfo=None)
                    current_time = datetime.datetime.now()
                    current_delta_time = (
                        current_time - start_time).total_seconds()
                    m, s = divmod(current_delta_time, 60)
                    h, m = divmod(m, 60)
                    process_rto = "%d时%02d分%02d秒" % (h, m, s)

                # 当前流程所有任务
                current_process_task_info = get_c_process_run_tasks(processrun)

                processresult["current_process_task_info"] = current_process_task_info
                processresult["step"] = result
                processresult["process_name"] = process_name
                processresult["process_state"] = process_state
                processresult["process_starttime"] = process_starttime
                processresult["process_endtime"] = process_endtime
                processresult["process_note"] = process_note
                processresult["process_rto"] = process_rto

                steplist = Step.objects.exclude(state="9").filter(process=processruns[0].process, pnode=None).order_by(
                    "sort")
                for step in steplist:
                    runid = 0
                    starttime = ""
                    endtime = ""
                    operator = ""
                    parameter = ""
                    runresult = ""
                    explain = ""
                    state = ""
                    group = ""
                    note = ""
                    rto = 0
                    steprunlist = StepRun.objects.exclude(state="9").filter(
                        processrun=processruns[0], step=step)
                    if len(steprunlist) > 0:
                        runid = steprunlist[0].id
                        try:
                            starttime = steprunlist[0].starttime.strftime(
                                "%Y-%m-%d %H:%M:%S")
                        except:
                            pass
                        try:
                            endtime = steprunlist[0].endtime.strftime(
                                "%Y-%m-%d %H:%M:%S")
                        except:
                            pass
                        rto = ""
                        if steprunlist[0].state == "DONE":
                            try:
                                current_delta_time = (
                                    steprunlist[0].endtime - steprunlist[0].starttime).total_seconds()
                                m, s = divmod(current_delta_time, 60)
                                h, m = divmod(m, 60)
                                rto = "%d时%02d分%02d秒" % (h, m, s)
                            except:
                                pass
                        else:
                            start_time = steprunlist[0].starttime.replace(tzinfo=None) if steprunlist[
                                0].starttime else ""
                            current_time = datetime.datetime.now()
                            current_delta_time = (
                                current_time - start_time).total_seconds() if current_time and start_time else 0
                            m, s = divmod(current_delta_time, 60)
                            h, m = divmod(m, 60)
                            rto = "%d时%02d分%02d秒" % (h, m, s)
                        operator = steprunlist[0].operator
                        if operator is not None and operator != "":
                            try:
                                curuser = User.objects.get(username=operator)
                                operator = curuser.userinfo.fullname
                            except:
                                pass
                        else:
                            operator = ""
                        parameter = steprunlist[0].parameter
                        runresult = steprunlist[0].result
                        explain = steprunlist[0].explain
                        state = steprunlist[0].state
                        note = steprunlist[0].note
                        group = step.group
                        try:
                            curgroup = Group.objects.get(id=int(group))
                            group = curgroup.name
                        except:
                            pass
                    scripts = []
                    scriptlist = Script.objects.exclude(
                        state="9").filter(step=step).order_by("sort")
                    for script in scriptlist:
                        runscriptid = 0
                        scriptstarttime = ""
                        scriptendtime = ""
                        scriptoperator = ""
                        scriptrunresult = ""
                        scriptexplain = ""
                        scriptrunlog = ""
                        scriptstate = ""
                        if len(steprunlist) > 0:
                            scriptrunlist = ScriptRun.objects.exclude(state="9").filter(steprun=steprunlist[0],
                                                                                        script=script)
                            if len(scriptrunlist) > 0:
                                runscriptid = scriptrunlist[0].id
                                try:
                                    scriptstarttime = scriptrunlist[0].starttime.strftime(
                                        "%Y-%m-%d %H:%M:%S")
                                except:
                                    pass
                                try:
                                    scriptendtime = scriptrunlist[0].endtime.strftime(
                                        "%Y-%m-%d %H:%M:%S")
                                except:
                                    pass
                                scriptoperator = scriptrunlist[0].operator
                                scriptrunlog = scriptrunlist[0].runlog
                                scriptrunresult = scriptrunlist[0].result
                                scriptexplain = scriptrunlist[0].explain
                                scriptstate = scriptrunlist[0].state
                        scripts.append(
                            {"id": script.id, "code": script.code, "name": script.name, "runscriptid": runscriptid,
                             "scriptstarttime": scriptstarttime,
                             "scriptendtime": scriptendtime, "scriptoperator": scriptoperator,
                             "scriptrunresult": scriptrunresult, "scriptexplain": scriptexplain,
                             "scriptrunlog": scriptrunlog, "scriptstate": scriptstate})
                    verifyitems = []
                    verifyitemslist = VerifyItems.objects.exclude(
                        state="9").filter(step=step)
                    for verifyitem in verifyitemslist:
                        runverifyitemid = 0
                        has_verified = ""
                        verifyitemstate = ""
                        if len(steprunlist) > 0:
                            verifyitemsrunlist = VerifyItemsRun.objects.exclude(state="9").filter(
                                steprun=steprunlist[0],
                                verify_items=verifyitem)
                            if len(verifyitemsrunlist) > 0:
                                runverifyitemid = verifyitemsrunlist[0].id
                                has_verified = verifyitemsrunlist[0].has_verified
                                verifyitemstate = verifyitemsrunlist[0].state
                        verifyitems.append(
                            {"id": verifyitem.id, "name": verifyitem.name, "runverifyitemid": runverifyitemid,
                             "has_verified": has_verified,
                             "verifyitemstate": verifyitemstate})

                    result.append({"id": step.id, "code": step.code, "name": step.name, "approval": step.approval,
                                   "skip": step.skip, "group": group, "time": step.time, "runid": runid,
                                   "starttime": starttime, "endtime": endtime, "operator": operator,
                                   "parameter": parameter, "runresult": runresult, "explain": explain,
                                   "state": state, "scripts": scripts, "verifyitems": verifyitems,
                                   "note": note, "rto": rto, "children": getchildrensteps(processruns[0], step)})
            return HttpResponse(json.dumps(processresult))


def cv_oracle_continue(request):
    if request.user.is_authenticated():
        result = {}
        process = request.POST.get('process', '')
        try:
            process = int(process)
        except:
            raise Http404()
        exec_process.delay(process, if_repeat=True)
        result["res"] = "执行成功。"

        current_process_run = ProcessRun.objects.filter(id=process)
        if current_process_run:
            current_process_run = current_process_run[0]

            all_tasks_ever = current_process_run.processtask_set.filter(state="0")
            if all_tasks_ever:
                for task in all_tasks_ever:
                    task.endtime = datetime.datetime.now()
                    task.state = "1"
                    task.save()
        else:
            result["res"] = "流程不存在。"
        return HttpResponse(json.dumps(result))


def processsignsave(request):
    """
    判断是否最后一个签字，如果是,签字后启动程序
    :param request:
    :return:
    """
    if 'task_id' in request.POST:
        result = {}
        id = request.POST.get('task_id', '')
        sign_info = request.POST.get('sign_info', '')

        try:
            id = int(id)
        except:
            raise Http404()
        try:
            process_task = ProcessTask.objects.get(id=id)
            process_task.operator = request.user.username
            process_task.explain = sign_info
            process_task.endtime = datetime.datetime.now()
            process_task.state = "1"
            process_task.save()

            myprocessrun = process_task.processrun

            prosssigns = ProcessTask.objects.filter(
                processrun=myprocessrun, state="0")
            if len(prosssigns) <= 0:
                myprocessrun.state = "RUN"
                myprocessrun.starttime = datetime.datetime.now()
                myprocessrun.save()

                myprocess = myprocessrun.process
                myprocesstask = ProcessTask()
                myprocesstask.processrun = myprocessrun
                myprocesstask.starttime = datetime.datetime.now()
                myprocesstask.type = "INFO"
                myprocesstask.logtype = "START"
                myprocesstask.state = "1"
                myprocesstask.content = "流程已启动。"
                myprocesstask.starttime = datetime.datetime.now()
                myprocesstask.senduser = request.user.username
                myprocesstask.save()

                exec_process.delay(myprocessrun.id)
                result["res"] = "签字成功,同时启动流程。"
                result["data"] = "/processindex/" + str(myprocessrun.id)
            else:
                result["res"] = "签字成功。"
        except:
            result["res"] = "流程启动失败，请于管理员联系。"
        return JsonResponse(result)


def get_current_scriptinfo(request):
    if request.user.is_authenticated():
        current_step_id = request.POST.get('steprunid', '')
        selected_script_id = request.POST.get('scriptid', '')

        if selected_script_id:
            try:
                selected_script_id = int(selected_script_id)
            except:
                selected_script_id = None
        else:
            selected_script_id = None

        scriptrun_objs = ScriptRun.objects.filter(
            id=selected_script_id).select_related("steprun", "steprun__processrun")
        script_id = scriptrun_objs[0].script_id if scriptrun_objs else None

        script_objs = Script.objects.filter(
            id=script_id).select_related("hosts_manage", "origin")
        script_obj = script_objs[0] if script_objs else None

        if script_obj:
            scriptrun_obj = scriptrun_objs[0]
            step_id_from_script = scriptrun_obj.steprun.step_id
            show_button = ""
            if step_id_from_script == current_step_id:
                # 显示button
                show_button = 1
            state_dict = {
                "DONE": "已完成",
                "EDIT": "未执行",
                "RUN": "执行中",
                "ERROR": "执行失败",
                "IGNORE": "忽略",
                "": "",
            }

            starttime = scriptrun_obj.starttime.strftime(
                "%Y-%m-%d %H:%M:%S") if scriptrun_obj.starttime else ""
            endtime = scriptrun_obj.endtime.strftime(
                "%Y-%m-%d %H:%M:%S") if scriptrun_obj.endtime else ""

            target = ""
            if script_obj.interface_type == "commvault":
                if scriptrun_obj.steprun.processrun.target:
                    target = scriptrun_obj.steprun.processrun.target.client_name

            script_info = {
                "processrunstate": scriptrun_obj.steprun.processrun.state,
                "code": script_obj.code,
                "ip": script_obj.hosts_manage.host_ip if script_obj.hosts_manage else "",
                "filename": script_obj.filename,
                "scriptpath": script_obj.scriptpath,
                "state": state_dict["{0}".format(scriptrun_obj.state)],
                "starttime": starttime,
                "endtime": endtime,
                "operator": scriptrun_obj.operator,
                "explain": scriptrun_obj.explain,
                "show_button": show_button,
                "step_id_from_script": step_id_from_script,
                "show_log_btn": "1" if script_obj.log_address else "0",
                "origin": script_obj.origin.client_name if script_obj.origin else "",
                "target": target,
                "interface_type": script_obj.interface_type,
            }

            return JsonResponse({"data": script_info})


def ignore_current_script(request):
    if request.user.is_authenticated():
        selected_script_id = request.POST.get('scriptid', '')
        scriptruns = ScriptRun.objects.filter(id=selected_script_id)[0]
        scriptruns.state = "IGNORE"
        scriptruns.save()

        # 继续运行
        current_script_run = ScriptRun.objects.filter(
            id=selected_script_id).select_related("steprun")
        if current_script_run:
            current_script_run = current_script_run[0]
            current_process_run = current_script_run.steprun.processrun
            current_process_run_id = current_process_run.id
            exec_process.delay(current_process_run_id, if_repeat=True)

            return JsonResponse({"data": "成功忽略当前脚本！", "result": 1})
        else:
            return JsonResponse({"data": "脚本忽略失败，请联系客服！", "result": 0})


def stop_current_process(request):
    if request.user.is_authenticated():
        process_run_id = request.POST.get('process_run_id', '')
        process_note = request.POST.get('process_note', '')

        try:
            process_run_id = int(process_run_id)
        except ValueError as e:
            return JsonResponse({"data": "当前选择终止的流程不存在。"})

        current_process_run = ProcessRun.objects.exclude(
            state="9").filter(id=process_run_id)
        if current_process_run:
            current_process_run = current_process_run[0]

            all_current_step_runs = current_process_run.steprun_set.filter(Q(state="RUN") | Q(state="CONFIRM")).exclude(
                state="9")
            if all_current_step_runs:
                for all_current_step_run in all_current_step_runs:
                    all_current_step_run.state = "EDIT"
                    all_current_step_run.save()
                    all_scripts_from_current_step = all_current_step_run.scriptrun_set.filter(state="RUN").exclude(
                        state="9")
                    if all_scripts_from_current_step:
                        for script in all_scripts_from_current_step:
                            script.state = "EDIT"
                            script.save()

            current_process_run.state = "STOP"
            current_process_run.endtime = datetime.datetime.now()
            current_process_run.note = process_note
            current_process_run.save()

            all_tasks_ever = current_process_run.processtask_set.filter(
                state="0")
            if all_tasks_ever:
                for task in all_tasks_ever:
                    task.endtime = datetime.datetime.now()
                    task.state = "1"
                    task.save()

            myprocesstask = ProcessTask()
            myprocesstask.processrun_id = process_run_id
            myprocesstask.starttime = datetime.datetime.now()
            myprocesstask.senduser = request.user.username
            myprocesstask.type = "INFO"
            myprocesstask.logtype = "STOP"
            myprocesstask.state = "1"
            myprocesstask.content = "流程被终止。"
            myprocesstask.save()

            ######################
            # 执行强制执行的脚本  #
            ######################
            force_exec_script.delay(process_run_id)

            return JsonResponse({"data": "流程已经被终止，将强制执行部分脚本。"})
        else:
            return JsonResponse({"data": "终止流程异常，请联系客服"})


def verify_items(request):
    if request.user.is_authenticated():
        verify_array = request.POST.get("verify_array", "")
        step_id = request.POST.get("step_id", "")

        try:
            verify_array = eval(verify_array)
        except:
            verify_array = []

        current_step_run = StepRun.objects.filter(id=step_id).exclude(state="9").select_related("processrun",
                                                                                                "step").all()
        if current_step_run:
            current_step_run = current_step_run[0]
            ###########################################
            # VerifyItemsRun中has_verified修改成已确认 #
            ###########################################
            all_verify_item_run = current_step_run.verifyitemsrun_set.exclude(
                state="9").filter(id__in=verify_array)
            if all_verify_item_run.exists():
                all_verify_item_run.update(has_verified="1")

            # CONFIRM修改成DONE
            current_step_run.state = "DONE"
            current_step_run.endtime = datetime.datetime.now()
            current_step_run.save()

            all_current__tasks = current_step_run.processrun.processtask_set.exclude(
                state="1")
            for task in all_current__tasks:
                task.endtime = datetime.datetime.now()
                task.state = "1"
                task.save()

            # 写入任务
            myprocesstask = ProcessTask()
            myprocesstask.processrun_id = current_step_run.processrun_id
            myprocesstask.starttime = datetime.datetime.now()
            myprocesstask.senduser = current_step_run.processrun.creatuser
            myprocesstask.type = "INFO"
            myprocesstask.logtype = "STEP"
            myprocesstask.state = "1"
            myprocesstask.content = "步骤" + current_step_run.step.name + "完成。"
            myprocesstask.save()

            # 运行流程
            current_process_run_id = current_step_run.processrun_id
            exec_process.delay(current_process_run_id, if_repeat=True)

            return JsonResponse({"data": "0"})
        else:
            return JsonResponse({"data": "1"})


def show_result(request):
    if request.user.is_authenticated():
        processrun_id = request.POST.get("process_run_id", "")

        show_result_dict = {}

        try:
            processrun_id = int(processrun_id)
        except:
            raise Http404()

        current_processrun = ProcessRun.objects.filter(id=processrun_id)
        if current_processrun:
            current_processrun = current_processrun[0]
            process_id = current_processrun.process.id
        else:
            raise Http404()

        process_name = current_processrun.process.name if current_processrun else ""
        processrun_time = current_processrun.starttime.strftime("%Y-%m-%d")

        # 父级
        step_info_list = []
        pnode_steplist = Step.objects.exclude(state="9").filter(process_id=process_id).order_by("sort").filter(
            pnode_id=None)

        for num, pstep in enumerate(pnode_steplist):
            second_el_dict = dict()
            step_name = pstep.name
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
                    second_el_dict["start_time"] = pnode_steprun.starttime.strftime(
                        "%Y-%m-%d %H:%M:%S") if pnode_steprun.starttime else ""
                    second_el_dict["end_time"] = pnode_steprun.endtime.strftime(
                        "%Y-%m-%d %H:%M:%S") if pnode_steprun.endtime else ""

                    if pnode_steprun.endtime and pnode_steprun.starttime:
                        end_time = pnode_steprun.endtime.strftime(
                            "%Y-%m-%d %H:%M:%S")
                        start_time = pnode_steprun.starttime.strftime(
                            "%Y-%m-%d %H:%M:%S")
                        delta_seconds = datetime.datetime.strptime(end_time,
                                                                   '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(
                            start_time, '%Y-%m-%d %H:%M:%S')
                        hour, minute, second = str(delta_seconds).split(":")
                        delta_time = "{0}时{1}分{2}秒".format(
                            hour, minute, second)
                        second_el_dict["rto"] = delta_time
                    else:
                        second_el_dict["rto"] = ""

            # 步骤负责人
            try:
                users = User.objects.filter(username=pnode_steprun.operator)
                if users:
                    operator = users[0].userinfo.fullname
                    second_el_dict["operator"] = operator
                else:
                    second_el_dict["operator"] = ""
            except:
                second_el_dict["operator"] = ""

            p_id = pstep.id
            inner_steps = Step.objects.exclude(state="9").filter(process_id=process_id).order_by("sort").filter(
                pnode_id=p_id)

            # 子级
            inner_step_list = []
            if inner_steps:
                for num, step in enumerate(inner_steps):
                    inner_second_el_dict = dict()
                    step_name = step.name
                    inner_second_el_dict["step_name"] = step_name
                    steprun_obj = StepRun.objects.exclude(state="9").filter(processrun_id=processrun_id).filter(
                        step=step).select_related("step")
                    if steprun_obj:
                        steprun_obj = steprun_obj[0]
                        if steprun_obj.step.rto_count_in == "0":
                            inner_second_el_dict["start_time"] = ""
                            inner_second_el_dict["end_time"] = ""
                            inner_second_el_dict["rto"] = ""
                        else:
                            inner_second_el_dict["start_time"] = steprun_obj.starttime.strftime("%Y-%m-%d %H:%M:%S") if \
                                steprun_obj.starttime else ""
                            inner_second_el_dict["end_time"] = steprun_obj.endtime.strftime("%Y-%m-%d %H:%M:%S") if \
                                steprun_obj.endtime else ""

                            if steprun_obj.endtime and steprun_obj.starttime:
                                end_time = steprun_obj.endtime.strftime(
                                    "%Y-%m-%d %H:%M:%S")
                                start_time = steprun_obj.starttime.strftime(
                                    "%Y-%m-%d %H:%M:%S")
                                delta_seconds = datetime.datetime.strptime(end_time,
                                                                           '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(
                                    start_time, '%Y-%m-%d %H:%M:%S')
                                hour, minute, second = str(
                                    delta_seconds).split(":")
                                delta_time = "{0}时{1}分{2}秒".format(
                                    hour, minute, second)

                                inner_second_el_dict["rto"] = delta_time
                            else:
                                inner_second_el_dict["rto"] = ""

                        # 步骤负责人
                        users = User.objects.filter(
                            username=steprun_obj.operator)
                        if users:
                            operator = users[0].userinfo.fullname
                            inner_second_el_dict["operator"] = operator
                        else:
                            inner_second_el_dict["operator"] = ""

                    inner_step_list.append(inner_second_el_dict)
            second_el_dict['inner_step_list'] = inner_step_list
            step_info_list.append(second_el_dict)

        show_result_dict["step_info_list"] = step_info_list
        # 用户组信息
        all_groups = Group.objects.exclude(state="9")
        total_list = []
        if all_groups:
            for group in all_groups:
                all_group_dict = {}
                current_group_users = group.userinfo_set.exclude(
                    state="9", pnode=None).filter(type="user")
                if current_group_users:
                    all_group_dict["group"] = group.name

                    current_users_and_departments = []
                    for user in current_group_users:
                        inner_dict = {}
                        inner_dict["fullname"] = user.fullname
                        inner_dict["depart_name"] = user.pnode.fullname if user.pnode else ""
                        current_users_and_departments.append(inner_dict)
                    all_group_dict["current_users_and_departments"] = current_users_and_departments
                    total_list.append(all_group_dict)
        show_result_dict["total_list"] = total_list

        # process_name
        show_result_dict["process_name"] = process_name
        # processrun_time
        show_result_dict["processrun_time"] = processrun_time

        # 项目起始时间，结束时间，RTO
        show_result_dict["start_time"] = current_processrun.starttime.strftime(
            "%Y-%m-%d %H:%M:%S") if current_processrun.starttime else ""
        show_result_dict["end_time"] = current_processrun.endtime.strftime(
            "%Y-%m-%d %H:%M:%S") if current_processrun.endtime else ""

        step_rto = get_process_run_rto(current_processrun)

        m, s = divmod(step_rto, 60)
        h, m = divmod(m, 60)
        show_result_dict["rto"] = "%d时%02d分%02d秒" % (h, m, s)

        return JsonResponse(show_result_dict)


def reject_invited(request):
    if request.user.is_authenticated():
        plan_process_run_id = request.POST.get("plan_process_run_id", "")
        rejected_process_runs = ProcessRun.objects.filter(
            id=plan_process_run_id)
        if rejected_process_runs:
            rejected_process_run = rejected_process_runs[0]
            rejected_process_run.state = "REJECT"
            rejected_process_run.save()

            # 生成取消任务信息
            myprocesstask = ProcessTask()
            myprocesstask.processrun_id = rejected_process_run.id
            myprocesstask.starttime = datetime.datetime.now()
            myprocesstask.senduser = request.user.username
            myprocesstask.type = "INFO"
            myprocesstask.logtype = "REJECT"
            myprocesstask.state = "1"
            myprocesstask.content = "取消演练计划。"
            myprocesstask.save()

            result = "取消演练计划成功！"
        else:
            result = "计划流程不存在，取消失败！"
        return JsonResponse({"res": result})


def reload_task_nums(request):
    if request.user.is_authenticated():
        mygroup = []
        userinfo = request.user.userinfo
        guoups = userinfo.group.all()
        pop = False
        if len(guoups) > 0:
            for curguoup in guoups:
                mygroup.append(str(curguoup.id))
        allprosstasks = ProcessTask.objects.filter(
            Q(receiveauth__in=mygroup) | Q(receiveuser=request.user.username)).filter(state="0").order_by(
            "-starttime").exclude(processrun__state="9").select_related("processrun", "processrun__process",
                                                                        "steprun__step", "steprun")
        total_task_info = {}
        message_task = []
        if len(allprosstasks) > 0:
            for task in allprosstasks:
                send_time = task.starttime
                process_name = task.processrun.process.name
                process_run_reason = task.processrun.run_reason
                task_id = task.id
                processrunid = task.processrun.id

                c_task_step_run = task.steprun
                if c_task_step_run:
                    address = c_task_step_run.step.remark
                    if not address:
                        address = ""
                else:
                    address = ""

                task_nums = len(allprosstasks)
                process_color = task.processrun.process.color
                process_url = task.processrun.process.url + \
                    "/" + str(task.processrun.id)
                time = task.starttime

                # 图标与颜色
                if task.type == "ERROR":
                    current_icon = "fa fa-exclamation-triangle"
                    current_color = "label-danger"
                elif task.type == "SIGN":
                    pop = True
                    current_icon = "fa fa-user"
                    current_color = "label-warning"
                elif task.type == "RUN":
                    current_icon = "fa fa-bell-o"
                    current_color = "label-warning"
                else:
                    current_icon = ""
                    current_color = ""

                time = custom_time(time)

                message_task.append(
                    {"content": task.content, "time": time, "process_name": process_name, "processrunid": processrunid,
                     "task_color": current_color.strip(), "task_type": task.type, "task_extra": task.content,
                     "task_icon": current_icon, "process_color": process_color.strip(), "process_url": process_url,
                     "pop": pop, "task_id": task_id, "send_time": send_time.strftime("%Y-%m-%d %H:%M:%S"),
                     "process_run_reason": process_run_reason, "group_name": guoups[0].name, "address": address})

        total_task_info["task_nums"] = len(allprosstasks)
        total_task_info["message_task"] = message_task

        return JsonResponse(total_task_info)


def delete_current_process_run(request):
    if request.user.is_authenticated():
        processrun_id = request.POST.get("processrun_id", "")

        try:
            processrun_id = int(processrun_id)
        except:
            raise Http404()

        current_process_run = ProcessRun.objects.filter(id=processrun_id)
        if current_process_run:
            current_process_run = current_process_run[0]
            current_process_run.state = "9"
            current_process_run.save()
            return HttpResponse(1)
        else:
            return HttpResponse(0)


def get_celery_tasks_info(request):
    if request.user.is_authenticated():
        task_url = "http://127.0.0.1:5555/api/tasks"
        try:
            task_json_info = requests.get(task_url).text
            task_dict_info = json.loads(task_json_info)
            tasks_list = task_dict_info.items()
        except:
            tasks_list = []

        result = []
        if (len(tasks_list) > 0):
            for key, value in tasks_list:
                if value["state"] == "STARTED":
                    received_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(value["received"])) if value[
                        "received"] else ""
                    # succeeded = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(value["succeeded"])) if value[
                    #     "succeeded"] else ""

                    result.append({
                        "uuid": value["uuid"],
                        "args": value["args"][1:-1],
                        "received": received_time,
                        "state": "执行中",
                    })
        # # 根据字典中的值对字典进行排序
        # result = sorted(result, key=itemgetter('received'), reverse=True)
        return JsonResponse({"data": result})


def revoke_current_task(request):
    if request.user.is_authenticated():
        process_run_id = request.POST.get("process_run_id", "")
        abnormal = request.POST.get("abnormal", "")
        task_url = "http://127.0.0.1:5555/api/tasks"

        try:
            process_run_id = int(process_run_id)
        except:
            return JsonResponse({"data": "流程不存在。"})

        try:
            task_json_info = requests.get(task_url).text
        except:
            return JsonResponse({"data": "终端未启动flower异步任务监控！"})

        task_dict_info = json.loads(task_json_info)
        task_id = ""

        for key, value in task_dict_info.items():
            try:
                task_process_id = int(value["args"][1:-1])
            except:
                task_process_id = ""
            # 终止指定流程的异步任务
            if value["state"] in ["STARTED", "SUCCESS"] and task_process_id == process_run_id:
                task_id = key

        # abnormal 对异步任务进行的类型判断
        #   1.手动终止异步任务
        #   2.手动终止异步任务，但不修改流程状态
        #   0.被动终止异步任务：celery-flower检测不到异步任务，但是流程还在跑

        if abnormal in ["1", "2"]:
            stop_url = "http://127.0.0.1:5555/api/task/revoke/{0}?terminate=true".format(
                task_id)
            response = requests.post(stop_url)
            print(response.text)
            task_content = "异步任务被自主关闭。"

            # 终止任务
            if task_id:
                # "1"修改状态  "2"表示强制终止流程时终止异步任务，不改变STOP状态为ERROR
                if abnormal == "1":
                    # 修改当前步骤/脚本/流程的状态为ERROR
                    set_error_state(request, process_run_id, task_content)
                return JsonResponse({"data": task_content})

            else:
                return JsonResponse({"data": "当前任务不存在"})

        else:
            task_content = "异步任务异常关闭。"

            # 终止任务
            if not task_id:
                # 修改当前步骤/脚本/流程的状态为ERROR
                set_error_state(request, process_run_id, task_content)

                return JsonResponse({"data": task_content})
            else:
                return JsonResponse({"data": "异步任务未出现异常"})


def get_script_log(request):
    if request.user.is_authenticated():
        script_run_id = request.POST.get("scriptRunId", "")
        try:
            script_run_id = int(script_run_id)
        except:
            return JsonResponse({
                "res": "0",
                "log_info": "网络错误导致的脚本信息获取失败。",
            })

        current_script_run = ScriptRun.objects.filter(
            id=script_run_id).select_related("script")
        log_info = ""
        if current_script_run:
            current_script_run = current_script_run[0]
            log_address = current_script_run.script.log_address

            # HostsManage
            cur_host_manage = current_script_run.script.hosts_manage
            remote_ip = cur_host_manage.host_ip
            remote_user = cur_host_manage.username
            remote_password = cur_host_manage.password
            script_os = cur_host_manage.os

            if script_os == "Linux":
                remote_cmd = "cat {0}".format(log_address)
            elif script_os == "AIX":
                remote_cmd = "cat {0}".format(log_address)
            else:
                remote_cmd = "type {0}".format(log_address)
            server_obj = ServerByPara(r"{0}".format(remote_cmd), remote_ip, remote_user, remote_password,
                                      script_os)
            result = server_obj.run("")
            base_data = result["data"]

            if result["exec_tag"] == "1":
                res = "0"
                data = "{0} 导致获取日志信息失败！".format(base_data)
            else:
                res = "1"
                data = base_data
        else:
            res = "0"
            data = "当前脚本不存在！"
        return JsonResponse({
            "res": res,
            "log_info": data,
        })


def save_task_remark(request):
    if request.user.is_authenticated():
        task_id = request.POST.get("task_id", "")
        sign_info_extra = request.POST.get("sign_info_extra", "")

        if task_id:
            c_process_task = ProcessTask.objects.filter(id=task_id)
            if c_process_task:
                c_process_task = c_process_task[0]
                c_process_task.explain = sign_info_extra
                c_process_task.save()
            return JsonResponse({"result": 1})
        else:
            return JsonResponse({"result": 0})


def get_server_time_very_second(request):
    if request.user.is_authenticated():
        current_time = datetime.datetime.now()
        return JsonResponse({"current_time": current_time.strftime('%Y-%m-%d %H:%M:%S')})



def get_force_script_info(request):
    if request.user.is_authenticated():
        ####################################################################
        # 获取所有包含强制执行步骤的脚本信息                                 #
        #   {"finish": 1, "script_name_list": [], "script_status_list": []}#
        ####################################################################
        process_run_id = request.POST.get("process", "")

        try:
            process_run_id = int(process_run_id)
        except ValueError as e:
            print("网络异常, {0}".format(e))
            return JsonResponse({
                "ret": 0,
                "data": "网络异常, {0}".format(e)
            })

        try:
            cur_process_run = ProcessRun.objects.get(id=process_run_id)
        except ProcessRun.DoesNotExist as e:
            print("当前流程不存在, {0}".format(e))
            return JsonResponse({
                "ret": 0,
                "data": "当前流程不存在, {0}".format(e)
            })
        else:
            finish = 1
            cur_process_id = cur_process_run.process.id
            script_name_list = []
            script_status_list = []
            all_step_runs = cur_process_run.steprun_set.exclude(
                step__state="9").filter(step__force_exec=1)
            for step_run in all_step_runs:
                cur_step_scripts = step_run.scriptrun_set.all()
                for cur_script in cur_step_scripts:
                    script_name_list.append(cur_script.script.name)
                    script_status_list.append(cur_script.state)
                    # 执行中
                    if cur_script.state not in ["ERROR", "DONE"]:
                        finish = 0
            return JsonResponse({
                "ret": 1,
                "data": {
                    "finish": finish,
                    "script_name_list": script_name_list,
                    "script_status_list": script_status_list,
                    "switch_url": "/oracle_restore/{0}".format(cur_process_id)
                }
            })
    else:
        return HttpResponseRedirect("/login")


######################
# 计划流程
######################
def process_schedule(request, funid):
    if request.user.is_authenticated():
        all_process = Process.objects.exclude(state="9").filter(type="cv_oracle").order_by("sort").only("id", "name")

        return render(request, 'process_schedule.html', {'username': request.user.userinfo.fullname,
                                                         "pagefuns": getpagefuns(funid, request=request),
                                                         "all_process": all_process})
    else:
        return HttpResponseRedirect("/login")


def process_schedule_save(request):
    if request.user.is_authenticated():
        process_schedule_id = request.POST.get('process_schedule_id', '')
        process_schedule_name = request.POST.get('process_schedule_name', '')
        process = request.POST.get('process', '')
        process_schedule_remark = request.POST.get('process_schedule_remark', '')

        schedule_type = request.POST.get('schedule_type', '')

        per_time = request.POST.get('per_time', '')
        per_month = request.POST.get('per_month', '')
        per_week = request.POST.get('per_week', '')
        ret = 1
        info = ""

        if not process_schedule_name:
            return JsonResponse({
                "ret": 0,
                "info": "计划名称不能为空。"
            })

        try:
            process = int(process)
        except ValueError as e:
            return JsonResponse({
                "ret": 0,
                "info": "流程未选择。"
            })

        try:
            process_schedule_id = int(process_schedule_id)
        except ValueError as e:
            return JsonResponse({
                "ret": 0,
                "info": "网络异常。"
            })

        # 周期类型
        try:
            schedule_type = int(schedule_type)
        except ValueError as e:
            return JsonResponse({
                "ret": 0,
                "info": "周期类型未选择。"
            })
        else:
            if schedule_type == 2:
                per_month = "*"
                if not per_week:
                    return JsonResponse({
                        "ret": 0,
                        "info": "周几未选择。"
                    })

            if schedule_type == 3:
                per_week = "*"
                if not per_month:
                    return JsonResponse({
                        "ret": 0,
                        "info": "每月第几天未选择。"
                    })

        try:
            cur_process = Process.objects.get(id=process)
        except Process.DoesNotExist as e:
            ret = 0
            info = "流程不存在。"
        else:
            if not per_time:
                ret = 0
                info = "时间未填写。"
            else:
                # 保存定时任务
                hour, minute = per_time.split(':')
                # 新增
                if process_schedule_id == 0:
                    cur_crontab_schedule = CrontabSchedule()
                    cur_crontab_schedule.hour = hour
                    cur_crontab_schedule.minute = minute
                    cur_crontab_schedule.day_of_week = per_week if per_week else "*"
                    cur_crontab_schedule.day_of_month = per_month if per_month else "*"

                    cur_crontab_schedule.save()
                    cur_crontab_schedule_id = cur_crontab_schedule.id

                    # 启动定时任务
                    cur_periodictask = PeriodicTask()
                    cur_periodictask.crontab_id = cur_crontab_schedule_id
                    cur_periodictask.name = uuid.uuid1()
                    # 默认关闭
                    cur_periodictask.enabled = 0
                    # 任务名称
                    cur_periodictask.task = "drm.tasks.create_process_run"
                    # cur_periodictask.args = [cur_process.id, request]
                    cur_periodictask.kwargs = json.dumps({
                        'cur_process': cur_process.id,
                        'creatuser':  request.user.username
                    })
                    cur_periodictask.save()
                    cur_periodictask_id = cur_periodictask.id

                    ps = ProcessSchedule()
                    ps.dj_periodictask_id = cur_periodictask_id
                    ps.process = cur_process
                    ps.name = process_schedule_name
                    ps.remark = process_schedule_remark
                    ps.schedule_type = schedule_type
                    ps.save()
                    ret = 1
                    info = "保存成功。"
                else:
                    # 修改
                    try:
                        ps = ProcessSchedule.objects.get(id=process_schedule_id)
                    except ProcessSchedule.DoesNotExist as e:
                        ret = 0
                        info = "计划流程不存在。"
                    else:

                        cur_periodictask_id = ps.dj_periodictask_id
                        # 启动定时任务
                        try:
                            cur_periodictask = PeriodicTask.objects.get(id=cur_periodictask_id)
                        except PeriodicTask.DoesNotExist as e:
                            ret = 0
                            info = "定时任务不存在。"
                        else:
                            cur_crontab_schedule = cur_periodictask.crontab
                            cur_crontab_schedule.hour = hour
                            cur_crontab_schedule.minute = minute
                            cur_crontab_schedule.day_of_week = per_week if per_week else "*"
                            cur_crontab_schedule.day_of_month = per_month if per_month else "*"
                            cur_crontab_schedule.save()
                            # 刷新定时器状态
                            cur_periodictask.task = "drm.tasks.create_process_run"
                            cur_periodictask.kwargs = json.dumps({
                                'cur_process': cur_process.id,
                                'creatuser':  request.user.username
                            })
                            cur_periodictask_status = cur_periodictask.enabled
                            cur_periodictask.enabled = cur_periodictask_status
                            cur_periodictask.save()

                            ps.process = cur_process
                            ps.name = process_schedule_name
                            ps.remark = process_schedule_remark
                            ps.schedule_type = schedule_type

                            ps.save()
                            ret = 1
                            info = "保存成功。"
        return JsonResponse({
            "ret": ret,
            "info": info
        })
    else:
        return HttpResponseRedirect("/login")


def process_schedule_data(request):
    if request.user.is_authenticated():
        result = []

        all_process_schedules = ProcessSchedule.objects.exclude(state="9").select_related("process", "dj_periodictask", "dj_periodictask__crontab")

        for process_schedule in all_process_schedules:
            process_id = process_schedule.process.id
            process_name = process_schedule.process.name
            remark = process_schedule.remark
            schedule_type = process_schedule.schedule_type
            schedule_type_display = process_schedule.get_schedule_type_display()
            # 定时任务
            status, minutes, hours, per_week, per_month = "", "", "", "", ""
            periodictask = process_schedule.dj_periodictask
            if periodictask:
                status = periodictask.enabled
                cur_crontab_schedule = periodictask.crontab
                if cur_crontab_schedule:
                    minutes = cur_crontab_schedule.minute
                    hours = cur_crontab_schedule.hour
                    per_week = cur_crontab_schedule.day_of_week
                    per_month = cur_crontab_schedule.day_of_month

            result.append({
                "process_schedule_id": process_schedule.id,
                "process_schedule_name": process_schedule.name,
                "process_id": process_id,
                "process_name": process_name,
                "remark": remark,
                "schedule_type": schedule_type,
                "schedule_type_display": schedule_type_display,
                "minutes": minutes,
                "hours": hours,
                "per_week": per_week,
                "per_month": per_month,
                "status": status,
            })
        return JsonResponse({"data": result})
    else:
        return HttpResponseRedirect("/login")


def change_periodictask(request):
    if request.user.is_authenticated():
        process_schedule_id = request.POST.get("process_schedule_id", "")
        process_periodictask_status = request.POST.get("process_periodictask_status", "")
        try:
            process_schedule_id = int(process_schedule_id)
            process_periodictask_status = int(process_periodictask_status)
        except ValueError as e:
            return JsonResponse({
                "ret": 0,
                "info": "网络异常。"
            })

        try:
            cur_process_schedule = ProcessSchedule.objects.get(id=process_schedule_id)
        except ProcessSchedule.DoesNotExist as e:
            return JsonResponse({
                "ret": 0,
                "info": "该计划流程不存在。"
            })
        else:
            cur_periodictask = cur_process_schedule.dj_periodictask
            if cur_periodictask:
                cur_periodictask.enabled = process_periodictask_status
                cur_periodictask.save()
                return JsonResponse({
                    "ret": 1,
                    "info": "定时任务状态修改成功。"
                })
            else:
                return JsonResponse({
                    "ret": 0,
                    "info": "该计划流程对应的定时任务不存在。"
                })
    else:
        return HttpResponseRedirect("/login")


def process_schedule_del(request):
    if request.user.is_authenticated():
        process_schedule_id = request.POST.get("process_schedule_id", "")

        try:
            process_schedule_id = int(process_schedule_id)
        except ValueError as e:
            return JsonResponse({
                "ret": 0,
                "info": "网络异常。"
            })

        ret = 1
        info = "流程计划删除成功。"
        # 删除process_schedule/crontab/periodictask
        try:
            cur_process_schedule = ProcessSchedule.objects.get(id=process_schedule_id)
        except ProcessSchedule.DoesNotExist as e:
            ret = 0
            info = "该流程计划不存在。"
        else:
            cur_process_schedule.state = "9"
            cur_process_schedule.save()

            try:
                cur_process_schedule.dj_periodictask.crontab.delete()
                cur_process_schedule.dj_periodictask.delete()
            except:
                ret = 0
                info = "定时任务删除失败。"
        return JsonResponse({
            "ret": ret,
            "info": info
        })
    else:
        return HttpResponseRedirect("/login")


######################
# 邀请函
######################
def invite(request):
    if request.user.is_authenticated():
        process_id = request.GET.get("process_id", "")
        start_date = request.GET.get("start_date", "")
        purpose = request.GET.get("purpose", "")
        end_date = request.GET.get("end_date", "")
        process_date = start_date
        nowtime = datetime.datetime.now()
        invite_time = nowtime.strftime("%Y-%m-%d")

        current_processes = Process.objects.filter(id=process_id).filter(type="cv_oracle")
        process_name = current_processes[0].name if current_processes else ""
        allgroup = current_processes[0].step_set.exclude(state="9").exclude(Q(group="") | Q(group=None)).values(
            "group").distinct()
        all_groups = ""
        if allgroup:
            for num, current_group in enumerate(allgroup):
                if num == len(allgroup) - 1:
                    group = Group.objects.get(id=int(current_group["group"]))
                    all_groups += group.name
                else:
                    group = Group.objects.get(id=int(current_group["group"]))
                    all_groups += group.name + "、"
        all_wrapper_steps = Step.objects.exclude(state="9").filter(process_id=process_id, pnode_id=None)
        wrapper_step_list = []
        num_to_char_choices = {
            "1": "一",
            "2": "二",
            "3": "三",
            "4": "四",
            "5": "五",
            "6": "六",
            "7": "七",
            "8": "八",
            "9": "九",
        }
        for num, wrapper_step in enumerate(all_wrapper_steps):
            wrapper_step_dict = {}
            wrapper_step_dict["wrapper_step_name"] = num_to_char_choices[
                                                         "{0}".format(str(num + 1))] + "." + wrapper_step.name
            wrapper_step_group_id = wrapper_step.group
            try:
                wrapper_step_group_id = int(wrapper_step_group_id)
            except:
                wrapper_step_group_id = None
            wrapper_step_group = Group.objects.filter(id=wrapper_step_group_id)
            if wrapper_step_group:
                wrapper_step_group_name = wrapper_step_group[0].name
            else:
                wrapper_step_group_name = ""
            wrapper_step_dict["wrapper_step_group_name"] = wrapper_step_group_name

            wrapper_script_list = []
            all_wrapper_scripts = wrapper_step.script_set.exclude(state="9")
            for wrapper_script in all_wrapper_scripts:
                wrapper_script_dict = {
                    "wrapper_script_name": wrapper_script.name
                }
                wrapper_script_list.append(wrapper_script_dict)
                wrapper_step_dict["wrapper_script_list"] = wrapper_script_list

            wrapper_verify_list = []
            all_wrapper_verifys = wrapper_step.verifyitems_set.exclude(state="9")
            for wrapper_verify in all_wrapper_verifys:
                wrapper_verify_dict = {
                    "wrapper_verify_name": wrapper_verify.name
                }
                wrapper_verify_list.append(wrapper_verify_dict)
                wrapper_step_dict["wrapper_verify_list"] = wrapper_verify_list

            pnode_id = wrapper_step.id
            inner_step_list = []
            all_inner_steps = Step.objects.exclude(state="9").filter(process_id=process_id, pnode_id=pnode_id)
            for inner_step in all_inner_steps:
                inner_step_dict = {}
                inner_step_dict["inner_step_name"] = inner_step.name

                inner_step_group_id = inner_step.group
                try:
                    inner_step_group_id = int(inner_step_group_id)
                except:
                    inner_step_group_id = None
                inner_step_group = Group.objects.filter(id=inner_step_group_id)
                if inner_step_group:
                    inner_step_group_name = inner_step_group[0].name
                else:
                    inner_step_group_name = ""
                inner_step_dict["inner_step_group_name"] = inner_step_group_name

                inner_script_list = []
                all_inner_scripts = inner_step.script_set.exclude(state="9")
                for inner_script in all_inner_scripts:
                    inner_script_dict = {
                        "inner_script_name": inner_script.name
                    }
                    inner_script_list.append(inner_script_dict)

                inner_step_dict["inner_script_list"] = inner_script_list

                inner_verify_list = []
                all_inner_verifys = inner_step.verifyitems_set.exclude(state="9")
                for inner_verify in all_inner_verifys:
                    inner_verify_dict = {
                        "inner_verify_name": inner_verify.name
                    }
                    inner_verify_list.append(inner_verify_dict)

                inner_step_dict["inner_verify_list"] = inner_verify_list

                inner_step_list.append(inner_step_dict)

            wrapper_step_dict["inner_step_list"] = inner_step_list

            wrapper_step_list.append(wrapper_step_dict)
        # return render(request, 'notice.html',
        #                      {"wrapper_step_list": wrapper_step_list, "person_invited": person_invited,
        #                       "invite_reason": invite_reason, "invite_time": invite_time})
        t = TemplateResponse(request, 'notice.html',
                             {"wrapper_step_list": wrapper_step_list, "process_date": process_date,
                              "purpose": purpose, "invite_time": invite_time, "start_date": start_date,
                              "end_date": end_date,
                              "process_name": process_name, "all_groups": all_groups})
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
        css_path = current_path + os.sep + "drm" + os.sep + "static" + os.sep + "assets" + os.sep + "global" + os.sep + "css"
        css_01 = css_path + os.sep + "bootstrap.css"
        # css_02 = css_path + os.sep + "font-awesome.min.css"
        css_03 = css_path + os.sep + "icon.css"
        # css_04 = css_path + os.sep + "font.css"
        css_05 = css_path + os.sep + "app.css"
        css_06 = current_path + os.sep + "drm" + os.sep + "static" + os.sep + "assets" + os.sep + "global" + os.sep + "css" + os.sep + "components.css"

        css = [r"{0}".format(mycss) for mycss in [css_01, css_03, css_05, css_06]]

        pdfkit.from_string(t.content.decode(encoding="utf-8"), r"invitation.pdf", configuration=config, options=options,
                           css=css)

        the_file_name = "invitation.pdf"
        response = StreamingHttpResponse(file_iterator(the_file_name))
        response['Content-Type'] = 'application/octet-stream; charset=unicode'
        response['Content-Disposition'] = 'attachment;filename="{0}"'.format(the_file_name)
        return response


def get_all_users(request):
    if request.user.is_authenticated():
        all_users = UserInfo.objects.exclude(user=None)
        user_string = ""
        for user in all_users:
            user_string += user.fullname + "&"
        return JsonResponse({"data": user_string})







