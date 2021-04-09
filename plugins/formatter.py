#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: formatter.py
Author: YJ
Email: yj1516268@outlook.com
Created Time: 2021-04-07 10:00:31

Description: 数据格式化工具
"""


def formatting(data, format_target, decorate_conf):
    """将数据进行格式化

    :data: 待格式化数据
    :format_target: 格式化目标
    :decorate_conf: 数据装饰器配置
    :returns: 已格式化数据

    """
    # 生成数据装饰器条目
    decorate_fields = dict()
    for key, value in decorate_conf.items():
        if key not in data.keys():
            decorate_fields[key] = value

    # 根据格式化目标将原始数据进行格式化
    if format_target.lower() in ['console']:
        data.update(decorate_fields)
    elif format_target.lower() in ['mqtt']:
        data.update(decorate_fields)

    return data


if __name__ == "__main__":
    target = 'console'
    data = {'output': 'example'}
    decorate_conf = {'module_name': 'formatter'}
    result = formatting(data=data,
                        format_target=target,
                        decorate_conf=decorate_conf)
    print(result)
