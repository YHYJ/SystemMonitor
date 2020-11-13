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

    #设备ID
    sid = ''
    #设备名称
    devname = ''

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
            self.sid = configobj['uartmodbus'][devtype]['sid']
            self.devname = configobj['uartmodbus'][devtype]['devname']
            self.unit = configobj['uartmodbus'][devtype]['unit']
            self.method = configobj['uartmodbus'][devtype]['method']
            self.port = configobj['uartmodbus'][devtype]['port']
            self.timeout = configobj['uartmodbus'][devtype]['timeout']
            self.baudrate = configobj['uartmodbus'][devtype]['baudrate']
            self.pubtopic = configobj['uartmodbus'][devtype]['pubtopic']
            self.location = configobj['uartmodbus'][devtype]['location']
            self.interval = configobj['uartmodbus'][devtype]['interval']
            self.addrcode = configobj['uartmodbus'][devtype]['holdingreg']['addrcode']
            self.startaddr = configobj['uartmodbus'][devtype]['holdingreg']['startaddr']
            self.datalen = configobj['uartmodbus'][devtype]['holdingreg']['datalen']
            

            if devtype == 'pt100':
                self.damrange = configobj['uartmodbus'][devtype]['damrange']
                self.damexpand = configobj['uartmodbus'][devtype]['damexpand']
                self.minma = configobj['uartmodbus'][devtype]['minma'] #最低电流值
                self.mapercelsius = configobj['uartmodbus'][devtype]['mapercelsius'] #对应电流
            if devtype == 'pressure':
                self.waterpremax = configobj['uartmodbus'][devtype]['waterpremax']
                self.waterpremin = configobj['uartmodbus'][devtype]['waterpremin']
            
        except Exception as e:
            logger.writeLog("串口uartmodbus组件初始化失败-->" + str(e),'uartmodbus.log')
    
    def gendate(self):
        '''
        返回当前日期时间
        '''
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    
    def genModClient(self):
        self.client = ModbusClient(method = self.method, 
                              port = self.port, 
                              timeout = self.timeout,
                              baudrate = self.baudrate)
        return self.client
    
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

    def calcpipe(self,rr):
        '''
        计算管道，用于对不同的modbus设备进行计算，并返回测量的数值
        '''
        if self.devtype == 'noise':
            decibel = int(rr.registers[0])
            print(self.gendate() + ':当前噪声值----> ' + str(decibel/10))
            mqttinfo = {"sid":self.sid,"devname":self.devname,"location":self.location,"decibel":decibel}
        elif self.devtype == 'pt100':
            mqttinfo = []
            for i in range(0, self.datalen):
                temprature = rr.registers[i]
                reltemp = self.calcRealTemprature(temprature)
                print(self.gendate() + ':当前序号为' + str(i) + '的PT100测量温度值----> ' + str(reltemp))
                tempinfo = {"sid":self.sid,"devname":self.devname,"location":self.location,"pt100":int(reltemp*100),"serialno":'pt'+str(i)}
                mqttinfo.append(tempinfo)
        elif self.devtype == 'temphumi':
            humi = int(rr.registers[0])
            temp = int(rr.registers[1])
            print(self.gendate() + ':当前温度湿度值----> ' + str(temp/10) +' '+ str(humi/10))
            mqttinfo = {"sid":self.sid,"devname":self.devname,"location":self.location,"temp":temp,"humi":humi}
        elif self.devtype == 'pressure':
            p = int(rr.registers[0])
            pre = round((self.waterpremax - self.waterpremin) / 2000 * p + self.waterpremin,2)
            print(self.gendate() + ':当前压力值----> ' + str(pre))
            mqttinfo = {"sid":self.sid,"devname":self.devname,"location":self.location,"pressure":int(pre*100)}
        return mqttinfo