from drm import remote
from lxml import etree


class KVMApi():
    def __init__(self, credit):
        self.ip = credit['KvmHost']
        self.username = credit['KvmUser']
        self.password = credit['KvmPasswd']
        self.system_tag = credit['SystemType']

    def remote_linux(self, exe_cmd):
        rm_obj = remote.ServerByPara(exe_cmd, self.ip, self.username, self.password, self.system_tag)
        result = rm_obj.run(succeedtext='')
        return result

    def list_of_groups(self, list_info, per_list_len):
        """
        list_info:   列表元素
        per_list_len:  每个小列表的长度
        """
        list_of_group = zip(*(iter(list_info),) * per_list_len)
        end_list = [list(i) for i in list_of_group]
        count = len(list_info) % per_list_len
        end_list.append(list_info[-count:]) if count != 0 else end_list
        return end_list

    def domstate(self, kvm_name):
        # 获取虚拟机的状态
        exe_cmd = r'virsh domstate {0}'.format(kvm_name)
        result = self.remote_linux(exe_cmd)

        return result['data']

    def kvm_all_list(self):
        # 获取所有kvm虚拟机
        exe_cmd = r'virsh list --all'
        result = self.remote_linux(exe_cmd)
        kvm_list = [x for x in result['data'].split(' ') if x]

        del kvm_list[0:3]
        kvm_list_filter = []
        for i in kvm_list:
            if i == 'shut':
                continue
            if i == 'off':
                i = 'shut off'
            kvm_list_filter.append(i)

        end_list = self.list_of_groups(kvm_list_filter, 3)
        kvm_all_list_dict = []
        for item in end_list:
            data = {}
            data['id'] = item[0]
            data['name'] = item[1]
            data['state'] = item[2]
            kvm_all_list_dict.append(data)

        return kvm_all_list_dict

    def kvm_run_list(self):
        # 获取正在运行的虚拟机
        exe_cmd = r'virsh list'
        result = self.remote_linux(exe_cmd)
        kvm_list = [x for x in result['data'].split(' ') if x]

        del kvm_list[0:3]

        end_list = self.list_of_groups(kvm_list, 3)
        kvm_all_list_dict = []
        for item in end_list:
            data = {}
            data['id'] = item[0]
            data['name'] = item[1]
            data['state'] = item[2]
            kvm_all_list_dict.append(data)

        return kvm_all_list_dict

    def start(self, kvm_name):
        # 开启虚拟机:是关闭的状态
        state = self.domstate(kvm_name)
        if state == 'shut off' or state == '关闭':
            exe_cmd = r'virsh start {0}'.format(kvm_name)
            result = self.remote_linux(exe_cmd)
            if result['data'] == 'Domain {0} started'.format(kvm_name) or \
                    result['data'] == '域 {0} 已开始'.format(kvm_name):
                result = '虚拟机{0}开启成功。'.format(kvm_name)
            else:
                result = '虚拟机{0}开启失败。'.format(kvm_name)
        else:
            result = '虚拟机{0}已开启。'.format(kvm_name)

        return result

    def shutdown(self, kvm_name):
        # 关闭虚拟机:是开启的状态
        state = self.domstate(kvm_name)
        if state == 'running':
            exe_cmd = r'virsh shutdown {}'.format(kvm_name)
            result = self.remote_linux(exe_cmd)
            if result['data'] == 'Domain {0} is being shutdown'.format(kvm_name) or \
                    result['data'] == '域 {0} 被关闭'.format(kvm_name):
                result = '虚拟机{0}关闭成功。'.format(kvm_name)
            else:
                result = '虚拟机{0}关闭失败。'.format(kvm_name)
        else:
            result = '虚拟机{0}未开启。'.format(kvm_name)
        return result

    def undefine(self, kvm_name):

        """
        删除虚拟机
        停止主机：virsh shutdown linux65
        删除主机定义：virsh undefine linux65
        删除KVM虚拟机文件： rm -f /home/vps/linux65.img
        """

        # 这里需要先判断虚拟机的状态
        # 如果是关闭（shut off）的虚拟机直接删除，然后删除磁盘文件，如果是开启（running）的虚拟机，先关闭再删除虚拟机，在删除磁盘文件
        # 如果虚拟机中创建了快照，虚拟机是无法删除的，需要删除所有的快照，然后在执行删除虚拟机操作
        # exe_cmd = r'virsh shutdown {}'.format(kvm_name)
        # rm_obj = remote.ServerByPara(exe_cmd, self.ip, self.username, self.password, self.system_tag)
        # rm_obj.run(succeedtext='')
        state = self.domstate(kvm_name)
        if state == 'shut off' or state == '关闭':
            snapshot_list = self.snapshot_list(kvm_name)
            if not snapshot_list:
                exe_cmd = r'virsh undefine {0}'.format(kvm_name)
                result = self.remote_linux(exe_cmd)
                if result:
                    # 删除虚拟机的磁盘文件：需要找到磁盘文件的路径：就是你创建虚拟机时设置的磁盘路径：默认是在/var/lib/libvirt/images
                    if result['data'] == 'Domain {0} has been undefined'.format(kvm_name) or \
                            result['data'] == '域 {0} 已经被取消定义'.format(kvm_name):
                        result = '虚拟机{0}删除成功。'.format(kvm_name)
                        dir = '/var/lib/libvirt/images/{0}.qcow2'.format(kvm_name)
                        exe_cmd = r'rm -rf {0}'.format(dir)
                        self.remote_linux(exe_cmd)
                    else:
                        result = '虚拟机{0}删除失败。'.format(kvm_name)
            else:
                result = '虚拟机{0}中已创建快照，无法删除此虚拟机。'.format(kvm_name)
        else:
            result = '虚拟机{0}未关闭，请先关闭虚拟机，再执行删除操作。'.format(kvm_name)

        return result

    def suspend(self, kvm_name):
        """
        暂停虚机：开启(ruuning)/暂停(paused)的状态，关闭状态提醒错误。
        """
        state = self.domstate(kvm_name)
        if state == 'shut off' or state == '关闭':
            result = '虚拟机{0}是关闭状态，不可执行暂停操作。'.format(kvm_name)
        else:
            exe_cmd = r'virsh suspend {0}'.format(kvm_name)
            result = self.remote_linux(exe_cmd)
            if result['data'] == 'Domain {0} suspended'.format(kvm_name) or \
                    result['data'] == '域 {0} 被挂起'.format(kvm_name):
                result = '虚拟机{0}暂停成功。'.format(kvm_name)
            else:
                result = '虚拟机{0}暂停失败。'.format(kvm_name)
        return result

    def resume(self, kvm_name):
        """
        恢复暂停的虚机：必须是暂停（paused）状态的虚拟机才可以执行恢复操作
        """
        state = self.domstate(kvm_name)
        if state == 'paused' or state == '暂停':
            exe_cmd = r'virsh resume {0}'.format(kvm_name)
            result = self.remote_linux(exe_cmd)
            if result['data'] == 'Domain {0} resumed'.format(kvm_name) or \
                    result['data'] == '域 {0} 被重新恢复'.format(kvm_name):
                result = '虚拟机{0}恢复成功。'.format(kvm_name)
            else:
                result = '虚拟机{0}恢复失败。'.format(kvm_name)
        else:
            result = '虚拟机{0}非暂停状态，无法执行恢复操作。'.format(kvm_name)
        return result

    def clone(self, kvm_name, kvm_name_clone):
        """
        克隆虚拟机：需要在关机或者暂停的状态下才可以进行克隆
        克隆出错：ERROR    Domain with devices to clone must be paused or shutoff.
        克隆成功：Allocating 'Test-3.qcow2'                                   |  80 GB  00:02     Clone 'Test-3' created successfully.

        virt-clone -o win2k16 -n Test-1 -f /var/lib/libvirt/images/Test—1.qcow2
        注：-o：original 后面跟要克隆的虚拟机名字
　　      -n：name 克隆后虚拟机的名字
　　      -f：file 指定镜像存放的路径：默认路径：/var/lib/libvirt/images
        新的虚拟机存在报错：ERROR    Invalid name for new guest: Guest name 'Test-3' is already in use.
        """
        # 判断虚拟机的状态
        state = self.domstate(kvm_name)

        if state == 'shut off' or state == 'paused' or state == '关闭' or state == '暂停':
            kvm_all_list = self.kvm_all_list()
            kvm_name_list = []
            for i in kvm_all_list:
                kvm_name_list.append(i['name'])
            if kvm_name_clone not in kvm_name_list:
                exe_cmd = r'virt-clone -o {0} -n {1} -f /var/lib/libvirt/images/{1}.qcow2'.format(kvm_name, kvm_name_clone)
                result = self.remote_linux(exe_cmd)
                if "Clone '{0}' created successfully.".format(kvm_name_clone) or \
                        "成功克隆 '{0}'".format(kvm_name_clone) in result['data']:
                    result = '虚拟机{0}克隆成功。'.format(kvm_name_clone)
                else:
                    result = '虚拟机{0}克隆失败。'.format(kvm_name_clone)
            else:
                result = '虚拟机{0}已存在，请使用其他名称。'.format(kvm_name_clone)

        else:
            result = '请先关闭虚拟机，再执行克隆操作。'.format(kvm_name)
        return result

    def snapshot_create(self, kvm_name):
        # 创建快照
        # 创建成功提示信息：Domain snapshot 1596685828 created
        exe_cmd = r'virsh snapshot-create {0}'.format(kvm_name)
        result = self.remote_linux(exe_cmd)

        if 'created' in result['data'] or '已生成域快照' in result['data']:
            result = '虚拟机{0}创建快照成功。'.format(kvm_name)
        else:
            result = '虚拟机{0}创建快照失败。'.format(kvm_name)
        return result

    def snapshot_list(self, kvm_name):
        # 查看快照列表
        exe_cmd = r'virsh snapshot-list {0}'.format(kvm_name)
        result = self.remote_linux(exe_cmd)
        list = [x for x in result['data'].split(' ') if x]

        # 根据显示中文还是英文过滤
        if list[1] == '生成时间':
            del list[0:3]
        elif list[1] == 'Creation':
            del list[0:4]

        end_list = self.list_of_groups(list, 5)
        snapshot_list_dict = []
        for item in end_list:
            data = {}
            data['name'] = item[0]
            data['create_time'] = item[1] + ' ' + item[2]
            data['state'] = item[4]
            snapshot_list_dict.append(data)

        """
        [{'name': '1596684491', 'state': 'shutoff', 'create_time': '2020-08-06 11:28:11'}, 
        {'name': '1596685828', 'state': 'running', 'create_time': '2020-08-06 11:50:28'}]

        """
        return snapshot_list_dict

    def snapshot_del(self, kvm_name, snapshotname):
        # 删除快照
        exe_cmd = r'virsh snapshot-delete {0} --snapshotname {1}'.format(kvm_name, snapshotname)
        result = self.remote_linux(exe_cmd)
        if result['data'] == 'Domain snapshot {0} deleted'.format(snapshotname) or result['data'] == '已删除域快照':
            result = '快照{0}删除成功。'.format(snapshotname)
        else:
            result = '快照{0}删除失败。'.format(snapshotname)

        return result

    def snapshot_revert(self, kvm_name, snapshotname):
        # 恢复快照：虚拟机是关机的状态
        state = self.domstate(kvm_name)
        if state == 'shut off':
            exe_cmd = r'virsh snapshot-revert {0} --snapshotname {1}'.format(kvm_name, snapshotname)
            self.remote_linux(exe_cmd)
            result = '恢复到快照{0}成功。'.format(snapshotname)
        else:
            result = '请先关闭虚拟机，再执行恢复操作。'.format(kvm_name)
        return result

    def zfs_kvm_filesystem(self):
        exe_cmd = r'ls /tank'.format()
        result = self.remote_linux(exe_cmd)
        kvm_filesystem = [x for x in result['data'].split(' ') if x]
        return kvm_filesystem

    def zfs_create_filesystem(self, kvm_name):
        """
        为每一台虚拟机分别创建一个文件系统
        tank/kvm_1
        tank/kvm_2
        tank/kvm_3

        zfs创建文件系统:zfs create tank/kvm_1
        zfs_pool_data:文件系统路径
        """
        info = ''
        try:
            exe_cmd = r'zfs create tank/{0}'.format(kvm_name)
            self.remote_linux(exe_cmd)
        except:
            info = '创建虚拟机{0}文件系统失败'.format(kvm_name)
        return info

    def copy_kvm_disk(self, kvm_name_new, kvm_name):
        """
        拷贝磁盘文件(kvm.qcow2)到文件系统
        cp /var/lib/libvirt/images/Test-1.qcow2 /tank/kvm_1/Test-1.qcow2
        """
        info = ''
        try:
            kvm_name_path = '/var/lib/libvirt/images/{0}.qcow2'.format(kvm_name)
            kvm_name_new_path = '/tank/{0}/{1}.qcow2'.format(kvm_name_new, kvm_name)

            exe_cmd = r'cp {0} {1}'.format(kvm_name_path, kvm_name_new_path)
            self.remote_linux(exe_cmd)
        except:
            info = '拷贝{0}磁盘文件失败。'.format(kvm_name)
        return info

    def zfs_create_snapshot(self, snapshot_name):
        """
        创建快照：zfs snapshot tank/kvm_1@2020-07-28
        kvm_name：虚拟机
        zfs_snapshot_name：快照名字
        """
        try:
            exe_cmd = r'zfs snapshot {0}'.format(snapshot_name)
            print(exe_cmd)
            self.remote_linux(exe_cmd)
            info = '创建成功。'
        except:
            info = '创建失败。'
        return info

    def zfs_snapshot_list(self, filesystem):
        """
        查看zfs快照：zfs list -t snapshot -r tank/kvm_1
        """
        exe_cmd = r'zfs list -t snapshot -r {0}'.format(filesystem)
        print(exe_cmd)
        result = self.remote_linux(exe_cmd)
        snapshot_list = [x for x in result['data'].split(' ') if x]
        split_monutpoint = snapshot_list[4].lstrip('MOUNTPOINT')
        snapshot_list[4] = split_monutpoint
        del snapshot_list[0:4]
        del snapshot_list[-1]
        end_list = self.list_of_groups(snapshot_list, 4)
        zfs_snapshot_list_dict = []
        for item in end_list:
            if item[0][0] == '-':
                item[0] = item[0].lstrip('-')
            data = {}
            data['name'] = item[0]
            zfs_snapshot_list_dict.append(data)
        return zfs_snapshot_list_dict

    def zfs_snapshot_del(self, snapshot_name):
        """
        删除快照:zfs destroy mypool/data@2020-07-28
        """
        try:
            exe_cmd = r'zfs destroy {0}'.format(snapshot_name)
            self.remote_linux(exe_cmd)
            info = '删除成功。'
        except:
            info = '快照已挂载，删除失败。'
        return info

    def zfs_clone_snapshot(self, snapshot_name, snapshot_clone_path):
        """
        克隆快照：zfs clone tank/Test-1/disk@2020-08-23 tank/Test-1/Test-1_clone
        kvm_name
        kvm_snapshot_name
        kvm_snapshot_clone_name
        """
        info = ''
        try:
            snapshot = snapshot_name.split('/')
            snapshot_clone_path = snapshot[0] + '/' + snapshot[1] + '/' + snapshot_clone_path
            exe_cmd = r'zfs clone {0} {1}'.format(snapshot_name, snapshot_clone_path)
            print(exe_cmd)
            # self.remote_linux(exe_cmd)
            info = '克隆成功。'
        except:
            info = '克隆快照失败。'
        return info

    def create_kvm_xml(self, snapshot_name, snapshot_clone_path, kvm_copy_name):
        """
        读取文件，修改文件，追加到新文件
        kvm_name = 'Test-1                               老虚拟机
        kvm_name_new = 'kvm_1                            新虚拟机
        kvm_disk_path = '/tank/kvm_1/kvm_1_clone/Test-1.qcow2'   新虚拟机磁盘
        """
        info = ''
        try:
            snapshot = snapshot_name.split('/')
            snapshot_clone_path = snapshot[0] + '/' + snapshot[1] + '/' + snapshot_clone_path + '/' + snapshot[1] + '.qcow2'
            exe_cmd = r'cat /etc/libvirt/qemu/{0}.xml'.format(snapshot[1])
            result = self.remote_linux(exe_cmd)
            # 解析xml文件找出要修改的name、uuid、disk_path、mac
            config = etree.XML(result['data'])
            kvm_name = config.xpath("//name")[0]
            kvm_diskpath = config.xpath("//disk/source")[0]
            kvm_uuid = config.xpath("//uuid")[0]
            kvm_interface = config.xpath("//interface")[0]
            kvm_mac = config.xpath("//mac")[0]

            # 修改名字、修改磁盘路径、删除uuid、删除mac
            kvm_name.text = kvm_copy_name
            kvm_diskpath.attrib['file'] = snapshot_clone_path
            config.remove(kvm_uuid)
            kvm_interface.remove(kvm_mac)
            xml_content = etree.tounicode(config)

            xml_path = '/etc/libvirt/qemu/{0}.xml'.format(kvm_copy_name)
            exe_cmd = r'cat > {0} << \EOH'.format(xml_path) + '\n' + xml_content + '\nEOH'
            self.remote_linux(exe_cmd)
            info = '创建成功。'
        except:
            info = '生成虚拟机{0}.xml失败。'.format(kvm_copy_name)
            pass
        return info

    def define_kvm(self, kvm_copy_name):
        """
        通过xml文件定义虚拟机
        virsh define /etc/libvirt/qemu/kvm_1.xml
        """
        xml_path = '/etc/libvirt/qemu/{0}.xml'.format(kvm_copy_name)
        exe_cmd = r'virsh define {0}'.format(xml_path)
        result = self.remote_linux(exe_cmd)
        if result['data'] == 'Domain {0} defined from {1}'.format(kvm_copy_name, xml_path) or \
                result['data'] == '定义域 {0}（从 {1}）'.format(kvm_copy_name, xml_path):
            result = '虚拟机{0}定义成功。'.format(kvm_copy_name)
        else:
            result = '虚拟机{0}定义失败。'.format(kvm_copy_name)

        return result


linuxserver_credit = {
    'KvmHost': '192.168.1.61',
    'KvmUser': 'root',
    'KvmPasswd': 'tesunet@2019',
    'SystemType': 'Linux',
}

# result = KVMApi(linuxserver_credit).kvm_all_list()
# result = KVMApi(linuxserver_credit).clone('Test-1', 'Test-3')
# result = KVMApi(linuxserver_credit).zfs_create_filesystem('kvm_1')
# result = KVMApi(linuxserver_credit).copy_kvm_disk('kvm_1', 'Test-1')
# result = KVMApi(linuxserver_credit).zfs_create_snapshot('kvm_1', '2020-08-20')
# result = KVMApi(linuxserver_credit).zfs_snapshot_list()
# result = KVMApi(linuxserver_credit).zfs_clone_snapshot('tank/Test-1/disk@2020-08-23', 'Test-1_clone')
# result = KVMApi(linuxserver_credit).create_kvm_xml('tank/Test-1/disk@2020-08-23', 'Test-1_clone')
# result = KVMApi(linuxserver_credit).define('kvm_1')
# result = KVMApi(linuxserver_credit).start('kvm_1')
# result = KVMApi(linuxserver_credit).shutdown('Test-1')
# result = KVMApi(linuxserver_credit).zfs_list()
# print(result)



