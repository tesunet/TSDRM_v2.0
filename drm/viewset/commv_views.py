# commvault相关：客户端监控相关、自主恢复、commvaul信息配置、客户端管理
from collections import OrderedDict

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse


from ..tasks import *
from TSDRM import settings
from drm.api.commvault import SQLApi
from drm.api.commvault.RestApi import *
from .public_func import *
from .basic_views import getpagefuns
from .config_views import get_credit_info


######################
# 客户端监控相关
######################
def get_rowspan(whole_list, **kwargs):
    clientname = kwargs.get('clientname', '')
    idataagent = kwargs.get('idataagent', '')
    type = kwargs.get('type', '')
    subclient = kwargs.get('subclient', '')

    scheduePolicy = kwargs.get('scheduePolicy', '')
    schedbackuptype = kwargs.get('schedbackuptype', '')

    row_span = 0

    if clientname and not any([idataagent, type, subclient, scheduePolicy, schedbackuptype]):
        for tl in whole_list:
            if tl['clientname'] == clientname:
                row_span += 1
    if all([clientname, idataagent]) and not any([type, subclient, scheduePolicy, schedbackuptype]):
        for tl in whole_list:
            if tl['clientname'] == clientname and tl['idataagent'] == idataagent:
                row_span += 1
    if all([clientname, idataagent, type]) and not any([subclient, scheduePolicy, schedbackuptype]):
        for tl in whole_list:
            if tl['clientname'] == clientname and tl['idataagent'] == idataagent and tl['type'] == type:
                row_span += 1
    if all([clientname, idataagent, type, subclient]) and not any([scheduePolicy, schedbackuptype]):
        for tl in whole_list:
            if tl['clientname'] == clientname and tl['idataagent'] == idataagent and tl['type'] == type and tl['subclient'] == subclient:
                row_span += 1
    if all([clientname, idataagent, type, subclient, scheduePolicy]) and not schedbackuptype:
        for tl in whole_list:
            if tl['clientname'] == clientname and tl['idataagent'] == idataagent and tl['type'] == type and tl['subclient'] == subclient and tl['scheduePolicy'] == scheduePolicy:
                row_span += 1
    if all([clientname, idataagent, type, subclient, scheduePolicy, schedbackuptype]):
        for tl in whole_list:
            if tl['clientname'] == clientname and tl['idataagent'] == idataagent and tl['type'] == type and tl['subclient'] == subclient and tl['scheduePolicy'] == scheduePolicy and tl['schedbackuptype'] == schedbackuptype:
                row_span += 1
    return row_span


@login_required
def get_backup_status(request):
    whole_list = []
    utils_manage_id = request.POST.get('utils_manage_id', '')

    try:
        utils_manage_id = int(utils_manage_id)
        utils_manage = UtilsManage.objects.get(id=utils_manage_id)
    except:
        return JsonResponse({
            "ret": 0,
            "data": "Commvault工具未配置。",
        })
    else:
        _, sqlserver_credit = get_credit_info(utils_manage.content)
        try:
            dm = SQLApi.CVApi(sqlserver_credit)
            whole_list = dm.get_backup_status()

            for num, wl in enumerate(whole_list):
                clientname_rowspan = get_rowspan(whole_list, clientname=wl['clientname'])
                idataagent_rowspan = get_rowspan(whole_list, clientname=wl['clientname'], idataagent=wl['idataagent'])
                type_rowspan = get_rowspan(whole_list, clientname=wl['clientname'], idataagent=wl['idataagent'],
                                           type=wl['type'])
                # 时间
                try:
                    whole_list[num]["startdate"] = "{:%Y-%m-%d %H:%M:%S}".format(whole_list[num]["startdate"])
                except Exception as e:
                    whole_list[num]["startdate"] = ""

                whole_list[num]['clientname_rowspan'] = clientname_rowspan
                whole_list[num]['idataagent_rowspan'] = idataagent_rowspan
                whole_list[num]['type_rowspan'] = type_rowspan

            dm.close()
        except Exception as e:
            return JsonResponse({
                "ret": 0,
                "data": "获取备份状态信息失败。",
            })
        return JsonResponse({
            "ret": 1,
            "data": whole_list,
        })


@login_required
def get_backup_content(request):
    utils_manage_id = request.POST.get('utils_manage_id', '')

    try:
        utils_manage_id = int(utils_manage_id)
        utils_manage = UtilsManage.objects.get(id=utils_manage_id)
    except:
        return JsonResponse({
            "ret": 0,
            "data": "Commvault工具未配置。",
        })
    else:
        _, sqlserver_credit = get_credit_info(utils_manage.content)

        whole_list = []
        try:
            dm = SQLApi.CVApi(sqlserver_credit)
            whole_list = dm.get_backup_content()

            for num, wl in enumerate(whole_list):
                clientname_rowspan = get_rowspan(whole_list, clientname=wl['clientname'])
                idataagent_rowspan = get_rowspan(whole_list, clientname=wl['clientname'], idataagent=wl['idataagent'])
                type_rowspan = get_rowspan(whole_list, clientname=wl['clientname'], idataagent=wl['idataagent'],
                                           type=wl['type'])

                whole_list[num]['clientname_rowspan'] = clientname_rowspan
                whole_list[num]['idataagent_rowspan'] = idataagent_rowspan
                whole_list[num]['type_rowspan'] = type_rowspan

        except Exception as e:
            print(e)
            return JsonResponse({
                "ret": 0,
                "data": "获取存储策略信息失败。",
            })
        else:
            return JsonResponse({
                "ret": 1,
                "data": whole_list,
            })


@login_required
def get_storage_policy(request):
    whole_list = []
    utils_manage_id = request.POST.get('utils_manage_id', '')

    try:
        utils_manage_id = int(utils_manage_id)
        utils_manage = UtilsManage.objects.get(id=utils_manage_id)
    except:
        return JsonResponse({
            "ret": 0,
            "data": "Commvault工具未配置。",
        })
    else:
        _, sqlserver_credit = get_credit_info(utils_manage.content)
        try:


            dm = SQLApi.CVApi(sqlserver_credit)
            whole_list = dm.get_storage_policy()

            for num, wl in enumerate(whole_list):
                clientname_rowspan = get_rowspan(whole_list, clientname=wl['clientname'])
                idataagent_rowspan = get_rowspan(whole_list, clientname=wl['clientname'], idataagent=wl['idataagent'])
                type_rowspan = get_rowspan(whole_list, clientname=wl['clientname'], idataagent=wl['idataagent'],
                                           type=wl['type'])

                whole_list[num]['clientname_rowspan'] = clientname_rowspan
                whole_list[num]['idataagent_rowspan'] = idataagent_rowspan
                whole_list[num]['type_rowspan'] = type_rowspan

        except Exception as e:
            print(e)
            return JsonResponse({
                "ret": 0,
                "data": "获取存储策略信息失败。",
            })
        else:
            return JsonResponse({
                "ret": 1,
                "data": whole_list
            })


@login_required
def get_schedule_policy(request):
    whole_list = []
    utils_manage_id = request.POST.get('utils_manage_id', '')

    try:
        utils_manage_id = int(utils_manage_id)
        utils_manage = UtilsManage.objects.get(id=utils_manage_id)
    except:
        return JsonResponse({
            "ret": 0,
            "data": "Commvault工具未配置。",
        })
    else:
        _, sqlserver_credit = get_credit_info(utils_manage.content)
        try:
            # all_client_manage = Origin.objects.exclude(state="9").values("client_name")
            # tmp_client_manage = [tmp_client["client_name"] for tmp_client in all_client_manage]

            dm = SQLApi.CVApi(sqlserver_credit)
            whole_list = dm.get_schedule_policy()
            ordered_whole_list = []
            dm.close()
            for num, wl in enumerate(whole_list):

                schedule_dict = OrderedDict()

                clientname_rowspan = get_rowspan(whole_list, clientname=wl['clientname'])
                idataagent_rowspan = get_rowspan(whole_list, clientname=wl['clientname'], idataagent=wl['idataagent'])
                type_rowspan = get_rowspan(whole_list, clientname=wl['clientname'], idataagent=wl['idataagent'],
                                           type=wl['type'])
                # 子客户端，计划策略，备份类型
                subclient_rowspan = get_rowspan(whole_list, clientname=wl['clientname'],
                                                      idataagent=wl['idataagent'],
                                                      type=wl['type'], subclient=wl['subclient'])
                if wl['scheduePolicy']:
                    scheduePolicy_rowspan = get_rowspan(whole_list, clientname=wl['clientname'],
                                                          idataagent=wl['idataagent'],
                                                          type=wl['type'], subclient=wl['subclient'],
                                                          scheduePolicy=wl['scheduePolicy'])
                else:
                    scheduePolicy_rowspan = 1
                if wl['schedbackuptype'] and wl['scheduePolicy']:
                    schedbackuptype_rowspan = get_rowspan(whole_list, clientname=wl['clientname'],
                                                          idataagent=wl['idataagent'],
                                                          type=wl['type'], subclient=wl['subclient'],
                                                          scheduePolicy=wl['scheduePolicy'],
                                                          schedbackuptype=wl['schedbackuptype'])
                else:
                    schedbackuptype_rowspan = 1
                schedule_dict['clientname_rowspan'] = clientname_rowspan
                schedule_dict['idataagent_rowspan'] = idataagent_rowspan
                schedule_dict['type_rowspan'] = type_rowspan
                schedule_dict['subclient_rowspan'] = subclient_rowspan
                schedule_dict['scheduePolicy_rowspan'] = scheduePolicy_rowspan
                schedule_dict['schedbackuptype_rowspan'] = schedbackuptype_rowspan

                schedule_dict["clientname"] = wl["clientname"]
                schedule_dict["idataagent"] = wl["idataagent"]
                schedule_dict["type"] = wl["type"]
                schedule_dict["subclient"] = wl["subclient"]
                schedule_dict["scheduePolicy"] = wl["scheduePolicy"] if wl["scheduePolicy"] else "无"
                schedule_dict["schedbackuptype"] = wl["schedbackuptype"] if wl["schedbackuptype"] else "无"
                schedule_dict["schedpattern"] = wl["schedpattern"] if wl["schedpattern"] else "无"

                schedule_dict["option"] = {
                    "schedpattern": wl["schedpattern"],
                    "schednextbackuptime": wl["schednextbackuptime"],
                    "scheduleName": wl["scheduleName"],
                    "schedinterval": wl["schedinterval"],
                    "schedbackupday": wl["schedbackupday"],
                    "schedbackuptype": wl["schedbackuptype"],
                }

                ordered_whole_list.append(schedule_dict)

        except Exception as e:
            print(e)
            return JsonResponse({
                "ret": 0,
                "data": "获取计划策略信息失败。",
            })
        else:
            return JsonResponse({
                "ret": 1,
                "data": ordered_whole_list,
            })


@login_required
def get_client_info(request):
    utils_manage_id = request.POST.get('utils_manage_id', '')

    try:
        utils_manage_id = int(utils_manage_id)
        utils_manage = UtilsManage.objects.get(id=utils_manage_id)
    except:
        return JsonResponse({
            "ret": 0,
            "data": "Commvault工具未配置。",
        })
    else:
        _, sqlserver_credit = get_credit_info(utils_manage.content)
        try:
            dm = SQLApi.CVApi(sqlserver_credit)
            whole_list = dm.get_clients_info()
            dm.close()
            for client in whole_list:
                client["net"] = "正常"
                # for i in range(4):
                #     netresult = os.system(u'ping -n 1 ' + client["network_interface"])
                #     if netresult == 0:
                #         client["net"] = "正常"
                #         break;
                # else:
                #     client["net"] = "中断"

        except Exception as e:
            print(e)
            return JsonResponse({
                "ret": 0,
                "data": "获取客户端基础信息失败。",
            })
        else:
            return JsonResponse({
                "ret": 1,
                "data": whole_list,
            })


@login_required
def get_cv_sla(request):
    whole_list = []
    utils_manage_id = request.POST.get('utils_manage_id', '')

    try:
        utils_manage_id = int(utils_manage_id)
        utils_manage = UtilsManage.objects.get(id=utils_manage_id)
    except:
        return JsonResponse({
            "ret": 0,
            "data": "Commvault工具未配置。",
        })
    else:
        _, sqlserver_credit = get_credit_info(utils_manage.content)
        try:
            dm = SQLApi.CVApi(sqlserver_credit)
            whole_list = dm.get_sla()

            for num, wl in enumerate(whole_list):
                clientname_rowspan = get_rowspan(whole_list, clientname=wl['clientname'])
                idataagent_rowspan = get_rowspan(whole_list, clientname=wl['clientname'], idataagent=wl['idataagent'])
                type_rowspan = get_rowspan(whole_list, clientname=wl['clientname'], idataagent=wl['idataagent'],
                                           type=wl['type'])

                whole_list[num]['clientname_rowspan'] = clientname_rowspan
                whole_list[num]['idataagent_rowspan'] = idataagent_rowspan
                whole_list[num]['type_rowspan'] = type_rowspan

            dm.close()
        except Exception as e:
            return JsonResponse({
                "ret": 0,
                "data": "获取健康度信息失败。",
            })
        return JsonResponse({
            "ret": 1,
            "data": whole_list,
        })


######################
# 自主恢复
######################
def manualrecovery(request, funid):
    if request.user.is_authenticated():
        result = []
        all_targets = Target.objects.exclude(state="9")
        return render(request, 'manualrecovery.html',
                      {'username': request.user.userinfo.fullname, "manualrecoverypage": True,
                       "pagefuns": getpagefuns(funid, request=request), "all_targets": all_targets})
    else:
        return HttpResponseRedirect("/login")


def manualrecoverydata(request):
    if request.user.is_authenticated():
        result = []
        all_origins = Origin.objects.exclude(state="9").select_related("target")
        for origin in all_origins:
            result.append({
                "client_manage_id": origin.id,
                "client_name": origin.client_name,
                "client_id": origin.client_id,
                "client_os": origin.os,
                "model": json.loads(origin.info)["agent"],
                "data_path": origin.data_path if origin.data_path else "",
                "copy_priority": origin.copy_priority,
                "target_client": origin.target.client_name
            })
        return JsonResponse({"data": result})
    else:
        return HttpResponseRedirect("/login")


def dooraclerecovery(request):
    if request.user.is_authenticated():
        if request.method == 'POST':
            sourceClient = request.POST.get('sourceClient', '')
            destClient = request.POST.get('destClient', '')
            restoreTime = request.POST.get('restoreTime', '')
            browseJobId = request.POST.get('browseJobId', '')
            agent = request.POST.get('agent', '')
            data_path = request.POST.get('data_path', '')
            copy_priority = request.POST.get('copy_priority', '')

            #################################
            # sourceClient>> instance_name  #
            #################################
            instance = ""
            try:
                cur_origin = Origin.objects.exclude(state="9").get(client_name=sourceClient)
            except Origin.DoesNotExist as e:
                return HttpResponse("恢复任务启动失败, 源客户端不存在。")
            else:
                oracle_info = json.loads(cur_origin.info)

                if oracle_info:
                    try:
                        instance = oracle_info["instance"]
                    except:
                        pass
            if not instance:
                return HttpResponse("恢复任务启动失败, 数据库实例不存在。")
            oraRestoreOperator = {"restoreTime": restoreTime, "browseJobId": None, "data_path": data_path, "copy_priority": copy_priority}

            cvToken = CV_RestApi_Token()
            cvToken.login(settings.CVApi_credit)
            cvAPI = CV_API(cvToken)
            if agent.upper() == "ORACLE DATABASE":
                if cvAPI.restoreOracleBackupset(sourceClient, destClient, instance, oraRestoreOperator):
                    return HttpResponse("恢复任务已经启动。" + cvAPI.msg)
                else:
                    return HttpResponse("恢复任务启动失败。" + cvAPI.msg)
            elif agent.upper() == "ORACLE RAC":
                oraRestoreOperator["browseJobId"] = browseJobId
                if cvAPI.restoreOracleRacBackupset(sourceClient, destClient, instance, oraRestoreOperator):
                    return HttpResponse("恢复任务已经启动。" + cvAPI.msg)
                else:
                    return HttpResponse("恢复任务启动失败。" + cvAPI.msg)
            else:
                return HttpResponse("无当前模块，恢复任务启动失败。")
        else:
            return HttpResponse("恢复任务启动失败。")


def oraclerecoverydata(request):
    if request.user.is_authenticated():
        client_name = request.GET.get('clientName', '')
        result = []

        dm = SQLApi.CVApi(settings.sql_credit)
        result = dm.get_oracle_backup_job_list(client_name)
        dm.close()
        return JsonResponse({"data": result})
    else:
        return HttpResponseRedirect("/login")


######################
# commvaul信息配置
######################
def serverconfig(request, funid):
    if request.user.is_authenticated():
        cvvendor = Vendor.objects.first()
        id = 0
        webaddr = ""
        port = ""
        usernm = ""
        passwd = ""

        SQLServerHost = ""
        SQLServerUser = ""
        SQLServerPasswd = ""
        SQLServerDataBase = ""
        if cvvendor:
            id = cvvendor.id
            doc = parseString(cvvendor.content)
            try:
                webaddr = (doc.getElementsByTagName("webaddr"))[0].childNodes[0].data
            except:
                pass
            try:
                port = (doc.getElementsByTagName("port"))[0].childNodes[0].data
            except:
                pass
            try:
                usernm = (doc.getElementsByTagName("username"))[0].childNodes[0].data
            except:
                pass
            try:
                passwd = (doc.getElementsByTagName("passwd"))[0].childNodes[0].data
            except:
                pass

            # SQLServer
            try:
                SQLServerHost = (doc.getElementsByTagName("SQLServerHost"))[0].childNodes[0].data
            except:
                pass
            try:
                SQLServerUser = (doc.getElementsByTagName("SQLServerUser"))[0].childNodes[0].data
            except:
                pass
            try:
                SQLServerPasswd = (doc.getElementsByTagName("SQLServerPasswd"))[0].childNodes[0].data
            except:
                pass
            try:
                SQLServerDataBase = (doc.getElementsByTagName("SQLServerDataBase"))[0].childNodes[0].data
            except:
                pass

        return render(request, 'serverconfig.html',
                      {'username': request.user.userinfo.fullname, "serverconfigpage": True, "id": id,
                       "webaddr": webaddr, "port": port, "usernm": usernm, "passwd": passwd,
                       "SQLServerHost": SQLServerHost, "SQLServerUser": SQLServerUser,
                       "SQLServerPasswd": SQLServerPasswd, "SQLServerDataBase": SQLServerDataBase,
                       "pagefuns": getpagefuns(funid, request=request)})
    else:
        return HttpResponseRedirect("/login")


def serverconfigsave(request):
    if request.method == 'POST':
        result = ""
        id = request.POST.get('id', '')
        webaddr = request.POST.get('webaddr', '')
        port = request.POST.get('port', '')
        usernm = request.POST.get('usernm', '')
        passwd = request.POST.get('passwd', '')

        SQLServerHost = request.POST.get('SQLServerHost', '')
        SQLServerUser = request.POST.get('SQLServerUser', '')
        SQLServerPasswd = request.POST.get('SQLServerPasswd', '')
        SQLServerDataBase = request.POST.get('SQLServerDataBase', '')

        cvvendor_content = """<?xml version="1.0" ?>
            <vendor>
                <webaddr>{webaddr}</webaddr>
                <port>{port}</port>
                <username>{username}</username>
                <passwd>{passwd}</passwd>
                <SQLServerHost>{SQLServerHost}</SQLServerHost>
                <SQLServerUser>{SQLServerUser}</SQLServerUser>
                <SQLServerPasswd>{SQLServerPasswd}</SQLServerPasswd>
                <SQLServerDataBase>{SQLServerDataBase}</SQLServerDataBase>
            </vendor>""".format(**{
            "webaddr": webaddr,
            "port": port,
            "username": usernm,
            "passwd": passwd,
            "SQLServerHost": SQLServerHost,
            "SQLServerUser": SQLServerUser,
            "SQLServerPasswd": SQLServerPasswd,
            "SQLServerDataBase": SQLServerDataBase
        })

        cvvendor = Vendor.objects.first()
        if cvvendor:
            cvvendor.content = cvvendor_content
            cvvendor.save()
            result = "保存成功。"
        else:
            cvvendor = Vendor()
            cvvendor.content = cvvendor_content
            cvvendor.save()
            result = "保存成功。"
        return HttpResponse(result)


######################
# 客户端管理
######################
def target(request, funid):
    if request.user.is_authenticated():
        #############################################
        # clientid, clientname, agent, instance, os #
        #############################################
        dm = SQLApi.CVApi(settings.sql_credit)

        oracle_data = dm.get_instance_from_oracle()

        # 获取包含oracle模块所有客户端
        installed_client = dm.get_all_install_clients()
        dm.close()
        oracle_data_list = []
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

                oracle_data_list.append({
                    "clientid": od["clientid"],
                    "clientname": od["clientname"],
                    "agent": od["agent"],
                    "instance": od["instance"],
                    "os": client_os
                })
                # 去重
                pre_od_name = od["clientname"]
        return render(request, 'target.html',
                      {'username': request.user.userinfo.fullname,
                       "oracle_data": json.dumps(oracle_data_list),
                       "pagefuns": getpagefuns(funid, request=request)})
    else:
        return HttpResponseRedirect("/login")


def target_data(request):
    if request.user.is_authenticated():
        all_target = Target.objects.exclude(state="9")
        all_target_list = []
        for target in all_target:
            target_info = json.loads(target.info)
            all_target_list.append({
                "id": target.id,
                "client_id": target.client_id,
                "client_name": target.client_name,
                "os": target.os,
                "agent": target_info["agent"],
                "instance": target_info["instance"]
            })
        return JsonResponse({"data": all_target_list})
    else:
        return HttpResponseRedirect("/login")


def target_save(request):
    if request.user.is_authenticated():
        target_id = request.POST.get("target_id", "")
        client_id = request.POST.get("client_id", "")
        client_name = request.POST.get("client_name", "").strip()
        agent = request.POST.get("agent", "").strip()
        instance = request.POST.get("instance", "").strip()
        os = request.POST.get("os", "").strip()
        ret = 0
        info = ""
        try:
            target_id = int(target_id)
        except:
            ret = 0
            info = "网络异常"
        else:
            try:
                client_id = int(client_id)
            except:
                ret = 0
                info = "目标客户端未选择。"
            else:
                if target_id == 0:
                    # 判断是否存在
                    check_target = Target.objects.exclude(
                        state="9").filter(client_id=client_id)
                    if check_target.exists():
                        ret = 0
                        info = "该客户端已选为目标客户端，请勿重复添加。"
                    else:
                        try:
                            cur_target = Target()
                            cur_target.client_id = client_id
                            cur_target.client_name = client_name
                            cur_target.os = os
                            cur_target.info = json.dumps({
                                "agent": agent,
                                "instance": instance
                            })
                            cur_target.save()
                        except:
                            ret = 0
                            info = "数据保存失败。"
                        else:
                            ret = 1
                            info = "新增成功。"
                else:
                    check_target = Target.objects.exclude(state="9").exclude(id=target_id).filter(
                        client_id=client_id)
                    if check_target.exists():
                        ret = 0
                        info = "该客户端已选为终端，请勿重复添加。"
                    else:
                        try:
                            cur_target = Target.objects.get(id=target_id)
                        except Target.DoesNotExist as e:
                            ret = 0
                            info = "终端不存在，请联系管理员。"
                        else:
                            try:
                                cur_target.client_id = client_id
                                cur_target.client_name = client_name
                                cur_target.os = os
                                cur_target.info = json.dumps({
                                    "agent": agent,
                                    "instance": instance
                                })
                                cur_target.save()
                            except:
                                ret = 0
                                info = "数据修改失败。"
                            else:
                                ret = 1
                                info = "修改成功"

        return JsonResponse({
            "ret": ret,
            "info": info
        })
    else:
        return HttpResponseRedirect("/login")


def target_del(request):
    if request.user.is_authenticated():
        target_id = request.POST.get("target_id", "")

        try:
            cur_target = Target.objects.get(id=int(target_id))
        except:
            return JsonResponse({
                "ret": 0,
                "info": "当前网络异常"
            })
        else:
            try:
                cur_target.state = "9"
                cur_target.save()
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


def origin(request, funid):
    if request.user.is_authenticated():
        #############################################
        # clientid, clientname, agent, instance, os #
        #############################################
        dm = SQLApi.CVApi(settings.sql_credit)

        oracle_data = dm.get_instance_from_oracle()

        # 获取包含oracle模块所有客户端
        installed_client = dm.get_all_install_clients()
        dm.close()
        oracle_data_list = []
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

                oracle_data_list.append({
                    "clientid": od["clientid"],
                    "clientname": od["clientname"],
                    "agent": od["agent"],
                    "instance": od["instance"],
                    "os": client_os
                })
                # 去重
                pre_od_name = od["clientname"]

        # 所有关联终端
        all_target = Target.objects.exclude(state="9")
        return render(request, 'origin.html',
                      {'username': request.user.userinfo.fullname,
                       "oracle_data": json.dumps(oracle_data_list),
                       "all_target": all_target,
                       "pagefuns": getpagefuns(funid, request=request)})
    else:
        return HttpResponseRedirect("/login")


def origin_data(request):
    if request.user.is_authenticated():
        all_origin = Origin.objects.exclude(state="9").select_related("target")
        all_origin_list = []
        for origin in all_origin:
            origin_info = json.loads(origin.info)
            all_origin_list.append({
                "id": origin.id,
                "client_id": origin.client_id,
                "client_name": origin.client_name,
                "os": origin.os,
                "agent": origin_info["agent"],
                "instance": origin_info["instance"],
                "target_client": origin.target.id,
                "target_client_name": origin.target.client_name,
                "copy_priority": origin.copy_priority,
                "db_open": origin.db_open,
                "data_path": origin.data_path,
            })

        return JsonResponse({"data": all_origin_list})
    else:
        return HttpResponseRedirect("/login")


def origin_save(request):
    if request.user.is_authenticated():
        origin_id = request.POST.get("origin_id", "")
        client_id = request.POST.get("client_id", "")
        client_name = request.POST.get("client_name", "").strip()
        agent = request.POST.get("agent", "").strip()
        instance = request.POST.get("instance", "").strip()
        client_os = request.POST.get("os", "")
        target_client = request.POST.get("target_client", "")

        copy_priority = request.POST.get("copy_priority", "")
        db_open = request.POST.get("db_open", "")
        data_path = request.POST.get("data_path", "")
        ret = 0
        info = ""
        try:
            copy_priority = int(copy_priority)
            db_open = int(db_open)
            origin_id = int(origin_id)
        except:
            ret = 0
            info = "网络异常"
        else:
            try:
                client_id = int(client_id)
            except:
                ret = 0
                info = "源端未选择。"
            else:
                try:
                    target_client = int(target_client)
                except:
                    ret = 0
                    info = "未关联终端"
                else:
                    try:
                        to_target = Target.objects.get(id=target_client)
                    except Target.DoesNotExist as e:
                        ret = 0
                        info = "该终端不存在。"
                    else:
                        target_id = to_target.id
                        if origin_id == 0:
                            try:
                                cur_origin = Origin()
                                cur_origin.client_id = client_id
                                cur_origin.client_name = client_name
                                cur_origin.os = client_os
                                cur_origin.info = json.dumps({
                                    "agent": agent,
                                    "instance": instance
                                })
                                cur_origin.target_id = target_id
                                cur_origin.copy_priority = copy_priority
                                cur_origin.db_open = db_open
                                cur_origin.data_path = data_path
                                cur_origin.save()
                            except Exception as e:
                                print(e)
                                ret = 0
                                info = "数据保存失败。"
                            else:
                                ret = 1
                                info = "新增成功。"
                        else:
                            try:
                                cur_origin = Origin.objects.get(id=origin_id)
                            except Origin.DoesNotExist as e:
                                ret = 0
                                info = "源端不存在，请联系管理员。"
                            else:
                                try:
                                    cur_origin.client_id = client_id
                                    cur_origin.client_name = client_name
                                    cur_origin.os = client_os
                                    cur_origin.info = json.dumps({
                                        "agent": agent,
                                        "instance": instance
                                    })
                                    cur_origin.copy_priority = copy_priority
                                    cur_origin.db_open = db_open
                                    cur_origin.data_path = data_path
                                    cur_origin.target_id = target_id
                                    cur_origin.save()
                                except:
                                    ret = 0
                                    info = "数据修改失败。"
                                else:
                                    ret = 1
                                    info = "修改成功"

        return JsonResponse({
            "ret": ret,
            "info": info
        })
    else:
        return HttpResponseRedirect("/login")


def origin_del(request):
    if request.user.is_authenticated():
        origin_id = request.POST.get("origin_id", "")
        try:
            cur_origin = Origin.objects.get(id=int(origin_id))
        except:
            return JsonResponse({
                "ret": 0,
                "info": "当前网络异常"
            })
        else:
            try:
                cur_origin.state = "9"
                cur_origin.save()
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
