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

sensorweather = Weather()

def gendate():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("cmd")

def on_message(client, userdata, msg):
    '''
    命令报文格式 {
                    "gatewaysid":"aaaaaaa",
                    "sensorsid":"dfdfdfd",
                    "sensortype":"weather",  # weather  plug  leak
                    "cmd":"read", # read on off
                }
    '''
    msgstr = str(msg.payload,'utf-8')
    # print(gendate() + " " + msg.topic+"--->"+ msgstr)
    if len(str.strip(msgstr)) > 1: #判断报文是否为空
        try:
            msgobj = json.loads(msgstr)
            findobj = False #存放找到的设备信息
            #1.判断报文中携带的 网关SID是否存在
            for siditem in sensorgateway.sidlist:
                if siditem['sid'] == msgobj['gatewaysid']:
                    findobj = siditem
                    break
            if findobj != False:
                if findobj['token'] != 0:
                    if msgobj['sensortype'] == "plug" and (msgobj['cmd'] == 'on' or msgobj['cmd'] == 'off'):
                        insstr = sensorplug.writeStatus(msgobj['sensorsid'],findobj['key'],msgobj['cmd'],findobj["token"])
                        tempobj = {"gatewaysid":findobj['sid'],"gatewayip":findobj['ip'],"insstr":insstr}
                        msgque.put(tempobj)
                        print(gendate() + ' 生成控制开关指令--->' + str(tempobj))
                    elif findobj['sensortype'] == "weather" and findobj['cmd'] == 'weather':
                        # insstr = sensorweather.readDevStatus()
                        # msgque.put(insstr)
                        # print(gendate() + ' 生成查询温湿度大气压指令--->' + insstr)
                        pass
                    else:
                        # print(gendate() + ' 此指令无法识别--->' + msgstr)
                        pass
                else:
                    print(gendate() + ' 无法获取正确的网关心跳Token，指令生成失败, 稍后请重试: ' + msgstr)
            else:
                # logger.writeLog(gendate() + ' 未找到要执行操作的设备->'+ msg + '\nReson->'+ msgstr,'mqtt.log')
                print(gendate() + ' 未找到要执行操作的设备->'+ msg + '\nReson->'+ msgstr)
        except Exception as e:
            logger.writeLog(gendate() + ' MQTT指令格式错误->'+ msg + '\nReson->'+ str(e),'mqtt.log')
    else:
        logger.writeLog(gendate() + ' MQTT指令格式错误->' + '\nReson->'+ msgstr,'mqtt.log')


async def udpclientsend(udpclient,mqttclient):
    while True:
        if not msgque.empty():
            msg = msgque.get()
            # msg = input(">> ").strip()
            ip_port = (msg['gatewayip'], udpobj.port)
            try:
                udpclient.sendto(msg['insstr'].encode('utf-8'),ip_port)
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
                    if res['cmd'] == 'read_rsp':
                        if res['model'] == 'weather':
                            mqttinfo = sensorweather.genMQTTinfo(sensorgateway.location,
                                                         res['params'][1]['temperature'],
                                                         res['params'][2]['humidity'],
                                                         res['params'][3]['pressure'],
                                                         res['params'][0]['battery_voltage'])
                            mqttclient.publish(sensorgateway.weatherpubtopic,json.dumps(mqttinfo))
                    if res['cmd'] == 'write_rsp':
                        print('命令反馈' + str(res))
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
            if res['cmd'] == 'write_rsp':
                print(res)
            elif res['cmd'] == 'read_rsp':
                if res['model'] == 'weather':
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
            for gatewayitem in sensorgateway.sidlist:
                if res['sid'] == gatewayitem['sid']:
                    if res['cmd'] == 'heartbeat':
                        gatewayitem['token'] = res['token']
                        # "params":[{"ip":"192.168.43.8"}]
                        gatewayitem['ip'] = res['params'][0]['ip']
                        print(gendate() + '更新TOKEN--->' + str(gatewayitem))
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
    # looper.create_task(requestWeather(mqclient))

    mqclient.loop_start()
    looper.run_forever()
    
    


    