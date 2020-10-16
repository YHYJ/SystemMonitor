from SerialModbus import MODBUSclient
from MqttClient import MQTTclient
import asyncio
import json
import time
import queue
import argparse

msgque = queue.Queue(0)
devtype = '' #设备类型

def gendate():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("cmd")

def on_message(client, userdata, msg):
    msgstr = str(msg.payload,'utf-8')
    print(gendate() + " " + msg.topic+"--->"+ msgstr)

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")

async def runModbusClient(modbusclient,modbusobj,mqttclient):
    try:
        modbusclient.connect()
    except Exception as e:
        print(gendate() + ' Modbus连接失败！' + str(e))
    
    while True:
        try:
            rr = modbusclient.read_holding_registers(modbusobj.startaddr, modbusobj.datalen, unit=modbusobj.unit)
            if rr.registers:
                if devtype == 'noise':
                    decibel = int(rr.registers[0])
                    print(gendate() + ':当前噪声值----> ' + str(decibel/10))
                    mqttinfo = modbusobj.genMQTTinfo(location = modbusobj.location,noise = decibel)
                elif devtype == 'pt100':
                    temprature = rr.registers[0]
                    reltemp = modbusobj.calcRealTemprature(temprature)
                    print(gendate() + ':当前PT100测量温度值----> ' + str(reltemp))
                    mqttinfo = modbusobj.genMQTTinfo(location = modbusobj.location,temp = int(reltemp*100))
                elif devtype == 'temphumi':
                    humi = int(rr.registers[0])
                    temp = int(rr.registers[1])
                    print(gendate() + ':当前温度湿度值----> ' + str(temp/10) +' '+ str(humi/10))
                    mqttinfo = modbusobj.genMQTTinfo(location = modbusobj.location,temp = temp,humi = humi)
                elif devtype == 'pressure':
                    p = int(rr.registers[0])
                    pre = round((modbusobj.waterpremax - modbusobj.waterpremin) / 2000 * p + modbusobj.waterpremin,2)
                    print(gendate() + ':当前压力值----> ' + str(pre))
                    mqttinfo = modbusobj.genMQTTinfo(modbusobj.location, waterpress = int(pre*100))
                mqttclient.publish(modbusobj.pubtopic,json.dumps(mqttinfo))
        except Exception as e:
            print(gendate() + ' Modbus连接异常，尝试重新连接！' + str(e))
            try:
                modbusclient.close()
            except Exception as e:
                print(gendate() + ' Modbus尝试关闭连接失败！' + str(e))
            
            try:
                modbusclient.connect()
            except Exception as e:
                print(gendate() + ' Modbus尝试重新失败！' + str(e))
            await asyncio.sleep(3)
        finally:
            await asyncio.sleep(modbusobj.interval)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Every to MQTT')
    parser.add_argument("-device", type=str, default="noise")
    args = parser.parse_args()
    devtype = args.device

    mqttobj = MQTTclient()
    mqclient = mqttobj.genMQTTClient()
    mqclient.on_connect = on_connect
    mqclient.on_message = on_message
    mqclient.on_disconnect = on_disconnect
    mqclient.connect(mqttobj.host, mqttobj.port, mqttobj.keepalive)

    modbusobj = MODBUSclient(devtype)
    modclient = modbusobj.genModClient()

    looper = asyncio.get_event_loop()
    looper.create_task(runModbusClient(modclient,modbusobj,mqclient))

    mqclient.loop_start()
    looper.run_forever()
    
    


    