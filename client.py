import paho.mqtt.client as paho_mqtt
import nmap
import time
import json

CL_ID = 'client1'
MQTT_BROKER = 'localhost'
MQTT_PORT = 1883

QUEUE = {}

def sendAck(mqtt):
    msg = json.dumps({
        'id':CL_ID,
        'msg':'CL_HELLO'
    })
    mqtt.publish('dnmap/hello', msg)
    

class Mqtt():
    def __init__(self, clientID):
        self.clientID = clientID
        self.cli = paho_mqtt.Client(self.clientID) 
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
        self.subscribe('dnmap/#')
        sendAck(self)
    
    def onMessage(self, client, userdata, msg):
        topic = msg.topic
        msg = json.loads(msg.payload)
        if 'hello' in topic and 'CL' not in msg['msg']:
            sendAck(self)

    def onDisconnect(self, client, userdata, rc):
        print('Client disconnected')

    def onSubscribe(self, client, userdata, mid, granted_qos):
        print("Client subscribed")
    
    def onPublish(self, client, userdata, mid):
        print("Message published")


# Start the server
client = Mqtt(CL_ID)

# Start the loop
while True:
    pass