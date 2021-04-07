#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: main.py
Author: YJ
Email: yj1516268@outlook.com
Created Time: 2021-04-02 16:01:08

Description: 监视器管理
"""

import asyncio
import logging

import toml

from monitor import SystemMonitor
from utils.log_wrapper import setup_logging
from utils.outputer import ConsoleClient, MqttClient

# load configuration file
confile = 'conf/config.toml'
config = toml.load(confile)

# monitor config            -- 监视器配置
monitor_conf = config.get('monitor', dict())
monitor_switch = monitor_conf.get('switch', False)
monitor_interval = monitor_conf.get('interval', 300)
# outputer config           -- 数据输出器配置
outputer_conf = config.get('outputer', dict())
outputer_switch = outputer_conf.get('switch', True)
output_to = outputer_conf.get('output_to', 'console')
# saver config              -- 数据存储器配置
saver_conf = config.get('saver', dict())
saver_switch = saver_conf.get('switch', True)
save_to = saver_conf.get('save_to', 'text')
saver_fields = saver_conf.get(save_to, dict())
# log config                -- 日志记录器配置
log_conf = config.get('log', dict())
logger = logging.getLogger('SystemMonitor.main')
setup_logging(log_conf)

# all clients               -- 所有客户端对象
# syste mmonitor client     -- 系统监视器客户端
systemmonitor_client = SystemMonitor(config=config)
logger.info('Create a system monitor client')
# outputer client           -- 数据输出器客户端
outputer_client = None
if outputer_switch:
    if output_to.lower() == 'mqtt':
        outputer_client = MqttClient(conf=outputer_conf.get(output_to, dict()))
    elif output_to.lower() == 'console':
        outputer_client = ConsoleClient()
logger.info('Create a outputer({name}) client'.format(name=output_to))


async def run_systemmonitor():
    """运行系统监视器"""
    while True:
        # 检查monitor开关状态
        if monitor_switch:
            # 获取格式化后的监视器数据
            systeminfo = systemmonitor_client.main()
            # 增补监视器数据
            for key, value in saver_fields.items():
                if key not in systeminfo.keys():
                    systeminfo[key] = value
            # 检查数据输出器客户端状态
            if outputer_client:
                # 输出数据
                outputer_client.put(msg=systeminfo)
            await asyncio.sleep(monitor_interval)
        else:
            logger.warning('System monitor switch is off')


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(run_systemmonitor())

    loop.run_forever()
