#! /usr/bin/python
import libvirt
conn = libvirt.open("qemu+tcp://192.168.1.61/system")
import time


def memory_cpu_usage(kvm_id):
    # kvm虚拟机内存、cpu使用情况
    info = {}
    id = int(kvm_id)
    dom = conn.lookupByID(id)
    dom.setMemoryStatsPeriod(10)

    meminfo = dom.memoryStats()
    free_mem = float(meminfo['unused'])
    total_mem = float(meminfo['available'])
    used_mem = total_mem-free_mem
    mem_usage = round(((total_mem-free_mem) / total_mem)*100, 2)
    info['mem_usage'] = mem_usage
    info['mem_used'] = round(used_mem/1024/1024, 2)
    info['mem_total'] = round(total_mem/1024/1024,  2)
    info['mem_free'] = round(free_mem/1024/1024, 2)

    t1 = time.time()
    c1 = int(dom.info()[4])
    time.sleep(1)
    t2 = time.time()
    c2 = int(dom.info()[4])
    c_nums = int(dom.info()[3])
    cpu_usage = round((c2 - c1) * 100 / ((t2 - t1) * c_nums * 1e9), 2)
    info['cpu_usage'] = cpu_usage
    return info
