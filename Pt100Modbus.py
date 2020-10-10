from pymodbus.client.sync import ModbusSerialClient as ModbusClient
import time
import yaml
import logger


class PT100client:
    unit = 0x1
    method = 'rtu'
    port = 'COM3'
    timeout = 1
    baudrate = 9600
    addrcode =  1  #地址码
    startaddr = 2  #数据起始地址
    datalen = 1  #数据长度
    pubtopic = 'sensor/uart/pt100'
    location = 'A1'
    interval = 3 #噪声采集间隔时间每3s一次
    damrange = 20 #DAM通道量程
    damexpand = 1.2 #DAM通道量程扩大值
    minma: 4 #最低电流值
    mapercelsius: 0.32 #对应电流为(20-4)/50=0.32mA/℃

    client = None

    def __init__(self):
        '''
        初始化，从配置文件读取相关串口Modbus中Pt100的参数
        '''
        try:
            # 读取配置文件
            f = open("config.yaml","r+",encoding="utf-8")
            fstream = f.read()
            configobj = yaml.safe_load(fstream)
            self.unit = configobj['pt100']['unit']
            self.method = configobj['pt100']['method']
            self.port = configobj['pt100']['port']
            self.timeout = configobj['pt100']['timeout']
            self.baudrate = configobj['pt100']['baudrate']
            self.pubtopic = configobj['pt100']['pubtopic']
            self.location = configobj['pt100']['location']
            self.interval = configobj['pt100']['interval']
            self.addrcode = configobj['pt100']['holdingreg']['addrcode']
            self.startaddr = configobj['pt100']['holdingreg']['startaddr']
            self.datalen = configobj['pt100']['holdingreg']['datalen']
            self.damrange = configobj['pt100']['damrange']
            self.damexpand = configobj['pt100']['damexpand']
            self.minma = configobj['pt100']['minma'] #最低电流值
            self.mapercelsius = configobj['pt100']['mapercelsius'] #对应电流
            
        except Exception as e:
            logger.writeLog("串口Pt100组件初始化失败-->" + str(e),'modbus.log')

    def genPtClient(self):
        self.client = ModbusClient(method = self.method, 
                              port = self.port, 
                              timeout = self.timeout,
                              baudrate = self.baudrate)
        return self.client
    
    def genMQTTinfo(self, location, temprature):
        '''
        生成MQTT发布报文
        {"location":"F1","pt100":332}
        '''
        info = {"location":location,"pt100":temprature}
        return info
    
    def calcRealTemprature(self,temprature):
        '''
        根据DAM-7082说明书公式计算正确的4-20mA电流值，并根据配置的区间
        计算正确的温度值
        电流真实val = Adata/0x7FFF * range * 120%
        0x7FFF = 32767
        '''
        symbol = temprature & 0x8000 #symbol = 0为正数 =1为负数
        temp = temprature & 0x7FFF #将最高位符号位赋值为0(避免对计算结果影响)
        temp = temp/32767 * self.damrange * self.damexpand 
        reltemp = temp - self.minma
        reltemp = round(reltemp / self.mapercelsius,4) #保留4位小数
        if symbol == 1:
            reltemp = 0 - reltemp
        return reltemp


