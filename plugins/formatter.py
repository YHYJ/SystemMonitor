#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: formatter.py
Author: YJ
Email: yj1516268@outlook.com
Created Time: 2021-04-07 10:00:31

Description: 数据格式化工具
"""

import logging

logger = logging.getLogger('SystemMonitor.plugins.formatter')


def formatting(data, format_target, decorate_conf):
    """将数据进行格式化

    :data: 待格式化数据
    :format_target: 格式化目标
    :decorate_conf: 数据装饰器配置
    :returns: 已格式化数据

    """
    # 生成数据装饰器条目
    decorate_fields = dict()
    for key, field_value in decorate_conf.items():
        if key not in data.keys():
            decorate_fields[key] = field_value

    if isinstance(data, dict):
        if format_target.lower() in ['console']:
            # 添加装饰数据
            data.update(decorate_fields)
        elif format_target.lower() in ['mqtt']:
            # 添加装饰数据
            data.update(decorate_fields)

            # 获取到未经处理的fields
            raw_fields = data.pop('fields', dict())
            # 定义处理后的fields变量
            new_fields = dict()
            # 格式化数据
            for prefix, fields in raw_fields.items():
                if prefix in ['process']:
                    for field in fields:
                        if isinstance(field, dict):
                            postfix = field.get('keyword', str())
                            field_name = '{}_{}'.format(prefix, postfix)
                            field_value = field.get('running', 0)
                            field_type = 'float'
                            new_fields[field_name] = {
                                'name': field_name,
                                'value': field_value,
                                'type': field_type
                            }
                        else:
                            logger.warning("‘process’ data error, discard")
                else:
                    if isinstance(fields, dict):
                        for postfix, field_value in fields.items():
                            field_name = '{}_{}'.format(prefix, postfix)
                            if isinstance(field_value, (int, float)):
                                field_type = 'float'
                            elif isinstance(field_value, (list, dict)):
                                field_type = 'json'
                            else:
                                field_type = 'str'

                            new_fields[field_name] = {
                                'name': field_name,
                                'value': field_value,
                                'type': field_type
                            }
                    elif isinstance(fields, list):
                        field_name = '{}'.format(prefix)
                        field_value = fields
                        field_type = 'json'

                        new_fields[field_name] = {
                            'name': field_name,
                            'value': field_value,
                            'type': field_type
                        }

            # 重组格式化后的数据
            data['fields'] = new_fields
    else:
        logger.error('The type of data must be dict')

    return data


if __name__ == "__main__":
    target = 'console'
    data = {'output': 'example'}
    decorate_conf = {'module_name': 'formatter'}
    result = formatting(data=data,
                        format_target=target,
                        decorate_conf=decorate_conf)
    print(result)
