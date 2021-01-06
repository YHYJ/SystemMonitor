# every2mqtt

- ~~支持将绿米Aqara局域网组播UDP转发至MQTT特定主题下，并且支持控制指令下发时的token自动更新生成；~~(功能迁移至其他程序)
- 支持将ModbusRTU数据转发至MQTT特定主题下；
- 支持系统运行状态信息采集用于远程监控



### 配置文件

配置文件默认开启系统运行状态监控，可通过将isopen改为false关闭

请根据运行系统修改platform名称  windows   或  linux

```yaml
monitor:
    isopen: true #是否开启监控
    platform: windows
    devid: CR101
    devname: Nanopi-噪声北  #设备名称
    pubtopic: monitor #mqtt发布主题
    interval: 120 #采集频率 /秒
```



### 运行方式



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
- paho-mqtt
- pymodbus
- psutil

