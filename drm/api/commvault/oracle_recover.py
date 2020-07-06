import sys
import requests
import time
import copy
import datetime
import pymysql
from xml.dom.minidom import parse, parseString
import os
from lxml import etree

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
import base64

try:
    import urllib.request as urllib
except:
    import urllib


class CV_RestApi_Token(object):
    """
    Class documentation goes here.
    it is CV Rest API

    member
        init
        login(credit) return None/token
        setAccess
    """

    def __init__(self):
        """
        Constructor
        """
        # super().__init__()
        self.service = 'http://<<server>>:<<port>>/SearchSvc/CVWebService.svc/'
        self.credit = {"webaddr": "", "port": "", "username": "",
                       "passwd": "", "token": "", "lastlogin": 0}
        self.isLogin = False
        self.msg = ""
        self.sendText = ""
        self.receiveText = ""

    def getTokenString(self):
        return self.credit["token"]

    def login(self, credit):
        if self.isLogin == False:
            self.credit["token"] = None
            self.credit["lastlogin"] = 0

        try:
            self.credit["webaddr"] = credit["webaddr"]
            self.credit["port"] = credit["port"]
            self.credit["username"] = credit["username"]
            self.credit["passwd"] = credit["passwd"]
            self.credit["token"] = credit["token"]
            self.credit["lastlogin"] = credit["lastlogin"]
        except:
            self.msg = "login information is not correct"
            return None

        if self.credit["token"] != None:
            if self.credit["token"].count("QSDK") == 1:
                diff = time.time() - self.credit["lastlogin"]
                if diff <= 550:
                    return self.credit["token"]

        self.isLogin = self._login(self.credit)
        return self.credit["token"]

    def _login(self, credit):
        """
        Constructor
        login function
        """
        self.isLogin = False
        self.credit["token"] = None
        # print(credit)
        self.service = self.service.replace(
            "<<server>>", self.credit["webaddr"])
        self.service = self.service.replace("<<port>>", self.credit["port"])

        password = base64.b64encode(
            self.credit["passwd"].encode(encoding="utf-8"))

        loginReq = '<DM2ContentIndexing_CheckCredentialReq mode="Webconsole" username="<<username>>" password="<<password>>" />'
        loginReq = loginReq.replace("<<username>>", self.credit["username"])
        loginReq = loginReq.replace("<<password>>", password.decode())
        self.sendText = self.service + 'Login' + loginReq
        try:
            r = requests.post(self.service + 'Login', data=loginReq)
        except:
            self.msg = "Connect Failed: webaddr " + \
                self.credit["webaddr"] + " port " + self.credit["port"]
            return False
        if r.status_code == 200:
            try:
                root = ET.fromstring(r.text)
            except:
                self.msg = "return string is not formatted"
                return False

            if 'token' in root.attrib:
                self.credit["token"] = root.attrib['token']
                if self.credit["token"].count("QSDK") == 1:
                    self.isLogin = True
                    self.credit["lastlogin"] = time.time()
                    self.msg = "Login Successful"

                    return True
                else:
                    self.msg = "Login Failed: username " + \
                        self.credit["username"] + \
                        " passwd " + self.credit["passwd"]
        else:
            self.msg = "Connect Failed: webaddr " + \
                self.credit["webaddr"] + " port " + self.credit["port"]

        return False

    def checkLogin(self):
        return self.login(self.credit)


class CV_RestApi(object):
    """
    Class documentation goes here.
    it is CV Rest API
    Base Class for CV RestAPI
    attrib
        service is CV webaddr service string
        msg is error/success msg

    member
        init
        login(credit) return None/token
        setAccess
    """

    def __init__(self, token):
        """
        Constructor
        """
        super(CV_RestApi, self).__init__()
        self.service = 'http://<<server>>:<<port>>/SearchSvc/CVWebService.svc/'
        self.webaddr = token.credit["webaddr"]
        self.port = token.credit["port"]
        self.service = self.service.replace(
            "<<server>>", token.credit["webaddr"])
        self.service = self.service.replace("<<port>>", token.credit["port"])
        self.token = token
        self.msg = ""
        self.sendText = ""
        self.receiveText = ""

    def _rest_cmd(self, restCmd, command, updatecmd=""):
        token = self.token.checkLogin()
        if token == None:
            self.msg = "did not get token"
            return None

        clientPropsReq = self.service + command
        self.sendText = clientPropsReq

        try:
            update = updatecmd.encode(encoding="utf-8")
        except:
            update = updatecmd
        headers = {'Cookie2': token}

        if restCmd == "GET":
            try:
                r = requests.get(clientPropsReq, data=update, headers=headers)
            except:
                self.msg = "Connect Failed: webaddr " + self.webaddr + " port " + self.port
                return None

        if restCmd == "POST":
            try:
                r = requests.post(clientPropsReq, data=update, headers=headers)
            except:
                self.msg = "Connect Failed: webaddr " + self.webaddr + " port " + self.port
                return None

        if restCmd == "PUT":
            try:
                r = requests.put(clientPropsReq, data=update, headers=headers)
            except:
                self.msg = "Connect Failed: webaddr " + self.webaddr + " port " + self.port
                return None

        if restCmd == "DEL":
            try:
                r = requests.delete(
                    clientPropsReq, data=update, headers=headers)
            except:
                self.msg = "Connect Failed: webaddr " + self.webaddr + " port " + self.port
                return None

        if restCmd == "QCMD":
            try:
                r = requests.post(clientPropsReq, data=update, headers=headers)
            except:
                self.msg = "Connect Failed: webaddr " + self.webaddr + " port " + self.port
                return None

        if r.status_code == 200 or r.status_code == 201:
            self.receiveText = r.text
        else:
            self.receiveText = r.status_code
            self.msg = 'Failure: webaddr ' + self.webaddr + \
                " port " + self.port + " retcode: %d" % r.status_code

        return self.receiveText

    def getCmd(self, command, updatecmd=""):
        """
        Constructor
        get command function
        """
        retString = self._rest_cmd("GET", command, updatecmd)
        # if tag:
        #     with open(r"C:\Users\Administrator\Desktop\{0}.xml".format(tag), "w") as f:
        #         f.write(retString)
        try:
            return ET.fromstring(retString)
        except:
            self.msg = "receive string is not XML format"
            return None

    def postCmd(self, command, updatecmd=""):
        """
        Constructor
        get command function
        """
        retString = self._rest_cmd("POST", command, updatecmd)
        try:
            respRoot = ET.fromstring(retString)
            respEle = respRoot.findall(".//response")
            errorCode = ""
            for node in respEle:
                errorCode = node.attrib["errorCode"]
            if errorCode == "0":
                self.msg = "Set successfully"
                return retString
            else:
                try:
                    errString = node.attrib["errorString"]
                    self.msg = "PostCmd:" + command + "ErrCode: " + \
                        errorCode + "ErrString:" + errString
                except:
                    self.msg = "post command:" + command + " Error Code: " + \
                        errorCode + " receive text is " + self.receiveText
                    pass
            return None
        except:
            self.msg = "receive string is not XML format:" + self.receiveText
            return None

    def delCmd(self, command, updatecmd=""):
        # DELETE <webservice>/Backupset/{backupsetId}
        retString = self._rest_cmd("DELETE", command, updatecmd)
        try:
            respRoot = ET.fromstring(retString)
            respEle = respRoot.findall(".//response")
            errorCode = ""
            for node in respEle:
                errorCode = node.attrib["errorCode"]
            if errorCode == "0":
                self.msg = "Set successfully"
                return True
            self.msg = "del command:" + command + " xml format:" + updatecmd + \
                " Error Code: " + errorCode + " receive text is " + self.receiveText
            return False
        except:
            self.msg = "receive string is not XML format:" + self.receiveText
            return False

    def putCmd(self, command, updatecmd=""):
        # PUT <webservice>/Backupset/{backupsetId}
        retString = self._rest_cmd("PUT", command, updatecmd)
        try:
            respRoot = ET.fromstring(retString)
            respEle = respRoot.findall(".//response")
            errorCode = ""
            for node in respEle:
                errorCode = node.attrib["errorCode"]
            if errorCode == "0":
                self.msg = "Set successfully"
                return retString
            self.msg = "del command:" + command + " xml format:" + updatecmd + \
                " Error Code: " + errorCode + " receive text is " + self.receiveText
            return None
        except:
            self.msg = "receive string is not XML format:" + self.receiveText
            return None

    def qCmd(self, command, updatecmd=""):
        """
        Constructor
        get command function
        """
        retString = self._rest_cmd("QCMD", command, updatecmd)
        try:
            respRoot = ET.fromstring(retString)
            respjob = respRoot.findall(".//jobIds")
            for node in respjob:
                return True
            respEle = respRoot.findall(".//response")
            errorCode = ""
            for node in respEle:
                errorCode = node.attrib["errorCode"]
            if errorCode == "0":
                self.msg = "Set successfully"
                return True
            else:
                try:
                    errString = node.attrib["errorString"]
                    self.msg = "qcmd command:" + command + " Error Code: " + \
                        errorCode + " ErrString: " + errString
                except:
                    self.msg = "qcmd command:" + command + " Error Code: " + \
                        errorCode + " receive text is " + self.receiveText
                    pass
            return False
        except:
            # traceback.print_exc()
            return retString


class CV_GetAllInformation(CV_RestApi):
    """
    class CV_getAllInformation is get total information class
    include client, subclient, storagePolice, schdule, joblist
    spList = {"storagePolicyId", "storagePolicyName"}
    schduleList = {"taskName", "associatedObjects", "taskType", "runUserId", "taskId", "ownerId", "description", "ownerName", "policyType", "GUID", "alertId"}
    clientList = {"clientId", "clientName", "_type_"}

    getSPlist return storage Police list
    getSchduleList return schdule List
    getClientList return client List
    getJobList return job list

    """

    def __init__(self, token):
        """
        Constructor
        """
        super(CV_GetAllInformation, self).__init__(token)

        self.SPList = []
        self.SchduleList = []
        self.clientList = []
        self.jobList = []
        self.vmClientList = []
        self.vmProxyList = []

        self.vmDCName = []
        self.vmESXHost = []
        self.vmDataStore = []
        self.vmList = []

    def getJobList(self, clientId, type="backup", appTypeName=None, backupsetName=None, subclientName=None, start=None,
                   end=None):
        statusList = {"Running": "运行", "Waiting": "等待", "Pending": "未决", "Suspend": "终止", "Completed": "完成",
                      "Failed": "失败", "Failed to Start": "启动失败", "Killed": "杀掉"}
        '''
        Running
        Waiting
        Pending
        Suspend
        Pending
        Suspended
        Kill Pending
        Interrupt Pending
        Interrupted
        Queued
        Running (cannot be verified)
        Abnormal Terminated Cleanup
        Completed
        Completed w/ one or more errors
        Completed w/ one or more warnings
        Committed
        Failed
        Failed to Start
        Killed
        '''
        del self.jobList[:]

        command = "/Job?clientId=<<clientId>>"
        param = ""
        if type != None:
            param = "&jobFilter=<<type>>"
        cmd = command + param
        cmd = cmd.replace("<<clientId>>", clientId)
        cmd = cmd.replace("<<type>>", type)
        resp = self.getCmd(cmd)

        if resp == None:
            return None

        # print(resp)
        # print(self.receiveText)
        activePhysicalNode = resp.findall(".//jobs/jobSummary")
        for node in activePhysicalNode:
            # if start != None:
            # if end != None:
            # print(node.attrib)
            if appTypeName != None:
                if appTypeName not in node.attrib["appTypeName"]:
                    continue
            if backupsetName != None:
                if backupsetName not in node.attrib["backupSetName"]:
                    continue
            if subclientName != None:
                if subclientName not in node.attrib["subclientName"]:
                    continue
            status = node.attrib["status"]
            try:
                node.attrib["status"] = statusList[status]
            except:
                node.attrib["status"] = status
            self.jobList.append(node.attrib)
        return self.jobList

    def apitest(self,command):
        return self.getCmd(command)



class CV_Client(CV_GetAllInformation):
    def __init__(self, token, client=None):
        """
        Constructor
        """
        super(CV_Client, self).__init__(token)
        self.client = client
        self.backupsetList = []
        self.subclientList = []
        self.platform = {"platform": None,
                         "ProcessorType": 0, "hostName": None}
        self.clientInfo = {"clientName": None, "clientId": None, "platform": self.platform, "backupsetList": [],
                           "agentList": []}
        # self.backupInfo = {"clientId":None, "clientName":None, "agentType":None, "agentId":None, "backupsetId":None, "backupsetName":None, "instanceName":None, "instanceId":None}

        self.isNewClient = True
        self.getClientInfo(client)
        self.schedule_description = []

    def getClient(self, client):
        # get clientName and clientId
        clientInfo = self.clientInfo
        if isinstance(client, (int)):
            command = "Client/<<client>>"
            command = command.replace("<<client>>", str(client))
            resp = self.getCmd(command)
            if resp == None:
                return False
            clientEntity = resp.findall(".//clientEntity")
            if clientEntity == []:
                return False
            clientInfo["clientId"] = clientEntity[0].attrib["clientId"]
            clientInfo["clientName"] = clientEntity[0].attrib["clientName"]
        else:
            command = "GetId?clientName=<<client>>"
            command = command.replace("<<client>>", client)
            resp = self.getCmd(command)
            if resp == None:
                return False
            clientInfo["clientId"] = resp.attrib["clientId"]
            if int(clientInfo["clientId"]) <= 0:
                return False
            clientInfo["clientName"] = resp.attrib["clientName"]
        return True

    def getClientInfo(self, client):
        self.isNewClient = True

        if self.token == None or client == None:
            return None
        # get client
        if self.getClient(client) == False:
            return None
        clientInfo = self.clientInfo
        self.isNewClient = False
        # get backupsetList
        clientInfo["backupsetList"] = self.getBackupsetList(
            clientInfo["clientId"])
        # get platform
        self.getClientOSInfo(clientInfo["clientId"])
        # get agent list
        clientInfo["agentList"] = self.getClientAgentList(
            clientInfo["clientId"])
        if (clientInfo["platform"]["platform"]).upper() == "ANY":
            clientInfo["instance"] = self.getClientInstance(
                clientInfo["clientId"])
        return clientInfo

    def getClientOSInfo(self, clientId):
        if clientId == None:
            return None
        command = "Client/<<clientId>>"
        command = command.replace("<<clientId>>", clientId)
        resp = self.getCmd(command)

        try:
            osinfo = resp.findall(".//OsDisplayInfo")
            self.platform["platform"] = osinfo[0].attrib["OSName"]
            self.platform["ProcessorType"] = osinfo[0].attrib["ProcessorType"]

            hostnames = resp.findall(".//clientEntity")
            self.platform["hostName"] = hostnames[0].attrib["hostName"]
        except:
            self.msg = "error get client platform"

    def getClientAgentList(self, clientId):
        agentList = []
        agent = {}
        if clientId == None:
            return None
        command = "Agent?clientId=<<clientId>>"
        command = command.replace("<<clientId>>", clientId)
        resp = self.getCmd(command)
        # print(self.receiveText)
        try:
            activePhysicalNode = resp.findall(".//idaEntity")
            for node in activePhysicalNode:
                # print("agent list")
                # print(node.attrib)
                agent["clientName"] = node.attrib["clientName"]
                agent["agentType"] = node.attrib["appName"]
                agent["appId"] = node.attrib["applicationId"]
                agentList.append(copy.deepcopy(agent))
        except:
            self.msg = "error get agent type"
            pass
        return agentList

    def getSubClientList(self, clientId):
        # subclientInfo {'subclientName','instanceName','backupsetName','appName','applicationId','clientName','instanceId','backupsetId','subclientId', 'clientId'}
        subList = self.subclientList
        del subList[:]
        if clientId == None:
            return None
        cmd = 'Subclient?clientId=<<clientId>>'
        cmd = cmd.replace("<<clientId>>", clientId)
        subclient = self.getCmd(cmd)
        if subclient == None:
            return None
        activePhysicalNode = subclient.findall(".//subClientEntity")
        for node in activePhysicalNode:
            subList.append(node.attrib)
        return subList

    def getBackupsetList(self, clientId):
        self.getSubClientList(clientId)
        flag = 0
        del self.backupsetList[:]
        backupsetInfo = {"clientId": -1, "clientName": None, "agentType": None, "agentId": None, "backupsetId": -1,
                         "backupsetName": None, "instanceName": None, "instanceId": -1}
        for node in self.subclientList:
            # backupsetId = int(node["backupsetId"])
            flag = 0
            for item in self.backupsetList:
                if node["backupsetId"] == item["backupsetId"]:
                    flag = 1
                    break
            if flag == 1:
                continue
            backupset = copy.deepcopy(backupsetInfo)
            backupset["clientName"] = node["clientName"]
            backupset["agentType"] = node["appName"]
            backupset["backupsetName"] = node["backupsetName"]
            backupset["instanceName"] = node["instanceName"]
            backupset["backupsetId"] = node["backupsetId"]
            backupset["instanceId"] = node["instanceId"]
            backupset["clientId"] = node["clientId"]
            backupset["subclientId"] = node["subclientId"]

            self.backupsetList.append(backupset)
        return self.backupsetList


class CV_Backupset(CV_Client):
    def __init__(self, token, client, agentType, backupset=None):
        """
        Constructor
        """
        super(CV_Backupset, self).__init__(token, client)
        self.isNewBackupset = True
        self.backupsetInfo = None
        self.getBackupset(agentType, backupset)
        self.curBrowselist = []

    def getIsNewBackupset(self):
        return self.isNewBackupset

    def getBackupset(self, agentType, backupset=None):
        # param client is clientName or clientId
        # param backupset is backupsetName or backupsetId
        # return backupset info backupset
        # None is no backupset
        self.isNewBackupset = True
        self.backupsetInfo = None
        # print(agentType, backupset)
        if agentType == None and backupset == None:
            return None
        for node in self.backupsetList:
            if backupset == None:
                if agentType in node["agentType"]:
                    self.backupsetInfo = node
                    self.isNewBackupset = False
                    return self.backupsetInfo
            else:
                # print(node)
                if "Virtual" in agentType or "File System" in agentType:
                    if node["backupsetName"] == backupset and agentType in node["agentType"]:
                        self.backupsetInfo = node
                        self.isNewBackupset = False
                        return self.backupsetInfo
                else:
                    if node["instanceName"].upper() == backupset.upper() and node[
                            "agentType"].upper() in agentType.upper():
                        self.backupsetInfo = node
                        self.isNewBackupset = False
                        return self.backupsetInfo
                '''
                if node["backupsetId"] == backupset:
                    self.backupsetInfo = node
                    #self._getSubclientList(node["backupsetId"])
                    self.isNewBackupset = False
                    return self.backupsetInfo
                if node["instanceName"] == backupset:
                    self.backupsetInfo = node
                    #self._getSubclientList(node["backupsetId"])
                    self.isNewBackupset = False
                    return self.backupsetInfo
                '''
        return None

    def restoreOracleBackupset(self, source, dest, operator):
        # param client is clientName or clientId
        # operator is {"instanceName":, "destClient":, "restoreTime":, "browseJobId":None}
        # return JobId
        # or -1 is error
        jobId = -1
        instance = self.backupsetInfo["instanceName"]
        if operator != None:
            keys = operator.keys()
            if "restoreTime" not in keys:
                self.msg = "operator - no restoreTime"
                return jobId
            if "browseJobId" not in keys:
                self.msg = "operator - no browseJobId"
                return jobId
            if "data_path" not in keys:
                self.msg = "operator - no data_path"
                return jobId
            if "copy_priority" not in keys:
                self.msg = "operator - no copy_priority"
                return jobId
            if "db_open" not in keys:
                self.msg = "operator - no db_open"
                return jobId
            if "curSCN" not in keys:
                self.msg = "operator - no curSCN"
                return jobId
        else:
            self.msg = "param not set"
            return jobId

        sourceClient = source
        destClient = dest
        restoreTime = operator["restoreTime"]
        data_path = operator["data_path"]
        copy_priority = operator["copy_priority"]
        curSCN = operator["curSCN"] if operator["curSCN"] else ""
        db_open = operator["db_open"]

        try:
            copy_priority = int(copy_priority)
        except ValueError as e:
            copy_priority = 1

        try:
            db_open = int(db_open)
        except ValueError as e:
            db_open = 1

        if db_open == 2:
            db_open = "false"
        else:
            db_open = "true"

        copyPrecedence_xml = '''                                        
        <copyPrecedence>
            <copyPrecedenceApplicable>false</copyPrecedenceApplicable>
            <synchronousCopyPrecedence>1</synchronousCopyPrecedence>
            <copyPrecedence>0</copyPrecedence>
        </copyPrecedence>
        '''
        # 2:表示选择辅助拷贝优先
        if copy_priority == 2:
            copyPrecedence_xml = '''                                        
            <copyPrecedence>
                <copyPrecedenceApplicable>true</copyPrecedenceApplicable>
                <synchronousCopyPrecedence>2</synchronousCopyPrecedence>
                <copyPrecedence>2</copyPrecedence>
            </copyPrecedence>
            '''
        data_path_xml = '''
        <redirectItemsPresent>false</redirectItemsPresent>
        <validate>false</validate>
        <renamePathForAllTablespaces></renamePathForAllTablespaces>
        <redirectAllItemsSelected>false</redirectAllItemsSelected>
        '''
        if data_path:
            data_path_xml = '''
            <redirectItemsPresent>true</redirectItemsPresent>
            <validate>false</validate>
            <renamePathForAllTablespaces>{data_path}</renamePathForAllTablespaces>
            <redirectAllItemsSelected>true</redirectAllItemsSelected>
            '''.format(data_path=data_path)

        restoreoracleXML = '''
            <TMMsg_CreateTaskReq>
                <taskInfo>
                    <associations>
                        <appName>Oracle</appName>
                        <backupsetName>default</backupsetName>
                        <clientName>{sourceClient}</clientName>
                        <instanceName>{instance}</instanceName>
                        <subclientName>default</subclientName>
                    </associations>
                    <subTasks>
                        <options>
                            <backupOpts>
                                <backupLevel>INCREMENTAL</backupLevel>
                                <vsaBackupOptions/>
                            </backupOpts>
                            <commonOpts>
                                <!--User Description for the job-->
                                <jobDescription></jobDescription>
                                <prePostOpts>
                                    <postRecoveryCommand></postRecoveryCommand>
                                    <preRecoveryCommand></preRecoveryCommand>
                                    <runPostWhenFail>false</runPostWhenFail>
                                </prePostOpts>
                                <startUpOpts>
                                    <priority>166</priority>
                                    <startInSuspendedState>false</startInSuspendedState>
                                    <useDefaultPriority>true</useDefaultPriority>
                                </startUpOpts>
                            </commonOpts>
                            <restoreOptions>
                                <browseOption>
                                    <backupset>
                                        <backupsetName>default</backupsetName>
                                        <clientName>{sourceClient}</clientName>
                                    </backupset>
                                    <commCellId>2</commCellId>
                                    <listMedia>false</listMedia>
                                    <mediaOption>
                                        {copyPrecedence_xml}
                                        <drive/>
                                        <drivePool/>
                                        <library/>
                                        <mediaAgent/>
                                        <proxyForSnapClients>
                                            <clientName></clientName>
                                        </proxyForSnapClients>
                                    </mediaOption>
                                    <noImage>false</noImage>
                                    <timeRange/>
                                    <timeZone>
                                        <TimeZoneName>(UTC+08:00)&#x5317;&#x4eAC;&#xFF0C;&#x91CD;&#x5e86;&#xFF0C;&#x9999;&#x6e2F;&#x7279;&#x522B;&#x884C;&#x653F;&#x533A;&#xFF0C;&#x4e4C;&#x9C81;&#x6728;&#x9F50;</TimeZoneName>
                                    </timeZone>
                                    <useExactIndex>false</useExactIndex>
                                </browseOption>
                                <commonOptions>
                                    <clusterDBBackedup>false</clusterDBBackedup>
                                    <detectRegularExpression>true</detectRegularExpression>
                                    <ignoreNamespaceRequirements>false</ignoreNamespaceRequirements>
                                    <isDBArchiveRestore>false</isDBArchiveRestore>
                                    <isFromBrowseBackup>false</isFromBrowseBackup>
                                    <onePassRestore>false</onePassRestore>
                                    <recoverAllProtectedMails>false</recoverAllProtectedMails>
                                    <restoreDeviceFilesAsRegularFiles>false</restoreDeviceFilesAsRegularFiles>
                                    <restoreSpaceRestrictions>false</restoreSpaceRestrictions>
                                    <restoreToDisk>false</restoreToDisk>
                                    <revert>false</revert>
                                    <skipErrorsAndContinue>false</skipErrorsAndContinue>
                                    <useRmanRestore>true</useRmanRestore>
                                </commonOptions>
                                <destination>
                                    <destClient>
                                        <clientName>{destClient}</clientName>
                                    </destClient>
                                </destination>
                                <fileOption>
                                    <sourceItem>SID&#xFF1A; jxcredit</sourceItem>
                                </fileOption>
                                <oracleOpt>
                                    <SPFilePath></SPFilePath>
                                    <SPFileTime>
                                        <timeValue>{restoreTime}</timeValue>
                                    </SPFileTime>
                                    <archiveLog>false</archiveLog>
                                    <archiveLogBy>DEFAULT</archiveLogBy>
                                    <autoDetectDevice>true</autoDetectDevice>
                                    <backupValidationOnly>false</backupValidationOnly>
                                    <catalogConnect1></catalogConnect1>
                                    <catalogConnect2>
                                        <password>||#5!M2NmZTNlZWI4NTRlOGFhNjRlMDE1NWJlYzAxOTY3NGQ1&#xA;</password>
                                    </catalogConnect2>
                                    <catalogConnect3></catalogConnect3>
                                    <checkReadOnly>false</checkReadOnly>
                                    <cloneEnv>false</cloneEnv>
                                    <controlFilePath></controlFilePath>
                                    <controlFileTime>
                                        <timeValue>{restoreTime}</timeValue>
                                    </controlFileTime>
                                    <controleFileScript></controleFileScript>
                                    <ctrlBackupPiece></ctrlBackupPiece>
                                    <ctrlFileBackupType>AUTO_BACKUP</ctrlFileBackupType>
                                    <ctrlRestoreFrom>true</ctrlRestoreFrom>
                                    <customizeScript>false</customizeScript>
                                    <databaseScript></databaseScript>
                                    <dbIncarnation>0</dbIncarnation>
                                    <deviceType>UTIL_FILE</deviceType>
                                    <doNotRecoverRedoLogs>false</doNotRecoverRedoLogs>
                                    <duplicate>false</duplicate>
                                    <duplicateActiveDatabase>false</duplicateActiveDatabase>
                                    <duplicateNoFileNamecheck>false</duplicateNoFileNamecheck>
                                    <duplicateStandby>false</duplicateStandby>
                                    <duplicateStandbyDoRecover>false</duplicateStandbyDoRecover>
                                    <duplicateStandbySID></duplicateStandbySID>
                                    <duplicateTo>false</duplicateTo>
                                    <duplicateToLogFile>false</duplicateToLogFile>
                                    <duplicateToName></duplicateToName>
                                    <duplicateToOpenRestricted>false</duplicateToOpenRestricted>
                                    <duplicateToPFile></duplicateToPFile>
                                    <duplicateToSkipReadOnly>false</duplicateToSkipReadOnly>
                                    <duplicateToSkipTablespace>false</duplicateToSkipTablespace>
                                    <endLSNNum>1</endLSNNum>
                                    <isDeviceTypeSelected>false</isDeviceTypeSelected>
                                    <logTarget></logTarget>
                                    <logTime>
                                        <fromTimeValue>{restoreTime}</fromTimeValue>
                                        <toTimeValue>{restoreTime}</toTimeValue>
                                    </logTime>
                                    <maxOpenFiles>0</maxOpenFiles>
                                    <mountDatabase>false</mountDatabase>
                                    <noCatalog>true</noCatalog>
                                    <openDatabase>{db_open}</openDatabase>
                                    <osID>2</osID>
                                    <partialRestore>false</partialRestore>
                                    <recover>true</recover>
                                    <recoverFrom>2</recoverFrom>
                                    <recoverSCN>{curSCN}</recoverSCN>
                                    <recoverTime>
                                        <timeValue>{restoreTime}</timeValue>
                                    </recoverTime>
                                    <redirectAllItemsSelected>false</redirectAllItemsSelected>
                                    {data_path_xml}
                                    <resetDatabase>false</resetDatabase>
                                    <resetLogs>1</resetLogs>
                                    <restoreByTag>false</restoreByTag>
                                    <restoreControlFile>true</restoreControlFile>
                                    <restoreData>true</restoreData>
                                    <restoreDataTag>false</restoreDataTag>
                                    <restoreFailover>false</restoreFailover>
                                    <restoreFrom>0</restoreFrom>
                                    <restoreSPFile>false</restoreSPFile>
                                    <restoreStream>1</restoreStream>
                                    <restoreTablespace>false</restoreTablespace>
                                    <restoreTag></restoreTag>
                                    <restoreTime/>
                                    <setDBId>true</setDBId>
                                    <skipTargetConnection>false</skipTargetConnection>
                                    <spFileBackupPiece></spFileBackupPiece>
                                    <spFileBackupType>AUTO_BACKUP</spFileBackupType>
                                    <spFileRestoreFrom>false</spFileRestoreFrom>
                                    <specifyControlFile>false</specifyControlFile>
                                    <specifyControlFileTime>false</specifyControlFileTime>
                                    <specifySPFile>false</specifySPFile>
                                    <specifySPFileTime>false</specifySPFileTime>
                                    <startLSNNum>1</startLSNNum>
                                    <switchDatabaseMode>false</switchDatabaseMode>
                                    <tableViewRestore>false</tableViewRestore>
                                    <tag></tag>
                                    <timeZone>
                                        <TimeZoneName>(UTC+08:00)&#x5317;&#x4eAC;&#xFF0C;&#x91CD;&#x5e86;&#xFF0C;&#x9999;&#x6e2F;&#x7279;&#x522B;&#x884C;&#x653F;&#x533A;&#xFF0C;&#x4e4C;&#x9C81;&#x6728;&#x9F50;</TimeZoneName>
                                    </timeZone>
                                    <useEndLSN>false</useEndLSN>
                                    <useEndLog>false</useEndLog>
                                    <useStartLSN>false</useStartLSN>
                                    <useStartLog>true</useStartLog>
                                </oracleOpt>
                                <volumeRstOption>
                                    <volumeLeveRestore>false</volumeLeveRestore>
                                </volumeRstOption>
                            </restoreOptions>
                        </options>
                        <subTask>
                            <operationType>RESTORE</operationType>
                            <subTaskType>RESTORE</subTaskType>
                        </subTask>
                    </subTasks>
                    <task>
                        <alert>
                            <alertName></alertName>
                        </alert>
                        <initiatedFrom>COMMANDLINE</initiatedFrom>
                        <policyType>DATA_PROTECTION</policyType>
                        <taskFlags>
                            <disabled>false</disabled>
                        </taskFlags>
                        <taskType>IMMEDIATE</taskType>
                    </task>
                </taskInfo>
            </TMMsg_CreateTaskReq>'''.format(sourceClient=sourceClient, destClient=destClient, instance=instance,
                                             restoreTime="{0:%Y-%m-%d %H:%M:%S}".format(
                                                 datetime.datetime.now()),
                                             copyPrecedence_xml=copyPrecedence_xml, data_path_xml=data_path_xml,
                                             curSCN=curSCN, db_open=db_open)

        if restoreTime:
            restoreoracleXML = '''
            <TMMsg_CreateTaskReq>
              <taskInfo>
                <associations>
                  <appName>Oracle</appName>
                  <backupsetName>default</backupsetName>
                  <clientName>{sourceClient}</clientName>
                  <instanceName>{instance}</instanceName>
                  <subclientName></subclientName>
                </associations>
                <subTasks>
                  <options>
                    <backupOpts>
                      <backupLevel>INCREMENTAL</backupLevel>
                      <vsaBackupOptions/>
                    </backupOpts>
                    <commonOpts>
                      <!--User Description for the job-->
                      <jobDescription></jobDescription>
                      <prePostOpts>
                        <postRecoveryCommand></postRecoveryCommand>
                        <preRecoveryCommand></preRecoveryCommand>
                        <runPostWhenFail>false</runPostWhenFail>
                      </prePostOpts>
                      <startUpOpts>
                        <priority>166</priority>
                        <startInSuspendedState>false</startInSuspendedState>
                        <useDefaultPriority>true</useDefaultPriority>
                      </startUpOpts>
                    </commonOpts>
                    <restoreOptions>
                      <browseOption>
                        <backupset>
                          <backupsetName>default</backupsetName>
                          <clientName>{sourceClient}</clientName>
                        </backupset>
                        <commCellId>2</commCellId>
                        <listMedia>false</listMedia>
                        <mediaOption>
                          {copyPrecedence_xml}
                          <drive/>
                          <drivePool/>
                          <library/>
                          <mediaAgent/>
                          <proxyForSnapClients>
                            <clientName></clientName>
                          </proxyForSnapClients>
                        </mediaOption>
                        <noImage>false</noImage>
                        <timeRange/>
                        <timeZone>
                          <TimeZoneName>(UTC+08:00)&#x5317;&#x4eAC;&#xFF0C;&#x91CD;&#x5e86;&#xFF0C;&#x9999;&#x6e2F;&#x7279;&#x522B;&#x884C;&#x653F;&#x533A;&#xFF0C;&#x4e4C;&#x9C81;&#x6728;&#x9F50;</TimeZoneName>
                        </timeZone>
                        <useExactIndex>false</useExactIndex>
                      </browseOption>
                      <commonOptions>
                        <clusterDBBackedup>false</clusterDBBackedup>
                        <detectRegularExpression>true</detectRegularExpression>
                        <ignoreNamespaceRequirements>false</ignoreNamespaceRequirements>
                        <isDBArchiveRestore>false</isDBArchiveRestore>
                        <isFromBrowseBackup>false</isFromBrowseBackup>
                        <onePassRestore>false</onePassRestore>
                        <recoverAllProtectedMails>false</recoverAllProtectedMails>
                        <restoreDeviceFilesAsRegularFiles>false</restoreDeviceFilesAsRegularFiles>
                        <restoreSpaceRestrictions>false</restoreSpaceRestrictions>
                        <restoreToDisk>false</restoreToDisk>
                        <revert>false</revert>
                        <skipErrorsAndContinue>false</skipErrorsAndContinue>
                        <useRmanRestore>true</useRmanRestore>
                      </commonOptions>
                      <destination>
                        <destClient>
                          <clientName>{destClient}</clientName>
                        </destClient>
                      </destination>
                      <fileOption>
                        <sourceItem>SID&#xFF1A; bbsp</sourceItem>
                      </fileOption>
                      <oracleOpt>
                        <SPFilePath></SPFilePath>
                        <SPFileTime>
                          <timeValue>{restoreTime}</timeValue>
                        </SPFileTime>
                        <archiveLog>false</archiveLog>
                        <archiveLogBy>DEFAULT</archiveLogBy>
                        <autoDetectDevice>true</autoDetectDevice>
                        <backupValidationOnly>false</backupValidationOnly>
                        <catalogConnect1></catalogConnect1>
                        <catalogConnect2>
                          <password>||#5!M2NmZTNlZWI4NTRlOGFhNjRlMDE1NWJlYzAxOTY3NGQ1&#xA;</password>
                        </catalogConnect2>
                        <catalogConnect3></catalogConnect3>
                        <checkReadOnly>false</checkReadOnly>
                        <cloneEnv>false</cloneEnv>
                        <controlFilePath></controlFilePath>
                        <controlFileTime>
                          <timeValue>{restoreTime}</timeValue>
                        </controlFileTime>
                        <controleFileScript></controleFileScript>
                        <ctrlBackupPiece></ctrlBackupPiece>
                        <ctrlFileBackupType>AUTO_BACKUP</ctrlFileBackupType>
                        <ctrlRestoreFrom>true</ctrlRestoreFrom>
                        <customizeScript>false</customizeScript>
                        <databaseScript></databaseScript>
                        <dbIncarnation>0</dbIncarnation>
                        <deviceType>UTIL_FILE</deviceType>
                        <doNotRecoverRedoLogs>false</doNotRecoverRedoLogs>
                        <duplicate>false</duplicate>
                        <duplicateActiveDatabase>false</duplicateActiveDatabase>
                        <duplicateNoFileNamecheck>false</duplicateNoFileNamecheck>
                        <duplicateStandby>false</duplicateStandby>
                        <duplicateStandbyDoRecover>false</duplicateStandbyDoRecover>
                        <duplicateStandbySID></duplicateStandbySID>
                        <duplicateTo>false</duplicateTo>
                        <duplicateToLogFile>false</duplicateToLogFile>
                        <duplicateToName></duplicateToName>
                        <duplicateToOpenRestricted>false</duplicateToOpenRestricted>
                        <duplicateToPFile></duplicateToPFile>
                        <duplicateToSkipReadOnly>false</duplicateToSkipReadOnly>
                        <duplicateToSkipTablespace>false</duplicateToSkipTablespace>
                        <endLSNNum>1</endLSNNum>
                        <isDeviceTypeSelected>false</isDeviceTypeSelected>
                        <logTarget></logTarget>
                        <logTime>
                          <fromTimeValue>{restoreTime}</fromTimeValue>
                          <toTimeValue>{restoreTime}</toTimeValue>
                        </logTime>
                        <maxOpenFiles>0</maxOpenFiles>
                        <mountDatabase>false</mountDatabase>
                        <noCatalog>true</noCatalog>
                        <openDatabase>{db_open}</openDatabase>
                        <osID>2</osID>
                        <partialRestore>false</partialRestore>
                        <recover>true</recover>
                        <recoverFrom>1</recoverFrom>
                        <recoverSCN></recoverSCN>
                        <recoverTime>
                          <timeValue>{restoreTime}</timeValue>
                        </recoverTime>
                        {data_path_xml}
                        <resetDatabase>false</resetDatabase>
                        <resetLogs>1</resetLogs>
                        <restoreByTag>false</restoreByTag>
                        <restoreControlFile>true</restoreControlFile>
                        <restoreData>true</restoreData>
                        <restoreDataTag>false</restoreDataTag>
                        <restoreFailover>false</restoreFailover>
                        <restoreFrom>1</restoreFrom>
                        <restoreSPFile>false</restoreSPFile>
                        <restoreStream>1</restoreStream>
                        <restoreTablespace>false</restoreTablespace>
                        <restoreTag></restoreTag>
                        <restoreTime>
                          <timeValue>2019-11-03 13:43:44</timeValue>
                        </restoreTime>
                        <setDBId>true</setDBId>
                        <skipTargetConnection>false</skipTargetConnection>
                        <spFileBackupPiece></spFileBackupPiece>
                        <spFileBackupType>AUTO_BACKUP</spFileBackupType>
                        <spFileRestoreFrom>false</spFileRestoreFrom>
                        <specifyControlFile>false</specifyControlFile>
                        <specifyControlFileTime>false</specifyControlFileTime>
                        <specifySPFile>false</specifySPFile>
                        <specifySPFileTime>false</specifySPFileTime>
                        <startLSNNum>1</startLSNNum>
                        <switchDatabaseMode>false</switchDatabaseMode>
                        <tableViewRestore>false</tableViewRestore>
                        <tag></tag>
                        <timeZone>
                          <TimeZoneName>(UTC+08:00)&#x5317;&#x4eAC;&#xFF0C;&#x91CD;&#x5e86;&#xFF0C;&#x9999;&#x6e2F;&#x7279;&#x522B;&#x884C;&#x653F;&#x533A;&#xFF0C;&#x4e4C;&#x9C81;&#x6728;&#x9F50;</TimeZoneName>
                        </timeZone>
                        <useEndLSN>false</useEndLSN>
                        <useEndLog>false</useEndLog>
                        <useStartLSN>false</useStartLSN>
                        <useStartLog>true</useStartLog>
                      </oracleOpt>
                      <volumeRstOption>
                        <volumeLeveRestore>false</volumeLeveRestore>
                      </volumeRstOption>
                    </restoreOptions>
                  </options>
                  <subTask>
                    <operationType>RESTORE</operationType>
                    <subTaskType>RESTORE</subTaskType>
                  </subTask>
                </subTasks>
                <task>
                  <alert>
                    <alertName></alertName>
                  </alert>
                  <initiatedFrom>COMMANDLINE</initiatedFrom>
                  <policyType>DATA_PROTECTION</policyType>
                  <taskFlags>
                    <disabled>false</disabled>
                  </taskFlags>
                  <taskType>IMMEDIATE</taskType>
                </task>
              </taskInfo>
            
            </TMMsg_CreateTaskReq>
            '''.format(sourceClient=sourceClient, destClient=destClient, instance=instance,
                       restoreTime=restoreTime, copyPrecedence_xml=copyPrecedence_xml,
                       data_path_xml=data_path_xml, db_open=db_open)

        try:
            root = ET.fromstring(restoreoracleXML)
        except:
            self.msg = "Error:parse xml: " + restoreoracleXML
            return jobId

        xmlString = ""
        xmlString = ET.tostring(root, encoding='utf-8', method='xml')
        if self.qCmd("QCommand/qoperation execute", xmlString):
            try:
                root = ET.fromstring(self.receiveText)
            except:
                self.msg = "unknown error" + self.receiveText
                return jobId

            nodes = root.findall(".//jobIds")
            for node in nodes:
                self.msg = "jobId is: " + node.attrib["val"]
                jobId = int(node.attrib["val"])
                return jobId
            self.msg = "unknown error:" + self.receiveText
        return jobId

    def restoreOracleRacBackupset(self, source, dest, operator):
        # param client is clientName or clientId
        # operator is {"instanceName":, "destClient":, "restoreTime":, "browseJobId":None}
        # return JobId
        # or -1 is error
        jobId = -1
        instance = self.backupsetInfo["instanceName"]
        if operator != None:
            keys = operator.keys()
            if "restoreTime" not in keys:
                self.msg = "operator - no restoreTime"
                return jobId
            if "browseJobId" not in keys:
                self.msg = "operator - no browseJobId"
                return jobId
            if "data_path" not in keys:
                self.msg = "operator - no data_path"
                return jobId
            if "copy_priority" not in keys:
                self.msg = "operator - no copy_priority"
                return jobId
            if "db_open" not in keys:
                self.msg = "operator - no db_open"
                return jobId
            if "curSCN" not in keys:
                self.msg = "operator - no curSCN"
                return jobId
        else:
            self.msg = "param not set"
            return jobId

        sourceClient = source
        destClient = dest
        restoreTime = operator["restoreTime"]
        browseJobId = operator["browseJobId"]
        data_path = operator["data_path"]
        copy_priority = operator["copy_priority"]
        db_open = operator["db_open"]
        curSCN = operator["curSCN"] if operator["curSCN"] else ""

        try:
            copy_priority = int(copy_priority)
        except ValueError as e:
            copy_priority = 1

        try:
            db_open = int(db_open)
        except ValueError as e:
            db_open = 1

        if db_open == 2:
            db_open = "false"
        else:
            db_open = "true"

        copyPrecedence_xml = '''                                        
        <copyPrecedence>
            <copyPrecedenceApplicable>false</copyPrecedenceApplicable>
            <synchronousCopyPrecedence>1</synchronousCopyPrecedence>
            <copyPrecedence>0</copyPrecedence>
        </copyPrecedence>
        '''
        # 2:表示选择辅助拷贝优先
        if copy_priority == 2:
            copyPrecedence_xml = '''                                        
            <copyPrecedence>
                <copyPrecedenceApplicable>true</copyPrecedenceApplicable>
                <synchronousCopyPrecedence>2</synchronousCopyPrecedence>
                <copyPrecedence>2</copyPrecedence>
            </copyPrecedence>
            '''
        data_path_xml = '''
        <redirectItemsPresent>false</redirectItemsPresent>
        <validate>false</validate>
        <renamePathForAllTablespaces></renamePathForAllTablespaces>
        <redirectAllItemsSelected>false</redirectAllItemsSelected>
        '''
        if data_path:
            data_path_xml = '''
            <redirectItemsPresent>true</redirectItemsPresent>
            <validate>false</validate>
            <renamePathForAllTablespaces>{data_path}</renamePathForAllTablespaces>
            <redirectAllItemsSelected>true</redirectAllItemsSelected>
            '''.format(data_path=data_path)

        restoreoracleRacXML = '''
            <TMMsg_CreateTaskReq>
              <taskInfo>
                <associations>
                  <appName>Oracle RAC</appName>
                  <backupsetName>defaultBackupSet</backupsetName>
                  <clientName>{sourceClient}</clientName>
                  <instanceName>{instance}</instanceName>
                  <subclientName>default</subclientName>
                </associations>
                <subTasks>
                  <options>
                    <backupOpts>
                      <backupLevel>INCREMENTAL</backupLevel>
                      <vsaBackupOptions/>
                    </backupOpts>
                    <commonOpts>
                      <!--User Description for the job-->
                      <jobDescription></jobDescription>
                      <startUpOpts>
                        <priority>166</priority>
                        <startInSuspendedState>false</startInSuspendedState>
                        <useDefaultPriority>true</useDefaultPriority>
                      </startUpOpts>
                    </commonOpts>
                    <restoreOptions>
                      <browseOption>
                        <backupset>
                          <backupsetName>defaultBackupSet</backupsetName>
                          <clientName>{sourceClient}</clientName>
                        </backupset>
                        <commCellId>2</commCellId>
                        <listMedia>false</listMedia>
                        <mediaOption>
                          {copyPrecedence_xml}
                          <drive/>
                          <drivePool/>
                          <library/>
                          <mediaAgent/>
                          <proxyForSnapClients>
                            <clientName></clientName>
                          </proxyForSnapClients>
                        </mediaOption>
                        <noImage>false</noImage>
                        <timeRange/>
                        <timeZone>
                          <TimeZoneName>(UTC+08:00)&#x5317;&#x4eAC;&#xFF0C;&#x91CD;&#x5e86;&#xFF0C;&#x9999;&#x6e2F;&#x7279;&#x522B;&#x884C;&#x653F;&#x533A;&#xFF0C;&#x4e4C;&#x9C81;&#x6728;&#x9F50;</TimeZoneName>
                        </timeZone>
                        <useExactIndex>false</useExactIndex>
                      </browseOption>
                      <commonOptions>
                        <clusterDBBackedup>false</clusterDBBackedup>
                        <detectRegularExpression>true</detectRegularExpression>
                        <ignoreNamespaceRequirements>false</ignoreNamespaceRequirements>
                        <isDBArchiveRestore>false</isDBArchiveRestore>
                        <isFromBrowseBackup>false</isFromBrowseBackup>
                        <onePassRestore>false</onePassRestore>
                        <recoverAllProtectedMails>false</recoverAllProtectedMails>
                        <restoreDeviceFilesAsRegularFiles>false</restoreDeviceFilesAsRegularFiles>
                        <restoreSpaceRestrictions>false</restoreSpaceRestrictions>
                        <restoreToDisk>false</restoreToDisk>
                        <revert>false</revert>
                        <skipErrorsAndContinue>false</skipErrorsAndContinue>
                        <useRmanRestore>true</useRmanRestore>
                      </commonOptions>
                      <destination>
                        <destClient>
                          <clientName>{destClient}</clientName>
                        </destClient>
                        <destinationInstance>
                          <appName>Oracle</appName>
                          <clientName>{destClient}</clientName>
                          <instanceName>{instance}</instanceName>
                        </destinationInstance>
                      </destination>
                      <fileOption>
                        <sourceItem/>
                      </fileOption>
                      <oracleOpt>
                        <SPFilePath></SPFilePath>
                        <SPFileTime>
                          <timeValue>{restoreTime}</timeValue>
                        </SPFileTime>
                        <archiveLog>false</archiveLog>
                        <archiveLogBy>DEFAULT</archiveLogBy>
                        <autoDetectDevice>true</autoDetectDevice>
                        <backupValidationOnly>false</backupValidationOnly>
                        <catalogConnect1></catalogConnect1>
                        <catalogConnect2>
                          <password>||#5!M2NmZTNlZWI4NTRlOGFhNjRlMDE1NWJlYzAxOTY3NGQ1&#xA;</password>
                        </catalogConnect2>
                        <catalogConnect3></catalogConnect3>
                        <checkReadOnly>false</checkReadOnly>
                        <cloneEnv>false</cloneEnv>
                        <controlFilePath></controlFilePath>
                        <controlFileTime>
                          <timeValue>{restoreTime}</timeValue>
                        </controlFileTime>
                        <controleFileScript></controleFileScript>
                        <ctrlBackupPiece></ctrlBackupPiece>
                        <ctrlFileBackupType>AUTO_BACKUP</ctrlFileBackupType>
                        <ctrlRestoreFrom>true</ctrlRestoreFrom>
                        <customizeScript>false</customizeScript>
                        <databaseScript></databaseScript>
                        <dbIncarnation>0</dbIncarnation>
                        <deviceType>UTIL_FILE</deviceType>
                        <doNotRecoverRedoLogs>false</doNotRecoverRedoLogs>
                        <duplicate>false</duplicate>
                        <duplicateActiveDatabase>false</duplicateActiveDatabase>
                        <duplicateNoFileNamecheck>false</duplicateNoFileNamecheck>
                        <duplicateStandby>false</duplicateStandby>
                        <duplicateStandbyDoRecover>false</duplicateStandbyDoRecover>
                        <duplicateStandbySID></duplicateStandbySID>
                        <duplicateTo>false</duplicateTo>
                        <duplicateToLogFile>false</duplicateToLogFile>
                        <duplicateToName></duplicateToName>
                        <duplicateToOpenRestricted>false</duplicateToOpenRestricted>
                        <duplicateToPFile></duplicateToPFile>
                        <duplicateToSkipReadOnly>false</duplicateToSkipReadOnly>
                        <duplicateToSkipTablespace>false</duplicateToSkipTablespace>
                        <endLSNNum>1</endLSNNum>
                        <isDeviceTypeSelected>false</isDeviceTypeSelected>
                        <logTarget></logTarget>
                        <logTime>
                          <fromTimeValue>{restoreTime}</fromTimeValue>
                          <toTimeValue>{restoreTime}</toTimeValue>
                        </logTime>
                        <maxOpenFiles>0</maxOpenFiles>
                        <mountDatabase>false</mountDatabase>
                        <noCatalog>true</noCatalog>
                        <openDatabase>{db_open}</openDatabase>
                        <osID>2</osID>
                        <partialRestore>false</partialRestore>
                        <racDataStreamAllcation>1 0</racDataStreamAllcation>
                        <racDataStreamAllcation>2 0</racDataStreamAllcation>
                        <recover>true</recover>
                        <recoverFrom>4</recoverFrom>
                        <recoverSCN>{curSCN}</recoverSCN>
                        <recoverTime>
                          <timeValue>{restoreTime}</timeValue>
                        </recoverTime>
                        {data_path_xml}
                        <resetDatabase>false</resetDatabase>
                        <resetLogs>1</resetLogs>
                        <restoreByTag>false</restoreByTag>
                        <restoreControlFile>true</restoreControlFile>
                        <restoreData>true</restoreData>
                        <restoreDataTag>false</restoreDataTag>
                        <restoreFailover>false</restoreFailover>
                        <restoreFrom>0</restoreFrom>
                        <restoreInstanceLog>false</restoreInstanceLog>
                        <restoreSPFile>false</restoreSPFile>
                        <restoreStream>1</restoreStream>
                        <restoreTablespace>false</restoreTablespace>
                        <restoreTag></restoreTag>
                        <restoreTime/>
                        <setDBId>true</setDBId>
                        <skipTargetConnection>false</skipTargetConnection>
                        <spFileBackupPiece></spFileBackupPiece>
                        <spFileBackupType>AUTO_BACKUP</spFileBackupType>
                        <spFileRestoreFrom>false</spFileRestoreFrom>
                        <specifyControlFile>false</specifyControlFile>
                        <specifyControlFileTime>false</specifyControlFileTime>
                        <specifySPFile>false</specifySPFile>
                        <specifySPFileTime>false</specifySPFileTime>
                        <startLSNNum>1</startLSNNum>
                        <switchDatabaseMode>false</switchDatabaseMode>
                        <tableViewRestore>false</tableViewRestore>
                        <tag></tag>
                        <threadId>1</threadId>
                        <timeZone>
                          <TimeZoneName>(UTC+08:00)&#x5317;&#x4eAC;&#xFF0C;&#x91CD;&#x5e86;&#xFF0C;&#x9999;&#x6e2F;&#x7279;&#x522B;&#x884C;&#x653F;&#x533A;&#xFF0C;&#x4e4C;&#x9C81;&#x6728;&#x9F50;</TimeZoneName>
                        </timeZone>
                        <useEndLSN>false</useEndLSN>
                        <useEndLog>false</useEndLog>
                        <useStartLSN>false</useStartLSN>
                        <useStartLog>true</useStartLog>
                      </oracleOpt>
                      <volumeRstOption>
                        <volumeLeveRestore>false</volumeLeveRestore>
                      </volumeRstOption>
                    </restoreOptions>
                  </options>
                  <subTask>
                    <operationType>RESTORE</operationType>
                    <subTaskType>RESTORE</subTaskType>
                  </subTask>
                </subTasks>
                <task>
                  <alert>
                    <alertName></alertName>
                  </alert>
                  <initiatedFrom>COMMANDLINE</initiatedFrom>
                  <policyType>DATA_PROTECTION</policyType>
                  <taskFlags>
                    <disabled>false</disabled>
                  </taskFlags>
                  <taskType>IMMEDIATE</taskType>
                </task>
              </taskInfo>
            </TMMsg_CreateTaskReq>'''.format(sourceClient=sourceClient, destClient=destClient, instance=instance,
                                             restoreTime="{0:%Y-%m-%d %H:%M:%S}".format(
                                                 datetime.datetime.now()),
                                             copyPrecedence_xml=copyPrecedence_xml, data_path_xml=data_path_xml, curSCN=curSCN, db_open=db_open)
        if restoreTime:
            restoreoracleRacXML = """
            <TMMsg_CreateTaskReq>
              <taskInfo>
                <associations>
                  <appName>Oracle RAC</appName>
                  <backupsetName>defaultBackupSet</backupsetName>
                  <clientName>{sourceClient}</clientName>
                  <instanceName>{instance}</instanceName>
                  <subclientName>default</subclientName>
                </associations>
                <subTasks>
                  <options>
                    <backupOpts>
                      <backupLevel>INCREMENTAL</backupLevel>
                      <vsaBackupOptions/>
                    </backupOpts>
                    <commonOpts>
                      <!--User Description for the job-->
                      <jobDescription></jobDescription>
                      <startUpOpts>
                        <priority>166</priority>
                        <startInSuspendedState>false</startInSuspendedState>
                        <useDefaultPriority>true</useDefaultPriority>
                      </startUpOpts>
                    </commonOpts>
                    <restoreOptions>
                      <browseOption>
                        <backupset>
                          <backupsetName>defaultBackupSet</backupsetName>
                          <clientName>{sourceClient}</clientName>
                        </backupset>
                        <commCellId>2</commCellId>
                        <listMedia>false</listMedia>
                        <mediaOption>
                          {copyPrecedence_xml}
                          <drive/>
                          <drivePool/>
                          <library/>
                          <mediaAgent/>
                          <proxyForSnapClients>
                            <clientName></clientName>
                          </proxyForSnapClients>
                        </mediaOption>
                        <noImage>false</noImage>
                        <timeRange/>
                        <timeZone>
                          <TimeZoneName>(UTC+08:00)&#x5317;&#x4eAC;&#xFF0C;&#x91CD;&#x5e86;&#xFF0C;&#x9999;&#x6e2F;&#x7279;&#x522B;&#x884C;&#x653F;&#x533A;&#xFF0C;&#x4e4C;&#x9C81;&#x6728;&#x9F50;</TimeZoneName>
                        </timeZone>
                        <useExactIndex>false</useExactIndex>
                      </browseOption>
                      <commonOptions>
                        <clusterDBBackedup>false</clusterDBBackedup>
                        <detectRegularExpression>true</detectRegularExpression>
                        <ignoreNamespaceRequirements>false</ignoreNamespaceRequirements>
                        <isDBArchiveRestore>false</isDBArchiveRestore>
                        <isFromBrowseBackup>false</isFromBrowseBackup>
                        <onePassRestore>false</onePassRestore>
                        <recoverAllProtectedMails>false</recoverAllProtectedMails>
                        <restoreDeviceFilesAsRegularFiles>false</restoreDeviceFilesAsRegularFiles>
                        <restoreSpaceRestrictions>false</restoreSpaceRestrictions>
                        <restoreToDisk>false</restoreToDisk>
                        <revert>false</revert>
                        <skipErrorsAndContinue>false</skipErrorsAndContinue>
                        <useRmanRestore>true</useRmanRestore>
                      </commonOptions>
                      <destination>
                        <destClient>
                          <clientName>{destClient}</clientName>
                        </destClient>
                        <destinationInstance>
                          <appName>Oracle</appName>
                          <clientName>{destClient}</clientName>
                          <instanceName>{instance}</instanceName>
                        </destinationInstance>
                      </destination>
                      <fileOption>
                        <sourceItem>SID&#xFF1A; zfxtora</sourceItem>
                      </fileOption>
                      <oracleOpt>
                        <SPFilePath></SPFilePath>
                        <SPFileTime>
                          <timeValue>{restoreTime}</timeValue>
                        </SPFileTime>
                        <archiveLog>false</archiveLog>
                        <archiveLogBy>DEFAULT</archiveLogBy>
                        <autoDetectDevice>true</autoDetectDevice>
                        <backupValidationOnly>false</backupValidationOnly>
                        <catalogConnect1></catalogConnect1>
                        <catalogConnect2>
                          <password>||#5!M2NmZTNlZWI4NTRlOGFhNjRlMDE1NWJlYzAxOTY3NGQ1&#xA;</password>
                        </catalogConnect2>
                        <catalogConnect3></catalogConnect3>
                        <checkReadOnly>false</checkReadOnly>
                        <cloneEnv>false</cloneEnv>
                        <controlFilePath></controlFilePath>
                        <controlFileTime>
                          <timeValue>{restoreTime}</timeValue>
                        </controlFileTime>
                        <controleFileScript></controleFileScript>
                        <ctrlBackupPiece></ctrlBackupPiece>
                        <ctrlFileBackupType>AUTO_BACKUP</ctrlFileBackupType>
                        <ctrlRestoreFrom>true</ctrlRestoreFrom>
                        <customizeScript>false</customizeScript>
                        <databaseScript></databaseScript>
                        <dbIncarnation>0</dbIncarnation>
                        <deviceType>UTIL_FILE</deviceType>
                        <doNotRecoverRedoLogs>false</doNotRecoverRedoLogs>
                        <duplicate>false</duplicate>
                        <duplicateActiveDatabase>false</duplicateActiveDatabase>
                        <duplicateNoFileNamecheck>false</duplicateNoFileNamecheck>
                        <duplicateStandby>false</duplicateStandby>
                        <duplicateStandbyDoRecover>false</duplicateStandbyDoRecover>
                        <duplicateStandbySID></duplicateStandbySID>
                        <duplicateTo>false</duplicateTo>
                        <duplicateToLogFile>false</duplicateToLogFile>
                        <duplicateToName></duplicateToName>
                        <duplicateToOpenRestricted>false</duplicateToOpenRestricted>
                        <duplicateToPFile></duplicateToPFile>
                        <duplicateToSkipReadOnly>false</duplicateToSkipReadOnly>
                        <duplicateToSkipTablespace>false</duplicateToSkipTablespace>
                        <endLSNNum>1</endLSNNum>
                        <isDeviceTypeSelected>false</isDeviceTypeSelected>
                        <logTarget></logTarget>
                        <logTime>
                          <fromTimeValue>{restoreTime}</fromTimeValue>
                          <toTimeValue>{restoreTime}</toTimeValue>
                        </logTime>
                        <maxOpenFiles>0</maxOpenFiles>
                        <mountDatabase>false</mountDatabase>
                        <noCatalog>true</noCatalog>
                        <openDatabase>{db_open}</openDatabase>
                        <osID>2</osID>
                        <partialRestore>false</partialRestore>
                        <racDataStreamAllcation>1 0</racDataStreamAllcation>
                        <racDataStreamAllcation>2 0</racDataStreamAllcation>
                        <recover>true</recover>
                        <recoverFrom>1</recoverFrom>
                        <recoverSCN></recoverSCN>
                        <recoverTime>
                          <timeValue>{restoreTime}</timeValue>
                        </recoverTime>
                        {data_path_xml}
                        <resetDatabase>false</resetDatabase>
                        <resetLogs>1</resetLogs>
                        <restoreByTag>false</restoreByTag>
                        <restoreControlFile>true</restoreControlFile>
                        <restoreData>true</restoreData>
                        <restoreDataTag>false</restoreDataTag>
                        <restoreFailover>false</restoreFailover>
                        <restoreFrom>1</restoreFrom>
                        <restoreInstanceLog>false</restoreInstanceLog>
                        <restoreSPFile>false</restoreSPFile>
                        <restoreStream>1</restoreStream>
                        <restoreTablespace>false</restoreTablespace>
                        <restoreTag></restoreTag>
                        <restoreTime>
                          <timeValue>{restoreTime}</timeValue>
                        </restoreTime>
                        <setDBId>true</setDBId>
                        <skipTargetConnection>false</skipTargetConnection>
                        <spFileBackupPiece></spFileBackupPiece>
                        <spFileBackupType>AUTO_BACKUP</spFileBackupType>
                        <spFileRestoreFrom>false</spFileRestoreFrom>
                        <specifyControlFile>false</specifyControlFile>
                        <specifyControlFileTime>false</specifyControlFileTime>
                        <specifySPFile>false</specifySPFile>
                        <specifySPFileTime>false</specifySPFileTime>
                        <startLSNNum>1</startLSNNum>
                        <switchDatabaseMode>false</switchDatabaseMode>
                        <tableViewRestore>false</tableViewRestore>
                        <tag></tag>
                        <threadId>1</threadId>
                        <timeZone>
                          <TimeZoneName>(UTC+08:00)&#x5317;&#x4eAC;&#xFF0C;&#x91CD;&#x5e86;&#xFF0C;&#x9999;&#x6e2F;&#x7279;&#x522B;&#x884C;&#x653F;&#x533A;&#xFF0C;&#x4e4C;&#x9C81;&#x6728;&#x9F50;</TimeZoneName>
                        </timeZone>
                        <useEndLSN>false</useEndLSN>
                        <useEndLog>false</useEndLog>
                        <useStartLSN>false</useStartLSN>
                        <useStartLog>true</useStartLog>
                      </oracleOpt>
                      <volumeRstOption>
                        <volumeLeveRestore>false</volumeLeveRestore>
                      </volumeRstOption>
                    </restoreOptions>
                  </options>
                  <subTask>
                    <operationType>RESTORE</operationType>
                    <subTaskType>RESTORE</subTaskType>
                  </subTask>
                </subTasks>
                <task>
                  <alert>
                    <alertName></alertName>
                  </alert>
                  <initiatedFrom>COMMANDLINE</initiatedFrom>
                  <policyType>DATA_PROTECTION</policyType>
                  <taskFlags>
                    <disabled>false</disabled>
                  </taskFlags>
                  <taskType>IMMEDIATE</taskType>
                </task>
              </taskInfo>
            </TMMsg_CreateTaskReq>""".format(sourceClient=sourceClient, destClient=destClient, instance=instance, restoreTime=restoreTime,
                                             copyPrecedence_xml=copyPrecedence_xml, data_path_xml=data_path_xml, db_open=db_open)

        try:
            root = ET.fromstring(restoreoracleRacXML)
        except:
            self.msg = "Error:parse xml: " + restoreoracleRacXML
            return jobId

        xmlString = ""
        xmlString = ET.tostring(root, encoding='utf-8', method='xml')
        if self.qCmd("QCommand/qoperation execute", xmlString):
            try:
                root = ET.fromstring(self.receiveText)
            except:
                self.msg = "unknown error" + self.receiveText
                return jobId

            nodes = root.findall(".//jobIds")
            for node in nodes:
                self.msg = "jobId is: " + node.attrib["val"]
                jobId = int(node.attrib["val"])
                return jobId
            self.msg = "unknown error:" + self.receiveText
        return jobId


class CV_API(object):
    def __init__(self, cvToken):
        """
        Constructor
        """
        super(CV_API, self).__init__()
        self.token = cvToken
        self.msg = None

    def getClientInfo(self, client):
        clientInfo = CV_Client(self.token)
        info = clientInfo.getClientInfo(client)
        self.msg = clientInfo.msg
        return info

    def getJobList(self, client, agentType=None, backupset=None, type="backup"):
        # param client is clientName or clientId or None is all client
        # param agentType =
        # backupset is backsetupName or backsetupId
        # operator is backup, restore, admin and others
        # return job List, {"jobID":, "clientName":, "clientId":, "Start":, "End":, }
        # None is no job
        joblist = []
        jobRec = {}
        info = CV_GetAllInformation(self.token)
        clientRec = CV_Client(self.token, client)
        list = info.getJobList(clientId=clientRec.clientInfo["clientId"], type=type, appTypeName=agentType,
                               backupsetName=backupset, subclientName=None, start=None, end=None)

        for node in list:
            jobRec["jobId"] = node["jobId"]
            jobRec["status"] = node["status"]
            jobRec["client"] = clientRec.clientInfo["clientName"]
            jobRec["agentType"] = node["appTypeName"]
            jobRec["backupSetName"] = node["backupSetName"]
            # jobRec["destClient"] = node["destClientName"]
            jobRec["jobType"] = node["jobType"]
            jobRec["Level"] = node["backupLevel"]
            # 流量
            jobRec["appSize"] = node["sizeOfApplication"]
            # 磁盘容量
            jobRec["diskSize"] = node["sizeOfMediaOnDisk"]
            jobRec["StartTime"] = node["jobStartTime"]
            jobRec["LastTime"] = node["lastUpdateTime"]
            joblist.append(copy.deepcopy(jobRec))
        self.msg = info.msg
        return joblist

    def getBackupset(self, client, agentType, backupset=None):
        # param client is clientName or clientId
        # param backupset is backupsetName or backupsetId
        # return backupset info backupset
        # None is no backupset
        info = CV_Backupset(self.token, client, agentType)
        backupsetInfo = info.getBackupset(agentType, backupset)
        self.msg = info.msg
        return backupsetInfo

    def restoreOracleBackupset(self, source, dest, instance, operator=None):
        # param client is clientName or clientId
        # operator is {"instanceName":, "destClient":, "restoreTime":, "data_path":None}
        # return JobId
        # or -1 is error

        # print(client, backupset, credit, content)
        sourceBackupset = CV_Backupset(
            self.token, source, "Oracle Database", instance)
        destBackupset = CV_Backupset(
            self.token, dest, "Oracle Database", instance)
        if sourceBackupset.getIsNewBackupset() == True:
            self.msg = "there is not this oracle sid " + source
            return False
        jobId = sourceBackupset.restoreOracleBackupset(source, dest, operator)
        self.msg = sourceBackupset.msg
        return jobId

    def restoreOracleRacBackupset(self, source, dest, instance, operator=None):
        # param client is clientName or clientId
        # operator is {"instanceName":, "destClient":, "restoreTime":, "browseJobId":None}
        # return JobId
        # or -1 is error

        # print(client, backupset, credit, content)
        sourceBackupset = CV_Backupset(
            self.token, source, "Oracle RAC", instance)
        destBackupset = CV_Backupset(self.token, dest, "Oracle RAC", instance)
        if sourceBackupset.getIsNewBackupset() == True:
            self.msg = "there is not this oracle rac sid" + source
            return False
        if destBackupset.getIsNewBackupset() == True:
            self.msg = "there is not this oracle rac sid" + dest
            return False
        jobId = sourceBackupset.restoreOracleRacBackupset(
            source, dest, operator)
        self.msg = sourceBackupset.msg
        return jobId



class DoMysql(object):
    def __init__(self, host, user, password, db):
        self.conn = pymysql.Connect(
            host=host,
            port=3306,
            user=user,
            password=password,
            db=db,
            charset='utf8',
            cursorclass=pymysql.cursors.DictCursor 
        )
        self.cursor = self.conn.cursor()

    def fetchAll(self, sql):
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def fetchOne(self, sql):
        self.cursor.execute(sql)
        return self.cursor.fetchone()

    def insert_one(self, sql):
        result = self.cursor.execute(sql)
        self.conn.commit()
        return result

    def insert_many(self, sql, datas):
        result = self.cursor.executemany(sql, datas)
        self.conn.commit()
        return result

    def update(self, sql):
        result = self.cursor.execute(sql)
        self.conn.commit()
        return result

    def close(self):
        self.cursor.close()
        self.conn.close()


def run(origin, target, instance, processrun_id):
    #############################################
    # 从config/db_config.xml中读取数据库认证信息 #
    #############################################
    db_host, db_name, db_user, db_password = '', '', '', ''

    try:
        db_config_file = os.path.join(os.path.join(os.path.join(
            os.getcwd(), "drm"), "config"), "db_config.xml")

        with open(db_config_file, "r") as f:
            content = etree.XML(f.read())
            db_config = content.xpath('./DB_CONFIG')
            if db_config:
                db_config = db_config[0]
                db_host = db_config.attrib.get("db_host", "")
                db_name = db_config.attrib.get("db_name", "")
                db_user = db_config.attrib.get("db_user", "")
                db_password = db_config.attrib.get("db_password", "")
    except:
        print("获取数据库信息失败。")
        exit(1)

    db = DoMysql(db_host, db_user, db_password, db_name)

    credit_result = {}
    recovery_result = {}

    credit_sql = "SELECT t.content FROM {db_name}.drm_vendor t;".format(
        **{"db_name": db_name})
    recovery_sql = """SELECT recover_time, browse_job_id, data_path, copy_priority, curSCN, db_open FROM {db_name}.drm_processrun
                      WHERE state!='9' AND id={processrun_id};""".format(
        **{"processrun_id": processrun_id, "db_name": db_name})

    try:
        credit_result = db.fetchOne(credit_sql)
        recovery_result = db.fetchOne(recovery_sql)
    except:
        pass

    recover_time = ""
    browse_job_id = ""
    data_path = ""
    copy_priority = ""
    curSCN = ""
    db_open = ""

    if recovery_result:
        try:
            recover_time = recovery_result["recover_time"]
        except Exception as e:
            recover_time = ""

        if recover_time:
            recover_time = '{0:%Y-%m-%d %H:%M:%S}'.format(recover_time)
        else:
            recover_time = ""

        browse_job_id = recovery_result["browse_job_id"]
        data_path = recovery_result["data_path"]
        copy_priority = recovery_result["copy_priority"]
        db_open = recovery_result["db_open"]
        curSCN = recovery_result["curSCN"]

    webaddr = ""
    port = ""
    usernm = ""
    passwd = ""
    if credit_result:
        doc = parseString(credit_result["content"])
        try:
            webaddr = (doc.getElementsByTagName("webaddr"))[
                0].childNodes[0].data
        except:
            pass
        try:
            port = (doc.getElementsByTagName("port"))[0].childNodes[0].data
        except:
            pass
        try:
            usernm = (doc.getElementsByTagName("username"))[
                0].childNodes[0].data
        except:
            pass
        try:
            passwd = (doc.getElementsByTagName("passwd"))[0].childNodes[0].data
        except:
            pass

    info = {
        "webaddr": webaddr,
        "port": port,
        "username": usernm,
        "passwd": passwd,
        "token": "",
        "last_login": 0
    }

    cvToken = CV_RestApi_Token()
    cvToken.login(info)
    cvAPI = CV_API(cvToken)
    
    jobId = cvAPI.restoreOracleBackupset(origin, target, instance,
                                         {'browseJobId': browse_job_id, 'restoreTime': recover_time,
                                          'data_path': data_path, "copy_priority": copy_priority, "curSCN": curSCN,
                                          "db_open": db_open})
    # jobId = 4553295
    if jobId == -1:
        print("oracle恢复接口调用失败，{0}。".format(cvAPI.msg))
        exit(1)
    else:
        while True:
            ret = cvAPI.getJobList(origin, type="restore")
            for i in ret:
                if str(i["jobId"]) == str(jobId):
                    if i['status'] in ['运行', '等待']:
                        continue
                    elif i['status'].upper() == '完成':
                        exit(0)
                    else:
                        # oracle恢复出现异常
                        #################################
                        # 程序中不要出现其他print()      #
                        # print()将会作为输出被服务器获取#
                        #################################
                        print(jobId)
                        exit(2)
            time.sleep(4)
        #################################
        # exit() 1:调用Oracle恢复接口失败#
        #        2:Oracle恢复出现异常    #
        #        0:执行Oracle恢复成功    #
        #################################


# if len(sys.argv) == 5:
#     run(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
# else:
#     print("脚本传参出现异常。")
#     exit(1)

if __name__ == "__main__":
    info = {"webaddr": "192.168.100.149", "port": "81", "username": "admin", "passwd": "Admin@2017", "token": "",
            "lastlogin": 0}

    cvToken = CV_RestApi_Token()
    cvToken.login(info)

    cvAPI = CV_GetAllInformation(cvToken)
    ret = cvAPI.apitest("/MediaAgent")  # backup status
    xmlstr = ET.tostring(ret, encoding='utf8', method='xml')
    print(xmlstr)

    client = CV_Client(cvToken)
    print(client.getClientInfo(2))