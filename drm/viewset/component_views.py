# -*- coding: utf-8 -*-
from .commv_views import *
from .basic_views import getpagefuns
from django.contrib.auth.decorators import login_required
from django.db.models import Max
from xml.dom.minidom import Document
from django.http import JsonResponse
import copy


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
    type = request.POST.get('my_type', '')

    node_name = request.POST.get('node_name', '')
    node_remark = request.POST.get('node_remark', '')

    shortname = request.POST.get('shortname', '')
    group = request.POST.getlist('group', [])
    icon = request.POST.get('icon', '')
    version = request.POST.get('version', '')
    language = request.POST.get('component_language', '')
    code = request.POST.get('script_code', '')
    remark = request.POST.get('remark', '')

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
                    info = "保存失败：{0}".format(e)
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
                    info = "保存失败：{0}".format(e)
                    status = 0
    else:
        allgroup = Group.objects.exclude(state="9")
        if shortname.strip() == '':
            info = '短名称不能为空。'
            status = 0
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
                    componentsave.guid = uuid.uuid1()
                    componentsave.shortname = shortname
                    componentsave.owner = "USER"
                    componentsave.icon = icon
                    componentsave.version = version
                    componentsave.language = language
                    componentsave.cod = code
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
                    for groupid in group:
                        try:
                            groupid = int(groupid)
                            mygroup = allgroup.get(id=groupid)
                            componentsave.group.add(mygroup)
                        except ValueError:
                            raise Http404()

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
                    componentsave.icon = icon
                    componentsave.version = version
                    componentsave.remark = remark
                    componentsave.language = language
                    componentsave.code = code
                    componentsave.updatetime = datetime.datetime.now()
                    componentsave.updateuser = request.user
                    componentsave.save()
                    componentsave.longname = getLongname(componentsave)
                    componentsave.save()
                    componentsave.group.clear()
                    for groupid in group:
                        try:
                            groupid = int(groupid)
                            mygroup = allgroup.get(id=groupid)
                            componentsave.group.add(mygroup)
                        except ValueError:
                            raise Http404()

                    select_id = componentsave.id
                    updatetime = componentsave.updatetime.strftime(
                        '%Y-%m-%d %H:%M:%S') if componentsave.updatetime else '',
                    updateuser = request.user.userinfo.fullname
                except Exception as e:
                    info = "保存失败：{0}".format(e)
                    status = 0

    return JsonResponse({
        "status": status,
        "info": info,
        "data": select_id,
        "createtime": createtime,
        "updatetime": updatetime,
        "createuser": createuser,
        "updateuser": updateuser,
        "component_language": language,
        "script_code": code
    })


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


def getLongname(node):
    if node.pnode is None:
        return node.shortname
    else:
        return getLongname(node.pnode) + "-" + node.shortname


# 从页面获取输入的参数和要修改的参数
@login_required
def component_form_input(request):
    if request.method == "POST":
        request_data = json.loads(request.body.decode())
        try:
            component_input_content = TSDRMComponent.objects.get(guid__exact=request_data["guid"])
            component_input_values = TSDRMComponent.objects.filter(guid__exact=request_data["guid"]).values("input")
        except Exception as e:
            return JsonResponse({
                "status": 4,
                "input": str(e)
            })
        else:
            if request_data["isnew"] == "0":
                input_content_xml = component_input_values[0]["input"]
                request_copy = copy.deepcopy(request_data)
                request_copy.pop("guid")
                request_copy.pop("isnew")
                update_Orderdict = update_input_params(input_content_xml, request_copy)
                if str(update_Orderdict) == "a bytes-like object is required, not 'NoneType'":
                    return JsonResponse({
                        "status": 4,
                        "input": "没有参数信息，请新增后再来修改"
                    })
                else:
                    xml_return_db = xmltodict.unparse(update_Orderdict)
                    component_input_content.input = xml_return_db
                    component_input_content.save()
                    return JsonResponse({
                        "status": 2,
                        "input": "修改成功"
                    })
            else:
                input_content_xml = component_input_values[0]["input"]
                if str(type(input_content_xml)) == "<class 'str'>":
                    input_orderdict = xmltodict.parse(input_content_xml, encoding='utf-8')
                    if "inputs" in input_orderdict and "input" in input_orderdict["inputs"]:
                        tmpDTL = input_orderdict["inputs"]["input"]
                        if str(type(tmpDTL)) == "<class 'collections.OrderedDict'>":
                            tmpDTL = [tmpDTL]
                        code_list = []
                        for curinput in tmpDTL:
                            code_list.append(curinput["code"])
                        if request_data["code"] in code_list:
                            return JsonResponse({
                                "status": 3,
                                "input": "参数名已存在,无法继续添加"
                            })
                        else:
                            request_copy = copy.deepcopy(request_data)
                            request_copy.pop("guid")
                            request_copy.pop("isnew")
                            xml_return_db = xmltodict.unparse(append_input_params(component_input_content.input, request_copy), encoding='utf-8')
                            component_input_content.input = xml_return_db
                            component_input_content.save()
                            return JsonResponse({
                                "status": 1,
                                "input": '保存成功'
                            })
                else:
                    request_copy = copy.deepcopy(request_data)
                    request_copy.pop("guid")
                    request_copy.pop("isnew")
                    xml_return_db = xmltodict.unparse({"inputs": {"input": request_copy}}, encoding='utf-8')
                    component_input_content.input = xml_return_db
                    component_input_content.save()
                    return JsonResponse({
                        "status": 1,
                        "input": '保存成功'
                    })
    else:
        return JsonResponse({
            "status": 0,
            "input": '保存失败'
        })


# 从页面获取新增输入的参数和要修改的参数
@login_required
def component_form_variable(request):
    if request.method == "POST":
        request_data = json.loads(request.body.decode())
        try:
            component_variable_content = TSDRMComponent.objects.get(guid__exact=request_data["guid"])
            component_variable_values = TSDRMComponent.objects.filter(guid__exact=request_data["guid"]).values("variable")
        except Exception as e:
            return JsonResponse({
                "status": 4,
                "variable": e
            })
        else:
            if request_data["isnew"] == "0":
                variable_content_xml = component_variable_values[0]["variable"]
                request_copy = copy.deepcopy(request_data)
                request_copy.pop("guid")
                request_copy.pop("isnew")
                update_Orderdict = update_variable_params(variable_content_xml, request_copy)
                if str(update_Orderdict) == "a bytes-like object is required, not 'NoneType'":
                    return JsonResponse({
                        "status": 4,
                        "variable": "没有参数信息，请新增后再来修改"
                    })
                else:
                    xml_return_db = xmltodict.unparse(update_Orderdict)
                    component_variable_content.input = xml_return_db
                    component_variable_content.save()
                    return JsonResponse({
                        "status": 2,
                        "variable": "修改成功"
                    })
            else:
                variable_content_xml = component_variable_values[0]["variable"]
                if str(type(variable_content_xml)) == "<class 'str'>":
                    variable_orderdict = xmltodict.parse(variable_content_xml, encoding='utf-8')
                    if "variables" in variable_orderdict and "variable" in variable_orderdict["variables"]:
                        tmpDTL = variable_orderdict["variables"]["variable"]
                        if str(type(tmpDTL)) == "<class 'collections.OrderedDict'>":
                            tmpDTL = [tmpDTL]
                        code_list = []
                        for curvariable in tmpDTL:
                            code_list.append(curvariable["code"])
                        if request_data["code"] in code_list:
                            return JsonResponse({
                                "status": 3,
                                "variable": "参数名已存在,无法继续添加"
                            })
                        else:
                            request_copy = copy.deepcopy(request_data)
                            request_copy.pop("guid")
                            request_copy.pop("isnew")
                            xml_return_db = xmltodict.unparse(append_variable_params(component_variable_content.variable, request_copy), encoding='utf-8')
                            component_variable_content.variable = xml_return_db
                            component_variable_content.save()
                            return JsonResponse({
                                "status": 1,
                                "variable": '保存成功'
                            })
                else:
                    request_copy = copy.deepcopy(request_data)
                    request_copy.pop("guid")
                    request_copy.pop("isnew")
                    xml_return_db = xmltodict.unparse({"variables": {"variable": request_copy}}, encoding='utf-8')
                    component_variable_content.variable = xml_return_db
                    component_variable_content.save()
                    return JsonResponse({
                        "status": 1,
                        "variable": '保存成功'
                    })
    else:
        return JsonResponse({
            "status": 0,
            "variable": '保存失败'
        })


# 从页面获取输入的参数和要修改的参数
@login_required
def component_form_output(request):
    if request.method == "POST":
        request_data = json.loads(request.body.decode())
        try:
            component_output_content = TSDRMComponent.objects.get(guid__exact=request_data["guid"])
            component_output_values = TSDRMComponent.objects.filter(guid__exact=request_data["guid"]).values("output")
        except Exception as e:
            return JsonResponse({
                "status": 4,
                "output": e
            })
        else:
            if request_data["isnew"] == "0":
                output_content_xml = component_output_values[0]["output"]
                request_copy = copy.deepcopy(request_data)
                request_copy.pop("guid")
                request_copy.pop("isnew")
                update_Orderdict = update_output_params(output_content_xml, request_copy)
                if str(update_Orderdict) == "a bytes-like object is required, not 'NoneType'":
                    return JsonResponse({
                        "status": 4,
                        "output": "没有参数信息，请新增后再来修改"
                    })
                else:
                    xml_return_db = xmltodict.unparse(update_Orderdict)
                    component_output_content.input = xml_return_db
                    component_output_content.save()
                    return JsonResponse({
                        "status": 2,
                        "output": "修改成功"
                    })
            else:
                output_content_xml = component_output_values[0]["output"]
                if str(type(output_content_xml)) == "<class 'str'>":
                    output_orderdict = xmltodict.parse(output_content_xml, encoding='utf-8')
                    if "outputs" in output_orderdict and "output" in output_orderdict["outputs"]:
                        tmpDTL = output_orderdict["outputs"]["output"]
                        if str(type(tmpDTL)) == "<class 'collections.OrderedDict'>":
                            tmpDTL = [tmpDTL]
                        code_list = []
                        for curoutput in tmpDTL:
                            code_list.append(curoutput["code"])
                        if request_data["code"] in code_list:
                            return JsonResponse({
                                "status": 3,
                                "output": "参数名已存在,无法继续添加"
                            })
                        else:
                            request_copy = copy.deepcopy(request_data)
                            request_copy.pop("guid")
                            request_copy.pop("isnew")
                            xml_return_db = xmltodict.unparse(append_output_params(component_output_content.output, request_copy), encoding='utf-8')
                            component_output_content.output = xml_return_db
                            component_output_content.save()
                            return JsonResponse({
                                "status": 1,
                                "output": '保存成功'
                            })
                else:
                    request_copy = copy.deepcopy(request_data)
                    request_copy.pop("guid")
                    request_copy.pop("isnew")
                    xml_return_db = xmltodict.unparse({"outputs": {"output": request_copy}}, encoding='utf-8')
                    component_output_content.output = xml_return_db
                    component_output_content.save()
                    return JsonResponse({
                        "status": 1,
                        "output": '保存成功'
                    })
    else:
        return JsonResponse({
            "status": 0,
            "output": '保存失败'
        })



# 根据页面修改db已有的输入参数
def update_input_params(input_content_xml, request_input_code):
    try:
        xml_tmp = xmltodict.parse(input_content_xml, encoding='utf-8')
    except Exception as e:
        return e
    else:
        tmp = xml_tmp["inputs"]["input"]
        if input_content_xml.count("<input>") > 1:
            for i in tmp:
                if i["code"] == request_input_code["code"]:
                    i["name"] = request_input_code["name"]
                    i["type"] = request_input_code["type"]
                    i["source"] = request_input_code["source"]
                    i["value"] = request_input_code["value"]
                    i["sort"] = request_input_code["sort"]
                    i["remark"] = request_input_code["remark"]
            return xml_tmp
        else:
            tmp["name"] = request_input_code["name"]
            tmp["type"] = request_input_code["type"]
            tmp["source"] = request_input_code["source"]
            tmp["value"] = request_input_code["value"]
            tmp["sort"] = request_input_code["sort"]
            tmp["remark"] = request_input_code["remark"]
            return xml_tmp


# 根据页面添加输入参数到db
def append_input_params(dbxml, request_dict):
    dict_xml = xmltodict.parse(xmltodict.unparse({"input": request_dict}, encoding='utf-8'))
    xml_tmp = xmltodict.parse(dbxml, encoding='utf-8')
    if dbxml.count("<input>") > 1:
        xml_tmp["inputs"]["input"].append(dict_xml['input'])
    else:
        list_input = [xml_tmp['inputs']['input']]
        list_input.append(dict_xml['input'])
        xml_tmp['inputs']['input'] = list_input
    return xml_tmp


# 根据页面修改db已有的临时变量参数
def update_variable_params(variable_content_xml, request_variable_code):
    try:
        xml_tmp = xmltodict.parse(variable_content_xml, encoding='utf-8')
    except Exception as e:
        return e
    tmp = xml_tmp["variables"]["variable"]
    if variable_content_xml.count("<variable>") > 1:
        for i in tmp:
            if i["code"] == request_variable_code["code"]:
                i["name"] = request_variable_code["name"]
                i["type"] = request_variable_code["type"]
                i["value"] = request_variable_code["value"]
                i["sort"] = request_variable_code["sort"]
                i["remark"] = request_variable_code["remark"]
        return xml_tmp
    else:
        tmp["name"] = request_variable_code["name"]
        tmp["type"] = request_variable_code["type"]
        tmp["value"] = request_variable_code["value"]
        tmp["sort"] = request_variable_code["sort"]
        tmp["remark"] = request_variable_code["remark"]
        return xml_tmp


# 根据页面添加输入参数到db
def append_variable_params(dbxml, request_dict):
    dict_xml = xmltodict.parse(xmltodict.unparse({"variable": request_dict}, encoding='utf-8'))
    xml_tmp = xmltodict.parse(dbxml, encoding='utf-8')
    if dbxml.count("<variable>") > 1:
        xml_tmp["variables"]["variable"].append(dict_xml['variable'])
    else:
        list_variable = [xml_tmp['variables']['variable']]
        list_variable.append(dict_xml['variable'])
        xml_tmp['variables']['variable'] = list_variable
    return xml_tmp

# 根据页面修改db已有的输出变量参数
def update_output_params(output_content_xml, request_output_code):
    try:
        xml_tmp = xmltodict.parse(output_content_xml, encoding='utf-8')
    except Exception as e:
        return e
    tmp = xml_tmp["outputs"]["output"]
    if output_content_xml.count("<output>") > 1:
        for i in tmp:
            if i["code"] == request_output_code["code"]:
                i["name"] = request_output_code["name"]
                i["type"] = request_output_code["type"]
                i["sort"] = request_output_code["sort"]
                i["remark"] = request_output_code["remark"]
        return xml_tmp
    else:
        tmp["name"] = request_output_code["name"]
        tmp["type"] = request_output_code["type"]
        tmp["sort"] = request_output_code["sort"]
        tmp["remark"] = request_output_code["remark"]
        return xml_tmp


# 根据页面添加输出参数到db
def append_output_params(dbxml, request_dict):
    dict_xml = xmltodict.parse(xmltodict.unparse({"output": request_dict}, encoding='utf-8'))
    xml_tmp = xmltodict.parse(dbxml, encoding='utf-8')
    if dbxml.count("<output>") > 1:
        xml_tmp["outputs"]["output"].append(dict_xml['output'])
    else:
        list_output = [xml_tmp['outputs']['output']]
        list_output.append(dict_xml['output'])
        xml_tmp['outputs']['output'] = list_output
    return xml_tmp

