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
from concurrent.futures import ThreadPoolExecutor, as_completed


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
            if tl['clientname'] == clientname and tl['idataagent'] == idataagent and tl['type'] == type and tl[
                'subclient'] == subclient:
                row_span += 1
    if all([clientname, idataagent, type, subclient, scheduePolicy]) and not schedbackuptype:
        for tl in whole_list:
            if tl['clientname'] == clientname and tl['idataagent'] == idataagent and tl['type'] == type and tl[
                'subclient'] == subclient and tl['scheduePolicy'] == scheduePolicy:
                row_span += 1
    if all([clientname, idataagent, type, subclient, scheduePolicy, schedbackuptype]):
        for tl in whole_list:
            if tl['clientname'] == clientname and tl['idataagent'] == idataagent and tl['type'] == type and tl[
                'subclient'] == subclient and tl['scheduePolicy'] == scheduePolicy and tl[
                'schedbackuptype'] == schedbackuptype:
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
                subclient_rowspan = get_rowspan(whole_list, clientname=wl['clientname'], idataagent=wl['idataagent'],
                                           type=wl['type'], subclient=wl['subclient'])
                whole_list[num]['clientname_rowspan'] = clientname_rowspan
                whole_list[num]['idataagent_rowspan'] = idataagent_rowspan
                whole_list[num]['type_rowspan'] = type_rowspan
                whole_list[num]['subclient_rowspan'] = subclient_rowspan

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


def get_instance_list(um):
    # 解析出账户信息
    _, sqlserver_credit = get_credit_info(um.content)

    #############################################
    # clientid, clientname, agent, instance, os #
    #############################################
    dm = SQLApi.CVApi(sqlserver_credit)

    instance_data = dm.get_all_instance()

    dm.close()
    instance_list = []
    for od in instance_data:
        instance_list.append({
            "clientid": od["clientid"],
            "clientname": od["clientname"],
            "agent": od["agent"],
            "instance": od["instance"],
        })
    return {
        'utils_manage': um.id,
        'instance_list': instance_list
    }


######################
# 自主恢复
######################
def manualrecovery(request, funid):
    if request.user.is_authenticated():
        stds = CvClient.objects.exclude(state="9").exclude(type=1)
        util_manages = UtilsManage.objects.exclude(state='9').filter(util_type='Commvault')
        return render(request, 'manualrecovery.html',
                    {'username': request.user.userinfo.fullname, "pagefuns": getpagefuns(funid, request=request),
                    "stds": stds, "util_manages": util_manages})
    else:
        return HttpResponseRedirect("/login")


def manualrecoverydata(request):
    if request.user.is_authenticated():
        utils_id = request.GET.get("utils_id", "")
        result = []

        try:
            utils_id = int(utils_id)
        except Exception as e:
            print(e)
        else:
            pris = CvClient.objects.exclude(state="9").exclude(type=2).filter(utils_id=utils_id).select_related("destination")
            for pri in pris:
                result.append({
                    "client_manage_id": pri.id,
                    "client_name": pri.client_name,
                    "client_id": pri.client_id,
                    "instanceName": pri.instanceName,
                    "agentType": pri.agentType,
                    # "data_path": pri.data_path if pri.data_path else "",
                    # "copy_priority": pri.copy_priority,
                    "std_client": pri.destination.client_name if pri.destination else ""
                })
        return JsonResponse({"data": result})
    else:
        return HttpResponseRedirect("/login")


def dooraclerecovery(request):
    if request.user.is_authenticated():
        sourceClient = request.POST.get('sourceClient', '')
        destClient = request.POST.get('destClient', '')
        restoreTime = request.POST.get('restoreTime', '')
        browseJobId = request.POST.get('browseJobId', '')
        agent = request.POST.get('agent', '')
        data_path = request.POST.get('data_path', '')
        copy_priority = request.POST.get('copy_priority', '')

        try:
            copy_priority = int(copy_priority)
        except:
            pass

        data_sp = request.POST.get('data_sp', '')

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

            utils_content = cur_origin.utils.content if cur_origin.utils else ""
            commvault_credit, sqlserver_credit = get_credit_info(utils_content)

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
                # auxcopy_status = 'ERROR'
                print('当前备份记录对应的辅助拷贝状态 %s' % auxcopy_completed)
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
            # print('Rac %s' % curSCN)
            oraRestoreOperator = {"curSCN": curSCN, "browseJobId": None, "data_path": data_path,
                                  "copy_priority": copy_priority, "restoreTime": restoreTime}
            # print("> %s > %s, %s, %s" % (oraRestoreOperator, sourceClient, destClient, instance))

            cvToken = CV_RestApi_Token()
            cvToken.login(commvault_credit)
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
        return HttpResponseRedirect("/login")

def oraclerecoverydata(request):
    if request.user.is_authenticated():
        origin_id = request.GET.get('origin_id', '')
        result = []
        try:
            origin_id = int(origin_id)
            origin = Origin.objects.get(id=origin_id)
            utils_manage = origin.utils
            _, sqlserver_credit = get_credit_info(utils_manage.content)
            dm = SQLApi.CVApi(sqlserver_credit)
            result = dm.get_oracle_backup_job_list(origin.client_name)
            dm.close()
        except Exception as e:
            print(e)

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
@login_required
def target(request, funid):
    # 工具
    utils_manage = UtilsManage.objects.exclude(state='9').filter(util_type='Commvault')
    data = []

    try:
        pool = ThreadPoolExecutor(max_workers=10)

        all_tasks = [pool.submit(get_oracle_client, (um)) for um in utils_manage]
        for future in as_completed(all_tasks):
            if future.result():
                data.append(future.result())
    except:
        pass

    return render(request, 'target.html',
                  {'username': request.user.userinfo.fullname, 'utils_manage': utils_manage,
                   "data": json.dumps(data),
                   "pagefuns": getpagefuns(funid, request=request)})


@login_required
def target_data(request):
    all_target = Target.objects.exclude(state="9").select_related('utils')
    all_target_list = []
    for target in all_target:
        target_info = json.loads(target.info)
        all_target_list.append({
            "id": target.id,
            "client_id": target.client_id,
            "client_name": target.client_name,
            "os": target.os,
            "agent": target_info["agent"],
            "instance": target_info["instance"],
            "utils_id": target.utils_id,
            "utils_name": target.utils.name if target.utils else ''
        })
    return JsonResponse({"data": all_target_list})


@login_required
def target_save(request):
    target_id = request.POST.get("target_id", "")
    client_id = request.POST.get("client_id", "")
    client_name = request.POST.get("client_name", "").strip()
    agent = request.POST.get("agent", "").strip()
    instance = request.POST.get("instance", "").strip()
    os = request.POST.get("os", "").strip()
    utils_manage = request.POST.get("utils_manage", "").strip()
    ret = 0
    info = ""
    try:
        target_id = int(target_id)
    except:
        ret = 0
        info = "网络异常。"
    else:
        try:
            utils_manage = int(utils_manage)
        except:
            ret = 0
            info = "工具未选择。"
        else:
            try:
                client_id = int(client_id)
            except:
                ret = 0
                info = "目标客户端未选择。"
            else:
                if target_id == 0:
                    # 判断是否存在
                    check_target = Target.objects.exclude(state="9").filter(client_id=client_id)
                    if check_target.exists():
                        ret = 0
                        info = "该客户端已选为目标客户端，请勿重复添加。"
                    else:
                        try:
                            cur_target = Target()
                            cur_target.client_id = client_id
                            cur_target.client_name = client_name
                            cur_target.os = os
                            cur_target.utils_id = utils_manage
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
                                cur_target.utils_id = utils_manage
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


@login_required
def target_del(request):
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


@login_required
def origin(request, funid):
    # 工具
    utils_manage = UtilsManage.objects.exclude(state='9').filter(util_type='Commvault')
    data = []

    try:
        pool = ThreadPoolExecutor(max_workers=10)

        all_tasks = [pool.submit(get_oracle_client, (um)) for um in utils_manage]
        for future in as_completed(all_tasks):
            if future.result():
                data.append(future.result())
    except:
        pass

    # 所有关联终端
    all_target = Target.objects.exclude(state="9").values()

    u_targets = []

    for um in utils_manage:
        target_list = []
        for target in all_target:
            if target['utils_id'] == um.id:
                target_list.append({
                    'target_id': target['id'],
                    'target_name': target['client_name']
                })
        u_targets.append({
            'utils_manage': um.id,
            'target_list': target_list
        })

    # 恢复资源
    # [{
    #     'utils_manage': '',
    #     'target_list': [{
    #         'target_id': '',
    #         'target_name': ''
    #     }]
    # }]

    return render(request, 'origin.html',
                  {'username': request.user.userinfo.fullname, 'utils_manage': utils_manage,
                   "data": json.dumps(data), "all_target": all_target, 'u_targets': u_targets,
                   "pagefuns": getpagefuns(funid, request=request)})


@login_required
def origin_data(request):
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
            "log_restore": origin.log_restore,

            "utils_id": origin.utils_id,
            "utils_name": origin.utils.name if origin.utils else ''
        })

    return JsonResponse({"data": all_origin_list})


@login_required
def origin_save(request):
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
    log_restore = request.POST.get("log_restore", "")

    utils_manage = request.POST.get("utils_manage", "").strip()
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
            utils_manage = int(utils_manage)
        except:
            ret = 0
            info = "工具未选择。"
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

                                cur_origin.utils_id = utils_manage

                                try:
                                    log_restore = int(log_restore)
                                except:
                                    pass
                                else:
                                    cur_origin.log_restore = log_restore
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

                                    cur_origin.utils_id = utils_manage

                                    try:
                                        log_restore = int(log_restore)
                                    except:
                                        pass
                                    else:
                                        cur_origin.log_restore = log_restore
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


@login_required
def origin_del(request):
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
