from pymodbus.client.sync import ModbusSerialClient as ModbusClient
import time
import yaml
import logger


class TemphumiClient:
    unit = 0x1
    method = 'rtu'
    port = 'COM3'
    timeout = 1
    baudrate = 4800
    addrcode =  1  #地址码
    startaddr = 0  #数据起始地址
    datalen = 2  #数据长度
    pubtopic = 'sensor/uart/temphumi'
    location = 'A1'
    interval = 3 #噪声采集间隔时间每3s一次
    client = None

    def __init__(self):
        '''
        初始化，从配置文件读取相关串口Modbus中建大仁科温湿度的参数
        '''
        try:
            # 读取配置文件
            f = open("config.yaml","r+",encoding="utf-8")
            fstream = f.read()
            configobj = yaml.safe_load(fstream)
            self.unit = configobj['temphumi']['unit']
            self.method = configobj['temphumi']['method']
            self.port = configobj['temphumi']['port']
            self.timeout = configobj['temphumi']['timeout']
            self.baudrate = configobj['temphumi']['baudrate']
            self.pubtopic = configobj['temphumi']['pubtopic']
            self.location = configobj['temphumi']['location']
            self.interval = configobj['temphumi']['interval']
            self.addrcode = configobj['temphumi']['holdingreg']['addrcode']
            self.startaddr = configobj['temphumi']['holdingreg']['startaddr']
            self.datalen = configobj['temphumi']['holdingreg']['datalen']
            
        except Exception as e:
            logger.writeLog("串口温湿度组件初始化失败-->" + str(e),'modbus.log')

    def genTemphumiClient(self):
        self.client = ModbusClient(method = self.method, 
                              port = self.port, 
                              timeout = self.timeout,
                              baudrate = self.baudrate)
        return self.client
    
    def genMQTTinfo(self, location, temprature, humidity):
        '''
        生成MQTT发布报文
        {"location":"F1","temp":332,"humi":333}
        '''
        info = {"location":location,"temp":temprature,"humi":humidity}
        return info


