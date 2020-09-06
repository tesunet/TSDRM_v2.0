# 公用方法
import datetime
from ..models import *
from django.db import connection
from django.db.models import Q
import re
from django.http import HttpResponseRedirect, Http404, HttpResponse, JsonResponse
from lxml import etree
import base64
from ..api.commvault import SQLApi


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


def get_oracle_client(um):
    # 解析出账户信息
    _, sqlserver_credit = get_credit_info(um.content)

    #############################################
    # clientid, clientname, agent, instance, os #
    #############################################
    dm = SQLApi.CVApi(sqlserver_credit)

    oracle_data = dm.get_instance_from_oracle()

    # 获取包含oracle模块所有客户端
    installed_client = dm.get_all_install_clients()
    dm.close()
    oracle_client_list = []
    pre_od_name = ""
    for od in oracle_data:
        if "Oracle" in od["agent"]:
            if od["clientname"] == pre_od_name:
                continue
            client_id = od["clientid"]
            client_os = ""
            for ic in installed_client:
                if client_id == ic["client_id"]:
                    client_os = ic["os"]

            oracle_client_list.append({
                "clientid": od["clientid"],
                "clientname": od["clientname"],
                "agent": od["agent"],
                "instance": od["instance"],
                "os": client_os
            })
            # 去重
            pre_od_name = od["clientname"]
    return {
        'utils_manage': um.id,
        'oracle_client': oracle_client_list
    }


def get_params(config):
    """
    <root>
        <param param_name="1" variable_name="2" param_value="3"/>
        <param param_name="3" variable_name="4" param_value="5"/>
        <param param_name="5" variable_name="6" param_value="7"/>
    </root>
    """
    param_list = []
    pre_config = "<root></root>"
    if config:
        config = etree.XML(config)
    else:
        config = etree.XML(pre_config)
    param_nodes = config.xpath("//param")
    for pn in param_nodes:
        param_list.append({
            "param_name": pn.attrib.get("param_name", ""),
            "variable_name": pn.attrib.get("variable_name", ""),
            "param_value": pn.attrib.get("param_value", ""),
        })
    return param_list


def get_variable_name(content, param_type):
    variable_list = []
    com = ""
    if param_type == "HOST":
        com = re.compile("\(\((.*?)\)\)")
    if param_type == "PROCESS":
        com = re.compile("\{\{(.*?)\}\}")
    if param_type == "SCRIPT":
        com = re.compile("\[\[(.*?)\]\]")
    if com:
        variable_list = com.findall(content)
    return variable_list


def file_iterator(file_name, chunk_size=512):
    with open(file_name, "rb") as f:
        while True:
            c = f.read(chunk_size)
            if c:
                yield c
            else:
                break


def custom_time(time):
    """
    构造最新操作的时间
    :param time:
    :return:
    """
    time = time.replace(tzinfo=None)
    timenow = datetime.datetime.now()
    days = int((timenow - time).days)

    if days > 1095:
        time = "很久以前"
    else:
        if days > 730:
            time = "2年前"
        else:
            if days > 365:
                time = "1年前"
            else:
                if days > 182:
                    time = "半年前"
                else:
                    if days > 150:
                        time = "5月前"
                    else:
                        if days > 120:
                            time = "4月前"
                        else:
                            if days > 90:
                                time = "3月前"
                            else:
                                if days > 60:
                                    time = "2月前"
                                else:
                                    if days > 30:
                                        time = "1月前"
                                    else:
                                        if days >= 1:
                                            time = str(days) + "天前"
                                        else:
                                            hours = int((timenow - time).seconds / 3600)
                                            if hours >= 1:
                                                time = str(hours) + "小时"
                                            else:
                                                minutes = int((timenow - time).seconds / 60)
                                                if minutes >= 1:
                                                    time = str(minutes) + "分钟"
                                                else:
                                                    time = "刚刚"
    return time


def get_process_run_rto(processrun):
    delta_time = processrun.rto
    return delta_time


def get_fun_node(parent, selectid):
    nodes = []
    children = parent.children.order_by("sort").all()
    for child in children:
        node = {}
        node["text"] = child.name
        node["id"] = child.id
        node["type"] = child.type
        node["data"] = {"name": child.name, "pname": parent.name}
        node["children"] = get_fun_node(child, selectid)
        try:
            if int(selectid) == child.id:
                node["state"] = {"selected": True}
        except:
            pass
        nodes.append(node)
    return nodes


def get_org_node(parent, selectid, allgroup):
    nodes = []
    children = parent.children.order_by("sort").exclude(state="9").all()
    for child in children:
        node = {}
        node["text"] = child.fullname
        node["id"] = child.id
        node["type"] = child.type
        if child.type == "org":
            node["data"] = {
                "remark": child.remark, 
                "pname": parent.fullname,
                "name": child.fullname,
            }
        if child.type == "user":
            node["data"] = {
                "pname": parent.fullname,
                "name": child.fullname,
            }
        node["children"] = get_org_node(child, selectid, allgroup)
        try:
            if int(selectid) == child.id:
                node["state"] = {"selected": True}
        except:
            pass
        nodes.append(node)
    return nodes


def group_get_user_tree(parent, selectusers):
    nodes = []
    children = parent.children.order_by("sort").exclude(state="9").all()
    for child in children:
        node = {}
        node["text"] = child.fullname
        node["id"] = "user_" + str(child.id)
        node["type"] = child.type
        if child.type == "user" and child in selectusers:
            node["state"] = {"selected": True}
        node["children"] = group_get_user_tree(child, selectusers)
        nodes.append(node)
    return nodes


def group_get_fun_tree(parent, selectfuns):
    nodes = []
    children = parent.children.order_by("sort").all()
    for child in children:
        node = {}
        node["text"] = child.name
        node["id"] = "fun_" + str(child.id)
        node["type"] = child.type
        if child.type == "fun" and child in selectfuns:
            node["state"] = {"selected": True}
        node["children"] = group_get_fun_tree(child, selectfuns)
        nodes.append(node)
    return nodes


def custom_c_color(task_type, task_state, task_logtype):
    """
    构造图标与颜色
    :param task_type:
    :param task_state:
    :param task_logtype:
    :return: current_icon, current_color
    """
    if task_type == "ERROR":
        current_icon = "fa fa-exclamation-triangle"
        if task_state == "0":
            current_color = "label-danger"
        if task_state == "1":
            current_color = "label-default"
    elif task_type == "SIGN":
        current_icon = "fa fa-user"
        if task_state == "0":
            current_color = "label-warning"
        if task_state == "1":
            current_color = "label-info"
    elif task_type == "RUN":
        current_icon = "fa fa-bell-o"
        if task_state == "0":
            current_color = "label-warning"
        if task_state == "1":
            current_color = "label-info"
    else:
        current_color = "label-success"
        if task_logtype == "START":
            current_icon = "fa fa-power-off"
        elif task_logtype == "START":
            current_icon = "fa fa-power-off"
        elif task_logtype == "STEP":
            current_icon = "fa fa-cog"
        elif task_logtype == "SCRIPT":
            current_icon = "fa fa-cog"
        elif task_logtype == "STOP":
            current_icon = "fa fa-stop"
        elif task_logtype == "CONTINUE":
            current_icon = "fa fa-play"
        elif task_logtype == "IGNORE":
            current_icon = "fa fa-share"
        elif task_logtype == "START":
            current_icon = "fa fa-power-off"
        elif task_logtype == "END":
            current_icon = "fa fa-lock"
        else:
            current_icon = "fa fa-info-circle"
    return current_icon, current_color


def get_c_process_run_tasks(current_processrun_id):
    """
    获取当前系统任务
    :return:
    """
    # 当前系统任务
    current_process_task_info = []

    cursor = connection.cursor()
    cursor.execute("""
    select t.starttime, t.content, t.type, t.state, t.logtype from drm_processtask as t where t.processrun_id = '{0}' order by t.starttime desc;
    """.format(current_processrun_id))
    rows = cursor.fetchall()
    if len(rows) > 0:
        for task in rows:
            time = task[0]
            content = task[1]
            task_type = task[2]
            task_state = task[3]
            task_logtype = task[4]

            # 图标与颜色
            current_icon, current_color = custom_c_color(task_type, task_state, task_logtype)

            time = custom_time(time)

            current_process_task_info.append(
                {"content": content, "time": time, "task_color": current_color,
                 "task_icon": current_icon})
    return current_process_task_info


def get_contact_org_tree(parent, selectid):
    nodes = []
    children = parent.children.order_by("sort").exclude(state="9").all()
    for child in children:
        if child.type == "org":
            node = {}
            node["text"] = child.fullname
            node["id"] = child.id
            node["type"] = child.type

            node["children"] = get_contact_org_tree(child, selectid)
            try:
                if int(selectid) == child.id:
                    node["state"] = {"selected": True}
            except:
                pass
            nodes.append(node)
    return nodes


def get_child_contact(cur_contact_id, contact_list):
    child_contacts = UserInfo.objects.filter(pnode_id=cur_contact_id).exclude(state="9")

    for cur_contact in child_contacts:
        if cur_contact.type == "user":
            try:
                parent_contact_org = UserInfo.objects.get(id=cur_contact.id)
            except:
                pass
            else:
                if parent_contact_org.pnode:
                    depart = parent_contact_org.pnode.fullname
                else:
                    depart = ""

                contact_list.append({
                    "user_name": cur_contact.fullname,
                    "tel": cur_contact.phone,
                    "email": cur_contact.user.email,
                    "depart": depart,
                })
        else:
            get_child_contact(cur_contact.id, contact_list)


def get_step_tree(parent, selectid):
    nodes = []
    children = parent.children.exclude(state="9").order_by("sort").all()
    for child in children:
        node = {}
        node["text"] = child.name
        node["id"] = child.id
        node["children"] = get_step_tree(child, selectid)
        try:
            if int(selectid) == child.id:
                node["state"] = {"selected": True}
        except:
            pass
        nodes.append(node)
    return nodes


# 定义流程中脚本的方法
def process_script_save(save_data, cur_host_manage=None):
    result = {}

    if save_data["id"] == 0:
        allscript = Script.objects.filter(code=save_data["code"]).exclude(state="9").filter(
            step_id=save_data["pid"])
        if (len(allscript) > 0):
            result["res"] = '脚本编码:' + save_data["code"] + '已存在。'
        else:
            steplist = Step.objects.filter(
                process_id=save_data["processid"])
            if len(steplist) > 0:
                scriptsave = Script()
                scriptsave.code = save_data["code"]
                scriptsave.name = save_data["name"]
                scriptsave.sort = save_data["script_sort"]

                # 判断是否commvault/脚本
                if save_data["interface_type"] == "commvault":
                    scriptsave.hosts_manage_id = None
                    scriptsave.script_text = ""
                    scriptsave.succeedtext = ""
                    scriptsave.log_address = ""

                    scriptsave.origin_id = save_data["origin"]
                    scriptsave.commv_interface = save_data["commv_interface"]
                else:
                    scriptsave.hosts_manage_id = cur_host_manage.id
                    scriptsave.script_text = save_data["script_text"]
                    scriptsave.succeedtext = save_data["success_text"]
                    scriptsave.log_address = save_data["log_address"]

                    scriptsave.origin_id = None
                    scriptsave.commv_interface = ""

                scriptsave.step_id = save_data["pid"]
                scriptsave.interface_type = save_data["interface_type"]
                scriptsave.save()
                result["res"] = "新增成功。"

                ############################################################
                # result["data"] = [{"script_id": 1, "script_name": "2"}]  #
                # 当前脚本所在步骤的所有脚本按排序构造数组                   #
                ############################################################
                script_info_list = []
                cur_step = scriptsave.step
                all_scripts = cur_step.script_set.exclude(
                    state="9").order_by("sort")
                for script in all_scripts:
                    script_info_list.append({
                        "script_id": script.id,
                        "script_name": script.name
                    })
                result["data"] = script_info_list
    else:
        # 修改
        allscript = Script.objects.filter(code=save_data["code"]).exclude(id=save_data["id"]).exclude(
            state="9").filter(step_id=save_data["pid"])
        if (len(allscript) > 0):
            result["res"] = '脚本编码:' + save_data["code"] + '已存在。'
        else:
            try:
                scriptsave = Script.objects.get(id=save_data["id"])
                cur_script = Script.objects.exclude(state="9").exclude(id=save_data["id"]).filter(
                    code=save_data["code"])
                if cur_script:
                    result["res"] = '脚本编码:' + \
                                    save_data["code"] + '已存在，无法修改成该编码。'
                else:
                    scriptsave.code = save_data["code"]
                    scriptsave.name = save_data["name"]
                    scriptsave.sort = save_data["script_sort"]

                    # 判断是否commvault/脚本
                    if save_data["interface_type"] == "commvault":
                        scriptsave.hosts_manage_id = None
                        scriptsave.script_text = ""
                        scriptsave.succeedtext = ""
                        scriptsave.log_address = ""

                        scriptsave.origin_id = save_data["origin"]
                        scriptsave.commv_interface = save_data["commv_interface"]
                    else:
                        scriptsave.hosts_manage_id = cur_host_manage.id
                        scriptsave.script_text = save_data["script_text"]
                        scriptsave.succeedtext = save_data["success_text"]
                        scriptsave.log_address = save_data["log_address"]

                        scriptsave.origin_id = None
                        scriptsave.commv_interface = ""

                    scriptsave.interface_type = save_data["interface_type"]
                    scriptsave.save()
                    result["res"] = "修改成功。"

                    ############################################################
                    # result["data"] = [{"script_id": 1, "script_name": "2"}]  #
                    # 当前脚本所在步骤的所有脚本按排序构造数组                   #
                    ############################################################
                    script_info_list = []
                    cur_step = scriptsave.step
                    all_scripts = cur_step.script_set.exclude(
                        state="9").order_by("sort")
                    for script in all_scripts:
                        script_info_list.append({
                            "script_id": script.id,
                            "script_name": script.name
                        })
                    result["data"] = script_info_list

            except Exception as e:
                print("scriptsave edit error:%s" % e)
                result["res"] = "修改失败。"
    return result


def set_error_state(temp_request, process_run_id, task_content):
    current_process_runs = ProcessRun.objects.filter(id=process_run_id)
    if current_process_runs:
        current_process_run = current_process_runs[0]
        current_process_run.state = "ERROR"
        current_process_run.save()
        current_step_runs = current_process_run.steprun_set.filter(state="RUN")
        if len(current_step_runs) > 1:
            for current_step_run in current_step_runs:
                if current_step_run.step.pnode_id is not None:
                    current_step_run.state = "ERROR"
                    current_step_run.save()
                    current_script_runs = current_step_run.scriptrun_set.filter(state="RUN")
                    if current_script_runs:
                        current_script_run = current_script_runs[0]
                        current_script_run.state = "ERROR"
                        current_script_run.explain = task_content
                        current_script_run.save()
        myprocesstask = ProcessTask()
        myprocesstask.processrun_id = process_run_id
        myprocesstask.starttime = datetime.datetime.now()
        myprocesstask.senduser = temp_request.user.username
        myprocesstask.type = "INFO"
        myprocesstask.logtype = "ERROR"
        myprocesstask.state = "1"
        myprocesstask.content = task_content
        myprocesstask.save()
    else:
        pass


def getchildrensteps(processrun, curstep):
    childresult = []
    steplist = Step.objects.exclude(state="9").filter(
        pnode=curstep).order_by("sort")
    for step in steplist:
        runid = 0
        starttime = ""
        endtime = ""
        operator = ""
        parameter = ""
        runresult = ""
        explain = ""
        state = ""
        steprunlist = StepRun.objects.exclude(
            state="9").filter(processrun=processrun, step=step)
        if len(steprunlist) > 0:
            runid = steprunlist[0].id
            try:
                starttime = steprunlist[0].starttime.strftime(
                    "%Y-%m-%d %H:%M:%S")
            except:
                pass
            try:
                endtime = steprunlist[0].endtime.strftime("%Y-%m-%d %H:%M:%S")
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
                start_time = steprunlist[0].starttime.replace(
                    tzinfo=None) if steprunlist[0].starttime else ""
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
        scriptlist = ScriptInstance.objects.exclude(
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
                scriptrunlist = ScriptRun.objects.exclude(
                    state="9").filter(steprun=steprunlist[0], script=script)
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
            scripts.append({"id": script.id, "name": script.name, "runscriptid": runscriptid,
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
                verifyitemsrunlist = VerifyItemsRun.objects.exclude(state="9").filter(steprun=steprunlist[0],
                                                                                      verify_items=verifyitem)
                if len(verifyitemsrunlist) > 0:
                    runverifyitemid = verifyitemsrunlist[0].id
                    has_verified = verifyitemsrunlist[0].has_verified
                    verifyitemstate = verifyitemsrunlist[0].state
            verifyitems.append(
                {"id": verifyitem.id, "name": verifyitem.name, "runverifyitemid": runverifyitemid,
                 "has_verified": has_verified,
                 "verifyitemstate": verifyitemstate})

        childresult.append({"id": step.id, "code": step.code, "name": step.name, "approval": step.approval,
                            "skip": step.skip, "group": group, "time": step.time, "runid": runid,
                            "starttime": starttime, "endtime": endtime, "operator": operator,
                            "parameter": parameter, "runresult": runresult,
                            "explain": explain, "state": state, "scripts": scripts, "verifyitems": verifyitems,
                            "note": note, "rto": rto, "children": getchildrensteps(processrun, step)})
    return childresult


def if_contains_sign(file_name):
    sign_string = '\/"*?<>'
    for i in sign_string:
        if i in file_name:
            return True
    return False


def custom_cv_params(**kwargs):
    """构造参数xml
    """
    root = etree.Element("root")
    param_node = etree.SubElement(root, "param")
    for k, v in kwargs.items():
        param_node.attrib['{0}'.format(k)] = str(v)
    config = etree.tounicode(root)
    return config
