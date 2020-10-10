#! /usr/bin/python
import libvirt
import time
from xml.etree import ElementTree
from drm import remote
from lxml import etree
import json

############################################################
#        KVM虚拟机管理：接口方式                             #
############################################################


class LibvirtApi():
    def __init__(self, ip):
        self.ip = ip

    def conn(self):
        address = "qemu+tcp://{0}/system".format(self.ip)
        conn = libvirt.open(address)
        return conn

    def kvm_memory_cpu_usage(self, kvm_id):
        # kvm虚拟机内存、cpu、disk使用情况
        data = {}
        id = int(kvm_id)
        dom = self.conn().lookupByID(id)
        dom.setMemoryStatsPeriod(10)
        meminfo = dom.memoryStats()
        if 'unnused' and 'available' in meminfo:
            free_mem = float(meminfo['unused'])
            total_mem = float(meminfo['available'])
            used_mem = total_mem-free_mem
            mem_usage = round(((total_mem-free_mem) / total_mem)*100, 2)
            data['mem_usage'] = mem_usage
            data['mem_used'] = round(used_mem/1024/1024, 2)
            data['mem_total'] = round(total_mem/1024/1024,  2)
            data['mem_free'] = round(free_mem/1024/1024, 2)

            t1 = time.time()
            c1 = int(dom.info()[4])
            time.sleep(1)
            t2 = time.time()
            c2 = int(dom.info()[4])
            c_nums = int(dom.info()[3])
            cpu_usage = round((c2 - c1) * 100 / ((t2 - t1) * c_nums * 1e9), 2)
            data['cpu_usage'] = cpu_usage
        else:
            data['mem_usage'] = 0
            data['mem_used'] = 0
            data['mem_total'] = 0
            data['mem_free'] = 0
            data['cpu_usage'] = 0

        return data

    def kvm_disk_usage(self, kvm_name):
        # kvm虚拟机磁盘使用情况
        disk_total = ''
        disk_used = ''
        disk_usage = ''
        domain = self.conn().lookupByName(kvm_name)
        tree = ElementTree.fromstring(domain.XMLDesc())
        devices = tree.findall('devices/disk/target')
        for d in devices:
            device = d.get('dev')
            if device == 'vda':
                try:
                    devinfo = domain.blockInfo(device)
                    disk_total = round(devinfo[0]/1024/1024/1024, 2)
                    disk_used = round(devinfo[2]/1024/1024/1024, 2)
                    disk_usage = round(disk_used/disk_total*100, 2)
                except libvirt.libvirtError:
                    pass
        data = {
            'disk_total': disk_total,
            'disk_used': disk_used,
            'disk_usage': disk_usage
        }
        return data

    def mem_cpu_hostname_info(self):
        # 宿主机：cpu个数、主机名：内存使用情况
        cpu_count = self.conn().getInfo()[2]
        hostname = self.conn().getHostname()
        mem_info = self.conn().getMemoryStats(libvirt.VIR_NODE_MEMORY_STATS_ALL_CELLS)
        mem_total = mem_info['total']
        mem_free = mem_info['free']
        mem_cached = mem_info['cached']
        mem_buffers = mem_info['buffers']
        free_mem = mem_free + mem_buffers + mem_cached
        used_mem = mem_total - free_mem
        memory_usage = round(100 * used_mem / mem_total, 2)
        data = {
            'mem_total': round(mem_total/1024/1024, 2),
            'mem_used': round(used_mem/1024/1024, 2),
            'memory_usage': memory_usage,
            'cpu_count': cpu_count,
            'hostname': hostname
        }
        return data


############################################################
#        KVM虚拟机管理：命令方式                             #
############################################################

class KVMApi():
    def __init__(self, credit):
        self.ip = credit['KvmHost']
        self.username = credit['KvmUser']
        self.password = credit['KvmPasswd']
        self.system_tag = credit['SystemType']

    def remote_linux(self, exe_cmd):
        rm_obj = remote.ServerByPara(exe_cmd, self.ip, self.username, self.password, self.system_tag)
        result = rm_obj.run(succeedtext='', linux_timeout=12 * 60)
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
        result = result['data'].strip()
        return result

    def domid(self, kvm_name):
        # 获取虚拟机的id
        exe_cmd = r'virsh domid {0}'.format(kvm_name)
        result = self.remote_linux(exe_cmd)
        result = result['data']
        return result

    def kvm_all_list(self):
        # 获取所有kvm虚拟机
        exe_cmd = r'virsh list --all'
        result = self.remote_linux(exe_cmd)
        kvm_list = [x for x in result['data'].split(' ') if x]

        del kvm_list[0:4]
        kvm_list_filter = []
        for i in kvm_list:
            if i == 'shut':
                continue
            if i == 'off':
                i = '关闭'
            if i == 'running':
                i = '运行中'
            if i == 'paused':
                i = '暂停'
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

    def kvm_exclude_copy_list(self):
        # 获取除实例之外所有kvm虚拟机
        exe_cmd = r'virsh list --all'
        result = self.remote_linux(exe_cmd)
        kvm_list = [x for x in result['data'].split(' ') if x]
        del kvm_list[0:4]
        kvm_list_filter = []
        for i in kvm_list:
            if i == 'shut':
                continue
            if i == 'off':
                i = '关闭'
            if i == 'running':
                i = '运行中'
            if i == 'paused':
                i = '暂停'
            kvm_list_filter.append(i)
        end_list = self.list_of_groups(kvm_list_filter, 3)
        kvm_all_list_dict = []
        for item in end_list:
            data = {}
            if '@' not in item[1]:
                data['id'] = item[0]
                data['name'] = item[1]
                data['state'] = item[2]
                kvm_all_list_dict.append(data)

        return kvm_all_list_dict

    def kvm_include_copy_list(self, kvm_copy_name):
        # 获取所有实例虚拟机
        exe_cmd = r'virsh list --all'
        result = self.remote_linux(exe_cmd)
        kvm_list = [x for x in result['data'].split(' ') if x]

        del kvm_list[0:4]
        kvm_list_filter = []
        for i in kvm_list:
            if i == 'shut':
                continue
            if i == 'off':
                i = '关闭'
            if i == 'running':
                i = '运行中'
            if i == 'paused':
                i = '暂停'
            kvm_list_filter.append(i)
        end_list = self.list_of_groups(kvm_list_filter, 3)
        kvm_all_list_dict = []
        for item in end_list:
            data = {}
            copyname = kvm_copy_name + '@'
            if copyname in item[1]:
                data['id'] = item[0]
                data['name'] = item[1]
                data['state'] = item[2]
                kvm_all_list_dict.append(data)

        return kvm_all_list_dict

    def kvm_start(self, kvm_state, kvm_name):
        # 开启虚拟机:是关闭的状态（shut off/关闭）
        if kvm_state == 'shut off' or kvm_state == '关闭':
            exe_cmd = r'virsh start {0}'.format(kvm_name)
            result = self.remote_linux(exe_cmd)
            if result['data'].strip() == 'Domain {0} started'.format(kvm_name) or \
                    result['data'].strip() == '域 {0} 已开始'.format(kvm_name):
                result = '开机成功。'
            else:
                result = '开机失败。'
        else:
            result = '虚拟机已开启。'

        return result

    def kvm_shutdown(self, kvm_state, kvm_name):
        # 关闭虚拟机:是开启的状态（running）
        if kvm_state == 'running' or kvm_state == '运行中':
            exe_cmd = r'virsh shutdown {0}'.format(kvm_name)
            result = self.remote_linux(exe_cmd)
            if result['data'].strip() == 'Domain {0} is being shutdown'.format(kvm_name) or \
                    result['data'].strip() == '域 {0} 被关闭'.format(kvm_name):
                time.sleep(3)
                state = self.domstate(kvm_name)
                if state == 'shut off' or state == '关闭':
                    result = '关闭成功。'
                else:
                    result = '关闭失败。'
            else:
                result = '关闭失败。'
        elif kvm_state == '暂停' or kvm_state == 'paused':
            result = '虚拟机未运行。'
        else:
            result = '虚拟机未开启。'
        return result

    def kvm_destroy(self, kvm_state, kvm_name):
        # 断电虚拟机:是开启的状态（running）或者是暂停状态（pasued）
        if kvm_state == 'running' or kvm_state == '运行中' or kvm_state == 'paused' or kvm_state == '暂停':
            exe_cmd = r'virsh destroy {0}'.format(kvm_name)
            result = self.remote_linux(exe_cmd)
            if result['data'].strip() == 'Domain {0} destroyed'.format(kvm_name) or \
                    result['data'].strip() == '域 {0} 被删除'.format(kvm_name):
                result = '断电成功。'
            else:
                result = '断电失败。'
        else:
            result = '虚拟机未开启。'
        return result

    def filesystem_del(self, filesystem):
        try:
            exe_cmd = r'zfs destroy {0}'.format(filesystem)
            result = self.remote_linux(exe_cmd)
            if result['data'] == '':
                result = '删除文件系统成功。'
            else:
                result = '删除文件系统成功。'
        except Exception as e:
            print(e)
            result = '删除文件系统失败。'
        return result

    def undefine(self, kvm_name, state):
        """
        删除虚拟机
        停止主机：virsh shutdown linux65
        删除主机定义：virsh undefine linux65
        删除KVM虚拟机文件系统： zfs destroy tank/CentOS-7@test3
        """
        # 这里需要先判断虚拟机的状态
        # 如果是关闭（shut off）的虚拟机直接删除，然后删除磁盘文件，如果是开启（running）的虚拟机，先关闭再删除虚拟机，在删除磁盘文件
        # 如果虚拟机中创建了快照，虚拟机是无法删除的，需要删除所有的快照，然后在执行删除虚拟机操作
        if state == 'shut off' or state == '关闭':
            snapshot_list = self.snapshot_list(kvm_name)
            if not snapshot_list:
                try:
                    exe_cmd = r'virsh undefine {0}'.format(kvm_name)
                    result = self.remote_linux(exe_cmd)
                    if result['data'].strip() == 'Domain {0} has been undefined'.format(kvm_name) or \
                            result['data'].strip() == '域 {0} 已经被取消定义'.format(kvm_name):
                        result = '取消定义成功。'
                    else:
                        result = '取消定义失败。'
                except Exception as e:
                    print(e)
                    result = '取消定义失败。'
            else:
                result = '虚拟机已创建快照，无法删除。'
        else:
            result = '虚拟机未关闭。'
        return result

    def kvm_suspend(self, kvm_state, kvm_name):
        """
        暂停虚机：开启(ruuning)/暂停(paused)的状态，关闭状态提醒错误。
        """
        if kvm_state == 'running' or kvm_state == '运行中' or kvm_state == 'paused' or kvm_state == '暂停':
            exe_cmd = r'virsh suspend {0}'.format(kvm_name)
            result = self.remote_linux(exe_cmd)
            if result['data'].strip() == 'Domain {0} suspended'.format(kvm_name) or \
                    result['data'].strip() == '域 {0} 被挂起'.format(kvm_name):
                result = '暂停成功。'
            else:
                result = '暂停失败。'
        else:
            result = '虚拟机未开启。'
        return result

    def kvm_resume(self, kvm_state, kvm_name):
        """
        恢复暂停的虚机：必须是暂停（paused）状态的虚拟机才可以执行恢复操作
        """
        if kvm_state == 'paused' or kvm_state == '暂停':
            exe_cmd = r'virsh resume {0}'.format(kvm_name)
            result = self.remote_linux(exe_cmd)
            if result['data'].strip() == 'Domain {0} resumed'.format(kvm_name) or \
                    result['data'].strip() == '域 {0} 被重新恢复'.format(kvm_name):
                result = '运行成功。'
            else:
                result = '运行失败。'
        else:
            result = '虚拟机非暂停状态，无法执行此操作。'
        return result

    def kvm_reboot(self, kvm_state, kvm_name):
        """
        重启虚机：必须是开启(running)/暂停(paused)状态的虚拟机才可以执行重启操作
        """
        if kvm_state == 'running' or kvm_state == '运行中' or kvm_state == '暂停' or kvm_state == 'paused':
            exe_cmd = r'virsh reboot {0}'.format(kvm_name)
            result = self.remote_linux(exe_cmd)
            if result['data'].strip() == 'Domain {0} is being rebooted'.format(kvm_name) or \
                    result['data'].strip() == '域 {0} 正在被重新启动'.format(kvm_name):
                result = '重启成功。'
            else:
                result = '重启失败。'
        else:
            result = '虚拟机未开启。'
        return result

    def kvm_clone(self, kvm_state, kvm_name, kvm_name_clone, filesystem):
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
        disk_path = '/' + filesystem + '/' + kvm_name_clone + '.qcow2'
        if kvm_state == 'shut off' or kvm_state == 'paused' or kvm_state == '关闭' or kvm_state == '暂停':
            exe_cmd = r'virt-clone -o {0} -n {1} -f {2}'.format(kvm_name, kvm_name_clone, disk_path)
            result = self.remote_linux(exe_cmd)
            if "Clone '{0}' created successfully.".format(kvm_name_clone) or \
                    "成功克隆 '{0}'".format(kvm_name_clone) in result['data']:
                result = '克隆成功。'
            else:
                result = '克隆失败。'
        else:
            result = '虚拟机未关闭。'
        return result

    def kvm_info_data(self, kvm_name):
        # 获取虚拟机cpu、内存、系统类型、磁盘
        try:
            exe_cmd = r'cat /etc/libvirt/qemu/{0}.xml'.format(kvm_name)
            result = self.remote_linux(exe_cmd)
            config = etree.XML(result['data'])
            kvm_cpu = config.xpath("//vcpu")[0]
            kvm_memory = config.xpath("//memory")[0]
            kvm_os = config.xpath("//os/type")[0]
            kvm_diskpath = config.xpath("//disk/source")[0]
            kvm_os = kvm_os.text
            kvm_cpu = int(kvm_cpu.text)
            kvm_memory = int(int(kvm_memory.text)/1024)
            kvm_disk = kvm_diskpath.attrib['file']
            result = {
                'kvm_os': kvm_os,
                'kvm_disk': kvm_disk,
                'kvm_cpu': kvm_cpu,
                'kvm_memory': kvm_memory
            }
        except:
            result = '获取信息失败。'
        return result

    def snapshot_list(self, kvm_name):
        # 查看快照列表
        try:
            exe_cmd = r'virsh snapshot-list {0}'.format(kvm_name)
            result = self.remote_linux(exe_cmd)
            list = [x for x in result['data'].split(' ') if x]
            del list[0:4]
            end_list = self.list_of_groups(list, 5)
            result = []
            for item in end_list:
                data = {}
                data['name'] = item[0]
                result.append(data)
                """
                [{'name': '1596684491'}, 
                {'name': '1596685828'}]
                """
        except:
            result = '获取信息失败。'
        return result

    def kvm_disk_space(self):
        """
        获取kvm文件系统磁盘使用情况：zfs list
        """

        exe_cmd = r'zfs list'
        result = self.remote_linux(exe_cmd)
        kvm_space_list = [x for x in result['data'].split(' ') if x]

        del kvm_space_list[0:5]
        end_list = self.list_of_groups(kvm_space_list, 5)
        data = {}
        for item in end_list:
            if 'data' == item[0]:
                data['used_total'] = float(item[1].replace('G', ''))
                data['size_total'] = float(item[2].replace('G', ''))
                data['used_percent'] = round(float(item[1].replace('G', '')) / float(item[2].replace('G', '')), 2) * 100

        return data

    def zfs_kvm_filesystem(self):
        try:
            exe_cmd = r'ls /data/vmdata'.format()
            result = self.remote_linux(exe_cmd)
            result = [x.replace('\t', '') for x in result['data'].split(' ') if x]
        except:
            result = '获取文件系统失败。'
        return result

    def create_filesystem(self, filesystem):
        """
        为每一台虚拟机分别创建一个文件系统
        """
        try:
            exe_cmd = r'zfs create {0}'.format(filesystem)
            result = self.remote_linux(exe_cmd)
            if result['data'] == '':
                result = '文件系统创建成功。'
            else:
                result = '文件系统创建失败。'
        except:
            result = '文件系统创建失败。'
        return result

    def zfs_create_snapshot(self, snapshot_name):
        """
        创建快照：zfs snapshot tank/kvm_1@2020-07-28
        kvm_name：虚拟机
        zfs_snapshot_name：快照名字
        """
        try:
            exe_cmd = r'zfs snapshot {0}'.format(snapshot_name)
            result = self.remote_linux(exe_cmd)
            if result['data'] == '':
                result = '创建成功。'
            else:
                result = '创建失败。'
        except:
            result = '创建失败。'
        return result

    def zfs_snapshot_list(self, filesystem):
        """
        查看zfs快照：zfs list -t snapshot -r tank/kvm_1
        """
        try:
            exe_cmd = r'zfs list -t snapshot -r {0}'.format(filesystem)
            result = self.remote_linux(exe_cmd)
            snapshot_list = [x for x in result['data'].split(' ') if x]
            del snapshot_list[0:5]

            end_list = self.list_of_groups(snapshot_list, 5)
            result = []
            for item in end_list:
                data = {}
                item = item[0].split('@')
                data['name'] = item[1]
                result.append(data)
        except:
            result = '获取信息失败。'
        return result

    def zfs_snapshot_del(self, snapshot_name):
        """
        删除快照:zfs destroy mypool/data@2020-07-28
        """
        try:
            exe_cmd = r'zfs destroy {0}'.format(snapshot_name)
            result = self.remote_linux(exe_cmd)
            if result['data'] == '':
                result = '删除快照成功。'
            else:
                result = '删除快照失败。'
        except:
            result = '删除快照失败。'
        return result

    def zfs_clone_snapshot(self, snapshot_name, filesystem_name):
        """
        克隆快照：zfs clone tank/kvm_1@2020-08-20 tank/kvm_1@2020-08-20
        kvm_name
        kvm_snapshot_name
        kvm_snapshot_clone_name
        """
        try:
            exe_cmd = r'zfs clone {0} {1}'.format(snapshot_name, filesystem_name)
            result = self.remote_linux(exe_cmd)
            if result['data'] == '':
                result = '克隆成功。'
            else:
                result = '克隆失败。'
        except:
            result = '克隆失败。'
        return result

    def create_kvm_xml(self, kvm_machine, snapshotname, copyname, copycpu, copymemory):
        """
        读取文件，修改文件，追加到新文件
        kvm_name = 'Test-1                                 老虚拟机
        kvm_name_new = 'kvm_1                              新虚拟机
        kvm_disk_path = '/tank/kvm_1@kvm_1/Test-1.qcow2'   新虚拟机磁盘
        """
        try:
            exe_cmd = r'cat /etc/libvirt/qemu/{0}.xml'.format(kvm_machine)
            snapshot_clone_name = snapshotname.replace('@', '-')
            kvm_disk_path = '/' + snapshot_clone_name + '/' + kvm_machine + '.qcow2'
            result = self.remote_linux(exe_cmd)
            # 解析xml文件找出要修改的name、uuid、disk_path、mac、cpu、memory
            config = etree.XML(result['data'])
            kvm_name = config.xpath("//name")[0]
            kvm_diskpath = config.xpath("//disk/source")[0]
            kvm_uuid = config.xpath("//uuid")[0]
            kvm_interface = config.xpath("//interface")[0]
            kvm_mac = config.xpath("//mac")[0]
            if copycpu != '' and copymemory != '':
                copymemory = int(copymemory) * 1024
                kvm_cpu = config.xpath("//vcpu")[0]
                kvm_cpu.text = copycpu
                kvm_memory = config.xpath("//memory")[0]
                kvm_currentmemory = config.xpath("//currentMemory")[0]
                kvm_memory.text = str(copymemory)
                kvm_currentmemory.text = str(copymemory)
            elif copycpu != '' and copymemory == '':
                kvm_cpu = config.xpath("//vcpu")[0]
                kvm_cpu.text = copycpu
            elif copycpu == '' and copymemory != '':
                copymemory = int(copymemory) * 1024
                kvm_memory = config.xpath("//memory")[0]
                kvm_currentmemory = config.xpath("//currentMemory")[0]
                kvm_memory.text = str(copymemory)
                kvm_currentmemory.text = str(copymemory)
            # 修改名字、修改磁盘路径、删除uuid、删除mac

            kvm_name.text = copyname
            kvm_diskpath.attrib['file'] = kvm_disk_path
            config.remove(kvm_uuid)
            kvm_interface.remove(kvm_mac)
            xml_content = etree.tounicode(config)
            xml_path = '/etc/libvirt/qemu/{0}.xml'.format(copyname)
            exe_cmd = r'cat > {0} << \EOH'.format(xml_path) + '\n' + xml_content + '\nEOH'
            result = self.remote_linux(exe_cmd)
            if result['data'] == '':
                result = '生成成功。'
            else:
                result = '生成失败。'
        except:
            result = '生成失败。'
        return result

    def define_kvm(self, copy_name):
        """
        通过xml文件定义虚拟机
        virsh define /etc/libvirt/qemu/kvm_1.xml
        """
        xml_path = '/etc/libvirt/qemu/{0}.xml'.format(copy_name)
        exe_cmd = r'virsh define {0}'.format(xml_path)
        result = self.remote_linux(exe_cmd)     # 定义域 CentOS-7@test4（从 /etc/libvirt/qemu/CentOS-7@test4.xml）
        if result['data'].strip() == 'Domain {0} defined from {1}'.format(copy_name, xml_path) or \
            result['data'].strip() == '定义域 {0}（从 {1}）'.format(copy_name, xml_path):
            result = '定义成功。'
        else:
            result = '定义失败。'
        return result

    def guestmount(self, kvm_machine, filesystem):
        """
        guestmount -a /data/vmdata/CentOS-7-2020-09-14/CentOS-7.qcow2 -i /etc/libvirt/kvm_mount
        /data/vmdata/CentOS-7-2020-09-14/CentOS-7.qcow2    磁盘路径
        /etc/libvirt/kvm_mount                             要挂载的目录
        """
        try:
            # filesystem: data/vmdata/CentOS-7-2020-09-14
            kvm_disk_path = '/' + filesystem + '/' + kvm_machine + '.qcow2'
            kvm_mount = '/etc/libvirt/kvm_mount'

            exe_cmd = r'guestmount -a {0} -i {1} && sleep 1'.format(kvm_disk_path, kvm_mount)
            self.remote_linux(exe_cmd)
            result = '挂载成功。'
        except Exception as e:
            print(e)
            result = '挂载失败。'
        return result

    def alert_ip_hostname(self, copy_ip,  copy_hostname):
        """
        sed -i "/IPADDR/s/=.*/=192.168.1.180/"  /etc/libvirt/kvm_mount/etc/sysconfig/network-scripts/ifcfg-eth0 修改ip
        sed -i '/HWADDR/d' /etc/libvirt/kvm_mount/etc/sysconfig/network-scripts/ifcfg-eth0                      删除MAC地址
        echo CentOS-7@test5 > /etc/libvirt/kvm_mount/etc/hostname                                               修改主机名
        """
        try:
            exe_cmd_ip = 'sed -i "/IPADDR/s/=.*/={0}/" /etc/libvirt/kvm_mount/etc/sysconfig/network-scripts/ifcfg-eth0'.format(copy_ip)
            exe_cmd_mac = 'sed -i "/HWADDR/d" /etc/libvirt/kvm_mount/etc/sysconfig/network-scripts/ifcfg-eth0'
            exe_cmd_hostname = 'echo {0} > /etc/libvirt/kvm_mount/etc/hostname'.format(copy_hostname)

            exe_cmd = r'{0} && {1} && {2}'.format(exe_cmd_ip, exe_cmd_mac, exe_cmd_hostname)
            result = self.remote_linux(exe_cmd)
            if result['data'] == '':
                result = '修改成功。'
            else:
                result = '修改失败。'
        except Exception as e:
            print(e)
            result = '修改失败。'
        return result

    def alter_password(self, password):
        # 修改密码
        try:
            # 找出要替换的密码
            exe_cmd = r'cat /etc/libvirt/kvm_mount/etc/shadow | grep root'
            result = self.remote_linux(exe_cmd)
            org_password = result['data'].strip()         # root:$1$hello$vuJDiWysCYBQzeY5biTng.::0:99999:7:::
            match_password = org_password.split(':')[1]   # $1$hello$vuJDiWysCYBQzeY5biTng.

            # 生成新的密码
            exe_cmd = r'openssl passwd -1 -salt "hello" "{0}"'.format(password)
            result = self.remote_linux(exe_cmd)
            new_password = result['data'].strip()         # $1$hello$uA2o9BNrEHkBeV0glgmvz/

            # 旧密码替换成新密码
            exe_cmd = r"sed -i 's#{0}#{1}#g' /etc/libvirt/kvm_mount/etc/shadow".format(match_password, new_password)
            result = self.remote_linux(exe_cmd)
            if result['data'] == '':
                result = '修改密码成功。'
            else:
                result = '修改密码失败。'
        except Exception as e:
            print(e)
            result = '修改密码失败。'
        return result

    def umount(self):
        """
        取消挂载：umount /etc/libvirt/kvm_mount
        """
        try:
            exe_cmd = r'umount /etc/libvirt/kvm_mount'
            result = self.remote_linux(exe_cmd)
            if result['data'] == '':
                result = '取消挂载成功。'
            else:
                result = '取消挂载失败'
        except Exception as e:
            print(e)
            result = '取消挂载失败。'
        return result

    def disk_cpu_data(self):
        """
        查看cpu使用率
        查看磁盘使用率
        """
        try:
            # 磁盘
            exe_cmd = r'df'
            result = self.remote_linux(exe_cmd)
            disk_info = [x for x in result['data'].split(' ') if x]
            del disk_info[0:6]
            end_list = self.list_of_groups(disk_info, 6)
            disk_info_list = []
            for item in end_list:
                data = {}
                data['name'] = item[0]
                data['total'] = item[1]
                data['used'] = item[2]
                data['mount'] = item[5]
                disk_info_list.append(data)
            total = 0
            used = 0
            for i in disk_info_list:
                if i['mount'] == '/' or i['mount'] == '/data' or i['mount'] == '/boot':
                    total += int(i['total'])
                    used += int(i['used'])
            disk_usage = round(used / total * 100, 2)
            # cpu使用率
            exe_cmd = r"top -n1 | awk '/Cpu/{print $2}'"
            result = self.remote_linux(exe_cmd)
            cpu_usage = float(result['data'])
            # 操作系统
            exe_cmd = r"cat /etc/centos-release"
            result = self.remote_linux(exe_cmd)
            os = result['data']
            data = {
                'disk_total': round(total / 1024 / 1024, 2),
                'disk_used': round(used / 1024 / 1024, 2),
                'disk_usage': disk_usage,
                'cpu_usage': cpu_usage,
                'os': os,
            }
        except Exception as e:
            print(e)
            data = '获取信息失败。'
        return data

    def kvm_cpu_mem_usage(self, kvm_id):
        try:
            # 获取内存使用信息
            exe_cmd = r"./test5.py {0}".format(kvm_id)
            result = self.remote_linux(exe_cmd)
            kvm_mem_usage = result['data']
            # 获取cpu使用信息
            exe_cmd = r"./test4.py {0}".format(kvm_id)
            result = self.remote_linux(exe_cmd)
            kvm_cpu_usage = result['data']
            kvm_mem_usage = json.loads(kvm_mem_usage)
            kvm_cpu_usage = json.loads(kvm_cpu_usage)
            data = {
                "kvm_mem_usage": kvm_mem_usage,
                "kvm_cpu_usage": kvm_cpu_usage,
            }
        except Exception as e:
            print(e)
            data = '获取信息失败。'
        return data

    def kvm_template(self):
        # kvm虚拟机模板文件： cd /home/images/os-image
        # kvm虚拟机存储文件： cd /home/images/disk-image
        try:
            exe_cmd = r'ls /home/images/os-image'
            result = self.remote_linux(exe_cmd)
            os_template = [x.replace('\t', ' ').split(' ') for x in result['data'].split(' ') if x][0]

            exe_cmd = r'ls /home/images/disk-image'
            result = self.remote_linux(exe_cmd)
            disk_template = [x.replace('\t', '') for x in result['data'].split(' ') if x]
            result = {
                'os_image': os_template,
                'disk_image': disk_template
            }
        except Exception as e:
            print(e)
            result = '查找模板文件失败。'
        return result

    def copy_disk(self, kvm_template_path, filesystem, kvm_storage, kvm_disk_image_path, kvm_storage_path):
        try:
            if kvm_storage == '':
                exe_cmd = r'cp {0} {1}'.format(kvm_template_path, filesystem)
                result = self.remote_linux(exe_cmd)
                if result['data'] == '':
                    result = '拷贝磁盘文件成功。'
                else:
                    result = '拷贝磁盘文件失败。'
            else:
                exe_cmd = r'cp {0} {1} && cp {2} {3}'.format(kvm_template_path, filesystem, kvm_disk_image_path, kvm_storage_path)
                result = self.remote_linux(exe_cmd)
                if result['data'] == '':
                    result = '拷贝磁盘文件成功。'
                else:
                    result = '拷贝磁盘文件失败。'
        except Exception as e:
            print(e)
            result = '拷贝磁盘文件失败。'
        return result

    def create_new_xml(self, kvm_xml, kvm_disk_path, kvmname, kvmcpu, kvmmemory, kvmstorage, kvm_storage_path):
        try:
            exe_cmd = r'cat /home/xml/{0}'.format(kvm_xml)
            result = self.remote_linux(exe_cmd)
            # 解析xml文件找出要修改的name、uuid、disk_path、mac、
            config = etree.XML(result['data'])
            kvm_name = config.xpath("//name")[0]
            kvm_diskpath = config.xpath("//disk/source")[0]
            kvm_uuid = config.xpath("//uuid")[0]
            kvm_interface = config.xpath("//interface")[0]
            kvm_mac = config.xpath("//mac")[0]

            if kvmcpu != '' and kvmmemory != '':
                kvmmemory = int(kvmmemory) * 1024
                kvm_cpu = config.xpath("//vcpu")[0]
                kvm_cpu.text = kvmcpu
                kvm_memory = config.xpath("//memory")[0]
                kvm_currentmemory = config.xpath("//currentMemory")[0]
                kvm_memory.text = str(kvmmemory)
                kvm_currentmemory.text = str(kvmmemory)
            elif kvmcpu != '' and kvmmemory == '':
                kvm_cpu = config.xpath("//vcpu")[0]
                kvm_cpu.text = kvmcpu
            elif kvmcpu == '' and kvmmemory != '':
                copymemory = int(kvmmemory) * 1024
                kvm_memory = config.xpath("//memory")[0]
                kvm_currentmemory = config.xpath("//currentMemory")[0]
                kvm_memory.text = str(copymemory)
                kvm_currentmemory.text = str(copymemory)

            # 修改名字、修改磁盘路径、删除uuid、删除mac
            kvm_name.text = kvmname
            kvm_diskpath.attrib['file'] = kvm_disk_path
            config.remove(kvm_uuid)
            kvm_interface.remove(kvm_mac)

            # 判断有无选择存储
            xml_content = ''
            if kvmstorage == '':
                xml_content = etree.tounicode(config)
            else:
                pass
            xml_path = '/etc/libvirt/qemu/{0}.xml'.format(kvmname)
            exe_cmd = r'cat > {0} << \EOH'.format(xml_path) + '\n' + xml_content + '\nEOH'
            result = self.remote_linux(exe_cmd)
            if result['data'] == '':
                result = '生成成功。'
            else:
                result = '生成失败。'
        except:
            result = '生成失败。'
        return result


linuxserver_credit = {
    'KvmHost': '192.168.1.61',
    'KvmUser': 'root',
    'KvmPasswd': 'tesunet@2019',
    'SystemType': 'Linux',
}

# result = KVMApi(linuxserver_credit).kvm_all_list()
# result = KVMApi(linuxserver_credit).zfs_kvm_filesystem()
# result = KVMApi(linuxserver_credit).memory_disk_cpu_data()
# result = KVMApi(linuxserver_credit).kvm_template()
# print(result)
