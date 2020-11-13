import json
import yaml
import logger
from Encrypt import AqaraEncrypt

# 所有设备通用的方法
class AqaraDev:
    aqaencrypt = AqaraEncrypt() # AES CBC 128为加密对象

    # 单播发现设备
    def findSubDev(self):
        insobj = {"cmd":"discovery"}
        return json.dumps(insobj)
    
    # 单播读取设备状态
    def readDevStatus(self):
        insobj = {"cmd":"read","sid":self.sid}
        return json.dumps(insobj)

#网关
class Gateway(AqaraDev):
    sidlist = []    #网关sid列表  列表单个对象
    ''' 
                    [ 
                        {"sid": "44237c81c7b9",
                         "key": "3547993204669991",
                         "ip": "127.0.0.1",
                         "token":"dsfsdfsfddsf"
                         "sensorlist":[{"type": "weather","sid":"158d00045affc9"}]
                        }
                    ]
    '''
    desport = ''   #发送指令的目标端口
    interval = 10 #获取数据间隔，默认10s/次
    weatherpubtopic = '' #温湿度大气压发布MQTT主题
    leakpubtopic = '' #漏液检测发布MQTT主题

    def __init__(self):
        '''
        初始化，从配置文件读取网关参数
        '''
        try:
            # 读取配置文件
            f = open("config.yaml","r+",encoding="utf-8")
            fstream = f.read()
            configobj = yaml.safe_load(fstream)
            self.sidlist = configobj['gateway']['sidlist']
            self.location = configobj['gateway']['location']
            self.desport = configobj['gateway']['port']
            self.interval = configobj['gateway']['interval']
            self.weatherpubtopic = configobj['gateway']['weatherpubtopic']
            self.leakpubtopic = configobj['gateway']['leakpubtopic']
            # print(configobj)
        except Exception as e:
            logger.writeLog("网关组件初始化失败" + str(e),'dev.log')
    
    def getPlugSid(self, gatewayid):
        sidlist = []
        for items in self.sidlist:
            if items['sid'] == gatewayid:
                for item in items['sensorlist']:
                    if item['type'] == 'plug':
                        sidlist.append(items['sid'])
        return sidlist

    def getWeatherSid(self, gatewayid):
        sidlist = []
        for items in self.sidlist:
            if items['sid'] == gatewayid:
                for item in items['sensorlist']:
                    if item['type'] == 'weather':
                        sidlist.append(items['sid'])
        return sidlist


# 插座
class Plug(AqaraDev):
    # status = "on" 打开插座, status = "off" 关闭插座
    def writeStatus(self,sid,key,status,token):
        strkey = self.aqaencrypt.encrypt(key,token)
        insobj = {
            "cmd":"write",
            "model":"plug",
            "sid":sid,
            "key":strkey,
            "params":[{"channel_0":status}]
        }
        return json.dumps(insobj)

#温度湿度大气压传感器
class Weather(AqaraDev):
    
    def genMQTTinfo(self,location, temp = 0.0, humi = 0.0, press = 0.0, battery = 0):
        '''
        生成MQTT发布报文
        {"location":"F1","temperature":33.2,"humidity":88.3,"airpressure":98.2,"battery":2995}
        '''
        info = {"location":location,
                "temperature":temp,
                "humidity":humi,
                "airpressure":press,
                "battery":battery
                }
        return info

#门传感器
class SensorMagnet(AqaraDev):
    # 预留函数
    def passfun(self):
        pass

