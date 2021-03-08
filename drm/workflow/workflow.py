from ..models import *
import uuid
import datetime
from lxml import etree
import decimal
import json
import xmltodict
from .public import *
import time


# 流程类/控件类/组件类
class WorkFlow(object):
    def __init__(self, type, guid=None,userid=None):
        self.workflowType = type
        self.workflowGuid = guid
        self.workflowBaseInfo = None
        self.workflow = None
        self.massage = ""
        # 实例化传入guid时，从数据库中查找，guid为None时，视为新建
        if self.workflowGuid and len(self.workflowGuid.strip()) > 0:
            self.get_workflow(self.workflowGuid)

    # 获取流程
    def get_workflow(self,workflowGuid):
        """
        根据guid从数据库中获取数据，赋值给workflowBaseInfo
        """
        self.workflow = None
        if self.workflowType == "WORKFLOW":
            self.workflow = TSDRMWorkflow.objects.exclude(state="9").filter(guid=workflowGuid).first()
        if self.workflowType == "CONTROL":
            self.workflow = TSDRMControl.objects.exclude(state="9").filter(guid=workflowGuid).first()
        if self.workflowType == "COMPONENT":
            self.workflow = TSDRMComponent.objects.exclude(state="9").filter(guid=workflowGuid).first()
        if self.workflow is not None:
            # 基础属性
            self.workflowBaseInfo = {}
            self.workflowBaseInfo["id"] = self.workflow.id
            self.workflowBaseInfo["createtime"] = self.workflow.createtime
            self.workflowBaseInfo["updatetime"] = self.workflow.updatetime
            self.workflowBaseInfo["createuser"] = self.workflow.createuser_id
            try:
                self.workflowBaseInfo["createusername"] = self.workflow.createuser.userinfo.fullname
            except:
                pass
            self.workflowBaseInfo["updateuser"] = self.workflow.updateuser_id
            try:
                self.workflowBaseInfo["updateusername"] = self.workflow.updateuser.userinfo.fullname
            except:
                pass
            self.workflowBaseInfo["longname"] = self.workflow.longname
            self.workflowBaseInfo["shortname"] = self.workflow.shortname
            self.workflowBaseInfo["type"] = self.workflow.type
            self.workflowBaseInfo["owner"] = self.workflow.owner
            groups=self.workflow.group.all()
            grouplist = []
            for curgroup in groups:
                grouplist.append(curgroup.id)
            self.workflowBaseInfo["group"] = grouplist
            self.workflowBaseInfo["pnode"] = self.workflow.pnode_id
            self.workflowBaseInfo["icon"] = self.workflow.icon
            self.workflowBaseInfo["version"] = self.workflow.version
            self.workflowBaseInfo["attribute"] = self.workflow.attribute
            self.workflowBaseInfo["input"] = self.workflow.input
            self.workflowBaseInfo["output"] = self.workflow.output
            self.workflowBaseInfo["variable"] = self.workflow.variable
            self.workflowBaseInfo["remark"] = self.workflow.remark
            self.workflowBaseInfo["sort"] = self.workflow.sort
            self.workflowBaseInfo["state"] = self.workflow.state
            if self.workflowType == "WORKFLOW":
                self.workflowBaseInfo["content"] = self.workflow.content
            if self.workflowType == "CONTROL":
                self.workflowBaseInfo["controlclass"] = self.workflow.controlclass
            if self.workflowType == "COMPONENT":
                self.workflowBaseInfo["language"] = self.workflow.language
                self.workflowBaseInfo["code"] = self.workflow.code
        else:
            self.massage = 'error(get_workflow):流程' + workflowGuid + '不存在'

    def set_workflow(self, jsonFromPage):
        """
        获取页面数据并赋值给workflowBaseInfo
        """
        if self.workflowGuid is None:
            self.workflowGuid = uuid.uuid1()
        self.workflowBaseInfo.creattime = jsonFromPage.creattime
        self.workflowBaseInfo.updatetime = jsonFromPage.updatetime
        self.workflowBaseInfo.creatuser = jsonFromPage.creatuser
        self.workflowBaseInfo.updateuser = jsonFromPage.updateuser
        self.workflowBaseInfo.longname = jsonFromPage.longname
        self.workflowBaseInfo.shortname = jsonFromPage.shortname
        self.workflowBaseInfo.type = jsonFromPage.type
        self.workflowBaseInfo.owner = jsonFromPage.owner
        self.workflowBaseInfo.pnode = jsonFromPage.pnode
        self.workflowBaseInfo.icon = jsonFromPage.icon
        self.workflowBaseInfo.version = jsonFromPage.version
        self.workflowBaseInfo.remark = jsonFromPage.remark
        self.workflowBaseInfo.sort = jsonFromPage.sort
        self.workflowBaseInfo.state = jsonFromPage.state
        self.workflowBaseInfo.visible = jsonFromPage.visible
        self.workflowBaseInfo.variables = jsonFromPage.variables
        self.workflowBaseInfo.inputs = jsonFromPage.inputs
        self.workflowBaseInfo.outputs = jsonFromPage.outputs
        self.workflowBaseInfo.steps = jsonFromPage.steps

    # 保存流程
    def save_workflow(self):
        """
        将workflowBaseInfo中数据保存到数据库
        """
        if self.workflowGuid is None:
            self.massage='error(save_workflow):流程未初始化'
        else:
            if self.workflow is None:
                if self.workflowType == "WORKFLOW":
                    self.workflow = TSDRMWorkflow()
                if self.workflowType == "CONTROL":
                    self.workflow = TSDRMControl()
                if self.workflowType == "COMPONENT":
                    self.workflow = TSDRMComponent()
            self.workflow.guid = self.workflowGuid
            self.workflow.creattime = self.workflowBaseInfo["creattime"]
            self.workflow.updatetime = self.workflowBaseInfo["updatetime"]
            self.workflow.creatuser_id = self.workflowBaseInfo["creatuser"]
            self.workflow.updateuser_id = self.workflowBaseInfo["updateuser"]
            self.workflow.longname = self.workflowBaseInfo["longname"]
            self.workflow.shortname = self.workflowBaseInfo["shortname"]
            self.workflow.type = self.workflowBaseInfo["type"]
            self.workflow.owner = self.workflowBaseInfo["owner"]
            self.workflow.pnode_id = self.workflowBaseInfo["pnode"]
            self.workflow.icon = self.workflowBaseInfo["icon"]
            self.workflow.version = self.workflowBaseInfo["version"]
            self.workflow.remark = self.workflowBaseInfo["remark"]
            self.workflow.sort = self.workflowBaseInfo["sort"]
            self.workflow.state = self.workflowBaseInfo["state"]
            self.workflow.visible = self.workflowBaseInfo["visible"]
            self.workflow.variables = self.workflowBaseInfo["variables"]
            self.workflow.inputs = self.workflowBaseInfo["inputs"]
            self.workflow.outputs = self.workflowBaseInfo["outputs"]
            self.workflow.steps = self.workflowBaseInfo["steps"]
            if self.workflowType == "WORKFLOW":
                self.workflow.content = self.workflowBaseInfo["content"]
            if self.workflowType == "CONTROL":
                self.workflow.controlclass = self.workflowBaseInfo["controlclass"]
            if self.workflowType == "COMPONENT":
                self.workflow.language = self.workflowBaseInfo["language"]
                self.workflow.code = self.workflowBaseInfo["code"]
            if self.workflow.save():
                groupmsg=""
                for curgroup in self.workflowBaseInfo["group"]:
                    try:
                        group = int(curgroup)
                        mygroup = Group.objects.exclude(state="9").get(id=group)
                        self.workflow.group.add(mygroup)
                    except Exception:
                        groupmsg+="，角色" + group + "授权失败"
                self.massage='success(save_workflow):保存成功' + groupmsg
            else:
                self.massage='error(save_workflow):保存失败'

    # 删除流程
    def del_workflow(self):
        if self.workflowGuid is None:
            self.massage = 'error(del_workflow):流程未初始化'
        else:
            if self.workflowType == "WORKFLOW":
                workflow_del = TSDRMWorkflow.objects.exclude(state="9").filter(
                    guid=self.workflowGuid)
            if self.workflowType == "CONTROL":
                workflow_del = TSDRMControl.objects.exclude(state="9").filter(
                    guid=self.workflowGuid)
            if self.workflowType == "COMPONENT":
                workflow_del = TSDRMComponent.objects.exclude(state="9").filter(
                    guid=self.workflowGuid)
            if len(workflow_del)>0:
                workflow_del.state='9'
                workflow_del.save()
                self.massage = 'success(del_workflow):删除成功'
            else:
                self.massage = 'error(del_workflow):流程' + self.workflowGuid + '不存在'

# 实例类
class Instance(WorkFlow):
    def __init__(self, instance_guid=None,workflow_guid=None,userid=None):
        self.instanceGuid = instance_guid
        self.instanceBaseInfo = None
        self.instance = None
        if workflow_guid is None and instance_guid is None:
            self.massage = 'error(Instance):参数错误,workflow_guid和instance_guid必须传递一个'
        elif self.instanceGuid and len(self.instanceGuid.strip()) > 0:
            self.get_instance(self.instanceGuid)
        else:
            super().__init__("WORKFLOW", workflow_guid)

        # 获取实例

    def get_instance(self,instanceGuid):
        self.instance = None
        self.instance = TSDRMInstance.objects.exclude(state="9").filter(guid=instanceGuid).first()
        if self.instance is not None:
            # 基础属性
            super().__init__("WORKFLOW", self.instance.workflow.guid)
            self.instanceBaseInfo = {}
            self.instanceBaseInfo["id"] = self.instance.id
            self.instanceBaseInfo["createtime"] = self.instance.createtime
            self.instanceBaseInfo["updatetime"] = self.instance.updatetime
            self.instanceBaseInfo["createuser"] = self.instance.createuser_id
            try:
                self.instanceBaseInfo["createusername"] = self.instance.createuser.userinfo.fullname
            except:
                pass
            self.instanceBaseInfo["updateuser"] = self.instance.updateuser_id
            try:
                self.instanceBaseInfo["updateusername"] = self.instance.updateuser.userinfo.fullname
            except:
                pass
            self.instanceBaseInfo["workflow"] = self.instance.workflow_id
            self.instanceBaseInfo["name"] = self.instance.name
            self.instanceBaseInfo["type"] = self.instance.type
            groups = self.workflow.group.all()
            grouplist = []
            for curgroup in groups:
                grouplist.append(curgroup.id)
            self.instanceBaseInfo["group"] = grouplist
            self.instanceBaseInfo["pnode"] = self.instance.pnode_id
            self.instanceBaseInfo["instancetype"] = self.instance.instancetype
            self.instanceBaseInfo["loglevel"] = self.instance.loglevel
            self.instanceBaseInfo["monitorable"] = self.instance.monitorable
            self.instanceBaseInfo["sync"] = self.instance.sync
            self.instanceBaseInfo["input"] = self.instance.input
            self.instanceBaseInfo["remark"] = self.instance.remark
            self.instanceBaseInfo["sort"] = self.instance.sort
            self.instanceBaseInfo["state"] = self.instance.state
        else:
            self.massage = 'error(get_instance):实例' + instanceGuid + '不存在'

    # 设置实例
    def set_instance(self, jsonFromPage):
        pass

    # 保存实例
    def save_instance(self):
        pass

    # 删除实例
    def del_instance(self):
        pass

# 任务类
class Job(object):
    """
    任务类，包含：
    1.job的增删改查部分：init、get、create、save
    2.job的运行部分：运行任务、执行控件、执行组件、执行流程、运行步骤、运行下一步、流程结束
    3.参数传递部分：子任务的输出更新到父任务、获取输入参数值、获取内部变量、格式化参数、转换数据类型
    4.进程控制部分：重试/继续步骤、跳过步骤、中止任务、暂停任务、暂停任务-修改任务状态
    5.控件部分：开始、结束、if、for、break
    6.公式解析部分：待丰富
    """


    #######################################################
    # job的增删改查部分 #
    #######################################################

    def __init__(self,job_guid=None,userid=None):
        """
        初始化任务，当job_guid不为None时，从数据库获得job信息；当job_guid空缺时，建一个空实例。

        Args:
            job_guid (string): 任务guid，空缺时创建一个空实例
            userid (string): 用户id，用于create和update时记录操作人信息

        Returns:
            无
        """
        self.userid = userid
        self.jobGuid = job_guid
        self.jobModelguid = None
        self.jobType = None
        # 父任务
        self.pnode = None
        #模型实例
        self.jobModel = None
        #任务信息
        self.jobBaseInfo = None
        #任务数据库对象
        self.job = None
        #每一步骤的输出参数及值
        self.jobStepOutput=[]
        #内部参数及值
        self.jobVariable = []
        #输入参数及值。input与finalInput的区别：input仅仅包含流程启动时输入的参数，finalInput则包含流程配置里的全部input参数，并根据配置从不同来源获取实际值。
        self.finalInput = []
        #输出参数及值
        self.finalOutput = []
        # 实例化传入guid时，从数据库中查找，guid为None时，视为新建
        if self.jobGuid and len(self.jobGuid.strip()) > 0:
            self.get_job(self.jobGuid)

    # 获取任务信息
    def get_job(self,jobGuid):
        """
        根据jobGuid从数据库中获取数据。

        1.从数据库中获取基础数据，存入jobBaseInfo.
        2.jobBaseInfo["pjob"]不为空且pnode为空时，说明当前job有父任务，需赋值父任务.
        3.解析XML获得jobStepOutput（每步的输出数据）.
        4.获得jobVariable（内部变量值）.
        5.获得finalInput（全部输入参数值）.
        6.获得finalOutput（全部输出参数值）.

        Args:
            jobGuid (string): 任务guid

        Returns:
            无
        """
        self.job = None
        self.job = TSDRMJob.objects.exclude(state="9").filter(guid=jobGuid).first()
        if self.job is not None:
            self.jobType = self.job.type
            self.jobModelguid = self.job.modelguid
            if self.jobType=='INSTANCE':
                self.jobModel = Instance(self.job.modelguid,userid=self.userid)
            else:
                self.jobModel = WorkFlow(self.jobType,self.job.modelguid,self.userid)

            # 基础属性
            self.jobBaseInfo = {}
            self.jobBaseInfo["id"] = self.job.id
            self.jobBaseInfo["createtime"] = self.job.createtime
            self.jobBaseInfo["updatetime"] = self.job.updatetime
            self.jobBaseInfo["starttime"] = self.job.starttime
            self.jobBaseInfo["createuser"] = self.job.createuser_id
            try:
                self.jobBaseInfo["createusername"] = self.job.createuser.userinfo.fullname
            except:
                pass
            self.jobBaseInfo["updateuser"] = self.job.updateuser_id
            try:
                self.jobBaseInfo["updateusername"] = self.job.updateuser.userinfo.fullname
            except:
                pass
            self.jobBaseInfo["startuser"] = self.job.startuser_id
            try:
                self.jobBaseInfo["startusername"] = self.job.startuser.userinfo.fullname
            except:
                pass
            self.jobBaseInfo["name"] = self.job.name
            self.jobBaseInfo["reson"] = self.job.reson
            self.jobBaseInfo["pjob"] = self.job.pjob_id
            self.jobBaseInfo["step"] = self.job.step
            self.jobBaseInfo["type"] = self.job.type
            self.jobBaseInfo["modelguid"] = self.job.modelguid
            self.jobBaseInfo["schedule"] = self.job.schedule_id
            self.jobBaseInfo["input"] = self.job.input
            self.jobBaseInfo["endtime"] = self.job.endtime
            if self.job.log is None:
                self.jobBaseInfo["log"] = ""
            else:
                self.jobBaseInfo["log"] = self.job.log
            self.jobBaseInfo["state"] = self.job.state
            # 获得父任务
            if self.jobBaseInfo["pjob"] is not None and self.pnode is None:
                pnode = TSDRMJob.objects.filter(id=self.jobBaseInfo["pjob"])
                if len(pnode)>0:
                    self.pnode = Job(pnode[0].guid)

            #获得jobStepOutput
            if self.job.jobstepoutput and len(self.job.jobstepoutput.strip()) > 0:
                tmpDTL = xmltodict.parse(self.job.jobstepoutput)
                if "stepoutputs" in tmpDTL and tmpDTL["stepoutputs"] and "stepoutput" in tmpDTL["stepoutputs"] and tmpDTL["stepoutputs"]["stepoutput"]:
                    tmpDTL = tmpDTL["stepoutputs"]["stepoutput"]
                    if str(type(tmpDTL)) == "<class 'collections.OrderedDict'>":
                        tmpDTL = [tmpDTL]
                    for curstepoutput in tmpDTL:
                        if "output" in curstepoutput and curstepoutput["output"]:
                            curstepoutput = curstepoutput["output"]
                            if str(type(curstepoutput)) == "<class 'collections.OrderedDict'>":
                                curstepoutput = [curstepoutput]
                                curstepoutput = self._changeType(curstepoutput)
                    self.jobStepOutput = tmpDTL
            # 获得jobVariable
            if self.job.jobvariable and len(self.job.jobvariable.strip()) > 0:
                tmpDTL = xmltodict.parse(self.job.jobvariable)
                if "variables" in tmpDTL and tmpDTL["variables"] and "variable" in tmpDTL["variables"] and tmpDTL["variables"]["variable"]:
                    tmpDTL = tmpDTL["variables"]["variable"]
                    if str(type(tmpDTL)) == "<class 'collections.OrderedDict'>":
                        tmpDTL = [tmpDTL]
                    self.jobVariable = self._changeType(tmpDTL)
            # 获得finalInput
            if self.job.finalinput and len(self.job.finalinput.strip()) > 0:
                tmpDTL = xmltodict.parse(self.job.finalinput)
                if "inputs" in tmpDTL and tmpDTL["inputs"] and "input" in tmpDTL["inputs"] and tmpDTL["inputs"]["input"]:
                    tmpDTL = tmpDTL["inputs"]["input"]
                    if str(type(tmpDTL)) == "<class 'collections.OrderedDict'>":
                        tmpDTL = [tmpDTL]
                    self.finalInput = self._changeType(tmpDTL)
            # 获得finalOutput
            if self.job.output and len(self.job.output.strip()) > 0:
                tmpDTL = xmltodict.parse(self.job.output)
                if "outputs" in tmpDTL and tmpDTL["outputs"] and "output" in tmpDTL["outputs"] and tmpDTL["outputs"]["output"]:
                    tmpDTL = tmpDTL["outputs"]["output"]
                    if str(type(tmpDTL)) == "<class 'collections.OrderedDict'>":
                        tmpDTL = [tmpDTL]
                    self.finalOutput = self._changeType(tmpDTL)
        else:
            self.massage = 'error(get_job):任务' + jobGuid + '不存在'

    # 新建任务
    def create_job(self,jobJson,pnode=None):
        """
        根据jobJson创建任务。

        1.初始化job.
        2.赋值pnode.
        3.创建数据库对象并保存.
        4.获取任务信息.

        Args:
            jobJson (dict): 任务基本信息，可包含type(必需，且只能为INSTANCE/CONTROL/COMPONENT/WORKFLOW)、modelguid(必需)、name、reson、schedule、input.
            pnode(Job):父级任务

        Returns:
            无
        """

        #初始化job
        self.jobGuid = None
        self.jobModelguid = None
        self.jobType = None
        self.jobBaseInfo = None
        self.job = None
        self.jobStepOutput = []
        self.jobVariable = []
        self.finalInput = []
        self.finalOutput = []

        #赋值pnode
        self.pnode = pnode
        if "type" not in jobJson:
            self.massage = 'error(create_job):jobJson需包含type元素'
        elif jobJson["type"]!='INSTANCE' and jobJson["type"]!='CONTROL' and jobJson["type"]!='COMPONENT' and jobJson["type"]!='WORKFLOW':
            self.massage = 'error(create_job):jobJson["type"]只能为INSTANCE、CONTROL、COMPONENT、WORKFLOW'
        elif "modelguid" not in jobJson or jobJson["modelguid"] is None:
            self.massage = 'error(create_job):jobJson需包含modelguid元素且不为空'
        else:
            try:
                #创建数据库对象并保存
                self.job = TSDRMJob()
                self.job.guid = uuid.uuid1()
                self.job.createtime = datetime.datetime.now()
                self.job.updatetime = datetime.datetime.now()
                if self.userid:
                    self.job.createuser_id = self.userid
                    self.job.updateuser_id = self.userid
                if "name" in jobJson:
                    self.job.name = jobJson["name"]
                if "reson" in jobJson:
                    self.job.reson = jobJson["reson"]
                if self.pnode is not None:
                    self.job.pjob_id = self.pnode.jobBaseInfo["id"]
                if "step" in jobJson:
                    self.job.step = jobJson["step"]
                if "type" in jobJson:
                    self.job.type = jobJson["type"]
                if "modelguid" in jobJson:
                    self.job.modelguid = jobJson["modelguid"]
                if "schedule" in jobJson:
                    self.job.schedule_id = jobJson["schedule"]
                if "input" in jobJson:
                    self.job.input = jobJson["input"]
                self.job.log=""
                self.job.save()
                self.jobGuid = self.job.guid
                #获取任务信息
                self.get_job(self.jobGuid)
            except Exception as e:
                self.massage = 'error(create_job):创建任务失败'

    # 保存任务
    def save_job(self):
        """
        保存任务，将jobBaseInfo中数据保存到数据库.

        Returns:
            无
        """

        self.job.updatetime = datetime.datetime.now()
        if self.userid:
            self.job.updateuser_id = self.userid

        self.job.startuser_id = self.jobBaseInfo["startuser"]
        self.job.starttime = self.jobBaseInfo["starttime"]
        self.job.endtime = self.jobBaseInfo["endtime"]
        self.job.log = self.jobBaseInfo["log"]
        self.job.state = self.jobBaseInfo["state"]

        #将jobStepOutput、jobVariable、finalInput、finalOutput转化成xml格式
        self.job.jobstepoutput = xmltodict.unparse({"stepoutputs":{"stepoutput":self.jobStepOutput}}, encoding='utf-8')
        self.job.jobvariable = xmltodict.unparse({"variables":{"variable":self.jobVariable}}, encoding='utf-8')
        self.job.finalinput = xmltodict.unparse({"inputs":{"input":self.finalInput}}, encoding='utf-8')
        self.job.output = xmltodict.unparse({"outputs":{"output":self.finalOutput}}, encoding='utf-8')
        self.job.save()

    #######################################################
    # job的运行部分 #
    #######################################################

    # 运行任务
    def run_job(self):
        """
        运行当前任务，根据任务模板的类型不同，分别运行流程、控件、组件。

        1.调用_getInput方法，初始化finalInput。input与finalInput的区别：input仅仅包含流程启动时输入的参数，finalInput则包含流程配置里的全部input参数，并根据配置从不同来源获取实际值。
        2.调用_getVariable方法，初始化内部参数变量
        3.初始化后保存任务
        4.根据类型(流程、控件、组件)执行任务，run_workflow，run_control，run_component
        5.任务完成保存任务
        6.返回执行结果

        Returns:
            state(string):任务运行结果状态
        """
        if self.jobGuid is None:
            self.jobBaseInfo["log"] += 'error(run_job):任务未初始化'
            self.jobBaseInfo["state"] = "ERROR"
        else:
            self.jobBaseInfo["starttime"] = datetime.datetime.now()
            self.jobBaseInfo["startuser"] = self.userid
            self.jobBaseInfo["state"] = "RUN"
            #1、调用_getInput方法，初始化finalInput。input与finalInput的区别：input仅仅包含流程启动时输入的参数，finalInput则包含流程配置里的全部input参数，并根据配置从不同来源获取实际值。
            self._getInput()
            #2、调用_getVariable方法，初始化内部参数变量
            self._getVariable()
            #3、初始化后保存任务
            self.save_job()
            #4、根据类型(流程、控件、组件)执行任务，run_workflow，run_control，run_component
            if self.jobModel.workflowType == "WORKFLOW":
                self.run_workflow()
            elif self.jobModel.workflowType == "CONTROL":
                self.run_control()
            elif self.jobModel.workflowType == "COMPONENT":
                self.run_component()
            else:
                self.jobBaseInfo["log"] += 'error(run_job):workflowType配置错误'
                self.jobBaseInfo["state"] = "ERROR"
        #6.任务运行完成后保存任务
        self.save_job()
        return self.jobBaseInfo["state"]

    # 执行控件
    def run_control(self):
        """
        运行控件任务，根据controlclass字段内容，执行对应方法。

        1.找到controlclass字段内容，并执行对应方法.
        2.将执行结果状态存入self.jobBaseInfo["state"].
        当前控件为for循环控件时，需做特殊处理，for控件执行一次循环后，如果计数未满，需要等待下一次，此时应该把状态改为WAIT而非DONE.
        for计数是否结束存在控件的output["code"]中，为True时，循环结束

        Returns:
            无
        """
        if self.jobModel.workflowBaseInfo["controlclass"] and len(self.jobModel.workflowBaseInfo["controlclass"].strip()) > 0:
            try:
                #找到controlclass字段内容，并执行对应方法
                exec("self._control_" + self.jobModel.workflowBaseInfo["controlclass"] + "()")
            except:
                self.jobBaseInfo["log"] += 'error(run_control)控件执行失败'
                self.jobBaseInfo["state"] = "ERROR"
                return
        #2.如果是循环控件，判断循环是否结束,未结束状态改为WAIT,结束改为DONE
        isRunLoop = False
        if self.jobModelguid =="0aa259dc-50ad-11eb-a8a3-84fdd1a17907":
            if len(self.finalOutput) > 0:
                for output in self.finalOutput:
                    if output["code"] == "result":
                        if output["value"]==False:
                            isRunLoop = True
                        break
        if isRunLoop:
            self.jobBaseInfo["state"] = "WAIT"
        else:
            self.jobBaseInfo["state"] = "DONE"
            self.jobBaseInfo["endtime"] = datetime.datetime.now()
        print(self.jobBaseInfo["name"] + ":")
        print(self.finalOutput)

    # 执行组件
    def run_component(self):
        """
        运行组件任务，根据脚本类型(language)和脚本内容(code)字段，执行脚本。

        1.定义组件componentInput和componentOutput，于脚本进行输入输出交互.
        2.根据类型执行组件代码，目前只写了python类型。组件code中，直接把输出参数值写到componentOutput对应的键上.
        3.将componentOutput写到任务的finalOutput中
        4.将执行结果状态存入self.jobBaseInfo["state"].

        Returns:
            无
        """

        #1.定义组件componentInput和componentOutput，于脚本进行输入输出交互.
        #time.sleep(10)
        componentInput = {}
        for input in self.finalInput:
            componentInput[input["code"]] = input["value"]
        componentOutput = {}
        #2.根据类型执行组件代码，目前只写了python类型。组件code中，直接把输出参数值写到componentOutput对应的键上.
        if self.jobModel.workflowBaseInfo["language"]=="python":
            componentCode=self.jobModel.workflowBaseInfo["code"]
            try:
                exec(componentCode)
                if "system_state" in componentOutput and componentOutput["system_state"]=="ERROR":
                    self.jobBaseInfo["state"] = "ERROR"
                    if "system_log" in componentOutput:
                        self.jobBaseInfo["log"] += componentOutput["system_log"]
                    else:
                        self.jobBaseInfo["log"] += 'error(run_component)组件代码执行失败,返回错误状态。'
                    return
            except Exception as e:
                self.jobBaseInfo["log"] += 'error(run_component)组件代码执行失败。'+ str(e)
                self.jobBaseInfo["state"] = "ERROR"
                return
        #3.将componentOutput写到任务的finalOutput中
        if self.jobModel.workflowBaseInfo["output"] and len(self.jobModel.workflowBaseInfo["output"].strip()) > 0:
            tmpDTL = xmltodict.parse(self.jobModel.workflowBaseInfo["output"])
            if "outputs" in tmpDTL and tmpDTL["outputs"] and "output" in tmpDTL["outputs"] and tmpDTL["outputs"]["output"]:
                tmpDTL = tmpDTL["outputs"]["output"]
                #xmltodict会将只有一条记录的output转成OrderedDict，而我们需要的时list，需转化下
                if str(type(tmpDTL)) == "<class 'collections.OrderedDict'>":
                    tmpDTL = [tmpDTL]
                self.finalOutput = tmpDTL

                for output in self.finalOutput:
                    if output["code"] in componentOutput:
                        output.update({'value':componentOutput[output["code"]]})
        #将执行结果状态存入self.jobBaseInfo["state"].
        self.jobBaseInfo["state"]="DONE"
        self.jobBaseInfo["endtime"] = datetime.datetime.now()

        print(self.jobBaseInfo["name"] + ":")
        print(self.finalOutput)

    # 执行流程
    def run_workflow(self):
        """
        找到流程的开始步骤，运行开始步骤，开始运行步骤完成，会自动执行下一步骤。

        1.解析workflow的content字段，找出开始步骤modelguid='ef81b0de-44cc-11eb-9c38-84fdd1a17907'
        2.执行开始步骤,并将返回的执行结果状态存入self.jobBaseInfo["state"]

        Returns:
            无
        """
        print('*----------------------------------------——*')
        print("<<" + self.jobBaseInfo["name"] + ">>")
        print('输入:')
        print(self.finalInput)
        print('*---------------——*')

        xml = etree.fromstring(self.jobModel.workflowBaseInfo["content"])
        #1.解析workflow的content字段，找出开始步骤modelguid='ef81b0de-44cc-11eb-9c38-84fdd1a17907'
        startStep = xml.xpath("//modelguid[text()='ef81b0de-44cc-11eb-9c38-84fdd1a17907'][1]/parent::*/parent::*")
        if len(startStep) > 0:
            #2.执行开始步骤
            self.jobBaseInfo["state"] = self._run_step(etree.tostring(startStep[0]).decode('utf-8'))
        else:
            self.jobBaseInfo["log"] += 'error(run_job)未配置开始步骤'
            self.jobBaseInfo["state"] = "ERROR"
        print('*---------------——*')
        print('输出:')
        print(self.finalOutput)
        print('*----------------------------------------——*')

    # 运行步骤
    def _run_step(self,step):
        """
        执行步骤，并继续下一步。每一个步骤都视为单独一个子任务。

        1.获得步骤信息
        2.当前步骤为for循环控件时，需做特殊处理。for控件执行一次循环后，并未结束，而是需要等待下次计数。
        因此，判断需执行的步骤是否为未完成的for循环，如果是，查找for步骤的信息；如果不是，创建并运行步骤任务
        2.1未完成的循环步骤直接运行控件代码
        2.2其他步骤创建并运行步骤任务
        3.将步骤运行结果写入主任务的步骤输出jobStepOutput和内部参数jobVariable中
        4.完成一个步骤后保存任务
        5.如果任务运行成功，运行下一步，否则直接返回状态

        Args:
            step (string): xml格式的步骤信息

        Returns:
            state(string):任务运行结果状态
        """
        returnState = ""
        stepJob=Job(userid=self.userid)
        jobJson = {}
        curStep = xmltodict.parse(step)

        if "step" in step and "baseInfo" in curStep["step"] and curStep["step"]["baseInfo"] and "stepid" in curStep["step"]["baseInfo"] and curStep["step"]["baseInfo"]["stepid"] and len(curStep["step"]["baseInfo"]["stepid"].strip()) and curStep["step"]["baseInfo"]["modelguid"] and len(curStep["step"]["baseInfo"]["modelguid"].strip()) and curStep["step"]["baseInfo"]["modelType"] and len(curStep["step"]["baseInfo"]["modelType"].strip()) > 0:
            #1.获得步骤信息
            jobJson["modelguid"] = curStep["step"]["baseInfo"]["modelguid"]
            jobJson["type"] = curStep["step"]["baseInfo"]["modelType"]
            jobJson["step"] = curStep["step"]["baseInfo"]["stepid"]
            jobJson["name"] = curStep["step"]["baseInfo"]["name"]
            #2.判断需执行的步骤是否为正在运行中的for循环，如果是，查找for步骤的信息；如果不是，创建并运行步骤任务
            isRunLoop=False
            if curStep["step"]["baseInfo"]["modelguid"]=="0aa259dc-50ad-11eb-a8a3-84fdd1a17907":
                loopJobList = self.job.children.filter(state__in=["RUN","WAIT"],modelguid="0aa259dc-50ad-11eb-a8a3-84fdd1a17907",step=curStep["step"]["baseInfo"]["stepid"])
                if len(loopJobList) > 0:
                    isRunLoop=True
            if isRunLoop:
                #2.1已存在的循环步骤直接运行控件代码
                stepJob.get_job(loopJobList[0].guid)
                stepJob.jobBaseInfo["state"] = "RUN"
                stepJob.save_job()
                stepJob.run_control()
                returnState = stepJob.jobBaseInfo["state"]
                stepJob.save_job()
            else:
                #2.2创建并运行步骤任务
                if "inputs" in curStep["step"] and curStep["step"]["inputs"] and"input" in curStep["step"]["inputs"] and curStep["step"]["inputs"]["input"]:
                    tmpDTL = curStep["step"]["inputs"]["input"]
                    # xmltodict会将只有一条记录的input转成OrderedDict，而我们需要的时list，需转化下
                    if str(type(tmpDTL)) == "<class 'collections.OrderedDict'>":
                        tmpDTL = [tmpDTL]
                    # 给步骤的input赋值
                    stepInput = self._sourceToValue(tmpDTL)
                    stepInput = {"inputs":{"input":stepInput}}
                    jobJson["input"] = xmltodict.unparse(stepInput,encoding='utf-8')
                stepJob.create_job(jobJson,self)
                returnState = stepJob.run_job()
            # 3.将步骤运行结果写入主任务的步骤输出jobStepOutput和内部参数jobVariable中
            self._update_stepOutput(curStep,stepJob.finalOutput)
        else:
            self.jobBaseInfo["log"] += 'error(_run_step)步骤信息错误'
            self.jobBaseInfo["state"] = "ERROR"
        #4.完成一个步骤后保存任务
        self.save_job()

        #5.如果任务运行成功，运行下一步，否则直接返回状态
        if returnState=="DONE" or returnState=="WAIT":
            returnState = self._run_nextStep(curStep,stepJob.finalOutput)
        return returnState

    # 运行下一步
    def _run_nextStep(self, curStep,stepOutput):
        """
        运行下一步

        1.判断是否为结束步骤modelguid=='69255378-44ce-11eb-9203-84fdd1a17907'，如果是执行2，如果不是执行3
        2.结束任务
        3.根据step中的line查找下一步
        4.解析line的条件criteria，判断条件是否成立
        5.执行下一步

        Args:
            curStep (dict): dict格式的上一步骤信息
            stepOutput(dict):上一步骤的任务输出

        Returns:
            无
        """
        returnState = self.jobBaseInfo["state"]
        #1.判断是否为结束步骤modelguid=='69255378-44ce-11eb-9203-84fdd1a17907'，如果是执行2，如果不是执行3
        if curStep["step"]["baseInfo"]["modelguid"]=='69255378-44ce-11eb-9203-84fdd1a17907':
            #2.结束任务
            returnState = self._end_workflow()
        else:
            #3.根据step中的line查找下一步
            if "step" in curStep and "lines" in curStep["step"] and "line" in curStep["step"]["lines"] and len(curStep["step"]["lines"]["line"]) > 0:
                tmpDTL = curStep["step"]["lines"]["line"]
                # xmltodict会将只有一条记录的line转成OrderedDict，而我们需要的时list，需转化下
                if str(type(tmpDTL)) == "<class 'collections.OrderedDict'>":
                    tmpDTL = [tmpDTL]
                nextcount=0
                for line in tmpDTL:
                    if "nextPoint" in line:
                        nextStepId = line["nextPoint"]
                        criteria = True
                        #4.解析line的条件criteria，判断条件是否成立
                        #判断上一步是否未判断控件，如果是，对比判断结果和线条条件；如果不是，无视条件直接继续
                        for lastOutput in stepOutput:
                            if "code" in lastOutput and lastOutput["code"]=="result":
                                criteriaStr = "True"
                                try:
                                    criteriaStr = line["criteria"]
                                except:
                                    pass
                                if lastOutput["value"]==False:
                                    if criteriaStr != "False":
                                        criteria = False
                                else:
                                    if criteriaStr == "False":
                                        criteria = False
                                break
                        #5.执行下一步
                        if criteria:
                            xml = etree.fromstring(self.jobModel.workflowBaseInfo["content"])
                            nextStep = xml.xpath("//stepid[text()='" + nextStepId + "'][1]/parent::*/parent::*")
                            if len(nextStep) > 0:
                                nextcount = nextcount+1
                                returnState=self._run_step(etree.tostring(nextStep[0]).decode('utf-8'))
                                if returnState=="ERROR":
                                    break
                if nextcount<=0:
                    self.jobBaseInfo["log"] += 'error(_run_step)步骤未找到下一步'
                    self.jobBaseInfo["state"] = "ERROR"
                    self.save_job()
                    returnState = "ERROR"
            else:
                self.jobBaseInfo["log"] += 'error(_run_step)步骤未找到下一步'
                self.jobBaseInfo["state"] = "ERROR"
                self.save_job()
                returnState = "ERROR"
        return returnState

    # 流程结束
    def _end_workflow(self):
        """
        1.设置finalOutput
        2.结束并保存
        """
        if self.jobModel.workflowBaseInfo["output"] and len(self.jobModel.workflowBaseInfo["output"].strip()) > 0:
            tmpOutput = xmltodict.parse(self.jobModel.workflowBaseInfo["output"])
            if "outputs" in tmpOutput and tmpOutput["outputs"] and "output" in tmpOutput["outputs"]:
                tmpDTL = tmpOutput["outputs"]["output"]
                # xmltodict会将只有一条记录的output转成OrderedDict，而我们需要的时list，需转化下
                if str(type(tmpDTL)) == "<class 'collections.OrderedDict'>":
                    tmpDTL = [tmpDTL]
                self.finalOutput = tmpDTL
                # 给步骤的finalOutput赋值
                self.finalOutput = self._sourceToValue(self.finalOutput)
        self.jobBaseInfo["state"] = "DONE"
        self.jobBaseInfo["endtime"] = datetime.datetime.now()
        return "DONE"
        print(self.finalOutput)

    #######################################################
    # 参数传递部分 #
    #######################################################

    # 将子任务的输出更新到父任务jobStepOutput和jobVariable
    def _update_stepOutput(self,curStep,stepOutput):
        """
        将步骤运行结果写入主任务的步骤输出jobStepOutput和内部参数jobVariable中

        1.将步骤output并存入主任务jobStepOutput
        2.将步骤output写入主任务内部参数jobVariable

        Args:
            curStep (dict): dict格式的步骤信息
            stepOutput(dict):任务输出

        Returns:
            无
        """
        # 1.获得步骤任务output并存入主任务jobStepOutput
        for oldJobStepOutput in self.jobStepOutput:
            if oldJobStepOutput["id"] == curStep["step"]["baseInfo"]["stepid"]:
                oldJobStepOutput["output"] = stepOutput
                break
        else:
            self.jobStepOutput.append({"id": curStep["step"]["baseInfo"]["stepid"], "output": stepOutput})
        # 2.将步骤output写入主任务内部参数jobVariable
        if "outputs" in curStep["step"] and curStep["step"]["outputs"] and "output" in curStep["step"]["outputs"] and len(
                curStep["step"]["outputs"]["output"]) > 0:
            tmpDTL = curStep["step"]["outputs"]["output"]
            # xmltodict会将只有一条记录的output转成OrderedDict，而我们需要的时list，需转化下
            if str(type(tmpDTL)) == "<class 'collections.OrderedDict'>":
                tmpDTL = [tmpDTL]
            for outputSet in tmpDTL:
                for variable in self.jobVariable:
                    if variable["code"] == outputSet["to"]:
                        for output in stepOutput:
                            if outputSet["code"] == output["code"]:
                                if outputSet["type"] == "cover":
                                    variable["value"] = output["value"]
                                elif outputSet["type"] == "add":
                                    try:
                                        if "value" in variable and variable["value"] is not None:
                                            variable["value"] = variable["value"] + output["value"]
                                        else:
                                            variable["value"] = output["value"]
                                    except:
                                        pass
                                break
                        break

    # 获取输入参数值
    def _getInput(self):
        """
        汇总流程配置、实例配置、任务配置中的input参数，并根据参数source，将配置转化为实际值

        1.从流程中获取input
        2.从实例中获取input
        3.从任务中获取input
        4.格式化input参数，将配置转化为实际值

        Returns:
            无
        """

        if self.jobModel.workflowBaseInfo["input"] and len(self.jobModel.workflowBaseInfo["input"].strip()) > 0:
            #1.从流程中获取input
            tmpInput = xmltodict.parse(self.jobModel.workflowBaseInfo["input"])
            if "inputs" in tmpInput and "input" in tmpInput["inputs"]:
                tmpDTL= tmpInput["inputs"]["input"]
                if str(type(tmpDTL)) == "<class 'collections.OrderedDict'>":
                    tmpDTL = [tmpDTL]
                self.finalInput = tmpDTL
                if len(self.finalInput)>0:
                    if self.jobType == 'INSTANCE':
                        #2.从实例中获取input
                        tmpInput = xmltodict.parse(self.jobModel.instanceBaseInfo["input"])
                        if "inputs" in tmpInput and "input" in tmpInput["inputs"]:
                            tmpDTL = tmpInput["inputs"]["input"]
                            if str(type(tmpDTL)) == "<class 'collections.OrderedDict'>":
                                tmpDTL = [tmpDTL]
                            instanceInputList = tmpDTL
                            if len(instanceInputList)>0:
                                for input in self.finalInput:
                                    if "source" in input and input["source"]=="input":
                                        for instanceInput in instanceInputList:
                                            if instanceInput["code"] == input["code"]:
                                                input["value"] = instanceInput["value"]
                    #3.从任务中获取input
                    tmpInput = xmltodict.parse(self.jobBaseInfo["input"])
                    if "inputs" in tmpInput and "input" in tmpInput["inputs"]:
                        tmpDTL = tmpInput["inputs"]["input"]
                        if str(type(tmpDTL)) == "<class 'collections.OrderedDict'>":
                            tmpDTL = [tmpDTL]
                        jobInputList = tmpDTL
                        if len(jobInputList) > 0:
                            for input in self.finalInput:
                                if "source" in input and input["source"]=="input":
                                    for jobInput in jobInputList:
                                        if jobInput["code"] == input["code"]:
                                            input["value"] = jobInput["value"]
                #4.格式化input参数，将配置转化为实际值
                self.finalInput = self._sourceToValue(self.finalInput)

    # 获取流程内部变量
    def _getVariable(self):
        if self.jobModel.workflowBaseInfo["variable"] and len(self.jobModel.workflowBaseInfo["variable"].strip()) > 0:
            #从流程中获取input
            tmpVariable = xmltodict.parse(self.jobModel.workflowBaseInfo["variable"])
            if "variables" in tmpVariable and tmpVariable["variables"] and "variable" in tmpVariable["variables"]:
                tmpDTL= tmpVariable["variables"]["variable"]
                if str(type(tmpDTL)) == "<class 'collections.OrderedDict'>":
                    tmpDTL = [tmpDTL]
                self.jobVariable = tmpDTL

    # 格式化参数
    def _sourceToValue(self, paramList,sourceNode=None):
        """
        将参数配置转化为实际值,用于输入、输出、判断条件等参数

        1.根据source，从workfolwInput、workfolwVariable、stepOutput、_getFunctionValue中获取参数值；常数和input不需要额外获取
        2.转换参数类型

        Args:
            paramList (list): 参数列表
            sourceNode(Job):数据源节点

        Returns:
            paramList(list): 参数列表
        """

        curSourceNode = self
        if sourceNode is not None:
            curSourceNode = sourceNode

        # 1.根据source，从workfolwInput、workfolwVariable、stepOutput、_getFunctionValue中获取参数值；常数和input不需要额外获取
        for param in paramList:

            if param["source"] == "workfolwInput":
                for tmpInput in curSourceNode.finalInput:
                    if param["value"] == tmpInput["code"]:
                        param["value"]=tmpInput["value"]
                        break
                else:
                    param["value"] == None
            elif param["source"] == "workfolwVariable":
                for tmpVariable in curSourceNode.jobVariable:
                    if param["value"] == tmpVariable["code"]:
                        param["value"]=tmpVariable["value"]
                        break
                else:
                    param["value"] == None
            elif param["source"] == "stepOutput":
                from_step = None
                from_param = None
                try:
                    from_step, from_param = param["value"].split('^')
                except:
                    pass
                if from_step and from_param:
                    for tmpStepOutput in curSourceNode.jobStepOutput:
                        if tmpStepOutput["id"]==from_step:
                            for tmpOutput in tmpStepOutput["output"]:
                                if from_param == tmpOutput["code"]:
                                    param["value"] = tmpOutput["value"]
                                    break
                            else:
                                param["value"] == None
                            break
            elif param["source"] == "function":
                param["value"] = self._getFunctionValue(param["value"])
        # 2.转换参数类型
        paramList = self._changeType(paramList)
        return paramList

    #转换数据类型
    def _changeType(self, paramList):
        """
        转换参数数据类型

        Args:
            paramList (list): 参数列表

        Returns:
            paramList(list): 参数列表
        """
        for param in paramList:
            try:
                if param["type"] == "int":
                    try:
                        param["value"] = int(param["value"])
                    except:
                        param["value"] = None
                elif param["type"] == "decimal":
                    try:
                        param["value"] = decimal.Decimal(param["value"])
                    except:
                        param["value"] = None
                elif param["type"] == "datetime":
                    try:
                        param["value"] = datetime.datetime.strptime(param["value"], "%Y-%m-%d %H:%M:%S')")
                    except:
                        param["value"] = None
                elif param["type"] == "bool":
                    if param["value"]=="True":
                        param["value"] = True
                    elif param["value"]=="False":
                        param["value"] = False
                # elif param["type"] == "json":
                #     try:
                #         param["value"] = json.loads(param["value"])
                #     except:
                #         param["value"] = None
            except:
                pass
        return paramList

    #######################################################
    # 进程控制部分 #
    #######################################################

    # 重试/继续步骤
    def retry_job(self):
        """
        重试/继续步骤。
        a)查找下级需重试的步骤，如果还有下级，一层层往下找，直至找到最底层。
        b)运行最底层任务
        c)运行最底层的后续步骤，后续步骤全部运行完成，视为父任务执行完成
        d)运行父节点后续任务，一一层层往上，直至主任务。

        1.查找有没有错误的子任务，如果有，重试子任务
            2.重试子任务，成功运行（state=DONE），执行子任务的下一步骤
                3.将子任务的输出更新到父任务jobStepOutput和jobVariable并保存
                4.运行子任务的后续步骤，直至结束或出错，结果返回给前任务状态
            5.子任务失败，则当前任务也失败
            6.保存
        7.如果没有，直接运行任务；

        Returns:
            无
        """

        #1.查找有没有错误的子任务，如果没有，直接运行任务；如果有，重试子步骤
        self.jobBaseInfo["state"] = "RUN"
        self.save_job()
        childrenJobList = self.job.children.filter(state__in=["ERROR", "PAUSE"])
        if len(childrenJobList)>0:
            childJob = Job(childrenJobList[0].guid)
            #2.重试子步骤，成功运行（state=DONE），执行子步骤的下一步骤
            curstate = childJob.retry_job()
            if curstate=="DONE" or curstate=="WAIT":
                xml = etree.fromstring(self.jobModel.workflowBaseInfo["content"])
                curStep = xml.xpath("//stepid[text()='" + childJob.jobBaseInfo["step"] + "'][1]/parent::*/parent::*")
                if len(curStep) > 0:
                    curStep = etree.tostring(curStep[0]).decode('utf-8')
                    curStep = xmltodict.parse(curStep)
                    # 3.将子任务的输出更新到父任务jobStepOutput和jobVariable并保存
                    self.save_job()
                    self._update_stepOutput(curStep, childJob.finalOutput)
                    # 4.运行子任务的后续步骤，直至结束或出错，结果返回给前任务状态
                    self.jobBaseInfo["state"] = self._run_nextStep(curStep,childJob.finalOutput)
                else:
                    self.jobBaseInfo["log"] += 'error(_retry_job)步骤信息错误'
                    self.jobBaseInfo["state"] = "ERROR"
            # 5.子任务失败，则当前任务也失败
            else:
                self.jobBaseInfo["state"] = curstate
            #6.保存
            self.save_job()
        else:
            #7.如果没有，直接运行任务
            self.run_job()
        return self.jobBaseInfo["state"]

    # 跳过步骤
    def skip_step(self,skipJobGuid):
        """
        跳过步骤，跳过操作只对暂停和出错的任务有效。
        a)用guid进行匹配需跳过的任务，如果还有下级，一层层往下找，直至找到或遍历到最底层。
        b)如果匹配不上，则跳过失败
        c)跳过匹配上的步骤
        d)运行跳过的后续步骤，后续步骤全部运行完成，视为父任务执行完成
        e)运行父节点后续任务，一一层层往上，直至主任务。

        1.判断当前任务是否为需跳过的任务
            2.如果不是，查询子任务中暂停或出错的任务
                3.如果子任务中存在暂停或出错的任务，调用递归函数skip_step
                  4.子任务返回SKIP或DONE时，说明跳过成功（SKIP为跳过的步骤返回状态，DONE为跳过的步骤的祖先节点返回状态），运行子任务后续步骤
                        5.将子任务的输出更新到父任务jobStepOutput和jobVariable并保存
                        6.运行子任务的后续步骤，直至结束或出错，结果返回给前任务状态
                    7.子任务返回ERROR，则当前任务也失败
                    8.子任务返回NONE时，提示不存在需跳过的步骤，不修改任何数据
                9.如果子任务中不存在暂停或出错的任务，返回NONE状态，提示不存在需跳过的步骤，不修改任何数据
            10.如果是，跳过该任务，设置SKIP状态
        11.保存并返回

        Returns:
            无
        """

        # 1.判断当前任务是否为需跳过的任务
        self.jobBaseInfo["state"] = "RUN"
        self.save_job()
        if self.jobGuid!=skipJobGuid:
            # 2.如果不是，查询子任务中暂停或出错的任务
            childrenJobList = self.job.children.filter(state__in=["ERROR", "PAUSE"])
            if len(childrenJobList) > 0:
                childJob = Job(childrenJobList[0].guid)
                # 3.如果子任务中存在暂停或出错的任务，调用递归函数skip_step
                curstate = childJob.skip_step(skipJobGuid)
                #4.子任务返回SKIP或DONE时，说明跳过成功（SKIP为跳过的步骤返回状态，DONE为跳过的步骤的祖先节点返回状态），运行子任务后续步骤
                if curstate == "DONE" or curstate == "SKIP" or curstate == "WAIT":
                    xml = etree.fromstring(self.jobModel.workflowBaseInfo["content"])
                    curStep = xml.xpath("//stepid[text()='" + childJob.jobBaseInfo["step"] + "'][1]/parent::*/parent::*")
                    if len(curStep) > 0:
                        curStep = etree.tostring(curStep[0]).decode('utf-8')
                        curStep = xmltodict.parse(curStep)
                        # 5.将子任务的输出更新到父任务jobStepOutput和jobVariable并保存
                        self._update_stepOutput(curStep, childJob.finalOutput)
                        # 6.运行子任务的后续步骤，直至结束或出错，结果返回给前任务状态
                        self.jobBaseInfo["state"] = self._run_nextStep(curStep, childJob.finalOutput)
                    else:
                        self.jobBaseInfo["log"] += 'error(skip_step)步骤信息错误'
                        self.jobBaseInfo["state"] = "ERROR"
                #7.子任务返回NONE时，直接return NONE，不修改任何数据
                elif curstate == "NONE":
                    return curstate
                # 8.子任务返回ERROR，则当前任务也失败
                else:
                    self.jobBaseInfo["state"] = curstate
            #9.如果子任务中不存在暂停或出错的任务，返回NONE状态，提示不存在需跳过的步骤，不修改任何数据
            else:
                return "NONE"
        # 10.如果是，跳过该任务，设置SKIP状态
        else:
            self.jobBaseInfo["state"] = "SKIP"
        # 11.保存并返回
        self.save_job()
        return self.jobBaseInfo["state"]

    # 中止任务
    def stop_job(self):
        """
        1.中止进程
        2.修改任务状态
        """
        revoke_p_task(self.jobGuid)#revoke_p_task是基于Celery的监控工具Flower写的方法，可根据jobGuid中断运行中的异步任务
        self.jobBaseInfo["state"] = "STOP"
        self.save_job()

    # 暂停任务
    def pause_job(self):
        """
        1.中止进程
        2.修改任务状态
        """
        revoke_p_task(self.jobGuid)#revoke_p_task是基于Celery的监控工具Flower写的方法，可根据jobGuid中断运行中的异步任务
        self.pause_job_state()

    # 暂停任务-修改任务状态
    def pause_job_state(self):
        self.jobBaseInfo["state"] = "PAUSE"
        self.save_job()
        childrenJobList = self.job.children.filter(state="RUN")
        for childrenJob in childrenJobList:
            childJob = Job(childrenJob.guid)
            childJob.pause_job_state()

    #######################################################
    # 控件部分 #
    #######################################################

    #控件——开始流程
    def _control_workflowStart(self):
        pass

    #控件——结束流程
    def _control_workflowEnd(self):
        pass

    # 控件——判断
    def _control_if(self):
        """
        1.获取条件列表
        2.解析每个条件不等式左右两边参数值
        3.根据不等式，判断单个条件结果
        4.根据逻辑运算符，取最终结果
        5.输出结果finalOutput
        """
        criteriaList = []
        result = True

        #1.获取条件列表
        if len(self.finalInput)>0:
            for input in self.finalInput:
                if input["code"]=="criteria":
                    criteriaList = input["value"]
                    break
        if criteriaList:
            for criteria in criteriaList:
                #2.解析每个条件不等式左右两边参数
                curResult = False
                leftParm = [{"type":criteria["type"],"source":criteria["left_source"],"value":criteria["left_value"]}]
                leftParm = self._sourceToValue(leftParm,sourceNode=self.pnode)
                leftValue = None
                if len(leftParm)>0:
                    leftValue=leftParm[0]["value"]

                rightParm = [
                    {"type": criteria["type"], "source": criteria["right_source"], "value": criteria["right_value"]}]
                rightParm = self._sourceToValue(rightParm,sourceNode=self.pnode)
                rightValue = None
                if len(rightParm) > 0:
                    rightValue = rightParm[0]["value"]

                #3.根据不等式，判断单个条件结果
                criteriaChar=criteria["char"].strip()
                if criteriaChar:
                    if criteriaChar=="==":
                        try:
                            if leftValue == rightValue:
                                curResult = True
                        except:
                            pass
                    elif criteriaChar==">":
                        try:
                            if leftValue > rightValue:
                                curResult = True
                        except:
                            pass
                    elif criteriaChar==">=":
                        try:
                            if leftValue >= rightValue:
                                curResult = True
                        except:
                            pass
                    elif criteriaChar=="<":
                        try:
                            if leftValue < rightValue:
                                curResult = True
                        except:
                            pass
                    elif criteriaChar=="<=":
                        try:
                            if leftValue <= rightValue:
                                curResult = True
                        except:
                            pass
                    elif criteriaChar=="!=":
                        try:
                            if leftValue != rightValue:
                                curResult = True
                        except:
                            pass
                #4.根据逻辑运算符，取最终结果
                criteriaLogic=criteria["logic"].strip()
                if criteriaLogic:
                    if criteriaLogic=="and":
                        result = result and curResult
                    elif criteriaLogic=="or":
                        result = result or curResult
        #5.输出结果finalOutput
        if self.jobModel.workflowBaseInfo["output"] and len(self.jobModel.workflowBaseInfo["output"].strip()) > 0:
            tmpDTL = xmltodict.parse(self.jobModel.workflowBaseInfo["output"])
            if "outputs" in tmpDTL and tmpDTL["outputs"] and "output" in tmpDTL["outputs"] and tmpDTL["outputs"][
                "output"]:
                tmpDTL = tmpDTL["outputs"]["output"]
                if str(type(tmpDTL)) == "<class 'collections.OrderedDict'>":
                    tmpDTL = [tmpDTL]
                self.finalOutput = tmpDTL

                for output in self.finalOutput:
                    if output["code"] == "result":
                        output.update({'value': result})
                        break

    # 控件——循环
    def _control_for(self):
        """
        1.获取循环列表
        2.循环列表存在时，列表长度为循环次数，否则从输入参数中获取总循环次数
        3.获取上次结果中的当前次数
        4.定义number、element、result(isEnd)
        5.输出结果finalOutput
        """
        mylist = []
        count=0
        isEnd =True
        element=None
        number=0
        # 1.获取循环列表
        if len(self.finalInput)>0:
            for input in self.finalInput:
                if input["code"]=="list":
                    try:
                        mylist = json.loads(input["value"])
                    except:
                        mylist=[]
                    break
            # 2.循环列表存在时，列表长度为循环次数，否则从输入参数中获取总循环次数
            if mylist is not None:
                count = len(mylist)
            else:
                for input in self.finalInput:
                    if input["code"] == "count":
                        count = input["value"]
                        break
            # 3.获取上次结果中的当前次数
            if len(self.finalOutput) > 0:
                for output in self.finalOutput:
                    if output["code"] == "number":
                        number = output["value"]
                        break
        number=number+1
        #3.定义number、element、result(isEnd)
        if count is not None and number is not None and count>=number:
            isEnd =False
            if mylist is not None:
                element = mylist[number-1]
        #4.输出结果finalOutput
        if self.jobModel.workflowBaseInfo["output"] and len(self.jobModel.workflowBaseInfo["output"].strip()) > 0:
            tmpDTL = xmltodict.parse(self.jobModel.workflowBaseInfo["output"])
            if "outputs" in tmpDTL and tmpDTL["outputs"] and "output" in tmpDTL["outputs"] and tmpDTL["outputs"][
                "output"]:
                tmpDTL = tmpDTL["outputs"]["output"]
                if str(type(tmpDTL)) == "<class 'collections.OrderedDict'>":
                    tmpDTL = [tmpDTL]
                self.finalOutput = tmpDTL

                for output in self.finalOutput:
                    if output["code"] == "result":
                        output.update({'value': isEnd})
                    if output["code"] == "element":
                        output.update({'value': element})
                    if output["code"] == "number":
                        output.update({'value': number})

    # 控件——跳出循环
    def _control_break(self):
        #找到父流程的最后一个未完成的循环任务,修改状态为BREAK
        loopJobList = self.pnode.job.children.filter(state__in=["RUN", "WAIT"],
                                               modelguid="0aa259dc-50ad-11eb-a8a3-84fdd1a17907").order_by("-id")
        if len(loopJobList)>0:
            loopJob = Job(loopJobList[0].guid)
            loopJob.jobBaseInfo["state"] = "BREAK"
            loopJob.jobBaseInfo["endtime"] = datetime.datetime.now()
            loopJob.save_job()

    #######################################################
    # 公式解析部分 #
    #######################################################

    # 解析公式,待完善
    def _getFunctionValue(self, fun):
        value=fun
        return value

if __name__ == "__main__":
    # #创建任务
    # testJob = Job()
    # jobJson = {}
    # jobJson["createuser"] = 1
    # jobJson["name"] = '测试任务'
    # jobJson["reson"] = '测试'
    # jobJson["type"] = 'INSTANCE'
    # aa = datetime.datetime.now()
    # jobJson["modelguid"] = 'd19e3a02-44d0-11eb-b557-84fdd1a17907'
    # jobJson["input"] = '<inputs><input><code>inputnum</code><value>1</value></input></inputs>'
    # testJob.create_job(jobJson)

    # get并执行任务
    testJob = Job('ff395b2e-454c-11eb-8c53-000c29c81d38')
    testJob.run_job()

