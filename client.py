from src.mqtt import Client
import nmap
import time
import json

CL_ID = 'client1'

client = Client(CL_ID)

msg = json.dumps({
    'id':CL_ID,
    'msg':'HELLO'
})
client.publish('dnmap/hello', msg)
client.stop()