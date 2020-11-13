# every2mqtt

- 支持将绿米Aqara局域网组播UDP转发至MQTT特定主题下，并且支持控制指令下发时的token自动更新生成；
- 支持将ModbusRTU数据转发至MQTT特定主题下；



### 运行方式
绿米智能网关
udp->mqtt     

```shell
python udpMain.py
```
#### Modbus串口模式

***注意：如果运行python uartMain.py不加 -device参数，则默认以噪声传感器方式运行***

​           ***即 python uartMain.py    ====      python uartMain.py -device=noise***

- 噪声传感器     

```shell
python uartMain.py -device=noise
```
- 贴片式温度传感器

```shell
python uartMain.py -device=pt100
```
- 建大仁科温湿度传感器

```shell
python uartMain.py -device=temphumi
```
- 水压传感器

```shell
python uartMain.py -device=pressure
```



#### Modbus TCP模式

- hpu数据采集

```
python tcpMain.py
```



### 依赖库列表

- asyncio
- PyYAML
- pycryptodome  (在Windows系统下安装)
- pycrypto  (在Linux系统下安装)
- paho-mqtt
- pymodbus



### 注意事项

- 如果在Linux运行UDP组播程序时遇到

  ```shell
   errno：19 no such device
  ```

  请使用**route -n** 查看组播地址是否已添加进路由表，如果没有请使用

  ```shell
  sudo route add -net 224.0.0.50 netmask 255.255.255.255 eth0
  ```

  224.0.0.50：为当前使用的多播IP地址

  eth0：为当前使用的有效网卡

