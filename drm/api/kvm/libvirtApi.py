#! /usr/bin/python
import libvirt
conn = libvirt.open("qemu+tcp://192.168.1.61/system")
import time
from xml.etree import ElementTree


def kvm_memory_cpu_usage(kvm_id):
    # kvm虚拟机内存、cpu使用情况
    data = {}
    id = int(kvm_id)
    dom = conn.lookupByID(id)
    dom.setMemoryStatsPeriod(10)
    meminfo = dom.memoryStats()
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
    return data


def kvm_disk_usage(kvm_name):
    # kvm虚拟机磁盘使用情况
    disk_total = ''
    disk_used = ''
    disk_usage = ''
    domain = conn.lookupByName(kvm_name)
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


def mem_cpu_hostname_info():
    # 宿主机：cpu个数、主机名：内存使用情况
    cpu_count = conn.getInfo()[2]
    hostname = conn.getHostname()
    mem_info = conn.getMemoryStats(libvirt.VIR_NODE_MEMORY_STATS_ALL_CELLS)
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





