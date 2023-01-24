# python3.6

import random
from decouple import config
from paho.mqtt import client as mqtt_client
from mypackage.lock_state import *

broker = config('BROKER')
port = int(config('PORT'))
lockTopic = config('LOCK_TOPIC')
ackTopic = config('ACK_TOPIC')
topic = [("IOFY/ID/lock",0),("IOFY/ID/ACK/test",0)]
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 100)}'



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
    if msg.topic == lockTopic :
        if msg.payload.decode() == "1":
            print("lock device")
            lock_state()
            publish_ack(client, "ACK")
        elif msg.payload.decode() == "0":
            print("unlock device")
            unlock_state()
            publish_ack(client, "ACK")
        else:
            print("lock Device Error")
            publish_ack(client, "NACK")
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


def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


if __name__ == '__main__':
    run()
