# 客户端管理
from django.db.models import Max
from django.http import HttpResponse
from django.shortcuts import render
from djcelery.views import JsonResponse
from .basic_views import getpagefuns
from django.contrib.auth.decorators import login_required
from ..models import *
from ..workflow.workflow import Job
from lxml import etree
import json


######################
# 客户端管理
######################

@login_required
def hosts_manage(request, funid):
    return render(request, 'hosts_manage.html',
                  {'username': request.user.userinfo.fullname,
                   "pagefuns": getpagefuns(funid, request=request),
                   "is_superuser": request.user.is_superuser
                   })


@login_required
def get_hosts_tree_by_business(request):
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
            "pname": "无",
            "edit": False
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
        root["children"] = get_hosts_node_by_business(root_node, select_id, request)
        tree_data.append(root)
    return JsonResponse({
        "ret": 1,
        "data": tree_data
    })



def get_hosts_node_by_business(parent, select_id, request):
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
        edit=True
        if child.id in [1, 2, 3]:
            edit=False
        node["data"] = {
            "name": child.host_name,
            "remark": child.remark,
            "pname": parent.host_name,
            "edit": edit
        }

        node["children"] = get_hosts_node_by_business(child, select_id, request)
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
def hosts_del(request):
    if 'id' in request.POST:
        id = request.POST.get('id', '')

        component_guid = '4348a146-9cdb-11eb-9ef2-84fdd1a17907'
        component_input = [{"code": "id", "value": id}]
        newJob = Job(userid=request.user.id)
        state = newJob.execute_workflow(component_guid, input=component_input)

        if state == 'NOTEXIST':
            return HttpResponse(0)
        elif state == 'ERROR':
            return HttpResponse(0)
        else:
            return HttpResponse(1)
    else:
        return HttpResponse(0)


@login_required
def hosts_move(request):
    id = request.POST.get('id', '')
    parent = request.POST.get('parent', '')
    old_parent = request.POST.get('old_parent', '')
    position = request.POST.get('position', '')

    ret = 0
    info = "未知错误。"
    data=None

    try:
        id = int(id)  # 节点 id
        parent = int(parent)  # 目标位置父节点 pnode_id
        position = int(position)  # 目标位置
        old_parent = int(old_parent)  # 起点位置父节点 pnode_id
    except:
        return JsonResponse({
            "ret": ret,
            "info": info,
            "data": data
        })

    component_guid = 'f188cf66-9cd4-11eb-901a-84fdd1a17907'
    component_input = [{"code": "id", "value": id},
                       {"code": "newParent", "value": parent},
                       {"code": "newPosition", "value": position}]
    newJob = Job(userid=request.user.id)
    state = newJob.execute_workflow(component_guid, input=component_input)
    if state == 'NOTEXIST':
        ret = 0
        info = "组件不存在，请于管理员联系。。"
    elif state == 'ERROR':
        ret = 0
        info = newJob.jobBaseInfo["log"]
    else:
        ret = 1
        if parent != old_parent:
            new_client_parent = HostsManage.objects.get(id=parent)
            data = new_client_parent.host_name + "^" + str(new_client_parent.id)
    return JsonResponse({
        "ret": ret,
        "info": info,
        "data": data
    })


@login_required
def hosts_node_save(request):
    id = request.POST.get("id", "")
    pid = request.POST.get("pid", "")
    node_name = request.POST.get("node_name", "")
    node_remark = request.POST.get("node_remark", "")
    ret = 0
    info = "未知错误"
    try:
        id = int(id)
    except:
        ret = 0
        info = "网络错误。"
    else:
        if id == 0:
            component_guid = 'f108ffb8-9cc4-11eb-87b4-84fdd1a17907'
            component_input = [{"code": "pid", "value": pid},
                                  {"code": "name", "value": node_name},
                                  {"code": "remark", "value": node_remark}]
            newJob = Job(userid=request.user.id)
            state = newJob.execute_workflow(component_guid, input=component_input)
            if state == 'NOTEXIST':
                ret = 0
                info = "组件不存在，请于管理员联系。。"
            elif state == 'ERROR':
                ret = 0
                info = newJob.jobBaseInfo["log"]
            else:
                ret = 1
                info = "新增节点成功。"
                for i in newJob.finalOutput:
                    if i['code'] == 'id':
                        id = i['value']
        else:
            # 修改
            component_guid = '0f1a9734-9cca-11eb-979e-84fdd1a17907'
            component_input = [{"code": "id", "value": id},
                               {"code": "name", "value": node_name},
                               {"code": "remark", "value": node_remark}]
            newJob = Job(userid=request.user.id)
            state = newJob.execute_workflow(component_guid, input=component_input)
            if state == 'NOTEXIST':
                ret = 0
                info = "组件不存在，请于管理员联系。。"
            elif state == 'ERROR':
                ret = 0
                info = newJob.jobBaseInfo["log"]
            else:
                ret = 1
                info = "节点信息修改成功。"
    return JsonResponse({
        "ret": ret,
        "info": info,
        "nodeid": id
    })


@login_required
def hosts_get_client_detail(request):
    id = request.POST.get("id", "")
    ret = 0
    info = "位置错误"
    data = None

    component_guid = '65816810-9cf3-11eb-8792-84fdd1a17907'
    component_input = [{"code": "id", "value": id}]
    newJob = Job(userid=request.user.id)
    state = newJob.execute_workflow(component_guid, input=component_input)
    if state == 'NOTEXIST':
        ret = 0
        info = "组件不存在，请于管理员联系。。"
    elif state == 'ERROR':
        ret = 0
        info = newJob.jobBaseInfo["log"]
    else:
        for i in newJob.finalOutput:
            if i['code'] == 'data':
                data = i['value']
        try:
            data = json.loads(data)
            ret = 1
            info = "查询成功。"
        except:
            ret = 0
            info = "数据异常"
    return JsonResponse({
        "ret": ret,
        "info": info,
        "data": data
    })


@login_required
def hosts_client_save(request):
    id = request.POST.get("id", "")
    pid = request.POST.get("pid", "")
    host_ip = request.POST.get("host_ip", "")
    host_name = request.POST.get("host_name", "")
    host_type = request.POST.get("host_type", "")
    username = request.POST.get("username", "")
    password = request.POST.get("password", "")
    config = request.POST.get("config", "")
    remark = request.POST.get("remark", "")

    ret = 0
    info = "未知错误"
    try:
        id = int(id)
    except:
        ret = 0
        info = "网络错误。"
    else:
        if id == 0:
            component_guid = '66171ec0-a308-11eb-8ab1-84fdd1a17907'
            component_input = [{"code": "pid", "value": pid},
                               {"code": "ip", "value": host_ip},
                               {"code": "name", "value": host_name},
                               {"code": "type", "value": host_type},
                               {"code": "username", "value": username},
                               {"code": "password", "value": password},
                               {"code": "config", "value": config},
                               {"code": "remark", "value": remark}]

            newJob = Job(userid=request.user.id)
            state = newJob.execute_workflow(component_guid, input=component_input)
            if state == 'NOTEXIST':
                ret = 0
                info = "组件不存在，请于管理员联系。。"
            elif state == 'ERROR':
                ret = 0
                info = newJob.jobBaseInfo["log"]
            else:
                ret = 1
                info = "客户端节点成功。"
                for i in newJob.finalOutput:
                    if i['code'] == 'id':
                        id = i['value']
        else:
            # 修改
            component_guid = '56336f1e-a30b-11eb-8b2d-84fdd1a17907'
            component_input = [{"code": "id", "value": id},
                               {"code": "ip", "value": host_ip},
                               {"code": "name", "value": host_name},
                               {"code": "type", "value": host_type},
                               {"code": "username", "value": username},
                               {"code": "password", "value": password},
                               {"code": "config", "value": config},
                               {"code": "remark", "value": remark}]
            newJob = Job(userid=request.user.id)
            state = newJob.execute_workflow(component_guid, input=component_input)
            if state == 'NOTEXIST':
                ret = 0
                info = "组件不存在，请于管理员联系。。"
            elif state == 'ERROR':
                ret = 0
                info = newJob.jobBaseInfo["log"]
            else:
                ret = 1
                info = "节点信息修改成功。"
    return JsonResponse({
        "ret": ret,
        "info": info,
        "nodeid": id
    })


@login_required
def hosts_client_test(request):
    host_ip = request.POST.get("host_ip", "")

    ret = 0
    info = "未知错误"

    component_guid = 'cc37675a-a312-11eb-ac9a-84fdd1a17907'
    component_input = [{"code": "ip", "value": host_ip}]

    newJob = Job(userid=request.user.id)
    state = newJob.execute_workflow(component_guid, input=component_input)
    if state == 'NOTEXIST':
        ret = 0
        info = "组件不存在，请于管理员联系。。"
    elif state == 'ERROR':
        ret = 0
        info = newJob.jobBaseInfo["log"]
    else:
        result=False
        for i in newJob.finalOutput:
            if i['code'] == 'check_result':
                result = i['value']
                break
        if result:
            ret = 1
            info = "网络正常"
        else:
            ret = 0
            info = "连接失败"
            for i in newJob.finalOutput:
                if i['code'] == 'message':
                    info = i['value']
                    break

    return JsonResponse({
        "ret": ret,
        "info": info,
    })


@login_required
def hosts_client_refresh(request):
    id = request.POST.get("id", "")

    ret = 0
    info = "未知错误"

    data = None

    component_guid = '03b36776-a34d-11eb-bdae-84fdd1a17907'
    component_input = [{"code": "id", "value": id}]

    newJob = Job(userid=request.user.id)
    state = newJob.execute_workflow(component_guid, input=component_input)
    if state == 'NOTEXIST':
        ret = 0
        info = "组件不存在，请于管理员联系。。"
    elif state == 'ERROR':
        ret = 0
        info = newJob.jobBaseInfo["log"]
    else:
        for i in newJob.finalOutput:
            if i['code'] == 'data':
                data = i['value']

        ret = 1
        info = "刷新成功"

    return JsonResponse({
        "ret": ret,
        "info": info,
        "data": data
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
                    elif "SQL Server" in cvclient_agentType:
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
                            if cvclient_type in ("1", "3"):
                                config = custom_cv_params(**cv_params)
                                cvclient.info = config
                                if cvclient_destination != "self":
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
                            if cvclient_type in ("1", "3"):
                                config = custom_cv_params(**cv_params)
                                cvclient.info = config
                                if cvclient_destination == "self":
                                    cvclient.destination_id = cv_id
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
        result = dm.get_all_restore_job_list(cvclient.client_name, cvclient.agentType, cvclient.instanceName)
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
        processlist = Process.objects.filter(hosts_id=id, type='Commvault', processtype="1").exclude(state="9")
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
            'type': std.dbtype,
            'id': std.id,
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
        dbcopy_id = 0
    try:
        dbcopy_std = int(dbcopy_std)
    except:
        dbcopy_std = 0
    try:
        id = int(id)
    except:
        id = 0

    host_list = [dbcopy_id, dbcopy_std]

    adg_info_list = []
    adg_process_list = []
    for hostid in host_list:
        if hostid != 0:
            host = DbCopyClient.objects.filter(id=hostid).exclude(state="9")
            if len(host) > 0:
                host = host[0]
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
                        oracle_name = param_el[0].attrib.get("dbusername", ""),
                        oracle_name = oracle_name[0]
                        oracle_password = param_el[0].attrib.get("dbpassowrd", ""),
                        oracle_password = oracle_password[0]
                        oracle_instance = param_el[0].attrib.get("dbinstance", ""),
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
                    print(e)
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
        processlist = Process.objects.filter(primary=id, type='Oracle ADG', processtype="1").exclude(state="9")
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
    if type == 'ADG':
        type = 'Oracle ADG'

    processlist = Process.objects.filter(primary=id, type=type, processtype="1").exclude(state="9")
    for process in processlist:
        allprocess.append(process.id)
        frontprocess.append(process.id)
        if process.backprocess is not None:
            allprocess.append(process.backprocess.id)
            backprocess.append(process.backprocess.id)
    allprocess_new = [str(x) for x in allprocess]
    strprocess = ','.join(allprocess_new)
    if strprocess == "":
        strprocess = "0"

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
        process_type = ""
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
    dbcopy_mysql_std = json.loads(dbcopy_mysql_std)

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
                                                if len(dbcopy_mysql_std) > 0:
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
                                                if len(dbcopy_mysql_std) > 0:
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
        for num, hostid in enumerate(host_list):
            if hostid != 0:
                host = DbCopyClient.objects.filter(id=hostid).exclude(state="9")
                if len(host) > 0:
                    host = host[0]
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
                            dbusername = param_el[0].attrib.get("dbusername", ""),
                            dbusername = dbusername[0]
                            dbpassowrd = param_el[0].attrib.get("dbpassowrd", ""),
                            dbpassowrd = dbpassowrd[0]
                    except:
                        pass

                    try:
                        conn = pymysql.connect(host_ip, dbusername, dbpassowrd, "mysql")
                        curs = conn.cursor()
                        a_db_status_sql = 'show slave status;'
                        curs.execute(a_db_status_sql)
                        db_status_row = curs.fetchone()
                        master_host = db_status_row[1] if db_status_row else ""
                        io_state = db_status_row[10] if db_status_row else ""
                        sql_state = db_status_row[11] if db_status_row else ""
                    except Exception as e:
                        conn_status = 0
                    else:
                        curs.close()
                        conn.close()

                    mysql_info_list.append({
                        "num": num + 1,
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
                if host["master_host"] == master_host["host_ip"] or host["master_host"] == master_host["host_name"]:
                    host["masternum"] = master_host["num"]
                    break

    if id != 0:
        processlist = Process.objects.filter(primary=id, type='MYSQL', processtype="1").exclude(state="9")
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

