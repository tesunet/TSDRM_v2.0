from ..models import *
import uuid
import datetime
from lxml import etree
import decimal
import json
import xmltodict


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
    def __init__(self,job_guid=None,userid=None,pnode=None):
        self.pnode=pnode
        self.userid = userid
        self.jobGuid = job_guid
        self.modelGuid = None
        self.jobType = None
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
        #输入参数及值
        self.finalInput = []
        #输出参数及值
        self.finalOutput = []
        # 实例化传入guid时，从数据库中查找，guid为None时，视为新建
        if self.jobGuid and len(self.jobGuid.strip()) > 0:
            self.get_job(self.jobGuid)

    # 获取任务
    def get_job(self,jobGuid):
        """
        根据guid从数据库中获取数据，jobBaseInfo
        解析XML获得jobStepOutput（每步的输出数据）
        jobVariable（内部变量值）
        finalInput（全部输入参数值）
        finalOutput（全部输出参数值）

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
                    self.jobStepOutput = tmpDTL
            if self.job.jobvariable and len(self.job.jobvariable.strip()) > 0:
                tmpDTL = xmltodict.parse(self.job.jobvariable)
                if "variables" in tmpDTL and tmpDTL["variables"] and "variable" in tmpDTL["variables"] and tmpDTL["variables"]["variable"]:
                    tmpDTL = tmpDTL["variables"]["variable"]
                    if str(type(tmpDTL)) == "<class 'collections.OrderedDict'>":
                        tmpDTL = [tmpDTL]
                    self.jobVariable = tmpDTL
            if self.job.finalinput and len(self.job.finalinput.strip()) > 0:
                tmpDTL = xmltodict.parse(self.job.finalinput)
                if "inputs" in tmpDTL and tmpDTL["inputs"] and "input" in tmpDTL["inputs"] and tmpDTL["inputs"]["input"]:
                    tmpDTL = tmpDTL["inputs"]["input"]
                    if str(type(tmpDTL)) == "<class 'collections.OrderedDict'>":
                        tmpDTL = [tmpDTL]
                    self.finalInput = tmpDTL
            if self.job.output and len(self.job.output.strip()) > 0:
                tmpDTL = xmltodict.parse(self.job.output)
                if "outputs" in tmpDTL and tmpDTL["outputs"] and "output" in tmpDTL["outputs"] and tmpDTL["outputs"]["output"]:
                    tmpDTL = tmpDTL["outputs"]["output"]
                    if str(type(tmpDTL)) == "<class 'collections.OrderedDict'>":
                        tmpDTL = [tmpDTL]
                    self.finalOutput = tmpDTL
        else:
            self.massage = 'error(get_job):任务' + jobGuid + '不存在'

    #新建任务
    def create_job(self,jobJson):
        """
        根据jobJson创建任务
        jobJson可包含name、reson、pjob、type、modelguid、schedule、input
        """

        self.jobGuid = None
        self.jobModelguid = None
        self.jobType = None
        self.jobBaseInfo = None
        self.job = None
        self.jobStepOutput = []
        self.jobVariable = []
        self.finalInput = []
        self.finalOutput = []
        if "type" not in jobJson:
            self.massage = 'error(create_job):jobJson需包含type元素'
        elif jobJson["type"]!='INSTANCE' and jobJson["type"]!='CONTROL' and jobJson["type"]!='COMPONENT' and jobJson["type"]!='WORKFLOW':
            self.massage = 'error(create_job):jobJson["type"]只能为INSTANCE、CONTROL、COMPONENT、WORKFLOW'
        elif "modelguid" not in jobJson or jobJson["modelguid"] is None:
            self.massage = 'error(create_job):jobJson需包含modelguid元素且不为空'
        else:
            try:
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
                if "pjob" in jobJson:
                    self.job.pjob_id = jobJson["pjob"]
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
                self.get_job(self.jobGuid)
            except Exception as e:
                self.massage = 'error(create_job):创建任务失败'

    # 保存任务
    def _save_job(self):
        """
        将jobBaseInfo中数据保存到数据库
        """
        self.job.updatetime = datetime.datetime.now()
        if self.userid:
            self.job.updateuser_id = self.userid

        self.job.startuser_id = self.jobBaseInfo["startuser"]
        self.job.starttime = self.jobBaseInfo["starttime"]
        self.job.endtime = self.jobBaseInfo["endtime"]
        self.job.log = self.jobBaseInfo["log"]
        self.job.state = self.jobBaseInfo["state"]
        aa = {"stepoutputs":{"stepoutput":self.jobStepOutput}}
        self.job.jobstepoutput = xmltodict.unparse({"stepoutputs":{"stepoutput":self.jobStepOutput}}, encoding='utf-8')
        self.job.jobvariable = xmltodict.unparse({"jobvariables":{"jobvariable":self.jobVariable}}, encoding='utf-8')
        self.job.finalinput = xmltodict.unparse({"inputs":{"input":self.finalInput}}, encoding='utf-8')
        self.job.output = xmltodict.unparse({"outputs":{"output":self.finalOutput}}, encoding='utf-8')
        self.job.save()

    # 开始任务
    def start_job(self):
        """
        1、_getInput，获取获取input参数值
        2、_getVariable，定义内部参数变量
        3、保存任务
        4、_run_workflow，_run_control，_run_component根据类型(流程、控件、组件)执行任务
        """
        if self.jobGuid is None:
            self.massage = 'error(start_job):任务未初始化'
            self.jobBaseInfo["log"]+='error(start_job):任务未初始化'
        else:
            self.jobBaseInfo["starttime"] = datetime.datetime.now()
            self.jobBaseInfo["startuser"] = self.userid
            self.jobBaseInfo["state"] = "RUN"
            #1、_getInput，获取获取input参数值
            self._getInput()
            #2、_getVariable，定义内部参数变量
            self._getVariable()
            #3、保存任务
            self._save_job()
            #4、_run_workflow，_run_control，_run_component根据类型(流程、控件、组件)执行任务
            if self.jobModel.workflowType == "WORKFLOW":
                self._run_workflow()
            if self.jobModel.workflowType == "CONTROL":
                self._run_control()
            if self.jobModel.workflowType == "COMPONENT":
                self._run_component()

    # 执行流程
    def _run_workflow(self):
        """
        解析workflow的content字段，找出开始步骤modelguid='ef81b0de-44cc-11eb-9c38-84fdd1a17907'
        执行开始步骤
        """
        xml = etree.fromstring(self.jobModel.workflowBaseInfo["content"])
        startStep = xml.xpath("//modelguid[text()='ef81b0de-44cc-11eb-9c38-84fdd1a17907'][1]/parent::*/parent::*")
        if len(startStep) > 0:
            self._run_step(etree.tostring(startStep[0]).decode('utf-8'))
        else:
            self.massage = 'error(start_job)未配置开始步骤'
            self.jobBaseInfo["log"] +='error(start_job)未配置开始步骤'

    # 执行控件
    def _run_control(self):
        """
        根据controlclass字段内容，执行对应方法
        exec方法可执行储存在字符串Python 语句
        """
        if self.jobModel.workflowBaseInfo["controlclass"] and len(self.jobModel.workflowBaseInfo["controlclass"].strip()) > 0:
            exec("self._control_" + self.jobModel.workflowBaseInfo["controlclass"] + "()")
        self.jobBaseInfo["state"] = "DONE"
        self._save_job()

    # 执行组件
    def _run_component(self):
        """
        1.定义组件componentInput和componentOutput
        2.根据类型执行组件代码，目前只写了python类型。组件code中，直接把输出参数值写到componentOutput对应的键上
        3.将componentOutput写到任务的finalOutput中
        4.保存任务
        """
        #1.定义组件componentInput和componentOutput
        componentInput = {}
        for input in self.finalInput:
            componentInput[input["code"]] = input["value"]
        componentOutput = {}
        #2.根据类型执行组件代码，目前只写了python类型。组件code中，直接把输出参数值写到componentOutput对应的键上
        if self.jobModel.workflowBaseInfo["language"]=="python":
            componentCode=self.jobModel.workflowBaseInfo["code"]
            exec(componentCode)
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
        self.jobBaseInfo["state"]="DONE"
        #4.保存任务
        self._save_job()
        print(self.finalOutput)

    # 运行步骤
    def _run_step(self,step):
        """
        1.获得步骤信息
        2.创建并运行步骤任务
        3.获得步骤任务output并存入主任务jobStepOutput
        4.将步骤output写入主任务内部参数jobVariable
        5.保存任务
        6.判断是否为结束步骤modelguid=='69255378-44ce-11eb-9203-84fdd1a17907'，如果是执行7，如果不是执行8
        7.结束任务
        8.根据step中的line查找下一步
        9.解析line的条件criteria，只有判断控件（modelguid=='c2d3f2b6-49a9-11eb-99aa-84fdd1a17907'）的criteria才生效
        10.执行下一步
        11.保存
        """
        stepJob=Job(userid=self.userid,pnode=self)
        jobJson = {}
        curStep = xmltodict.parse(step)

        if "step" in step and "baseInfo" in curStep["step"] and curStep["step"]["baseInfo"] and "stepid" in curStep["step"]["baseInfo"] and curStep["step"]["baseInfo"]["stepid"] and len(curStep["step"]["baseInfo"]["stepid"].strip()) and curStep["step"]["baseInfo"]["modelguid"] and len(curStep["step"]["baseInfo"]["modelguid"].strip()) and curStep["step"]["baseInfo"]["modelType"] and len(curStep["step"]["baseInfo"]["modelType"].strip()) > 0:
            #1.获得步骤信息
            jobJson["modelguid"] = curStep["step"]["baseInfo"]["modelguid"]
            jobJson["type"] = curStep["step"]["baseInfo"]["modelType"]
            jobJson["pjob"] = self.jobBaseInfo["id"]
            jobJson["step"] = curStep["step"]["baseInfo"]["stepid"]
            if "inputs" in curStep["step"] and curStep["step"]["inputs"] and"input" in curStep["step"]["inputs"] and curStep["step"]["inputs"]["input"]:
                tmpDTL = curStep["step"]["inputs"]["input"]
                # xmltodict会将只有一条记录的input转成OrderedDict，而我们需要的时list，需转化下
                if str(type(tmpDTL)) == "<class 'collections.OrderedDict'>":
                    tmpDTL = [tmpDTL]
                # 给步骤的input赋值
                stepInput = self._sourceToValue(tmpDTL)
                stepInput = {"inputs":{"input":stepInput}}
                jobJson["input"] = xmltodict.unparse(stepInput,encoding='utf-8')
            #2.创建并运行步骤任务
            stepJob.create_job(jobJson)
            stepJob.start_job()
            #3.获得步骤任务output并存入主任务jobStepOutput
            stepOutput = stepJob.finalOutput
            for oldJobStepOutput in self.jobStepOutput:
                if oldJobStepOutput["id"] ==curStep["step"]["baseInfo"]["stepid"]:
                    oldJobStepOutput["output"] =stepOutput
                    break
            else:
                self.jobStepOutput.append({"id":curStep["step"]["baseInfo"]["stepid"],"output":stepOutput})
            #4.将步骤output写入主任务内部参数jobVariable
            if "outputs" in curStep["step"] and "output" in curStep["step"]["outputs"] and len(curStep["step"]["outputs"]["output"]) > 0:
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
        else:
            self.massage = 'error(_run_step)步骤信息错误'
            self.jobBaseInfo["log"] +='error(_run_step)步骤信息错误'
        #5.保存任务
        self._save_job()

        #6.判断是否为结束步骤modelguid=='69255378-44ce-11eb-9203-84fdd1a17907'，如果是执行7，如果不是执行8
        if curStep["step"]["baseInfo"]["modelguid"]=='69255378-44ce-11eb-9203-84fdd1a17907':
            #7.结束任务
            self._end_job()
        else:
            #8.根据step中的line查找下一步
            if "step" in step and "lines" in curStep["step"] and "line" in curStep["step"]["lines"] and len(curStep["step"]["lines"]["line"]) > 0:
                tmpDTL = curStep["step"]["lines"]["line"]
                # xmltodict会将只有一条记录的line转成OrderedDict，而我们需要的时list，需转化下
                if str(type(tmpDTL)) == "<class 'collections.OrderedDict'>":
                    tmpDTL = [tmpDTL]
                for line in tmpDTL:
                    if "nextPoint" in line:
                        nextStepId = line["nextPoint"]
                        criteria = True
                        #9.解析line的条件criteria，只有判断控件（modelguid=='c2d3f2b6-49a9-11eb-99aa-84fdd1a17907'）的criteria才生效
                        #判断上一步是否未判断控件，如果是，对比判断结果和线条条件；如果不是，无视条件直接继续
                        if curStep["step"]["baseInfo"]["modelguid"] == 'c2d3f2b6-49a9-11eb-99aa-84fdd1a17907':
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
                        #10.执行下一步
                        if criteria:
                            xml = etree.fromstring(self.jobModel.workflowBaseInfo["content"])
                            nextStep = xml.xpath("//stepid[text()='" + nextStepId + "'][1]/parent::*/parent::*")
                            if len(nextStep) > 0:
                                self._run_step(etree.tostring(nextStep[0]).decode('utf-8'))
                            else:
                                self.massage = 'error(_run_step)下一步' + nextStepId +'未找到'
                                self.jobBaseInfo["log"] +='error(_run_step)下一步' + nextStepId +'未找到'
            else:
                self.massage = 'error(_run_step)步骤未找到下一步'
                self.jobBaseInfo["log"] +='error(_run_step)步骤未找到下一步'
            #11.保存
            self._save_job()

    # 运行结束
    def _end_job(self):
        """
        1.设置finalOutput
        2.结束并保存
        """
        if self.jobModel.workflowBaseInfo["output"] and len(self.jobModel.workflowBaseInfo["output"].strip()) > 0:
            tmpOutput = xmltodict.parse(self.jobModel.workflowBaseInfo["output"])
            if "outputs" in tmpOutput and "output" in tmpOutput["outputs"]:
                tmpDTL = tmpOutput["outputs"]["output"]
                # xmltodict会将只有一条记录的output转成OrderedDict，而我们需要的时list，需转化下
                if str(type(tmpDTL)) == "<class 'collections.OrderedDict'>":
                    tmpDTL = [tmpDTL]
                self.finalOutput = tmpDTL
                # 给步骤的finalOutput赋值
                self.finalOutput = self._sourceToValue(self.finalOutput)
        self.jobBaseInfo["state"] = "DONE"
        self._save_job()
        print(self.finalOutput)

    # 获取输入参数
    def _getInput(self):
        """
        1.从流程中获取input
        2.从实例中获取input
        3.从任务中获取input
        4.格式化input参数
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
                #4.格式化input参数
                self.finalInput = self._sourceToValue(self.finalInput)

    # 获取内部变量
    def _getVariable(self):
        if self.jobModel.workflowBaseInfo["variable"] and len(self.jobModel.workflowBaseInfo["variable"].strip()) > 0:
            #从流程中获取input
            tmpVariable = xmltodict.parse(self.jobModel.workflowBaseInfo["variable"])
            if "variables" in tmpVariable and "variable" in tmpVariable["variables"]:
                tmpDTL= tmpVariable["variables"]["variable"]
                if str(type(tmpDTL)) == "<class 'collections.OrderedDict'>":
                    tmpDTL = [tmpDTL]
                self.jobVariable = tmpDTL


    # 格式化参数
    def _sourceToValue(self, paramList,sourceNode=None):
        """
        1.根据source，从workfolwInput、workfolwVariable、stepOutput、_getFunctionValue中获取参数值；常数和input不需要额外获取
        2.转换参数个格式
        """
        curSourceNode = self
        if sourceNode is not None:
            curSourceNode = sourceNode

        for param in paramList:
            #1.根据source，从workfolwInput、workfolwVariable、stepOutput、_getFunctionValue中获取参数值；常数和input不需要额外获取
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
            try:
                #2.转换参数个格式
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
                elif param["type"] == "list":
                    try:
                        param["value"] = json.loads(param["value"])
                    except:
                        param["value"] = None
            except:
                pass
        return paramList

    # 解析公式,待完善
    def _getFunctionValue(self, fun):
        value=fun
        return value


    #控件——开始流程
    def _control_workflowStart(self):
        print("流程开始")

    #控件——结束流程
    def _control_workflowEnd(self):
        print("流程结束")

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
        #getjob时，需查找children中未完成的for循环
        #在pjob中增加forList，存放for的状态，每套一层for，增加一条记录；完成或break一个循环，删除列表最后一条记录
        #输入list或length
        #输出element、number、state
        pass

    def _control_continue(self):
        #continue时，查找pjob中forList的最后一条数据作为当前for
        pass

    def _control_break(self):
        #结束循环，删除pjob中forList的最后一条记录
        pass

'''
    # 设置任务
    def set_job(self, jsonFromPage):
        pass

    # 保存任务
    def save_job(self):
        pass

    # 删除任务
    def del_job(self):
        pass

    # 开始任务
    def start_job(self):
        # 寻找开始步骤并执行
        step_run(start)

    # 暂停任务
    def pause_job(self):
        pass

    # 中止任务
    def stop_job(self):
        pass

    # 继续任务
    def continue_job(self,Step):
        pass

    # 运行结束
    def end_job(self):
        pass
    # 结束并输出

    # 运行步骤
    def step_run(self,Step):
        # 运行并执行下一步，直至end
        if Step.type == "CONTROL"
            # 执行控件
            control_run(Step)
        elif Step.type == "COMPONENT"
            # 执行组件
            component_run(Step)
        elif self.workflowInfo.type == "WORKFLOW"

        # 执行流程
        workflow_run(Step)

        if not laststep:
            step_run(next)
        else ：
        end_job()


    # 重试步骤
    def step_retry(self,Step):
        pass


    # 跳过步骤
    def step_skip(self,Step):
        pass


    # 执行控件
    def run_control(self,Step):


    # 执行并输出

    # 执行组件
    def run_component(self,Step):


    # 执行并输出

    # 执行流程
    def run_workflow(self,Step):
        # 执行并输出
        childJob = Job(workflow_guid=Step.WORKFLOW.guid, parentJob=Job.jobInfo.guid)
        childJob.set_job(Step.inputs)
        childJob.save_job()
        childJob.start_job()


    #开始流程
    def workflow_sart(instance):
        # 获取实例信息
        instance = getinstance(instanceid)
        # 获取流程信息
        workflow = getworkflow(instance.workflowid)

        # 创建流程运行数据
        workflowrun = new workflowrun()
        # 先从实例中获取input配置信息
        workflowrun.inputs = instance.inputs
        # 再从页面中获取页面输入的input信息
        workflowrun.inputs = getInputsFormPage()

        # 获取input实际值
        # input来源暂定3种，1.页面输入；2.常数；3.指定函数
        for input in workflowrun.inputs:
            if input.source='input':
                input.curvalue=input.value
            if input.source='constant':
                input.curvalue = input.value
            if input.source='function':
                input.curvalue = getFunctionValue(input.value)
        # 追加系统输入
        input.append(systeminput)
        #保存流程运行数据
        workflowrun.save()

        # 找到并允许开始步骤
        startStep=workflow.steps.fliter(modelguid='开始',modelType='TSDRMCONTROL')
        step_run(startStep,workflowrun)

    def step_run(step,workflowrun):
        # 从流程中获取当前步骤的input配置信息
        steprun.inputs = step.inputs
        for input in steprun.inputs:
            # 获取input实际值
            # input来源暂定5种
            #     1.来自流程输入
            #     2.来自步骤输出
            #     3.变量
            #     4.常数
            #     5.函数
            if input.source=="1":
                # 根据参数名查找流程input
                input.curvalue = workflowrun.inputs[input.value].curvalue
            if input.source == "2":
                # 根据$拆分，第一位是步骤名，第二位是参数名
                from_step,from_param = input.value.split('^')
                input.curvalue = workflowrun.steprun.fliter(stepid=from_step).outputs[from_param].curvalue
            if input.source == "3":
                # 根据参数名查找流程变量
                input.curvalue = workflowrun.variables[input.value].curvalue
            if input.source == "4":
                # 直接使用常数
                input.curvalue = input.value
            if input.source=="5":
                # 调用指定函数
                input.curvalue = getFunctionValue(input.value)

        #执行步骤脚本，用json格式输出
        result_json=execute(steprun.inputs)
        #解析json格式，赋值给output，两者根据code进行匹配
        steprun.outputs = step.outputs
        for output in steprun.outputs:
            output.curvalue=result_json[output.code].value
            #将output赋值给流程内部变量
            if output.variable is not None:
                if output.variable.type=="cover":
                    workflowrun.variable[output.variable.code].curvalue = output.curvalue
        steprun.save()
        workflowrun.save()

        #结束或下一步
        if step.modelguid='结束' and step.modelType='TSDRMCONTROL':
            workflow_end(workflowrun)
        else:
            for line in steprun.lines:
                for criteria in line.criterias:
                    # 判断line上条件是否成立
                    # 获取criteria实际值,和37行步骤input相同，不再重复写
                    # criteria来源暂定5种
                    #     1.来自流程输入
                    #     2.来自步骤输出
                    #     3.变量
                    #     4.常数
                    #     5.函数
                    criteria.criteria_left.curvalue=get(criteria.criteria_left.value)
                    criteria.criteria_right.curvalue = get(criteria.criteria_right.value)
                    if eval(criteria.criteria_left.curvalue + criteria.char + criteria.criteria_right):
                        step_run(line.nextPoint, workflowrun)

    def workflow_end(workflowrun):
        # 获取流程output配置信息
        for output in workflowrun.outputs:
            # 获取output实际值
            # output来源暂定5种
            #     1.来自流程输入
            #     2.来自步骤输出
            #     3.变量
            #     4.常数
            #     5.函数
            if output.source=="1":
                # 根据参数名查找流程input
                output.curvalue = workflowrun.inputs[input.value].curvalue
            if output.source == "2":
                # 根据$拆分，第一位是步骤名，第二位是参数名
                from_step,from_param = input.value.split('$')
                output.curvalue = workflowrun.steprun.fliter(stepid=from_step).outputs[from_param].curvalue
            if output.source == "3":
                # 根据参数名查找流程变量
                output.curvalue = workflowrun.variables[input.value].curvalue
            if output.source == "4":
                # 直接使用常数
                output.curvalue = input.value
            if output.source=="5":
                # 调用指定函数
                output.curvalue = getFunctionValue(input.value)
        #追加系统输出
        output.append(systemoutput)
        workflowrun.state="结束"
        workflowrun.save()
'''

# #解析XML
# def _xmlToList(self,xml,xpath):
#     nodelist =[]
#     if xml is not None and xml != "":
#         xml = etree.fromstring(xml)
#         nodeList = xml.xpath(xpath)
#         for node in nodeList:
#             nodelist.append(self._xmlToList_child(node))
#     return nodelist
#
# #解析XML子项
# def _xmlToList_child(self,node):
#     nodelist ={}
#     nodeTagList = node.xpath('*')
#     if len(nodeTagList)>0:
#         curNode = {}
#         for tag in nodeTagList:
#             curNode[tag.tag] = tag.text
#         nodelist.append(curNode)
#     else:
#         nodelist.append(node.text)
#     return nodelist

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
    testJob.start_job()

