# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from djcelery import models as djmodels


class Fun(models.Model):
    pnode = models.ForeignKey('self', blank=True, null=True, related_name='children', verbose_name='父节点')
    name = models.CharField("功能名称", max_length=100)
    sort = models.IntegerField("排序", blank=True, null=True)
    type = models.CharField("类型", blank=True, null=True, max_length=20)
    url = models.CharField("地址", blank=True, null=True, max_length=500)
    icon = models.CharField("图标", blank=True, null=True, max_length=100)


class Group(models.Model):
    name = models.CharField("组名", blank=True, null=True, max_length=50)
    fun = models.ManyToManyField(Fun)
    remark = models.TextField("说明", blank=True, null=True)
    state = models.CharField("状态", blank=True, null=True, max_length=20)
    sort = models.IntegerField("排序", blank=True, null=True)


class UserInfo(models.Model):
    user = models.OneToOneField(User, blank=True, null=True, )
    userGUID = models.CharField("GUID", null=True, max_length=50)
    fullname = models.CharField("姓名", blank=True, max_length=50)
    phone = models.CharField("电话", blank=True, null=True, max_length=50)
    group = models.ManyToManyField(Group)
    pnode = models.ForeignKey('self', blank=True, null=True, related_name='children', verbose_name='父节点')
    type = models.CharField("类型", blank=True, null=True, max_length=20)
    state = models.CharField("状态", blank=True, null=True, max_length=20)
    sort = models.IntegerField("排序", blank=True, null=True)
    remark = models.TextField("说明", blank=True, null=True)
    company = models.CharField("公司", blank=True, null=True, max_length=100)
    tell = models.CharField("电话", blank=True, null=True, max_length=50)
    forgetpassword = models.CharField("修改密码地址", blank=True, null=True, max_length=50)


class Process(models.Model):
    code = models.CharField("预案编号", blank=True, max_length=50)
    name = models.CharField("预案名称", blank=True, max_length=50)
    remark = models.TextField("预案描述", blank=True, null=True)
    sign = models.CharField("是否签到", blank=True, null=True, max_length=20)
    rto = models.IntegerField("RTO", blank=True, null=True)
    rpo = models.IntegerField("RPO", blank=True, null=True)
    state = models.CharField("状态", blank=True, null=True, max_length=20)
    sort = models.IntegerField("排序", blank=True, null=True)
    url = models.CharField("页面链接", blank=True, max_length=100)
    type = models.CharField("预案类型", blank=True, max_length=100, null=True)
    color = models.CharField("颜色", blank=True, max_length=50)


class Step(models.Model):
    process = models.ForeignKey(Process)
    last = models.ForeignKey('self', blank=True, null=True, related_name='next', verbose_name='上一步')
    pnode = models.ForeignKey('self', blank=True, null=True, related_name='children', verbose_name='父节点')
    code = models.CharField("步骤编号", blank=True, null=True, max_length=50)
    name = models.CharField("步骤名称", blank=True, null=True, max_length=50)
    approval = models.CharField("是否审批", blank=True, null=True, max_length=10)
    skip = models.CharField("能否跳过", blank=True, null=True, max_length=10)
    group = models.CharField("角色", blank=True, null=True, max_length=50)
    time = models.IntegerField("预计耗时", blank=True, null=True)
    state = models.CharField("状态", blank=True, null=True, max_length=10)
    sort = models.IntegerField("排序", blank=True, null=True)
    rto_count_in = models.CharField("是否算入RTO", blank=True, null=True, max_length=10, default="1")
    remark = models.CharField("备注", blank=True, null=True, max_length=500, help_text="告知业务人员灾备环境地址等信息")
    force_exec_choices = (
        (1, "是"),
        (2, "否")
    )
    force_exec = models.IntegerField("流程关闭时强制执行", choices=force_exec_choices, null=True, default=2)


# 客户端管理
class Target(models.Model):
    client_id = models.IntegerField("终端client_id", blank=True, null=True)
    client_name = models.CharField("终端client_name", blank=True, null=True, max_length=128)
    info = models.TextField("客户端相关信息", blank=True, null=True)
    state = models.CharField("状态", blank=True, null=True, max_length=20)
    os = models.CharField("系统", blank=True, null=True, max_length=50)


class Origin(models.Model):
    target = models.ForeignKey(Target, blank=True, null=True, verbose_name="默认关联终端")
    client_id = models.IntegerField("源端client_id", blank=True, null=True)
    client_name = models.CharField("源端client_name", blank=True, null=True, max_length=128)
    info = models.TextField("客户端相关信息", blank=True, null=True)
    state = models.CharField("状态", blank=True, null=True, max_length=20)
    os = models.CharField("系统", blank=True, null=True, max_length=50)
    copy_priority_choices = (
        (1, "主拷贝"),
        (2, "辅助拷贝")
    )
    copy_priority = models.IntegerField(
        "拷贝优先级：1：主拷贝；2：辅助拷贝", blank=True, null=True, default=1, choices=copy_priority_choices)
    data_path = models.CharField("数据文件重定向路径", blank=True, default="", max_length=512)
    db_open_choices = (
        (1, "是"),
        (2, "否")
    )
    db_open = models.IntegerField(
        "是否恢复完成后打开数据库：1：默认打开数据库；2：不打开数据库", null=True, default=1, choices=db_open_choices)


class HostsManage(models.Model):
    host_ip = models.CharField("主机IP", blank=True, null=True, max_length=50)
    host_name = models.CharField("主机名称", blank=True, null=True, max_length=256)
    os = models.CharField("系统", blank=True, null=True, max_length=50)
    type = models.CharField("连接类型", blank=True, null=True, max_length=20)
    username = models.CharField("用户名", blank=True, null=True, max_length=50)
    password = models.CharField("密码", blank=True, null=True, max_length=50)
    state = models.CharField("状态", blank=True, null=True, max_length=20)


class Script(models.Model):
    hosts_manage = models.ForeignKey(HostsManage, blank=True, null=True, verbose_name='主机管理')
    step = models.ForeignKey(Step, blank=True, null=True)
    code = models.CharField("脚本编号", blank=True, max_length=50)
    name = models.CharField("脚本名称", blank=True, max_length=500)
    filename = models.CharField("脚本文件名", blank=True, null=True, max_length=50)
    scriptpath = models.CharField("脚本文件路径", blank=True, null=True, max_length=100)
    state = models.CharField("状态", blank=True, null=True, max_length=20)
    sort = models.IntegerField("排序", blank=True, null=True)
    succeedtext = models.CharField("成功代码", blank=True, null=True, max_length=500)
    log_address = models.CharField("日志地址", blank=True, null=True, max_length=100)
    script_text = models.TextField("脚本内容", blank=True, default="")
    # commvault接口
    interface_type = models.CharField("日志地址", blank=True, null=True, max_length=32)
    origin = models.ForeignKey(Origin, blank=True, null=True, verbose_name='源端客户端')
    commv_interface = models.CharField("commvault接口脚本", blank=True, null=True, max_length=64)


class ProcessRun(models.Model):
    process = models.ForeignKey(Process)
    starttime = models.DateTimeField("开始时间", blank=True, null=True)
    endtime = models.DateTimeField("结束时间", blank=True, null=True)
    creatuser = models.CharField("发起人", blank=True, max_length=50)
    state = models.CharField("状态", blank=True, null=True, max_length=20)
    run_reason = models.TextField("启动原因", blank=True, null=True)
    note = models.TextField("记录", blank=True, null=True)
    target = models.ForeignKey(Target, blank=True, null=True, verbose_name="oracle恢复流程指定目标客户端")
    recover_time = models.DateTimeField("指定恢复时间点", blank=True, null=True)
    browse_job_id = models.CharField("指点时间点的备份任务ID", blank=True, null=True, max_length=50)
    data_path = models.CharField("数据重定向路径", blank=True, null=True, max_length=512)
    copy_priority = models.IntegerField("优先拷贝顺序", blank=True, default=1, null=True)
    origin = models.CharField("源客户端", blank=True, null=True, max_length=256)
    curSCN = models.BigIntegerField("当前备份nextSCN-1", blank=True, null=True)
    db_open = models.IntegerField("是否打开数据库", default=1, null=True)

    rto = models.IntegerField("流程RTO", default=0, null=True)


class StepRun(models.Model):
    step = models.ForeignKey(Step, blank=True, null=True)
    processrun = models.ForeignKey(ProcessRun, blank=True, null=True)
    starttime = models.DateTimeField("开始时间", blank=True, null=True)
    endtime = models.DateTimeField("结束时间", blank=True, null=True)
    operator = models.CharField("操作人", blank=True, null=True, max_length=50)
    parameter = models.CharField("运行参数", blank=True, null=True, max_length=500)
    result = models.TextField("运行结果", blank=True, null=True)
    explain = models.TextField("运行说明", blank=True, null=True)
    state = models.CharField("状态", blank=True, null=True, max_length=20)
    note = models.TextField("记录", blank=True, null=True)


class ScriptRun(models.Model):
    script = models.ForeignKey(Script, blank=True, null=True)
    steprun = models.ForeignKey(StepRun, blank=True, null=True)
    starttime = models.DateTimeField("开始时间", blank=True, null=True)
    endtime = models.DateTimeField("结束时间", blank=True, null=True)
    operator = models.CharField("操作人", blank=True, null=True, max_length=50)
    result = models.TextField("运行结果", blank=True, null=True)
    explain = models.TextField("运行说明", blank=True, null=True)
    runlog = models.TextField("运行日志", blank=True, null=True)
    state = models.CharField("状态", blank=True, null=True, max_length=20)
    note = models.TextField("记录", blank=True, null=True)


class ProcessTask(models.Model):
    processrun = models.ForeignKey(ProcessRun, blank=True, null=True)
    steprun = models.ForeignKey(StepRun, blank=True, null=True)
    starttime = models.DateTimeField("发送时间", blank=True, null=True)
    senduser = models.CharField("发送人", blank=True, null=True, max_length=50)
    receiveuser = models.CharField("接收人", blank=True, null=True, max_length=50)
    receiveauth = models.CharField("接收角色", blank=True, null=True, max_length=50)
    operator = models.CharField("操作人", blank=True, null=True, max_length=50)
    endtime = models.DateTimeField("处理时间", blank=True, null=True)
    type = models.CharField("任务类型", blank=True, null=True, max_length=20)
    content = models.TextField("任务内容", blank=True, null=True)
    state = models.CharField("状态", blank=True, null=True, max_length=20)
    result = models.TextField("处理结果", blank=True, null=True)
    explain = models.TextField("处理说明", blank=True, null=True)
    logtype = models.CharField("日志类型", blank=True, null=True, max_length=20)


class VerifyItems(models.Model):
    step = models.ForeignKey(Step, blank=True, null=True)
    name = models.CharField("确认项", blank=True, null=True, max_length=50)
    state = models.CharField("状态", blank=True, null=True, max_length=30)


class VerifyItemsRun(models.Model):
    verify_items = models.ForeignKey(VerifyItems)
    steprun = models.ForeignKey(StepRun, blank=True, null=True)
    state = models.CharField("状态", blank=True, null=True, max_length=30)
    has_verified = models.CharField("是否确认", blank=True, null=True, max_length=20)


class Invitation(models.Model):
    process_run = models.OneToOneField(ProcessRun, blank=True, null=True)
    start_time = models.DateTimeField("开始时间", blank=True, null=True)
    end_time = models.DateTimeField("结束时间", blank=True, null=True)
    purpose = models.TextField("演练目的", blank=True, null=True)
    current_time = models.DateTimeField("邀请时间", blank=True, null=True)


class KnowledgeFileDownload(models.Model):
    """
    知识库
    """
    person = models.CharField("上传人", blank=True, null=True, max_length=64)
    upload_time = models.DateTimeField("上传时间", blank=True, null=True)
    remark = models.CharField("备注", blank=True, null=True, max_length=500)
    file_name = models.CharField("文件名称", blank=True, null=True, max_length=128)
    state = models.CharField("状态", blank=True, null=True, max_length=20)


class Vendor(models.Model):
    content = models.TextField("内容", blank=True, null=True)


class ProcessSchedule(models.Model):
    dj_periodictask = models.OneToOneField(djmodels.PeriodicTask, null=True, verbose_name="定时任务")
    process = models.ForeignKey(Process, null=True, verbose_name="流程预案")
    name = models.CharField("流程计划名称", blank=True, null=True, max_length=256)
    remark = models.TextField("计划说明", null=True, blank=True)
    state = models.CharField("状态", blank=True, null=True, max_length=20)
    schedule_type_choices = (
        (1, "每日"),
        (2, "每周"),
        (3, "每月"),
    )
    schedule_type = models.IntegerField(choices=schedule_type_choices, default=1, null=True)

