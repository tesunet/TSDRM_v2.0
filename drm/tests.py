# from django.test import TestCase
# import sys,os
# import django
# from drm.workflow.workflow import *
# sys.path.append(os.path.dirname(__file__) + os.sep + '../')
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TSDRM.settings')
# django.setup()
# # Create your tests here.
# testJob = Job('eef392ec-8ada-11eb-9d49-a4bb6d10e0ef')
# testJob.run_job()

from drm.workflow import workflow_remote

class KVMApi():
    def __init__(self, credit):
        self.ip = credit['KvmHost']
        self.username = credit['KvmUser']
        self.password = credit['KvmPasswd']
        self.system_tag = credit['SystemType']

    def remote_linux(self, exe_cmd):
        rm_obj = workflow_remote.ServerByPara(exe_cmd, self.ip, self.username, self.password, self.system_tag)
        result = rm_obj.run(isComponent=False, linux_timeout=12 * 60)
        return result

    def test(self):
        # 获取KVM模板文件列表
        exe_cmd = r'/tmp/drm/work_for_component_2e445090-a26c-11eb-bc9a-405bd8b00cd6_33d0d440-a2a4-11eb-be46-405bd8b00cd6.sh'
        result = self.remote_linux(exe_cmd)
        return result
linuxserver_credit = {
    'KvmHost': '192.168.226.128',
    'KvmUser': 'root',
    'KvmPasswd': '123456',
    'SystemType': 'Linux',
}


result = KVMApi(linuxserver_credit).test()

print(result)


