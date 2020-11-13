from pymodbus.client.sync import ModbusTcpClient as ModbusClient
import time
import yaml
import logger
import copy
import struct


class MODBUSclient:
    '''
    TCPmodbus类客户端，当前支持类型为 
    (1)HPU油泵数据
    '''
    unit = 0x1
    method = 'tcp'
    iplist = ['192.168.100.1']
    port = 502
    pubtopic = 'sensor/tcp/hpu'
    location = 'A2'
    interval = 3 #采集间隔
    
    #hpu的地址对照表
    maptable = []

    devtype = 'hpu'
    client = None

    #设备ID
    sid = ''
    #设备名称
    devname = ''
    

    def __init__(self,devtype="hpu"):
        '''
        初始化，从配置文件读取TCPModbus参数
        '''
        try:
            self.devtype = devtype
            # 读取配置文件
            f = open("config.yaml","r+",encoding="utf-8")
            fstream = f.read()
            configobj = yaml.safe_load(fstream)
            #通用部分
            self.sid = configobj['tcpmodbus'][devtype]['sid']
            self.devname = configobj['tcpmodbus'][devtype]['devname']
            self.unit = configobj['tcpmodbus'][devtype]['unit']
            self.method = configobj['tcpmodbus'][devtype]['method']
            self.iplist = configobj['tcpmodbus'][devtype]['iplist']
            self.port = configobj['tcpmodbus'][devtype]['port']
            self.interval = configobj['tcpmodbus'][devtype]['interval']
            self.pubtopic = configobj['tcpmodbus'][devtype]['pubtopic']
            self.location = configobj['tcpmodbus'][devtype]['location']
            self.addrcode = configobj['tcpmodbus'][devtype]['addrcode']
            self.startaddr = configobj['tcpmodbus'][devtype]['startaddr']
            self.datalen = configobj['tcpmodbus'][devtype]['datalen']

            if devtype == 'hpu':
                self.maptable = configobj['tcpmodbus'][devtype]['maptable']
            
        except Exception as e:
            logger.writeLog("TCPmodbus组件初始化失败-->" + str(e),'tcpmodbus.log')
    
    def gendate(self):
        '''
        返回当前日期时间
        '''
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    
    def genModClient(self):
        self.client = ModbusClient(host=self.iplist[0],port = self.port)
        return self.client
    
    def calcpipe(self,rr):
        '''
        计算管道，用于对不同的modbus设备进行计算，并返回测量的数值
        '''
        mqttsendobj = {"sid":self.sid,"devname":self.devname,"devid":self.devid,"val":[]}
        if self.devtype == 'hpu':
            '''
            如果是HPU则需要根据配置文件中的对照表来进行解码赋值
            '''
            sendobj = {"name":"","val":[]}
            for mapobj in self.maptable:
                sendobj['name'] = mapobj['name']
                curindex = mapobj['startaddr'] - self.startaddr
                if mapobj['datalen'] > 1:
                    curvaluelist = []
                    for i in range(0,mapobj['datalen']):
                        curvaluelist.append(rr.registers[curindex+i])
                else:
                    curvaluelist=int(rr.registers[curindex])
                
                if str(mapobj['name']).find('running_time') != -1: #running_time字段的值占两个长度需要计算
                    datatemp = struct.pack('<HH', curvaluelist[0], curvaluelist[1])
                    curvaluelist = struct.unpack('<L', datatemp)[0]
                sendobj['val'] = curvaluelist
                mqttsendobj['val'].append(copy.deepcopy(sendobj))
            print(self.gendate() + ':当前HPU值----> ' + str(mqttsendobj))
            mqttinfo = mqttsendobj
        return mqttinfo