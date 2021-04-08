#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: monitor.py
Author: YJ
Email: yj1516268@outlook.com
Created Time: 2021-04-01 16:28:10

Description: 系统软硬件信息监视器
"""

import logging
import platform
import time

import psutil
import toml

from utils.formatter import formatting

logger = logging.getLogger('SystemMonitor.monitor')


class SystemMonitor(object):
    """系统软硬件信息监视器"""
    system = platform.system()

    def __init__(self, config):
        """初始化 """
        # monitor config            -- 监视器配置
        monitor_conf = config.get('monitor', dict())
        # monitor.custom config     -- 自定义信息配置
        monitor_custom_conf = monitor_conf.get('custom', dict())
        self.custom_id = monitor_custom_conf.get('id', str())
        self.custom_name = monitor_custom_conf.get('name', str())
        # monitor.cpu config        -- CPU信息配置
        monitor_cpu_conf = monitor_conf.get('cpu', dict())
        self.cpu_interval = monitor_cpu_conf.get('interval', 0)
        self.cpu_percpu = monitor_cpu_conf.get('percpu', False)
        # monitor.mem config        -- 内存信息配置
        monitor_mem_conf = monitor_conf.get('mem', dict())
        self.mem_format = monitor_mem_conf.get('format', 'GB')
        self.mem_digit = monitor_mem_conf.get('digit', 1)
        # monitor.swap config       -- 交换分区信息配置
        monitor_swap_conf = monitor_conf.get('swap', dict())
        self.swap_format = monitor_swap_conf.get('format', 'GB')
        self.swap_digit = monitor_swap_conf.get('digit', 1)
        # monitor.disk config       -- 磁盘信息配置
        monitor_disk_conf = monitor_conf.get('disk', dict())
        self.disk_path = monitor_disk_conf.get('path', '/')
        self.disk_format = monitor_disk_conf.get('format', 'GB')
        self.disk_digit = monitor_disk_conf.get('digit', 1)
        # monitor.process config    -- 进程信息配置
        monitor_process_conf = monitor_conf.get('process', dict())
        self.process_names = monitor_process_conf.get('names', list())
        self.process_keywords = monitor_process_conf.get('keywords', list())

        # outputer config           -- 数据输出器配置
        outputer_conf = config.get('outputer', dict())
        self.output_format = outputer_conf.get('output_format', 'console')

        # decorator config          -- 数据装饰器配置
        decorator_conf = config.get('decorator', dict())
        decorator_selector = decorator_conf.get('selector', 'text')
        self.decorator_switch = decorator_conf.get('switch', False)
        self.decorator_fields = decorator_conf.get(decorator_selector, dict())

    @staticmethod
    def _bool2int(boolean):
        """布尔值转换为整数

        :boolean: Boolean value
        :returns: Integer value

        """
        result = None

        try:
            result = int(boolean)
        except Exception as e:
            logger.error(e)

        return result

    @staticmethod
    def _timestamp_gen():
        """生成时间戳
        :returns: A string, timestamp

        """
        struct_time = time.localtime(time.time())
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', struct_time)

        return timestamp

    def get_cpu_info(self):
        """获取CPU信息
        :returns: A float, percentage of current CPU utilization

        """
        info = dict()

        # 获取CPU信息
        cpuinfo = psutil.cpu_percent(interval=self.cpu_interval,
                                     percpu=self.cpu_percpu)

        info['percent'] = cpuinfo

        return info

    def get_memory_info(self):
        """获取内存信息
        :returns: A dict, memory usage statistics

        """
        info = dict()

        # 获取内存信息
        vmeminfo = psutil.virtual_memory()

        # 原始返回值以bytes表示，自定义输出值的单位（默认GB）
        factor = 3
        if self.mem_format.upper() == 'GB':
            factor = 3
        elif self.mem_format.upper() == 'MB':
            factor = 2
        elif self.mem_format.upper() == 'KB':
            factor = 1
        muse = 1024**factor

        info['total'] = round(vmeminfo[0] / muse, self.mem_digit)
        info['available'] = round(vmeminfo[1] / muse, self.mem_digit)
        info['percent'] = round(vmeminfo[2], self.mem_digit)
        info['used'] = round(vmeminfo[3] / muse, self.mem_digit)
        info['free'] = round(vmeminfo[4] / muse, self.mem_digit)

        if self.system == 'Linux':
            info['active'] = round(vmeminfo[5] / muse, self.mem_digit)
            info['inactive'] = round(vmeminfo[6] / muse, self.mem_digit)
            info['buffers'] = round(vmeminfo[7] / muse, self.mem_digit)
            info['cached'] = round(vmeminfo[8] / muse, self.mem_digit)
            info['shared'] = round(vmeminfo[9] / muse, self.mem_digit)
            info['slab'] = round(vmeminfo[10] / muse, self.mem_digit)

        return info

    def get_swap_info(self):
        """获取交换分区信息
        :returns: A dict, swap usage statistics

        """
        info = dict()

        # 获取交换分区信息
        smeminfo = psutil.swap_memory()

        # 原始返回值以bytes表示，自定义输出值的单位（默认GB）
        factor = 3
        if self.swap_format.upper() == 'GB':
            factor = 3
        elif self.swap_format.upper() == 'MB':
            factor = 2
        elif self.swap_format.upper() == 'KB':
            factor = 1
        muse = 1024**factor

        info['total'] = round(smeminfo[0] / muse, self.swap_digit)
        info['used'] = round(smeminfo[1] / muse, self.swap_digit)
        info['free'] = round(smeminfo[2] / muse, self.swap_digit)
        info['percent'] = round(smeminfo[3], self.swap_digit)
        info['sin'] = round(smeminfo[4] / muse, self.swap_digit)
        info['sout'] = round(smeminfo[5] / muse, self.swap_digit)

        return info

    def get_disk_info(self):
        """获取磁盘信息
        :returns: A dict, disk usage statistics

        """
        info = dict()

        # 获取磁盘信息
        diskinfo = psutil.disk_usage(path=self.disk_path)

        # 原始返回值以bytes表示，自定义输出值的单位（默认GB）
        factor = 3
        if self.disk_format.upper() == 'GB':
            factor = 3
        elif self.disk_format.upper() == 'MB':
            factor = 2
        elif self.disk_format.upper() == 'KB':
            factor = 1
        muse = 1024**factor

        info['total'] = round(diskinfo[0] / muse, self.disk_digit)
        info['used'] = round(diskinfo[1] / muse, self.disk_digit)
        info['free'] = round(diskinfo[2] / muse, self.disk_digit)
        info['percent'] = round(diskinfo[3], self.disk_digit)

        return info

    def get_nic_info(self):
        """获取网卡信息
        :returns: A list, NICs information

        """
        info = list()

        # 获取网卡信息
        nicinfo = psutil.net_if_addrs()

        # 系统不同取值不同的变量
        locate = 'AF_PACKET'
        if self.system == 'Windows':
            locate = 'AF_LINK'

        for name, datas in nicinfo.items():
            cache = {'name': '', 'macaddr': '', 'ipaddr': '', 'netmask': ''}
            cache['name'] = name
            for data in datas:
                if data.family.name == 'AF_INET':
                    cache['ipaddr'] = data.address
                    cache['netmask'] = data.netmask
                elif data.family.name == locate:
                    cache['macaddr'] = data.address
            info.append(cache)

        return info

    def get_process_info(self):
        """获取进程信息ff
        :returns: A list, processes information

        """
        info = list()

        # 获取进程信息
        processinfo = psutil.process_iter()

        for process in processinfo:
            cache = dict()
            if process.name() in self.process_names:
                for keyword in self.process_keywords:
                    if any(keyword in cmd for cmd in process.cmdline()):
                        cache['name'] = process.name()
                        cache['keyword'] = keyword
                        cache['pid'] = process.pid
                        cache['status'] = process.status()
                        cache['running'] = self._bool2int(process.is_running())
                        info.append(cache)

        return info

    def get_all_info(self):
        """汇总所有信息
        :returns: A dict, all system info

        """
        information = dict()
        information['fields'] = dict()

        information['timestamp'] = self._timestamp_gen()
        information['deviceid'] = self.custom_id
        information['devicename'] = self.custom_name
        information['fields']['cpu'] = self.get_cpu_info()
        information['fields']['memory'] = self.get_memory_info()
        information['fields']['swap'] = self.get_swap_info()
        information['fields']['disk'] = self.get_disk_info()
        information['fields']['nic'] = self.get_nic_info()
        information['fields']['process'] = self.get_process_info()

        logger.info('Successfully get system information')

        return information

    def main(self):
        """主函数
        :returns: 监视数据

        """
        # 获取原始监视数据
        information = self.get_all_info()

        # 格式化原始监视数据
        if self.decorator_switch:
            result = formatting(data=information,
                                format_target=self.output_format,
                                decorate_conf=self.decorator_fields)
        else:
            result = information

        return result


if __name__ == "__main__":
    confile = 'conf/config.toml'
    config = toml.load(confile)
    monitor = SystemMonitor(config)

    information = monitor.main()
    print(information)
