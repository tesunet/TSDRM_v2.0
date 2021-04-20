# -*- coding: utf-8 -*-
from .commv_views import *
from .basic_views import getpagefuns
from django.contrib.auth.decorators import login_required
from django.db.models import Max
from xml.dom.minidom import Document
from django.http import JsonResponse
from .workflow_views import getLongname


# 组件管理
@login_required
def component_manage(request, funid):
    grouplist = Group.objects.all().exclude(state='9')
    return render(request, "component_manage.html", {
        'username': request.user.userinfo.fullname,
        "pagefuns": getpagefuns(funid, request=request),
        "grouplist": grouplist,
    })


@login_required
def get_component_tree(request):
    status = 1
    info = ""
    data = []
    select_id = request.POST.get("id", "")
    owner = request.POST.get("owner", "SYSTEM")
    root_id = 6
    if owner == "USER":
        root_id = 3

    try:
        root_nodes = TSDRMComponent.objects.order_by("sort").exclude(state="9").filter(id=root_id)
        for root_node in root_nodes:
            root = dict()
            root["text"] = root_node.shortname
            root["id"] = root_node.id
            root["data"] = {
                "pname": "无",
                "guid": root_node.guid
            }
            root["type"] = "NODE"
            try:
                if int(select_id) == root_node.id:
                    root["state"] = {"opened": True, "selected": True}
                else:
                    root["state"] = {"opened": True}
            except Exception as e:
                root["state"] = {"opened": True}
            root["children"] = get_component_node(root_node, select_id)
            data.append(root)
    except Exception as e:
        status = 0
        info = "获取组件树失败。"
    return JsonResponse({
        "status": status,
        "data": data,
        "info": info
    })


def get_component_node(parent, select_id):
    nodes = []
    children = parent.children.order_by("sort").exclude(state="9").exclude(Q(type=None) | Q(type=""))
    for child in children:
        node = dict()
        node["text"] = child.shortname
        node["id"] = child.id
        node["children"] = get_component_node(child, select_id)
        childtype = child.type
        input = []
        if childtype != "NODE":
            childtype = "LEAF"
            if child.input and len(child.input.strip()) > 0:
                tmpInput = xmltodict.parse(child.input, encoding='utf-8')
                if "inputs" in tmpInput and "input" in tmpInput["inputs"]:
                    tmpDTL = tmpInput["inputs"]["input"]
                    if str(type(tmpDTL)) == "<class 'collections.OrderedDict'>":
                        tmpDTL = [tmpDTL]
                    for curinput in tmpDTL:
                        if curinput["source"] == "input":
                            input.append({"code": curinput["code"], "name": curinput["name"],
                                          "type": curinput["type"], "remark": curinput["remark"],
                                          "variable": "True",
                                          "value": ""})
            node["input"] = input
        node["type"] = childtype
        node["data"] = {
            "pname": parent.shortname,
            "name": child.shortname,
            "remark": child.remark,
            "input": input
        }

        try:
            if int(select_id) == child.id:
                node["state"] = {"selected": True}
        except:
            pass
        nodes.append(node)
    return nodes


@login_required
def get_component_detail(request):
    status = 1
    info = ""
    data = {}

    component_id = request.POST.get("id", "")

    try:
        component_id = int(component_id)
        component = TSDRMComponent.objects.get(id=component_id)
    except Exception as e:
        status = 0
        info = "获取组件信息失败。"
    else:
        input = []
        if component.input and len(component.input.strip()) > 0:
            tmpInput = xmltodict.parse(component.input)
            if "inputs" in tmpInput and "input" in tmpInput["inputs"]:
                tmpDTL = tmpInput["inputs"]["input"]
                if str(type(tmpDTL)) == "<class 'collections.OrderedDict'>":
                    tmpDTL = [tmpDTL]
                for curinput in tmpDTL:
                    input.append({"code": curinput["code"], "name": curinput["name"], "type": curinput["type"],
                                  "remark": curinput["remark"], "source": curinput["source"], "value": curinput["value"],"sort":curinput["sort"]})
        output = []
        if component.output and len(component.output.strip()) > 0:
            tmpoutput = xmltodict.parse(component.output)
            if "outputs" in tmpoutput and "output" in tmpoutput["outputs"]:
                tmpDTL = tmpoutput["outputs"]["output"]
                if str(type(tmpDTL)) == "<class 'collections.OrderedDict'>":
                    tmpDTL = [tmpDTL]
                for curoutput in tmpDTL:
                    output.append({"code": curoutput["code"], "name": curoutput["name"], "type": curoutput["type"],
                                  "remark": curoutput["remark"], "sort":curoutput["sort"]})
        variable = []
        if component.variable and len(component.variable.strip()) > 0:
            tmpvariable = xmltodict.parse(component.variable)
            if "variables" in tmpvariable and "variable" in tmpvariable["variables"]:
                tmpDTL = tmpvariable["variables"]["variable"]
                if str(type(tmpDTL)) == "<class 'collections.OrderedDict'>":
                    tmpDTL = [tmpDTL]
                for curvariable in tmpDTL:
                    variable.append({"code": curvariable["code"], "name": curvariable["name"], "type": curvariable["type"],
                                   "remark": curvariable["remark"], "value": curvariable["value"],"sort":curvariable["sort"]})

        data = {
            "pname": component.pnode.shortname if component.pnode else "",
            "id": component.id,
            "guid": component.guid,
            "createtime": component.createtime.strftime(
                '%Y-%m-%d %H:%M:%S') if component.createtime else '',
            "updatetime": component.updatetime.strftime(
                '%Y-%m-%d %H:%M:%S') if component.updatetime else '',
            "createuser": component.createuser.userinfo.fullname if component.createuser else "",
            "updateuser": component.updateuser.userinfo.fullname if component.updateuser else "",
            "shortname": component.shortname,
            "type": component.type,
            "owner": component.owner,
            "group": [x.id for x in component.group.all()],
            "icon": component.icon,
            "language": component.language,
            "code": component.code,
            "input": input,
            "output": output,
            "variable": variable,
            "version": component.version,
            "remark": component.remark,
            "sort": component.sort,

        }
    return JsonResponse({
        "status": status,
        "data": data,
        "info": info
    })


@login_required
def component_save(request):
    status = 1
    info = "保存成功。"
    select_id = ""
    createtime = None
    updatetime = None
    createuser = None
    updateuser = None

    id = request.POST.get('id', '')
    pid = request.POST.get('pid', '')
    type = request.POST.get('type', '')
    node_name = request.POST.get('node_name', '')
    node_remark = request.POST.get('node_remark', '')
    shortname = request.POST.get('shortname', '')
    language = request.POST.get('component_language', '')
    code = request.POST.get('script_code', '')
    remark = request.POST.get('remark', '')
    input_arr = request.POST.get("input_arr")
    variable_arr = request.POST.get("variable_arr")
    output_arr = request.POST.get("output_arr")


    try:
        id = int(id)
        pid = int(pid)
    except Exception as e:
        pass

    if type == "NODE":
        if node_name.strip() == '':
            status = 0
            info = '节点名称不能为空。'
        else:
            if id == 0:
                try:
                    sort = 1
                    try:
                        max_sort = TSDRMComponent.objects.exclude(state="9").filter(pnode_id=pid).aggregate(
                            max_sort=Max('sort', distinct=True))["max_sort"]
                        sort = max_sort + 1
                    except:
                        pass
                    componentsave = TSDRMComponent()
                    componentsave.shortname = node_name
                    componentsave.sort = sort if sort else None
                    componentsave.remark = node_remark
                    componentsave.type = "NODE"
                    componentsave.pnode_id = pid

                    componentsave.createtime = datetime.datetime.now()
                    componentsave.updatetime = datetime.datetime.now()
                    componentsave.createuser = request.user
                    componentsave.updateuser = request.user
                    componentsave.save()
                    componentsave.longname = getLongname(componentsave)
                    componentsave.save()

                    select_id = componentsave.id
                except Exception as e:
                    info = "保存失败：{0}1".format(e)
                    status = 0
            else:
                # 修改
                try:
                    componentsave = TSDRMComponent.objects.get(id=id)
                    componentsave.name = node_name
                    componentsave.remark = node_remark
                    componentsave.updatetime = datetime.datetime.now()
                    componentsave.updateuser = request.user
                    componentsave.save()
                    componentsave.longname = getLongname(componentsave)
                    componentsave.save()

                    select_id = componentsave.id
                except Exception as e:
                    info = "保存失败：{0}2".format(e)
                    status = 0
    else:
        if shortname.strip() == '':
            info = '短名称不能为空。'
            status = 0
        else:
            input_params_xml = ''
            if input_arr != '':
                list_arr = split_input_option_value(input_arr)
                input_dict = {"inputs": {"input": list_arr}}
                input_params_xml = xmltodict.unparse(input_dict, encoding='utf-8')
            else:
                pass
            variable_params_xml = ''
            if variable_arr != '':
                list_arr = split_variable_option_value(variable_arr)
                variable_dict = {"variables": {"variable": list_arr}}
                variable_params_xml = xmltodict.unparse(variable_dict, encoding='utf-8')
            else:
                pass
            output_params_xml = ''
            if output_arr != '':
                list_arr = split_output_option_value(output_arr)
                output_dict = {"outputs": {"output": list_arr}}
                output_params_xml = xmltodict.unparse(output_dict, encoding='utf-8')
            else:
                pass

            if id == 0:
                try:
                    sort = 1
                    try:
                        max_sort = TSDRMComponent.objects.exclude(state="9").filter(pnode_id=pid).aggregate(
                            max_sort=Max('sort', distinct=True))["max_sort"]
                        sort = max_sort + 1
                    except:
                        pass
                    componentsave = TSDRMComponent()
                    componentsave.guid = uuid.uuid1()
                    componentsave.shortname = shortname
                    componentsave.owner = "USER"
                    componentsave.language = language
                    componentsave.input = input_params_xml
                    componentsave.variable = variable_params_xml
                    componentsave.output = output_params_xml
                    componentsave.code = code
                    componentsave.sort = sort if sort else None
                    componentsave.remark = remark
                    componentsave.type = "LEAF"
                    componentsave.pnode_id = pid

                    componentsave.createtime = datetime.datetime.now()
                    componentsave.updatetime = datetime.datetime.now()
                    componentsave.createuser = request.user
                    componentsave.updateuser = request.user
                    componentsave.save()
                    componentsave.longname = getLongname(componentsave)
                    componentsave.save()
                    componentsave.group.clear()

                    select_id = componentsave.id
                    createtime = componentsave.createtime.strftime(
                        '%Y-%m-%d %H:%M:%S') if componentsave.createtime else '',
                    updatetime = componentsave.updatetime.strftime(
                        '%Y-%m-%d %H:%M:%S') if componentsave.updatetime else '',
                    createuser = request.user.userinfo.fullname
                    updateuser = request.user.userinfo.fullname
                except Exception as e:
                    # info = "保存失败：{0}".format(e)
                    status = 0
            else:
                try:
                    componentsave = TSDRMComponent.objects.get(id=id)
                    componentsave.shortname = shortname
                    componentsave.remark = remark
                    componentsave.language = language
                    componentsave.code = code
                    componentsave.input = input_params_xml
                    componentsave.variable = variable_params_xml
                    componentsave.output = output_params_xml
                    componentsave.updatetime = datetime.datetime.now()
                    componentsave.updateuser = request.user
                    componentsave.save()
                    componentsave.longname = getLongname(componentsave)
                    componentsave.save()
                    select_id = componentsave.id
                    updatetime = componentsave.updatetime.strftime(
                        '%Y-%m-%d %H:%M:%S') if componentsave.updatetime else '',
                    updateuser = request.user.userinfo.fullname
                except Exception as e:
                    info = "保存失败：{0}3".format(e)
                    status = 0

    return JsonResponse({
        "status": status,
        "info": info,
        "data": select_id,
        "createtime": createtime,
        "updatetime": updatetime,
        "createuser": createuser,
        "updateuser": updateuser,
    })

@login_required
def component_move(request):
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
    old_component_parent = TSDRMComponent.objects.get(id=old_parent)
    old_sort = old_position + 1
    old_components = TSDRMComponent.objects.exclude(state="9").filter(pnode=old_component_parent).filter(sort__gt=old_sort)

    # 目标节点下方(包括该节点) 所有节点 sort += 1
    component_parent = TSDRMComponent.objects.get(id=parent)
    sort = position + 1
    components = TSDRMComponent.objects.exclude(state=9).exclude(id=id).filter(pnode=component_parent).filter(sort__gte=sort)

    my_component = TSDRMComponent.objects.get(id=id)

    # 判断目标父节点是否为叶子，若为叶子无法挪动
    if component_parent.type != "NODE":
        return HttpResponse("组件")
    else:
        # 目标父节点下所有节点 除了自身 组件名称都不得相同 否则重名
        component_same = TSDRMComponent.objects.exclude(state="9").exclude(id=id).filter(pnode=component_parent).filter(
            shortname=my_component.shortname)

        if component_same:
            return HttpResponse("重名")
        else:
            for old_component in old_components:
                try:
                    old_component.sort -= 1
                    old_component.save()
                except:
                    pass
            for component in components:
                try:
                    component.sort += 1
                    component.save()
                except:
                    pass

            # 该节点位置变动
            try:
                my_component.pnode = component_parent
                my_component.sort = sort
                my_component.save()
                my_component.longname = getLongname(my_component)
                my_component.save()
            except:
                pass

            # 起始 结束 点不在同一节点下 写入父节点名称与ID ?
            if parent != old_parent:
                return HttpResponse(component_parent.shortname + "^" + str(component_parent.id))
            else:
                return HttpResponse("0")

@login_required
def component_del(request):
    if 'id' in request.POST:
        id = request.POST.get('id', '')
        try:
            id = int(id)
        except:
            raise Http404()
        component = TSDRMComponent.objects.get(id=id)
        component.state = "9"
        component.save()

        return HttpResponse(1)
    else:
        return HttpResponse(0)

# 拆解input的option的value信息
def split_input_option_value(arr_string):
    list_double = []
    list_params = []
    a_list = arr_string.split("##")
    for i in a_list:
        i_list = i.split("^")
        list_double.append(i_list)
    for i in list_double:
        list_params.append({"code": i[0], "name": i[1], "type": i[2], "source": i[3], "remark": i[4], "sort": i[5], "value": i[6]})
    return list_params

# 拆解variable的option的value信息
def split_variable_option_value(arr_string):
    list_double = []
    list_params = []
    a_list = arr_string.split("##")
    for i in a_list:
        i_list = i.split("^")
        list_double.append(i_list)
    for i in list_double:
        list_params.append({"code": i[0], "name": i[1], "type": i[2], "remark": i[3], "sort": i[4], "value": i[5]})
    return list_params

# 拆解variable的option的value信息
def split_output_option_value(arr_string):
    list_double = []
    list_params = []
    a_list = arr_string.split("##")
    for i in a_list:
        i_list = i.split("^")
        list_double.append(i_list)
    for i in list_double:
        list_params.append({"code": i[0], "name": i[1], "type": i[2], "remark": i[3], "sort": i[4]})
    return list_params