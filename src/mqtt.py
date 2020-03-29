import paho.mqtt.client as mqtt
import json

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
        print(msg)
        topic = msg.topic
        msg = json.loads(msg.payload)
        print(msg)
        # Route Discovery
        if 'hello' in topic:
            queueUpdate(msg['id'])

    def onDisconnect(self, client, userdata, rc):
        print('Client disconnected')

    def onSubscribe(self, client, userdata, mid, granted_qos):
        print("Client subscribed")
    
    def onPublish(self, client, userdata, mid):
        print("Message published")

        