dnmap-mqtt

# Protocol Overview
## Network Discovery
The server send an ```S_HELLO``` message. If a client is already connected, it sends back a ```CL_HELLO```. When the server receives it, it investigate the queue. If the client is already in there, nothing is performed, otherwise the new client is added. 
```
   |   S_HELLO      |                |
   |--------------->|    S_HELLO     |
   |                |--------------->|
   |                |    CL_HELLO    |
   |    CL_HELLO    |<---------------|
   |<---------------|                |
   +                +                +
 server           broker           client
```
When a client is connected or reconnected, it sends a ```CL_HELLO```. When the server receives it, it investigate the queue. If the client is already in there, nothing is performed, otherwise the new client is added. 
```
   |                |    CL_HELLO    |
   |    CL_HELLO    |<---------------|
   |<---------------|                |
   +                +                +
 server           broker           client
```
When a clent has performed a nmap scan, it sends a ```DATA_REQ``` to the server to check if the connection is still alive. Then the server sends back a ```DATA_REQ_ACK```. The client replies with the data and in the end a ```DATA_ACK``` is sent by the server.
```
   |                |    DATA_REQ    |
   |    DATA_REQ    |<---------------|
   |<---------------|                |
   |  DATA_REQ_ACK  |                |
   |--------------->|  DATA_REQ_ACK  |
   |                |--------------->|
   |                |    PAYLOAD     |
   |    PAYLOAD     |<---------------|
   |<---------------|                |
   |     DATA_ACK   |                |
   |--------------->|     DATA_ACK   |
   |                |--------------->|
   +                +                +
 server           broker           client
```