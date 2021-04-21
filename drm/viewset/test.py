# 基础平台：知识库、登录相关、首页、通讯录
import uuid

from django.shortcuts import render
from django.contrib import auth
from django.http import HttpResponseRedirect, Http404, HttpResponse, JsonResponse
from django.http import StreamingHttpResponse
from django.utils.encoding import escape_uri_path
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required

from TSDRM import settings
from drm.api.commvault import SQLApi
from drm.api.commvault.RestApi import *
from .public_func import *
from ..workflow.workflow import *
from ..tasks import *

######################
# 首页
######################


def test(request):
    newJob = Job(userid=request.user.id)
    aa = newJob.execute_workflow('2e445090-a26c-11eb-bc9a-405bd8b00cd6',
                                  input=[{"code": "ip", "value": "www.baidu.com"}])
    print(aa)

    # 虚机给电：b1d51880-9751-11eb-afc2-a4bb6d10e0ef
    # 虚机断电：a55d4a56-9791-11eb-b36d-000c29921d27
    # 虚机重启：35017fd4-9796-11eb-9ff7-000c29921d27
    # 虚机关闭：101e2c5e-9795-11eb-9921-000c29921d27
    # 虚机列表：73c5e79c-979a-11eb-ac18-000c29921d27
    # 虚机暂停：7db3a31e-980f-11eb-91cc-000c29921d27
    # 虚机唤醒：9f1a12d0-9810-11eb-b3de-000c29921d27
    # 虚机信息：0cf3fd1e-9813-11eb-a964-000c29921d27
    # 虚机克隆：6bab5454-9815-11eb-bc7a-000c29921d27
    # 虚机删除：75d3413e-9799-11eb-b4e8-000c29921d27

    # zfs池列表：3ca9b7be-9841-11eb-b1bb-000c29921d27
    # zfs池删除：3d9f523a-984d-11eb-9309-000c29921d27
    # zfs池创建：c0f1ce72-984a-11eb-8ba1-000c29921d27
    # zfs文件系统：68bfdaa4-9864-11eb-81bb-000c29921d27
    # 文件系统创建：4c8c68c4-986a-11eb-ba10-000c29921d27

    # 虚机注册：10825768-98d7-11eb-b09f-000c29921d27
    # 虚机模板：0f298100-9b31-11eb-849b-000c29921d27
    # 宿主机资源监控：cc4e507c-9b35-11eb-b93f-000c29921d27
    # 虚机资源消耗情况:798bbe14-98d4-11eb-9499-000c29921d27
    # 虚机硬件信息修改: 689d7bb0-98d4-11eb-9997-000c29921d27
    # 资源监控：f8352306-9b6b-11eb-a25e-000c29921d27
    # 虚机激活：9a33ff3a-9b65-11eb-8467-000c29921d27
    # ZFS文件系统删除：81fd30e4-9b83-11eb-9827-000c29921d27
    # ZFS快照列表：9d8a3c02-9b84-11eb-a739-000c29921d27
    # ZFS快照创建：38a25fa8-9bf3-11eb-b2e2-000c29921d27
    # ZFS快照删除：83ef27de-9bf8-11eb-b70c-000c29921d27
    # ZFS快照克隆列表：cfd97018-9bf9-11eb-8a6c-000c29921d27
    # ZFS快照克隆创建：d3d7fc4e-9c07-11eb-b0a5-000c29921d27
    # ZFS快照克隆删除：b8c57ac6-9c0c-11eb-a6c3-000c29921d27
    # ZFS文件系统创建：4c8c68c4-986a-11eb-ba10-000c29921d27
    # print(newJob.execute_workflow('3ca9b7be-9841-11eb-b1bb-000c29921d27',
    #                               input=[{"code": "username", "value": 'root'},
    #                                      {"code": "password", "value": "tesunet@2019"},
    #                                      {"code": "ip", "value": "192.168.1.61"},
    #                                      ]))

    print(newJob.finalOutput)
    print(newJob.jobBaseInfo['log'])


    return render(request, 'test.html')


def tsdrmstart1(request):
    # testJob = Job()
    # jobJson = {}
    # jobJson["createuser"] = 1
    # jobJson["name"] = '测试任务'
    # jobJson["reson"] = '测试'
    # jobJson["type"] = 'INSTANCE'
    # aa = datetime.datetime.now()
    # jobJson["modelguid"] = 'd19e3a02-44d0-11eb-b557-84fdd1a17907'
    # jobJson["input"] = '<inputs><input><code>inputnum</code><value>1</value></input></inputs>'
    #testJob.create_job(jobJson)
    #testJob.get_job('ff395b2e-454c-11eb-8c53-000c29c81d38')

    TSDRMJob.objects.exclude(id=1).delete()
    testJob = Job('ff395b2e-454c-11eb-8c53-000c29c81d38')
    testJob.run_job()
    return HttpResponse(0)

def tsdrmstart2(request):
    # testJob = Job()
    # jobJson = {}
    # jobJson["createuser"] = 1
    # jobJson["name"] = '测试任务'
    # jobJson["reson"] = '测试'
    # jobJson["type"] = 'INSTANCE'
    # aa = datetime.datetime.now()
    # jobJson["modelguid"] = 'd19e3a02-44d0-11eb-b557-84fdd1a17907'
    # jobJson["input"] = '<inputs><input><code>inputnum</code><value>1</value></input></inputs>'
    #testJob.create_job(jobJson)
    #testJob.get_job('ff395b2e-454c-11eb-8c53-000c29c81d38')

    # testJob = Job('ff395b2e-454c-11eb-8c53-000c29c81d38')
    # testJob.run_job()
    TSDRMJob.objects.exclude(id=1).delete()
    run_workflow.delay('ff395b2e-454c-11eb-8c53-000c29c81d38','start')
    return HttpResponse(0)

def tsdrmstop(request):
    testJob = Job('ff395b2e-454c-11eb-8c53-000c29c81d38')
    testJob.stop_job()
    return HttpResponse(0)

def tsdrmpause(request):
    testJob = Job('ff395b2e-454c-11eb-8c53-000c29c81d38')
    testJob.pause_job()
    return HttpResponse(0)

def tsdrmretry1(request):
    testJob = Job('ff395b2e-454c-11eb-8c53-000c29c81d38')
    testJob.retry_job()
    return HttpResponse(0)

def tsdrmretry2(request):
    run_workflow.delay('ff395b2e-454c-11eb-8c53-000c29c81d38','retry')
    return HttpResponse(0)

