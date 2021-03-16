# every2mqtt

- 支持将ModbusRTU及ModbusTCP数据转发至MQTT特定主题下；
- 支持系统运行状态信息采集用于远程监控



### 配置文件

配置文件默认开启系统运行状态监控，可通过将isopen改为false关闭

```yaml
monitor:
    isopen: true #是否开启监控
    devid: CR101
    devname: Nanopi-噪声北  #设备名称
    pubtopic: eim/monitor #mqtt发布主题
    interval: 120 #采集频率 /秒
```



### 运行方式



#### Modbus串口模式

***注意：如果运行python Main.py不加 -device参数，则默认以噪声传感器方式运行***

​           ***即 python Main.py    ====      python Main.py -device=noise***

- 噪声传感器     

```shell
python Main.py -device=noise
```
- 贴片式温度传感器

```shell
python Main.py -device=pt100
```
- 建大仁科温湿度传感器

```shell
python Main.py -device=temphumi
```
- 水压传感器

```shell
python Main.py -device=pressure
```

- HPU电流传感器

```shell
python Main.py -device=ampere
```

#### Modbus TCP模式

- hpu数据采集

```shell
python Main.py -device=hpu
```



### 远程控制

程序会自动订阅cmd/all及cmd/devid主题，

通过  **cmd/all**  主题可以批量修改边缘设备的配置文件

通过 **cmd/devid** 主题可以单独修改特定边缘设备的配置文件

控制报文如下

```json
{
  "attr":"mqtt",
  "value":{
    "host":"127.0.0.1",
    "port": 1883,
    "keepalive":60,
    "clientid": "test12111"
  }
}
```

程序启动成功后，会在 cmd/feedback 主题下发布反馈报文如下

```json
{
  "devid" : "CR344",
  "info" : "启动成功",
  "date" : "2021-02-26 09:33:16"
}
```



### 依赖库列表

- asyncio
- PyYAML
- paho-mqtt
- pymodbus
- psutil

