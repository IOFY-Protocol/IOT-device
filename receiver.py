# python3.6

import random
from decouple import config
from paho.mqtt import client as mqtt_client
from mypackage.lock_state import *
from apscheduler.schedulers.background import BackgroundScheduler

# Creates a default Background Scheduler
sched = BackgroundScheduler()

broker = config('BROKER')
port = int(config('PORT'))
lockTopic = config('LOCK_TOPIC')
ackTopic = config('ACK_TOPIC')
rtTopic = config('RT_TOPIC')
getIdTopic = config('GET_ID_TOPIC')
deviceIdTopic = config('DEVICE_ID_TOPIC')

deviceId = config('ID')
client_id = deviceId
topic = [("IOFY/ID/lock"+"/"+deviceId,0),("IOFY/ID/ACK/test",0),(getIdTopic,0)]
# generate client ID with pub prefix randomly





def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    #client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def subscribe(client: mqtt_client):
    client.subscribe(topic)
    client.on_message = on_message

def on_message(client, userdata, msg):
    if msg.topic == lockTopic+"/"+deviceId :
        if msg.payload.decode() == "1":
            print("lock device")
            lock_state()
            publish_ack(client, "ACK")
            if sched.state != 0:
                stop_rt_data()
        elif msg.payload.decode() == "0":
            print("unlock device")
            unlock_state()
            publish_ack(client, "ACK")
            if sched.state == 0:
                send_rt_data(client)
        elif msg.payload.decode() == "7":
            if sched.state != 0:
                stop_rt_data()
        else:
            print("lock Device Error")
            publish_ack(client, "NACK")
    elif msg.topic == getIdTopic:
        if msg.payload.decode() == "getId":
            print("sending device ID")
            send_id(client, deviceId)
    else:
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

def publish_ack(client: mqtt_client, msg):
    #msg = f"{msg_count}"
    result = client.publish(ackTopic, msg)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{ackTopic}`")
    else:
        print(f"Failed to send message to topic {ackTopic}")

def send_id(client: mqtt_client, msg):
    #msg = f"{msg_count}"
    result = client.publish(deviceIdTopic, msg)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{deviceIdTopic}`")
    else:
        print(f"Failed to send message to topic {deviceIdTopic}")

def send_rt_data(client):
    print("start sending real time data")
    sched.add_job(RTData,'interval', seconds=5, args=(client,))
    sched.start()

def stop_rt_data():
    print("stop sending real time data")
    sched.shutdown()
  
def RTData(client):
    print("send real time data")
    data = random.randint(0, 1000)
    msg = f"{data}"
    result = client.publish(rtTopic, msg)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{rtTopic}`")
    else:
        print(f"Failed to send message to topic {rtTopic}")


def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


if __name__ == '__main__':
    run()
