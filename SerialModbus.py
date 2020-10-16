from pymodbus.client.sync import ModbusSerialClient as ModbusClient
import time
import yaml
import logger

class MODBUSclient:
    '''
    modbus类客户端，当前支持类型为 
    (1)noise(噪声) 
    (2)pt100(贴片式温度传感器)
    (3)temphumi(温湿度传感器-建大仁科)
    '''
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

    #pt100 特有属性
    damrange = 20 #DAM通道量程
    damexpand = 1.2 #DAM通道量程扩大值
    minma = 4 #最低电流值
    mapercelsius = 0.32 #对应电流为(20-4)/50=0.32mA/℃

     #水压
    waterpremax = 1.6
    waterpremin = 0

    devtype = 'noise' #默认初始化噪声传感器
    client = None
    

    def __init__(self,devtype="noise"):
        '''
        初始化，从配置文件读取相关串口Modbus参数
        '''
        try:
            self.devtype = devtype
            # 读取配置文件
            f = open("config.yaml","r+",encoding="utf-8")
            fstream = f.read()
            configobj = yaml.safe_load(fstream)
            #通用部分
            self.unit = configobj['modbus'][devtype]['unit']
            self.method = configobj['modbus'][devtype]['method']
            self.port = configobj['modbus'][devtype]['port']
            self.timeout = configobj['modbus'][devtype]['timeout']
            self.baudrate = configobj['modbus'][devtype]['baudrate']
            self.pubtopic = configobj['modbus'][devtype]['pubtopic']
            self.location = configobj['modbus'][devtype]['location']
            self.interval = configobj['modbus'][devtype]['interval']
            self.addrcode = configobj['modbus'][devtype]['holdingreg']['addrcode']
            self.startaddr = configobj['modbus'][devtype]['holdingreg']['startaddr']
            self.datalen = configobj['modbus'][devtype]['holdingreg']['datalen']

            if devtype == 'pt100':
                self.damrange = configobj['modbus'][devtype]['damrange']
                self.damexpand = configobj['modbus'][devtype]['damexpand']
                self.minma = configobj['modbus'][devtype]['minma'] #最低电流值
                self.mapercelsius = configobj['modbus'][devtype]['mapercelsius'] #对应电流
            if devtype == 'pressure':
                self.waterpremax = configobj['modbus'][devtype]['waterpremax']
                self.waterpremin = configobj['modbus'][devtype]['waterpremin']
            
        except Exception as e:
            logger.writeLog("串口modbus组件初始化失败-->" + str(e),'modbus.log')

    def genModClient(self):
        self.client = ModbusClient(method = self.method, 
                              port = self.port, 
                              timeout = self.timeout,
                              baudrate = self.baudrate)
        return self.client
    
    def genMQTTinfo(self, location, noise=0, temp=0, humi=0, waterpress=0):
        '''
        生成MQTT发布报文
        {"location":"F1","decibel":332}
        '''
        if self.devtype == 'noise':
            info = {"location":location,"decibel":noise}
        elif self.devtype == 'pt100':
            info = {"location":location,"pt100":temp}
        elif self.devtype == 'temphumi':
            info = {"location":location,"temp":temp,"humi":humi}
        elif self.devtype == 'pressure':
            info = {"location":location,"pressure":waterpress}
        else:
            info = 'genMQTTinfo error : not find match Device'
        return info
    
    def calcRealTemprature(self,temprature):
        '''
        devtype == pt100
        根据DAM-7082说明书公式计算正确的4-20mA电流值，并根据配置的区间
        计算正确的温度值
        电流真实val = Adata/0x7FFF * range * 120%
        0x7FFF = 32767
        '''
        symbol = temprature & 0x8000 #symbol = 0为正数 =1为负数
        temp = temprature & 0x7FFF #将最高位符号位赋值为0(避免对计算结果影响)
        temp = temp/32767 * self.damrange * self.damexpand 
        reltemp = temp - self.minma
        reltemp = round(reltemp / self.mapercelsius,2) #保留2位小数
        if symbol == 1:
            reltemp = 0 - reltemp
        return reltemp