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
from utils.io_wrapper import ConsoleClient, MqttClient
from utils.log_wrapper import setup_logging

logger = logging.getLogger('SystemMonitor.main')

# load configuration file
confile = 'conf/config.toml'
config = toml.load(confile)

# app config                -- 程序配置
app_conf = config.get('app', dict())
app_name = app_conf.get('name', 'SystemMonitor')
app_version = app_conf.get('version', None)
# monitor config            -- 监视器配置
monitor_conf = config.get('monitor', dict())
monitor_switch = monitor_conf.get('switch', False)
monitor_interval = monitor_conf.get('interval', 300)
# outputer config           -- 数据输出器配置
outputer_conf = config.get('outputer', dict())
outputer_switch = outputer_conf.get('switch', True)
outputer_selector = outputer_conf.get('selector', 'console')
# log config                -- 日志记录器配置
log_conf = config.get('log', dict())
setup_logging(log_conf)

# Action
logger.info('{name}({version}) start running'.format(name=app_name,
                                                     version=app_version))

# all clients               -- 所有客户端对象
# syste mmonitor client     -- 系统监视器客户端
systemmonitor_client = SystemMonitor(config=config)
logger.info('Create a system monitor client')
# outputer client           -- 数据输出器客户端
outputer_client = None
if outputer_switch:
    if outputer_selector.lower() == 'mqtt':
        outputer_client = MqttClient(
            conf=outputer_conf.get(outputer_selector, dict()))
    elif outputer_selector.lower() == 'console':
        outputer_client = ConsoleClient()
logger.info('Create a outputer({name}) client'.format(name=outputer_selector))


async def run_systemmonitor():
    """运行系统监视器"""
    while True:
        # 检查monitor开关状态
        if monitor_switch:
            # 获取格式化后的监视器数据
            systeminfo = systemmonitor_client.main()
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
