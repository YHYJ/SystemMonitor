from pymodbus.client.sync import ModbusSerialClient as ModbusClient
import time
import yaml
import logger


class MODBUSclient:
    unit = 0x1
    method = 'rtu'
    port = 'COM3'
    timeout = 1
    baudrate = 9600
    addrcode =  1  #地址码
    startaddr = 0  #数据起始地址
    datalen = 1  #数据长度
    pubtopic = 'sensor/uart/noise'
    location = 'A1'
    interval = 3 #噪声采集间隔时间每3s一次

    client = None

    def __init__(self):
        '''
        初始化，从配置文件读取相关串口Modbus参数
        '''
        try:
            # 读取配置文件
            f = open("config.yaml","r+",encoding="utf-8")
            fstream = f.read()
            configobj = yaml.safe_load(fstream)
            self.unit = configobj['modbus']['unit']
            self.method = configobj['modbus']['method']
            self.port = configobj['modbus']['port']
            self.timeout = configobj['modbus']['timeout']
            self.baudrate = configobj['modbus']['baudrate']
            self.pubtopic = configobj['modbus']['pubtopic']
            self.location = configobj['modbus']['location']
            self.interval = configobj['modbus']['interval']
            self.addrcode = configobj['modbus']['holdingreg']['addrcode']
            self.startaddr = configobj['modbus']['holdingreg']['startaddr']
            self.datalen = configobj['modbus']['holdingreg']['datalen']
            
        except Exception as e:
            logger.writeLog("串口modbus组件初始化失败-->" + str(e),'modbus.log')

    def genModClient(self):
        self.client = ModbusClient(method = self.method, 
                              port = self.port, 
                              timeout = self.timeout,
                              baudrate = self.baudrate)
        return self.client
    
    def genMQTTinfo(self, location, noise):
        '''
        生成MQTT发布报文
        {"location":"F1","decibel":332}
        '''
        info = {"location":location,"decibel":noise}
        return info