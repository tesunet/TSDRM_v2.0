# 基础平台：知识库、登录相关、首页、通讯录
import uuid

from django.shortcuts import render
from django.contrib import auth
from django.http import HttpResponseRedirect, Http404, HttpResponse, JsonResponse
from django.http import StreamingHttpResponse
from django.utils.encoding import escape_uri_path
from django.core.mail import send_mail

from TSDRM import settings
from drm.api.commvault import SQLApi
from drm.api.commvault.RestApi import *
from .public_func import *

walkthroughinfo = {}
funlist = []

######################
# 知识库
######################
def downloadlist(request, funid):
    if request.user.is_authenticated():
        errors = []
        if request.method == 'POST':
            file_remark = request.POST.get("file_remark", "")
            my_file = request.FILES.get("myfile", None)
            if not my_file:
                errors.append("请选择要导入的文件。")
            else:
                if if_contains_sign(my_file.name):
                    errors.append(r"""请注意文件命名格式，'\/"*?<>'符号文件不允许上传。""")
                else:
                    myfilepath = settings.BASE_DIR + os.sep + "drm" + os.sep + "upload" + os.sep + "knowledgefiles" + os.sep + my_file.name

                    c_exist_model = KnowledgeFileDownload.objects.filter(file_name=my_file.name).exclude(state="9")

                    if os.path.exists(myfilepath) or c_exist_model.exists():
                        errors.append("该文件已存在,请勿重复上传。")
                    else:
                        with open(myfilepath, 'wb+') as f:
                            for chunk in my_file.chunks():  # 分块写入文件
                                f.write(chunk)

                        # 存入字段：备注，上传时间，上传人
                        c_file = KnowledgeFileDownload()
                        c_file.file_name = my_file.name
                        c_file.person = request.user.userinfo.fullname
                        c_file.remark = file_remark
                        c_file.upload_time = datetime.datetime.now()
                        c_file.save()

                        errors.append("导入成功。")
        return render(request, "downloadlist.html",
                      {'username': request.user.userinfo.fullname, "errors": errors,
                       "pagefuns": getpagefuns(funid, request=request)})
    else:
        return HttpResponseRedirect("/login")


def download_list_data(request):
    if request.user.is_authenticated():
        result = []
        c_files = KnowledgeFileDownload.objects.exclude(state="9")
        if c_files.exists():
            for file in c_files:
                result.append({
                    "id": file.id,
                    "name": file.person,
                    "up_time": "{0:%Y-%m-%d %H:%M:%S}".format(file.upload_time),
                    "remark": file.remark,
                    "file_name": file.file_name,
                })

        return JsonResponse({
            "data": result
        })


def knowledge_file_del(request):
    if request.user.is_authenticated():
        file_id = request.POST.get("id", "")
        assert int(file_id), "网页异常"

        c_file = KnowledgeFileDownload.objects.filter(id=file_id)
        if c_file.exists():
            c_file = c_file[0]
            c_file.delete()
            c_file_name = c_file.file_name
            the_file_name = settings.BASE_DIR + os.sep + "drm" + os.sep + "upload" + os.sep + "knowledgefiles" + os.sep + c_file_name
            if os.path.exists(the_file_name):
                os.remove(the_file_name)
            result = "删除成功。"
        else:
            result = "文件不存在，删除失败,请于管理员联系。"

        return JsonResponse({
            "data": result
        })


def download(request):
    if request.user.is_authenticated():
        file_id = request.GET.get("file_id", "")
        assert int(file_id), "网页异常"
        c_file = KnowledgeFileDownload.objects.filter(id=file_id)
        if c_file.exists():
            c_file = c_file[0]
            c_file_name = c_file.file_name
        else:
            raise Http404()
        try:
            the_file_name = settings.BASE_DIR + os.sep + "drm" + os.sep + "upload" + os.sep + "knowledgefiles" + os.sep + c_file_name
            response = StreamingHttpResponse(file_iterator(the_file_name))
            response['Content-Type'] = 'application/octet-stream; charset=unicode'
            response['Content-Disposition'] = 'attachment;filename="{0}"'.format(
                escape_uri_path(c_file_name))  # escape_uri_path()解决中文名文件
            return response
        except:
            return HttpResponseRedirect("/downloadlist")
    else:
        return HttpResponseRedirect("/login")


######################
# 登录
######################
def login(request):
    auth.logout(request)
    try:
        del request.session['ispuser']
        del request.session['isadmin']
    except KeyError:
        pass
    return render(request, 'login.html')


def userlogin(request):
    if request.method == 'POST':
        result = ""
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(username=username, password=password)
        if user is not None and user.is_active:
            auth.login(request, user)
            myuserinfo = user.userinfo
            if myuserinfo.forgetpassword:
                myuserinfo.forgetpassword = ""
                myuserinfo.save()
            if request.user.is_authenticated():
                if myuserinfo.state == "0":
                    result = "success1"
                else:
                    result = "success"
                if (request.POST.get('remember', '') != '1'):
                    request.session.set_expiry(0)
                myuser = User.objects.get(username=username)
                usertype = myuser.userinfo.type
                if usertype == '1':
                    request.session['ispuser'] = True
                else:
                    request.session['ispuser'] = False
                request.session['isadmin'] = myuser.is_superuser
            else:
                result = "登录失败，请于客服联系。"
        else:
            result = "用户名或密码不正确。"

    return HttpResponse(result)


def forgetPassword(request):
    if request.method == 'POST':
        result = ""
        email = request.POST.get('email', '')
        alluser = User.objects.filter(email=email)
        if (len(alluser) <= 0):
            result = u"邮箱" + email + u'不存在。'
        else:
            myuserinfo = alluser[0].userinfo
            url = str(uuid.uuid1())
            subject = u'密码重置'
            message = u'用户:' + alluser[0].username + u'您好。' \
                      + u"\n您在云灾备系统申请了密码重置，点击链接进入密码重置页面:" \
                      + u"http://127.0.0.1:8000/resetpassword/" + url
            send_mail(subject, message, settings.EMAIL_HOST_USER, [alluser[0].email])
            myuserinfo.forgetpassword = url
            myuserinfo.save()
            result = "邮件发送成功，请注意查收。"
        return HttpResponse(result)


def resetpassword(request, offset):
    myuserinfo = UserInfo.objects.filter(forgetpassword=offset)
    if len(myuserinfo) > 0:
        myusername = myuserinfo[0].user.username
        return render(request, 'reset.html', {"myusername": myusername})
    else:
        return render(request, 'reset.html', {"error": True})


def reset(request):
    if request.method == 'POST':
        result = ""
        myusername = request.POST.get('username', '')
        password = request.POST.get('password', '')

        alluser = User.objects.filter(username=myusername)
        if (len(alluser) > 0):
            alluser[0].set_password(password)
            alluser[0].save()
            myuserinfo = alluser[0].userinfo
            myuserinfo.forgetpassword = ""
            myuserinfo.save()
            if myuserinfo.state == "0":
                result = "success1"
            else:
                result = "success"
            auth.logout(request)
            user = auth.authenticate(username=myusername, password=password)
            if user is not None and user.is_active:
                auth.login(request, user)
                usertype = myuserinfo.type
                if usertype == '1':
                    request.session['ispuser'] = True
                else:
                    request.session['ispuser'] = False
                request.session['isadmin'] = alluser[0].is_superuser
        else:
            result = "用户不存在。"
        return HttpResponse(result)


def password(request):
    if request.user.is_authenticated():
        return render(request, 'password.html', {"myusername": request.user.username})
    else:
        return HttpResponseRedirect("/login")


def userpassword(request):
    if request.method == 'POST':
        result = ""
        username = request.POST.get('username', '')
        oldpassword = request.POST.get('oldpassword', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(username=username, password=oldpassword)
        if user is not None and user.is_active:
            alluser = User.objects.filter(username=username)
            if (len(alluser) > 0):
                alluser[0].set_password(password)
                alluser[0].save()
                myuserinfo = alluser[0].userinfo
                myuserinfo.forgetpassword = ""
                myuserinfo.save()
                result = "success"
                auth.logout(request)
                user = auth.authenticate(username=username, password=password)
                if user is not None and user.is_active:
                    auth.login(request, user)
                    usertype = myuserinfo.type
                    if usertype == '1':
                        request.session['ispuser'] = True
                    else:
                        request.session['ispuser'] = False
                    request.session['isadmin'] = alluser[0].is_superuser
            else:
                result = "用户异常，修改密码失败。"
        else:
            result = "旧密码输入错误，请重新输入。"

    return HttpResponse(result)


######################
# 首页
######################
def test(request):
    if request.user.is_authenticated():
        errors = []

        # 填充原RTO数据
        all_process_run = ProcessRun.objects.exclude(state="9")
        for processrun in all_process_run:
            if processrun.state == "DONE":
                cur_process = processrun.process

                # 正确顺序的父级Step
                all_pnode_steps = cur_process.step_set.exclude(state="9").filter(pnode_id=None).order_by("sort")

                correct_step_id_list = []

                for pnode_step in all_pnode_steps:
                    correct_step_id_list.append(pnode_step)

                # 正确顺序的父级StepRun
                correct_step_run_list = []

                for pnode_step in correct_step_id_list:
                    current_step_run = pnode_step.steprun_set.filter(processrun_id=processrun.id)
                    if current_step_run.exists():
                        current_step_run = current_step_run[0]
                        correct_step_run_list.append(current_step_run)
                starttime = processrun.starttime
                rtoendtime = processrun.starttime

                for c_step_run in reversed(correct_step_run_list):
                    if c_step_run.step.rto_count_in == "1":
                        rtoendtime = c_step_run.endtime
                        break
                delta_time = 0
                if rtoendtime:
                    delta_time = (rtoendtime - starttime).total_seconds()

                processrun.rto = delta_time
                processrun.save()
            else:
                processrun.rto = 0
                processrun.save()

        return render(request, 'test.html',
                      {'username': request.user.userinfo.fullname, "errors": errors})
    else:
        return HttpResponseRedirect("/login")


def processindex(request, processrun_id):
    if request.user.is_authenticated():
        errors = []
        s_tag = request.GET.get("s", "")
        # exclude
        global walkthroughinfo
        walkthroughinfo = {}
        c_process_run = ProcessRun.objects.filter(id=processrun_id).select_related("process")
        if c_process_run.exists():
            process_url = c_process_run[0].process.url
            process_name = c_process_run[0].process.name
            process_id = c_process_run[0].process.id
        else:
            raise Http404()
        return render(request, 'processindex.html',
                      {'username': request.user.userinfo.fullname, "errors": errors, "processrun_id": processrun_id,
                       "process_url": process_url, "process_name": process_name, "process_id": process_id,
                       "s_tag": s_tag})
    else:
        return HttpResponseRedirect("/login")


def get_process_index_data(request):
    if request.user.is_authenticated():
        # print('************')
        processrun_id = request.POST.get("p_run_id", "")
        # print(processrun_id)

        current_processruns = ProcessRun.objects.filter(id=int(processrun_id)).select_related("process")

        if current_processruns:
            current_processrun = current_processruns[0]

            # 当前流程状态
            c_process_run_state = current_processrun.state
            name = current_processrun.process.name
            starttime = current_processrun.starttime
            endtime = current_processrun.endtime
            rtoendtime = ""

            state = current_processrun.state
            percent = 0

            process_id = current_processrun.process_id

            # 正确顺序的父级Step
            all_pnode_steps = Step.objects.exclude(state="9").filter(process_id=process_id, pnode_id=None).order_by(
                "sort")
            correct_step_id_list = []
            if all_pnode_steps:
                for pnode_step in all_pnode_steps:
                    pnode_step_id = pnode_step.id
                    correct_step_id_list.append(pnode_step_id)
            else:
                raise Http404()

            # 正确顺序的父级StepRun
            correct_step_run_list = []
            for step_id in correct_step_id_list:
                current_step_run = StepRun.objects.filter(step_id=step_id).filter(
                    processrun_id=processrun_id).select_related("step")
                if current_step_run.exists():
                    current_step_run = current_step_run[0]
                    correct_step_run_list.append(current_step_run)

            # 构造当前流程步骤info
            steps = []
            rtostate = "RUN"

            if correct_step_run_list:
                c_step_index = 0
                # 流程运行中的rtostate
                if c_process_run_state != "DONE":
                    if c_process_run_state == "ERROR":
                        rtostate = "RUN"
                    else:
                        c_state = False
                        for num, c_step_run in enumerate(correct_step_run_list):
                            c_rto_count_in = c_step_run.step.rto_count_in
                            if c_rto_count_in == "0" and c_step_run.state in ["CONFIRM", "DONE"]:
                                c_state = True
                                rtostate = "DONE"
                                c_step_index = num
                                break

                        if c_state:
                            # 表示需要计入rto的步骤已经完成
                            if c_step_index > 0 and rtostate == "DONE":
                                pre_step_index = c_step_index - 1
                                rtoendtime = correct_step_run_list[pre_step_index].endtime.strftime('%Y-%m-%d %H:%M:%S')
                # 流程结束后的rtostate
                else:
                    for num, c_step_run in enumerate(correct_step_run_list):
                        c_rto_count_in = c_step_run.step.rto_count_in

                        if c_rto_count_in == "0" and c_step_run.state == "DONE":
                            rtostate = "DONE"
                            c_step_index = num
                            break
                    if c_step_index > 0 and rtostate == "DONE":
                        pre_step_index = c_step_index - 1
                        rtoendtime = correct_step_run_list[pre_step_index].endtime.strftime('%Y-%m-%d %H:%M:%S')

                if_has_run = False
                if_has_index = 0
                for num, c_step_run in enumerate(correct_step_run_list):
                    num += 1
                    if c_step_run.state not in ["DONE", "STOP", "EDIT"]:
                        if_has_run = True
                        break
                    elif c_step_run.state == "DONE":
                        if_has_index = num

                for num, c_step_run in enumerate(correct_step_run_list):
                    num += 1
                    # 流程结束后的当前步骤
                    if c_process_run_state == "DONE":
                        if num == len(correct_step_run_list):
                            c_step_run_type = "cur"
                        else:
                            c_step_run_type = ""
                    # 流程运行中的当前步骤
                    else:
                        if c_step_run.state not in ["DONE", "STOP", "EDIT"]:
                            c_step_run_type = "cur"
                        else:
                            # 这里还要加一个没有RUN的判断
                            c_step_run_type = ""

                    if not if_has_run and num == if_has_index:
                        c_step_run_type = "cur"

                    c_step_id = c_step_run.step.id
                    c_inner_step_runs = StepRun.objects.filter(step__pnode_id=c_step_id).filter(step__state__in=["9"])

                    # 未完成
                    all_steps = c_step_run.step.children.exclude(state="9")
                    all_done_step_list = []
                    for step in all_steps:
                        step_id = step.id
                        done_step_run = StepRun.objects.filter(step_id=step_id, processrun_id=processrun_id).filter(
                            state="DONE")
                        if done_step_run.exists():
                            all_done_step_list.append(done_step_run[0])

                    if all_done_step_list:
                        inner_step_run_percent = "%2d" % (len(all_done_step_list) / len(all_steps) * 100)
                    else:
                        inner_step_run_percent = 0

                    if c_step_run.state in ["DONE"]:
                        inner_step_run_percent = 100

                    start_time = c_step_run.starttime
                    end_time = c_step_run.endtime

                    delta_time = 0
                    if c_step_run.step.children.all().exclude(
                            state="9").count() == 0 and c_step_run.verifyitemsrun_set.all().count() == 0 and c_step_run.scriptrun_set.all().exists():
                        # 用于判断 没有子步骤，不需要确认，有脚本的步骤
                        now_time = datetime.datetime.now()
                        if not end_time and start_time:
                            delta_time = (now_time - start_time)
                            if delta_time:
                                delta_time = "%.f" % delta_time.total_seconds()
                            else:
                                delta_time = 0
                        c_tag = "yes"

                        ########################################
                        # 获取当前运行的流程对应的源客户端，     #
                        # 获取其最近一次作业控制器中的恢复记录。 #
                        ########################################
                        origin = current_processrun.origin
                        if origin:
                            dm = SQLApi.CustomFilter(settings.sql_credit)
                            all_jobs = dm.get_job_controller()
                            dm.close()
                            for job in all_jobs:
                                if origin.upper() == job["clientComputer"].upper():
                                    inner_step_run_percent = job["progress"]
                                    break

                    else:
                        c_tag = "no"
                    c_step_run_dict = {
                        "name": c_step_run.step.name,
                        "state": c_step_run.state if c_step_run.state else "",
                        "starttime": starttime.strftime('%Y-%m-%d %H:%M:%S') if starttime else None,
                        "endtime": endtime.strftime('%Y-%m-%d %H:%M:%S') if endtime else None,
                        "percent": inner_step_run_percent,
                        "type": c_step_run_type,
                        "delta_time": delta_time,
                        "c_tag": c_tag,
                    }
                    steps.append(c_step_run_dict)

            done_step_run = current_processrun.steprun_set.filter(state="DONE")
            if done_step_run.exists():
                done_num = len(done_step_run)
            else:
                done_num = 0

            # 消息列表
            showtasks = []
            tasks = ProcessTask.objects.filter(type='info').filter(processrun=current_processrun).exclude(state='9')
            for task in tasks:
                showtasks.append({
                    "taskid": task.id,
                    "taskname": name,
                    "taskcontent": task.content,
                    "tasktime": task.starttime.strftime('%Y-%m-%d %H:%M:%S') if task.starttime else "",
                })
            # 构造展示步骤
            process_rate = "%02d" % (done_num / len(current_processrun.steprun_set.all()) * 100)
            isConfirm = "0"
            confirmStepruns = StepRun.objects.exclude(state="9").filter(processrun_id=processrun_id, state='CONFIRM')
            if len(confirmStepruns) > 0:
                isConfirm = "1"

            if current_processrun.state == "SIGN":
                rtostate = "DONE"
                rtoendtime = current_processrun.starttime.strftime('%Y-%m-%d %H:%M:%S')
            current_time = datetime.datetime.now()
            c_step_run_data = {
                "current_time": current_time.strftime('%Y-%m-%d %H:%M:%S'),
                "name": name,
                "starttime": starttime.strftime('%Y-%m-%d %H:%M:%S') if starttime else "",
                "rtoendtime": rtoendtime,
                "endtime": endtime.strftime('%Y-%m-%d %H:%M:%S') if endtime else "",
                "state": state,
                "rtostate": rtostate,
                "percent": process_rate,
                "isConfirm": isConfirm,
                "steps": steps,
                "showtasks": showtasks
            }
            global walkthroughinfo
            oldwalkthroughinfo = walkthroughinfo
            walkthroughinfo = c_step_run_data
            c_step_run_data["oldwalkthroughinfo"] = oldwalkthroughinfo
        else:
            c_step_run_data = {}

        return JsonResponse(c_step_run_data)


def getfun(myfunlist, fun):
    try:
        if (fun.pnode_id is not None):
            if fun not in myfunlist:
                childfun = {}
                if (fun.pnode_id != 1):
                    myfunlist = getfun(myfunlist, fun.pnode)
                myfunlist.append(fun)
    except:
        pass
    return myfunlist


def childfun(myfun, funid):
    mychildfun = []
    funs = myfun.children.order_by("sort").all()
    pisselected = False
    for fun in funs:
        if fun in funlist:
            isselected = False
            if str(fun.id) == funid:
                isselected = True
                pisselected = True
                mychildfun.append(
                    {"id": fun.id, "name": fun.name, "url": fun.url, "icon": fun.icon, "isselected": isselected,
                     "child": []})
            else:
                returnfuns = childfun(fun, funid)
                mychildfun.append({"id": fun.id, "name": fun.name, "url": fun.url, "icon": fun.icon,
                                   "isselected": returnfuns["isselected"], "child": returnfuns["fun"]})
                if returnfuns["isselected"]:
                    pisselected = returnfuns["isselected"]
    return {"fun": mychildfun, "isselected": pisselected}


def getpagefuns(funid, request=""):
    pagefuns = []
    mycurfun = {}
    message_task = []
    task_nums = 0

    for fun in funlist:
        if fun.pnode_id == 1:
            isselected = False
            if str(fun.id) == funid:
                isselected = True
                pagefuns.append(
                    {"id": fun.id, "name": fun.name, "url": fun.url, "icon": fun.icon, "isselected": isselected,
                     "child": []})
            else:
                returnfuns = childfun(fun, funid)
                pagefuns.append({"id": fun.id, "name": fun.name, "url": fun.url, "icon": fun.icon,
                                 "isselected": returnfuns["isselected"], "child": returnfuns["fun"]})
    curfun = Fun.objects.filter(id=int(funid))
    if len(curfun) > 0:
        myurl = curfun[0].url
        jsurl = curfun[0].url
        if len(myurl) > 0:
            myurl = myurl[:-1]
            jsurl = jsurl[:-1]
            if "oracle_restore" in myurl:
                compile_obj = re.compile(r"/.*/")
                jsurl = compile_obj.findall(myurl)[0][:-1]
        mycurfun = {"id": curfun[0].id, "name": curfun[0].name, "url": myurl, "jsurl": jsurl}
    if request:
        # 右上角消息下拉菜单
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
                                                                        "steprun__step")
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
                process_url = task.processrun.process.url + "/" + str(task.processrun.id)
                time = task.starttime

                # 图标与颜色
                if task.type == "ERROR":
                    current_icon = "fa fa-exclamation-triangle"
                    current_color = "label-danger"
                elif task.type == "SIGN":
                    current_icon = "fa fa-user"
                    current_color = "label-warning"
                elif task.type == "RUN":
                    current_icon = "fa fa-bell-o"
                    current_color = "label-warning"
                else:
                    pass

                time = custom_time(time)

                message_task.append(
                    {"content": task.content, "time": time, "process_name": process_name, "address": address,
                     "task_color": current_color.strip(), "task_type": task.type, "task_extra": task.content,
                     "task_icon": current_icon, "process_color": process_color.strip(), "process_url": process_url,
                     "pop": True if task.type == "SIGN" else False, "task_id": task_id,
                     "send_time": send_time.strftime("%Y-%m-%d %H:%M:%S"),
                     "processrunid": processrunid, "process_run_reason": process_run_reason,
                     "group_name": guoups[0].name})
    return {"pagefuns": pagefuns, "curfun": mycurfun, "message_task": message_task, "task_nums": task_nums}


def index(request, funid):
    if request.user.is_authenticated():
        global funlist
        funlist = []
        if request.user.is_superuser == 1:
            allfunlist = Fun.objects.all()
            for fun in allfunlist:
                funlist.append(fun)
        else:
            cursor = connection.cursor()
            cursor.execute(
                "select drm_fun.id from drm_group,drm_fun,drm_userinfo,drm_userinfo_group,drm_group_fun "
                "where drm_group.id=drm_userinfo_group.group_id and drm_group.id=drm_group_fun.group_id and "
                "drm_group_fun.fun_id=drm_fun.id and drm_userinfo.id=drm_userinfo_group.userinfo_id and userinfo_id= "
                + str(request.user.userinfo.id) + " order by drm_fun.sort"
            )

            rows = cursor.fetchall()
            for row in rows:
                try:
                    fun = Fun.objects.get(id=row[0])
                    funlist = getfun(funlist, fun)
                except:
                    pass
        for index, value in enumerate(funlist):
            if value.sort is None:
                value.sort = 0
        funlist = sorted(funlist, key=lambda fun: fun.sort)
        # 最新操作
        alltask = []
        cursor = connection.cursor()
        cursor.execute("""
        select t.starttime, t.content, t.type, t.state, t.logtype, p.name, p.color from drm_processtask as t left join drm_processrun as r on t.processrun_id = r.id left join drm_process as p on p.id = r.process_id where r.state!='9' order by t.starttime desc;
        """)
        rows = cursor.fetchall()

        # cvsql = SQLApi.CVApi(settings.sql_credit)
        # cvsql.updateCVUTC()
        # cvsql.close()

        if len(rows) > 0:
            for task in rows:
                time = task[0]
                content = task[1]
                task_type = task[2]
                task_state = task[3]
                task_logtype = task[4]
                process_name = task[5]
                process_color = task[6]

                # 图标与颜色
                current_icon, current_color = custom_c_color(task_type, task_state, task_logtype)

                time = custom_time(time)

                alltask.append(
                    {"content": content, "time": time, "process_name": process_name, "task_color": current_color,
                     "task_icon": current_icon, "process_color": process_color})
                if len(alltask) >= 50:
                    break
        # 成功率，恢复次数，平均RTO，最新切换
        all_processrun_objs = ProcessRun.objects.filter(Q(state="DONE") | Q(state="STOP"))
        successful_processruns = ProcessRun.objects.filter(state="DONE")
        processrun_times_obj = ProcessRun.objects.exclude(state__in=["RUN", "REJECT"]).exclude(state="9")

        success_rate = "%.0f" % (len(successful_processruns) / len(
            all_processrun_objs) * 100) if all_processrun_objs and successful_processruns else 0
        last_processrun_time = successful_processruns.last().starttime if successful_processruns else ""
        all_processruns = len(processrun_times_obj) if processrun_times_obj else 0

        current_processruns = ProcessRun.objects.exclude(state__in=["DONE", "STOP", "REJECT"]).exclude(
            state="9").select_related("process")
        curren_processrun_info_list = []
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

        process_rate = "0"
        if current_processruns:
            for current_processrun in current_processruns:
                current_processrun_dict = {}
                start_time_strftime = ""
                current_delta_time = ""
                current_step_name = ""
                current_process_name = ""
                current_step_index = ""
                all_steps = []
                group_name = ""
                users = ""
                process_id = current_processrun.process_id
                current_process_name = current_processrun.process.name
                start_time = current_processrun.starttime.replace(tzinfo=None)
                start_time_strftime = start_time.strftime('%Y-%m-%d %H:%M:%S')
                current_time = datetime.datetime.now()
                current_delta_time = (current_time - start_time).total_seconds()
                m, s = divmod(current_delta_time, 60)
                h, m = divmod(m, 60)
                current_delta_time = "%d时%02d分%02d秒" % (h, m, s)

                current_processrun_id = current_processrun.id

                # 进程url
                processrun_url = current_processrun.process.url + "/" + str(current_processrun_id)

                # 当前系统任务
                current_process_task_info = get_c_process_run_tasks(current_processrun.id)

                current_processrun_dict["current_process_run_state"] = state_dict[
                    "{0}".format(current_processrun.state)]
                current_processrun_dict["current_process_task_info"] = current_process_task_info
                current_processrun_dict["current_processrun_dict"] = current_processrun_dict
                current_processrun_dict["start_time_strftime"] = start_time_strftime
                current_processrun_dict["current_delta_time"] = current_delta_time
                current_processrun_dict["current_process_name"] = current_process_name
                current_processrun_dict["current_step_index"] = current_step_index
                current_processrun_dict["all_steps"] = all_steps
                current_processrun_dict["process_rate"] = process_rate
                current_processrun_dict["current_step_name"] = current_step_name
                current_processrun_dict["group_name"] = group_name
                current_processrun_dict["users"] = users
                current_processrun_dict["processrun_url"] = processrun_url
                current_processrun_dict["processrun_id"] = current_processrun.id

                curren_processrun_info_list.append(current_processrun_dict)

        ##################################
        # 今日演练：                      #
        #   今天演练过的系统个数/总系统数  #
        ##################################
        today_process_run_length = 0
        today_date = datetime.datetime.now().date()
        pre_client = ""
        for processrun_obj in all_processrun_objs:
            if today_date == processrun_obj.starttime.date():
                if pre_client == processrun_obj.origin:
                    continue
                today_process_run_length += 1

                pre_client = processrun_obj.origin

        all_process = Process.objects.exclude(state="9").filter(type="cv_oracle")
        # 右上角消息任务
        return render(request, "index.html",
                      {'username': request.user.userinfo.fullname, "alltask": alltask, "homepage": True,
                       "pagefuns": getpagefuns(funid, request), "success_rate": success_rate,
                       "all_processruns": all_processruns, "last_processrun_time": last_processrun_time,
                       "curren_processrun_info_list": curren_processrun_info_list,
                       "today_process_run_length": today_process_run_length, "all_process": all_process})
    else:
        return HttpResponseRedirect("/login")


def monitor(request):
    if request.user.is_authenticated():
        global funlist
        # 最新操作
        alltask = []
        cursor = connection.cursor()
        cursor.execute("""
        select t.starttime, t.content, t.type, t.state, t.logtype, p.name, p.color from drm_processtask as t left join drm_processrun as r on t.processrun_id = r.id left join drm_process as p on p.id = r.process_id where r.state!='9' order by t.starttime desc;
        """)
        rows = cursor.fetchall()

        if len(rows) > 0:
            for task in rows:
                time = task[0]
                content = task[1]
                task_type = task[2]
                task_state = task[3]
                task_logtype = task[4]
                process_name = task[5]
                process_color = task[6]

                # 图标与颜色
                current_icon, current_color = custom_c_color(task_type, task_state, task_logtype)

                time = custom_time(time)

                alltask.append(
                    {"content": content, "time": time, "process_name": process_name, "task_color": current_color,
                     "task_icon": current_icon, "process_color": process_color})
                if len(alltask) >= 50:
                    break
        # 成功率，恢复次数，平均RTO，最新切换
        all_processrun_objs = ProcessRun.objects.filter(Q(state="DONE") | Q(state="STOP"))
        successful_processruns = ProcessRun.objects.filter(state="DONE")
        processrun_times_obj = ProcessRun.objects.exclude(state__in=["RUN", "REJECT"]).exclude(state="9")

        success_rate = "%.0f" % (len(successful_processruns) / len(
            all_processrun_objs) * 100) if all_processrun_objs and successful_processruns else 0

        last_processrun_time = successful_processruns.last().starttime if successful_processruns else ""
        all_processruns = len(processrun_times_obj) if processrun_times_obj else 0

        current_processruns = ProcessRun.objects.exclude(state__in=["DONE", "STOP", "REJECT"]).exclude(
            state="9").select_related("process")
        curren_processrun_info_list = []
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

        process_rate = "0"
        if current_processruns:
            for current_processrun in current_processruns:
                current_processrun_dict = {}
                start_time_strftime = ""
                current_delta_time = ""
                current_step_name = ""
                current_process_name = ""
                current_step_index = ""
                all_steps = []
                group_name = ""
                users = ""
                process_id = current_processrun.process_id
                current_process_name = current_processrun.process.name
                start_time = current_processrun.starttime.replace(tzinfo=None)
                start_time_strftime = start_time.strftime('%Y-%m-%d %H:%M:%S')
                current_time = datetime.datetime.now()
                current_delta_time = (current_time - start_time).total_seconds()
                m, s = divmod(current_delta_time, 60)
                h, m = divmod(m, 60)
                current_delta_time = "%d时%02d分%02d秒" % (h, m, s)

                current_processrun_id = current_processrun.id

                # 进程url
                processrun_url = current_processrun.process.url + "/" + str(current_processrun_id)

                # 当前系统任务
                current_process_task_info = get_c_process_run_tasks(current_processrun.id)

                current_processrun_dict["current_process_run_state"] = state_dict[
                    "{0}".format(current_processrun.state)]
                current_processrun_dict["current_process_task_info"] = current_process_task_info
                current_processrun_dict["current_processrun_dict"] = current_processrun_dict
                current_processrun_dict["start_time_strftime"] = start_time_strftime
                current_processrun_dict["current_delta_time"] = current_delta_time
                current_processrun_dict["current_process_name"] = current_process_name
                current_processrun_dict["current_step_index"] = current_step_index
                current_processrun_dict["all_steps"] = all_steps
                current_processrun_dict["process_rate"] = process_rate
                current_processrun_dict["current_step_name"] = current_step_name
                current_processrun_dict["group_name"] = group_name
                current_processrun_dict["users"] = users
                current_processrun_dict["processrun_url"] = processrun_url
                current_processrun_dict["processrun_id"] = current_processrun.id

                curren_processrun_info_list.append(current_processrun_dict)

        ##################################
        # 今日演练：                      #
        #   今天演练过的系统个数/总系统数  #
        ##################################
        today_process_run_length = 0
        today_date = datetime.datetime.now().date()
        pre_client = ""
        for processrun_obj in all_processrun_objs:
            if today_date == processrun_obj.starttime.date():
                if pre_client == processrun_obj.origin:
                    continue
                today_process_run_length += 1

                pre_client = processrun_obj.origin

        all_process = Process.objects.exclude(state="9").filter(type="cv_oracle")
        # 右上角消息任务
        return render(request, "monitor.html",
                      {'username': request.user.userinfo.fullname, "alltask": alltask, "homepage": True,
                       "success_rate": success_rate,
                       "all_processruns": all_processruns, "last_processrun_time": last_processrun_time,
                       "curren_processrun_info_list": curren_processrun_info_list,
                       "today_process_run_length": today_process_run_length, "all_process": all_process})
    else:
        return HttpResponseRedirect("/login")


def get_monitor_data(request):
    if request.user.is_authenticated():
        drill_day = []

        # 最近7日演练次数
        drill_times = []
        drill_rto = []
        for i in range(0, 7)[::-1]:
            today_datetime = datetime.datetime.now()
            if i == 0:
                pass
            else:
                today_datetime = today_datetime - datetime.timedelta(days=i)
            today_drills = ProcessRun.objects.exclude(state__in=["RUN", "REJECT", "9"]).filter(
                starttime__startswith=today_datetime.date())
            drill_day.append("{0:%m-%d}".format(today_datetime.date()))
            drill_times.append(len(today_drills))

            # 平均RTO趋势
            cur_client_succeed_process = ProcessRun.objects.filter(state="DONE").filter(
                starttime__startswith=today_datetime.date())

            if cur_client_succeed_process:
                rto_sum_seconds = 0

                for processrun in cur_client_succeed_process:
                    ########################################################
                    # 构造出正确顺序的父级步骤RTO，                         #
                    # 最后一个步骤rto_count_in="0"，记录endtime为rtoendtime #
                    ########################################################
                    delta_time = get_process_run_rto(processrun)
                    rto_sum_seconds += delta_time

                rto = "%.2f" % (rto_sum_seconds / 60)

                drill_rto.append(rto)
            else:
                drill_rto.append(0)

        week_drill = {
            "drill_day": drill_day,
            "drill_times": drill_times
        }

        avgRTO = {
            "drill_day": drill_day,
            "drill_rto": drill_rto
        }

        # 系统演练次数TOP5
        all_process = Process.objects.exclude(state="9").filter(type="cv_oracle")
        drill_name = []
        drill_time = []
        for process in all_process:
            process_runs = process.processrun_set.exclude(state__in=["RUN", "REJECT", "9"])
            cur_drill_time = len(process_runs)

            if drill_time:
                for dt in drill_time:
                    dt_index = drill_time.index(dt)
                    if cur_drill_time > dt:
                        drill_name.insert(dt_index, process.name)
                        drill_time.insert(dt_index, cur_drill_time)
                        break
                else:
                    drill_name.append(process.name)
                    drill_time.append(cur_drill_time)
            else:
                drill_name.append(process.name)
                drill_time.append(cur_drill_time)

        drill_top_time = {
            "drill_name": drill_name[:5][::-1] if len(drill_name[::-1]) > 5 else drill_name,
            "drill_time": drill_time[:5][::-1] if len(drill_time[::-1]) > 5 else drill_time
        }
        # print(drill_top_time)
        # 演练成功率
        all_processrun_objs = ProcessRun.objects.filter(Q(state="DONE") | Q(state="STOP"))
        successful_processruns = ProcessRun.objects.filter(state="DONE")

        success_rate = "%.0f" % (len(successful_processruns) / len(
            all_processrun_objs) * 100) if all_processrun_objs and successful_processruns else 0
        drill_rate = [success_rate, 100 - int(success_rate)]

        # 演练日志
        task_list = []
        all_process_tasks = ProcessTask.objects.filter(logtype__in=["ERROR", "STOP", "END", "START"]).order_by(
            "-starttime").select_related("processrun", "processrun__process")
        for num, process_task in enumerate(all_process_tasks):
            if num == 50:
                break
            process_name = ""
            try:
                process_name = process_task.processrun.process.name
            except:
                pass

            task_list.append({
                "process_name": process_name,
                "start_time": "{0: %Y-%m-%d %H:%M:%S}".format(process_task.starttime) if process_task.starttime else "",
                "content": process_task.content
            })
        # 今日作业
        running_job, success_job, error_job = 0, 0, 0
        all_processes = Process.objects.exclude(state="9").filter(type="cv_oracle")
        has_run_process = 0
        for process in all_processes:
            process_run = process.processrun_set.exclude(state__in=["9", "REJECT"]).filter(
                starttime__startswith=datetime.datetime.now().date())
            if process_run.exists():
                has_run_process += 1

                # 运行中
                if process_run.last().state == "RUN":
                    running_job += 1

                if process_run.last().state == "DONE":
                    success_job += 1

        not_running = 0
        try:
            # 未启动
            not_running = len(all_processes) - has_run_process

            # 失败：总的-成功-运行中-未启动
            error_job = len(all_processes) - success_job - running_job - not_running
        except:
            pass

        # 演练监控
        drill_monitor = []

        for process in all_processes:
            today_process_run = process.processrun_set.exclude(state__in=["9", "REJECT"]).filter(
                starttime__startswith=datetime.datetime.now().date())

            if today_process_run:
                today_process_run = today_process_run.last()
                done_step_run = today_process_run.steprun_set.filter(state="DONE")
                if done_step_run.exists():
                    done_num = len(done_step_run)
                else:
                    done_num = 0

                # 构造展示步骤
                process_rate = "%02d" % (done_num / len(today_process_run.steprun_set.all()) * 100)

                # 策略时间
                cur_schedule = ""
                try:
                    process_schedule = ProcessSchedule.objects.filter(process=process).exclude(state="9")
                    if process_schedule.exists():
                        cur_schedule_hour = process_schedule[0].dj_periodictask.crontab.hour
                        cur_schedule_minute = process_schedule[0].dj_periodictask.crontab.minute
                        cur_schedule = "{0}:{1}".format(cur_schedule_hour, cur_schedule_minute)
                except:
                    pass

                drill_monitor.append({
                    "process_name": process.name,
                    "state": today_process_run.state,
                    "schedule_time": cur_schedule,
                    "start_time": "{0:%Y-%m-%d %H:%M:%S}".format(
                        today_process_run.starttime) if today_process_run.starttime else "",
                    "end_time": "{0:%Y-%m-%d %H:%M:%S}".format(
                        today_process_run.endtime) if today_process_run.endtime else "",
                    "percent": "{0}%".format((int(process_rate)))
                })
            else:
                # 策略时间
                cur_schedule = ""
                try:
                    process_schedule = ProcessSchedule.objects.filter(process=process).exclude(state="9")
                    if process_schedule.exists():
                        cur_schedule_hour = process_schedule[0].dj_periodictask.crontab.hour
                        cur_schedule_minute = process_schedule[0].dj_periodictask.crontab.minute
                        cur_schedule = "{0}:{1}".format(cur_schedule_hour, cur_schedule_minute)
                except:
                    pass
                drill_monitor.append({
                    "process_name": process.name,
                    "state": "未演练",
                    "schedule_time": cur_schedule,
                    "start_time": "",
                    "end_time": "",
                    "percent": "0%"
                })

        # 待处理异常
        error_processrun_list = []
        error_processrun = ProcessRun.objects.filter(state="ERROR").select_related("process").order_by("-starttime")
        for epr in error_processrun:
            error_processrun_list.append({
                "process_name": epr.process.name,
                "start_time": "{0:%Y-%m-%d %H:%M:%S}".format(epr.starttime) if epr.starttime else "",
                "processrun_url": "/cv_oracle/{processrun_id}/".format(processrun_id=epr.id)
            })
        return JsonResponse({
            "week_drill": week_drill,
            "avgRTO": avgRTO,
            "drill_top_time": drill_top_time,
            "drill_rate": drill_rate,
            "drill_monitor": drill_monitor,
            "task_list": task_list,
            "today_job": {
                "running_job": running_job,
                "success_job": success_job,
                "error_job": error_job,
                "not_running": not_running
            },
            "error_processrun": error_processrun_list
        })
    else:
        return HttpResponseRedirect("/login")


def get_clients_status(request):
    if request.user.is_authenticated():
        # 客户端状态
        dm = SQLApi.CustomFilter(settings.sql_credit)

        if dm.msg == "链接数据库失败。":
            service_status = "中断"
            net_status = "中断"
        else:
            service_status = "正常"
            net_status = "正常"

        # 客户端列表
        client_list = Origin.objects.exclude(state=9).values_list("client_name")
        client_name_list = [client_name[0] for client_name in client_list]
        # 报警客户端
        whole_backup_list = dm.custom_concrete_job_list(client_name_list)
        dm.close()
        return JsonResponse({
            "clients_status": {
                "service_status": service_status,
                "net_status": net_status,
                "all_clients": len(client_list),
                "whole_backup_list": whole_backup_list
            }
        })
    else:
        return HttpResponseRedirect("/login")


def get_process_run_facts(request):
    if request.user.is_authenticated():
        #######################################################
        # 演练概况：                                          #
        # 客户端名称/今日演练(状态:√/×/○>> 成功/失败/未演练) #
        # /平均RTO/演练次数/演练成功率                         #
        #######################################################
        cv_oracle_process_list = []

        all_process = Process.objects.exclude(state="9").order_by("sort").filter(type="cv_oracle"). \
            prefetch_related("processrun_set", "step_set", "step_set__scriptinstance_set", "step_set__scriptinstance_set__origin")

        for cur_process in all_process:
            # 今日演练(状态)  0/1/2
            # 演练一次成功就算成功
            today_date = datetime.datetime.now().date()

            all_process_run = cur_process.processrun_set.filter(state__in=["DONE", "STOP", "ERROR"]).filter(
                starttime__startswith=today_date)
            process_run_today = 2

            if all_process_run.exists():
                cur_process_run = all_process_run.last()
                if cur_process_run.state == "DONE":
                    process_run_today = 0
                else:
                    process_run_today = 1
            # 平均RTO
            cur_client_succeed_process = cur_process.processrun_set.filter(state="DONE")

            if cur_client_succeed_process:
                rto_sum_seconds = 0

                for processrun in cur_client_succeed_process:
                    ########################################################
                    # 构造出正确顺序的父级步骤RTO，                         #
                    # 最后一个步骤rto_count_in="0"，记录endtime为rtoendtime #
                    ########################################################
                    delta_time = get_process_run_rto(processrun)

                    try:
                        delta_time = int(delta_time)
                    except ValueError as e:
                        delta_time = 0

                    rto_sum_seconds += delta_time

                m, s = divmod(rto_sum_seconds / len(cur_client_succeed_process), 60)
                h, m = divmod(m, 60)
                average_rto = "%d时%02d分%02d秒" % (h, m, s)
            else:
                average_rto = "00时00分00秒"

            # 演练次数
            cur_client_process = cur_process.processrun_set.filter(Q(state="DONE") | Q(state="STOP"))
            cur_client_process_times = len(cur_client_process) if cur_client_process else 0

            # 演练成功率
            cur_client_succeed_process_times = len(cur_client_succeed_process) if cur_client_succeed_process else 0
            process_run_rate = "%.0f" % ((
                                             cur_client_succeed_process_times / cur_client_process_times if cur_client_process_times != 0 else 0) * 100)

            # 客户端
            client_name = ""
            all_steps = cur_process.step_set.exclude(state="9")
            for step in all_steps:
                all_scripts = step.scriptinstance_set.exclude(state="9")
                for script in all_scripts:
                    if script.origin:
                        client_name = script.origin.client_name
                        break

            cv_oracle_process_list.append({
                "process_name": cur_process.name,
                "process_run_today": process_run_today,
                "average_rto": average_rto,
                "cur_client_process_times": cur_client_process_times,
                "process_run_rate": process_run_rate,
                "process_id": cur_process.id,
            })
        return JsonResponse({"data": cv_oracle_process_list})
    else:
        return HttpResponseRedirect("/login")


def get_process_rto(request):
    if request.user.is_authenticated():
        # 不同流程最近的12次切换RTO
        all_processes = Process.objects.exclude(state="9").filter(type="cv_oracle")
        process_rto_list = []
        if all_processes:
            for process in all_processes:
                process_name = process.name
                processrun_rto_obj_list = process.processrun_set.filter(state="DONE")
                current_rto_list = []
                for processrun_rto_obj in processrun_rto_obj_list:
                    step_rto = get_process_run_rto(processrun_rto_obj)

                    current_rto = float("%.2f" % (step_rto / 60))

                    current_rto_list.append(current_rto)
                process_dict = {
                    "process_name": process_name,
                    "current_rto_list": current_rto_list,
                    "color": process.color
                }
                process_rto_list.append(process_dict)
        return JsonResponse({"data": process_rto_list if len(process_rto_list) <= 12 else process_rto_list[-12:]})


def get_daily_processrun(request):
    if request.user.is_authenticated():
        all_processrun_objs = ProcessRun.objects.select_related("process").filter(state__in=["DONE", "STOP", "PLAN"])
        process_success_rate_list = []

        for process_run in all_processrun_objs:
            if process_run.state in ["DONE", "STOP"]:
                process_name = process_run.process.name
                start_time = process_run.starttime
                end_time = process_run.endtime
                process_color = process_run.process.color
                process_run_id = process_run.id
                # 进程url
                processrun_url = "/processindex/" + str(process_run.id) + "?s=true"

                process_run_dict = {
                    "process_name": process_name,
                    "start_time": start_time,
                    "end_time": end_time,
                    "process_color": process_color,
                    "process_run_id": process_run_id,
                    "url": processrun_url,
                    "invite": "0"
                }
                process_success_rate_list.append(process_run_dict)
            if process_run.state == "PLAN":
                invitations_dict = {
                    "process_name": process_run.process.name,
                    "start_time": process_run.starttime,
                    "end_time": process_run.endtime,
                    "process_color": process_run.process.color,
                    "process_run_id": process_run.id,
                    "url": "/oracle_restore/{0}".format(process_run.process_id),
                    "invite": "1",
                }
                process_success_rate_list.append(invitations_dict)

        return JsonResponse({"data": process_success_rate_list})


######################
# 通讯录
######################
def contact(request, funid):
    if request.user.is_authenticated():
        return render(request, 'contact.html',
                      {'username': request.user.userinfo.fullname,
                       "pagefuns": getpagefuns(funid, request=request)})
    else:
        return HttpResponseRedirect("/login")


def get_contact_tree(request):
    if request.user.is_authenticated():
        selectid = ""
        treedata = []
        rootnodes = UserInfo.objects.order_by("sort").exclude(state="9").filter(pnode=None, type="org")
        if len(rootnodes) > 0:
            for rootnode in rootnodes:
                root = {}
                root["text"] = rootnode.fullname
                root["id"] = rootnode.id
                root["type"] = "org"

                root["data"] = {"remark": rootnode.remark, "pname": "无"}
                try:
                    if int(selectid) == rootnode.id:
                        root["state"] = {"opened": True, "selected": True}
                    else:
                        root["state"] = {"opened": True}
                except:
                    root["state"] = {"opened": True}
                root["children"] = get_contact_org_tree(rootnode, selectid)
                treedata.append(root)
        return JsonResponse({"data": treedata})
    else:
        return HttpResponseRedirect("/login")


def get_contact_info(request):
    if request.user.is_authenticated():
        user_id = request.GET.get("user_id", "")

        try:
            user_id = int(user_id)
        except:
            JsonResponse({"data": []})

        contact_list = []
        # 查看当前节点下所有userinfo的type为user的信息
        if user_id == 0:
            # pnode不为空，state不为"9"，type为"user"
            all_contacts = UserInfo.objects.exclude(state="9").filter(type="user")
            for contact in all_contacts:
                if contact.pnode_id != None:
                    try:
                        parent_contact_org = UserInfo.objects.get(id=contact.id)
                    except:
                        pass
                    else:
                        if parent_contact_org.pnode:
                            depart = parent_contact_org.pnode.fullname
                        else:
                            depart = ""

                        contact_list.append({
                            "user_name": contact.fullname,
                            "tel": contact.phone,
                            "email": contact.user.email,
                            "depart": depart,
                        })
        else:
            # 当前节点下所有用户信息
            get_child_contact(user_id, contact_list)

        return JsonResponse({"data": contact_list})
    else:
        return HttpResponseRedirect("/login")
