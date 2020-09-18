# everything2mqtt

- 支持将绿米Aqara局域网组播UDP转发至MQTT特定主题下，并且支持控制指令下发时的token自动更新生成；
- 支持将ModbusRTU数据转发至MQTT特定主题下；



### 运行方式

udp->mqtt     

```shell
python udpMain.py
```

uart->mqtt    

```shell
 python  uartMain.py
```



### 依赖库列表

- asyncio
- PyYAML
- pycryptodome  (在Windows系统下安装)
- pycrypto  (在Linux系统下安装)
- paho-mqtt
- pymodbus

