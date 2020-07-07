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

            for i in range(4):
                #先判断网络
                netresult = os.system(u'ping -n 1 ' + commvault_credit["webaddr"])
                if netresult == 0:
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
                            for i in range(4):
                                netresult = os.system(u'ping -n 1 ' + ma["InterfaceName"])
                                if netresult == 0:
                                    break;
                            else:
                                state=1
                        for ma in ma_info:
                            if ma["Offline"] == 0:
                                break
                            else:
                                state=2
                break;
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

            for i in range(4):
                #先判断网络
                netresult = os.system(u'ping -n 1 ' + commvault_credit["webaddr"])
                if netresult == 0:
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
                            for i in range(4):
                                netresult = os.system(u'ping -n 1 ' + ma["InterfaceName"])
                                if netresult == 0:
                                    ma["net"] = "正常"
                                    break;
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

                break;
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


    return render(request, "client_list.html", {
        'username': request.user.userinfo.fullname,
        "pagefuns": getpagefuns(funid, request=request),
        "util_manages": util_manages,
        "util_id":util,
    })