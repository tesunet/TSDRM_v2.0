# 监控图表：仪表盘、灾备基础框架
from django.shortcuts import render
from django.http import Http404, JsonResponse

from ..tasks import *
from .basic_views import getpagefuns
from .config_views import get_credit_info
from .public_func import *
from drm.api.commvault import SQLApi
from drm.api.commvault.RestApi import *
from django.contrib.auth.decorators import login_required
import pythoncom
from ping3 import ping
pythoncom.CoInitialize ()
import wmi

######################
# 仪表盘
######################
@login_required
def dashboard(request, funid):
    util_manages = UtilsManage.objects.exclude(state='9')

    return render(request, "dashboard.html", {
        'username': request.user.userinfo.fullname,
        "pagefuns": getpagefuns(funid, request=request),
        "util_manages":util_manages,
    })

@login_required
def get_dashboard(request):
    util = request.POST.get('util', '')
    startdate = (datetime.datetime.now() - datetime.timedelta(hours=24)).strftime("%Y-%m-%d")
    enddate = (datetime.datetime.now()).strftime("%Y-%m-%d")

    clientid = ''
    jobstatus = ''
    try:
        util = int(util)
    except:
        return JsonResponse({
            "ret": 0,
            "data": [],
        })
    # 24小时作业显示成功，执行中，失败状态的个数
    error_job_list = []
    show_job_status_num = ''
    util_manages = UtilsManage.objects.exclude(state='9').filter(id=util)
    if len(util_manages) > 0:
        util = util_manages[0]
        if util.util_type.upper() == 'COMMVAULT':
            commvault_credit, sqlserver_credit = get_credit_info(util.content)

            try:
                dm = SQLApi.CVApi(sqlserver_credit)
                #24小时作业
                _, show_job_status_num = dm.get_cv_joblist(startdate=startdate,
                               enddate=enddate, clientid=clientid, jobstatus=jobstatus)

                #异常事件
                job_list = dm.display_error_job_list(startdate=startdate, enddate=enddate, clientid=clientid)
                error_job_list = job_list[0:50]
            except Exception as e:
                print(e)
                return JsonResponse({
                    "ret": 0,
                    "data": "获取信息失败。",
                })
    return JsonResponse({"error_job_list": error_job_list,
                         "show_job_status_num": show_job_status_num,
                         })


@login_required
def cv_joblist(request,funid):
    startdate = (datetime.datetime.now() - datetime.timedelta(hours=24)).strftime("%Y-%m-%d")
    enddate = (datetime.datetime.now()).strftime("%Y-%m-%d")

    util_manages = UtilsManage.objects.exclude(state='9')
    util = request.GET.get('util', '')
    try:
        util = int(util)
    except:
        pass

    return render(request, "cv_joblist.html", {
        'username': request.user.userinfo.fullname,
        "pagefuns": getpagefuns(funid, request=request),
        "util_manages": util_manages,
        "util_id": util,
        "startdate": startdate,
        "enddate": enddate,
    })


@login_required
def get_cv_joblist(request):
    util = request.GET.get('util', '')
    startdate = request.GET.get('startdate', '')
    enddate = request.GET.get('enddate', '')
    clientid = request.GET.get('clientid', '')
    jobstatus = request.GET.get('jobstatus', '')


    try:
        clientid = int(clientid)
    except:
        clientid = ""

    try:
        util = int(util)
    except:
        return JsonResponse({
            "ret": 0,
            "data": 'Commvault工具未配置。',
        })
    job_list = []
    util_manages = UtilsManage.objects.exclude(state='9').filter(id=util)
    if len(util_manages) > 0:
        util = util_manages[0]
        if util.util_type.upper() == 'COMMVAULT':
            commvault_credit, sqlserver_credit = get_credit_info(util.content)

            try:
                dm = SQLApi.CVApi(sqlserver_credit)
                job_list, _ = dm.get_cv_joblist(startdate, enddate, clientid, jobstatus)

            except Exception as e:
                print(e)
                return JsonResponse({
                    "ret": 0,
                    "data": "获取信息失败。",
                })
    return JsonResponse({"data": job_list})


@login_required
def get_client_name(request):
    utils = request.POST.get('utils', '')

    try:
        utils = int(utils)
        utils_manage = UtilsManage.objects.get(id=utils)
    except:
        return JsonResponse({
            "ret": 0,
            "data": "Commvault工具未配置。",
        })
    else:
        _, sqlserver_credit = get_credit_info(utils_manage.content)
        try:
            dm = SQLApi.CVApi(sqlserver_credit)
            clientname_list = dm.get_clients_name()

        except Exception as e:
            print(e)
            return JsonResponse({
                "ret": 0,
                "data": "获取客户端基础信息失败。",
            })
        else:
            return JsonResponse({
                "ret": 1,
                "data": clientname_list,
            })


@login_required
def display_error_job(request,funid):
    startdate = (datetime.datetime.now() - datetime.timedelta(hours=24)).strftime("%Y-%m-%d")
    enddate = datetime.datetime.now().strftime("%Y-%m-%d")

    util_manages = UtilsManage.objects.exclude(state='9')
    util = request.GET.get('util', '')
    try:
        util = int(util)
    except:
        pass
    return render(request, "display_error_job.html", {
        'username': request.user.userinfo.fullname,
        "pagefuns": getpagefuns(funid, request=request),
        "util_manages": util_manages,
        "util_id": util,
        "startdate": startdate,
        "enddate": enddate,
    })


@login_required
def get_display_error_job(request):
    util = request.GET.get('util', '')
    startdate = request.GET.get('startdate', '')
    enddate = request.GET.get('enddate', '')
    clientid = request.GET.get('clientid', '')

    try:
        clientid = int(clientid)
    except:
        clientid = ""

    try:
        util = int(util)
    except:
        return JsonResponse({
            "ret": 0,
            "data": [],
        })
    job_list = []
    util_manages = UtilsManage.objects.exclude(state='9').filter(id=util)
    if len(util_manages) > 0:
        util = util_manages[0]
        if util.util_type.upper() == 'COMMVAULT':
            commvault_credit, sqlserver_credit = get_credit_info(util.content)

            try:
                dm = SQLApi.CVApi(sqlserver_credit)
                job_list = dm.display_error_job_list(startdate=startdate, enddate=enddate, clientid=clientid)

            except Exception as e:
                print(e)
                return JsonResponse({
                    "ret": 0,
                    "data": "获取信息失败。",
                })

    return JsonResponse({"data": job_list})


@login_required
def get_frameworkstate(request):
    util = request.POST.get('util', '')
    try:
        util = int(util)
    except:
        raise Http404()
    state=0
    util_manages = UtilsManage.objects.exclude(state='9').filter(id=util)
    if len(util_manages)>0:
        util=util_manages[0]
        if util.util_type.upper() == 'COMMVAULT':
            commvault_credit, sqlserver_credit = get_credit_info(util.content)
            # 先判断网络
            netresult = ping(commvault_credit["webaddr"])
            if netresult is not None:
                # 网络正常时取接口信息
                cvToken = CV_RestApi_Token()
                commvault_credit["token"]=""
                commvault_credit["lastlogin"] = 0
                cvToken.login(commvault_credit)
                if not cvToken.isLogin:
                    state=1
                # 网络正常时取数据库信息
                dm = SQLApi.CVApi(sqlserver_credit)
                if dm.isconnected() is not None:
                    #数据库正常时取ma信息
                    ma_info = dm.get_ma_info()
                    for ma in ma_info:
                        netresult = ping(ma["InterfaceName"])
                        if netresult is None:
                            state=1
                    for ma in ma_info:
                        if ma["Offline"] == 0:
                            break
                        else:
                            state=2
            else:
                state = 2
    return JsonResponse({
        "ret": 1,
        "data": state,
    })

######################
# 灾备基础框架
######################
@login_required
def framework(request, funid):
    util = request.GET.get("util", "")
    util_manages = UtilsManage.objects.exclude(state='9')
    try:
        util=int(util)
    except:
        pass


    return render(request, "framework.html", {
        'username': request.user.userinfo.fullname,
        "pagefuns": getpagefuns(funid, request=request),
        "util_manages": util_manages,
        "util_id":util,
    })

@login_required
def get_framework(request):
    util = request.POST.get('util', '')
    try:
        util = int(util)
    except:
        raise Http404()
    frameworkdata={}
    util_manages = UtilsManage.objects.exclude(state='9').filter(id=util)
    if len(util_manages)>0:
        util=util_manages[0]
        if util.util_type.upper() == 'COMMVAULT':
            commvault_credit, sqlserver_credit = get_credit_info(util.content)

            commserve = {
                'host': '无法获取',
                'version': '无法获取',
                'sp': '无法获取',
                'os': '无法获取',
                'net': '无法获取',

                'apiport': '无法获取',
                'apiconnect': '无法获取',
                'dbname': '无法获取',
                'dbconnect': '无法获取',
            }
            mas=[]

            #先判断网络
            netresult = ping(commvault_credit["webaddr"])
            if netresult is not None:
                commserve["net"] = "正常"
                # 网络正常时取数据库信息
                commserve["dbname"] = sqlserver_credit["SQLServerDataBase"]
                dm = SQLApi.CVApi(sqlserver_credit)
                if dm.isconnected() is not None:
                    commserve["dbconnect"] = "正常"

                    # 数据库连接正常，取cs信息
                    commserv_info = dm.get_commserv_info()
                    if commserv_info is not None:
                        commserve["host"] = commserv_info[3]
                        commserve["version"] = commserv_info[0]
                        commserve["sp"] = commserv_info[1]
                        commserve["os"] = commserv_info[2]
                    # 数据库连接正常，取ma信息
                    ma_info = dm.get_ma_info()
                    for ma in ma_info:
                        netresult = ping(ma["InterfaceName"])
                        if netresult is not None:
                            ma["net"] = "正常"
                        else:
                            ma["net"] = "中断"
                        if ma["Offline"] == 0:
                            ma["Offline"] = "在线"
                        else:
                            ma["Offline"] = "离线"
                        try:
                            ma["TotalSpaceMB"] = round(ma["TotalSpaceMB"]/1024/1024,2)
                        except:
                            pass
                        try:
                            ma["TotalFreeSpaceMB"] = round(ma["TotalFreeSpaceMB"]/1024/1024,2)
                        except:
                            pass
                        try:
                            ma["Percent"] = round((ma["TotalSpaceMB"] - ma["TotalFreeSpaceMB"])/ma["TotalSpaceMB"]*100,2)
                        except:
                            ma["Percent"] = 0
                        try:
                            ma["SpaceReserved"] = round(ma["SpaceReserved"]/1024/1024,2)
                        except:
                            pass
                        ma["CapacityAvailable"] = ma["TotalFreeSpaceMB"]
                        try:
                            ma["CapacityAvailable"] = ma["TotalFreeSpaceMB"]-ma["SpaceReserved"]
                        except:
                            pass
                        mas.append(ma)
                    frameworkdata["ma"] = mas


                else:
                    commserve["dbconnect"] = "中断"
                commserve["apiport"] = commvault_credit["port"]
                # 网络正常时取接口信息
                cvToken = CV_RestApi_Token()
                commvault_credit["token"]=""
                commvault_credit["lastlogin"] = 0
                cvToken.login(commvault_credit)
                if cvToken.isLogin:
                    commserve["apiconnect"] = "正常"
                else:
                    commserve["apiconnect"] = "中断"

            else:
                commserve["net"] = "中断"

            frameworkdata["commserve"] = commserve

    return JsonResponse({
        "ret": 1,
        "data": frameworkdata,
    })


@login_required
def get_csinfo(request):
    util = request.POST.get('util', '')
    try:
        util = int(util)
    except:
        raise Http404()
    frameworkdata={}
    util_manages = UtilsManage.objects.exclude(state='9').filter(id=util)
    if len(util_manages)>0:
        util=util_manages[0]
        if util.util_type.upper() == 'COMMVAULT':
            commvault_credit, sqlserver_credit = get_credit_info(util.content)

            commserve = {
                'cpuloadpercentage': '无法获取',
                'memtotal': '无法获取',
                'memutilization': '无法获取',
                'swaptotal': '无法获取',
                'swaputilization': '无法获取',
                'disktotal': '无法获取',
                'diskutilization': '无法获取',
            }
            try:
                conn = wmi.WMI(computer=commvault_credit["webaddr"], user=commvault_credit["hostusername"],
                               password=commvault_credit["hostpasswd"])
                cs = conn.Win32_ComputerSystem()
                ops = conn.Win32_OperatingSystem()
                pfu = conn.Win32_PageFileUsage()
                processor = conn.Win32_Processor()
                dd = conn.Win32_DiskDrive()
                commserve["memtotal"] = str(round(int(cs[0].TotalPhysicalMemory) / 1024 / 1024/1024,2))+'GB'
                commserve["memutilization"] = str(round((int(cs[0].TotalPhysicalMemory) / 1024 -int(ops[0].FreePhysicalMemory) )/(int(cs[0].TotalPhysicalMemory) / 1024 )*100,2))+'%'
                commserve["swaptotal"] = str(round(int(pfu[0].AllocatedBaseSize)/1024,2))+'GB'
                commserve["swaputilization"] = str(round(pfu[0].CurrentUsage/pfu[0].AllocatedBaseSize*100,2))+'%'
                cpuloadpercentage=""
                for cpu in processor:
                    cpuloadpercentage+=str(cpu.DeviceID) + ':' + str(cpu.LoadPercentage) + '% '
                commserve["cpuloadpercentage"] = cpuloadpercentage

                tmplist = []
                diskTotal=0
                freeSpace=0
                percent = 0
                for physical_disk in dd:
                    for partition in physical_disk.associators("Win32_DiskDriveToDiskPartition"):
                        for logical_disk in partition.associators("Win32_LogicalDiskToPartition"):
                            tmpdict = {}
                            tmpdict["Caption"] = logical_disk.Caption
                            tmpdict["DiskTotal"] = int(logical_disk.Size) / 1024 / 1024 / 1024
                            diskTotal +=int(logical_disk.Size) / 1024 / 1024 / 1024
                            tmpdict["FreeSpace"] = int(logical_disk.FreeSpace) / 1024 / 1024 / 1024
                            freeSpace += int(logical_disk.FreeSpace) / 1024 / 1024 / 1024
                            tmpdict["Percent"] = int(
                                100.0 * (int(logical_disk.Size) - int(logical_disk.FreeSpace)) / int(
                                    logical_disk.Size))
                            tmplist.append(tmpdict)
                try:
                    percent = (diskTotal-freeSpace)/diskTotal*100
                except:
                    pass
                commserve["disktotal"]= str(round(diskTotal,2))+'GB'
                commserve["diskutilization"] = str(round(percent, 2)) + '%'
            except Exception as e:
                pass

            frameworkdata["commserve"] = commserve

    return JsonResponse({
        "ret": 1,
        "data": frameworkdata,
    })

@login_required
def client_list(request, funid):
    util = request.GET.get("util", "")
    util_manages = UtilsManage.objects.exclude(state='9')
    try:
        util=int(util)
    except:
        pass


    return render(request, "client_list.html", {
        'username': request.user.userinfo.fullname,
        "pagefuns": getpagefuns(funid, request=request),
        "util_manages": util_manages,
        "util_id":util,
    })

@login_required
def sla(request, funid):
    util = request.GET.get("util", "")
    util_manages = UtilsManage.objects.exclude(state='9')
    try:
        util=int(util)
    except:
        pass


    return render(request, "sla.html", {
        'username': request.user.userinfo.fullname,
        "pagefuns": getpagefuns(funid, request=request),
        "util_manages": util_manages,
        "util_id":util,
    })


@login_required
def disk_space(request, funid):
    utils_manage = UtilsManage.objects.exclude(state='9').filter(util_type='Commvault')
    return render(request, 'disk_space.html', {
        'username': request.user.userinfo.fullname, 'utils_manage': utils_manage,
        "pagefuns": getpagefuns(funid, request=request)
    })


@login_required
def get_disk_space(request):
    # MA rowspan 总记录数
    # 库 rowspan 相同库记录数
    status = 1
    data = []
    info = ''
    utils_manage_id = request.POST.get('utils_manage_id', '')

    try:
        utils_manage_id = int(utils_manage_id)
        utils_manage = UtilsManage.objects.get(id=utils_manage_id)
    except:
        status = 0
        info = 'Commvault工具未配置。'
    else:
        _, sqlserver_credit = get_credit_info(utils_manage.content)
        try:
            dm = SQLApi.CVApi(sqlserver_credit)
            data = dm.get_library_space_info()
            dm.close()

            # 遍历所有记录 总记录数
            def get_rowspan(total_list, **kwargs):
                row_span = 0
                display_name = kwargs.get('DisplayName', '')
                library_name = kwargs.get('LibraryName', '')
                if all([display_name, library_name]):
                    for tl in total_list:
                        if tl['DisplayName'] == display_name and tl['LibraryName'] == library_name:
                            row_span += 1
                if display_name and not library_name:
                    for tl in total_list:
                        if tl['DisplayName'] == display_name:
                            row_span += 1
                return row_span

            for num, lsi in enumerate(data):
                display_name_rowspan = get_rowspan(data, DisplayName=lsi['DisplayName'])
                library_name_rowspan = get_rowspan(data, DisplayName=lsi['DisplayName'], LibraryName=lsi['LibraryName'])

                # 时间
                try:
                    data[num]["LastBackupTime"] = "{:%Y-%m-%d %H:%M:%S}".format(data[num]["LastBackupTime"])
                except Exception as e:
                    data[num]["LastBackupTime"] = ""
                # 是否可用
                if data[num]["Offline"] == 0:
                    data[num]["Offline"] = '<i class="fa fa-plug" style="color:green; height:20px;width:14px;"></i>'
                else:
                    data[num]["Offline"] = '<i class="fa fa-plug" style="color:red; height:20px;width:14px;"></i>'

                data[num]['display_name_rowspan'] = display_name_rowspan
                data[num]['library_name_rowspan'] = library_name_rowspan

        except Exception as e:
            print(e)
            status = 0
            info = '获取磁盘容量信息失败: {e}。'.format(e=e)
    return JsonResponse({
        "status": status,
        "info": info,
        "data": data
    })


@login_required
def get_disk_space_daily(request):
    disk_list = []

    media_id = request.POST.get("media_id", "")
    utils_id = request.POST.get("utils_id", "")

    try:
        media_id = int(media_id)
    except:
        pass
    try:
        utils_id = int(utils_id)
    except:
        pass
    if media_id:
        disk_space_weekly_data = DiskSpaceWeeklyData.objects.filter(utils_id=utils_id, media_id=media_id).values()
        capacity_available_list = []
        space_reserved_list = []
        total_space_list = []

        if disk_space_weekly_data:
            for num, dswd in enumerate(disk_space_weekly_data):
                if num > 20:
                    break

                capacity_available_list.append(round(dswd["capacity_avaible"] / 1024, 2))
                space_reserved_list.append(round(dswd["space_reserved"] / 1024, 2))
                total_space_list.append(round(dswd["total_space"] / 1024, 2))

            disk_list.append({
                "name": "可用容量",
                "color": "#3598dc",
                "capacity_list": capacity_available_list
            })
            disk_list.append({
                "name": "保留空间容量",
                "color": "#e7505a",
                "capacity_list": space_reserved_list
            })
            disk_list.append({
                "name": "总容量",
                "color": "#32c5d2",
                "capacity_list": total_space_list
            })
    else:
        # 总
        disk_space_weekly_data = DiskSpaceWeeklyData.objects.filter(utils_id=utils_id).values(
            "utils_id", "capacity_avaible", "space_reserved", "total_space", "point_tag"
        )
        capacity_available_list = []
        space_reserved_list = []
        total_space_list = []
        if disk_space_weekly_data:
            pre_point_tag = ""
            num = 0
            for dswd in disk_space_weekly_data:
                if num > 20:
                    break
                # util_id 与 相同记录的 数据相加
                if dswd["point_tag"] == pre_point_tag:
                    continue
                num += 1

                cur_disk_space_weekly_data = [i for i in disk_space_weekly_data if
                                              i["utils_id"] == utils_id and i["point_tag"] == dswd["point_tag"]]

                sum_capacity_avaible = 0
                sum_space_reserved = 0
                sum_total_space = 0
                for cdswd in cur_disk_space_weekly_data:
                    sum_capacity_avaible += cdswd["capacity_avaible"]
                    sum_space_reserved += cdswd["space_reserved"]
                    sum_total_space += cdswd["total_space"]

                capacity_available_list.append(round(sum_capacity_avaible / 1024, 2))
                space_reserved_list.append(round(sum_space_reserved / 1024, 2))
                total_space_list.append(round(sum_total_space / 1024, 2))

                pre_point_tag = dswd["point_tag"]
            disk_list.append({
                "name": "可用容量",
                "color": "#3598dc",
                "capacity_list": capacity_available_list
            })
            disk_list.append({
                "name": "保留空间容量",
                "color": "#e7505a",
                "capacity_list": space_reserved_list
            })
            disk_list.append({
                "name": "总容量",
                "color": "#32c5d2",
                "capacity_list": total_space_list
            })

    return JsonResponse({
        "data": disk_list,
    })


@login_required
def get_ma_disk_space(request):
    """
    获取总容量
    :param request:
    :return:
    """
    status = 1
    data = []
    info = ''
    utils_id = request.POST.get('utils_id', '')

    try:
        utils_id = int(utils_id)
        utils_manage = UtilsManage.objects.get(id=utils_id)
    except:
        status = 0
        info = 'Commvault工具未配置。'
    else:
        _, sqlserver_credit = get_credit_info(utils_manage.content)
        try:
            dm = SQLApi.CVApi(sqlserver_credit)
            ret = dm.get_library_space_info()
            dm.close()
            capacity_available = 0
            space_reserved = 0
            total_space = 0
            for r in ret:
                if type(r["CapacityAvailable"]) == int:
                    capacity_available += r["CapacityAvailable"]
                if type(r["SpaceReserved"]) == int:
                    space_reserved += r["SpaceReserved"]
                if type(r["TotalSpaceMB"]) == int:
                    total_space += r["TotalSpaceMB"]

            capacity_available_percent = round((capacity_available / total_space) * 100, 2)
            space_reserved_percent = round((space_reserved / total_space) * 100, 2)
            used_space_percent = round((100 - capacity_available_percent - space_reserved_percent), 2)
            data = {
                "capacity_available_percent": capacity_available_percent,
                "space_reserved_percent": space_reserved_percent,
                "used_space_percent": used_space_percent
            }
        except:
            pass
    return JsonResponse({
        "status": status,
        "info": info,
        "data": data
    })

