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
# 宿主机IP，用户名、密码
######################
def kvm_credit_data(utils_id):
    utils_kvm_info = UtilsManage.objects.filter(id=utils_id)
    content = utils_kvm_info[0].content
    util_type = utils_kvm_info[0].util_type
    kvm_credit = get_credit_info(content, util_type.upper())
    return kvm_credit


######################
# 客户端管理
######################
@login_required
def client_manage(request, funid):
    # kvm虚拟化平台
    util_manage = UtilsManage.objects.filter(util_type='Kvm').exclude(state='9')
    utils_kvm_list = []
    for utils in util_manage:
        utils_kvm_list.append({
            "id": utils.id,
            "code": utils.code,
            "name": utils.name,
        })
    return render(request, 'client_manage.html',
                  {'username': request.user.userinfo.fullname,
                   "pagefuns": getpagefuns(funid, request=request),
                   "utils_kvm_list": utils_kvm_list,
                   "is_superuser": request.user.is_superuser
                   })


@login_required
def kvm_data(request):
    util_manage = UtilsManage.objects.filter(util_type='Kvm').exclude(state='9')
    all_kvm_dict = {}
    for utils in util_manage:
        utils_id = utils.id
        kvm_credit = kvm_credit_data(utils_id)
        try:
            kvm_list = libvirtApi.KVMApi(kvm_credit).kvm_exclude_copy_list()
            all_kvm_dict[utils_id] = kvm_list
        except Exception as e:
            print(e)
            return JsonResponse({
                "ret": 0,
                "data": "获取kvm虚拟机失败。",
            })
    return JsonResponse({'all_kvm_dict': all_kvm_dict})


@login_required
def kvm_machine_data(request):
    kvminfo = {}
    id = request.POST.get("id", "")
    utils_id = request.POST.get("utils_id", "")
    try:
        id = int(id)
        utils_id = int(utils_id)
    except:
        pass
    kc = KvmMachine.objects.exclude(state="9").filter(hostsmanage_id=id).filter(utils_id=utils_id)
    if len(kc) > 0:
        kvminfo["id"] = kc[0].id
        kvminfo["utils_id"] = kc[0].utils_id
        kvminfo["name"] = kc[0].name
        kvminfo["filesystem"] = kc[0].filesystem
    return JsonResponse({'ret': 1, 'kvminfo': kvminfo})


@login_required
def kvm_save(request):
    hostsmanage_id = request.POST.get("hostsmanage_id", "")
    id = request.POST.get("kvm_id", "")
    utils_id = request.POST.get("util_kvm_id", "")
    name = request.POST.get("name", "")
    try:
        hostsmanage_id = int(hostsmanage_id)
        id = int(id)
        utils_id = int(utils_id)
    except:
        status = 0
        info = '网络异常。'
    else:
        if not utils_id:
            status = 0
            info = '虚拟化平台未选择。'
        elif not name.strip():
            status = 0
            info = '虚机未选择。'
        else:
            # 新增
            if id == 0:
                try:
                    kvmmachine = KvmMachine()
                    kvmmachine.utils_id = utils_id
                    kvmmachine.hostsmanage_id = hostsmanage_id
                    kvmmachine.name = name
                    kvmmachine.save()
                    id = kvmmachine.id
                    status = 1
                    info = "保存成功。"
                except:
                    status = 0
                    info = "服务器异常。"
            # 修改
            else:
                try:
                    kvmmachine = KvmMachine.objects.get(id=id)
                    kvmmachine.utils_id = utils_id
                    kvmmachine.hostsmanage_id = hostsmanage_id
                    kvmmachine.name = name
                    kvmmachine.save()
                    id = kvmmachine.id
                    status = 1
                    info = "修改成功。"
                except:
                    status = 0
                    info = "服务器异常。"
    return JsonResponse({
        'status': status,
        'info': info,
        'id': id
    })


@login_required
def kvm_del(request):
    if 'id' in request.POST:
        id = request.POST.get('id', '')
        try:
            id = int(id)
        except:
            return HttpResponse(0)
        kvm = KvmMachine.objects.get(id=id)
        kvm.state = '9'
        kvm.save()
        return HttpResponse(1)
    else:
        return HttpResponse(0)


@login_required
def kvm_copy_create(request):
    result = {}
    utils_id = request.POST.get("utils_id", "")
    snapshot_name = request.POST.get("snapshot_name", "")
    copy_name = request.POST.get("kvm_copy_name", "")
    kvm_machine = request.POST.get("kvm_machine", "")
    kvm_machine_id = request.POST.get("kvm_machine_id", "")
    copy_cpu = request.POST.get("kvm_copy_cpu", "")
    copy_memory = request.POST.get("kvm_copy_memory", "")
    user_id = request.user.id
    try:
        user_id = int(user_id)
        kvm_machine_id = int(kvm_machine_id)
        utils_id = int(utils_id)
    except:
        pass
    if not copy_name.strip():
        result['res'] = '实例名称未填写。'
    else:
        kvm_credit = kvm_credit_data(utils_id)
        # 拼接路径
        filesystem = 'data/vmdata/' + kvm_machine        # data/vmdata/CentOS-7
        snapshotname = filesystem + '@' + snapshot_name  # data/vmdata/CentOS-7@2020-07-28
        filesystemname = filesystem + ':' + copy_name    # data/vmdata/CentOS-7:2020-07-28
        copyname = kvm_machine + '@' + copy_name         # CentOS-7@2020-07-28
        try:
            kvm_exist = []
            kvm_list = libvirtApi.KVMApi(kvm_credit).kvm_all_list()
            for i in kvm_list:
                kvm_exist.append(i['name'])
            if copyname in kvm_exist:
                result['res'] = '实例' + copy_name + '已存在。'
            else:
                # ①创建快照
                result_info = libvirtApi.KVMApi(kvm_credit).zfs_create_snapshot(snapshotname)
                if result_info == '创建成功。':
                    # ②克隆快照，生成新的文件系统
                    result_info = libvirtApi.KVMApi(kvm_credit).zfs_clone_snapshot(snapshotname, filesystemname)
                    if result_info == '克隆成功。':
                        # ③克隆成功，生成新的xml文件
                        result_info = libvirtApi.KVMApi(kvm_credit).create_kvm_xml(kvm_machine, snapshotname, copyname, copy_cpu, copy_memory)
                        if result_info == '生成成功。':
                            # ④新的xml文件生成，开始定义虚拟机
                            result_info = libvirtApi.KVMApi(kvm_credit).define_kvm(copyname)
                            if result_info == '定义成功。':
                                # ④定义成功，保存数据库
                                try:
                                    KvmCopy.objects.create(**{
                                        'name': copyname,
                                        'create_time': datetime.datetime.now(),
                                        'create_user_id': user_id,
                                        'utils_id': utils_id,
                                        'kvmmachine_id': kvm_machine_id,
                                        'snapshot': snapshotname,
                                    })
                                    result['res'] = '创建成功。'
                                except Exception as e:
                                    print(e)
                                    result['res'] = '保存失败。'
                            else:
                                result['res'] = '定义失败。'
                        else:
                            result['res'] = '生成失败。'
                    else:
                        result['res'] = '克隆失败。'
                else:
                    result['res'] = '创建失败。'
        except Exception as e:
            print(e)
            result['res'] = '创建失败。'
    return JsonResponse(result)


@login_required
def kvm_copy_data(request):
    kvmmachine_id = request.GET.get("kvmmachine_id", "")
    utils_id = request.GET.get("utils_id", "")
    try:
        utils_id = int(utils_id)
        kvmmachine_id = int(kvmmachine_id)
    except:
        pass
    kvm_credit = kvm_credit_data(utils_id)
    utils_ip = kvm_credit['KvmHost']
    result = []
    all_kvmcopy = KvmCopy.objects.filter(kvmmachine_id=kvmmachine_id).filter(utils_id=utils_id).order_by('-create_time').exclude(state='9')
    if len(all_kvmcopy) > 0:
        for kvmcopy in all_kvmcopy:
            copy_state = libvirtApi.LibvirtApi(utils_ip).kvm_state(kvmcopy.name)
            result.append({
                "id": kvmcopy.id,
                "name": kvmcopy.name,
                "ip": kvmcopy.ip,
                "hostname": kvmcopy.hostname,
                "password": kvmcopy.password,
                "create_time": kvmcopy.create_time.strftime(
                                '%Y-%m-%d %H:%M:%S') if kvmcopy.create_time else '',
                "create_user": kvmcopy.create_user.userinfo.fullname if kvmcopy.create_user.userinfo.fullname else '',
                "copy_state": copy_state,
                "snapshot": kvmcopy.snapshot,
            })
    return JsonResponse({"data": result})


@login_required
def kvm_copy_del(request):
    # 删除副本：删除虚拟机 + 删除文件系统 + 删除快照 + 删除本地数据库数据
    result = {}
    id = request.POST.get("id", "")
    utils_id = request.POST.get("utils_id", "")
    name = request.POST.get("name", "")
    state = request.POST.get("state", "")
    try:
        id = int(id)
        utils_id = int(utils_id)
    except:
        pass
    kvm_credit = kvm_credit_data(utils_id)
    utils_ip = kvm_credit['KvmHost']
    filesystem_snapshot = 'data/vmdata/' + name         # data/vmdata/CentOS-7@test2    快照
    filesystem = filesystem_snapshot.replace('@', ':')  # data/vmdata/CentOS-7:test2    文件系统
    try:
        # ①删除虚拟机
        result_info = libvirtApi.LibvirtApi(utils_ip).kvm_undefine(state, name)
        if result_info == '取消定义成功。':
            # ②删除文件系统
            result_info = libvirtApi.KVMApi(kvm_credit).filesystem_del(filesystem)
            if result_info == '删除文件系统成功。':
                # ③删除快照
                result_info = libvirtApi.KVMApi(kvm_credit).zfs_snapshot_del(filesystem_snapshot)
                if result_info == '删除快照成功。':
                    # ④删除数据库数据
                    kvmcopy = KvmCopy.objects.get(id=id)
                    kvmcopy.state = '9'
                    kvmcopy.save()
                    result["res"] = '删除成功。'
                else:
                    result["res"] = result_info
            else:
                result["res"] = result_info
        else:
            result["res"] = result_info
    except Exception as e:
        print(e)
        result["res"] = '删除失败。'

    return JsonResponse(result)


@login_required
def kvm_power_on(request):
    # 给电：修改ip、主机名、root密码，开启虚拟机
    result = {}
    utils_id = request.POST.get("utils_id", "")
    copy_id = request.POST.get("id", "")
    copy_name = request.POST.get("copy_name", "")
    copy_state = request.POST.get("copy_state", "")
    kvm_machine = request.POST.get("kvm_machine", "")
    copy_ip = request.POST.get("copy_ip", "")
    copy_hostname = request.POST.get("copy_hostname", "")
    copy_password = request.POST.get("copy_password", "")
    compile_ip = re.compile('^(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|[1-9])\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)$')
    try:
        utils_id = int(utils_id)
    except:
        pass
    if not copy_ip.strip():
        result['res'] = '实例IP未填写。'
    elif not copy_hostname.strip():
        result['res'] = '实例主机名未填写。'
    elif not copy_password.strip():
        result['res'] = '实例密码未填写。'
    elif not compile_ip.match(copy_ip):
        result['res'] = '实例IP不合法。'
    else:
        kvm_credit = kvm_credit_data(utils_id)
        utils_ip = kvm_credit['KvmHost']
        # 拼接路径
        filesystem = 'data/vmdata/' + copy_name     # data/vmdata/CentOS-7@2020-09-14
        filesystem = filesystem.replace('@', ':')   # data/vmdata/CentOS-7:2020-09-14
        try:
            result_info = libvirtApi.KVMApi(kvm_credit).guestmount(kvm_machine, filesystem)
            if result_info == '挂载成功。':
                # ①挂载成功，修改ip和主机名
                result_info = libvirtApi.KVMApi(kvm_credit).alert_ip_hostname(copy_ip, copy_hostname)
                if result_info == '修改成功。':
                    # ②修改密码
                    result_info = libvirtApi.KVMApi(kvm_credit).alter_password(copy_password)
                    if result_info == '修改密码成功。':
                        # ③取消挂载
                        result_info = libvirtApi.KVMApi(kvm_credit).umount()
                        if result_info == '取消挂载成功。':
                            # ④开机
                            result_info = libvirtApi.LibvirtApi(utils_ip).kvm_start(copy_state, copy_name)
                            if result_info == '开机成功。':
                                # ⑤保存数据库
                                try:
                                    kvm_copy = KvmCopy.objects.get(id=copy_id)
                                    kvm_copy.ip = copy_ip
                                    kvm_copy.hostname = copy_hostname
                                    kvm_copy.password = copy_password
                                    kvm_copy.save()
                                    result['res'] = '给电成功。'
                                except Exception as e:
                                    print(e)
                                    result['res'] = '给电失败。'
                            else:
                                result['res'] = '开机失败。'
                        else:
                            result['res'] = '取消挂载失败。'
                    else:
                        result['res'] = '修改密码失败。'
                else:
                    result['res'] = '修改失败。'
            else:
                result['res'] = '挂载失败。'
        except Exception as e:
            print(e)
            result["res"] = '开机失败。'
    return JsonResponse(result)


@login_required
def kvm_start(request):
    utils_id = request.POST.get("utils_id", "")
    kvm_name = request.POST.get("kvm_name", "")
    kvm_state = request.POST.get("kvm_state", "")
    kvm_id = ""
    try:
        utils_id = int(utils_id)
    except:
        pass
    kvm_credit = kvm_credit_data(utils_id)
    utils_ip = kvm_credit['KvmHost']
    try:
        result = libvirtApi.LibvirtApi(utils_ip).kvm_start(kvm_state, kvm_name)
        kvm_id = libvirtApi.LibvirtApi(utils_ip).kvm_id(kvm_name)
    except Exception as e:
        print(e)
        result = '开机失败。'
    return JsonResponse({
        'res': result,
        'kvm_id': kvm_id
    })


@login_required
def kvm_destroy(request):
    utils_id = request.POST.get("utils_id", "")
    kvm_name = request.POST.get("kvm_name", "")
    kvm_state = request.POST.get("kvm_state", "")
    kvm_id = ""
    try:
        utils_id = int(utils_id)
    except:
        pass
    kvm_credit = kvm_credit_data(utils_id)
    utils_ip = kvm_credit['KvmHost']
    try:
        result = libvirtApi.LibvirtApi(utils_ip).kvm_destroy(kvm_state, kvm_name)
        kvm_id = libvirtApi.LibvirtApi(utils_ip).kvm_id(kvm_name)
    except Exception as e:
        print(e)
        result = '断电失败。'
    return JsonResponse({
        'res': result,
        'kvm_id': kvm_id
    })


######################
# 虚拟机管理
######################
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
    utils_ip = kvm_credit['KvmHost']
    try:
        # 通过传参判断点击节点类型：点击根节点：kvm_name=='' and kvm_id==''，点击kvm虚拟机节点：kvm_name=='Test-1' and kvm_id=='1'
        # 宿主机信息：cpu、内存、磁盘
        if kvm_name == '' and kvm_id == '':
            memory_disk_cpu_data = libvirtApi.KVMApi(kvm_credit).disk_cpu_data()
            memory_info = libvirtApi.LibvirtApi(utils_ip).mem_cpu_hostname_info()
            memory_disk_cpu_data['cpu_count'] = memory_info['cpu_count']
            memory_disk_cpu_data['hostname'] = memory_info['hostname']
            memory_disk_cpu_data['mem_total'] = memory_info['mem_total']
            memory_disk_cpu_data['mem_used'] = memory_info['mem_used']
            memory_disk_cpu_data['memory_usage'] = memory_info['memory_usage']
            data = {
                'memory_disk_cpu_data': memory_disk_cpu_data
            }
        # kvm虚拟机磁盘文件信息：cpu、内存、磁盘
        else:
            kvm_id = kvm_id.strip()
            ip = ''
            hostname = ''
            password = ''
            # 已开启的虚拟机有id，未开启的虚拟机id为-1
            if kvm_id != '-1':
                kvm_data = KvmCopy.objects.exclude(state='9').filter(name=kvm_name).filter(utils_id=utils_id)
                if kvm_data.exists():
                    ip = kvm_data[0].ip
                    hostname = kvm_data[0].hostname
                    password = kvm_data[0].password
                kvm_info_data = libvirtApi.LibvirtApi(utils_ip).kvm_info_data(kvm_name)
                kvm_disk_data = libvirtApi.LibvirtApi(utils_ip).kvm_disk_usage(kvm_name)
                kvm_cpu_mem_data = libvirtApi.LibvirtApi(utils_ip).kvm_memory_cpu_usage(kvm_id)
                data = {
                    'kvm_info_data': kvm_info_data,
                    'kvm_cpu_mem_data': kvm_cpu_mem_data,
                    'kvm_disk_data': kvm_disk_data,
                    'ip': ip,
                    'hostname': hostname,
                    'password': password
                }
            else:
                kvm_data = KvmCopy.objects.exclude(state='9').filter(name=kvm_name).filter(utils_id=utils_id)
                if kvm_data.exists():
                    ip = kvm_data[0].ip
                    hostname = kvm_data[0].hostname
                    password = kvm_data[0].password
                kvm_info_data = libvirtApi.LibvirtApi(utils_ip).kvm_info_data(kvm_name)
                kvm_disk_data = libvirtApi.LibvirtApi(utils_ip).kvm_disk_usage(kvm_name)
                data = {
                    'kvm_info_data': kvm_info_data,
                    'kvm_disk_data': kvm_disk_data,
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


@login_required
def get_kvm_task_data(request):
    # kvm虚拟机磁盘文件信息：cpu、内存、磁盘
    kvm_id = request.POST.get("kvm_id", "")
    utils_ip = request.POST.get("utils_ip", "")
    ret = 1
    data = ''
    kvm_id = kvm_id.strip()
    try:
        # 已开启的虚拟机有id，未开启的虚拟机id为-1
        if kvm_id != '-1':
            kvm_cpu_mem_data = libvirtApi.LibvirtApi(utils_ip).kvm_memory_cpu_usage(kvm_id)
            data = {
                'kvm_cpu_mem_data': kvm_cpu_mem_data,
            }
    except Exception as e:
        print(e)
        ret = 0
        data = '获取信息失败。'
    return JsonResponse({
        'ret': ret,
        'data': data})


@login_required
def kvm_suspend(request):
    utils_id = request.POST.get("utils_id", "")
    kvm_name = request.POST.get("kvm_name", "")
    kvm_state = request.POST.get("kvm_state", "")
    kvm_id = ""
    try:
        utils_id = int(utils_id)
    except:
        pass
    kvm_credit = kvm_credit_data(utils_id)
    utils_ip = kvm_credit['KvmHost']
    try:
        result = libvirtApi.LibvirtApi(utils_ip).kvm_suspend(kvm_state, kvm_name)
        kvm_id = libvirtApi.LibvirtApi(utils_ip).kvm_id(kvm_name)
    except Exception as e:
        print(e)
        result = '暂停失败。'
    return JsonResponse({
        'res': result,
        'kvm_id': kvm_id
    })


@login_required
def kvm_resume(request):
    utils_id = request.POST.get("utils_id", "")
    kvm_name = request.POST.get("kvm_name", "")
    kvm_state = request.POST.get("kvm_state", "")
    kvm_id = ""
    try:
        utils_id = int(utils_id)
    except:
        pass
    kvm_credit = kvm_credit_data(utils_id)
    utils_ip = kvm_credit['KvmHost']
    try:
        result = libvirtApi.LibvirtApi(utils_ip).kvm_resume(kvm_state, kvm_name)
        kvm_id = libvirtApi.LibvirtApi(utils_ip).kvm_id(kvm_name)
    except Exception as e:
        print(e)
        result = '运行失败。'
    return JsonResponse({
        'res': result,
        'kvm_id': kvm_id
    })


@login_required
def kvm_reboot(request):
    utils_id = request.POST.get("utils_id", "")
    kvm_name = request.POST.get("kvm_name", "")
    kvm_state = request.POST.get("kvm_state", "")
    kvm_id = ""
    try:
        utils_id = int(utils_id)
    except:
        pass
    kvm_credit = kvm_credit_data(utils_id)
    utils_ip = kvm_credit['KvmHost']
    try:
        result = libvirtApi.LibvirtApi(utils_ip).kvm_reboot(kvm_state, kvm_name)
        kvm_id = libvirtApi.LibvirtApi(utils_ip).kvm_id(kvm_name)
    except Exception as e:
        print(e)
        result = '重启失败。'
    return JsonResponse({
        'res': result,
        'kvm_id': kvm_id
    })


@login_required
def kvm_shutdown(request):
    # 关闭虚拟机
    utils_id = request.POST.get("utils_id", "")
    kvm_name = request.POST.get("kvm_name", "")
    kvm_state = request.POST.get("kvm_state", "")
    kvm_id = ""
    try:
        utils_id = int(utils_id)
    except:
        pass
    kvm_credit = kvm_credit_data(utils_id)
    utils_ip = kvm_credit['KvmHost']
    try:
        result = libvirtApi.LibvirtApi(utils_ip).kvm_shutdown(kvm_state, kvm_name)
        kvm_id = libvirtApi.LibvirtApi(utils_ip).kvm_id(kvm_name)
    except Exception as e:
        print(e)
        result = '关闭失败。'
    return JsonResponse({
        'res': result,
        'kvm_id': kvm_id
    })


@login_required
def kvm_delete(request):
    # 删除副本：删除虚拟机 + 删除文件系统 + 删除快照 + 删除本地数据库数据
    result = {}
    utils_id = request.POST.get("utils_id", "")
    name = request.POST.get("kvm_name", "")
    state = request.POST.get("kvm_state", "")
    try:
        utils_id = int(utils_id)
    except:
        pass
    kvm_credit = kvm_credit_data(utils_id)
    utils_ip = kvm_credit['KvmHost']
    # 拼接路径
    filesystem_snapshot = 'data/vmdata/' + name         # data/vmdata/CentOS-7@test2    快照
    filesystem = filesystem_snapshot.replace('@', ':')  # data/vmdata/CentOS-7:test2    文件系统
    try:
        # ①删除虚拟机
        result_info = libvirtApi.LibvirtApi(utils_ip).kvm_undefine(name, state)
        if result_info == '取消定义成功。':
            # ②删除文件系统
            result_info = libvirtApi.KVMApi(kvm_credit).filesystem_del(filesystem)
            if result_info == '删除文件系统成功。':
                # ③删除快照
                result_info = libvirtApi.KVMApi(kvm_credit).zfs_snapshot_del(filesystem_snapshot)
                if result_info == '删除快照成功。':
                    # ④删除数据库数据:name为虚拟机的名称是唯一的
                    kvmcopy = KvmCopy.objects.exclude(state='9').filter(name=name).filter(utils_id=utils_id)
                    if kvmcopy.exists():
                        kvm = kvmcopy[0]
                        kvm.state = '9'
                        kvm.save()
                        result["res"] = '删除成功。'
                else:
                    result["res"] = result_info
            else:
                result["res"] = result_info
        else:
            result["res"] = result_info
    except Exception as e:
        print(e)
        result["res"] = '删除失败。'
    return JsonResponse(result)


@login_required
def kvm_clone_save(request):
    # 克隆虚拟机：①判断要克隆虚拟机是否存在 ②先创建文件系统 ③再执行克隆操作
    result = {}
    utils_id = request.POST.get("utils_id", "")
    kvm_state = request.POST.get("kvm_state", "")
    kvm_name = request.POST.get("kvm_name_old", "")
    kvm_name_clone = request.POST.get("kvm_name_new", "")
    try:
        utils_id = int(utils_id)
    except:
        pass
    if not kvm_name_clone.strip():
        result['res'] = '新虚拟机名称未填写。'
    elif kvm_state == 'running' or kvm_state == '运行中':
        result['res'] = '虚拟机未关闭。'
    else:
        kvm_credit = kvm_credit_data(utils_id)
        filesystem = 'data/vmdata/' + kvm_name_clone  # 文件系统
        try:
            kvm_exist = []
            kvm_list = libvirtApi.KVMApi(kvm_credit).kvm_all_list()
            for i in kvm_list:
                kvm_exist.append(i['name'])
            if kvm_name_clone in kvm_exist:
                result['res'] = '虚拟机' + kvm_name_clone + '已存在。'
            else:
                result_info = libvirtApi.KVMApi(kvm_credit).create_filesystem(filesystem)
                if result_info == '文件系统创建成功。':
                    result_info = libvirtApi.KVMApi(kvm_credit).kvm_clone(kvm_state, kvm_name, kvm_name_clone, filesystem)
                    result["res"] = result_info
                else:
                    result["res"] = '文件系统创建失败。'
        except Exception as e:
            print(e)
            result["res"] = '克隆失败。'
    return JsonResponse(result)


@login_required
def kvm_machine_create(request):
    # 模板中新建虚拟机：创建文件系统 + 拷贝模板文件到文件系统 + 生成新的xml文件 + 定义虚拟机
    result = {}
    utils_id = request.POST.get("utils_id", "")
    kvm_template = request.POST.get("kvm_template", "")
    kvm_template_name = request.POST.get("kvm_template_name", "")
    kvm_storage = request.POST.get("kvm_storage", "")
    kvm_cpu = request.POST.get("kvm_cpu", "")
    kvm_memory = request.POST.get("kvm_memory", "")
    try:
        utils_id = int(utils_id)
    except:
        pass
    if not kvm_template.strip():
        result['res'] = '模板未选择。'
    elif not kvm_template_name.strip():
        result['res'] = '虚拟机名称未填写。'
    else:
        kvm_credit = kvm_credit_data(utils_id)
        # 拼接路径
        filesystem = 'data/vmdata/' + kvm_template_name                          # data/vmdata/Test-10
        kvm_os_image_path = '/home/images/os-image/' + kvm_template              # /home/images/os-image/CentOS-7.qcow2
        kvm_xml = kvm_template.replace('.qcow2', '.xml')                         # CentOS-7.xml
        kvm_disk_path = '/' + filesystem + '/' + kvm_template_name + '.qcow2'    # /data/vmdata/Test-10/Test-10.qcow2
        kvm_disk_image_path = '/home/images/disk-image/' + kvm_storage           # /home/images/disk-image/100G.qcow2
        kvm_storage_path = '/' + filesystem + '/' + kvm_storage                  # /data/vmdata/Test-10/100G.qcow2
        try:
            kvm_exist = []
            kvm_list = libvirtApi.KVMApi(kvm_credit).kvm_all_list()
            for i in kvm_list:
                kvm_exist.append(i['name'])
            if kvm_template_name in kvm_exist:
                result['res'] = '虚拟机' + kvm_template_name + '已存在。'
            else:
                # ①创建文件系统
                result_info = libvirtApi.KVMApi(kvm_credit).create_filesystem(filesystem)
                if result_info == '文件系统创建成功。':
                    # ②拷贝模板文件到文件系统   + 判断有无选择存储文件
                    result_info = libvirtApi.KVMApi(kvm_credit).copy_disk(kvm_os_image_path, kvm_disk_path, kvm_storage, kvm_disk_image_path, kvm_storage_path)
                    if result_info == '拷贝磁盘文件成功。':
                        # ③生成新的xml文件  + 判断有无选择存储文件
                        result_info = libvirtApi.KVMApi(kvm_credit).create_new_xml(kvm_xml, kvm_disk_path, kvm_template_name, kvm_cpu, kvm_memory, kvm_storage, kvm_storage_path)
                        if result_info == '生成成功。':
                            # ④新的xml文件生成，开始定义虚拟机
                            result_info = libvirtApi.KVMApi(kvm_credit).define_kvm(kvm_template_name)
                            if result_info == '定义成功。':
                                result['res'] = '新建成功。'
                            else:
                                result['res'] = '新建失败。'
                        else:
                            result['res'] = '生成失败。'
                    else:
                        result['res'] = '拷贝文件失败。'
                else:
                    result['res'] = '文件系统创建失败。'
        except Exception as e:
            print(e)
            result["res"] = '新建失败。'
    return JsonResponse(result)


@login_required
def kvm_power(request):
    # 给电：修改ip和主机名，开启虚拟机、新增数据库
    result = {}
    utils_id = request.POST.get("utils_id", "")
    kvm_name = request.POST.get("kvm_name", "")
    kvm_state = request.POST.get("kvm_state", "")
    kvm_ip = request.POST.get("kvm_ip", "")
    kvm_hostname = request.POST.get("kvm_hostname", "")
    kvm_password = request.POST.get("kvm_password", "")
    kvm_id = ''
    compile_ip = re.compile('^(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|[1-9])\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)$')
    user_id = request.user.id
    try:
        user_id = int(user_id)
        utils_id = int(utils_id)
    except:
        pass
    if not kvm_ip.strip():
        result['res'] = 'IP未填写。'
    elif not kvm_hostname.strip():
        result['res'] = '主机名未填写。'
    elif not compile_ip.match(kvm_ip):
        result['res'] = 'IP不合法。'
    else:
        kvm_credit = kvm_credit_data(utils_id)
        utils_ip = kvm_credit['KvmHost']
        filesystem = 'data/vmdata/' + kvm_name     # data/vmdata/Test-10
        try:
            result_info = libvirtApi.KVMApi(kvm_credit).guestmount(kvm_name, filesystem)
            if result_info == '挂载成功。':
                result_info = libvirtApi.KVMApi(kvm_credit).alert_ip_hostname(kvm_ip, kvm_hostname)
                if result_info == '修改成功。':
                    result_info = libvirtApi.KVMApi(kvm_credit).alter_password(kvm_password)
                    if result_info == '修改密码成功。':
                        result_info = libvirtApi.KVMApi(kvm_credit).umount()
                        if result_info == '取消挂载成功。':
                            result_info = libvirtApi.LibvirtApi(utils_ip).kvm_start(kvm_state, kvm_name)
                            if result_info == '开机成功。':
                                # 保存数据库
                                try:
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
                                    result = '给电成功。'
                                    kvm_id = libvirtApi.LibvirtApi(utils_ip).kvm_id(kvm_name)
                                except Exception as e:
                                    print(e)
                                    result = '给电失败。'
                            else:
                                result = '开机失败。'
                        else:
                            result = '取消挂载失败。'
                    else:
                        result = '修改密码失败。'
                else:
                    result = '修改失败。'
            else:
                result = '挂载失败。'
        except Exception as e:
            print(e)
            result = '给电失败。'
    return JsonResponse({
        'res': result,
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