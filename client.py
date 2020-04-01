import paho.mqtt.client as paho_mqtt
import nmap
import time
import json
import uuid  
from threading import Thread
from os import getuid

DEBUG = 0

CL_ID = uuid.uuid1().hex
MQTT_BROKER = 'broker.hivemq.com'
MQTT_PORT = 1883

QUEUE = {}

def sendAck(mqtt):
    if DEBUG == 1:
        print('Sending CL_HELLO')
    msg = json.dumps({
        'id':CL_ID,
        'msg':'CL_HELLO'
    })
    mqtt.publish('dnmap/hello', msg)

def sendData(mqtt):
    if DEBUG == 1:
        print('Sending Data')
    msg = json.dumps({
        'id':CL_ID,
        'msg':mqtt.res
    })
    mqtt.publish(f'dnmap/out/{CL_ID}', msg)

def scanner(mqtt, msg):
    # If the client has been down, the packet has been dropped, but
    # now it is up again, change the once_down status
    if mqtt.connected and mqtt.once_down:
        mqtt.once_down = False
    if DEBUG == 1:
        print('Performing the scanning')
    mqtt.res = nmap.PortScanner().scan(msg['msg'])
    mqtt.res['nmap']['client'] = mqtt.clientID
    # If the client is connected and it has not been down during
    # the scanning, send data
    if mqtt.connected or not mqtt.once_down:
        if DEBUG == 1:
            print('Sending Data to the server')
        sendData(mqtt)
        mqtt.sent = True
    # Otherwise drop the packets
    else:
        if DEBUG == 1:
            print('Client down during scanning. Dropping Packet')

class Mqtt():
    def __init__(self, clientID):
        self.connected = False
        # Set True the following if the client is 
        # down while scanning 
        self.once_down = False 
        
        # Retransmission stuff
        self.serv_down = 0
        self.sent = False

        self.clientID = clientID
        self.cli = paho_mqtt.Client(self.clientID) 
        self.res = None
        # Register the callback
        self.cli.on_connect = self.onConnect
        self.cli.on_disconnect = self.onDisconnect
        self.cli.on_message = self.onMessage
        self.cli.on_publish = self.onPublish
        self.cli.on_subscribe = self.onSubscribe
        # Start the client
        self.start()

    def start(self):
        self.cli.connect(MQTT_BROKER, MQTT_PORT, keepalive=2)
        self.cli.loop_start()

    def stop (self):
        self.cli.loop_stop()
        self.cli.disconnect()

    def publish(self, topic, message):
        self.cli.publish(topic, message, 2)

    def subscribe(self, topic):
        self.cli.subscribe(topic)

    def onConnect(self, client, userdata, flags, rc):
        self.connected = True
        print("Client connected")
        self.subscribe('dnmap/hello')
        self.subscribe(f'dnmap/cmd/{CL_ID}')
        self.subscribe(f'dnmap/out/{CL_ID}')
        sendAck(self)
    
    def onMessage(self, client, userdata, msg):
        topic = msg.topic
        msg = json.loads(msg.payload)

        # Notify the cliet activeness
        if 'hello' in topic and 'CL' not in msg['msg']:
            if DEBUG == 1:
                print('S_HELLO received')
            sendAck(self)
            if self.sent:
                if self.serv_down >=3:
                    if DEBUG == 1:
                        print('Server was down. Retransmitting data')
                    sendData(self)
                else:
                    self.serv_down += 1
                
        # When the server sends the nmap command to perform, the 
        # client runs it and sends back the DATA_REQ when it has
        # finished
        elif 'cmd' in topic:
            print(f"Scanning network: {msg['msg']}")
            t = Thread(target=scanner, args=(self, msg))
            t.start()
        
        # When the DATA_ACK is received, the client waits for 
        # new instructions
        elif 'out' in topic and msg['msg'] == 'DATA_ACK':
            self.sent = False
            if DEBUG == 1:
                print('Waiting for new commands')

    def onDisconnect(self, client, userdata, rc):
        self.connected = False
        self.once_down = True
        print('Client disconnected')

    def onSubscribe(self, client, userdata, mid, granted_qos):
        if DEBUG == 1:
            print("Client subscribed")
    
    def onPublish(self, client, userdata, mid):
        if DEBUG == 1:
            print('Message published')

if getuid()!=0:
    print('You need to have root privileges to run this script.')
    exit()
# Start the server
client = Mqtt(CL_ID)

# Start the loop
while True:
    pass