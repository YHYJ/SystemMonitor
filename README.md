# README

System Monitor

---

## Table of Contents

<!-- vim-markdown-toc GFM -->

* [简介](#简介)

<!-- vim-markdown-toc -->

---

直接执行monitor.py将会把格式化后的系统监视信息打印到console

执行main.py将会把格式化后的系统监视信息根据配置文件输出到指定位置

---

## 简介

SystemMonitor用于提取指定模块的系统信息并输出到指定位置（Console, MQTT...）

目前支持的模块有：

- [ x ] 自定义
- [ x ] CPU
- [ x ] 内存（Memory和Swap）
- [ x ] 磁盘
- [ x ] 网卡
- [ x ] 进程
