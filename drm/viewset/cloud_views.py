# 流程配置：场景配置、脚本配置、流程配置、主机配置
from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404, HttpResponse, JsonResponse
from TSDRM import settings

from .commv_views import *
from .basic_views import getpagefuns
from django.contrib.auth.decorators import login_required

from ..remote import ServerByPara
from ..api.kvm import libvirtApi


######################
# 虚拟机管理
######################
def kvm_credit_data(utils_id):
    utils_kvm_info = UtilsManage.objects.filter(id=utils_id)
    content = utils_kvm_info[0].content
    util_type = utils_kvm_info[0].util_type
    kvm_credit = get_credit_info(content, util_type.upper())
    return kvm_credit


@login_required
def kvm_manage(request, funid):
    util_manage = UtilsManage.objects.filter(util_type='Kvm').exclude(state='9')
    utils_kvm_list = []
    for utils in util_manage:
        utils_kvm_list.append({
            "id": utils.id,
            "code": utils.code,
            "name": utils.name,
        })
    return render(request, 'kvm_manage.html',
                  {'username': request.user.userinfo.fullname,
                   "pagefuns": getpagefuns(funid, request=request),
                   "utils_kvm_list": utils_kvm_list,
                   })


def get_kvm_copy_node(utils_id, parent, kvm_credit, finalOutput):
    datas = []
    children = []
    for i in finalOutput:
        if i['code'] == 'kvmlistonlycopy':
            for name in i['value']:
                if parent + '@' in name['name']:
                    children = i['value']
    for child in children:
        data = dict()
        data['state'] = {'opened': 'True'}
        data['data'] = {
            'id': child['id'],
            'utils_id': utils_id,
            'name': child['name'],
            'state': child['state'],
            'pname': parent,
        }
        if child['state'] == '运行中':
            data['text'] = "<span class='fa fa-desktop' style='color:green; height:24px;'></span> " + child['name']
        else:
            data['text'] = "<span class='fa fa-desktop' style='color:red; height:24px;'></span> " + child['name']
        data['type'] = 'COPY'
        data['ip'] = kvm_credit['KvmHost']
        datas.append(data)
    return datas


def get_kvm_node(utils_id, parent, kvm_credit, children, finalOutput):
    nodes = []
    for child in children:
        node = dict()
        node['state'] = {'opened': 'True'}
        node['data'] = {
            'id': child['id'],
            'utils_id': utils_id,
            'name': child['name'],
            'state': child['state'],
            'pname': parent,
        }
        if child['state'] == '运行中':
            node['text'] = "<span class='fa fa-desktop' style='color:green; height:24px;'></span> " + child['name']
        else:
            node['text'] = "<span class='fa fa-desktop' style='color:red; height:24px;'></span> " + child['name']
        node['type'] = 'KVM'
        node['ip'] = kvm_credit['KvmHost']

        # 获取三级菜单：实例虚拟机
        node["children"] = get_kvm_copy_node(utils_id, child['name'], kvm_credit, finalOutput)
        nodes.append(node)
    return nodes


@login_required
def get_kvm_tree(request):
    # 循环一级菜单工具管理：kvm
    util_manage = UtilsManage.objects.filter(util_type='Kvm').exclude(state='9')
    tree_data = []
    for utils in util_manage:
        utils_id = utils.id
        kvm_credit = kvm_credit_data(utils_id)
        root = dict()
        root["text"] = "<img src = '/static/pages/images/ts.png' height='24px'> " + utils.code,
        root['id'] = utils.id
        root['state'] = {'opened': 'True'}
        root['data'] = {
            'utils_id': utils.id,
            'name': utils.name,
            'pname': '无',
        }
        root['kvm_credit'] = kvm_credit
        # 获取kvm模板文件
        kvm_template_guid = '0f298100-9b31-11eb-849b-000c29921d27'
        kvm_template_input = [{"code": "ip", "value": kvm_credit['KvmHost']},
                {"code": "username", "value": kvm_credit['KvmUser']},
                {"code": "password", "value": kvm_credit['KvmPasswd']}]
        newJob = Job(userid=request.user.id)
        state = newJob.execute_workflow(kvm_template_guid, input=kvm_template_input)
        if state == 'NOTEXIST':
            return JsonResponse({
                "ret": 0,
                "data": "组件不存在，请于管理员联系。",
            })
        elif state == 'ERROR':
            return JsonResponse({
                "ret": 0,
                "data": newJob.jobBaseInfo['log'],
            })
        else:
            for i in newJob.finalOutput:
                if i['code'] == 'templatefile':
                    root['kvm_template'] = i['value']
        root['type'] = 'ROOT'
        # 循环二级菜单：虚拟机
        children = []
        kvm_list_guid = '73c5e79c-979a-11eb-ac18-000c29921d27'
        kvm_list_input = [{"code": "ip", "value": kvm_credit['KvmHost']},
                 {"code": "username", "value": kvm_credit['KvmUser']},
                 {"code": "password", "value": kvm_credit['KvmPasswd']}]
        newJob = Job(userid=request.user.id)
        state = newJob.execute_workflow(kvm_list_guid, input=kvm_list_input)
        if state == 'NOTEXIST':
            return JsonResponse({
                "ret": 0,
                "data": "组件不存在，请于管理员联系。",
            })
        elif state == 'ERROR':
            return JsonResponse({
                "ret": 0,
                "data": newJob.jobBaseInfo['log'],
            })
        else:
            for i in newJob.finalOutput:
                if i['code'] == 'kvmlistexcludecopy':
                    children = i['value']
        root["children"] = get_kvm_node(utils.id, utils.code, kvm_credit, children, newJob.finalOutput)
        tree_data.append(root)
    return JsonResponse({
        "ret": 1,
        "data": tree_data
    })


@login_required
def get_kvm_detail(request):
    utils_id = request.POST.get("utils_id", "")
    kvm_id = request.POST.get("kvm_id", "")
    kvm_name = request.POST.get("kvm_name", "")
    ret = 1
    try:
        utils_id = int(utils_id)
    except:
        pass
    kvm_credit = kvm_credit_data(utils_id)
    try:
        # 通过传参判断点击节点类型：点击根节点：kvm_name=='' and kvm_id==''，
        # 点击kvm虚拟机节点：kvm_name=='Test-1' and kvm_id=='1'
        if kvm_name == '' and kvm_id == '':
            memory_disk_cpu_data = []
            # 宿主机资源监控组件
            host_guid = 'cc4e507c-9b35-11eb-b93f-000c29921d27'
            host_input = [{"code": "ip", "value": kvm_credit['KvmHost']},
                              {"code": "username", "value": kvm_credit['KvmUser']},
                              {"code": "password", "value": kvm_credit['KvmPasswd']}]
            newJob = Job(userid=request.user.id)
            state = newJob.execute_workflow(host_guid, input=host_input)
            if state == 'NOTEXIST':
                return JsonResponse({
                    "ret": 0,
                    "data": "组件不存在，请于管理员联系。",
                })
            elif state == 'ERROR':
                return JsonResponse({
                    "ret": 0,
                    "data": newJob.jobBaseInfo['log'],
                })
            else:
                for i in newJob.finalOutput:
                    if i['code'] == 'diskcpumemory':
                        memory_disk_cpu_data = i['value']
            data = {
                    'memory_disk_cpu_data': memory_disk_cpu_data
                    }
        # kvm虚拟机磁盘文件信息：cpu、内存、磁盘
        else:
            ip = ''
            hostname = ''
            password = ''
            # 从数据库获取虚机的ip、密码、主机名
            kvm_data = KvmCopy.objects.exclude(state='9').filter(name=kvm_name).filter(utils_id=utils_id)
            if kvm_data.exists():
                ip = kvm_data[0].ip
                hostname = kvm_data[0].hostname
                password = kvm_data[0].password

            kvm_info_data = []
            kvm_diskcpumemory_data = []
            # 虚机硬件资源信息组件
            kvm_info_guid = '0cf3fd1e-9813-11eb-a964-000c29921d27'
            kvm_info_input = [{"code": "ip", "value": kvm_credit['KvmHost']},
                          {"code": "kvm_name", "value": kvm_name}]
            newJob = Job(userid=request.user.id)
            state = newJob.execute_workflow(kvm_info_guid, input=kvm_info_input)
            if state == 'NOTEXIST':
                return JsonResponse({
                    "ret": 0,
                    "data": "组件不存在，请于管理员联系。",
                })
            elif state == 'ERROR':
                return JsonResponse({
                    "ret": 0,
                    "data": newJob.jobBaseInfo['log'],
                })
            else:
                for i in newJob.finalOutput:
                    if i['code'] == 'kvminfo':
                        kvm_info_data = i['value']

            # 虚机资源消耗情况组件
            diskcpumem_guid = '798bbe14-98d4-11eb-9499-000c29921d27'
            diskcpumem_input = [{"code": "ip", "value": kvm_credit['KvmHost']},
                                {"code": "kvm_name", "value": kvm_name}]
            newJob = Job(userid=request.user.id)
            state = newJob.execute_workflow(diskcpumem_guid, input=diskcpumem_input)
            if state == 'NOTEXIST':
                return JsonResponse({
                    "ret": 0,
                    "data": "组件不存在，请于管理员联系。",
                })
            elif state == 'ERROR':
                return JsonResponse({
                    "ret": 0,
                    "data": newJob.jobBaseInfo['log'],
                })
            else:
                for i in newJob.finalOutput:
                    if i['code'] == 'kvmdiskcpumemory':
                        kvm_diskcpumemory_data = i['value']
            data = {
                'kvm_info_data': kvm_info_data,
                'kvm_diskcpumemory_data': kvm_diskcpumemory_data,
                'ip': ip,
                'hostname': hostname,
                'password': password
            }
    except Exception as e:
        print(e)
        ret = 0
        data = '获取信息失败。'
    return JsonResponse({
        'ret': ret,
        'data': data})


# 执行组件，获取KVM虚拟机资源消耗情况
@login_required
def get_kvm_task_data(request):
    kvm_name = request.POST.get("kvm_name", "")
    utils_ip = request.POST.get("utils_ip", "")
    ret = 1
    try:
        kvm_diskcpumemory_data = []
        diskcpumem_guid = '798bbe14-98d4-11eb-9499-000c29921d27'
        diskcpumem_input = [{"code": "ip", "value": utils_ip},
                            {"code": "kvm_name", "value": kvm_name}]
        newJob = Job(userid=request.user.id)
        state = newJob.execute_workflow(diskcpumem_guid, input=diskcpumem_input)
        if state == 'NOTEXIST':
            return JsonResponse({
                "ret": 0,
                "data": "组件不存在，请于管理员联系。",
            })
        elif state == 'ERROR':
            return JsonResponse({
                "ret": 0,
                "data": newJob.jobBaseInfo['log'],
            })
        else:
            for i in newJob.finalOutput:
                if i['code'] == 'kvmdiskcpumemory':
                    kvm_diskcpumemory_data = i['value']
        data = {
            'kvm_cpu_mem_data': kvm_diskcpumemory_data,
        }
    except Exception as e:
        print(e)
        ret = 0
        data = '获取信息失败。'
    return JsonResponse({
        'ret': ret,
        'data': data})


# 执行组件，开启KVM虚拟机
@login_required
def kvm_start(request):
    utils_id = request.POST.get("utils_id", "")
    kvm_name = request.POST.get("kvm_name", "")
    kvm_id = ""
    ret = 1
    try:
        utils_id = int(utils_id)
    except:
        pass
    kvm_credit = kvm_credit_data(utils_id)
    try:
        start_giid = 'b1d51880-9751-11eb-afc2-a4bb6d10e0ef'
        start_input = [{"code": "ip", "value": kvm_credit['KvmHost']},
                        {"code": "kvm_name", "value": kvm_name}]
        newJob = Job(userid=request.user.id)
        state = newJob.execute_workflow(start_giid, input=start_input)
        if state == 'NOTEXIST':
            return JsonResponse({
                "ret": 0,
                "data": "组件不存在，请于管理员联系。",
            })
        elif state == 'ERROR':
            return JsonResponse({
                "ret": 0,
                "data": newJob.jobBaseInfo['log'],
            })
        else:
            data = '给电成功。'
            for i in newJob.finalOutput:
                if i['code'] == 'kvmid':
                    kvm_id = i['value']
    except Exception as e:
        print(e)
        ret = 0
        data = '给电失败。'
    return JsonResponse({
        'ret': ret,
        'data': data,
        'kvm_id': kvm_id
    })


# 执行组件，断电KVM虚拟机
@login_required
def kvm_destroy(request):
    utils_id = request.POST.get("utils_id", "")
    kvm_name = request.POST.get("kvm_name", "")
    kvm_id = ""
    ret = 1
    try:
        utils_id = int(utils_id)
    except:
        pass
    kvm_credit = kvm_credit_data(utils_id)
    try:
        destroy_giid = 'a55d4a56-9791-11eb-b36d-000c29921d27'
        destroy_input = [{"code": "ip", "value": kvm_credit['KvmHost']},
                       {"code": "kvm_name", "value": kvm_name}]
        newJob = Job(userid=request.user.id)
        state = newJob.execute_workflow(destroy_giid, input=destroy_input)
        if state == 'NOTEXIST':
            return JsonResponse({
                "ret": 0,
                "data": "组件不存在，请于管理员联系。",
            })
        elif state == 'ERROR':
            return JsonResponse({
                "ret": 0,
                "data": newJob.jobBaseInfo['log'],
            })
        else:
            data = '断电成功。'
            for i in newJob.finalOutput:
                if i['code'] == 'kvmid':
                    kvm_id = i['value']
    except Exception as e:
        print(e)
        ret = 0
        data = '断电失败。'
    return JsonResponse({
        'ret': ret,
        'data': data,
        'kvm_id': kvm_id
    })


# 执行组件，关闭KVM虚拟机
@login_required
def kvm_shutdown(request):
    utils_id = request.POST.get("utils_id", "")
    kvm_name = request.POST.get("kvm_name", "")
    kvm_id = ""
    ret = 1
    try:
        utils_id = int(utils_id)
    except:
        pass
    kvm_credit = kvm_credit_data(utils_id)
    try:
        shutdown_giid = '101e2c5e-9795-11eb-9921-000c29921d27'
        shutdown_input = [{"code": "ip", "value": kvm_credit['KvmHost']},
                         {"code": "kvm_name", "value": kvm_name}]
        newJob = Job(userid=request.user.id)
        state = newJob.execute_workflow(shutdown_giid, input=shutdown_input)
        if state == 'NOTEXIST':
            return JsonResponse({
                "ret": 0,
                "data": "组件不存在，请于管理员联系。",
            })
        elif state == 'ERROR':
            return JsonResponse({
                "ret": 0,
                "data": newJob.jobBaseInfo['log'],
            })
        else:
            data = '关闭成功。'
            for i in newJob.finalOutput:
                if i['code'] == 'kvmid':
                    kvm_id = i['value']
    except Exception as e:
        print(e)
        ret = 0
        data = '关闭成功。'
    return JsonResponse({
        'ret': ret,
        'data': data,
        'kvm_id': kvm_id
    })


# 执行组件，暂停KVM虚拟机
@login_required
def kvm_suspend(request):
    utils_id = request.POST.get("utils_id", "")
    kvm_name = request.POST.get("kvm_name", "")
    kvm_id = ""
    ret = 1
    try:
        utils_id = int(utils_id)
    except:
        pass
    kvm_credit = kvm_credit_data(utils_id)
    try:
        suspend_giid = '7db3a31e-980f-11eb-91cc-000c29921d27'
        suspend_input = [{"code": "ip", "value": kvm_credit['KvmHost']},
                          {"code": "kvm_name", "value": kvm_name}]
        newJob = Job(userid=request.user.id)
        state = newJob.execute_workflow(suspend_giid, input=suspend_input)
        if state == 'NOTEXIST':
            return JsonResponse({
                "ret": 0,
                "data": "组件不存在，请于管理员联系。",
            })
        elif state == 'ERROR':
            return JsonResponse({
                "ret": 0,
                "data": newJob.jobBaseInfo['log'],
            })
        else:
            data = '暂停成功。'
            for i in newJob.finalOutput:
                if i['code'] == 'kvmid':
                    kvm_id = i['value']
    except Exception as e:
        print(e)
        ret = 0
        data = '暂停失败。'
    return JsonResponse({
        'ret': ret,
        'data': data,
        'kvm_id': kvm_id
    })


# 执行组件，唤醒KVM虚拟机
@login_required
def kvm_resume(request):
    utils_id = request.POST.get("utils_id", "")
    kvm_name = request.POST.get("kvm_name", "")
    kvm_id = ""
    ret = 1
    try:
        utils_id = int(utils_id)
    except:
        pass
    kvm_credit = kvm_credit_data(utils_id)
    try:
        resume_giid = '9f1a12d0-9810-11eb-b3de-000c29921d27'
        resume_input = [{"code": "ip", "value": kvm_credit['KvmHost']},
                         {"code": "kvm_name", "value": kvm_name}]
        newJob = Job(userid=request.user.id)
        state = newJob.execute_workflow(resume_giid, input=resume_input)
        if state == 'NOTEXIST':
            return JsonResponse({
                "ret": 0,
                "data": "组件不存在，请于管理员联系。",
            })
        elif state == 'ERROR':
            return JsonResponse({
                "ret": 0,
                "data": newJob.jobBaseInfo['log'],
            })
        else:
            data = '唤醒成功。'
            for i in newJob.finalOutput:
                if i['code'] == 'kvmid':
                    kvm_id = i['value']
    except Exception as e:
        print(e)
        ret = 0
        data = '唤醒失败。'
    return JsonResponse({
        'ret': ret,
        'data': data,
        'kvm_id': kvm_id
    })


# 执行组件，重启KVM虚拟机
@login_required
def kvm_reboot(request):
    utils_id = request.POST.get("utils_id", "")
    kvm_name = request.POST.get("kvm_name", "")
    kvm_id = ""
    ret = 1
    try:
        utils_id = int(utils_id)
    except:
        pass
    kvm_credit = kvm_credit_data(utils_id)
    try:
        reboot_giid = '35017fd4-9796-11eb-9ff7-000c29921d27'
        reboot_input = [{"code": "ip", "value": kvm_credit['KvmHost']},
                         {"code": "kvm_name", "value": kvm_name}]
        newJob = Job(userid=request.user.id)
        state = newJob.execute_workflow(reboot_giid, input=reboot_input)
        if state == 'NOTEXIST':
            return JsonResponse({
                "ret": 0,
                "data": "组件不存在，请于管理员联系。",
            })
        elif state == 'ERROR':
            return JsonResponse({
                "ret": 0,
                "data": newJob.jobBaseInfo['log'],
            })
        else:
            data = '重启成功。'
            for i in newJob.finalOutput:
                if i['code'] == 'kvmid':
                    kvm_id = i['value']
    except Exception as e:
        print(e)
        ret = 0
        data = '重启失败。'
    return JsonResponse({
        'ret': ret,
        'data': data,
        'kvm_id': kvm_id
    })


# 执行组件、删除KVM虚拟机
# 步骤：删除虚拟机 + 删除文件系统 + 删除本地数据库数据
@login_required
def kvm_delete(request):
    utils_id = request.POST.get("utils_id", "")
    kvm_name = request.POST.get("kvm_name", "")
    ret = 1
    try:
        utils_id = int(utils_id)
    except:
        pass
    kvm_credit = kvm_credit_data(utils_id)
    try:
        delete_giid = '75d3413e-9799-11eb-b4e8-000c29921d27'
        delete_input = [{"code": "ip", "value": kvm_credit['KvmHost']},
                        {"code": "username", "value": kvm_credit['KvmUser']},
                        {"code": "password", "value": kvm_credit['KvmPasswd']},
                        {"code": "kvm_name", "value": kvm_name}]
        newJob = Job(userid=request.user.id)
        state = newJob.execute_workflow(delete_giid, input=delete_input)
        if state == 'NOTEXIST':
            return JsonResponse({
                "ret": 0,
                "data": "组件不存在，请于管理员联系。",
            })
        elif state == 'ERROR':
            return JsonResponse({
                "ret": 0,
                "data": newJob.jobBaseInfo['log'],
            })
        else:
            # 删除数据库数据:name为虚拟机的名称是唯一的
            kvmcopy = KvmCopy.objects.exclude(state='9').filter(name=kvm_name).filter(utils_id=utils_id)
            if kvmcopy.exists():
                kvm = kvmcopy[0]
                kvm.state = '9'
                kvm.save()
            data = '删除成功。'
    except Exception as e:
        print(e)
        ret = 0
        data = '删除失败。'
    return JsonResponse({
        'ret': ret,
        'data': data,
    })


# 执行组件，克隆KVM虚拟机
# 步骤：①关闭或者暂停状态 ②判断要克隆虚拟机是否存在 ③先创建文件系统 ④再执行克隆操作
@login_required
def kvm_clone_save(request):
    utils_id = request.POST.get("utils_id", "")
    kvm_name = request.POST.get("kvm_name", "")
    kvm_clone_name = request.POST.get("kvm_clone_name", "")
    ret = 1
    try:
        utils_id = int(utils_id)
    except:
        pass
    kvm_credit = kvm_credit_data(utils_id)
    if not kvm_clone_name.strip():
        return JsonResponse({
            "ret": 0,
            "data": "新虚拟机名称未填写。",
        })
    else:
        try:
            clone_giid = '6bab5454-9815-11eb-bc7a-000c29921d27'
            clone_input = [{"code": "ip", "value": kvm_credit['KvmHost']},
                           {"code": "username", "value": kvm_credit['KvmUser']},
                           {"code": "password", "value": kvm_credit['KvmPasswd']},
                           {"code": "kvm_name", "value": kvm_name},
                           {"code": "kvm_clone_name", "value": kvm_clone_name}]
            newJob = Job(userid=request.user.id)
            state = newJob.execute_workflow(clone_giid, input=clone_input)
            if state == 'NOTEXIST':
                return JsonResponse({
                    "ret": 0,
                    "data": "组件不存在，请于管理员联系。",
                })
            elif state == 'ERROR':
                return JsonResponse({
                    "ret": 0,
                    "data": newJob.jobBaseInfo['log'],
                })
            else:
                data = '克隆成功。'
        except Exception as e:
            print(e)
            ret = 0
            data = '克隆失败。'
    return JsonResponse({
        'ret': ret,
        'data': data,
        'utils_ip': kvm_credit['KvmHost'],
        'utils_id': utils_id

    })


# 执行组件，注册KVM虚拟机
# 模板中新建虚拟机：创建文件系统 + 拷贝模板文件到文件系统 + 生成新的xml文件 + 定义虚拟机
@login_required
def kvm_machine_create(request):
    utils_id = request.POST.get("utils_id", "")
    kvm_template_name = request.POST.get("kvm_template_name", "")
    kvm_name = request.POST.get("kvm_name", "")
    kvm_cpu = request.POST.get("kvm_cpu", "")
    kvm_memory = request.POST.get("kvm_memory", "")
    ret = 1
    try:
        utils_id = int(utils_id)
    except:
        pass
    kvm_credit = kvm_credit_data(utils_id)
    try:
        create_giid = '10825768-98d7-11eb-b09f-000c29921d27'
        create_input = [{"code": "ip", "value": kvm_credit['KvmHost']},
                        {"code": "username", "value": kvm_credit['KvmUser']},
                        {"code": "password", "value": kvm_credit['KvmPasswd']},
                        {"code": "kvm_template_name", "value": kvm_template_name},
                        {"code": "kvm_name", "value": kvm_name},
                        {"code": "kvm_cpu", "value": kvm_cpu},
                        {"code": "kvm_memory", "value": kvm_memory}]
        newJob = Job(userid=request.user.id)
        state = newJob.execute_workflow(create_giid, input=create_input)
        if state == 'NOTEXIST':
            return JsonResponse({
                "ret": 0,
                "data": "组件不存在，请于管理员联系。",
            })
        elif state == 'ERROR':
            return JsonResponse({
                "ret": 0,
                "data": newJob.jobBaseInfo['log'],
            })
        else:
            data = '注册成功。'
    except Exception as e:
        print(e)
        ret = 0
        data = '注册失败。'
    return JsonResponse({
        'ret': ret,
        'data': data,
        'utils_ip': kvm_credit['KvmHost'],
        'utils_id': utils_id
    })


# 执行组件，激活KVM虚拟机
# ①修改ip、密码、主机名 ②开启虚拟机 ③保存数据库
@login_required
def kvm_power(request):
    utils_id = request.POST.get("utils_id", "")
    kvm_name = request.POST.get("kvm_name", "")
    kvm_ip = request.POST.get("kvm_ip", "")
    kvm_hostname = request.POST.get("kvm_hostname", "")
    kvm_password = request.POST.get("kvm_password", "")
    user_id = request.user.id
    kvm_id = ''
    ret = 1
    try:
        user_id = int(user_id)
        utils_id = int(utils_id)
    except:
        pass
    kvm_credit = kvm_credit_data(utils_id)
    try:
        power_giid = '9a33ff3a-9b65-11eb-8467-000c29921d27'
        power_input = [{"code": "ip", "value": kvm_credit['KvmHost']},
                       {"code": "username", "value": kvm_credit['KvmUser']},
                       {"code": "password", "value": kvm_credit['KvmPasswd']},
                       {"code": "kvm_name", "value": kvm_name},
                       {"code": "kvm_ip", "value": kvm_ip},
                       {"code": "kvm_password", "value": kvm_password},
                       {"code": "kvm_hostname", "value": kvm_hostname}]
        newJob = Job(userid=request.user.id)
        state = newJob.execute_workflow(power_giid, input=power_input)
        if state == 'NOTEXIST':
            return JsonResponse({
                "ret": 0,
                "data": "组件不存在，请于管理员联系。",
            })
        elif state == 'ERROR':
            return JsonResponse({
                "ret": 0,
                "data": newJob.jobBaseInfo['log'],
            })
        else:
            kvm = KvmCopy.objects.exclude(state='9').filter(name=kvm_name).filter(utils_id=utils_id)
            if kvm.exists():
                kvm.update(**{
                    'name': kvm_name,
                    'create_time': datetime.datetime.now(),
                    'create_user_id': user_id,
                    'utils_id': utils_id,
                    'ip': kvm_ip,
                    'hostname': kvm_hostname,
                    'password': kvm_password
                })
            else:
                kvm.create(**{
                    'name': kvm_name,
                    'create_time': datetime.datetime.now(),
                    'create_user_id': user_id,
                    'utils_id': utils_id,
                    'ip': kvm_ip,
                    'hostname': kvm_hostname,
                    'password': kvm_password
                })
            data = '激活成功。'
            for i in newJob.finalOutput:
                if i['code'] == 'kvmid':
                    kvm_id = i['value']
    except Exception as e:
        print(e)
        ret = 0
        data = '激活失败。'
    return JsonResponse({
        'ret': ret,
        'data': data,
        'kvm_id': kvm_id,
        'ip': kvm_ip,
        'hostname': kvm_hostname,
        'password': kvm_password
    })


######################
# 模板管理
######################
def kvm_template(request, funid):
    util_manage = UtilsManage.objects.filter(util_type='Kvm').exclude(state='9')
    utils_kvm_list = []
    for utils in util_manage:
        utils_kvm_list.append({
            "id": utils.id,
            "code": utils.code,
            "name": utils.name,
        })
    return render(request, 'kvm_template.html',
                  {'username': request.user.userinfo.fullname,
                   "pagefuns": getpagefuns(funid, request=request),
                   "utils_kvm_list": utils_kvm_list,
                   })


def kvm_template_data(request):
    result = []
    all_template = DiskTemplate.objects.exclude(state='9')
    type_dict = {
        'os_image': '系统磁盘',
        'disk_image': '存储磁盘'
    }
    if len(all_template) > 0:
        for template in all_template:
            result.append({
                "id": template.id,
                "name": template.name,
                "file_name": template.file_name,
                "path": template.path,
                "type": type_dict[template.type],
                "os": template.os,
                "utils_name": template.utils.code if template.utils.code else '',
                "type_val": template.type,
                "utils_id": template.utils_id
            })
    return JsonResponse({"data": result})


def get_kvm_template(request):
    utils_id = request.POST.get("utils_id", "")
    try:
        utils_id = int(utils_id)
    except:
        pass
    ret = 1
    kvm_credit = kvm_credit_data(utils_id)
    try:
        data = libvirtApi.KVMApi(kvm_credit).all_kvm_template()
    except Exception as e:
        print(e)
        ret = 0
        data = '获取远程模板文件失败。'
    return JsonResponse({
        "ret": ret,
        "data": data,
    })


def kvm_template_save(request):
    if request.user.is_authenticated():
        result = {}
        id = request.POST.get("id", "")
        name = request.POST.get("name", "")
        utils_id = request.POST.get("utils_id", "")
        type = request.POST.get("type", "")
        path = request.POST.get("path", "")
        template_file = request.FILES.get("template_file", None)
        remote_template_file = request.POST.get("remote_template_file", "")
        file_name = template_file.name if template_file else ""
        try:
            id = int(id)
            utils_id = int(utils_id)
        except:
            raise Http404()
        # 判断是选择本地模板还是选择现有模板
        if remote_template_file == '':
            if not template_file and id == 0:
                result['res'] = '请选择要导入的文件。'
            else:
                if if_contains_sign(file_name):
                    result['res'] = r"""请注意文件命名格式，'\/"*?<>'符号文件不允许上传。"""
                else:
                    localfilepath = settings.BASE_DIR + os.sep + "drm" + os.sep + "upload" + os.sep + "disk_img" + os.sep + file_name
                    linuxfilepath = path + '/' + file_name
                    name_exist = DiskTemplate.objects.filter(name=name).filter(utils_id=utils_id).exclude(state="9")
                    # 新增时判断是否存在，修改时覆盖，不需要判断
                    if name_exist.exists() and id == 0:
                        result['res'] = '模板名称已存在。'
                    else:
                        if not name.strip():
                            result['res'] = '模板名称不能为空。'
                        elif not utils_id:
                            result['res'] = '模板平台未选择。'
                        elif not type.strip():
                            result['res'] = '模板类型未选择。'
                        elif not path.strip():
                            result['res'] = '模板路径未填写。'
                        else:
                            kvm_credit = kvm_credit_data(utils_id)

                            ip = kvm_credit['KvmHost']
                            username = kvm_credit['KvmUser']
                            password = kvm_credit['KvmPasswd']

                            # 新增 (且有my_file存在) 上传文件
                            if id == 0 and template_file:
                                name_exist = DiskTemplate.objects.filter(path=linuxfilepath).filter(utils_id=utils_id).exclude(state="9")
                                if name_exist.exists():
                                    result['res'] = '该文件已存在,请勿重复上传。'
                                else:
                                    try:
                                        with open(localfilepath, 'wb+') as f:
                                            for chunk in template_file.chunks():
                                                f.write(chunk)
                                    except Exception as e:
                                        print(e)
                                        result['res'] = '文件保存失败。'
                                    else:
                                        try:
                                            ssh = paramiko.Transport((ip, 22))
                                            ssh.connect(username=username, password=password)
                                            sftp = paramiko.SFTPClient.from_transport(ssh)
                                        except Exception as e:
                                            print(e)
                                            result['res'] = '保存失败。'
                                        else:
                                            try:
                                                sftp.put(localfilepath, linuxfilepath)
                                            except Exception as e:
                                                print(e)
                                                result['res'] = '保存失败'
                                            else:
                                                # 上传成功，数据库新增数据
                                                template_save = DiskTemplate()
                                                template_save.name = name
                                                template_save.file_name = file_name
                                                template_save.type = type
                                                template_save.path = linuxfilepath
                                                template_save.utils_id = utils_id
                                                template_save.save()
                                                result['res'] = '保存成功。'
                                            ssh.close()

        else:
            if not name.strip():
                result['res'] = '模板名称不能为空。'
            elif not utils_id:
                result['res'] = '模板平台未选择。'
            elif not type.strip():
                result['res'] = '模板类型未选择。'
            elif not path.strip():
                result['res'] = '模板路径未填写。'
            else:
                # 新增
                if id == 0:
                    name_exist = DiskTemplate.objects.filter(name=name).filter(utils_id=utils_id).exclude(state="9")
                    file_exist = DiskTemplate.objects.filter(path=path).filter(utils_id=utils_id).exclude(state="9")
                    if file_exist.exists():
                        result['res'] = '该文件已存在。'
                    elif name_exist.exists():
                        result['res'] = '模板名称已存在。'
                    else:
                        template_save = DiskTemplate()
                        template_save.name = name
                        template_save.file_name = remote_template_file
                        template_save.type = type
                        template_save.path = path
                        template_save.utils_id = utils_id
                        template_save.save()
                        result['res'] = '保存成功。'
                # 编辑
                else:
                    name_exist = DiskTemplate.objects.filter(name=name).filter(utils_id=utils_id).exclude(id=id).exclude(state="9")
                    file_exist = DiskTemplate.objects.filter(Q(path=path) | Q(path=path + '/' + remote_template_file)).\
                        filter(utils_id=utils_id).exclude(id=id).exclude(state="9")
                    if file_exist.exists():
                        result['res'] = '该文件已存在。'
                    elif name_exist.exists():
                        result['res'] = '模板名称已存在。'
                    else:
                        template_save = DiskTemplate.objects.get(id=id)
                        template_save.name = name
                        template_save.file_name = remote_template_file
                        template_save.type = type
                        template_save.utils_id = utils_id
                        # 判断是否修改了模板路径和模板文件: 没有修改，路径不变
                        if template_save.path == path and template_save.file_name == remote_template_file:
                            template_save.path = path
                            template_save.save()
                            result['res'] = '保存成功。'
                        else:
                            if remote_template_file in path:
                                template_save.path = path
                                template_save.save()
                                result['res'] = '保存成功。'
                            else:
                                template_save.path = path + '/' + remote_template_file
                                template_save.save()
                                result['res'] = '保存成功。'
        return JsonResponse(result)


def kvm_template_del(request):
    # 删除模板文件： 删除远程数据 + 删除数据库数据
    id = request.POST.get("id", "")
    path = request.POST.get("path", "")
    utils_id = request.POST.get("utils_id", "")
    try:
        id = int(id)
        utils_id = int(utils_id)
    except:
        pass
    status = 1
    kvm_credit = kvm_credit_data(utils_id)
    try:
        info = libvirtApi.KVMApi(kvm_credit).del_kvm_template(path)
        if info == '删除成功。':
            template_save = DiskTemplate.objects.get(id=id)
            template_save.state = "9"
            template_save.save()
            result = '删除成功。'
        else:
            status = 0
            result = '删除失败。'
    except Exception as e:
        print(e)
        status = 0
        result = '删除失败。'
    return JsonResponse({
        "status": status,
        "data": result,
    })