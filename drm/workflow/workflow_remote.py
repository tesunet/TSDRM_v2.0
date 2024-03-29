"""
paramiko, pywinrm实现windows/linux脚本调用
linux下脚本语法错误,或者命令不存在等没有通过stderr变量接收到，只能添加判断条件；
windows下可以接收到错误信息并作出判断；
"""
import paramiko
import socket
import requests
import datetime
from requests.exceptions import ConnectionError
import winrm
from winrm.exceptions import WinRMTransportError, WinRMOperationTimeoutError, WinRMError


###############################################################
# 为实现 WINDOWS下执行脚本时长超时设置，对wimrm中相关类进行重写。#
###############################################################
# 重写Protocol类
class Protocol(winrm.protocol.Protocol):
    def get_command_output(self, shell_id, command_id):
        """
        Get the Output of the given shell and command
        @param string shell_id: The shell id on the remote machine.
        See #open_shell
        @param string command_id: The command id on the remote machine.
        See #run_command
        #@return [Hash] Returns a Hash with a key :exitcode and :data.
        Data is an Array of Hashes where the cooresponding key
        #   is either :stdout or :stderr.  The reason it is in an Array so so
        we can get the output in the order it ocurrs on
        #   the console.
        """
        stdout_buffer, stderr_buffer = [], []
        command_done = False

        ############################################################################
        # 限时6*60s                                                                #
        #   程序反复查看相应，如果相应成功，且在超时时限内则命令成功，否则报超时异常。 #
        #   获取响应的时长较长。                                                    #
        ############################################################################
        return_code = -1
        limited_seconds = 6 * 60
        start_time = datetime.datetime.now()
        while not command_done:
            print('get the response from windows...')
            try:
                stdout, stderr, return_code, command_done = \
                    self._raw_get_command_output(shell_id, command_id)
                stdout_buffer.append(stdout)
                stderr_buffer.append(stderr)
            except WinRMOperationTimeoutError as e:
                # this is an expected error when waiting for a long-running process, just silently retry
                pass

            end_time = datetime.datetime.now()
            delta_time = end_time - start_time
            total_seconds = delta_time.total_seconds()
            if total_seconds > limited_seconds:
                raise WinRMOperationTimeoutError()
        return b''.join(stdout_buffer), b''.join(stderr_buffer), return_code


# 重写Session类
class Session(winrm.Session):
    # TODO implement context manager methods
    def __init__(self, target, auth, **kwargs):
        username, password = auth
        self.url = self._build_url(target, kwargs.get('transport', 'plaintext'))
        self.protocol = Protocol(self.url,
                                username=username, password=password, **kwargs)


class ServerByPara(object):
    def __init__(self, cmd, host, user, password, system_choice):
        self.cmd = cmd
        self.client = paramiko.SSHClient()
        self.host = host
        self.user = user
        self.pwd = password
        self.system_choice = system_choice

    @staticmethod
    def handle_codec(content):
        """
        处理编码问题
        @content: 响应信息
        """
        try:
            content = str(content, encoding='utf-8')
        except Exception as e:
            try:
                content = str(content, encoding='gbk')
            except:
                raise Exception("编码错误")
        return content

    def exec_linux_cmd(self, isComponent, linux_timeout, port=22):
        data_init = ""
        scriptResult = ""
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.client.connect(hostname=self.host, username=self.user, password=self.pwd, timeout=5, port=port)
        except Exception as e:
            print("连接服务器失败")
            return {
                "exec_tag": 1,
                "data": "连接服务器失败 {0}".format(e),
                "message": "连接服务器失败",
            }
        try:
            stdin, stdout, stderr = self.client.exec_command(self.cmd, get_pty=True, timeout=linux_timeout)
            if stderr.read():
                exec_tag = 1
                data_init = ServerByPara.handle_codec(stderr.read())
                message = ""
            else:
                exec_tag = 0
                message = ""

                try:
                    data_init = ServerByPara.handle_codec(stdout.read())
                    if data_init:
                        data_init = " ".join(data_init.split("\r\n"))

                    if "<scriptResult>" not in data_init or "</scriptResult>" not in data_init:
                        scriptResult = data_init
                        if isComponent:
                            exec_tag = 1
                            message = "无法获取执行结果"
                        if "command not found" in data_init:  # 命令不存在
                            exec_tag = 1
                            message = "命令不存在"
                        elif "syntax error" in data_init:  # 语法错误
                            exec_tag = 1
                            message = "语法错误"
                        elif "No such file or directory" in data_init:  # 脚本不存在
                            exec_tag = 1
                            message = "脚本不存在"
                    else:
                        startindex=data_init.index("<scriptResult>")
                        endindex = data_init.index("</scriptResult>")
                        scriptResult= data_init[startindex+14:endindex]


                except Exception as e:
                    print(e)
                    exec_tag = 1
                    message = "编码错误"
        except socket.timeout as e:
            print("脚本执行超时")
            return {
                "exec_tag": 1,
                "data": scriptResult,
                "message": "脚本执行超时",
            }
        return {
            "exec_tag": exec_tag,
            "data": scriptResult,
            "message": message,
        }

    def exec_win_cmd(self, isComponent):
        scriptResult = ""
        data_init = ""
        message = ""

        try:
            s = Session(self.host, auth=(self.user, self.pwd))
            ret = s.run_cmd(self.cmd)
        except Exception as e:
            if type(e) == WinRMOperationTimeoutError:
                print("脚本执行超时")
                exec_tag = 1
                message = "脚本执行超时 {0}".format(e)
            elif type(e) in [ConnectionError, WinRMTransportError]:
                print("连接windows失败")
                exec_tag = 1
                message = "连接windows失败 {0}".format(e)
            else:
                print("执行windows脚本发生异常错误")
                exec_tag = 1
                message = "执行windows脚本发生异常错误 {0}".format(e)

            return {
                "exec_tag": exec_tag,
                "data": scriptResult,
                "message": message,
            }
        else:
            if ret.std_err:
                data_init = str(ret.std_err, encoding='gbk')
                exec_tag = 1
                # for data in ret.std_err.decode().split("\r\n"):
                #     data_init += data
                message = ""
            else:
                exec_tag = 0

                try:
                    data_init = str(ret.std_out, encoding='gbk')
                    if data_init:
                        data_init = "".join(data_init.split("\r\n"))
                except Exception as e:
                    print(e)
                    exec_tag = 1
                    message = "编码错误"
                else:
                    if '<scriptResult>' not in data_init or '</scriptResult>' not in data_init:
                        scriptResult = data_init
                        if isComponent:
                            exec_tag = 1
                            message = "无法获取执行结果"
                    else:
                        startindex = data_init.index("<scriptResult>")
                        endindex = data_init.index("</scriptResult>")
                        scriptResult = data_init[startindex + 14:endindex]

            return {
                "exec_tag": exec_tag,
                "data": scriptResult,
                "message": message,
            }

    def run(self,isComponent=False,linux_timeout=6 * 60):
        if self.system_choice == "Linux":
            result = self.exec_linux_cmd(isComponent, linux_timeout)
            if self.client:
                self.client.close()
        elif self.system_choice == "AIX":
            result = self.exec_linux_cmd(isComponent, linux_timeout, port=22)
            if self.client:
                self.client.close()
        else:
            result = self.exec_win_cmd(isComponent)
        # print(result)
        return result

if __name__ == '__main__':
    # server_obj = ServerByPara(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    # server_obj = ServerByPara(r"C:\Users\Administrator\Desktop\test_python.bat", "192.168.100.151", "administrator","tesunet@2017", "Windows")
    server_obj = ServerByPara(r"echo 中文 > C:\Users\Administrator\Desktop\test.bat",
                              "192.168.100.154", "administrator", "tesunet@2017", "Windows")
    # linux_temp_script_file = r"/tmp/drm/954/tmp_script_6486.sh&&/tmp/drm/954/tmp_script_6486.sh"
    # cmd = r"sed -i 's/\r$//' {0}&&{0}".format(linux_temp_script_file)
    # print(cmd)  # sed -i 's/\r$//' /tmp/drm/954/tmp_script_6486.sh&&/tmp/drm/954/tmp_script_6486.sh
    # server_obj = ServerByPara("mkdir -p /tmp/drm/957",
    #                           "10.64.7.43", "root", "qtdl2003", "Linux")
    # server_obj = ServerByPara("echo 中文",
    #                           "192.168.184.66", "root", "password", "Linux")
    # server_obj = ServerByPara(r"echo '你好你好你好你好你好你好你好';echo '你好你好你好你好你好你好你好';echo '你好你好你好你好你好你好你好'", "192.168.184.66", "root","password", "Linux")

    # server_obj.run()
    # print(11111111111111)
