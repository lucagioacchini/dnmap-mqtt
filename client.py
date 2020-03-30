import paho.mqtt.client as paho_mqtt
import nmap
import time
import json
import uuid  
from threading import Thread

CL_ID = uuid.uuid1().hex
MQTT_BROKER = 'broker.hivemq.com'
MQTT_PORT = 1883

QUEUE = {}

def sendAck(mqtt):
    print('Sending CL_HELLO')
    msg = json.dumps({
        'id':CL_ID,
        'msg':'CL_HELLO'
    })
    mqtt.publish('dnmap/hello', msg)

def sendDataReq(mqtt):
    print('Sending DATA_REQ')
    mqtt.done = True
    msg = json.dumps({
        'id':CL_ID,
        'msg':'DATA_REQ'
    })
    mqtt.publish(f'dnmap/out/{CL_ID}', msg)

def sendData(mqtt):
    print('Sending DATA')
    msg = json.dumps({
        'id':CL_ID,
        'msg':mqtt.res
    })
    mqtt.publish(f'dnmap/out/{CL_ID}', msg)

def scanner(mqtt, msg):
    print('Here1')
    mqtt.res = nmap.PortScanner().scan(msg['msg'])
    print('Here2')
    sendDataReq(mqtt)
    time.sleep(20)

class Mqtt():
    def __init__(self, clientID):
        self.done = False
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
        self.subscribe('dnmap/hello')
        self.subscribe(f'dnmap/cmd/{CL_ID}')
        self.subscribe(f'dnmap/out/{CL_ID}')
        sendAck(self)
    
    def onMessage(self, client, userdata, msg):
        topic = msg.topic
        msg = json.loads(msg.payload)

        # Notify the cliet activeness
        if 'hello' in topic and 'CL' not in msg['msg']:
            print('S_HELLO received')
            sendAck(self)
        
        # When the server sends the nmap command to perform, the 
        # client runs it and sends back the DATA_REQ when it has
        # finished
        elif 'cmd' in topic:
            print(f"Scanning network: {msg['msg']}")
            t = Thread(target=scanner, args=(self, msg))
            t.start()

        # Receive DATA_REQ_ACK and send the output
        elif 'out' in topic and msg['msg'] == 'DATA_REQ_ACK':
            print('DATA_REQ_ACK received')
            sendData(self)
        
        # When the DATA_ACK is received, the client waits for 
        # new instructions
        elif 'out' in topic and msg['msg'] == 'DATA_ACK':
            print('DATA_ACK received')
            self.done = False

    def onDisconnect(self, client, userdata, rc):
        print('Client disconnected')

    def onSubscribe(self, client, userdata, mid, granted_qos):
        print("Client subscribed")
    
    def onPublish(self, client, userdata, mid):
        pass


# Start the server
client = Mqtt(CL_ID)

# Start the loop
while True:
    pass