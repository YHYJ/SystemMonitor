import paho.mqtt.client as mqtt
import yaml
import logger

class MQTTclient:
    client = None
    clientid = None
    host = ''
    port = None
    keepalive = None
    
    def __init__(self):
        '''
        初始化，从配置文件读取MQTT参数
        '''
        try:
            # 读取配置文件
            f = open("config.yaml","r+",encoding="utf-8")
            fstream = f.read()
            configobj = yaml.safe_load(fstream)
            self.host = configobj['mqtt']['host']
            self.port =configobj['mqtt']['port']
            self.keepalive = configobj['mqtt']['keepalive']
            self.clientid = configobj['mqtt']['clientid']
        except Exception as e:
            logger.writeLog("MQTT组件初始化失败" + str(e),'mqtt.log')

    # 生成MQTT客户端
    def genMQTTClient(self):
        self.client = mqtt.Client(client_id=self.clientid)
        return self.client