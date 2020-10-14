from Encrypt import AqaraEncrypt
from Devices import Gateway,Plug,Weather,SensorMagnet
from UdpClient import UDPclient
from MqttClient import MQTTclient
import asyncio
import json
import time
import queue
import logger

msgque = queue.Queue(0)
udpobj = UDPclient()
sensorgateway = Gateway()

sensorplug = Plug()
sensorplug.sid = sensorgateway.getPlugSid()[0]

sensorweather = Weather()
sensorweather.sid = sensorgateway.getWeatherSid()[0]

def gendate():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("cmd")

def on_message(client, userdata, msg):
    msgstr = str(msg.payload,'utf-8')
    # print(gendate() + " " + msg.topic+"--->"+ msgstr)
    if str.strip(msgstr) == 'on' or str.strip(msgstr) == 'off':
        if sensorgateway.token != '':
            insstr = sensorplug.writeStatus(str.strip(msgstr),sensorgateway.token)
            msgque.put(insstr)
            print(gendate() + ' 生成指令--->' + insstr)
        else:
            print(gendate() + ' 无法获取正确的网关心跳Token，指令生成失败: ' + msgstr)
    elif str.strip(msgstr) == 'weather':
        insstr = sensorweather.readDevStatus()
        msgque.put(insstr)
        print(gendate() + ' 生成指令--->' + insstr)
    else:
        print(gendate() + ' 此指令无法识别--->' + msgstr)


async def udpclientsend(udpclient,mqttclient):
    while True:
        if not msgque.empty():
            msg = msgque.get()
            # msg = input(">> ").strip()
            ip_port = (sensorgateway.ip, udpobj.port)
            try:
                udpclient.sendto(msg.encode('utf-8'),ip_port)
            except Exception as e:
                logger.writeLog(gendate() + ' 发送UDP请求指令失败->'+ msg + '\nReson->'+ str(e),'udpmain.log')
            print(gendate() + ' 等待接收信息--->')
            for i in range(0,3):
                await asyncio.sleep(1)
                try:
                    data,server_addr = udpclient.recvfrom(1024)
                except Exception:
                    pass
                else:
                    print(data, server_addr)
                    res = json.loads(data)
                    if res['model'] == 'weather':
                        if res['cmd'] == 'read_rsp':
                            mqttinfo = sensorweather.genMQTTinfo(sensorgateway.location,
                                                         res['params'][1]['temperature'],
                                                         res['params'][2]['humidity'],
                                                         res['params'][3]['pressure'],
                                                         res['params'][0]['battery_voltage'])
                            mqttclient.publish(sensorweather.mqtttopic,json.dumps(mqttinfo))
                    break
                i = i + 1
        await asyncio.sleep(0.01)


async def multirec(multiudp,mqttclient):
    '''
    接收组播信息
    wheather-->{"cmd":"read_rsp",
                "model":"weather",
                "sid":"158d00045affc9",
                "params":[{"battery_voltage":2995},
                          {"temperature":0},
                          {"humidity":0},
                          {"pressure":0}
                        ]
                }

    '''
    while True:
        try:
            data, address = multiudp.recvfrom(2048)
        except:
            pass
        else:
            # print(address)
            res = json.loads(data)
            if res['model'] == 'weather':
                if res['cmd'] == 'read_rsp':
                    mqttinfo = sensorweather.genMQTTinfo(sensorgateway.location,
                                                         res['params'][1]['temperature'],
                                                         res['params'][2]['humidity'],
                                                         res['params'][3]['pressure'],
                                                         res['params'][0]['battery_voltage'])
                    mqttclient.publish(sensorweather.mqtttopic,json.dumps(mqttinfo))
            elif res['model'] == 'plug':
                if res['cmd'] == 'heartbeat':
                    pass
            
            # print(gendate() + '-->' + json.dumps(res))
            if res['sid'] == sensorgateway.sid:
                if res['cmd'] == 'heartbeat':
                    sensorgateway.token = res['token']
                    # "params":[{"ip":"192.168.43.8"}]
                    sensorgateway.ip = res['params'][0]['ip']
                    print(gendate() + '--->' + sensorgateway.token)
        await asyncio.sleep(0.01)


async def requestWeather(mqttclient):
    while True:
        try:
            mqttclient.publish('cmd','weather')
        except:
            print('请求环境温度发送失败')
        finally:
            await asyncio.sleep(10)




if __name__ == "__main__":
    
    udpclient = udpobj.genUDPClient()
    muticlient = udpobj.genMulitiUDP()

    mqttobj = MQTTclient()
    mqclient = mqttobj.genMQTTClient()
    mqclient.on_connect = on_connect
    mqclient.on_message = on_message
    mqclient.connect(mqttobj.host, mqttobj.port, mqttobj.keepalive)

    looper = asyncio.get_event_loop()
    looper.create_task(udpclientsend(udpclient,mqclient))
    looper.create_task(multirec(muticlient,mqclient))
    looper.create_task(requestWeather(mqclient))

    mqclient.loop_start()
    looper.run_forever()
    
    


    