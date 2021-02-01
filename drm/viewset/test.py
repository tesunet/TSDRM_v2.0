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

