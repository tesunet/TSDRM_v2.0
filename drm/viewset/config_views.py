# 流程配置：场景配置、脚本配置、流程配置、主机配置
import xlrd
import xlwt

from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404, HttpResponse, JsonResponse
from django.http import StreamingHttpResponse
from django.db.models import Max
from django.forms.models import model_to_dict

from ..tasks import *
from TSDRM import settings
from drm.api.commvault.RestApi import *
from .public_func import *
from .commv_views import *
from .basic_views import getpagefuns
from django.contrib.auth.decorators import login_required
from lxml import etree
from concurrent.futures import ThreadPoolExecutor, as_completed
import cx_Oracle
import pymysql
from ..remote import ServerByPara
from ..kvm import KVMApi


######################
# 脚本配置
######################
def get_script_node(parent, select_id):
    nodes = []
    children = parent.children.order_by("sort").exclude(state="9")
    for child in children:
        node = dict()
        node["text"] = child.name
        node["id"] = child.id
        node["type"] = child.type

        if child.type == "NODE":  # 节点
            node["data"] = {
                "remark": child.remark,
                "pname": parent.name
            }
            node["a_attr"] = {
                "class": "jstree-no-checkboxes"
            }
        if child.type == "INTERFACE":  # 接口
            # 脚本参数
            param_list = []
            try:
                config = etree.XML(child.config)

                param_el = config.xpath("//param")
                for v_param in param_el:
                    param_list.append({
                        "param_name": v_param.attrib.get("param_name", ""),
                        "variable_name": v_param.attrib.get("variable_name", ""),
                        "param_value": v_param.attrib.get("param_value", ""),
                    })
            except Exception as e:
                print(e)

            node["data"] = {
                "pname": parent.name,
                "remark": child.remark,
                "code": child.code,
                "name": child.name,
                "type": child.type,
                "interface_type": child.interface_type,
                "commv_interface": child.commv_interface,
                "script_text": child.script_text,
                "success_text": child.succeedtext,
                "variable_param_list": param_list,
            }
        node["children"] = get_script_node(child, select_id)
        try:
            if int(select_id) == child.id:
                node["state"] = {"selected": True}
        except:
            pass
        nodes.append(node)
    return nodes


@login_required
def script(request, funid):
    return render(request, 'script.html', {
        'username': request.user.userinfo.fullname, 
        "pagefuns": getpagefuns(funid, request=request),
    })


@login_required
def get_script_tree(request):
    status = 1
    info = ""
    data = []
    select_id = request.POST.get("id", )
    root_nodes = Script.objects.order_by("sort").exclude(state="9").filter(pnode=None).filter(type="NODE")

    for root_node in root_nodes:
        root = dict()
        root["text"] = root_node.name
        root["id"] = root_node.id
        root["type"] = "NODE"
        root["data"] = {
            "remark": root_node.remark,
            "pname": "无"
        }
        try:
            if int(select_id) == root_node.id:
                root["state"] = {"opened": True, "selected": True}
            else:
                root["state"] = {"opened": True}
        except:
            root["state"] = {"opened": True}
        root["children"] = get_script_node(root_node, select_id)
        data.append(root)
    return JsonResponse({
        "status": status,
        "info": info,
        "data": data
    })


@login_required
def script_save(request):
    status = 1
    info = "保存成功。"
    select_id = ""

    id = request.POST.get('id', '')
    code = request.POST.get('code', '')
    name = request.POST.get('name', '')

    # script_text
    script_text = request.POST.get('script_text', '')

    success_text = request.POST.get('success_text', '')
    log_address = request.POST.get('log_address', '')

    # commvault接口
    interface_type = request.POST.get('interface_type', '')

    # 类名
    commv_interface = request.POST.get('commv_interface', '')

    pid = request.POST.get('pid', '')
    my_type = request.POST.get('my_type', '')
    remark = request.POST.get('remark', '')
    pname = request.POST.get('pname')

    # 节点
    node_remark = request.POST.get('node_remark', '')
    node_pname = request.POST.get('node_pname', '')
    node_name = request.POST.get('node_name', '')

    insert_params = request.POST.get('insert_params', '')
    try:
        insert_params = json.loads(insert_params)
    except Exception as e:
        pass

    # 节点存储方法
    def node_save(save_data):
        status = 1
        info = "保存成功。"
        # 删除ID
        copy_save_data = copy.deepcopy(save_data)
        copy_save_data.pop("id")
        if save_data["id"] == 0:
            select_id = save_data["pnode_id"]
            # 排序
            sort = 1
            try:
                max_sort = Script.objects.exclude(state="9").filter(pnode_id=save_data["pnode_id"]).aggregate(
                    max_sort=Max('sort', distinct=True))["max_sort"]
                sort = max_sort + 1
            except:
                pass
            copy_save_data["sort"] = sort
            try:
                scriptsave = Script.objects.create(**copy_save_data)
                status = 1
                select_id = scriptsave.id
            except Exception as e:
                print(e)
                status = 0
                info = "新增接口失败。"
        else:
            # 修改
            select_id = save_data["id"]
            try:
                Script.objects.filter(id=save_data["id"]).update(**copy_save_data)
                status = 1
            except:
                status = 0
                info = "修改接口失败。"
        return status, info, select_id

    # 接口存储方法
    def interface_save(save_data):
        status = 1
        info = "保存成功。"

        if save_data["id"] == 0:
            select_id = save_data["pnode_id"]
            allscript = Script.objects.filter(code=save_data["code"]).exclude(state="9")
            if allscript.exists():
                status = 0
                info = '脚本编码:' + save_data["code"] + '已存在。'
            else:
                scriptsave = Script()
                scriptsave.code = save_data["code"]
                scriptsave.name = save_data["name"]
                scriptsave.type = save_data["type"]
                scriptsave.pnode_id = save_data["pnode_id"]
                scriptsave.remark = save_data["remark"]
                scriptsave.config = save_data["config"]

                # 判断是否commvault/脚本
                if save_data["interface_type"] == "Commvault":
                    scriptsave.script_text = ""
                    scriptsave.succeedtext = ""
                    scriptsave.commv_interface = save_data["commv_interface"]
                else:
                    scriptsave.script_text = save_data["script_text"]
                    scriptsave.succeedtext = save_data["succeedtext"]
                    scriptsave.commv_interface = ""

                scriptsave.interface_type = save_data["interface_type"]

                # 排序
                sort = 1
                try:
                    max_sort = Script.objects.exclude(state="9").filter(pnode_id=save_data["pnode_id"]).aggregate(
                        max_sort=Max('sort', distinct=True))["max_sort"]
                    sort = max_sort + 1
                except:
                    pass
                scriptsave.sort = sort

                scriptsave.save()
                select_id = scriptsave.id
                status = 1
        else:
            # 修改
            select_id = id
            allscript = Script.objects.exclude(id=save_data["id"]).filter(code=save_data["code"]).exclude(state="9")
            if allscript.exists():
                info = '脚本编码:' + save_data["code"] + '已存在。'
                status = 0
            else:
                try:
                    scriptsave = Script.objects.get(id=save_data["id"])
                    scriptsave.code = save_data["code"]
                    scriptsave.name = save_data["name"]
                    scriptsave.type = save_data["type"]
                    scriptsave.remark = save_data["remark"]
                    scriptsave.config = save_data["config"]

                    # 判断是否commvault/脚本
                    if save_data["interface_type"] == "Commvault":
                        scriptsave.hosts_manage_id = None
                        scriptsave.script_text = ""
                        scriptsave.succeedtext = ""
                        scriptsave.commv_interface = save_data["commv_interface"]
                    else:
                        scriptsave.script_text = save_data["script_text"]
                        scriptsave.succeedtext = save_data["succeedtext"]
                        scriptsave.commv_interface = ""

                    scriptsave.interface_type = save_data["interface_type"]

                    scriptsave.save()
                    status = 1
                except Exception as e:
                    print("scriptsave edit error:%s" % e)
                    status = 0
                    info = "修改失败。"

        return status, info, select_id

    try:
        id = int(id)
        pid = int(pid)
    except ValueError as e:
        status = 0
        info = "网络连接异常。"
    else:
        status = ""
        # NODE/INTERFACE
        if my_type == "NODE":
            save_data = {
                "id": id,
                "code": "",
                "name": node_name,
                "script_text": "",
                "succeedtext": "",
                "interface_type": "",
                "remark": node_remark,
                "pnode_id": pid,
                "type": my_type,
            }
            status, info, select_id = node_save(save_data)
        else:
            # 脚本参数
            root = etree.Element("root")

            if insert_params:
                # 动态参数
                for insert_param in insert_params:
                    param_node = etree.SubElement(root, "param")
                    param_node.attrib["param_name"] = insert_param["param_name"].strip()
                    param_node.attrib["variable_name"] = insert_param["variable_name"].strip()
                    param_node.attrib["param_value"] = insert_param["param_value"].strip()
            config = etree.tounicode(root)

            save_data = {
                "id": id,
                "code": code,
                "name": name,
                "script_text": script_text,
                "succeedtext": success_text,
                "interface_type": interface_type,
                "commv_interface": commv_interface,
                "remark": remark,
                "pnode_id": pid,
                "type": my_type,
                "config": config,
            }
            if code.strip() == '':
                info = '接口编码不能为空。'
                status = 0
            else:
                if name.strip() == '':
                    info = '接口名称不能为空。'
                    status = 0
                else:
                    # 区分interface_type: commvault/脚本
                    if interface_type.strip() == "":
                        info = '接口类型未选择。'
                        status = 0
                    else:
                        if interface_type == "Commvault":
                            if not commv_interface:
                                info = 'Commvault类名不能为空。'
                                status = 0
                            else:
                                status, info, select_id = interface_save(save_data)
                        else:
                            if script_text.strip() == '':
                                info = '脚本内容不能为空。'
                                status = 0
                            else:
                                status, info, select_id = interface_save(save_data)
    return JsonResponse({
        "status": status,
        "info": info,
        "data": select_id
    })


@login_required
def get_script_detail(request):
    status = 1
    info = ""
    data = {}
    selected_id = request.POST.get("id", "")

    try:
        cur_script = Script.objects.get(id=int(selected_id))
    except Exception as e:
        status = 0
        info = "获取脚本信息失败。"
    else:
        # 脚本参数
        param_list = []
        try:
            config = etree.XML(cur_script.config)

            param_el = config.xpath("//param")
            for v_param in param_el:
                param_list.append({
                    "param_name": v_param.attrib.get("param_name", ""),
                    "variable_name": v_param.attrib.get("variable_name", ""),
                    "param_value": v_param.attrib.get("param_value", ""),
                })
        except Exception as e:
            print(e)

        data = {
            "remark": cur_script.remark,
            "code": cur_script.code,
            "name": cur_script.name,
            "type": cur_script.type,
            "interface_type": cur_script.interface_type,
            "commv_interface": cur_script.commv_interface,
            "script_text": cur_script.script_text,
            "success_text": cur_script.succeedtext,
            "variable_param_list": param_list,
        }
    return JsonResponse({
        "status": status,
        "info": info,
        "data": data
    })


@login_required
def scriptdel(request):
    """
    当删除脚本管理中的脚本的同时
    :param request:
    :return:
    """
    if 'id' in request.POST:
        id = request.POST.get('id', '')
        try:
            id = int(id)
        except:
            return HttpResponse(0)
        script = Script.objects.get(id=id)
        script.state = "9"
        script.save()

        return HttpResponse(1)
    else:
        return HttpResponse(0)


@login_required
def script_move(request):
    id = request.POST.get('id', '')
    parent = request.POST.get('parent', '')
    old_parent = request.POST.get('old_parent', '')
    position = request.POST.get('position', '')
    old_position = request.POST.get('old_position', '')
    try:
        id = int(id)  # 节点 id
        parent = int(parent)  # 目标位置父节点 pnode_id
        position = int(position)  # 目标位置
        old_parent = int(old_parent)  # 起点位置父节点 pnode_id
        old_position = int(old_position)  # 起点位置
    except:
        return HttpResponse("0")
    # sort = position + 1 sort从1开始

    # 起始节点下方 所有节点  sort -= 1
    old_script_parent = Script.objects.get(id=old_parent)
    old_sort = old_position + 1
    old_scripts = Script.objects.exclude(state="9").filter(pnode=old_script_parent).filter(sort__gt=old_sort)

    # 目标节点下方(包括该节点) 所有节点 sort += 1
    script_parent = Script.objects.get(id=parent)
    sort = position + 1
    scripts = Script.objects.exclude(state=9).exclude(id=id).filter(pnode=script_parent).filter(sort__gte=sort)

    my_script = Script.objects.get(id=id)

    # 判断目标父节点是否为接口，若为接口无法挪动
    if script_parent.type == "INTERFACE":
        return HttpResponse("接口")
    else:
        # 目标父节点下所有节点 除了自身 接口名称都不得相同 否则重名
        script_same = Script.objects.exclude(state="9").exclude(id=id).filter(pnode=script_parent).filter(
            name=my_script.name)

        if script_same:
            return HttpResponse("重名")
        else:
            for old_script in old_scripts:
                try:
                    old_script.sort -= 1
                    old_script.save()
                except:
                    pass
            for script in scripts:
                try:
                    script.sort += 1
                    script.save()
                except:
                    pass

            # 该节点位置变动
            try:
                my_script.pnode = script_parent
                my_script.sort = sort
                my_script.save()
            except:
                pass

            # 起始 结束 点不在同一节点下 写入父节点名称与ID ?
            if parent != old_parent:
                return HttpResponse(script_parent.name + "^" + str(script_parent.id))
            else:
                return HttpResponse("0")


######################
# 场景配置
######################
@login_required
def process_design(request, funid):
    all_main_database = []
    all_hosts = DbCopyClient.objects.exclude(state="9").filter(hosttype="1")
    for host in all_hosts:
        all_main_database.append({
            "main_database_id": host.hostsmanage.id,
            "main_database_name": host.hostsmanage.host_name
        })

    # 选择关联客户端
    hosts = HostsManage.objects.exclude(state="9").filter(nodetype="CLIENT").values("id", "host_name")

    # 回切流程
    p_backs = Process.objects.exclude(state="9").filter(processtype=2).values("id", "name", "type", "pnode_id")

    return render(request, "processdesign.html", {
        'username': request.user.userinfo.fullname, 
        "pagefuns": getpagefuns(funid, request=request),
        'all_main_database': all_main_database, 
        'p_backs':p_backs,
        "hosts": [{
            "id": str(x["id"]),
            "host_name": x["host_name"]
        } for x in hosts],
    })


@login_required
def get_process_tree(request):
    status = 1
    info = ""
    data = []
    select_id = request.POST.get("id", "")

    try:
        root_nodes = Process.objects.order_by("sort").exclude(state="9").filter(pnode=None)
        for root_node in root_nodes:
            root = dict()
            root["text"] = root_node.name
            root["id"] = root_node.id
            root["data"] = {
                "pname": "无"
            }
            root["type"] = "NODE"
            try:
                if int(select_id) == root_node.id:
                    root["state"] = {"opened": True, "selected": True}
                else:
                    root["state"] = {"opened": True}
            except Exception as e:
                root["state"] = {"opened": True}
            root["children"] = get_process_node(root_node, select_id)
            data.append(root)
    except Exception as e:
        status = 0
        info = "获取流程树失败。"
    return JsonResponse({
        "status": status,
        "data": data,
        "info": info
    })


@login_required
def get_process_detail(request):
    status = 1
    info = ""
    data = {}

    process_id = request.POST.get("id", "")

    try:
        process_id = int(process_id)
        process = Process.objects.get(id=process_id)
    except Exception as e:
        status = 0
        info = "获取流程信息失败。"
    else:
        param_list = []
        try:
            config = etree.XML(process.config)

            param_el = config.xpath("//param")
            for v_param in param_el:
                param_list.append({
                    "param_name": v_param.attrib.get("param_name", ""),
                    "variable_name": v_param.attrib.get("variable_name", ""),
                    "param_value": v_param.attrib.get("param_value", ""),
                })
        except Exception as e:
            print(e)

        data = {
            "process_id": process.id,
            "process_code": process.code,
            "process_name": process.name,
            "process_remark": process.remark,
            "process_sign": process.sign,
            "process_rto": process.rto,
            "process_rpo": process.rpo,
            "process_sort": process.sort,
            "process_color": process.color,
            "type": process.type,
            "processtype": process.processtype,
            "variable_param_list": param_list,
            "cv_client": process.hosts_id,
            "main_database": process.primary_id,
            "p_back": process.backprocess_id
        }

    return JsonResponse({
        "status": status,
        "data": data,
        "info": info
    })


@login_required
def process_move(request):
    id = request.POST.get('id', '')
    parent = request.POST.get('parent', '')
    old_parent = request.POST.get('old_parent', '')
    position = request.POST.get('position', '')
    old_position = request.POST.get('old_position', '')
    try:
        id = int(id)  # 节点 id
        parent = int(parent)  # 目标位置父节点 pnode_id
        position = int(position)  # 目标位置
        old_parent = int(old_parent)  # 起点位置父节点 pnode_id
        old_position = int(old_position)  # 起点位置
    except:
        return HttpResponse("0")
    # sort = position + 1 sort从1开始

    # 起始节点下方 所有节点  sort -= 1
    old_process_parent = Process.objects.get(id=old_parent)
    old_sort = old_position + 1
    old_processs = Process.objects.exclude(state="9").filter(pnode=old_process_parent).filter(sort__gt=old_sort)

    # 目标节点下方(包括该节点) 所有节点 sort += 1
    process_parent = Process.objects.get(id=parent)
    sort = position + 1
    processs = Process.objects.exclude(state=9).exclude(id=id).filter(pnode=process_parent).filter(sort__gte=sort)

    my_process = Process.objects.get(id=id)

    # 判断目标父节点是否为接口，若为接口无法挪动
    if process_parent.type != "NODE" and my_process.processtype=="1":
        return HttpResponse("主场景")
    elif process_parent.type == "NODE" and my_process.type != "NODE" and my_process.processtype!="1" :
        return HttpResponse("子场景")
    else:
        # 目标父节点下所有节点 除了自身 接口名称都不得相同 否则重名
        process_same = Process.objects.exclude(state="9").exclude(id=id).filter(pnode=process_parent).filter(
            name=my_process.name)

        if process_same:
            return HttpResponse("重名")
        else:
            for old_process in old_processs:
                try:
                    old_process.sort -= 1
                    old_process.save()
                except:
                    pass
            for process in processs:
                try:
                    process.sort += 1
                    process.save()
                except:
                    pass

            # 该节点位置变动
            try:
                my_process.pnode = process_parent
                my_process.sort = sort
                my_process.save()
            except:
                pass

            # 起始 结束 点不在同一节点下 写入父节点名称与ID ?
            if parent != old_parent:
                return HttpResponse(process_parent.name + "^" + str(process_parent.id))
            else:
                return HttpResponse("0")


def get_process_node(parent, select_id):
    nodes = []
    children = parent.children.order_by("sort").exclude(state="9").exclude(Q(type=None) | Q(type=""))
    for child in children:
        node = dict()
        node["text"] = child.name
        node["id"] = child.id
        node["children"] = get_process_node(child, select_id)
        childtype=child.type
        if childtype != "NODE":
            childtype="PROCESS"
        node["type"] = childtype
        node["data"] = {
            "pname": parent.name,
            "name": child.name,
            "processtype": child.processtype,
            "remark": child.remark,
        }

        try:
            if int(select_id) == child.id:
                node["state"] = {"selected": True}
        except:
            pass
        nodes.append(node)
    return nodes


@login_required
def process_save(request):
    status = 1
    info = "保存成功。"
    select_id = ""

    id = request.POST.get('id', '')
    pid = request.POST.get('pid', '')
    name = request.POST.get('name', '')
    remark = request.POST.get('remark', '')
    sign = request.POST.get('sign', '')
    rto = request.POST.get('rto', '')
    rpo = request.POST.get('rpo', '')
    sort = request.POST.get('sort', '')
    color = request.POST.get('color', '')
    cv_client = request.POST.get('cv_client', '')
    type = request.POST.get('type', '')
    nodetype = request.POST.get('my_type', '')
    processtype = request.POST.get('processtype', '')
    config = request.POST.get('config', [])
    node_name = request.POST.get('node_name', '')
    node_remark = request.POST.get('node_name', '')

    main_database = request.POST.get('process_main_database', '')
    process_back = request.POST.get('process_back', '')
    try:
        id = int(id)
        pid = int(pid)
        process_back = int(process_back)
        cv_client = int(cv_client)
    except Exception as e:
        pass

    if nodetype == "NODE":
        if node_name.strip() == '':
            status = 0
            info = '节点名称不能为空。'
        else:
            if id == 0:
                try:
                    sort = 1
                    try:
                        max_sort = Process.objects.exclude(state="9").filter(pnode_id=pid).aggregate(
                            max_sort=Max('sort', distinct=True))["max_sort"]
                        sort = max_sort + 1
                    except:
                        pass
                    processsave = Process()
                    processsave.name = node_name
                    processsave.sort = sort if sort else None
                    processsave.remark = node_remark
                    processsave.type = "NODE"
                    processsave.pnode_id = pid

                    processsave.save()
                    name=node_name
                    select_id = processsave.id
                except Exception as e:
                    info = "保存失败：{0}".format(e)
                    status = 0
            else:
                # 修改
                try:
                    processsave = Process.objects.get(id=id)
                    processsave.name = node_name
                    processsave.remark = node_remark
                    processsave.save()
                    select_id = processsave.id
                except Exception as e:
                    info = "保存失败：{0}".format(e)
                    status = 0
    else:
        if name.strip() == '':
            info = '场景名称不能为空。'
            status = 0
        elif type.strip() == '':
            info = '场景类型不能为空。'
            status = 0
        elif sign.strip() == '':
            info = '是否签到不能为空。'
            status = 0
        else:
            try:
                if type=="Oracle ADG" or type=="Oracle ADG":
                    main_database = int(main_database)
            except ValueError as e:
                info = '主数据库不能为空。'
                status = 0
            else:
                # 流程参数
                root = etree.Element("root")

                if config:
                    config = json.loads(config)
                    # 动态参数
                    for c_config in config:
                        param_node = etree.SubElement(root, "param")
                        param_node.attrib["param_name"] = c_config["param_name"].strip()
                        param_node.attrib["variable_name"] = c_config["variable_name"].strip()
                        param_node.attrib["param_value"] = c_config["param_value"].strip()
                xml_config = etree.tounicode(root)

                if id == 0:
                    all_process = Process.objects.filter(name=name).exclude(state="9").exclude(Q(type=None) | Q(type=""))
                    if (len(all_process) > 0):
                        info = '场景:' + name + '已存在。'
                        status = 0
                    else:
                        try:
                            processsave = Process()
                            processsave.url = '/cv_oracler'
                            processsave.name = name
                            processsave.remark = remark
                            processsave.sign = sign
                            processsave.rto = rto if rto else None
                            processsave.rpo = rpo if rpo else None
                            processsave.sort = sort if sort else None
                            processsave.color = color
                            processsave.type = type
                            processsave.processtype = processtype
                            processsave.primary_id = main_database
                            processsave.backprocess_id = process_back
                            processsave.hosts_id = cv_client if cv_client else None
                            processsave.config = xml_config
                            processsave.pnode_id = pid

                            # 排序
                            sort = 1
                            try:
                                max_sort = Process.objects.exclude(state="9").filter(pnode_id=pid).aggregate(
                                    max_sort=Max('sort', distinct=True))["max_sort"]
                                sort = max_sort + 1
                            except:
                                pass
                            processsave.sort = sort

                            processsave.save()
                            select_id = processsave.id
                        except Exception as e:
                            info = "保存失败：{0}".format(e)
                            status = 0
                else:
                    all_process = Process.objects.filter(name=name).exclude(id=id).exclude(state="9")
                    if (len(all_process) > 0):
                        info = '场景:' + name + '已存在。'
                        status = 0
                    else:
                        try:
                            processsave = Process.objects.get(id=id)
                            processsave.name = name
                            processsave.remark = remark
                            processsave.sign = sign
                            processsave.rto = rto if rto else None
                            processsave.rpo = rpo if rpo else None
                            processsave.sort = sort if sort else None
                            processsave.color = color
                            processsave.type = type
                            processsave.processtype = processtype
                            processsave.primary_id = main_database
                            processsave.backprocess_id = process_back
                            processsave.hosts_id = cv_client if cv_client else None
                            processsave.config = xml_config
                            processsave.save()
                            select_id = processsave.id
                        except Exception as e:
                            info = "保存失败：{0}".format(e)
                            status = 0

    return JsonResponse({
        "status": status,
        "info": info,
        "data": select_id
    })


@login_required
def process_del(request):
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
@login_required
def processconfig(request, funid):
    process_id = request.GET.get("process_id", "")
    if process_id:
        process_id = int(process_id)

    processes = Process.objects.exclude(state="9").order_by("sort").filter(processtype="1",).exclude(type="NODE")
    processlist = []
    for process in processes:
        processlist.append({"id": process.id, "code": process.code, "name": process.name})

    # 主机选项
    all_hosts_manage = HostsManage.objects.exclude(state="9")

    # commvault源端客户端
    # 工具
    cv_client_data = []
    utils = UtilsManage.objects.exclude(state="9").filter(util_type="Commvault")
    for u in utils:
        cv_client_list = u.cvclient_set.exclude(state="9").exclude(type=2).values("id", "client_name", "hostsmanage__host_name")
        cv_client_data.append({
            "utils_id": u.id,
            "utils_name": u.name,
            "cv_client_list": [{
                "id": str(x["id"]),
                "client_name": x["client_name"],
                "host_name": x["hostsmanage__host_name"]
            } for x in cv_client_list],
        })
    # tree_data
    select_id = ""
    tree_data = []
    root_nodes = Script.objects.order_by("sort").exclude(state="9").filter(pnode=None).filter(type="NODE")

    for root_node in root_nodes:
        root = dict()
        root["text"] = root_node.name
        root["id"] = root_node.id
        root["type"] = "NODE"
        root["data"] = {
            "remark": root_node.remark,
            "pname": "无"
        }
        root["a_attr"] = {
            "class": "jstree-no-checkboxes"
        }
        try:
            if int(select_id) == root_node.id:
                root["state"] = {"opened": True, "selected": True}
            else:
                root["state"] = {"opened": True}
        except:
            root["state"] = {"opened": True}
        root["children"] = get_script_node(root_node, select_id)
        tree_data.append(root)
    tree_data = json.dumps(tree_data, ensure_ascii=False)

    return render(request, 'processconfig.html',
                  {'username': request.user.userinfo.fullname, "pagefuns": getpagefuns(funid, request=request),
                   "processlist": processlist, "process_id": process_id, "all_hosts_manage": all_hosts_manage,
                   "tree_data": tree_data, "cv_client_data": cv_client_data})


@login_required
def processscriptsave(request):
    result = {}
    result["status"] = 1
    result["info"] = "保存脚本成功。"
    step_id = request.POST.get('step_id', '')
    script_id = request.POST.get('script_id', '')
    script_instance_id = request.POST.get('script_instance_id', '')
    config = request.POST.get('config', '')
    interface_type = request.POST.get('interface_type', '')  # 接口类型：Commvault Linux Windows
    error_solved = request.POST.get('error_solved', '')

    # add
    script_instance_name = request.POST.get('script_instance_name', '')  # 必填
    utils = request.POST.get('utils', '')  # Commvault 必填
    host_id = request.POST.get('host_id', '')  # Linux Window 必填
    origin_id = request.POST.get('origin', '')  # Commvault必填
    log_address = request.POST.get('log_address', '')
    sort = request.POST.get('sort', '')
    script_instance_remark = request.POST.get('script_instance_remark', '')

    try:
        step_id = int(step_id)
    except:
        step_id = None
    try:
        script_id = int(script_id)
    except:
        script_id = None
    try:
        host_id = int(host_id)
    except:
        host_id = None
    try:
        origin_id = int(origin_id)
    except:
        origin_id = None
    try:
        utils = int(utils)
    except:
        utils = None
    try:
        script_instance_id = int(script_instance_id)
    except:
        script_instance_id = None
    try:
        sort = int(sort)
    except:
        sort = None
    try:
        error_solved = int(error_solved)
    except:
        error_solved = None

    # 初始化
    if not script_instance_name:
        result["status"] = 0
        result["info"] = "接口实例名称未填写。"
    else:
        if interface_type == "Commvault":
            if not utils:
                return JsonResponse({
                    "status": 0,
                    "info": "未选择工具。"
                })
            if not origin_id:
                return JsonResponse({
                    "status": 0,
                    "info": "未选择源客户端"
                })
            create_data = {
                "params": config,
                "step_id": step_id,
                "script_id": script_id,
                "name": script_instance_name,
                "utils_id": utils,
                "primary_id": origin_id,
                "log_address": log_address,
                "sort": sort,
                "process_id": error_solved,
                "remark": script_instance_remark,
                "hosts_manage_id": None,
            }
        else:
            if not host_id:
                return JsonResponse({
                    "status": 0,
                    "info": "未选择主机"
                })
            create_data = {
                "params": config,
                "step_id": step_id,
                "script_id": script_id,
                "hosts_manage_id": host_id,
                "name": script_instance_name,
                "log_address": log_address,
                "sort": sort,
                "process_id": error_solved,
                "remark": script_instance_remark,

                "utils_id": None,
                "primary_id": None,
            }

        try:
            step = Step.objects.get(id=int(step_id))
            script_id = int(script_id)
        except Exception as e:
            result["status"] = 0
            result["info"] = "保存脚本失败: {0}。".format(e)
        else:
            # 步骤在已有该脚本实例不可保存
            if script_instance_id:
                try:
                    ScriptInstance.objects.filter(id=script_instance_id).update(**create_data)
                    # 步骤下所有脚本
                    result["data"] = str(step.scriptinstance_set.exclude(state="9").values("id", "name"))
                    result["id"] = script_instance_id
                except Exception as e:
                    result["status"] = 0
                    result["info"] = "修改脚本失败: {0}。".format(e)
            else:
                try:
                    script_instance_id = ScriptInstance.objects.create(**create_data).id
                    # 步骤下所有脚本
                    result["data"] = str(step.scriptinstance_set.exclude(state="9").values("id", "name"))
                    result["id"] = script_instance_id
                except Exception as e:
                    result["status"] = 0
                    result["info"] = "新增脚本失败: {0}。".format(e)

    return JsonResponse(result)


@login_required
def get_script_data(request):
    """
    返回；
        接口信息
            接口编号
            接口名称
            接口类型
            脚本内容
            SUCCESSTEXT
            接口说明
        接口实例信息
            接口实例名称
            选择主机
            选择工具
            选择客户端
            填写类名
            日志地址
            接口实例说明
            参数值
    """
    status = 1
    info = '获取脚本信息成功。'
    data = []

    id = request.POST.get('id', '')
    try:
        id = int(id)
    except:
        status = 0
        info = '步骤未创建，请先保存步骤后添加脚本。'
    script_instance_id = request.POST.get("script_instance_id", "")
    try:
        script_instance = ScriptInstance.objects.get(id=int(script_instance_id))
    except:
        pass
    else:
        script = script_instance.script
        data = {
            "script_id": script.id,
            "script_code": script.code,
            "script_name": script.name,
            "interface_type": script.interface_type,
            "commv_interface": script.commv_interface,
            "script_text": script.script_text,
            "succeedtext": script.succeedtext,
            "remark": script.remark,
            "type": script.type,
            "script_instance_id": script_instance.id,
            "script_instance_name": script_instance.name,
            "script_instance_remark": script_instance.remark,
            "script_instance_sort": script_instance.sort,
            "script_instance_error_solved": script_instance.process_id,
            "params": "",
            "log_address": script_instance.log_address,
            "host_id": script_instance.hosts_manage_id,
            "primary_id": script_instance.primary_id,
            "utils_id": script_instance.utils_id
        }

    return JsonResponse({
        'status': status,
        'info': info,
        'data': data,
    })


@login_required
def get_error_solved_process(request):
    """
    @params process_id
    """
    p_id = request.POST.get("process_id", "")

    status = 1
    info = "获取排错流程成功。"
    data = []
    try:
        p_id = int(p_id)
    except Exception as e:
        info = "获取排错流程失败。"
        status = 0
    else:
        data = Process.objects.exclude(state="9").filter(pnode_id=p_id,processtype="3").values("id", "name")

    return JsonResponse({
        "status": status,
        "info": info,
        "data": str(data)
    })


@login_required
def remove_script(request):
    status = 1
    info = "移除成功。"
    # 取消步骤中脚本的关联
    script_instance_id = request.POST.get("script_instance_id", "")
    try:
        script_instance = ScriptInstance.objects.filter(id=int(script_instance_id)).update(state="9")
    except Exception as e:
        print(e)
        status = 0
        info = "移除失败：{0}".format(e)
    return JsonResponse({
        "status": status,
        "info": info
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


@login_required
def custom_step_tree(request):
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
                maxstep = Step.objects.filter(pnode=p_step).latest('sort').exclude(state="9")
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
    rootnodes = Step.objects.order_by("sort").filter(process_id=process_id, pnode=None).exclude(state="9")

    all_groups = Group.objects.exclude(state="9")
    group_string = "" + "+" + " -------------- " + "&"
    for group in all_groups:
        id_name_plus = str(group.id) + "+" + str(group.name) + "&"
        group_string += id_name_plus
    if len(rootnodes) > 0:
        for rootnode in rootnodes:
            root = {}
            root["text"] = rootnode.name
            root["id"] = rootnode.id
            root["children"] = get_step_tree(rootnode, selectid)
            root["state"] = {"opened": True}
            treedata.append(root)
    process = {}
    process["text"] = process_name
    process["data"] = {"allgroups": group_string}
    process["children"] = treedata
    process["state"] = {"opened": True}
    return JsonResponse({"treedata": process})


@login_required
def get_step_detail(request):
    status = 1
    info = ""
    data = {}

    step_id = request.POST.get("id", "")

    try:
        cur_step = Step.objects.get(id=int(step_id))
    except Exception as e:
        status = 0
        info = "获取步骤信息失败。"
    else:
        scripts = cur_step.scriptinstance_set.exclude(state="9").order_by("sort")
        script_string = ""
        for script in scripts:
            id_code_plus = str(script.id) + "+" + str(script.name) + "&"
            script_string += id_code_plus

        verify_items_string = ""
        verify_items = cur_step.verifyitems_set.exclude(state="9")
        for verify_item in verify_items:
            id_name_plus = str(verify_item.id) + "+" + str(verify_item.name) + "&"
            verify_items_string += id_name_plus

        group_name = ""
        if cur_step.group and cur_step.group != " ":
            group_id = cur_step.group
            try:
                group_id = int(group_id)
                group_name = Group.objects.filter(id=group_id)[0].name
            except:
               pass

        all_groups = Group.objects.exclude(state="9")
        group_string = " " + "+" + " -------------- " + "&"
        for group in all_groups:
            id_name_plus = str(group.id) + "+" + str(group.name) + "&"
            group_string += id_name_plus

        data = {
            "time": cur_step.time, 
            "approval": cur_step.approval, 
            "skip": cur_step.skip, 
            "group_name": group_name,
            "group": cur_step.group, 
            "scripts": script_string, 
            "allgroups": group_string,
            "rto_count_in": cur_step.rto_count_in, 
            "remark": cur_step.remark,
            "verifyitems": verify_items_string, 
            "force_exec": cur_step.force_exec if cur_step.force_exec else 2
        }
    return JsonResponse({
        "status": status,
        "data": data,
        "info": info
    })


@login_required
def solve_error(request):
    status = 1
    info = "启动排错流程成功。"
    data = ""
    sr_id = request.POST.get("script_run_id", "")
    try:
        sr_id = int(sr_id)
        sr = ScriptRun.objects.get(id=sr_id)
    except Exception as e:
        status = 0
        info = "启动排错流程失败：{e}。".format(e)
    else:
        si = sr.script
        error_solved = si.process if si else None
        if error_solved:
            # 启动排错流程
            # 返回排错流程ID
            # 前端定时获取该进程状态
            running_process = ProcessRun.objects.filter(process=error_solved, state__in=["RUN"])
            if running_process.exists():
                myprocesstask = ProcessTask()
                myprocesstask.starttime = datetime.datetime.now()
                myprocesstask.type = "INFO"
                myprocesstask.logtype = "END"
                myprocesstask.state = "0"
                myprocesstask.processrun = running_process[0]
                myprocesstask.content = "排错流程({0})已运行。".format(running_process[0].process.name)
                myprocesstask.save()
            else:
                myprocessrun = ProcessRun()
                myprocessrun.creatuser = request.user.username
                myprocessrun.process = error_solved
                myprocessrun.starttime = datetime.datetime.now()
                myprocessrun.state = "RUN"
                process_type = error_solved.type
                if process_type.upper() == "COMMVAULT":
                    cv_restore_params_save(myprocessrun)

                myprocessrun.save()
                mystep = error_solved.step_set.exclude(state="9")
                if not mystep.exists():
                    myprocesstask = ProcessTask()
                    myprocesstask.starttime = datetime.datetime.now()
                    myprocesstask.type = "INFO"
                    myprocesstask.logtype = "END"
                    myprocesstask.state = "0"
                    myprocesstask.processrun = myprocessrun
                    myprocesstask.content = "排错流程({0})不存在可运行步骤。".format(error_solved.name)
                    myprocesstask.save()
                else:
                    for step in mystep:
                        mysteprun = StepRun()
                        mysteprun.step = step
                        mysteprun.processrun = myprocessrun
                        mysteprun.state = "EDIT"
                        mysteprun.save()

                        myscript = step.scriptinstance_set.exclude(state="9")
                        for script in myscript:
                            myscriptrun = ScriptRun()
                            myscriptrun.script = script
                            myscriptrun.steprun = mysteprun
                            myscriptrun.state = "EDIT"
                            myscriptrun.save()

                    myprocesstask = ProcessTask()
                    myprocesstask.processrun = myprocessrun
                    myprocesstask.starttime = datetime.datetime.now()
                    myprocesstask.type = "INFO"
                    myprocesstask.logtype = "START"
                    myprocesstask.state = "1"
                    myprocesstask.content = "排错流程({0})已启动。".format(error_solved.name)
                    myprocesstask.save()

                    exec_process.delay(myprocessrun.id)
                    data = myprocessrun.id
        else:
            status = 0
            info = "启动排错流程失败：无排错流程。"

    return JsonResponse({
        "status": status,
        "info": info,
        "data": data,
    })


@login_required
def get_error_sovled_status(request):
    """
    @param pr_id:
    @return status: 1 成功 0 未完成 2出错
    """
    pr_id = request.POST.get("pr_id", "")
    status = 0
    try:
        pr_id = int(pr_id)
        c_pr = ProcessRun.objects.get(id=pr_id)
        state = c_pr.state
        if state == "DONE":
            status = 1
        elif state == "ERROR":
            # 排错流程错误的处理(待补充)
            status = 2
        else:
            status = 0
    except Exception as e:
        pass

    return JsonResponse({
        "status": status
    })


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


@login_required
def display_params(request):
    """
    参数： script_id, process_id
    响应：
        根据 脚本内容中 参数符号 从 主机参数、流程参数、脚本参数 匹配出 参数名称、变量、值、类别
    """
    status = 1
    data = []
    info = ""
    script_id = request.POST.get("script_id", "")
    script_instance_id = request.POST.get("script_instance_id", "")
    if_instance = request.POST.get("if_instance", "")
    process_id = request.POST.get("process_id", "")

    try:
        script = Script.objects.get(id=int(script_id))
    except:
        pass
    else:
        script_text = script.script_text

        if if_instance == "1":
            try:
                script_instance = ScriptInstance.objects.get(id=int(script_instance_id))
                cur_params = eval(script_instance.params)
            except Exception as e:
                print(e)
            else:
                data = [{
                    "param_name": x["param_name"],
                    "variable_name": x["variable_name"],
                    "param_value": x["param_value"],
                    "type": x["type"]
                } for x in cur_params]

        else:
            # 流程参数
            try:
                process = Process.objects.get(id=int(process_id))
            except:
                pass
            else:
                process_param_list = get_params(process.config)
                process_variable_list = get_variable_name(script_text, "PROCESS")
                for pv in process_variable_list:
                    for pp in process_param_list:
                        if pv.strip() == pp["variable_name"]:
                            data.append({
                                "param_name": pp["param_name"],
                                "variable_name": pp["variable_name"],
                                "param_value": pp["param_value"],
                                "type": "PROCESS"
                            })
                            break

            script_param_list = get_params(script.config)
            script_variable_list = get_variable_name(script_text, "SCRIPT")
            for sv in script_variable_list:
                for sp in script_param_list:
                    if sv.strip() == sp["variable_name"]:
                        data.append({
                            "param_name": sp["param_name"],
                            "variable_name": sp["variable_name"],
                            "param_value": sp["param_value"],
                            "type": "SCRIPT"
                        })
                        break

    return JsonResponse({
        "status": status,
        "data": data,
        "info": info
    })


@login_required
def load_hosts_params(request):
    """
    流程配置
        切换主机，载入主机参数
    """
    host_id = request.POST.get("host_id", "")
    script_id = request.POST.get("script_id", "")
    data = []
    status = 1
    info = ""
    try:
        host = HostsManage.objects.get(id=int(host_id))
    except:
        stauts = 0
        info = "载入主机参数失败：主机不存在。"
    else:
        try:
            script = Script.objects.get(id=int(script_id))
        except:
            status = 0
            info = "载入主机参数失败：当前脚本不存在。"
        else:
            script_text = script.script_text

            # 主机参数
            host_param_list = get_params(host.config) if host else []
            host_variable_list = get_variable_name(script_text, "HOST")
            for hv in host_variable_list:
                for hp in host_param_list:
                    if hv.strip() == hp["variable_name"]:
                        data.append({
                            "param_name": hp["param_name"],
                            "variable_name": hp["variable_name"],
                            "param_value": hp["param_value"],
                            "type": "HOST"
                        })
                        break
    return JsonResponse({
        "status": status,
        "data": data,
        "info": info
    })


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
        utils_kvm_info = UtilsManage.objects.filter(id=utils_id)
        content = utils_kvm_info[0].content
        util_type = utils_kvm_info[0].util_type
        kvm_credit = get_credit_info(content, util_type.upper())
        try:
            kvm_list = KVMApi(kvm_credit).kvm_all_list()
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
    ret = 1
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

            else:
                # 修改
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
def zfs_snapshot_data(request):
    result = {}
    zfs_snapshot_list = []
    kvm_machine = request.GET.get("kvm_machine", "")
    utils_id = request.GET.get("utils_id", "")

    filesystem = 'tank/' + kvm_machine
    try:
        utils_id = int(utils_id)
    except:
        pass

    utils_kvm_info = UtilsManage.objects.filter(id=utils_id)
    content = utils_kvm_info[0].content
    util_type = utils_kvm_info[0].util_type
    kvm_credit = get_credit_info(content, util_type.upper())

    try:
        zfs_snapshot_list = KVMApi(kvm_credit).zfs_snapshot_list(filesystem)
    except Exception as e:
        print(e)
        result["res"] = '查询失败。'
    return JsonResponse({'data': zfs_snapshot_list})


@login_required
def zfs_snapshot_save(request):
    result = {}
    utils_id = request.POST.get("util_kvm_id", "")
    kvm_name = request.POST.get("kvm_name", "")
    name = request.POST.get("snapshot_name", "")
    try:
        utils_id = int(utils_id)
    except:
        pass

    utils_kvm_info = UtilsManage.objects.filter(id=utils_id)
    content = utils_kvm_info[0].content
    util_type = utils_kvm_info[0].util_type
    kvm_credit = get_credit_info(content, util_type.upper())

    filesystem = 'tank/' + kvm_name
    snapshot_name = filesystem + '@' + name
    try:
        if name.strip() == '':
            result["res"] = '快照名称不能为空。'
        else:
            # 远程先查出所有快照，快照不存在创建快照
            zfs_snapshot_list = KVMApi(kvm_credit).zfs_snapshot_list(filesystem)
            exist_snapshot = []
            for i in zfs_snapshot_list:
                exist_snapshot.append(i['name'])
            if name in exist_snapshot:
                result["res"] = '快照' + name + '已存在。'
            else:
                result_info = KVMApi(kvm_credit).zfs_create_snapshot(snapshot_name)
                result["res"] = result_info
    except Exception as e:
        print(e)
        result["res"] = '创建失败。'

    return JsonResponse(result)


@login_required
def zfs_snapshot_del(request):
    result = {}
    utils_id = request.POST.get("utils_id", "")
    snapshot_name = request.POST.get("snapshot_name", "")
    kvm_name = request.POST.get("kvm_name", "")
    try:
        utils_id = int(utils_id)
    except:
        pass

    utils_kvm_info = UtilsManage.objects.filter(id=utils_id)
    content = utils_kvm_info[0].content
    util_type = utils_kvm_info[0].util_type
    kvm_credit = get_credit_info(content, util_type.upper())

    # 删除快照：快照已创建实例，无法删除
    filesystem = 'tank/' + kvm_name
    snapshotname = filesystem + '@' + snapshot_name
    filesystem_exist = []
    try:
        filesystem_list = KVMApi(kvm_credit).zfs_kvm_filesystem()
        for i in filesystem_list:
            i = 'tank/' + i
            filesystem_exist.append(i)
        snapname = snapshotname.replace('@', '-')
        if snapname in filesystem_exist:
            result['res'] = '快照已创建实例，无法删除。'
        else:
            result_info = KVMApi(kvm_credit).zfs_snapshot_del(snapshotname)
            result["res"] = result_info
    except Exception as e:
        print(e)
        result["res"] = '删除失败。'

    return JsonResponse(result)


@login_required
def zfs_snapshot_mount(request):
    result = {}
    # ①创建快照完成：tank/Test-1@2020-08-23
    # ②克隆快照：zfs clone tank/Test-1/disk@2020-08-23 tank/Test-1/Test-1_clone
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

    utils_kvm_info = UtilsManage.objects.filter(id=utils_id)
    content = utils_kvm_info[0].content
    util_type = utils_kvm_info[0].util_type
    kvm_credit = get_credit_info(content, util_type.upper())

    # 挂载快照：先判断快照是否已经挂载，根据副本名称，查出所有虚拟机，判断副本是否存在
    filesystem = 'tank/' + kvm_machine
    snapshotname = filesystem + '@' + snapshot_name
    filesystemname = filesystem + '-' + copy_name
    copyname = kvm_machine + '@' + copy_name

    if not copy_name:
        result['res'] = '名称未填写。'
    else:
        try:
            kvm_exist = []
            kvm_list = KVMApi(kvm_credit).kvm_all_list()
            for i in kvm_list:
                kvm_exist.append(i['name'])
            if copyname in kvm_exist:
                result['res'] = '实例' + copy_name + '已存在。'
            else:
                result_info = KVMApi(kvm_credit).zfs_clone_snapshot(snapshotname, filesystemname)
                if result_info == '克隆成功。':
                    # ③克隆成功，生成新的xml文件
                    result_info = KVMApi(kvm_credit).create_kvm_xml(kvm_machine, snapshotname, copyname, copy_cpu, copy_memory)
                    if result_info == '生成成功。':
                        # ④新的xml文件生成，开始定义虚拟机
                        result_info = KVMApi(kvm_credit).define_kvm(copyname)
                        if result_info == '定义成功。':
                            # ⑤定义成功，开启虚拟机
                            result_info = KVMApi(kvm_credit).kvm_start(copyname)
                            if result_info == '开机成功。':
                                # 副本开启成功，保存数据库
                                try:
                                    kvm_copy = KvmCopy.objects.filter(name=copyname).exclude(state='9')
                                    if kvm_copy.exists():
                                        result['res'] = '实例已存在。'
                                    else:
                                        kvm_copy.create(**{
                                            'name': copyname,
                                            'create_time': datetime.datetime.now(),
                                            'create_user_id': user_id,
                                            'utils_id': utils_id,
                                            'kvmmachine_id': kvm_machine_id
                                        })
                                        result['res'] = '创建成功。'
                                except Exception as e:
                                    print(e)
                                    result['res'] = '保存失败。'
                            else:
                                result['res'] = '开机失败。'
                        else:
                            result['res'] = '定义失败。'
                    else:
                        result['res'] = '生成失败。'
                else:
                    result['res'] = '克隆失败。'

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

    utils_kvm_info = UtilsManage.objects.filter(id=utils_id)
    content = utils_kvm_info[0].content
    util_type = utils_kvm_info[0].util_type
    kvm_credit = get_credit_info(content, util_type.upper())

    result = []
    all_kvmcopy = KvmCopy.objects.filter(kvmmachine_id=kvmmachine_id).exclude(state='9')
    if len(all_kvmcopy) > 0:
        for kvmcopy in all_kvmcopy:

            copy_state = ''
            try:
                copy_state = KVMApi(kvm_credit).domstate(kvmcopy.name)
            except:
                pass

            copy_state_dict = {
                'running': '运行中',
                'shut off': '关闭'
            }

            if copy_state in copy_state_dict:
                copy_state = copy_state_dict[copy_state]
            result.append({
                "id": kvmcopy.id,
                "name": kvmcopy.name,
                "ip": kvmcopy.ip,
                "hostname": kvmcopy.hostname,
                "create_time": kvmcopy.create_time.strftime(
                                '%Y-%m-%d %H:%M:%S') if kvmcopy.create_time else '',
                "create_user": kvmcopy.create_user.userinfo.fullname if kvmcopy.create_user.userinfo.fullname else '',
                "copy_state": copy_state,
            })
    return JsonResponse({"data": result})


@login_required
def kvm_copy_del(request):
    # 删除副本：删除远程 + 删除本地数据库数据
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
    utils_kvm_info = UtilsManage.objects.filter(id=utils_id)
    content = utils_kvm_info[0].content
    util_type = utils_kvm_info[0].util_type
    kvm_credit = get_credit_info(content, util_type.upper())

    filesystem = 'tank/' + name                # tank/CentOS-7@test3
    filesystem = filesystem.replace('@', '-')  # tank/CentOS-7-test3

    try:
        result_info = KVMApi(kvm_credit).undefine(name, state, filesystem)
        if result_info == '删除成功。':
            kvmcopy = KvmCopy.objects.get(id=id)
            kvmcopy.state = '9'
            kvmcopy.save()
            result["res"] = '删除成功。'
        else:
            result["res"] = result_info
    except Exception as e:
        print(e)
        result["res"] = '删除失败。'

    return JsonResponse(result)


@login_required
def kvm_ip_save(request):
    # 远程修改 + 数据库修改
    result = {}
    utils_id = request.POST.get("utils_id", "")
    id = request.POST.get("id", "")
    kvm_ip = request.POST.get("kvm_ip", "")
    username = request.POST.get("username", "")
    password = request.POST.get("password", "")
    password = request.POST.get("password", "")
    os = request.POST.get("os", "")
    try:
        id = int(id)
        utils_id = int(utils_id)
    except:
        pass

    # 登录kvm虚拟机: virsh console CentOS-7@test4
    utils_kvm_info = UtilsManage.objects.filter(id=utils_id)
    content = utils_kvm_info[0].content
    util_type = utils_kvm_info[0].util_type
    kvm_credit = get_credit_info(content, util_type.upper())


@login_required
def kvm_hostname_save(request):
    id = request.POST.get("id", "")
    kvm_hostname = request.POST.get("kvm_hostname", "")


@login_required
def kvm_start(request):
    result = {}
    utils_id = request.POST.get("utils_id", "")
    kvm_name = request.POST.get("kvm_name", "")

    try:
        utils_id = int(utils_id)
    except:
        pass
    utils_kvm_info = UtilsManage.objects.filter(id=utils_id)
    content = utils_kvm_info[0].content
    util_type = utils_kvm_info[0].util_type
    kvm_credit = get_credit_info(content, util_type.upper())

    try:
        result_info = KVMApi(kvm_credit).kvm_start(kvm_name)
        result['res'] = result_info
    except Exception as e:
        print(e)
        result["res"] = '开机失败。'
    return JsonResponse(result)


@login_required
def kvm_shutdown(request):
    result = {}
    utils_id = request.POST.get("utils_id", "")
    kvm_name = request.POST.get("kvm_name", "")

    try:
        utils_id = int(utils_id)
    except:
        pass
    utils_kvm_info = UtilsManage.objects.filter(id=utils_id)
    content = utils_kvm_info[0].content
    util_type = utils_kvm_info[0].util_type
    kvm_credit = get_credit_info(content, util_type.upper())

    try:
        result_info = KVMApi(kvm_credit).kvm_shutdown(kvm_name)
        result['res'] = result_info
    except Exception as e:
        print(e)
        result["res"] = '关机失败。'
    return JsonResponse(result)


def get_client_node(parent, select_id, request):
    nodes = []
    children = parent.children.order_by("sort").exclude(state="9")
    for child in children:
        # 当前用户所在用户组所拥有的 主机访问权限
        # 如当前用户是管理员 均可访问
        if not request.user.is_superuser and child.nodetype == "CLIENT":
            # 能访问当前主机的所有角色
            # 当前用户所在的所有角色
            # 只要匹配一个就展示
            user_in_groups = request.user.userinfo.group.all()
            host_in_groups = child.group_set.all()

            has_privilege = False

            for uig in user_in_groups:
                for hig in host_in_groups:
                    if uig.id == hig.id:
                        has_privilege = True
                        break
            if not has_privilege:
                continue

        node = dict()
        node["text"] = child.host_name
        node["id"] = child.id
        node["type"] = child.nodetype
        node["data"] = {
            "name": child.host_name,
            "remark": child.remark,
            "pname": parent.host_name
        }

        node["children"] = get_client_node(child, select_id, request)
        if child.id in [1,2,3]:
            node["state"] = {"opened": True}
        if child.id==2:
            node["text"] = "<img src = '/static/pages/images/s.png' height='24px'> " + node["text"]
        if child.id==3:
            node["text"] = "<img src = '/static/pages/images/d.png' height='24px'> " + node["text"]
        if child.nodetype=="NODE" and child.id not in [1,2,3]:
            node["text"] = "<i class='jstree-icon jstree-themeicon fa fa-folder icon-state-warning icon-lg jstree-themeicon-custom'></i>" + node["text"]

        if child.nodetype=="CLIENT":
            kvm_client = KvmMachine.objects.exclude(state="9").filter(hostsmanage=child)
            if len(kvm_client)>0:
                node["text"] = "<img src = '/static/pages/images/ts.png' height='24px'> " + node["text"]
            db_client = DbCopyClient.objects.exclude(state="9").filter(hostsmanage=child)
            if len(db_client) > 0:
                if db_client[0].dbtype=="1":
                    node["text"] = "<img src = '/static/pages/images/oracle.png' height='24px'> " + node["text"]
                if db_client[0].dbtype == "2":
                    node["text"] = "<img src = '/static/pages/images/mysql.png' height='24px'> " + node["text"]
            cv_client = CvClient.objects.exclude(state="9").filter(hostsmanage=child)
            if len(cv_client)>0:
                node["text"] = "<img src = '/static/pages/images/cv.png' height='24px'> " + node["text"]
        try:
            if int(select_id) == child.id:
                node["state"] = {"selected": True}
        except:
            pass
        nodes.append(node)
    return nodes


@login_required
def get_client_tree(request):
    select_id = request.POST.get('id', '')
    tree_data = []
    root_nodes = HostsManage.objects.order_by("sort").exclude(state="9").filter(pnode=None).filter(nodetype="NODE")

    for root_node in root_nodes:
        root = dict()
        root["text"] = root_node.host_name
        root["id"] = root_node.id
        root["type"] = root_node.nodetype
        root["data"] = {
            "name": root_node.host_name,
            "remark": root_node.remark,
            "pname": "无"
        }
        if root_node.id==1:
            root["text"] = "<img src = '/static/pages/images/c.png' height='24px'> " + root["text"]
        try:
            if int(select_id) == root_node.id:
                root["state"] = {"opened": True, "selected": True}
            else:
                root["state"] = {"opened": True}
        except:
            root["state"] = {"opened": True}
        root["children"] = get_client_node(root_node, select_id, request)
        tree_data.append(root)
    return JsonResponse({
        "ret": 1,
        "data": tree_data
    })


@login_required
def clientdel(request):
    if 'id' in request.POST:
        id = request.POST.get('id', '')
        try:
            id = int(id)
        except:
            return HttpResponse(0)
        client = HostsManage.objects.get(id=id)
        client.state = "9"
        client.save()

        return HttpResponse(1)
    else:
        return HttpResponse(0)


@login_required
def client_move(request):
    id = request.POST.get('id', '')
    parent = request.POST.get('parent', '')
    old_parent = request.POST.get('old_parent', '')
    position = request.POST.get('position', '')
    old_position = request.POST.get('old_position', '')
    try:
        id = int(id)  # 节点 id
        parent = int(parent)  # 目标位置父节点 pnode_id
        position = int(position)  # 目标位置
        old_parent = int(old_parent)  # 起点位置父节点 pnode_id
        old_position = int(old_position)  # 起点位置
    except:
        return HttpResponse("0")
    # sort = position + 1 sort从1开始

    # 起始节点下方 所有节点  sort -= 1
    old_client_parent = HostsManage.objects.get(id=old_parent)
    old_sort = old_position + 1
    old_clients = HostsManage.objects.exclude(state="9").filter(pnode=old_client_parent).filter(sort__gt=old_sort)

    # 目标节点下方(包括该节点) 所有节点 sort += 1
    client_parent = HostsManage.objects.get(id=parent)
    sort = position + 1
    clients = HostsManage.objects.exclude(state=9).exclude(id=id).filter(pnode=client_parent).filter(sort__gte=sort)

    my_client = HostsManage.objects.get(id=id)

    # 判断目标父节点是否为接口，若为接口无法挪动
    if client_parent.nodetype == "CLIENT":
        return HttpResponse("客户端")
    else:
        # 目标父节点下所有节点 除了自身 接口名称都不得相同 否则重名
        client_same = HostsManage.objects.exclude(state="9").exclude(id=id).filter(pnode=client_parent).filter(
            host_name=my_client.host_name)

        if client_same:
            return HttpResponse("重名")
        else:
            for old_client in old_clients:
                try:
                    old_client.sort -= 1
                    old_client.save()
                except:
                    pass
            for client in clients:
                try:
                    client.sort += 1
                    client.save()
                except:
                    pass

            # 该节点位置变动
            try:
                my_client.pnode = client_parent
                my_client.sort = sort
                my_client.save()
            except:
                pass

            # 起始 结束 点不在同一节点下 写入父节点名称与ID ?
            if parent != old_parent:
                return HttpResponse(client_parent.host_name + "^" + str(client_parent.id))
            else:
                return HttpResponse("0")


@login_required
def client_node_save(request):
    id = request.POST.get("id", "")
    pid = request.POST.get("pid", "")
    node_name = request.POST.get("node_name", "")
    node_remark = request.POST.get("node_remark", "")

    try:
        id = int(id)
    except:
        ret = 0
        info = "网络错误。"
    else:
        if node_name.strip():
            if id == 0:
                try:
                    cur_host_manage = HostsManage()
                    cur_host_manage.pnode_id = pid
                    cur_host_manage.host_name = node_name
                    cur_host_manage.remark = node_remark
                    cur_host_manage.nodetype = "NODE"
                    # 排序
                    sort = 1
                    try:
                        max_sort = HostsManage.objects.exclude(state="9").filter(pnode_id=pid).aggregate(
                            max_sort=Max('sort', distinct=True))["max_sort"]
                        sort = max_sort + 1
                    except:
                        pass
                    cur_host_manage.sort= sort

                    cur_host_manage.save()
                    id=cur_host_manage.id
                except:
                    ret = 0
                    info = "服务器异常。"
                else:
                    ret = 1
                    info = "新增节点成功。"
            else:
                # 修改
                try:
                    cur_host_manage = HostsManage.objects.get(id=id)
                    cur_host_manage.host_name = node_name
                    cur_host_manage.remark = node_remark
                    cur_host_manage.save()

                    ret = 1
                    info = "节点信息修改成功。"
                except:
                    ret = 0
                    info = "服务器异常。"
        else:
            ret = 0
            info = "节点名称不能为空。"
    return JsonResponse({
        "ret": ret,
        "info": info,
        "nodeid": id
    })


@login_required
def get_cvinfo(request):
    # 工具
    utils_manage = UtilsManage.objects.exclude(state='9').filter(util_type='Commvault')
    data = []

    try:
        pool = ThreadPoolExecutor(max_workers=10)

        all_tasks = [pool.submit(get_instance_list, (um)) for um in utils_manage]
        for future in as_completed(all_tasks):
            if future.result():
                data.append(future.result())
    except:
        pass
    # for um in utils_manage:
    #     data.append(get_instance_list(um))

    # 所有关联终端
    destination = CvClient.objects.exclude(state="9").filter(type__in=['2', '3'])

    u_destination = []

    for um in utils_manage:
        destination_list = []
        for d in destination:
            if d.utils.id == um.id:
                destination_list.append({
                    'id':d.id,
                    'name': d.client_name
                })
        u_destination.append({
            'utilid': um.id,
            'utilname':um.name,
            'destination_list': destination_list
        })
    return JsonResponse({
        "ret": 1,
        "info": "查询成功。",
        "data": data,
        'u_destination': u_destination,
    })


@login_required
def get_client_detail(request):
    hostinfo={}
    cvinfo={}
    dbcopyinfo={}
    kvminfo = {}
    id = request.POST.get("id", "")
    try:
        id = int(id)
        host_manage = HostsManage.objects.get(id=id)

    except:
        ret = 0
        info = "当前客户端不存在。"
    else:
        param_list = []
        try:
            config = etree.XML(host_manage.config)

            param_el = config.xpath("//param")
            for v_param in param_el:
                param_list.append({
                    "param_name": v_param.attrib.get("param_name", ""),
                    "variable_name": v_param.attrib.get("variable_name", ""),
                    "param_value": v_param.attrib.get("param_value", ""),
                })
        except:
            ret = 0
            info = "数据格式异常，无法获取。"
        else:
            hostinfo={
                "host_id": host_manage.id,
                "host_ip": host_manage.host_ip,
                "host_name": host_manage.host_name,
                "os": host_manage.os,
                "username": host_manage.username,
                "password": host_manage.password,
                "remark": host_manage.remark,
                "variable_param_list": param_list,
            }
            ret = 1
            info = "查询成功。"

            cc = CvClient.objects.exclude(state="9").filter(hostsmanage_id=id)
            if len(cc) >0:
                cvinfo["id"] = cc[0].id
                cvinfo["type"] = cc[0].type
                cvinfo["utils_id"] = cc[0].utils_id
                cvinfo["client_id"] = cc[0].client_id
                cvinfo["agentType"] = cc[0].agentType
                cvinfo["instanceName"] = cc[0].instanceName
                cvinfo["destination_id"] = cc[0].destination_id

                # oracle
                cvinfo["copy_priority"] = ""
                cvinfo["db_open"] = ""
                cvinfo["log_restore"] = ""
                cvinfo["data_path"] =""
                # File System
                cvinfo["overWrite"] = ""
                cvinfo["destPath"] = ""
                cvinfo["sourcePaths"] =""
                # SQL Server
                cvinfo["mssqlOverWrite"] = ""

                try:
                    config = etree.XML(cc[0].info)
                    param_el = config.xpath("//param")
                    if len(param_el) >0:
                        cvinfo["copy_priority"] = param_el[0].attrib.get("copy_priority", "")
                        cvinfo["db_open"] = param_el[0].attrib.get("db_open", "")
                        cvinfo["log_restore"] = param_el[0].attrib.get("log_restore", "")
                        cvinfo["data_path"] = param_el[0].attrib.get("data_path", "")

                        cvinfo["overWrite"] = param_el[0].attrib.get("overWrite", "")
                        cvinfo["destPath"] = param_el[0].attrib.get("destPath", "")
                        cvinfo["sourcePaths"] = eval(param_el[0].attrib.get("sourcePaths", "[]")) 

                        cvinfo["mssqlOverWrite"] = param_el[0].attrib.get("mssqlOverWrite", "")
                except:
                    pass

            dc = DbCopyClient.objects.exclude(state="9").filter(hostsmanage_id=id)
            if len(dc) >0:
                dbcopyinfo["id"] = dc[0].id
                dbcopyinfo["hosttype"] = dc[0].hosttype
                dbcopyinfo["dbtype"] = dc[0].dbtype
                if dc[0].dbtype=="1":
                    stdclient = DbCopyClient.objects.exclude(state="9").filter(pri=dc[0])
                    dbcopyinfo["std_id"] = None
                    if len(stdclient)>0:
                        dbcopyinfo["std_id"] = stdclient[0].id
                    dbcopyinfo["dbusername"] = ""
                    dbcopyinfo["dbpassowrd"] = ""
                    dbcopyinfo["dbinstance"] = ""

                    try:
                        config = etree.XML(dc[0].info)
                        param_el = config.xpath("//param")
                        if len(param_el) >0:
                            dbcopyinfo["dbusername"] = param_el[0].attrib.get("dbusername", ""),
                            dbcopyinfo["dbpassowrd"] = param_el[0].attrib.get("dbpassowrd", ""),
                            dbcopyinfo["dbinstance"] = param_el[0].attrib.get("dbinstance", ""),
                    except:
                        pass
                if dc[0].dbtype == "2":
                    dbcopyinfo["std_id"] = []
                    stdclientlist = DbCopyClient.objects.exclude(state="9").filter(pri=dc[0])
                    for stdclient in stdclientlist:
                        dbcopyinfo["std_id"].append(str(stdclient.id))
                    dbcopyinfo["dbusername"] = ""
                    dbcopyinfo["dbpassowrd"] = ""
                    dbcopyinfo["copyusername"] = ""
                    dbcopyinfo["copypassowrd"] = ""
                    dbcopyinfo["binlog"] = ""

                    try:
                        config = etree.XML(dc[0].info)
                        param_el = config.xpath("//param")
                        if len(param_el) >0:
                            dbcopyinfo["dbusername"] = param_el[0].attrib.get("dbusername", ""),
                            dbcopyinfo["dbpassowrd"] = param_el[0].attrib.get("dbpassowrd", ""),
                            dbcopyinfo["copyusername"] = param_el[0].attrib.get("copyusername", ""),
                            dbcopyinfo["copypassowrd"] = param_el[0].attrib.get("copypassowrd", ""),
                            dbcopyinfo["binlog"] = param_el[0].attrib.get("binlog", ""),
                    except:
                        pass

            kc = KvmMachine.objects.exclude(state="9").filter(hostsmanage_id=id)
            if len(kc) > 0:
                kvminfo["id"] = kc[0].id
                kvminfo["utils_id"] = kc[0].utils_id
                kvminfo["name"] = kc[0].name
                kvminfo["filesystem"] = kc[0].filesystem
    return JsonResponse({
        "ret": ret,
        "info": info,
        "data": hostinfo,
        "cvinfo":cvinfo,
        "dbcopyinfo": dbcopyinfo,
        "kvminfo": kvminfo
    })


@login_required
def client_client_save(request):
    id = request.POST.get("id", "")
    pid = request.POST.get("pid", "")
    host_ip = request.POST.get("host_ip", "")
    host_name = request.POST.get("host_name", "")
    host_os = request.POST.get("os", "")
    username = request.POST.get("username", "")
    password = request.POST.get("password", "")
    config = request.POST.get("config", "")
    remark = request.POST.get("remark", "")

    try:
        id = int(id)
    except:
        ret = 0
        info = "网络错误。"
    else:
        if host_ip.strip():
            if host_name.strip():
                if host_os.strip():
                    if username.strip():
                        if password.strip():
                            # 主机参数
                            root = etree.Element("root")

                            if config:
                                config = json.loads(config)
                                # 动态参数
                                for c_config in config:
                                    param_node = etree.SubElement(root, "param")
                                    param_node.attrib["param_name"] = c_config["param_name"].strip()
                                    param_node.attrib["variable_name"] = c_config["variable_name"].strip()
                                    param_node.attrib["param_value"] = c_config["param_value"].strip()
                            config = etree.tounicode(root)

                            # 新增
                            if id == 0:
                                # 判断主机是否已经存在
                                check_host_manage = HostsManage.objects.exclude(state="9").filter(host_name=host_name)
                                if check_host_manage.exists():
                                    ret = 0
                                    info = "主机已经存在，请勿重复添加。"
                                else:
                                    try:
                                        cur_host_manage = HostsManage()
                                        cur_host_manage.pnode_id = pid
                                        cur_host_manage.nodetype = "CLIENT"
                                        cur_host_manage.host_ip = host_ip
                                        cur_host_manage.host_name = host_name
                                        cur_host_manage.os = host_os
                                        cur_host_manage.username = username
                                        cur_host_manage.password = password
                                        cur_host_manage.config = config
                                        cur_host_manage.remark = remark
                                        # 排序
                                        sort = 1
                                        try:
                                            max_sort = \
                                            HostsManage.objects.exclude(state="9").filter(pnode_id=pid).aggregate(
                                                max_sort=Max('sort', distinct=True))["max_sort"]
                                            sort = max_sort + 1
                                        except:
                                            pass
                                        cur_host_manage.sort = sort

                                        cur_host_manage.save()
                                        id = cur_host_manage.id
                                    except:
                                        ret = 0
                                        info = "服务器异常。"
                                    else:
                                        ret = 1
                                        info = "主机信息新增成功。"
                            else:
                                # 修改
                                try:
                                    cur_host_manage = HostsManage.objects.get(id=id)
                                    cur_host_manage.host_ip = host_ip
                                    cur_host_manage.host_name = host_name
                                    cur_host_manage.os = host_os
                                    cur_host_manage.username = username
                                    cur_host_manage.password = password
                                    cur_host_manage.config = config
                                    cur_host_manage.remark = remark
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
                    info = "系统未选择。"
            else:
                ret = 0
                info = "主机名称不能为空。"
        else:
            ret = 0
            info = "主机IP未填写。"
    return JsonResponse({
        "ret": ret,
        "info": info,
        "nodeid": id
    })


@login_required
def client_cv_save(request):
    id = request.POST.get("id", "")
    cv_id = request.POST.get("cv_id", "")
    cvclient_type = request.POST.get("cvclient_type", "")
    cvclient_utils_manage = request.POST.get("cvclient_utils_manage", "")
    cvclient_source = request.POST.get("cvclient_source", "")
    cvclient_clientname = request.POST.get("cvclient_clientname", "")
    cvclient_agentType = request.POST.get("cvclient_agentType", "")
    cvclient_instance = request.POST.get("cvclient_instance", "")
    cvclient_destination = request.POST.get("cvclient_destination", "")

    # oracle
    cvclient_copy_priority = request.POST.get("cvclient_copy_priority", "")
    cvclient_db_open = request.POST.get("cvclient_db_open", "")
    cvclient_log_restore = request.POST.get("cvclient_log_restore", "")
    cvclient_data_path = request.POST.get("cvclient_data_path", "")

    # File System
    cv_mypath = request.POST.get("cv_mypath", "")
    cv_iscover = request.POST.get("cv_iscover", "")
    cv_selectedfile = request.POST.get("cv_selectedfile", "")

    # SQL Server
    mssql_iscover = request.POST.get("mssql_iscover", "")

    try:
        id = int(id)
        cv_id = int(cv_id)
        cvclient_utils_manage = int(cvclient_utils_manage)
    except:
        ret = 0
        info = "网络错误。"
    else:
        if cvclient_type.strip():
            if cvclient_source.strip():
                if cvclient_agentType.strip():
                    cv_params = {}
                    if "Oracle" in cvclient_agentType:
                        cv_params = {
                            "copy_priority": cvclient_copy_priority,
                            "db_open": cvclient_db_open,
                            "log_restore": cvclient_log_restore,
                            "data_path": cvclient_data_path,
                        }
                    elif "File System" in cvclient_agentType:
                        inPlace = True
                        if cv_mypath != "same":
                            inPlace = False
                        overWrite = False
                        if cv_iscover == "TRUE":
                            overWrite = True
                        
                        sourceItemlist = cv_selectedfile.split("*!-!*")
                        for sourceItem in sourceItemlist:
                            if sourceItem == "":
                                sourceItemlist.remove(sourceItem)
                        cv_params = {
                            "overWrite": overWrite,
                            "inPlace": inPlace,
                            "destPath": cv_mypath,
                            "sourcePaths": sourceItemlist,
                            "OSRestore": False
                        }
                    elif "SQL Server"in cvclient_agentType:
                        mssqlOverWrite = False
                        if mssql_iscover == "TRUE":
                            mssqlOverWrite = True
                        cv_params = {
                            "mssqlOverWrite": mssqlOverWrite,
                        }
                    # 新增
                    if cv_id == 0:
                        try:
                            cvclient = CvClient()
                            cvclient.hostsmanage_id = id
                            cvclient.utils_id = cvclient_utils_manage
                            cvclient.client_id = cvclient_source
                            cvclient.client_name = cvclient_clientname
                            cvclient.type = cvclient_type
                            cvclient.agentType = cvclient_agentType
                            cvclient.instanceName = cvclient_instance
                            if cvclient_type in ("1","3"):
                                config = custom_cv_params(**cv_params)
                                cvclient.info = config
                                if cvclient_destination!="self":
                                    try:
                                        cvclient_destination = int(cvclient_destination)
                                        cvclient.destination_id = cvclient_destination
                                    except:
                                        pass
                            cvclient.save()
                            if cvclient_destination == "self":
                                cvclient.destination_id = cvclient.id
                                cvclient.save()
                            cv_id = cvclient.id
                        except:
                            ret = 0
                            info = "服务器异常。"
                        else:
                            ret = 1
                            info = "Commvault保护创建成功。"
                    else:
                        # 修改
                        try:
                            cvclient = CvClient.objects.get(id=cv_id)
                            cvclient.hostsmanage_id = id
                            cvclient.utils_id = cvclient_utils_manage
                            cvclient.client_id = cvclient_source
                            cvclient.client_name = cvclient_clientname
                            cvclient.type = cvclient_type
                            cvclient.agentType = cvclient_agentType
                            cvclient.instanceName = cvclient_instance
                            if cvclient_type in ("1","3"):
                                config = custom_cv_params(**cv_params)
                                cvclient.info = config
                                if cvclient_destination=="self":
                                    cvclient.destination_id=cv_id
                                else:
                                    try:
                                        cvclient_destination = int(cvclient_destination)
                                        cvclient.destination_id = cvclient_destination
                                    except Exception as e:
                                        pass
                            cvclient.save()
                            ret = 1
                            info = "Commvault保护修改成功。"
                        except Exception as e:
                            ret = 0
                            info = "服务器异常。"
                else:
                    ret = 0
                    info = "应用类型不能为空。"
            else:
                ret = 0
                info = "源客户端不能为空。"
        else:
            ret = 0
            info = "客户端类型不能为空。"
    return JsonResponse({
        "ret": ret,
        "info": info,
        "cv_id": cv_id
    })


@login_required
def client_cv_del(request):
    if 'id' in request.POST:
        id = request.POST.get('id', '')
        try:
            id = int(id)
        except:
            return HttpResponse(0)
        cv = CvClient.objects.get(id=id)
        cv.state = "9"
        cv.save()

        return HttpResponse(1)
    else:
        return HttpResponse(0)


@login_required
def client_cv_get_backup_his(request):
    id = request.GET.get('id', '')

    result = []
    try:
        id = int(id)
        cvclient = CvClient.objects.get(id=id)
        utils_manage = cvclient.utils
        _, sqlserver_credit = get_credit_info(utils_manage.content)
        dm = SQLApi.CVApi(sqlserver_credit)
        result = dm.get_all_backup_job_list(cvclient.client_name, cvclient.agentType, cvclient.instanceName)
        dm.close()
    except Exception as e:
        print(e)

    return JsonResponse({"data": result})


@login_required
def client_cv_recovery(request):
    if request.method == 'POST':
        cv_id = request.POST.get('cv_id', '')
        sourceClient = request.POST.get('sourceClient', '')
        destClient = request.POST.get('destClient', '')
        restoreTime = request.POST.get('restoreTime', '')
        browseJobId = request.POST.get('browseJobId', '')
        agent = request.POST.get('agent', '')

        #################################
        # sourceClient>> instance_name  #
        #################################
        instance = ""
        try:
            pri = CvClient.objects.exclude(state="9").get(id=int(cv_id))
        except CvClient.DoesNotExist as e:
            return HttpResponse("恢复任务启动失败, 源客户端不存在。")
        else:
            instance = pri.instanceName
            if not instance:
                return HttpResponse("恢复任务启动失败, 实例不存在。")

            # 账户信息
            utils_content = pri.utils.content if pri.utils else ""
            commvault_credit, sqlserver_credit = get_credit_info(utils_content)

            # 区分应用
            if "Oracle" in agent:
                data_path = request.POST.get('data_path', '')
                copy_priority = request.POST.get('copy_priority', '')
                data_sp = request.POST.get('data_sp', '')

                try:
                    copy_priority = int(copy_priority)
                except:
                    pass
                # restoreTime对应curSCN号
                dm = SQLApi.CVApi(sqlserver_credit)
                oraclecopys = dm.get_oracle_backup_job_list(sourceClient)
                # print("> %s" % restoreTime)
                curSCN = ""
                if restoreTime:
                    for i in oraclecopys:
                        if i["subclient"] == "default" and i['LastTime'] == restoreTime:
                            # print('>>>>>1')
                            print(i['LastTime'])
                            curSCN = i["cur_SCN"]
                            break
                else:
                    for i in oraclecopys:
                        if i["subclient"] == "default":
                            # print('>>>>>2')
                            curSCN = i["cur_SCN"]
                            break

                if copy_priority == 2:
                    # 辅助拷贝状态
                    auxcopys = dm.get_all_auxcopys()
                    jobs_controller = dm.get_job_controller()

                    dm.close()

                    # 判断当前存储策略是否有辅助拷贝未完成
                    auxcopy_completed = True
                    for job in jobs_controller:
                        if job['storagePolicy'] == data_sp and job['operation'] == "Aux Copy":
                            auxcopy_completed = False
                            break
                    # 假设未恢复成功
                    if not auxcopy_completed:
                        # 找到成功的辅助拷贝，开始时间在辅助拷贝前的、值对应上的主拷贝备份时间点(最终转化UTC)
                        for auxcopy in auxcopys:
                            if auxcopy['storagepolicy'] == data_sp and auxcopy['jobstatus'] in ["Completed", "Success"]:
                                bytesxferred = auxcopy['bytesxferred']

                                end_tag = False
                                for orcl_copy in oraclecopys:
                                    try:
                                        orcl_copy_starttime = datetime.datetime.strptime(orcl_copy['StartTime'],
                                                                                        "%Y-%m-%d %H:%M:%S")
                                        aux_copy_starttime = datetime.datetime.strptime(auxcopy['startdate'],
                                                                                        "%Y-%m-%d %H:%M:%S")
                                        if orcl_copy[
                                            'numbytesuncomp'] == bytesxferred and orcl_copy_starttime < aux_copy_starttime and \
                                                orcl_copy['subclient'] == "default":
                                            # 获取enddate,转化时间
                                            curSCN = orcl_copy['cur_SCN']
                                            end_tag = True
                                            break
                                    except Exception as e:
                                        print(e)
                                if end_tag:
                                    break

                dm.close()
                oraRestoreOperator = {"curSCN": curSCN, "browseJobId": None, "data_path": data_path,
                                    "copy_priority": copy_priority, "restoreTime": restoreTime}

                cvToken = CV_RestApi_Token()
                cvToken.login(commvault_credit)
                cvAPI = CV_API(cvToken)
                if agent == "Oracle Database":
                    if cvAPI.restoreOracleBackupset(sourceClient, destClient, instance, oraRestoreOperator):
                        return HttpResponse("恢复任务已经启动。" + cvAPI.msg)
                    else:
                        return HttpResponse("恢复任务启动失败。" + cvAPI.msg)
                elif agent.upper() == "Oracle RAC":
                    oraRestoreOperator["browseJobId"] = browseJobId
                    if cvAPI.restoreOracleRacBackupset(sourceClient, destClient, instance, oraRestoreOperator):
                        return HttpResponse("恢复任务已经启动。" + cvAPI.msg)
                    else:
                        return HttpResponse("恢复任务启动失败。" + cvAPI.msg)
                else:
                    return HttpResponse("无当前模块，恢复任务启动失败。")
            elif "File System" in agent:
                iscover = request.POST.get('iscover', '')
                mypath = request.POST.get('mypath', '')
                selectedfile = request.POST.get('selectedfile')
                sourceItemlist = selectedfile.split("*!-!*")
                inPlace = True
                if mypath != "same":
                    inPlace = False
                overWrite = False
                if iscover == "TRUE":
                    overWrite = True

                for sourceItem in sourceItemlist:
                    if sourceItem == "":
                        sourceItemlist.remove(sourceItem)

                fileRestoreOperator = {"restoreTime": restoreTime, "overWrite": overWrite, "inPlace": inPlace,
                                    "destPath": mypath, "sourcePaths": sourceItemlist, "OS Restore": False}

                cvToken = CV_RestApi_Token()
                cvToken.login(commvault_credit)
                cvAPI = CV_API(cvToken)
                if cvAPI.restoreFSBackupset(sourceClient, destClient, "defaultBackupSet", fileRestoreOperator):
                    return HttpResponse("恢复任务已经启动。")
                else:
                    return HttpResponse("恢复任务启动失败。")
            elif "SQL Server" in agent:
                mssql_iscover = request.POST.get('mssql_iscover', '')
                mssqlOverWrite = False
                if mssql_iscover == "TRUE":
                    mssqlOverWrite = True
                cvToken = CV_RestApi_Token()
                cvToken.login(commvault_credit)
                cvAPI = CV_API(cvToken)
                mssql_dbs = cvAPI.get_mssql_db(pri.client_id, instance)
                mssqlRestoreOperator = {"restoreTime": restoreTime, "overWrite": mssqlOverWrite, "mssql_dbs": mssql_dbs}
                if cvAPI.restoreMssqlBackupset(sourceClient, destClient, instance, mssqlRestoreOperator):
                    return HttpResponse("恢复任务已经启动。")
                else:
                    return HttpResponse(u"恢复任务启动失败。")
    else:
        return HttpResponse("恢复任务启动失败。")


@login_required
def client_cv_get_restore_his(request):
    id = request.GET.get('id', '')

    result = []
    try:
        id = int(id)
        cvclient = CvClient.objects.get(id=id)
        utils_manage = cvclient.utils
        _, sqlserver_credit = get_credit_info(utils_manage.content)
        dm = SQLApi.CVApi(sqlserver_credit)
        result = dm.get_all_restore_job_list(cvclient.client_name,cvclient.agentType,cvclient.instanceName)
        dm.close()
    except Exception as e:
        print(e)
    return JsonResponse({"data": result})


@login_required
def get_cv_process(request):
    id = request.POST.get('id', "")
    try:
        id = int(id)
    except:
        id = 0

    cv_process_list = []
    if id != 0:
        # 所属流程
        processlist = Process.objects.filter(hosts_id=id, type='Commvault',processtype="1").exclude(state="9")
        for process in processlist:
            cv_process_list.append({
                "process_id": process.id,
                "process_name": process.name
            })

    return JsonResponse({
        "ret": 1,
        "process": cv_process_list
    })


@login_required
def get_dbcopyinfo(request):
    # 所有关联终端
    stdlist = DbCopyClient.objects.exclude(state="9").filter(hosttype='2')

    u_std = []

    for std in stdlist:
        u_std.append({
            'type':std.dbtype,
            'id':std.id,
            'name': std.hostsmanage.host_name + "(" + std.hostsmanage.host_ip + ")"
        })
    return JsonResponse({
        "ret": 1,
        "info": "查询成功。",
        'u_std': u_std,
    })


@login_required
def get_adg_status(request):
    id = request.POST.get('id', "")
    dbcopy_id = request.POST.get('dbcopy_id', "")
    dbcopy_std = request.POST.get('dbcopy_std', "")
    try:
        dbcopy_id = int(dbcopy_id)
    except:
        dbcopy_id=0
    try:
        dbcopy_std = int(dbcopy_std)
    except:
        dbcopy_std=0
    try:
        id = int(id)
    except:
        id = 0

    host_list = [dbcopy_id, dbcopy_std]

    adg_info_list = []
    adg_process_list = []
    for hostid in host_list:
        if hostid !=0:
            host=DbCopyClient.objects.filter(id=hostid).exclude(state="9")
            if len(host)>0:
                host=host[0]
                db_status = ''
                database_role = ''
                switchover_status = ''
                host_status = 1  # 1为连接，0为断开
                host_name = host.hostsmanage.host_name
                host_ip = host.hostsmanage.host_ip
                host_password = host.hostsmanage.password
                host_username = host.hostsmanage.username
                host_os = host.hostsmanage.os
                # oracle用户名/密码
                oracle_name = ""
                oracle_password = ""
                oracle_instance = ""

                try:
                    config = etree.XML(host.info)
                    param_el = config.xpath("//param")
                    if len(param_el) > 0:
                        oracle_name =  param_el[0].attrib.get("dbusername", ""),
                        oracle_name=oracle_name[0]
                        oracle_password =  param_el[0].attrib.get("dbpassowrd", ""),
                        oracle_password = oracle_password[0]
                        oracle_instance =  param_el[0].attrib.get("dbinstance", ""),
                        oracle_instance = oracle_instance[0]
                except:
                    pass

                try:
                    conn = cx_Oracle.connect('{oracle_name}/{oracle_password}@{host_ip}/{oracle_instance}'.format(
                        oracle_name=oracle_name, oracle_password=oracle_password, host_ip=host_ip,
                        oracle_instance=oracle_instance))
                    curs = conn.cursor()
                    a_db_status_sql = 'select open_mode,switchover_status,database_role from v$database'
                    curs.execute(a_db_status_sql)
                    db_status_row = curs.fetchone()
                    db_status = db_status_row[0] if db_status_row else ""
                    database_role = db_status_row[1] if db_status_row else ""
                    switchover_status = db_status_row[2] if db_status_row else ""
                except Exception as e:
                    check_host = ServerByPara('cd ..', host_ip, host_username, host_password, host_os)
                    result = check_host.run("")
                    if result["exec_tag"] == "1":
                        host_status = 0
                else:
                    curs.close()
                    conn.close()

                adg_info_list.append({
                    "db_status": db_status,
                    "database_role": database_role,
                    "switchover_status": switchover_status,
                    "host_status": host_status,
                    "host_name": host_name,
                    "host_ip": host_ip
                })

    if id != 0:
        processlist = Process.objects.filter(primary=id,type='Oracle ADG',processtype="1").exclude(state="9")
        for process in processlist:
            adg_process_list.append({
                "process_id": process.id,
                "back_id": process.backprocess_id,
                "process_name": process.name
            })

    return JsonResponse({
        "ret": 1,
        "data": adg_info_list,
        "process": adg_process_list
    })


@login_required
def client_dbcopy_get_his(request):
    result = []
    id = request.GET.get("id", "")
    type = request.GET.get("type", "")
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

    allprocess = []
    frontprocess = []
    backprocess = []
    if type=='ADG':
        type='Oracle ADG'

    processlist = Process.objects.filter(primary=id,type=type,processtype="1").exclude(state="9")
    for process in processlist:
        allprocess.append(process.id)
        frontprocess.append(process.id)
        if process.backprocess is not None:
            allprocess.append(process.backprocess.id)
            backprocess.append(process.backprocess.id)
    allprocess_new = [str(x) for x in allprocess]
    strprocess = ','.join(allprocess_new)
    if strprocess=="":
        strprocess="0"

    cursor = connection.cursor()

    exec_sql = """
    select r.starttime, r.endtime, r.creatuser, r.state, r.process_id, r.id, r.run_reason, p.name, p.url, p.type from drm_processrun as r 
    left join drm_process as p on p.id = r.process_id where r.state != '9' and r.state != 'REJECT' and p.id in ({0}) order by r.starttime desc;
    """.format(strprocess)

    cursor.execute(exec_sql)
    rows = cursor.fetchall()
    for processrun_obj in rows:
        create_users = processrun_obj[2] if processrun_obj[2] else ""
        create_user_objs = User.objects.filter(username=create_users)
        create_user_fullname = create_user_objs[0].userinfo.fullname if create_user_objs else ""
        process_type=""
        if processrun_obj[4] in frontprocess:
            process_type = "正切"
        elif processrun_obj[4] in backprocess:
            process_type = "回切"

        result.append({
            "starttime": processrun_obj[0].strftime('%Y-%m-%d %H:%M:%S') if processrun_obj[0] else "",
            "endtime": processrun_obj[1].strftime('%Y-%m-%d %H:%M:%S') if processrun_obj[1] else "",
            "createuser": create_user_fullname,
            "state": state_dict["{0}".format(processrun_obj[3])] if processrun_obj[3] else "",
            "process_id": processrun_obj[4] if processrun_obj[4] else "",
            "processrun_id": processrun_obj[5] if processrun_obj[5] else "",
            "run_reason": processrun_obj[6][:20] if processrun_obj[6] else "",
            "process_name": processrun_obj[7] if processrun_obj[7] else "",
            "process_type": process_type,
            "process_url": processrun_obj[8] if processrun_obj[8] else ""
        })

    return JsonResponse({"data": result})


@login_required
def client_dbcopy_save(request):
    id = request.POST.get("id", "")
    dbcopy_id = request.POST.get("dbcopy_id", "")
    dbcopy_dbtype = request.POST.get("dbcopy_dbtype", "")
    dbcopy_hosttype = request.POST.get("dbcopy_hosttype", "")
    dbcopy_oracleusername = request.POST.get("dbcopy_oracleusername", "")
    dbcopy_oraclepassword = request.POST.get("dbcopy_oraclepassword", "")
    dbcopy_oracleinstance = request.POST.get("dbcopy_oracleinstance", "")
    dbcopy_std = request.POST.get("dbcopy_std", "")

    try:
        id = int(id)
        dbcopy_id = int(dbcopy_id)
    except:
        ret = 0
        info = "网络错误。"
    else:
        if dbcopy_dbtype.strip():
            if dbcopy_hosttype.strip():
                if dbcopy_oracleusername.strip():
                    if dbcopy_oraclepassword.strip():
                        if dbcopy_oracleinstance.strip():
                            # 新增
                            if dbcopy_id == 0:
                                try:
                                    dbcopy = DbCopyClient()
                                    dbcopy.hostsmanage_id = id
                                    dbcopy.dbtype = dbcopy_dbtype
                                    dbcopy.hosttype = dbcopy_hosttype
                                    root = etree.Element("root")
                                    param_node = etree.SubElement(root, "param")
                                    param_node.attrib["dbusername"] = dbcopy_oracleusername
                                    param_node.attrib["dbpassowrd"] = dbcopy_oraclepassword
                                    param_node.attrib["dbinstance"] = dbcopy_oracleinstance
                                    config = etree.tounicode(root)
                                    dbcopy.info = config
                                    dbcopy.save()
                                    dbcopy_id = dbcopy.id
                                    if dbcopy_hosttype == "1":
                                        if dbcopy_std != "none":
                                            try:
                                                dbcopy_std = int(dbcopy_std)
                                                stdclient = DbCopyClient.objects.get(id=dbcopy_std)
                                                stdclient.pri = dbcopy
                                                stdclient.save()
                                            except:
                                                pass
                                except:
                                    ret = 0
                                    info = "服务器异常。"
                                else:
                                    ret = 1
                                    info = "数据库复制保护创建成功。"
                            else:
                                # 修改
                                try:
                                    dbcopy = DbCopyClient.objects.get(id=dbcopy_id)
                                    dbcopy.hostsmanage_id = id
                                    dbcopy.dbtype = dbcopy_dbtype
                                    dbcopy.hosttype = dbcopy_hosttype
                                    root = etree.Element("root")
                                    param_node = etree.SubElement(root, "param")
                                    param_node.attrib["dbusername"] = dbcopy_oracleusername
                                    param_node.attrib["dbpassowrd"] = dbcopy_oraclepassword
                                    param_node.attrib["dbinstance"] = dbcopy_oracleinstance
                                    config = etree.tounicode(root)
                                    dbcopy.info = config
                                    dbcopy.save()
                                    if dbcopy_hosttype == "1":
                                        if dbcopy_std != "none":
                                            try:
                                                dbcopy_std = int(dbcopy_std)
                                                stdclient = DbCopyClient.objects.get(id=dbcopy_std)
                                                stdclient.pri = dbcopy
                                                stdclient.save()
                                            except:
                                                pass
                                    ret = 1
                                    info = "数据库复制保护修改成功。"
                                except:
                                    ret = 0
                                    info = "服务器异常。"

                        else:
                            ret = 0
                            info = "oracle实例名不能为空。"
                    else:
                        ret = 0
                        info = "oracle密码不能为空。"
                else:
                    ret = 0
                    info = "oracle用户名不能为空。"
            else:
                ret = 0
                info = "主机类型不能为空。"
        else:
            ret = 0
            info = "保护类型不能为空。"
    return JsonResponse({
        "ret": ret,
        "info": info,
        "dbcopy_id": dbcopy_id
    })


@login_required
def client_dbcopy_del(request):
    if 'id' in request.POST:
        id = request.POST.get('id', '')
        try:
            id = int(id)
        except:
            return HttpResponse(0)
        dc = DbCopyClient.objects.get(id=id)
        dc.state = "9"
        dc.save()

        return HttpResponse(1)
    else:
        return HttpResponse(0)


@login_required
def client_dbcopy_mysql_save(request):
    id = request.POST.get("id", "")
    dbcopy_id = request.POST.get("dbcopy_id", "")
    dbcopy_dbtype = request.POST.get("dbcopy_dbtype", "")
    dbcopy_hosttype = request.POST.get("dbcopy_hosttype", "")
    dbcopy_mysqlusername = request.POST.get("dbcopy_mysqlusername", "")
    dbcopy_mysqlpassword = request.POST.get("dbcopy_mysqlpassword", "")
    dbcopy_mysqlcopyusername = request.POST.get("dbcopy_mysqlcopyusername", "")
    dbcopy_mysqlcopypassword = request.POST.get("dbcopy_mysqlcopypassword", "")
    dbcopy_mysqlbinlog = request.POST.get("dbcopy_mysqlbinlog", "")
    dbcopy_mysql_std = request.POST.get('dbcopy_mysql_std')
    dbcopy_mysql_std  = json.loads(dbcopy_mysql_std)

    try:
        id = int(id)
        dbcopy_id = int(dbcopy_id)
    except:
        ret = 0
        info = "网络错误。"
    else:
        if dbcopy_dbtype.strip():
            if dbcopy_hosttype.strip():
                if dbcopy_mysqlusername.strip():
                    if dbcopy_mysqlpassword.strip():
                        if dbcopy_mysqlcopyusername.strip():
                            if dbcopy_mysqlcopypassword.strip():
                                if dbcopy_mysqlbinlog.strip():
                                    # 新增
                                    if dbcopy_id == 0:
                                        try:
                                            dbcopy = DbCopyClient()
                                            dbcopy.hostsmanage_id = id
                                            dbcopy.dbtype = dbcopy_dbtype
                                            dbcopy.hosttype = dbcopy_hosttype
                                            root = etree.Element("root")
                                            param_node = etree.SubElement(root, "param")
                                            param_node.attrib["dbusername"] = dbcopy_mysqlusername
                                            param_node.attrib["dbpassowrd"] = dbcopy_mysqlpassword
                                            param_node.attrib["copyusername"] = dbcopy_mysqlcopyusername
                                            param_node.attrib["copypassowrd"] = dbcopy_mysqlcopypassword
                                            param_node.attrib["binlog"] = dbcopy_mysqlbinlog
                                            config = etree.tounicode(root)
                                            dbcopy.info = config
                                            dbcopy.save()
                                            dbcopy_id = dbcopy.id
                                            if dbcopy_hosttype == "1":
                                                if len(dbcopy_mysql_std)>0:
                                                    for std in dbcopy_mysql_std:
                                                        try:
                                                            std = int(std)
                                                            stdclient = DbCopyClient.objects.get(id=std)
                                                            stdclient.pri = dbcopy
                                                            stdclient.save()
                                                        except:
                                                            pass

                                        except:
                                            ret = 0
                                            info = "服务器异常。"
                                        else:
                                            ret = 1
                                            info = "数据库复制保护创建成功。"
                                    else:
                                        # 修改
                                        try:
                                            dbcopy = DbCopyClient.objects.get(id=dbcopy_id)
                                            dbcopy.hostsmanage_id = id
                                            dbcopy.dbtype = dbcopy_dbtype
                                            dbcopy.hosttype = dbcopy_hosttype
                                            root = etree.Element("root")
                                            param_node = etree.SubElement(root, "param")
                                            param_node.attrib["dbusername"] = dbcopy_mysqlusername
                                            param_node.attrib["dbpassowrd"] = dbcopy_mysqlpassword
                                            param_node.attrib["copyusername"] = dbcopy_mysqlcopyusername
                                            param_node.attrib["copypassowrd"] = dbcopy_mysqlcopypassword
                                            param_node.attrib["binlog"] = dbcopy_mysqlbinlog
                                            config = etree.tounicode(root)
                                            dbcopy.info = config
                                            dbcopy.save()
                                            if dbcopy_hosttype == "1":
                                                if len(dbcopy_mysql_std)>0:
                                                    for std in dbcopy_mysql_std:
                                                        try:
                                                            std = int(std)
                                                            stdclient = DbCopyClient.objects.get(id=std)
                                                            stdclient.pri = dbcopy
                                                            stdclient.save()
                                                        except:
                                                            pass
                                            ret = 1
                                            info = "数据库复制保护修改成功。"
                                        except:
                                            ret = 0
                                            info = "服务器异常。"

                                else:
                                    ret = 0
                                    info = "binlog路径不能为空。"
                            else:
                                ret = 0
                                info = "复制密码不能为空。"
                        else:
                            ret = 0
                            info = "复制用户名不能为空。"
                    else:
                        ret = 0
                        info = "mysql密码不能为空。"
                else:
                    ret = 0
                    info = "mysql用户名不能为空。"
            else:
                ret = 0
                info = "主机类型不能为空。"
        else:
            ret = 0
            info = "保护类型不能为空。"
    return JsonResponse({
        "ret": ret,
        "info": info,
        "dbcopy_id": dbcopy_id
    })


@login_required
def get_mysql_status(request):
    id = request.POST.get('id', "")
    dbcopy_id = request.POST.get('dbcopy_id', "")
    dbcopy_mysql_std = request.POST.get('dbcopy_mysql_std')
    dbcopy_mysql_std = json.loads(dbcopy_mysql_std)
    host_list = []
    try:
        id = int(id)
    except:
        id = 0
    try:
        dbcopy_id = int(dbcopy_id)
        host_list.append(dbcopy_id)
    except:
        pass

    if len(dbcopy_mysql_std) > 0:
        for std in dbcopy_mysql_std:
            try:
                std = int(std)
                host_list.append(std)
            except:
                pass


    mysql_info_list = []
    mysql_process_list = []
    if len(host_list) > 0:
        for num,hostid in enumerate(host_list):
            if hostid !=0:
                host=DbCopyClient.objects.filter(id=hostid).exclude(state="9")
                if len(host)>0:
                    host=host[0]
                    db_status = ''
                    database_role = ''
                    switchover_status = ''
                    conn_status = 1  # 1为连接，0为断开
                    host_name = host.hostsmanage.host_name
                    host_ip = host.hostsmanage.host_ip
                    # mysql用户名/密码
                    dbusername = ""
                    dbpassowrd = ""
                    # salve复制状态
                    master_host = ""
                    io_state = ""
                    sql_state = ""

                    try:
                        config = etree.XML(host.info)
                        param_el = config.xpath("//param")
                        if len(param_el) > 0:
                            dbusername =  param_el[0].attrib.get("dbusername", ""),
                            dbusername=dbusername[0]
                            dbpassowrd =  param_el[0].attrib.get("dbpassowrd", ""),
                            dbpassowrd = dbpassowrd[0]
                    except:
                        pass

                    try:
                        conn = pymysql.connect(host_ip, dbusername, dbpassowrd, "mysql")
                        curs = conn.cursor()
                        a_db_status_sql = 'show slave status;'
                        curs.execute(a_db_status_sql)
                        db_status_row = curs.fetchone()
                        master_host= db_status_row[1] if db_status_row else ""
                        io_state = db_status_row[10] if db_status_row else ""
                        sql_state = db_status_row[11] if db_status_row else ""
                    except Exception as e:
                        conn_status = 0
                    else:
                        curs.close()
                        conn.close()

                    mysql_info_list.append({
                        "num": num+1,
                        "conn_status": conn_status,
                        "host_name": host_name,
                        "host_ip": host_ip,
                        "master_host": master_host,
                        "io_state": io_state,
                        "sql_state": sql_state,
                        "masternum": 0,
                    })
        for host in mysql_info_list:
            for master_host in mysql_info_list:
                if host["master_host"] ==master_host["host_ip"] or host["master_host"] == master_host["host_name"]:
                    host["masternum"]=master_host["num"]
                    break


    if id != 0:
        processlist = Process.objects.filter(primary=id,type='MYSQL',processtype="1").exclude(state="9")
        for process in processlist:
            mysql_process_list.append({
                "process_id": process.id,
                "back_id": process.backprocess_id,
                "process_name": process.name
            })

    return JsonResponse({
        "ret": 1,
        "data": mysql_info_list,
        "process": mysql_process_list
    })


@login_required
def get_file_tree(request):
    id = request.POST.get('id', '')
    cv_id = request.POST.get('cv_id', '')
    treedata = []

    try:
        cv_id = int(cv_id)
        pri = CvClient.objects.exclude(state="9").get(id=int(cv_id))
    except Exception:
        pass
    else:
        client_id = pri.client_id
        utils_content = pri.utils.content if pri.utils else ""
        commvault_credit, _ = get_credit_info(utils_content)
        cvToken = CV_RestApi_Token()
        cvToken.login(commvault_credit)
        cvAPI = CV_API(cvToken)
        file_list = []
        try:
            file_list = cvAPI.browse(client_id, "File System", None, id, False)
            for node in file_list:
                root = {}
                root["id"] = node["path"]
                root["pId"] = id
                root["name"] = node["path"]
                if node["DorF"] == "D":
                    root["isParent"] = True
                else:
                    root["isParent"] = False
                treedata.append(root)
        except Exception:
            pass
        treedata = json.dumps(treedata)

    return HttpResponse(treedata)


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


def get_credit_info(content, util_type="COMMVAULT"):
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
    kvm_credit = {
        'KvmHost': '',
        'KvmUser': '',
        'KvmPasswd': '',
        'SystemType': '',
    }

    try:
        doc = etree.XML(content)
        if util_type == 'COMMVAULT':
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

            return commvault_credit, sqlserver_credit
        elif util_type == 'KVM':
            # Kvm账户信息
            try:
                kvm_credit['KvmHost'] = doc.xpath('//KvmHost/text()')[0]
            except:
                pass
            try:
                kvm_credit['KvmUser'] = doc.xpath('//KvmUser/text()')[0]
            except:
                pass
            try:
                kvm_credit['KvmPasswd'] = base64.b64decode(
                    doc.xpath('//KvmPasswd/text()')[0]).decode()
            except:
                pass
            try:
                kvm_credit['SystemType'] = doc.xpath('//SystemType/text()')[0]
            except:
                pass
            return kvm_credit

    except Exception as e:
        print(e)



@login_required
def util_manage_data(request):
    """
    工具管理信息
    """
    util_manage_list = []

    util_manages = UtilsManage.objects.exclude(state='9')

    for um in util_manages:
        if um.util_type.upper() == 'COMMVAULT':
            commvault_credit, sqlserver_credit = get_credit_info(um.content, um.util_type.upper())
            util_manage_list.append({
                'id': um.id,
                'code': um.code,
                'name': um.name,
                'util_type': um.util_type,
                'commvault_credit': commvault_credit,
                'sqlserver_credit': sqlserver_credit,
            })

        elif um.util_type.upper() == 'KVM':
            kvm_credit = get_credit_info(um.content, um.util_type.upper())
            util_manage_list.append({
                'id': um.id,
                'code': um.code,
                'name': um.name,
                'util_type': um.util_type,
                'kvm_credit': kvm_credit
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

    KvmHost = request.POST.get('KvmHost', '')
    KvmUser = request.POST.get('KvmUser', '')
    KvmPasswd = request.POST.get('KvmPasswd', '')
    SystemType = request.POST.get('SystemType', '')

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
            elif util_type.strip().upper() == 'KVM':
                credit = """<?xml version="1.0" ?>
                    <vendor>
                        <KvmHost>{KvmHost}</KvmHost>
                        <KvmUser>{KvmUser}</KvmUser>
                        <KvmPasswd>{KvmPasswd}</KvmPasswd>
                        <SystemType>{SystemType}</SystemType>
                    </vendor>""".format(**{
                    "KvmHost": KvmHost,
                    "KvmUser": KvmUser,
                    "KvmPasswd": base64.b64encode(KvmPasswd.encode()).decode(),
                    "SystemType": SystemType
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
