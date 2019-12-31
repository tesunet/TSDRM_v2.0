from __future__ import absolute_import
from celery import shared_task
import pymssql
from drm.models import *
from django.db import connection
from xml.dom.minidom import parse, parseString
from . import remote
from .models import *
import datetime
from django.db.models import Q
import time
import paramiko
import os
from TSDRM import settings
import json
from .api import SQLApi
import subprocess


@shared_task
def force_exec_script(processrunid):
    try:
        processrunid = int(processrunid)
    except ValueError as e:
        print("网络异常导致流程ID未传入, ", e)
    else:
        try:
            processrun = ProcessRun.objects.get(id=processrunid)
        except ProcessRun.DoesNotExist as e:
            print("流程不存在, ", e)
        else:
            all_step_runs = processrun.steprun_set.exclude(step__state="9").filter(step__force_exec=1)
            for steprun in all_step_runs:
                cur_step_scripts = steprun.scriptrun_set.all()
                for script in cur_step_scripts:
                    script.starttime = datetime.datetime.now()
                    script.result = ""
                    script.state = "RUN"
                    script.save()

                    # HostsManage
                    cur_host_manage = script.script.hosts_manage
                    ip = cur_host_manage.host_ip
                    username = cur_host_manage.username
                    password = cur_host_manage.password
                    system_tag = cur_host_manage.os

                    if system_tag in ["Linux", "AIX"]:
                        ############################
                        # 创建windows下目录:       #
                        #   先判断文件是否存在，再  #
                        #   mkdir/md path 创建文件 #
                        ############################
                        linux_temp_script_path = "/tmp/drm/{processrunid}".format(**{"processrunid": processrun.id})
                        mkdir_cmd = "mkdir -p {linux_temp_script_path}".format(
                            **{"linux_temp_script_path": linux_temp_script_path})
                        mkdir_obj = remote.ServerByPara(mkdir_cmd, ip, username, password, system_tag)
                        mkdir_result = mkdir_obj.run("")

                        # Linux系统创建文件夹失败
                        if mkdir_result["exec_tag"] == 1:
                            script.runlog = mkdir_result['log']  # 写入错误类型
                            script.explain = mkdir_result['data']
                            print("强制执行脚本时，Linux系统创建文件夹失败,结束任务!")
                            script.state = "ERROR"
                            script.save()
                            steprun.state = "ERROR"
                            steprun.save()

                        linux_temp_script_name = "tmp_script_{scriptrun_id}.sh".format(**{"scriptrun_id": script.id})
                        linux_temp_script_file = linux_temp_script_path + "/" + linux_temp_script_name

                        tmp_cmd = r"cat > {0} << \EOH".format(linux_temp_script_file) + "\n" + script.script.script_text + "\nEOH"
                        tmp_obj = remote.ServerByPara(tmp_cmd, ip, username, password, system_tag)
                        tmp_result = tmp_obj.run("")

                        if tmp_result["exec_tag"] == 1:
                            script.runlog = "强制执行脚本时，上传Linux脚本文件失败。"  # 写入错误类型
                            script.explain = "强制执行脚本时，上传Linux脚本文件失败：{0}。".format(tmp_result["data"])
                            script.state = "ERROR"
                            script.save()
                            steprun.state = "ERROR"
                            steprun.save()

                        exe_cmd = "chmod 777 {0}&&{0}".format(linux_temp_script_file)
                    else:
                        ############################
                        # 创建windows下目录:       #
                        #   先判断文件是否存在，再  #
                        #   mkdir/md path 创建文件 #
                        ############################
                        windows_temp_script_path = r"C:\drm\{processrunid}".format(**{"processrunid": processrun.id})
                        mkdir_cmd = "if not exist {windows_temp_script_path} mkdir {windows_temp_script_path}".format(
                            **{"windows_temp_script_path": windows_temp_script_path})
                        mkdir_obj = remote.ServerByPara(mkdir_cmd, ip, username, password, system_tag)
                        mkdir_result = mkdir_obj.run("")

                        # Windows系统创建文件夹失败
                        if mkdir_result["exec_tag"] == 1:
                            script.runlog = mkdir_result['log']  # 写入错误类型
                            script.explain = mkdir_result['data']
                            print("强制执行脚本时，Windows系统创建文件夹失败,结束任务!")
                            script.state = "ERROR"
                            script.save()
                            steprun.state = "ERROR"
                            steprun.save()

                        windows_temp_script_name = "tmp_script_{scriptrun_id}.bat".format(**{"scriptrun_id": script.id})
                        windows_temp_script_file = windows_temp_script_path + r"\\" + windows_temp_script_name
                        para_list = script.script.script_text.split("\n")
                        for num, content in enumerate(para_list):
                            tmp_cmd = ""
                            if num == 0:
                                tmp_cmd = r"""echo {0}>{1}""".format(content, windows_temp_script_file)
                            else:
                                tmp_cmd = r"""echo {0}>>{1}""".format(content, windows_temp_script_file)

                            tmp_obj = remote.ServerByPara(tmp_cmd, ip, username, password, system_tag)
                            tmp_result = tmp_obj.run("")

                            if tmp_result["exec_tag"] == 1:
                                script.runlog = "强制执行脚本时，上传windows脚本文件失败。"  # 写入错误类型
                                script.explain = "强制执行脚本时，上传windows脚本文件失败：{0}。".format(tmp_result["data"])
                                script.state = "ERROR"
                                script.save()
                                steprun.state = "ERROR"
                                steprun.save()

                        exe_cmd = windows_temp_script_file

                    # 执行文件
                    rm_obj = remote.ServerByPara(exe_cmd, ip, username, password, system_tag)
                    result = rm_obj.run(script.script.succeedtext)

                    script.endtime = datetime.datetime.now()
                    script.result = result['exec_tag']
                    script.explain = result['data']

                    # 处理脚本执行失败问题
                    if result["exec_tag"] == 1:
                        script.runlog = result['log']  # 写入错误类型
                        script.explain = result['data']
                        print("当前脚本执行失败,结束任务!")
                        script.state = "ERROR"
                        script.save()
                        steprun.state = "ERROR"
                        steprun.save()
                    else:
                        script.endtime = datetime.datetime.now()
                        script.state = "DONE"
                        script.save()

                        script_name = script.script.name if script.script.name else ""

                        myprocesstask = ProcessTask()
                        myprocesstask.processrun = steprun.processrun
                        myprocesstask.starttime = datetime.datetime.now()
                        myprocesstask.senduser = steprun.processrun.creatuser
                        myprocesstask.type = "INFO"
                        myprocesstask.logtype = "SCRIPT"
                        myprocesstask.state = "1"
                        myprocesstask.content = "强制执行脚本" + script_name + "完成。"
                        myprocesstask.save()


def runstep(steprun, if_repeat=False):
    """
    执行当前步骤下的所有脚本
    返回值0,：错误，1：完成，2：确认，3：流程已结束
    if_repeat用于避免已执行步骤重复执行。
    """
    # 判断该步骤是否已完成，如果未完成，先执行当前步骤
    processrun = ProcessRun.objects.filter(id=steprun.processrun.id)
    processrun = processrun[0]
    if processrun.state == "RUN" or processrun.state == "ERROR":
        # 将错误流程改成RUN
        processrun.state = "RUN"
        processrun.save()

        if steprun.state != "DONE":
            # 判断是否有子步骤，如果有，先执行子步骤
            # 取消错误消息展示
            all_done_tasks = ProcessTask.objects.exclude(state="1").filter(processrun_id=processrun.id,
                                                                           type="ERROR")
            for task in all_done_tasks:
                task.state = "1"
                task.save()

            if not if_repeat:
                steprun.starttime = datetime.datetime.now()  # 这个位置pnode的starttime存多次
            steprun.state = "RUN"
            steprun.save()

            children = steprun.step.children.order_by("sort").exclude(state="9")
            if len(children) > 0:
                for child in children:
                    childsteprun = child.steprun_set.exclude(state="9").filter(processrun=steprun.processrun)
                    if len(childsteprun) > 0:
                        childsteprun = childsteprun[0]
                        start_time = childsteprun.starttime
                        if start_time:
                            if_repeat = True
                        else:
                            if_repeat = False
                        childreturn = runstep(childsteprun, if_repeat)
                        if childreturn == 0:
                            return 0
                        if childreturn == 2:
                            return 2
            scriptruns = steprun.scriptrun_set.exclude(Q(state__in=("9", "DONE", "IGNORE")) | Q(result=0))
            for script in scriptruns:
                # 目的：不在服务器存放脚本；
                #   Linux：通过ssh上传文件至服务器端；执行脚本；删除脚本；
                #   Windows：通过>/>> 逐行重定向字符串至服务端文件；执行脚本；删除脚本；
                script.starttime = datetime.datetime.now()
                script.result = ""
                script.state = "RUN"
                script.save()

                if script.script.interface_type == "脚本":
                    # HostsManage
                    cur_host_manage = script.script.hosts_manage
                    ip = cur_host_manage.host_ip
                    username = cur_host_manage.username
                    password = cur_host_manage.password
                    system_tag = cur_host_manage.os

                    if system_tag in ["Linux", "AIX"]:
                        ############################
                        # 创建windows下目录:       #
                        #   先判断文件是否存在，再  #
                        #   mkdir/md path 创建文件 #
                        ############################
                        linux_temp_script_path = "/tmp/drm/{processrunid}".format(**{"processrunid": processrun.id})
                        mkdir_cmd = "mkdir -p {linux_temp_script_path}".format(
                            **{"linux_temp_script_path": linux_temp_script_path})
                        mkdir_obj = remote.ServerByPara(mkdir_cmd, ip, username, password, system_tag)
                        mkdir_result = mkdir_obj.run("")

                        # Linux系统创建文件夹失败
                        if mkdir_result["exec_tag"] == 1:
                            script.runlog = mkdir_result['log']  # 写入错误类型
                            script.explain = mkdir_result['data']
                            print("Linux系统创建文件夹失败,结束任务!")
                            script.state = "ERROR"
                            script.save()
                            steprun.state = "ERROR"
                            steprun.save()

                            script_name = script.script.name if script.script.name else ""
                            myprocesstask = ProcessTask()
                            myprocesstask.processrun = steprun.processrun
                            myprocesstask.starttime = datetime.datetime.now()
                            myprocesstask.senduser = steprun.processrun.creatuser
                            myprocesstask.receiveauth = steprun.step.group
                            myprocesstask.type = "ERROR"
                            myprocesstask.logtype = "SCRIPT"
                            myprocesstask.state = "0"
                            myprocesstask.content = "脚本" + script_name + "执行前创建文件夹失败，请处理。"
                            myprocesstask.steprun_id = steprun.id
                            myprocesstask.save()
                            return 0

                        linux_temp_script_name = "tmp_script_{scriptrun_id}.sh".format(**{"scriptrun_id": script.id})
                        linux_temp_script_file = linux_temp_script_path + "/" + linux_temp_script_name

                        tmp_cmd = r"cat > {0} << \EOH".format(linux_temp_script_file) + "\n" + script.script.script_text + "\nEOH"
                        tmp_obj = remote.ServerByPara(tmp_cmd, ip, username, password, system_tag)
                        tmp_result = tmp_obj.run("")

                        if tmp_result["exec_tag"] == 1:
                            script.runlog = "上传Linux脚本文件失败。"  # 写入错误类型
                            script.explain = "上传Linux脚本文件失败：{0}。".format(tmp_result["data"])
                            script.state = "ERROR"
                            script.save()
                            steprun.state = "ERROR"
                            steprun.save()

                            script_name = script.script.name if script.script.name else ""
                            myprocesstask = ProcessTask()
                            myprocesstask.processrun = steprun.processrun
                            myprocesstask.starttime = datetime.datetime.now()
                            myprocesstask.senduser = steprun.processrun.creatuser
                            myprocesstask.receiveauth = steprun.step.group
                            myprocesstask.type = "ERROR"
                            myprocesstask.logtype = "SCRIPT"
                            myprocesstask.state = "0"
                            myprocesstask.content = "脚本" + script_name + "内容写入失败，请处理。"
                            myprocesstask.steprun_id = steprun.id
                            myprocesstask.save()
                            return 0

                        exe_cmd = "chmod 777 {0}&&{0}".format(linux_temp_script_file)
                    else:
                        ############################
                        # 创建windows下目录:       #
                        #   先判断文件是否存在，再  #
                        #   mkdir/md path 创建文件 #
                        ############################
                        windows_temp_script_path = r"C:\drm\{processrunid}".format(**{"processrunid": processrun.id})
                        mkdir_cmd = "if not exist {windows_temp_script_path} mkdir {windows_temp_script_path}".format(
                            **{"windows_temp_script_path": windows_temp_script_path})
                        mkdir_obj = remote.ServerByPara(mkdir_cmd, ip, username, password, system_tag)
                        mkdir_result = mkdir_obj.run("")

                        # Windows系统创建文件夹失败
                        if mkdir_result["exec_tag"] == 1:
                            script.runlog = mkdir_result['log']  # 写入错误类型
                            script.explain = mkdir_result['data']
                            print("Windows系统创建文件夹失败,结束任务!")
                            script.state = "ERROR"
                            script.save()
                            steprun.state = "ERROR"
                            steprun.save()

                            script_name = script.script.name if script.script.name else ""
                            myprocesstask = ProcessTask()
                            myprocesstask.processrun = steprun.processrun
                            myprocesstask.starttime = datetime.datetime.now()
                            myprocesstask.senduser = steprun.processrun.creatuser
                            myprocesstask.receiveauth = steprun.step.group
                            myprocesstask.type = "ERROR"
                            myprocesstask.logtype = "SCRIPT"
                            myprocesstask.state = "0"
                            myprocesstask.content = "脚本" + script_name + "执行前创建文件夹失败，请处理。"
                            myprocesstask.steprun_id = steprun.id
                            myprocesstask.save()
                            return 0

                        windows_temp_script_name = "tmp_script_{scriptrun_id}.bat".format(**{"scriptrun_id": script.id})
                        windows_temp_script_file = windows_temp_script_path + r"\\" + windows_temp_script_name

                        para_list = script.script.script_text.split("\n")
                        for num, content in enumerate(para_list):
                            tmp_cmd = ""
                            if num == 0:
                                tmp_cmd = r"""echo {0}>{1}""".format(content, windows_temp_script_file)
                            else:
                                tmp_cmd = r"""echo {0}>>{1}""".format(content, windows_temp_script_file)

                            tmp_obj = remote.ServerByPara(tmp_cmd, ip, username, password, system_tag)
                            tmp_result = tmp_obj.run("")

                            if tmp_result["exec_tag"] == 1:
                                script.runlog = "上传windows脚本文件失败。"  # 写入错误类型
                                script.explain = "上传windows脚本文件失败：{0}。".format(tmp_result["data"])
                                script.state = "ERROR"
                                script.save()
                                steprun.state = "ERROR"
                                steprun.save()

                                script_name = script.script.name if script.script.name else ""
                                myprocesstask = ProcessTask()
                                myprocesstask.processrun = steprun.processrun
                                myprocesstask.starttime = datetime.datetime.now()
                                myprocesstask.senduser = steprun.processrun.creatuser
                                myprocesstask.receiveauth = steprun.step.group
                                myprocesstask.type = "ERROR"
                                myprocesstask.logtype = "SCRIPT"
                                myprocesstask.state = "0"
                                myprocesstask.content = "脚本" + script_name + "内容写入失败，请处理。"
                                myprocesstask.steprun_id = steprun.id
                                myprocesstask.save()
                                return 0

                        exe_cmd = windows_temp_script_file

                    # 执行文件
                    rm_obj = remote.ServerByPara(exe_cmd, ip, username, password, system_tag)
                    result = rm_obj.run(script.script.succeedtext)
                    script.endtime = datetime.datetime.now()
                    script.result = result['exec_tag']
                    script.explain = result['data']

                    # 处理脚本执行失败问题
                    if result["exec_tag"] == 1:
                        script.runlog = result['log']  # 写入错误类型
                        script.explain = result['data']
                        print("当前脚本执行失败,结束任务!")
                        script.state = "ERROR"
                        script.save()
                        steprun.state = "ERROR"
                        steprun.save()

                        script_name = script.script.name if script.script.name else ""
                        myprocesstask = ProcessTask()
                        myprocesstask.processrun = steprun.processrun
                        myprocesstask.starttime = datetime.datetime.now()
                        myprocesstask.senduser = steprun.processrun.creatuser
                        myprocesstask.receiveauth = steprun.step.group
                        myprocesstask.type = "ERROR"
                        myprocesstask.logtype = "SCRIPT"
                        myprocesstask.state = "0"
                        myprocesstask.content = "脚本" + script_name + "执行错误，请处理。"
                        myprocesstask.steprun_id = steprun.id
                        myprocesstask.save()
                        return 0

                else:
                    result = {}
                    commvault_api_path = os.path.join(os.path.join(settings.BASE_DIR, "drm"),
                                                      "commvault_api") + os.sep + script.script.commv_interface
                    ret = ""
                    print("################### %s" % commvault_api_path)
                    origin = script.script.origin.client_name if script.script.origin else ""
                    target = ""
                    if script.steprun.processrun.target:
                        target = script.steprun.processrun.target.client_name if script.steprun.processrun.target else ""
                    else:
                        target = script.script.target.client_name if script.script.target else ""
                    oracle_info = json.loads(script.script.origin.info)

                    instance = ""
                    if oracle_info:
                        instance = oracle_info["instance"]

                    oracle_param = "%s %s %s %d" % (origin, target, instance, processrun.id)
                    print("################### %s" % oracle_param)
                    try:
                        ret = subprocess.getstatusoutput(commvault_api_path + " %s" % oracle_param)
                        exec_status, recover_job_id = ret
                    except Exception as e:
                        result["exec_tag"] = 1
                        result["data"] = "执行commvault接口出现异常{0}。".format(e)
                        result["log"] = "执行commvault接口出现异常{0}。".format(e)
                    else:
                        if exec_status == 0:
                            result["exec_tag"] = 0
                            result["data"] = "调用commvault接口成功。"
                            result["log"] = "调用commvault接口成功。"
                        elif exec_status == 2:
                            #######################################
                            # ret=2时，查看任务错误信息写入日志    #
                            # Oracle恢复出错                      #
                            #######################################

                            # 查看Oracle恢复错误信息
                            dm = SQLApi.CustomFilter(settings.sql_credit)
                            job_controller = dm.get_job_controller()

                            recover_error = "无"

                            for jc in job_controller:
                                if str(recover_job_id) == str(jc["jobID"]):
                                    recover_error = jc["delayReason"]
                                    break

                            result["exec_tag"] = 2
                            # 查看任务错误信息写入>>result["data"]
                            result["data"] = recover_error
                            result["log"] = "Oracle恢复出错。"
                        else:
                            result["exec_tag"] = 1
                            result["data"] = recover_job_id
                            result["log"] = recover_job_id

                script.endtime = datetime.datetime.now()
                script.result = result['exec_tag']
                script.explain = result['data']

                # 处理接口调用执行失败问题
                if result["exec_tag"] == 1:
                    script.runlog = result['log']  # 写入错误类型
                    script.explain = result['data']
                    script.state = "ERROR"
                    script.save()
                    steprun.state = "ERROR"
                    steprun.save()

                    script_name = script.script.name if script.script.name else ""
                    myprocesstask = ProcessTask()
                    myprocesstask.processrun = steprun.processrun
                    myprocesstask.starttime = datetime.datetime.now()
                    myprocesstask.senduser = steprun.processrun.creatuser
                    myprocesstask.receiveauth = steprun.step.group
                    myprocesstask.type = "ERROR"
                    myprocesstask.logtype = "SCRIPT"
                    myprocesstask.state = "0"
                    myprocesstask.content = "接口" + script_name + "调用执行失败，请处理。"
                    myprocesstask.steprun_id = steprun.id
                    myprocesstask.save()
                    return 0
                # Oracle恢复失败问题
                if result["exec_tag"] == 2:
                    script.runlog = result['log']  # 写入错误类型
                    script.explain = result['data']
                    print("Oracle恢复失败,结束任务!")
                    script.state = "ERROR"
                    script.save()
                    steprun.state = "ERROR"
                    steprun.save()

                    script_name = script.script.name if script.script.name else ""
                    myprocesstask = ProcessTask()
                    myprocesstask.processrun = steprun.processrun
                    myprocesstask.starttime = datetime.datetime.now()
                    myprocesstask.senduser = steprun.processrun.creatuser
                    myprocesstask.receiveauth = steprun.step.group
                    myprocesstask.type = "ERROR"
                    myprocesstask.logtype = "SCRIPT"
                    myprocesstask.state = "0"
                    myprocesstask.content = "接口" + script_name + "调用过程中，Oracle恢复异常。"
                    myprocesstask.steprun_id = steprun.id
                    myprocesstask.save()
                    return 0

                script.endtime = datetime.datetime.now()
                script.state = "DONE"
                script.save()

                script_name = script.script.name if script.script.name else ""

                myprocesstask = ProcessTask()
                myprocesstask.processrun = steprun.processrun
                myprocesstask.starttime = datetime.datetime.now()
                myprocesstask.senduser = steprun.processrun.creatuser
                myprocesstask.type = "INFO"
                myprocesstask.logtype = "SCRIPT"
                myprocesstask.state = "1"
                myprocesstask.content = "接口" + script_name + "完成。"
                myprocesstask.save()

            if steprun.step.approval == "1" or steprun.verifyitemsrun_set.all():
                steprun.state = "CONFIRM"
                steprun.endtime = datetime.datetime.now()
                steprun.save()

                steprun_name = steprun.step.name if steprun.step.name else ""
                myprocesstask = ProcessTask()
                myprocesstask.processrun = steprun.processrun
                myprocesstask.starttime = datetime.datetime.now()
                myprocesstask.senduser = steprun.processrun.creatuser
                myprocesstask.receiveauth = steprun.step.group
                myprocesstask.logtype = "STEP"
                myprocesstask.type = "RUN"
                myprocesstask.state = "0"
                task_content = "步骤" + steprun_name + "等待确认，请处理。"
                myprocesstask.content = task_content
                myprocesstask.steprun_id = steprun.id

                myprocesstask.save()

                return 2
            else:
                steprun.state = "DONE"
                steprun.endtime = datetime.datetime.now()
                steprun.save()

                steprun_name = steprun.step.name if steprun.step.name else ""
                myprocesstask = ProcessTask()
                myprocesstask.processrun = steprun.processrun
                myprocesstask.starttime = datetime.datetime.now()
                myprocesstask.senduser = steprun.processrun.creatuser
                myprocesstask.type = "INFO"
                myprocesstask.logtype = "STEP"
                myprocesstask.state = "1"
                myprocesstask.content = "步骤" + steprun_name + "完成。"
                myprocesstask.save()

        nextstep = steprun.step.next.exclude(state="9")
        if len(nextstep) > 0:
            nextsteprun = nextstep[0].steprun_set.exclude(state="9").filter(processrun=steprun.processrun)
            if len(nextsteprun) > 0:
                # starttime存在，一级步骤不需要再次写入starttime
                nextsteprun = nextsteprun[0]
                start_time = nextsteprun.starttime

                if start_time:
                    if_repeat = True
                else:
                    if_repeat = False

                nextreturn = runstep(nextsteprun, if_repeat)

                if nextreturn == 0:
                    return 0
                if nextreturn == 2:
                    return 2

        return 1
    else:
        return 3


@shared_task
def exec_process(processrunid, if_repeat=False):
    """
    执行当前流程下的所有脚本
    """
    end_step_tag = 0
    processrun = ProcessRun.objects.filter(id=processrunid)
    processrun = processrun[0]

    # nextSCN-1
    # 获取流程客户端

    cur_client = processrun.origin
    dm = SQLApi.CustomFilter(settings.sql_credit)
    ret = dm.get_oracle_backup_job_list(cur_client)
    curSCN = None
    for i in ret:
        if i["subclient"] == "default":
            curSCN = i["cur_SCN"]
            break
    processrun.curSCN = curSCN
    processrun.save()

    steprunlist = StepRun.objects.exclude(state="9").filter(processrun=processrun, step__last=None, step__pnode=None)
    if len(steprunlist) > 0:
        end_step_tag = runstep(steprunlist[0], if_repeat)
    else:
        myprocesstask = ProcessTask()
        myprocesstask.processrun = processrun
        myprocesstask.starttime = datetime.datetime.now()
        myprocesstask.senduser = processrun.creatuser
        myprocesstask.receiveuser = processrun.creatuser
        myprocesstask.type = "ERROR"
        myprocesstask.state = "0"
        myprocesstask.content = "流程配置错误，请处理。"
        myprocesstask.save()
    if end_step_tag == 0:
        processrun.state = "ERROR"
        processrun.save()
    if end_step_tag == 1:
        processrun.state = "DONE"
        processrun.endtime = datetime.datetime.now()
        processrun.save()
        myprocesstask = ProcessTask()
        myprocesstask.processrun = processrun
        myprocesstask.starttime = datetime.datetime.now()
        myprocesstask.senduser = processrun.creatuser
        myprocesstask.type = "INFO"
        myprocesstask.logtype = "END"
        myprocesstask.state = "1"
        myprocesstask.content = "流程结束。"
        myprocesstask.save()

        # ************************ 写入RTO *************************
        cur_process = processrun.process

        # 正确顺序的父级Step
        all_pnode_steps = cur_process.step_set.exclude(state="9").filter(pnode_id=None).order_by("sort")

        correct_step_id_list = []

        for pnode_step in all_pnode_steps:
            correct_step_id_list.append(pnode_step)

        # 正确顺序的父级StepRun
        correct_step_run_list = []

        for pnode_step in correct_step_id_list:
            current_step_run = pnode_step.steprun_set.filter(processrun_id=processrun.id)
            if current_step_run.exists():
                current_step_run = current_step_run[0]
                correct_step_run_list.append(current_step_run)
        starttime = processrun.starttime
        rtoendtime = processrun.starttime

        for c_step_run in reversed(correct_step_run_list):
            if c_step_run.step.rto_count_in == "1":
                rtoendtime = c_step_run.endtime
                break

        delta_time = 0
        if rtoendtime:
            delta_time = (rtoendtime - starttime).total_seconds()

        processrun.rto = delta_time
        processrun.save()


@shared_task
def create_process_run(*args, **kwargs):
    """
    创建计划流程
    :param process:
    :return:
    """
    # exec_process.delay(processrunid)
    # data_path/target/origin/
    origin_name, target_id, data_path, copy_priority, db_open = "", None, "", 1, 1
    try:
        process_id = int(kwargs["cur_process"])
    except ValueError as e:
        pass
    else:
        try:
            cur_process = Process.objects.get(id=process_id)
        except Process.DoesNotExist as e:
            pass
        else:
            # 过滤所有脚本
            all_steps = cur_process.step_set.exclude(state="9")
            for cur_step in all_steps:
                all_scripts = cur_step.script_set.exclude(state="9")
                for cur_script in all_scripts:
                    if cur_script.origin:
                        origin_name = cur_script.origin.client_name
                        data_path = cur_script.origin.data_path
                        copy_priority = cur_script.origin.copy_priority
                        db_open = cur_script.origin.db_open
                        if cur_script.origin.target:
                            target_id = cur_script.origin.target.id
                        break

            # running_process = ProcessRun.objects.filter(process=cur_process, state__in=["RUN", "ERROR"])
            running_process = ProcessRun.objects.filter(process=cur_process, state__in=["RUN"])
            if running_process.exists():
                myprocesstask = ProcessTask()
                myprocesstask.starttime = datetime.datetime.now()
                myprocesstask.type = "INFO"
                myprocesstask.logtype = "END"
                myprocesstask.state = "0"
                myprocesstask.processrun = running_process[0]
                myprocesstask.content = "计划流程({0})已运行或者错误流程未处理，无法按计划创建恢复流程任务。".format(running_process[0].process.name)
                myprocesstask.save()
                # result["res"] = '流程启动失败，该流程正在进行中，请勿重复启动。'
            else:
                myprocessrun = ProcessRun()
                myprocessrun.creatuser = kwargs["creatuser"]
                myprocessrun.process = cur_process
                myprocessrun.starttime = datetime.datetime.now()
                myprocessrun.state = "RUN"
                myprocessrun.target_id = target_id
                myprocessrun.data_path = data_path
                myprocessrun.copy_priority = copy_priority
                myprocessrun.db_open = db_open
                myprocessrun.origin = origin_name
                myprocessrun.save()
                mystep = cur_process.step_set.exclude(state="9")
                if not mystep.exists():
                    myprocesstask = ProcessTask()
                    myprocesstask.starttime = datetime.datetime.now()
                    myprocesstask.type = "INFO"
                    myprocesstask.logtype = "END"
                    myprocesstask.state = "0"
                    myprocesstask.processrun = myprocessrun
                    myprocesstask.content = "计划流程({0})不存在可运行步骤，无法按计划创建恢复流程任务。".format(myprocessrun.process.name)
                    myprocesstask.save()
                    # result["res"] = '流程启动失败，没有找到可用步骤。'
                else:
                    for step in mystep:
                        mysteprun = StepRun()
                        mysteprun.step = step
                        mysteprun.processrun = myprocessrun
                        mysteprun.state = "EDIT"
                        mysteprun.save()

                        myscript = step.script_set.exclude(state="9")
                        for script in myscript:
                            myscriptrun = ScriptRun()
                            myscriptrun.script = script
                            myscriptrun.steprun = mysteprun
                            myscriptrun.state = "EDIT"
                            myscriptrun.save()

                    myprocesstask = ProcessTask()
                    myprocesstask.processrun = myprocessrun
                    myprocesstask.starttime = datetime.datetime.now()
                    myprocesstask.type = "INFO"
                    myprocesstask.logtype = "START"
                    myprocesstask.state = "1"
                    myprocesstask.content = "流程已启动。"
                    myprocesstask.save()

                    exec_process.delay(myprocessrun.id)
