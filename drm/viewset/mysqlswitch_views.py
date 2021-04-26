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


def mysqlswitch(request, funid):
    return render(request, 'mysqlswitch.html',
                  {'username': request.user.userinfo.fullname,
                   "pagefuns": getpagefuns(funid, request=request),
                   "is_superuser": request.user.is_superuser
                   })


@login_required
def check_master_network(request):
    """
    检查主库的网络是否畅通
    state:  状态
    info:   错误信息
    code：  错误状态码 0失败，1成功
    """
    info = '必要参数缺失'
    code = 0
    user = request.POST.get('user', '')
    mip = request.POST.get('mip', '')
    password = request.POST.get('password', '')
    if user.strip() and mip.strip() and password.strip():
        component_guid = '2e445090-a26c-11eb-bc9a-405bd8b00cd6'
        component_input = [{"code": "inputusername", "value": user},
                           {"code": "inputhost", "value": mip},
                           {"code": "inputpassword", "value": password}]

        newJob = Job()
        state = newJob.execute_workflow(component_guid, input=component_input)

        if state == 'NOTEXIST':
            info = "组件不存在,请联系管理员。"
            code = 0
        elif state == 'ERROR':
            info = "ERROR"
            code = 0
        else:
            info = "网络正常。"
            code = 1
    return JsonResponse({
        "info": info,
        "code": code
    })

@login_required
def check_master_dbstate(request):
    """
    检查主数据库状态
    """
    info = '必要参数缺失'
    code = 0
    user = request.POST.get('user', '')
    mip = request.POST.get('mip', '')
    password = request.POST.get('password', '')
    dbuser = request.POST.get('dbuser', '')
    dbpassword = request.POST.get('dbpassword', '')
    if user.strip() and mip.strip() and password.strip() and dbuser.strip() and dbpassword.strip():
        component_guid = '2e445090-a26c-11eb-bc9a-405bd8b00cd6'
        component_input = [{"code": "inputusername", "value": user},
                           {"code": "inputhost", "value": mip},
                           {"code": "dbusername", "value": dbuser},
                           {"code": "dbpassword", "value": dbpassword}]

        newJob = Job()
        state = newJob.execute_workflow(component_guid, input=component_input)

        if state == 'NOTEXIST':
            info = "组件不存在,请联系管理员。"
            code = 0
        elif state == 'ERROR':
            info = "ERROR"
            code = 0
        else:
            info = "数据库状态正常。"
            code = 1
    return JsonResponse({
        "info": info,
        "code": code
    })