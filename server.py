import paho.mqtt.client as paho_mqtt
import nmap
import time 
import json
import sys

TIMEOUT = 5
MQTT_BROKER = 'broker.hivemq.com'
MQTT_PORT = 1883

def usage():
    print(f"usage: {sys.argv[0]}")
    print("options:")
    print("  -f, --nmap-commands   Nmap commands file")
    exit()

def queueUpdate(mqtt, client):
    print()
    print(mqtt.queue)
    # If there are commands to process
    if len(mqtt.cmd) > 0:
        # If the client is not in the queue, register it and sends
        # command
        if client not in mqtt.queue:
            print(f'{client} not in queue')
            mqtt.queue[client] = mqtt.cmd.pop(0)
            sendCmd(mqtt, client, mqtt.queue[client])
            print('Command sent')
        # If the client is in the queue
        else: 
            print(f'{client} is in queue')
            # and if it is waiting, sends command
            if mqtt.queue[client]=='':
                print('The client is waiting') 
                mqtt.queue[client] = mqtt.cmd.pop(0)
                sendCmd(mqtt, client, mqtt.queue[client])
                print('Command sent')
    # If the commands are finished, register the client
    else:
        if client not in mqtt.queue:
            mqtt.queue[client] = ''

def sendCmd(mqtt, client, cmd):
    #print(f"Sending '{cmd}' to {client}")
    msg = json.dumps({
        'id':'server',
        'msg':cmd
    })
    mqtt.publish(f'dnmap/cmd/{client}', msg)

def netDiscovery(mqtt):
    """Send an HELLO message to the related topic to check if 
    some clients are waiting or are operative
    """
    msg = json.dumps({
        'id':'server',
        'msg':'HELLO'
    })
    mqtt.publish('dnmap/hello', msg)

def sendDataReqAck(mqtt, cl_id):
    #print('sending DATA_REQ_ACK')
    msg = json.dumps({
        'id':'server',
        'msg':'DATA_REQ_ACK'
    })
    mqtt.publish(f'dnmap/out/{cl_id}', msg)

def sendDataAck(mqtt, cl_id):
    #print('sending DATA_ACK')
    msg = json.dumps({
        'id':'server',
        'msg':'DATA_ACK'
    })
    mqtt.publish(f'dnmap/out/{cl_id}', msg)

def sendStart(mqtt):
    msg = json.dumps({
        'id':'server',
        'msg':'START'
    })
    mqtt.publish('dnmap', msg)

def loadCmds(fname):
    with open(fname, 'r') as file:
        cmd = file.readlines()
    # Remove some empty line
    for item in cmd:
        if item == '\n': cmd.remove('\n')
    # Replace the '\n' char from each line
    for i, item in enumerate(cmd):
        cmd[i] = item.replace('\n', '').replace('nmap', '')
    
    return cmd


class Mqtt():
    def __init__(self, clientID, nmap_cmd):
        self.cmd = nmap_cmd
        self.queue = {}
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
        print("Client connected")
        self.subscribe('dnmap/#')
        netDiscovery(self)
    
    def onMessage(self, client, userdata, msg):
        topic = msg.topic
        msg = json.loads(msg.payload)
        
        # Network Discovery
        if 'hello' in topic and 'CL' in msg['msg']:
            #print('CL_HELLO received')
            queueUpdate(self, msg['id'])
        
        # The client has data to send, and sends a DATA_REQ message.
        # The server replies with a DATA_REQ_ACK
        elif 'out' in topic and msg['msg'] == 'DATA_REQ':
            #print('DATA_REQ received')
            sendDataReqAck(self, msg['id'])
        
        # The client sends the scanning output to the server and it
        # sends back a DATA_ACK message
        elif 'out' in topic and 'DATA_'not in msg['msg']:
            #print(f"Data received from {msg['id']}")
            self.queue[msg['id']] = ''
            sendDataAck(self, msg['id'])
            #
            # Process Data
            #
            # Update the queue
            queueUpdate(self, msg['id'])

    def onDisconnect(self, client, userdata, rc):
        print('Client disconnected')
        pass
    def onSubscribe(self, client, userdata, mid, granted_qos):
        #print("Client subscribed")
        pass
    def onPublish(self, client, userdata, mid):
        pass


# Parsing the arguments and load the file
try:
    cmds = loadCmds(sys.argv[2])
except:
    usage()

# Start the server
server = Mqtt('server', cmds)

def status(serv):
    print(f"\nN\t{16*' '}ID{16*' '}\t\tCMD")
    for n, key in enumerate(serv.queue):
        if serv.queue[key] == '':
            print(f"{n+1}\t{key}\t  WAITING  ")
        else:
            print(f"{n+1}\t{key}\t{serv.queue[key]}")

# Start the loop
while True:
    #time.sleep(TIMEOUT)
    #status(server)
    #server.cli.connect()