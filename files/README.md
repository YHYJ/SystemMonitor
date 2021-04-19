# service和timer文件说明

**注意：service和timer除后缀名之外文件名应该完全一致，否则无法匹配**

---

## Table of Contents

<!-- vim-markdown-toc GFM -->

* [service文件](#service文件)
* [timer文件](#timer文件)

<!-- vim-markdown-toc -->

---

只需使用命令`systemctl enable XXX.timer`使timer开机自启即可，它会自动调用对应的service

注意enable完成之后需要重启设备

---

## service文件

只需修改`[Service]`部分

- `WorkingDirectory`定义工作路径，即指定的命令相对于该目录执行
- `ExecStart`定义该service执行的命令

## timer文件

只需修改`[Timer]`部分

- `OnBootSec`定义系统启动之后多长时间启动一次timer
- `OnUnitActiveSec`定义距该timer最后一次启动的时间点多长时间之后再次启动该timer
