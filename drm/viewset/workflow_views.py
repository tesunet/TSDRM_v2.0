# 流程管理
from .commv_views import *
from .basic_views import getpagefuns
from django.contrib.auth.decorators import login_required
from django.db.models import Max
from xml.dom.minidom import Document

######################
# 流程管理
######################
@login_required
def workflowlist(request, funid):
    grouplist = Group.objects.all().exclude(state='9')
    return render(request, "workflowlist.html", {
        'username': request.user.userinfo.fullname,
        "pagefuns": getpagefuns(funid, request=request),
        "grouplist": grouplist
    })


@login_required
def get_workflow_tree(request):
    status = 1
    info = ""
    data = []
    select_id = request.POST.get("id", "")

    try:
        root_nodes = TSDRMWorkflow.objects.order_by("sort").exclude(state="9").filter(pnode=None)
        for root_node in root_nodes:
            root = dict()
            root["text"] = root_node.shortname
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
            root["children"] = get_workflow_node(root_node, select_id)
            data.append(root)
    except Exception as e:
        status = 0
        info = "获取流程树失败。"
    return JsonResponse({
        "status": status,
        "data": data,
        "info": info
    })


def get_workflow_node(parent, select_id):
    nodes = []
    children = parent.children.order_by("sort").exclude(state="9").exclude(Q(type=None) | Q(type=""))
    for child in children:
        node = dict()
        node["text"] = child.shortname
        node["id"] = child.id
        node["children"] = get_workflow_node(child, select_id)
        childtype=child.type
        if childtype != "NODE":
            childtype="LEAF"
        node["type"] = childtype
        node["data"] = {
            "pname": parent.shortname,
            "name": child.shortname,
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
def get_workflow_detail(request):
    status = 1
    info = ""
    data = {}

    workflow_id = request.POST.get("id", "")

    try:
        workflow_id = int(workflow_id)
        workflow = TSDRMWorkflow.objects.get(id=workflow_id)
    except Exception as e:
        status = 0
        info = "获取流程信息失败。"
    else:
        data = {
            "pname": workflow.pnode.shortname if workflow.pnode else "",
            "id": workflow.id,
            "guid": workflow.guid,
            "createtime": workflow.createtime.strftime(
                                '%Y-%m-%d %H:%M:%S') if workflow.createtime else '',
            "updatetime": workflow.updatetime.strftime(
                                '%Y-%m-%d %H:%M:%S') if workflow.updatetime else '',
            "createuser": workflow.createuser.userinfo.fullname if workflow.createuser else "",
            "updateuser": workflow.updateuser.userinfo.fullname if workflow.updateuser else "",
            "shortname": workflow.shortname,
            "type": workflow.type,
            "owner": workflow.owner,
            "group": [x.id for x in workflow.group.all()] ,
            "icon": workflow.icon,
            "version": workflow.version,
            "remark": workflow.remark,
            "sort": workflow.sort,
        }

    return JsonResponse({
        "status": status,
        "data": data,
        "info": info
    })


@login_required
def workflow_move(request):
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
    old_workflow_parent = TSDRMWorkflow.objects.get(id=old_parent)
    old_sort = old_position + 1
    old_workflows = TSDRMWorkflow.objects.exclude(state="9").filter(pnode=old_workflow_parent).filter(sort__gt=old_sort)

    # 目标节点下方(包括该节点) 所有节点 sort += 1
    workflow_parent = TSDRMWorkflow.objects.get(id=parent)
    sort = position + 1
    workflows = TSDRMWorkflow.objects.exclude(state=9).exclude(id=id).filter(pnode=workflow_parent).filter(sort__gte=sort)

    my_workflow = TSDRMWorkflow.objects.get(id=id)

    # 判断目标父节点是否为叶子，若为叶子无法挪动
    if workflow_parent.type != "NODE":
        return HttpResponse("流程")
    else:
        # 目标父节点下所有节点 除了自身 流程名称都不得相同 否则重名
        workflow_same = TSDRMWorkflow.objects.exclude(state="9").exclude(id=id).filter(pnode=workflow_parent).filter(
            shortname=my_workflow.shortname)

        if workflow_same:
            return HttpResponse("重名")
        else:
            for old_workflow in old_workflows:
                try:
                    old_workflow.sort -= 1
                    old_workflow.save()
                except:
                    pass
            for workflow in workflows:
                try:
                    workflow.sort += 1
                    workflow.save()
                except:
                    pass

            # 该节点位置变动
            try:
                my_workflow.pnode = workflow_parent
                my_workflow.sort = sort
                my_workflow.save()
                my_workflow.longname = getLongname(my_workflow)
                my_workflow.save()
            except:
                pass

            # 起始 结束 点不在同一节点下 写入父节点名称与ID ?
            if parent != old_parent:
                return HttpResponse(workflow_parent.shortname + "^" + str(workflow_parent.id))
            else:
                return HttpResponse("0")


@login_required
def workflow_save(request):
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
    owner = request.POST.get('owner', '')
    group = request.POST.getlist('group', [])
    icon = request.POST.get('icon', '')
    version = request.POST.get('version', '')
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
                        max_sort = TSDRMWorkflow.objects.exclude(state="9").filter(pnode_id=pid).aggregate(
                            max_sort=Max('sort', distinct=True))["max_sort"]
                        sort = max_sort + 1
                    except:
                        pass
                    workflowsave = TSDRMWorkflow()
                    workflowsave.shortname = node_name
                    workflowsave.sort = sort if sort else None
                    workflowsave.remark = node_remark
                    workflowsave.type = "NODE"
                    workflowsave.pnode_id = pid

                    workflowsave.createtime = datetime.datetime.now()
                    workflowsave.updatetime = datetime.datetime.now()
                    workflowsave.createuser = request.user
                    workflowsave.updateuser = request.user
                    workflowsave.save()
                    workflowsave.longname = getLongname(workflowsave)
                    workflowsave.save()

                    select_id = workflowsave.id
                except Exception as e:
                    info = "保存失败：{0}".format(e)
                    status = 0
            else:
                # 修改
                try:
                    workflowsave = TSDRMWorkflow.objects.get(id=id)
                    workflowsave.name = node_name
                    workflowsave.remark = node_remark
                    workflowsave.updatetime = datetime.datetime.now()
                    workflowsave.updateuser = request.user
                    workflowsave.save()
                    workflowsave.longname = getLongname(workflowsave)
                    workflowsave.save()

                    select_id = workflowsave.id
                except Exception as e:
                    info = "保存失败：{0}".format(e)
                    status = 0
    else:
        allgroup = Group.objects.exclude(state="9")
        if shortname.strip() == '':
            info = '短名称不能为空。'
            status = 0
        elif owner.strip() == '':
            info = '用户级别不能为空。'
            status = 0
        else:
            if id == 0:
                try:
                    sort = 1
                    try:
                        max_sort = TSDRMWorkflow.objects.exclude(state="9").filter(pnode_id=pid).aggregate(
                            max_sort=Max('sort', distinct=True))["max_sort"]
                        sort = max_sort + 1
                    except:
                        pass
                    workflowsave = TSDRMWorkflow()
                    workflowsave.guid = uuid.uuid1()
                    workflowsave.shortname = shortname
                    workflowsave.owner = owner
                    workflowsave.icon = icon
                    workflowsave.version = version
                    workflowsave.sort = sort if sort else None
                    workflowsave.remark = remark
                    workflowsave.type = "LEAF"
                    workflowsave.pnode_id = pid

                    workflowsave.createtime = datetime.datetime.now()
                    workflowsave.updatetime = datetime.datetime.now()
                    workflowsave.createuser = request.user
                    workflowsave.updateuser = request.user
                    workflowsave.save()
                    workflowsave.longname = getLongname(workflowsave)
                    workflowsave.save()
                    workflowsave.group.clear()
                    for groupid in group:
                        try:
                            groupid = int(groupid)
                            mygroup = allgroup.get(id=groupid)
                            workflowsave.group.add(mygroup)
                        except ValueError:
                            raise Http404()

                    select_id = workflowsave.id
                    createtime = workflowsave.createtime.strftime(
                                '%Y-%m-%d %H:%M:%S') if workflowsave.createtime else '',
                    updatetime = workflowsave.updatetime.strftime(
                                '%Y-%m-%d %H:%M:%S') if workflowsave.updatetime else '',
                    createuser = request.user.userinfo.fullname
                    updateuser = request.user.userinfo.fullname
                except Exception as e:
                    info = "保存失败：{0}".format(e)
                    status = 0
            else:
                try:
                    workflowsave = TSDRMWorkflow.objects.get(id=id)
                    workflowsave.shortname = shortname
                    workflowsave.owner = owner
                    workflowsave.icon = icon
                    workflowsave.version = version
                    workflowsave.remark = remark

                    workflowsave.updatetime = datetime.datetime.now()
                    workflowsave.updateuser = request.user
                    workflowsave.save()
                    workflowsave.longname = getLongname(workflowsave)
                    workflowsave.save()
                    workflowsave.group.clear()
                    for groupid in group:
                        try:
                            groupid = int(groupid)
                            mygroup = allgroup.get(id=groupid)
                            workflowsave.group.add(mygroup)
                        except ValueError:
                            raise Http404()

                    select_id = workflowsave.id
                    updatetime = workflowsave.updatetime.strftime(
                        '%Y-%m-%d %H:%M:%S') if workflowsave.updatetime else '',
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
    })


@login_required
def workflow_del(request):
    if 'id' in request.POST:
        id = request.POST.get('id', '')
        try:
            id = int(id)
        except:
            raise Http404()
        workflow = TSDRMWorkflow.objects.get(id=id)
        workflow.state = "9"
        workflow.save()

        return HttpResponse(1)
    else:
        return HttpResponse(0)

@login_required
def workflow(request,offset, funid):
    grouplist = Group.objects.all().exclude(state='9')
    return render(request, 'workflow.html',
                  {'username': request.user.userinfo.fullname, "pagefuns": getpagefuns(funid, request=request),"workflowid":offset,"grouplist": grouplist})


@login_required
def workflow_getdata(request):
    id = request.POST.get('id', '')
    try:
        id = int(id)
    except:
        pass
    workflowData={}
    status=1

    workflow = TSDRMWorkflow.objects.exclude(state="9").filter(id=id,type="LEAF")
    if len(workflow) > 0:
        #控件模型
        controlDate=[]
        controlList = TSDRMControl.objects.exclude(state="9").filter(type='LEAF').order_by("sort")
        for control in controlList:
            input=[]
            if control.input and len(control.input.strip()) > 0:
                tmpInput = xmltodict.parse(control.input)
                if "inputs" in tmpInput and "input" in tmpInput["inputs"]:
                    tmpDTL = tmpInput["inputs"]["input"]
                    if str(type(tmpDTL)) == "<class 'collections.OrderedDict'>":
                        tmpDTL = [tmpDTL]
                    for curinput in tmpDTL:
                        if curinput["source"]=="input":
                            input.append({"code":curinput["code"],"name":curinput["name"],"type":curinput["type"],"remark":curinput["remark"],"source":"","value":""})
            output=[]
            if control.output and len(control.output.strip()) > 0:
                tmpOutput = xmltodict.parse(control.output)
                if "outputs" in tmpOutput and "output" in tmpOutput["outputs"]:
                    tmpDTL = tmpOutput["outputs"]["output"]
                    if str(type(tmpDTL)) == "<class 'collections.OrderedDict'>":
                        tmpDTL = [tmpDTL]
                    for curoutput in tmpDTL:
                        output.append(
                            {"code": curoutput["code"], "name": curoutput["name"], "type": curoutput["type"],"remark":curoutput["remark"], "to": "",
                             "totype": ""})

            controlDate.append({"category": control.controlclass, "modeltype": "CONTROL", "modelguid": control.guid, "modelname": control.shortname,
             "text": control.shortname, "geo": control.icon, "color": "#2a6dc0", "input": json.dumps(input), "output": json.dumps(output)})
        workflowData["controlDate"]=controlDate

        # 组件模型
        componentDate = []
        componentList = TSDRMComponent.objects.exclude(state="9").filter(type='LEAF').order_by("sort")
        for component in componentList:
            input=[]
            if component.input and len(component.input.strip()) > 0:
                tmpInput = xmltodict.parse(component.input)
                if "inputs" in tmpInput and "input" in tmpInput["inputs"]:
                    tmpDTL = tmpInput["inputs"]["input"]
                    if str(type(tmpDTL)) == "<class 'collections.OrderedDict'>":
                        tmpDTL = [tmpDTL]
                    for curinput in tmpDTL:
                        if curinput["source"]=="input":
                            input.append({"code":curinput["code"],"name":curinput["name"],"type":curinput["type"],"remark":curinput["remark"],"source":"","value":""})
            output=[]
            if component.output and len(component.output.strip()) > 0:
                tmpOutput = xmltodict.parse(component.output)
                if "outputs" in tmpOutput and "output" in tmpOutput["outputs"]:
                    tmpDTL = tmpOutput["outputs"]["output"]
                    if str(type(tmpDTL)) == "<class 'collections.OrderedDict'>":
                        tmpDTL = [tmpDTL]
                    for curoutput in tmpDTL:
                        output.append(
                            {"code": curoutput["code"], "name": curoutput["name"], "type": curoutput["type"],"remark":curoutput["remark"], "to": "",
                             "totype": ""})
            componentDate.append(
                {"category": "component", "modeltype": "COMPONENT", "modelguid": component.guid, "modelname": component.shortname,
                 "text": component.shortname, "geo": component.icon, "color": "#2a6dc0", "input": json.dumps(input), "output": json.dumps(output)})
        workflowData["componentDate"] = componentDate

        # 子流程模型
        subworkflowDate = []
        subworkflowList = TSDRMWorkflow.objects.exclude(state="9").exclude(id=id).filter(type='LEAF').order_by("sort")
        for subworkflow in subworkflowList:
            input = []
            if subworkflow.input and len(subworkflow.input.strip()) > 0:
                tmpInput = xmltodict.parse(subworkflow.input)
                if "inputs" in tmpInput and "input" in tmpInput["inputs"]:
                    tmpDTL = tmpInput["inputs"]["input"]
                    if str(type(tmpDTL)) == "<class 'collections.OrderedDict'>":
                        tmpDTL = [tmpDTL]
                    for curinput in tmpDTL:
                        if curinput["source"] == "input":
                            input.append(
                                {"code": curinput["code"], "name": curinput["name"], "type": curinput["type"],"remark":curinput["remark"], "source": "",
                                 "value": ""})
            output = []
            if subworkflow.output and len(subworkflow.output.strip()) > 0:
                tmpOutput = xmltodict.parse(subworkflow.output)
                if "outputs" in tmpOutput and "output" in tmpOutput["outputs"]:
                    tmpDTL = tmpOutput["outputs"]["output"]
                    if str(type(tmpDTL)) == "<class 'collections.OrderedDict'>":
                        tmpDTL = [tmpDTL]
                    for curoutput in tmpDTL:
                        output.append(
                            {"code": curoutput["code"], "name": curoutput["name"], "type": curoutput["type"], "remark":curoutput["remark"], "to": "",
                             "totype": ""})
            subworkflowDate.append(
                {"category": "subworkflow", "modeltype": "WORKFLOW", "modelguid": subworkflow.guid,
                 "modelname": subworkflow.shortname,
                 "text": subworkflow.shortname, "geo": subworkflow.icon, "color": "#2a6dc0", "input": json.dumps(input), "output": json.dumps(output)})
        workflowData["subworkflowDate"] = subworkflowDate

        # 流程数据
        curworkflow={}

        baseinfo={}
        content = {"class": "GraphLinksModel","linkFromPortIdProperty": "fromPort","linkToPortIdProperty": "toPort"}

        if len(workflow)>0:
            # 流程基础信息
            workflow = workflow[0]
            input = []
            if workflow.input and len(workflow.input.strip()) > 0:
                tmpInput = xmltodict.parse(workflow.input)
                if "inputs" in tmpInput and "input" in tmpInput["inputs"]:
                    tmpDTL = tmpInput["inputs"]["input"]
                    if str(type(tmpDTL)) == "<class 'collections.OrderedDict'>":
                        tmpDTL = [tmpDTL]
                    input = tmpDTL
            output = []
            if workflow.output and len(workflow.output.strip()) > 0:
                tmpOutput = xmltodict.parse(workflow.output)
                if "outputs" in tmpOutput and "output" in tmpOutput["outputs"]:
                    tmpDTL = tmpOutput["outputs"]["output"]
                    if str(type(tmpDTL)) == "<class 'collections.OrderedDict'>":
                        tmpDTL = [tmpDTL]
                    output = tmpDTL
            variable = []
            if workflow.variable and len(workflow.variable.strip()) > 0:
                tmpVariable = xmltodict.parse(workflow.variable)
                if "variables" in tmpVariable and tmpVariable["variables"] and "variable" in tmpVariable["variables"]:
                    tmpDTL = tmpVariable["variables"]["variable"]
                    if str(type(tmpDTL)) == "<class 'collections.OrderedDict'>":
                        tmpDTL = [tmpDTL]
                    variable = tmpDTL
            baseinfo = {
                "pnode": workflow.pnode.shortname if workflow.pnode else "",
                "id": workflow.id,
                "guid": workflow.guid,
                "createtime": workflow.createtime.strftime(
                    '%Y-%m-%d %H:%M:%S') if workflow.createtime else '',
                "updatetime": workflow.updatetime.strftime(
                    '%Y-%m-%d %H:%M:%S') if workflow.updatetime else '',
                "createuser": workflow.createuser.userinfo.fullname if workflow.createuser else "",
                "updateuser": workflow.updateuser.userinfo.fullname if workflow.updateuser else "",
                "shortname": workflow.shortname,
                "type": workflow.type,
                "owner": workflow.owner,
                "group": json.dumps([x.id for x in workflow.group.all()]),
                "icon": workflow.icon,
                "version": workflow.version,
                "remark": workflow.remark,
                "input": json.dumps(input),
                "variable": json.dumps(variable),
                "output": json.dumps(output)
            }

            # 流程步骤内容
            nodelist=[]
            linklist = []
            if workflow.content and len(workflow.content.strip()) > 0:
                tmpStep = xmltodict.parse(workflow.content)
                if "tsdrmworkflow" in tmpStep and "steps" in tmpStep["tsdrmworkflow"] and "step" in tmpStep["tsdrmworkflow"]["steps"]:
                    tmpDTL = tmpStep["tsdrmworkflow"]["steps"]["step"]
                    if str(type(tmpDTL)) == "<class 'collections.OrderedDict'>":
                        tmpDTL = [tmpDTL]
                    for curstep in tmpDTL:
                        # 步骤
                        step_modeltype = curstep["baseInfo"]["modelType"]
                        step_guid = curstep["baseInfo"]["modelguid"]
                        stepObject = None
                        if step_modeltype=="CONTROL":
                            stepObject = TSDRMControl.objects.filter(guid=step_guid)
                        elif  step_modeltype=="COMPONENT":
                            stepObject = TSDRMComponent.objects.filter(guid=step_guid)
                        elif step_modeltype == "WORKFLOW":
                            stepObject = TSDRMWorkflow.objects.filter(guid=step_guid)
                        if len(stepObject)>0:
                            stepObject = stepObject[0]
                            stepinput = []
                            stepoutput = []
                            if "inputs" in curstep and curstep["inputs"] and "input" in curstep["inputs"]:
                                tmpDTL = curstep["inputs"]["input"]
                                if str(type(tmpDTL)) == "<class 'collections.OrderedDict'>":
                                    tmpDTL = [tmpDTL]
                                stepinput = tmpDTL
                            if "outputs" in curstep and curstep["outputs"] and "output" in curstep["outputs"]:
                                tmpDTL = curstep["outputs"]["output"]
                                if str(type(tmpDTL)) == "<class 'collections.OrderedDict'>":
                                    tmpDTL = [tmpDTL]
                                stepoutput = tmpDTL

                            input = []
                            if stepObject.input and len(stepObject.input.strip()) > 0:
                                tmpInput = xmltodict.parse(stepObject.input)
                                if "inputs" in tmpInput and "input" in tmpInput["inputs"]:
                                    tmpDTL = tmpInput["inputs"]["input"]
                                    if str(type(tmpDTL)) == "<class 'collections.OrderedDict'>":
                                        tmpDTL = [tmpDTL]
                                    for curinput in tmpDTL:
                                        if curinput["source"] == "input":
                                            cursource=""
                                            curvalue=""
                                            for curstepinput in stepinput:
                                                if curstepinput["code"]==curinput["code"]:
                                                    cursource=curstepinput["source"]
                                                    curvalue = curstepinput["value"]
                                                    # #if stepObject.guid=="c2d3f2b6-49a9-11eb-99aa-84fdd1a17907" and curstepinput["code"]=="criteria":
                                                    #     curvalue= json.loads(curstepinput["value"])
                                                    break
                                            input.append({"code": curinput["code"], "name": curinput["name"],
                                                          "type": curinput["type"],"remark":curinput["remark"], "source": cursource, "value": curvalue})
                            output = []
                            if stepObject.output and len(stepObject.output.strip()) > 0:
                                tmpOutput = xmltodict.parse(stepObject.output)
                                if "outputs" in tmpOutput and "output" in tmpOutput["outputs"]:
                                    tmpDTL = tmpOutput["outputs"]["output"]
                                    if str(type(tmpDTL)) == "<class 'collections.OrderedDict'>":
                                        tmpDTL = [tmpDTL]
                                    for curoutput in tmpDTL:
                                        curto = ""
                                        curtotype = ""
                                        for curstepoutput in stepoutput:
                                            if curstepoutput["code"] == curoutput["code"]:
                                                curto = curstepoutput["to"]
                                                curtotype = curstepoutput["type"]
                                                break
                                        output.append(
                                            {"code": curoutput["code"], "name": curoutput["name"],
                                             "type": curoutput["type"],"remark":curoutput["remark"], "to": curto,
                                             "totype": curtotype})

                            category = ""
                            if step_modeltype == "CONTROL":
                                category = stepObject.controlclass
                            elif step_modeltype == "COMPONENT":
                                category = "component"
                            elif step_modeltype == "WORKFLOW":
                                category = "subworkflow"
                            nodelist.append({"category": category, "modeltype": step_modeltype, "modelguid": step_guid,
                             "modelname": stepObject.shortname, "text": curstep["baseInfo"]["name"], "geo": stepObject.icon, "color": "#2a6dc0", "key":  curstep["baseInfo"]["stepid"],
                             "loc": curstep["baseInfo"]["loc"],"input": json.dumps(input), "output": json.dumps(output)})

                        # 线条
                        if "lines" in curstep and curstep["lines"] and "line" in curstep["lines"]:
                            tmpDTL = curstep["lines"]["line"]
                            if str(type(tmpDTL)) == "<class 'collections.OrderedDict'>":
                                tmpDTL = [tmpDTL]
                            for line in tmpDTL:
                                points=[]
                                if line["visible"]["points"] and "point" in line["visible"]["points"]:
                                    points=line["visible"]["points"]["point"]
                                if str(type(points)) == "<class 'collections.OrderedDict'>":
                                    points = [points]
                                for i in range(len(points)):
                                    try:
                                        points[i] = float(points[i])
                                    except:
                                        pass
                                visible = line["visible"]["visible"]
                                if visible=="true":
                                    visible=True
                                else:
                                    visible = False
                                linklist.append(
                                    {"from": curstep["baseInfo"]["stepid"], "to": line["nextPoint"],
                                     "criteria": line["criteria"],"text": line["text"],
                                     "fromPort": line["visible"]["fromPort"], "toPort": line["visible"]["toPort"],
                                     "visible": visible,"points": points})
            content["nodeDataArray"]=nodelist
            content["linkDataArray"] = linklist

        content["modelData"] = baseinfo
        curworkflow["content"] = content

        workflowData["curworkflow"] = curworkflow

    else:
        status = 0
    return JsonResponse({
        "workflowData":workflowData,
        "status": status,
    })


@login_required
def workflow_draw_save(request):
    status = 1
    info = "保存成功。"

    content = request.POST.get('content', '')
    if len(content.strip()) <= 0:
        status = 0
        info = "保存失败，流程不存在！"
    else:
        content=json.loads(content)
        baseinfo=content["modelData"]
        id = baseinfo["id"]
        try:
            id=int(id)
        except:
            status = 0
            info="保存失败，流程不存在！"
            return JsonResponse({
                "status": status,
                "info": info,
            })
        workflow = TSDRMWorkflow.objects.exclude(state="9").filter(id=id, type="LEAF")
        if len(workflow) <= 0:
            status = 0
            info = "保存失败，流程不存在！"
        else:
            shortname = baseinfo["shortname"]
            owner = baseinfo["owner"]
            group = json.loads(baseinfo["group"])
            icon = baseinfo["icon"]
            version = baseinfo["version"]
            remark = baseinfo["remark"]
            input = json.loads(baseinfo["input"])
            output = json.loads(baseinfo["output"])
            variable = json.loads(baseinfo["variable"])

            workflowsave=workflow[0]
            if shortname.strip() == '':
                info = '短名称不能为空。'
                status = 0
            elif owner.strip() == '':
                info = '用户级别不能为空。'
                status = 0
            else:

                workflowsave.shortname = shortname
                workflowsave.owner = owner
                workflowsave.icon = icon
                workflowsave.version = version
                workflowsave.remark = remark
                workflowsave.input = xmltodict.unparse({"inputs": {"input": input}}, encoding='utf-8')
                workflowsave.output = xmltodict.unparse({"outputs": {"output": output}}, encoding='utf-8')
                workflowsave.variable = xmltodict.unparse({"variables": {"variable": variable}}, encoding='utf-8')

                root = etree.Element("tsdrmworkflow")
                etree.SubElement(root, "visible")
                xmlnode_steps = etree.SubElement(root, "steps")
                if content["nodeDataArray"]:
                    for step in content["nodeDataArray"]:
                        xmlnode_step = etree.SubElement(xmlnode_steps, "step")
                        xmlnode_step_baseInfo = etree.SubElement(xmlnode_step, "baseInfo")
                        xmlnode_step_stepid = etree.SubElement(xmlnode_step_baseInfo, "stepid")
                        xmlnode_step_stepid.text = str(step["key"])
                        xmlnode_step_modelguid = etree.SubElement(xmlnode_step_baseInfo, "modelguid")
                        xmlnode_step_modelguid.text = step["modelguid"]
                        xmlnode_step_name = etree.SubElement(xmlnode_step_baseInfo, "name")
                        xmlnode_step_name.text = step["text"]
                        xmlnode_step_modelType = etree.SubElement(xmlnode_step_baseInfo, "modelType")
                        xmlnode_step_modelType.text = step["modeltype"]
                        xmlnode_step_loc = etree.SubElement(xmlnode_step_baseInfo, "loc")
                        xmlnode_step_loc.text = step["loc"]
                        xmlnode_step_inputs = etree.SubElement(xmlnode_step, "inputs")
                        step["input"] = json.loads(step["input"])
                        if "input" in step and step["input"]:
                            for input in step["input"]:
                                xmlnode_step_input = etree.SubElement(xmlnode_step_inputs, "input")
                                xmlnode_step_input_code = etree.SubElement(xmlnode_step_input, "code")
                                xmlnode_step_input_code.text = input["code"]
                                xmlnode_step_input_source = etree.SubElement(xmlnode_step_input, "source")
                                xmlnode_step_input_source.text = input["source"]
                                xmlnode_step_input_value = etree.SubElement(xmlnode_step_input, "value")
                                inputvalue=input["value"]
                                # #if step["modelguid"]=="c2d3f2b6-49a9-11eb-99aa-84fdd1a17907" and input["code"]=="criteria":
                                #     inputvalue = json.dumps(inputvalue)
                                xmlnode_step_input_value.text = inputvalue
                        xmlnode_step_outputs = etree.SubElement(xmlnode_step, "outputs")
                        step["output"] = json.loads(step["output"])
                        if "output" in step and step["output"]:
                            for output in step["output"]:
                                xmlnode_step_output = etree.SubElement(xmlnode_step_outputs, "output")
                                xmlnode_step_output_code = etree.SubElement(xmlnode_step_output, "code")
                                xmlnode_step_output_code.text = output["code"]
                                xmlnode_step_output_to = etree.SubElement(xmlnode_step_output, "to")
                                xmlnode_step_output_to.text = output["to"]
                                xmlnode_step_output_type = etree.SubElement(xmlnode_step_output, "type")
                                xmlnode_step_output_type.text = output["totype"]
                        if content["linkDataArray"]:
                            xmlnode_step_lines = etree.SubElement(xmlnode_step, "lines")
                            for link in content["linkDataArray"]:
                                if link["from"] == step["key"]:
                                    xmlnode_step_line = etree.SubElement(xmlnode_step_lines, "line")
                                    xmlnode_step_line_text = etree.SubElement(xmlnode_step_line, "text")
                                    if "text" in link:
                                        xmlnode_step_line_text.text = link["text"]
                                    xmlnode_step_line_nextPoint = etree.SubElement(xmlnode_step_line, "nextPoint")
                                    xmlnode_step_line_nextPoint.text = str(link["to"])
                                    xmlnode_step_line_criteria = etree.SubElement(xmlnode_step_line, "criteria")
                                    if "criteria" in link:
                                        xmlnode_step_line_criteria.text = link["criteria"]
                                    xmlnode_step_line_visible = etree.SubElement(xmlnode_step_line, "visible")
                                    xmlnode_step_line_visible_fromPort = etree.SubElement(xmlnode_step_line_visible, "fromPort")
                                    xmlnode_step_line_visible_fromPort.text = link["fromPort"]
                                    xmlnode_step_line_visible_toPort = etree.SubElement(xmlnode_step_line_visible,
                                                                                          "toPort")
                                    xmlnode_step_line_visible_toPort.text = link["toPort"]
                                    xmlnode_step_line_visible_visible = etree.SubElement(xmlnode_step_line_visible,
                                                                                        "visible")
                                    linkvisible="false"
                                    if  "visible" in link and link["visible"]==True:
                                        linkvisible="true"
                                    xmlnode_step_line_visible_visible.text = linkvisible
                                    xmlnode_step_line_visible_points = etree.SubElement(xmlnode_step_line_visible, "points")
                                    if "points" in link and  link["points"]:
                                        for point in link["points"]:
                                            xmlnode_step_line_visible_points_point = etree.SubElement(
                                                xmlnode_step_line_visible_points,
                                                "point")
                                            xmlnode_step_line_visible_points_point.text = str(point)



                xml_config = etree.tounicode(root)
                workflowsave.content=xml_config

                workflowsave.updatetime = datetime.datetime.now()
                workflowsave.updateuser = request.user
                workflowsave.save()
                workflowsave.longname = getLongname(workflowsave)
                workflowsave.save()
                workflowsave.group.clear()
                allgroup = Group.objects.exclude(state="9")
                for groupid in group:
                    try:
                        groupid = int(groupid)
                        mygroup = allgroup.get(id=groupid)
                        workflowsave.group.add(mygroup)
                    except ValueError:
                        pass

    return JsonResponse({
        "status": status,
        "info": info,
    })


def getLongname(node):
    if node.pnode is None:
        return node.shortname
    else:
        return getLongname(node.pnode) + "-" + node.shortname
