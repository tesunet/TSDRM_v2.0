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
                job_list = dm.display_error_job_list(startdate=startdate, enddate=enddate, jobstatus=jobstatus)
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
    jobstatus = request.GET.get('jobstatus', '')


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
                job_list = dm.display_error_job_list(startdate=startdate, enddate=enddate, jobstatus=jobstatus)

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