import paho.mqtt.client as mqtt
import nmap
import time 
import json
import sys


MQTT_BROKER = 'localhost'
MQTT_PORT = 1883

QUEUE = {}

def queueUpdate(client):
    if client in QUEUE:
        pass
    else:
        QUEUE[client] = 'nmapMessage'


class Client():
    def __init__(self, clientID):
        self.clientID = clientID
        self.cli = mqtt.Client(self.clientID) 
        # Register the callback
        self.cli.on_connect = self.onConnect
        self.cli.on_disconnect = self.onDisconnect
        self.cli.on_message = self.onMessage
        self.cli.on_publish = self.onPublish
        self.cli.on_subscribe = self.onSubscribe
        # Start the client
        self.start()

    def start(self):
        self.cli.connect(MQTT_BROKER, MQTT_PORT)
        self.cli.loop_start()

    def stop (self):
        self.cli.loop_stop()
        self.cli.disconnect()

    def publish(self, topic, message):
        self.cli.publish(topic, message, 2)

    def subscribe(self, topic):
        self.cli.subscribe(topic)

    def onConnect(self, client, userdata, flags, rc):
        print("Client connected")
    
    def onMessage(self, client, userdata, msg):
        topic = msg.topic
        msg = json.loads(msg.payload)
        # Route Discovery
        if 'hello' in topic:
            queueUpdate(msg['id'])

    def onDisconnect(self, client, userdata, rc):
        print('Client disconnected')

    def onSubscribe(self, client, userdata, mid, granted_qos):
        print("Client subscribed")
    
    def onPublish(self, client, userdata, mid):
        print("Message published")


# Parsing the arguments and load the file
if sys.argv[1] != '-f':
    print('Error')
else:
    with open(sys.argv[2], 'r') as file:
        cmd = file.read()

# Start the server and subscribe it
server = Client('server')
server.subscribe('dnmap/#')

# Start the loop
while True:
    pass