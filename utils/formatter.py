#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: formatter.py
Author: YJ
Email: yj1516268@outlook.com
Created Time: 2021-04-07 10:00:31

Description: 数据格式化工具
"""


def formatting(format_target, data):
    """将数据进行格式化

    :format_target: 格式化目标
    :data: 待格式化数据
    :returns: 已格式化数据

    """
    if format_target in ['console']:
        # TODO: 数据格式处理 <02-04-21, YJ> #
        result = data
    elif format_target in ['mqtt']:
        # TODO: 数据格式处理 <02-04-21, YJ> #
        result = data
    else:
        result = data

    return result


if __name__ == "__main__":
    target = 'json'
    data = {'output': 'example'}
    result = formatting(format_target=target, data=data)
    print(result)
