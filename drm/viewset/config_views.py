# 流程配置：预案配置、脚本配置、流程配置、主机配置
import xlrd
import xlwt

from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404, HttpResponse, JsonResponse
from django.http import StreamingHttpResponse
from django.db.models import Max

from ..tasks import *
from TSDRM import settings
from drm.api.commvault.RestApi import *
from .public_func import *
from .basic_views import getpagefuns
from django.contrib.auth.decorators import login_required
from lxml import etree


######################
# 脚本配置
######################
def script(request, funid):
    if request.user.is_authenticated():
        errors = []
        if request.method == 'POST':
            # 获取上传的文件，如果没有文件，则默认为None
            my_file = request.FILES.get("myfile", None)
            if not my_file:
                errors.append("请选择要导入的文件。")
            else:
                filetype = my_file.name.split(".")[-1]
                if filetype == "xls" or filetype == "xlsx":
                    myfilepath = os.path.join(os.path.join(
                        os.path.dirname(__file__), "upload\\temp"), my_file.name)
                    destination = open(myfilepath, 'wb+')
                    for chunk in my_file.chunks():  # 分块写入文件
                        destination.write(chunk)
                    destination.close()

                    data = xlrd.open_workbook(myfilepath)
                    sheet = data.sheets()[0]
                    rows = sheet.nrows

                    succeed_tag = True
                    for i in range(rows):
                        if i > 0:
                            allscript = Script.objects.filter(code=sheet.cell(i, 0).value).exclude(
                                state="9").filter(step_id=None)
                            if (len(allscript) > 0):
                                errors.append(sheet.cell(i, 0).value + ":已存在。")
                                succeed_tag = False
                            else:
                                try:
                                    # add hosts
                                    check_host_manage = HostsManage.objects.filter(
                                        host_ip=sheet.cell(i, 2).value).exclude(state="9")
                                    if check_host_manage.exists():
                                        cur_host = check_host_manage[0]
                                    else:
                                        # add host
                                        cur_host_manage = HostsManage()
                                        cur_host_manage.host_ip = sheet.cell(
                                            i, 2).value
                                        cur_host_manage.type = sheet.cell(
                                            i, 3).value
                                        cur_host_manage.username = sheet.cell(
                                            i, 4).value
                                        cur_host_manage.password = sheet.cell(
                                            i, 5).value
                                        host_os = ""
                                        if sheet.cell(i, 3).value == "SSH":
                                            host_os = "Linux"
                                        if sheet.cell(i, 3).value == "BAT":
                                            host_os = "Windows"
                                        cur_host_manage.os = host_os
                                        cur_host_manage.save()
                                        cur_host = cur_host_manage

                                    scriptsave = Script()
                                    scriptsave.code = sheet.cell(i, 0).value
                                    scriptsave.name = sheet.cell(i, 1).value
                                    scriptsave.hosts_manage = cur_host
                                    scriptsave.succeedtext = sheet.cell(
                                        i, 6).value
                                    scriptsave.script_text = sheet.cell(
                                        i, 7).value
                                    scriptsave.save()
                                except Exception as e:
                                    succeed_tag = False
                                    print(e)
                                    errors.append("脚本上传失败，请检查文件内容。")
                                    break

                    if succeed_tag:
                        errors = ["导入成功。"]

                    os.remove(myfilepath)
                else:
                    errors.append("只能上传xls和xlsx文件，请选择正确的文件类型。")

        # 主机选项
        all_hosts_manage = HostsManage.objects.exclude(state="9")

        # commvault源端客户端
        all_origins = Origin.objects.exclude(state="9")

        # 过滤本地commvaul接口脚本
        commv_path = os.path.join(os.path.join(
            settings.BASE_DIR, "drm"), "commvault_api")

        commv_file_list = os.listdir(commv_path)

        return render(request, 'script.html',
                      {'username': request.user.userinfo.fullname, "pagefuns": getpagefuns(funid, request=request),
                       "errors": errors, "all_hosts_manage": all_hosts_manage, "all_origins": all_origins,
                       "commv_file_list": commv_file_list})
    else:
        return HttpResponseRedirect("/login")


def scriptdata(request):
    if request.user.is_authenticated():
        result = []
        allscript = Script.objects.exclude(state="9").filter(
            step_id=None).select_related("origin", "hosts_manage")
        if (len(allscript) > 0):
            for script in allscript:
                # modify
                if script.interface_type == "commvault":
                    cur_origin = script.origin
                    if cur_origin:
                        result.append({
                            "id": script.id,
                            "code": script.code,
                            "name": script.name,
                            "ip": "",
                            "host_id": "",
                            "script_text": "",
                            "success_text": "",
                            "log_address": "",

                            "interface_type": script.interface_type,
                            "commv_interface": script.commv_interface,
                            "origin": cur_origin.id
                        })
                else:
                    cur_host = script.hosts_manage
                    if cur_host:
                        host_id = cur_host.id
                        ip = cur_host.host_ip

                        result.append({
                            "id": script.id,
                            "code": script.code,
                            "name": script.name,
                            "ip": ip,
                            "host_id": host_id,
                            "script_text": script.script_text,
                            "success_text": script.succeedtext,
                            "log_address": script.log_address,

                            "interface_type": script.interface_type,
                            "commv_interface": "",
                            "origin": "",
                        })

        return HttpResponse(json.dumps({"data": result}))


def scriptdel(request):
    """
    当删除脚本管理中的脚本的同时，需要删除预案中绑定的脚本；
    :param request:
    :return:
    """
    if request.user.is_authenticated():
        if 'id' in request.POST:
            id = request.POST.get('id', '')
            try:
                id = int(id)
            except:
                raise Http404()
            script = Script.objects.get(id=id)
            script.state = "9"
            script.save()

            script_code = script.code
            related_scripts = Script.objects.filter(code=script_code)
            for related_script in related_scripts:
                related_script.state = "9"
                related_script.save()

            return HttpResponse(1)
        else:
            return HttpResponse(0)


def scriptsave(request):
    if request.user.is_authenticated():
        if 'id' in request.POST:
            result = {}
            id = request.POST.get('id', '')
            code = request.POST.get('code', '')
            name = request.POST.get('name', '')
            host_id = request.POST.get('ip', '')

            # script_text
            script_text = request.POST.get('script_text', '')

            success_text = request.POST.get('success_text', '')
            log_address = request.POST.get('log_address', '')

            # commvault接口
            interface_type = request.POST.get('interface_type', '')
            origin = request.POST.get('origin', '')
            commv_interface = request.POST.get('commv_interface', '')


            try:
                id = int(id)
            except ValueError as e:
                print("id:%s" % e)
                result["res"] = '网络连接异常。'
            else:
                if code.strip() == '':
                    result["res"] = '接口编码不能为空。'
                else:
                    if name.strip() == '':
                        result["res"] = '接口名称不能为空。'
                    else:
                        # 区分interface_type: commvault/脚本
                        if interface_type.strip() == "":
                            result["res"] = '接口类型未选择。'
                        else:
                            save_data = {
                                "id": id,
                                "code": code,
                                "name": name,
                                "script_text": script_text,
                                "success_text": success_text,
                                "log_address": log_address,
                                "host_id": host_id,
                                "interface_type": interface_type,
                                "origin": origin,
                                "commv_interface": commv_interface
                            }

                            if interface_type == "commvault":
                                if origin.strip() == "":
                                    result["res"] = 'commvault源端未选择。'
                                else:
                                    if commv_interface.strip() == "":
                                        result["res"] = 'commvault接口未选择。'
                                    else:
                                        result = script_save(
                                            save_data, cur_host_manage=None)
                            else:
                                try:
                                    host_id = int(host_id)
                                except ValueError as e:
                                    print("host_id:%s" % e)
                                    result["res"] = '网络连接异常。'
                                else:
                                    if not host_id:
                                        result["res"] = '脚本存放的主机未选择。'
                                    else:
                                        if script_text.strip() == '':
                                            result["res"] = '脚本内容不能为空。'
                                        else:
                                            try:
                                                cur_host_manage = HostsManage.objects.get(
                                                    id=host_id)
                                            except HostsManage.DoesNotExist as e:
                                                print(e)
                                                result["res"] = '所选主机不存在。'
                                            else:
                                                result = script_save(
                                                    save_data, cur_host_manage=cur_host_manage)

            return HttpResponse(json.dumps(result))


def scriptexport(request):
    if request.user.is_authenticated():
        myfilepath = os.path.join(os.path.dirname(
            __file__), "upload\\temp\\scriptexport.xls")
        try:
            os.remove(myfilepath)
        except:
            pass
        filename = xlwt.Workbook()
        sheet = filename.add_sheet('sheet1')
        allscript = Script.objects.exclude(state="9").filter(step_id=None)
        sheet.write(0, 0, '脚本编号')
        sheet.write(0, 1, '脚本名称')
        sheet.write(0, 2, '主机IP')
        sheet.write(0, 3, '连接类型')
        sheet.write(0, 4, '用户名')
        sheet.write(0, 5, '密码')
        sheet.write(0, 6, 'SUCCESSTEXT')
        sheet.write(0, 7, '脚本内容')

        if len(allscript) > 0:
            for i in range(len(allscript)):
                # host_id, host_ip, type, username, password
                cur_host_manage = allscript[i].hosts_manage
                host_ip = cur_host_manage.host_ip
                host_type = cur_host_manage.type
                username = cur_host_manage.username
                password = cur_host_manage.password

                sheet.write(i + 1, 0, allscript[i].code)
                sheet.write(i + 1, 1, allscript[i].name)
                sheet.write(i + 1, 2, host_ip)
                sheet.write(i + 1, 3, host_type)
                sheet.write(i + 1, 4, username)
                sheet.write(i + 1, 5, password)
                sheet.write(i + 1, 6, allscript[i].succeedtext)
                sheet.write(i + 1, 7, allscript[i].script_text)

        filename.save(myfilepath)

        the_file_name = "scriptexport.xls"
        response = StreamingHttpResponse(file_iterator(myfilepath))
        response['Content-Type'] = 'application/octet-stream; charset=unicode'
        response['Content-Disposition'] = 'attachment;filename="{0}"'.format(
            the_file_name)
        return response

    else:
        return HttpResponseRedirect("/login")


######################
# 预案配置
######################
def process_design(request, funid):
    if request.user.is_authenticated():
        return render(request, "processdesign.html",
                      {'username': request.user.userinfo.fullname, "pagefuns": getpagefuns(funid, request=request)})


def process_data(request):
    if request.user.is_authenticated():
        result = []
        all_process = Process.objects.exclude(state="9").filter(
            type="cv_oracle").order_by("sort").values()
        if (len(all_process) > 0):
            for process in all_process:
                result.append({
                    "process_id": process["id"],
                    "process_code": process["code"],
                    "process_name": process["name"],
                    "process_remark": process["remark"],
                    "process_sign": process["sign"],
                    "process_rto": process["rto"],
                    "process_rpo": process["rpo"],
                    "process_sort": process["sort"],
                    "process_color": process["color"],
                })
        return JsonResponse({"data": result})


def process_save(request):
    if request.user.is_authenticated():
        if 'id' in request.POST:
            result = {}
            id = request.POST.get('id', '')
            code = request.POST.get('code', '')
            name = request.POST.get('name', '')
            remark = request.POST.get('remark', '')
            sign = request.POST.get('sign', '')
            rto = request.POST.get('rto', '')
            rpo = request.POST.get('rpo', '')
            sort = request.POST.get('sort', '')
            color = request.POST.get('color', '')
            try:
                id = int(id)
            except:
                raise Http404()
            if code.strip() == '':
                result["res"] = '预案编码不能为空。'
            else:
                if name.strip() == '':
                    result["res"] = '预案名称不能为空。'
                else:
                    if sign.strip() == '':
                        result["res"] = '是否签到不能为空。'
                    else:
                        # if color.strip() == "":
                        #     result["res"] = '项目图标配色不能为空。'
                        # else:
                        if id == 0:
                            all_process = Process.objects.filter(code=code).exclude(
                                state="9").filter(type="cv_oracle")
                            if (len(all_process) > 0):
                                result["res"] = '预案编码:' + code + '已存在。'
                            else:
                                processsave = Process()
                                processsave.url = '/cv_oracle'
                                processsave.type = 'cv_oracle'
                                processsave.code = code
                                processsave.name = name
                                processsave.remark = remark
                                processsave.sign = sign
                                processsave.rto = rto if rto else None
                                processsave.rpo = rpo if rpo else None
                                processsave.sort = sort if sort else None
                                processsave.color = color
                                processsave.save()
                                result["res"] = "保存成功。"
                                result["data"] = processsave.id
                        else:
                            all_process = Script.objects.filter(code=code).exclude(
                                id=id).exclude(state="9")
                            if (len(all_process) > 0):
                                result["res"] = '预案编码:' + code + '已存在。'
                            else:
                                try:
                                    processsave = Process.objects.get(id=id)
                                    processsave.code = code
                                    processsave.name = name
                                    processsave.remark = remark
                                    processsave.sign = sign
                                    processsave.rto = rto if rto else None
                                    processsave.rpo = rpo if rpo else None
                                    processsave.sort = sort if sort else None
                                    processsave.color = color
                                    processsave.save()
                                    result["res"] = "保存成功。"
                                    result["data"] = processsave.id
                                except:
                                    result["res"] = "修改失败。"
        return HttpResponse(json.dumps(result))


def process_del(request):
    if request.user.is_authenticated():
        if 'id' in request.POST:
            id = request.POST.get('id', '')
            try:
                id = int(id)
            except:
                raise Http404()
            process = Process.objects.get(id=id)
            process.state = "9"
            process.save()

            return HttpResponse(1)
        else:
            return HttpResponse(0)


######################
# 流程配置
######################
def processconfig(request, funid):
    if request.user.is_authenticated():
        process_id = request.GET.get("process_id", "")
        if process_id:
            process_id = int(process_id)

        processes = Process.objects.exclude(
            state="9").order_by("sort").filter(type="cv_oracle")
        processlist = []
        for process in processes:
            processlist.append(
                {"id": process.id, "code": process.code, "name": process.name})

        # 主机选项
        all_hosts_manage = HostsManage.objects.exclude(state="9")

        # commvault源端客户端
        all_origins = Origin.objects.exclude(state="9")

        # 过滤本地commvaul接口脚本
        commv_path = os.path.join(os.path.join(
            settings.BASE_DIR, "drm"), "commvault_api")

        commv_file_list = os.listdir(commv_path)

        return render(request, 'processconfig.html',
                      {'username': request.user.userinfo.fullname, "pagefuns": getpagefuns(funid, request=request),
                       "processlist": processlist, "process_id": process_id, "all_hosts_manage": all_hosts_manage,
                       "all_origins": all_origins, "commv_file_list": commv_file_list})


def processscriptsave(request):
    if request.user.is_authenticated():
        if 'id' in request.POST:
            result = {}
            processid = request.POST.get('processid', '')
            pid = request.POST.get('pid', '')
            id = request.POST.get('id', '')
            code = request.POST.get('code', '')
            name = request.POST.get('name', '')
            script_text = request.POST.get('script_text', '')

            success_text = request.POST.get('success_text', '')
            log_address = request.POST.get('log_address', '')
            host_id = request.POST.get('host_id', '')

            # commvault接口
            interface_type = request.POST.get('interface_type', '')
            origin = request.POST.get('origin', '')
            commv_interface = request.POST.get('commv_interface', '')

            script_sort = request.POST.get('script_sort', '')


            try:
                id = int(id)
                pid = int(pid)
                processid = int(processid)
            except ValueError as e:
                print("id, pid, processid:%s" % e)
                result["res"] = '网络连接异常。'
            else:
                if code.strip() == '':
                    result["res"] = '接口编码不能为空。'
                else:
                    if name.strip() == '':
                        result["res"] = '接口名称不能为空。'
                    else:
                        try:
                            script_sort = int(script_sort)
                        except ValueError as e:
                            result["res"] = '脚本排序不能为空。'
                        else:
                            # 区分interface_type: commvault/脚本
                            if interface_type.strip() == "":
                                result["res"] = '接口类型未选择。'
                            else:
                                save_data = {
                                    "processid": processid,
                                    "pid": pid,
                                    "id": id,
                                    "code": code,
                                    "name": name,
                                    "script_text": script_text,
                                    "success_text": success_text,
                                    "log_address": log_address,
                                    "host_id": host_id,
                                    "interface_type": interface_type,
                                    "origin": origin,
                                    "commv_interface": commv_interface,
                                    "script_sort": script_sort
                                }

                                if interface_type == "commvault":
                                    if origin.strip() == "":
                                        result["res"] = 'commvault源端未选择。'
                                    else:
                                        if commv_interface.strip() == "":
                                            result["res"] = 'commvault接口未选择。'
                                        else:
                                            result = process_script_save(
                                                save_data, cur_host_manage=None)
                                else:
                                    try:
                                        host_id = int(host_id)
                                    except ValueError as e:
                                        print("host_id:%s" % e)
                                        result["res"] = '网络连接异常。'
                                    else:
                                        if not host_id:
                                            result["res"] = '脚本存放的主机未选择。'
                                        else:
                                            if script_text.strip() == '':
                                                result["res"] = '脚本内容不能为空。'
                                            else:
                                                try:
                                                    cur_host_manage = HostsManage.objects.get(
                                                        id=host_id)
                                                except HostsManage.DoesNotExist as e:
                                                    print(e)
                                                    result["res"] = '所选主机不存在。'
                                                else:
                                                    result = process_script_save(save_data,
                                                                                 cur_host_manage=cur_host_manage)

            return HttpResponse(json.dumps(result))


def get_script_data(request):
    if request.user.is_authenticated():
        if 'id' in request.POST:
            id = request.POST.get('id', '')
            try:
                id = int(id)
            except:
                raise Http404()
            script_id = request.POST.get("script_id", "")
            allscript = Script.objects.exclude(state="9").filter(
                id=script_id).select_related("origin")
            script_data = ""
            if (len(allscript) > 0):
                cur_script = allscript[0]

                cur_host_manage = cur_script.hosts_manage

                script_data = {
                    "id": cur_script.id,
                    "code": cur_script.code,
                    "name": cur_script.name,
                    "host_id": cur_host_manage.id if cur_host_manage else "",
                    "script_text": cur_script.script_text,
                    "success_text": cur_script.succeedtext,
                    "log_address": cur_script.log_address,
                    # commvault
                    "interface_type": cur_script.interface_type,
                    "origin": cur_script.origin.id if cur_script.origin else "",
                    "commv_interface": cur_script.commv_interface,

                    "script_sort": cur_script.sort
                }
            return HttpResponse(json.dumps(script_data))


def remove_script(request):
    if request.user.is_authenticated():
        # 移除当前步骤中的脚本关联
        script_id = request.POST.get("script_id", "")
        try:
            current_script = Script.objects.filter(id=script_id)[0]
        except:
            pass
        else:
            # current_script.delete()
            current_script.state = "9"
            current_script.save()
        return JsonResponse({
            "status": 1
        })


def setpsave(request):
    if request.method == 'POST':
        result = ""
        id = request.POST.get('id', '')
        pid = request.POST.get('pid', '')
        name = request.POST.get('name', '')
        time = request.POST.get('time', '')
        skip = request.POST.get('skip', '')
        approval = request.POST.get('approval', '')
        group = request.POST.get('group', '')
        rto_count_in = request.POST.get('rto_count_in', '')
        remark = request.POST.get('remark', '')
        force_exec = request.POST.get('force_exec', '')

        process_id = request.POST.get('process_id', '')

        data = ""

        try:
            id = int(id)
        except:
            return JsonResponse({
                "result": "网络异常。",
                "data": data
            })

        try:
            force_exec = int(force_exec)
        except:
            force_exec = 2

        data = ""
        # 新增步骤
        if id == 0:
            # process_name下右键新增
            try:
                pid = int(pid)
            except:
                pid = None
                max_sort_from_pnode = \
                    Step.objects.exclude(state="9").filter(pnode_id=None, process_id=process_id).aggregate(Max("sort"))[
                        "sort__max"]
            else:
                max_sort_from_pnode = \
                    Step.objects.exclude(state="9").filter(pnode_id=pid).filter(process_id=process_id).aggregate(
                        Max("sort"))["sort__max"]

            # 当前没有父节点
            if max_sort_from_pnode or max_sort_from_pnode == 0:
                my_sort = max_sort_from_pnode + 1
            else:
                my_sort = 0

            step = Step()
            step.skip = skip
            step.approval = approval
            step.group = group
            step.rto_count_in = rto_count_in

            if time:
                try:
                    time = int(time)
                except:
                    time = None

            step.time = time if time != "" else None
            step.name = name
            step.process_id = process_id
            step.pnode_id = pid
            step.sort = my_sort
            step.remark = remark
            step.force_exec = force_exec
            step.save()
            # last_id
            current_steps = Step.objects.filter(pnode_id=pid).exclude(state="9").order_by("sort").filter(
                process_id=process_id)
            last_id = current_steps[0].id
            for num, step in enumerate(current_steps):
                if num == 0:
                    step.last_id = ""
                else:
                    step.last_id = last_id
                last_id = step.id
                step.save()
            result = "保存成功。"
            data = step.id
        else:
            step = Step.objects.filter(id=id)
            if (len(step) > 0):
                step[0].name = name
                step[0].time = time if time != "" else None
                step[0].skip = skip
                step[0].approval = approval
                step[0].group = group
                step[0].rto_count_in = rto_count_in
                step[0].remark = remark
                step[0].force_exec = force_exec
                step[0].save()
                result = "保存成功。"
            else:
                result = "当前步骤不存在，请联系客服！"

        return JsonResponse({
            "result": result,
            "data": data
        })


def custom_step_tree(request):
    if request.user.is_authenticated():
        errors = []
        id = request.POST.get('id', "")
        p_step = ""
        pid = request.POST.get('pid', "")
        name = request.POST.get('name', "")
        process_id = request.POST.get("process", "")
        current_process = Process.objects.filter(id=process_id)
        if current_process:
            current_process = current_process[0]
        else:
            raise Http404()
        process_name = current_process.name

        if id == 0:
            selectid = pid
            title = "新建"
        else:
            selectid = id
            title = name

        try:
            if id == 0:
                sort = 1
                try:
                    maxstep = Step.objects.filter(
                        pnode=p_step).latest('sort').exclude(state="9")
                    sort = maxstep.sort + 1
                except:
                    pass
                funsave = Step()
                funsave.pnode = p_step
                funsave.name = name
                funsave.sort = sort
                funsave.save()
                title = name
                id = funsave.id
                selectid = id
            else:
                funsave = Step.objects.get(id=id)
                funsave.name = name
                funsave.save()
                title = name
        except:
            errors.append('保存失败。')

        treedata = []
        rootnodes = Step.objects.order_by("sort").filter(
            process_id=process_id, pnode=None).exclude(state="9")

        all_groups = Group.objects.exclude(state="9")
        group_string = "" + "+" + " -------------- " + "&"
        for group in all_groups:
            id_name_plus = str(group.id) + "+" + str(group.name) + "&"
            group_string += id_name_plus
        if len(rootnodes) > 0:
            for rootnode in rootnodes:
                root = {}
                scripts = rootnode.script_set.exclude(
                    state="9").order_by("sort")
                script_string = ""
                for script in scripts:
                    id_code_plus = str(script.id) + "+" + \
                        str(script.name) + "&"
                    script_string += id_code_plus

                verify_items_string = ""
                verify_items = rootnode.verifyitems_set.exclude(state="9")
                for verify_item in verify_items:
                    id_name_plus = str(verify_item.id) + \
                        "+" + str(verify_item.name) + "&"
                    verify_items_string += id_name_plus
                root["text"] = rootnode.name
                root["id"] = rootnode.id
                group_name = ""

                try:
                    group_id = int(rootnode.group)
                    cur_group = Group.objects.get(id=group_id)

                    group_name = cur_group.name
                except:
                    pass

                root["data"] = {"time": rootnode.time, "approval": rootnode.approval, "skip": rootnode.skip,
                                "allgroups": group_string, "group": rootnode.group, "group_name": group_name,
                                "scripts": script_string, "errors": errors, "title": title,
                                "rto_count_in": rootnode.rto_count_in, "remark": rootnode.remark,
                                "verifyitems": verify_items_string, "force_exec": rootnode.force_exec if rootnode.force_exec else 2}
                root["children"] = get_step_tree(rootnode, selectid)
                root["state"] = {"opened": True}
                treedata.append(root)
        process = {}
        process["text"] = process_name
        process["data"] = {"allgroups": group_string, "verify": "first_node"}
        process["children"] = treedata
        process["state"] = {"opened": True}
        return JsonResponse({"treedata": process})
    else:
        return HttpResponseRedirect("/login")





def del_step(request):
    if request.user.is_authenticated():
        if 'id' in request.POST:
            id = request.POST.get('id', '')
            process_id = request.POST.get('process_id', '')
            try:
                id = int(id)
            except:
                raise Http404()
            try:
                process_id = int(process_id)
            except:
                raise Http404()
            allsteps = Step.objects.filter(id=id)
            if (len(allsteps) > 0):
                sort = allsteps[0].sort
                pstep = allsteps[0].pnode
                allsteps[0].state = 9
                allsteps[0].save()
                sortsteps = Step.objects.filter(pnode=pstep).filter(sort__gt=sort).exclude(state="9").filter(
                    process_id=process_id)
                if len(sortsteps) > 0:
                    for sortstep in sortsteps:
                        try:
                            sortstep.sort = sortstep.sort - 1
                            sortstep.save()
                        except:
                            pass

                current_pnode_id = allsteps[0].pnode_id
                # last_id
                current_steps = Step.objects.filter(pnode_id=current_pnode_id).exclude(state="9").order_by(
                    "sort").filter(
                    process_id=process_id)
                if current_steps:
                    last_id = current_steps[0].id
                    for num, step in enumerate(current_steps):
                        if num == 0:
                            step.last_id = ""
                        else:
                            step.last_id = last_id
                        last_id = step.id
                        step.save()

                return HttpResponse(1)
            else:
                return HttpResponse(0)


def move_step(request):
    if request.user.is_authenticated():
        if 'id' in request.POST:
            id = request.POST.get('id', '')
            parent = request.POST.get('parent', '')
            old_parent = request.POST.get('old_parent', '')
            old_position = request.POST.get('old_position', '')
            position = request.POST.get('position', '')
            process_id = request.POST.get('process_id', '')
            try:
                id = int(id)
            except:
                raise Http404()
            try:
                parent = int(parent)
            except:
                parent = None
            try:
                old_parent = int(old_parent)
            except:
                old_parent = None
            try:
                old_position = int(old_position)
            except:
                raise Http404()
            try:
                position = int(position)
            except:
                raise Http404()

            cur_step_obj = \
                Step.objects.filter(pnode_id=old_parent).filter(sort=old_position).filter(
                    process_id=process_id).exclude(state="9")[0]
            cur_step_obj.sort = position
            cur_step_id = cur_step_obj.id
            cur_step_obj.save()
            # 同一pnode
            if parent == old_parent:
                # 向上拽
                steps_under_pnode = Step.objects.filter(pnode_id=old_parent).exclude(state="9").filter(
                    sort__gte=position,
                    sort__lt=old_position).exclude(
                    id=cur_step_id).filter(process_id=process_id)
                for step in steps_under_pnode:
                    step.sort += 1
                    step.save()

                # 向下拽
                steps_under_pnode = Step.objects.filter(pnode_id=old_parent).exclude(state="9").filter(
                    sort__gt=old_position, sort__lte=position).exclude(id=cur_step_id).filter(process_id=process_id)
                for step in steps_under_pnode:
                    step.sort -= 1
                    step.save()

            # 向其他节点拽
            else:
                # 原来pnode下
                old_steps = Step.objects.filter(pnode_id=old_parent).exclude(state="9").filter(
                    sort__gt=old_position).exclude(id=cur_step_id).filter(process_id=process_id)
                for step in old_steps:
                    step.sort -= 1
                    step.save()
                # 后来pnode下
                cur_steps = Step.objects.filter(pnode_id=parent).exclude(state="9").filter(sort__gte=position).exclude(
                    id=cur_step_id).filter(process_id=process_id)
                for step in cur_steps:
                    step.sort += 1
                    step.save()

            # pnode
            if parent:
                parent_step = Step.objects.get(id=parent)
            else:
                parent_step = None
            mystep = Step.objects.get(id=id)
            try:
                mystep.pnode = parent_step
                mystep.save()
            except:
                pass

            # last_id
            old_steps = Step.objects.filter(pnode_id=old_parent).exclude(state="9").order_by("sort").filter(
                process_id=process_id)
            if old_steps:
                last_id = old_steps[0].id
                for num, step in enumerate(old_steps):
                    if num == 0:
                        step.last_id = ""
                    else:
                        step.last_id = last_id
                    last_id = step.id
                    step.save()
            after_steps = Step.objects.filter(pnode_id=parent).exclude(state="9").order_by("sort").filter(
                process_id=process_id)
            if after_steps:
                last_id = after_steps[0].id
                for num, step in enumerate(after_steps):
                    if num == 0:
                        step.last_id = ""
                    else:
                        step.last_id = last_id
                    last_id = step.id
                    step.save()

            if parent != old_parent:
                if parent == None:
                    return HttpResponse(" ^ ")
                else:
                    return HttpResponse(parent_step.name + "^" + str(parent_step.id))
            else:
                return HttpResponse("0")


def get_all_groups(request):
    if request.user.is_authenticated():
        all_group_list = []
        all_groups = Group.objects.exclude(state="9")
        for num, group in enumerate(all_groups):
            group_info_dict = {
                "group_id": group.id,
                "group_name": group.name,
            }
            all_group_list.append(group_info_dict)
        return JsonResponse({"data": all_group_list})


def verify_items_save(request):
    if request.user.is_authenticated():
        if 'id' in request.POST:
            result = {}
            id = request.POST.get('id', '')
            name = request.POST.get('name', '')
            process_id = request.POST.get('processid', '')
            step_id = request.POST.get('step_id', '')
            try:
                id = int(id)
            except:
                raise Http404()

            if name.strip() == '':
                result["res"] = '名称不能为空。'
            else:
                if id == 0:
                    verify_save = VerifyItems()
                    verify_save.name = name
                    verify_save.step_id = step_id if step_id else None
                    verify_save.save()
                    result["res"] = "新增成功。"
                    result["data"] = verify_save.id
                else:
                    try:
                        verify_save = VerifyItems.objects.get(id=id)
                        verify_save.name = name
                        verify_save.save()
                        result["res"] = "修改成功。"
                        result["data"] = verify_save.id
                    except:
                        result["res"] = "修改失败。"
            return HttpResponse(json.dumps(result))


def get_verify_items_data(request):
    if request.user.is_authenticated():
        if 'id' in request.POST:
            id = request.POST.get('id', '')
            try:
                id = int(id)
            except:
                raise Http404()
            verify_id = request.POST.get("verify_id", "")
            all_verify_items = VerifyItems.objects.exclude(
                state="9").filter(id=verify_id)
            verify_data = ""
            if (len(all_verify_items) > 0):
                verify_data = {
                    "id": all_verify_items[0].id, "name": all_verify_items[0].name}
            return HttpResponse(json.dumps(verify_data))


def remove_verify_item(request):
    if request.user.is_authenticated():
        # 移除当前步骤中的脚本关联
        verify_id = request.POST.get("verify_id", "")
        try:
            current_verify_item = VerifyItems.objects.filter(id=verify_id)[0]
        except:
            pass
        else:
            current_verify_item.state = "9"
            current_verify_item.save()
        return JsonResponse({
            "status": 1
        })


######################
# 主机配置
######################
def hosts_manage(request, funid):
    if request.user.is_authenticated():
        return render(request, 'hosts_manage.html',
                      {'username': request.user.userinfo.fullname,
                       "pagefuns": getpagefuns(funid, request=request)})
    else:
        return HttpResponseRedirect("/login")


def host_save(request):
    if request.user.is_authenticated():
        host_id = request.POST.get("host_id", "")
        host_ip = request.POST.get("host_ip", "")
        host_name = request.POST.get("host_name", "")
        host_os = request.POST.get("os", "")
        connect_type = request.POST.get("type", "")
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        ret = 0
        info = ""
        try:
            host_id = int(host_id)
        except:
            ret = 0
            info = "网络错误。"
        else:
            if host_ip.strip():
                if host_name.strip():
                    if host_os.strip():
                        if connect_type.strip():
                            if username.strip():
                                if password.strip():
                                    # 新增
                                    if host_id == 0:
                                        # 判断主机是否已经存在
                                        check_host_manage = HostsManage.objects.filter(host_ip=host_ip)
                                        if check_host_manage.exists():
                                            ret = 0
                                            info = "主机已经存在，请勿重复添加。"
                                        else:
                                            try:
                                                cur_host_manage = HostsManage()
                                                cur_host_manage.host_ip = host_ip
                                                cur_host_manage.host_name = host_name
                                                cur_host_manage.os = host_os
                                                cur_host_manage.type = connect_type
                                                cur_host_manage.username = username
                                                cur_host_manage.password = password
                                                cur_host_manage.save()
                                            except:
                                                ret = 0
                                                info = "服务器异常。"
                                            else:
                                                ret = 1
                                                info = "新增主机成功。"
                                    else:
                                        # 修改
                                        try:
                                            cur_host_manage = HostsManage.objects.get(id=host_id)
                                            cur_host_manage.host_ip = host_ip
                                            cur_host_manage.host_name = host_name
                                            cur_host_manage.os = host_os
                                            cur_host_manage.type = connect_type
                                            cur_host_manage.username = username
                                            cur_host_manage.password = password
                                            cur_host_manage.save()

                                            ret = 1
                                            info = "主机信息修改成功。"
                                        except:
                                            ret = 0
                                            info = "服务器异常。"
                                else:
                                    ret = 0
                                    info = "密码未填写。"
                            else:
                                ret = 0
                                info = "用户名未填写。"
                        else:
                            ret = 0
                            info = "连接类型未选择。"
                    else:
                        ret = 0
                        info = "系统未选择。"
                else:
                    ret = 0
                    info = "主机名称不能为空。"
            else:
                ret = 0
                info = "主机IP未填写。"
            return JsonResponse({
                "ret": ret,
                "info": info
            })
    else:
        return HttpResponseRedirect("/login")


def hosts_manage_data(request):
    if request.user.is_authenticated():
        all_hosts_manage = HostsManage.objects.exclude(state="9")
        all_hm_list = []
        for host_manage in all_hosts_manage:
            all_hm_list.append({
                "host_id": host_manage.id,
                "host_ip": host_manage.host_ip,
                "host_name": host_manage.host_name,
                "os": host_manage.os,
                "type": host_manage.type,
                "username": host_manage.username,
                "password": host_manage.password
            })
        return JsonResponse({"data": all_hm_list})
    else:
        return HttpResponseRedirect("/login")


def hosts_manage_del(request):
    if request.user.is_authenticated():
        host_id = request.POST.get("host_id", "")

        try:
            cur_host_manage = HostsManage.objects.get(id=int(host_id))
        except:
            return JsonResponse({
                "ret": 0,
                "info": "当前网络异常"
            })
        else:
            try:
                cur_host_manage.state = "9"
                cur_host_manage.save()
            except:
                return JsonResponse({
                    "ret": 0,
                    "info": "服务器网络异常。"
                })
            else:
                return JsonResponse({
                    "ret": 1,
                    "info": "删除成功。"
                })
    else:
        return HttpResponseRedirect("/login")

######################
# 工具管理
######################
@login_required
def util_manage(request, funid):
    return render(request, 'util_manage.html',
                  {'username': request.user.userinfo.fullname, "pagefuns": getpagefuns(funid, request=request)})


def get_credit_info(content):
    commvault_credit = {
        'webaddr': '',
        'port': '',
        'hostusername': '',
        'hostpasswd': '',
        'username': '',
        'passwd': '',
    }
    sqlserver_credit = {
        'SQLServerHost': '',
        'SQLServerUser': '',
        'SQLServerPasswd': '',
        'SQLServerDataBase': '',
    }
    try:
        doc = etree.XML(content)

        # Commvault账户信息
        try:
            commvault_credit['webaddr'] = doc.xpath('//webaddr/text()')[0]
        except:
            pass
        try:
            commvault_credit['port'] = doc.xpath('//port/text()')[0]
        except:
            pass
        try:
            commvault_credit['hostusername'] = doc.xpath('//hostusername/text()')[0]
        except:
            pass
        try:
            commvault_credit['hostpasswd'] = base64.b64decode(doc.xpath('//hostpasswd/text()')[0]).decode()
        except:
            pass
        try:
            commvault_credit['username'] = doc.xpath('//username/text()')[0]
        except:
            pass
        try:
            commvault_credit['passwd'] = base64.b64decode(doc.xpath('//passwd/text()')[0]).decode()
        except:
            pass

        # SQL Server账户信息
        try:
            sqlserver_credit['SQLServerHost'] = doc.xpath('//SQLServerHost/text()')[0]
        except:
            pass
        try:
            sqlserver_credit['SQLServerUser'] = doc.xpath('//SQLServerUser/text()')[0]
        except:
            pass
        try:
            sqlserver_credit['SQLServerPasswd'] = base64.b64decode(
                doc.xpath('//SQLServerPasswd/text()')[0]).decode()
        except:
            pass
        try:
            sqlserver_credit['SQLServerDataBase'] = doc.xpath('//SQLServerDataBase/text()')[0]
        except:
            pass

    except Exception as e:
        print(e)
    return commvault_credit, sqlserver_credit


@login_required
def util_manage_data(request):
    """
    工具管理信息
    """
    util_manage_list = []

    util_manages = UtilsManage.objects.exclude(state='9')

    for um in util_manages:
        commvault_credit = {
            'webaddr': '',
            'port': '',
            'hostusername': '',
            'hostpasswd': '',
            'username': '',
            'passwd': '',
        }
        sqlserver_credit = {
            'SQLServerHost': '',
            'SQLServerUser': '',
            'SQLServerPasswd': '',
            'SQLServerDataBase': '',
        }
        if um.util_type.upper() == 'COMMVAULT':
            commvault_credit, sqlserver_credit = get_credit_info(um.content)

        util_manage_list.append({
            'id': um.id,
            'code': um.code,
            'name': um.name,
            'util_type': um.util_type,
            'commvault_credit': commvault_credit,
            'sqlserver_credit': sqlserver_credit
        })

    return JsonResponse({"data": util_manage_list})


@login_required
def util_manage_save(request):
    status = 1
    info = '保存成功。'

    util_manage_id = request.POST.get('util_manage_id', '')

    util_type = request.POST.get('util_type', '')
    code = request.POST.get('code', '')
    name = request.POST.get('name', '')

    webaddr = request.POST.get('webaddr', '')
    port = request.POST.get('port', '')
    hostusername = request.POST.get('hostusernm', '')
    hostpasswd = request.POST.get('hostpasswd', '')
    username = request.POST.get('usernm', '')
    passwd = request.POST.get('passwd', '')

    SQLServerHost = request.POST.get('SQLServerHost', '')
    SQLServerUser = request.POST.get('SQLServerUser', '')
    SQLServerPasswd = request.POST.get('SQLServerPasswd', '')
    SQLServerDataBase = request.POST.get('SQLServerDataBase', '')

    credit = ''

    try:
        util_manage_id = int(util_manage_id)
    except:
        status = 0
        info = '网络异常。'
    else:
        if not util_type.strip():
            status = 0
            info = '工具类型未选择。'
        elif not code.strip():
            status = 0
            info = '工具编号未填写。'
        elif not name.strip():
            status = 0
            info = '工具名称未填写。'
        elif UtilsManage.objects.exclude(state='9').exclude(id=util_manage_id).filter(code=code).exists():
            status = 0
            info = '工具编号已存在。'
        else:
            if util_type.strip().upper() == 'COMMVAULT':
                credit = """<?xml version="1.0" ?>
                    <vendor>
                        <webaddr>{webaddr}</webaddr>
                        <port>{port}</port>
                        <hostusername>{hostusername}</hostusername>
                        <hostpasswd>{hostpasswd}</hostpasswd>
                        <username>{username}</username>
                        <passwd>{passwd}</passwd>
                        <SQLServerHost>{SQLServerHost}</SQLServerHost>
                        <SQLServerUser>{SQLServerUser}</SQLServerUser>
                        <SQLServerPasswd>{SQLServerPasswd}</SQLServerPasswd>
                        <SQLServerDataBase>{SQLServerDataBase}</SQLServerDataBase>
                    </vendor>""".format(**{
                    "webaddr": webaddr,
                    "port": port,
                    "hostusername": hostusername,
                    "hostpasswd": base64.b64encode(hostpasswd.encode()).decode(),
                    "username": username,
                    "passwd": base64.b64encode(passwd.encode()).decode(),
                    "SQLServerHost": SQLServerHost,
                    "SQLServerUser": SQLServerUser,
                    "SQLServerPasswd": base64.b64encode(SQLServerPasswd.encode()).decode(),
                    "SQLServerDataBase": SQLServerDataBase
                })
            try:
                cur_util_manage = UtilsManage.objects.filter(id=util_manage_id)
                if cur_util_manage.exists():
                    cur_util_manage.update(**{
                        'util_type': util_type,
                        'code': code,
                        'name': name,
                        'content': credit
                    })
                else:
                    cur_util_manage.create(**{
                        'util_type': util_type,
                        'code': code,
                        'name': name,
                        'content': credit
                    })
            except Exception as e:
                print(e)
                status = 0
                info = '保存失败。'

    return JsonResponse({
        'status': status,
        'info': info,
    })


@login_required
def util_manage_del(request):
    status = 1
    info = '删除成功。'
    util_manage_id = request.POST.get('util_manage_id', '')

    try:
        util_manage_id = int(util_manage_id)
    except:
        status = 0
        info = '网络异常。'
    else:
        util_manage = UtilsManage.objects.filter(id=util_manage_id)
        if util_manage.exists():
            util_manage.update(**{'state': '9'})
        else:
            status = 0
            info = '该工具不存在，删除失败。'
    return JsonResponse({
        'status': status,
        'info': info
    })



