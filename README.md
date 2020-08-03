# Distributed Nmap Scanning System Over MQTT
This is a simple distributed nmap scanning system through mqtt.<br>
The master node, or server, reads the nmap commands from a .txt files. If one or more clients are waiting for commands, the master node sends a command to each node.<br>
When a client completes the network scanning, it sends back to the master the JSON output which is processed and updated to a local InfluxDB database. 

## Simple Protocol Overview
To make reliable the communication between all the nodes, a simple protocol has been developed.<br>
Since this project is mqtt-based, all the nodes can communicate between each other through an mqtt broker.<br>
The very first function of the server is reading the commands file, storing them in a commands queue and performing the network discovery to know the clients status.

### Network Discovery
When the server is connected or reconnected to the broker, it broadcasts an ```S_HELLO``` message exploiting a dedicated topic. If a client is already connected and subscribed to the relative topic, it sends back a ```CL_HELLO```. When the server receives it, it investigates the clients queue. If the client is already in there, it is procesed as it is shown later, otherwise the new client is added. 
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
When a client is connected or reconnected, it broadcasts a ```CL_HELLO``` exploiting a dedicated topic. When the server receives it, it investigates the clients queue. If the client is already in there, it is procesed as it is shown later, otherwise the new client is added. 
```
   |                |    CL_HELLO    |
   |    CL_HELLO    |<---------------|
   |<---------------|                |
   +                +                +
 server           broker           client
```

### Network Maintenance
The server periodically sends a ```S_HELLO``` as in the Network discovery. <br>
To monitor the clients status, a request counter is associated to each node. After having sent the ```S_HELLO```, all the request counters are incremented by one. If the master node receive a response by the client, it sets its request counter to 0, otherwise. When a request counter is greater than 2, meaning that the client did not reply two times, it is considered inactive with a flag.<br>
When the server receive a ```CL_HELLO``` containing the client ID, it checks in the clients queue if it is already in there. <br>
1. If the client is a new one, its ID is added to the client queue with a ```WAITING``` flag. After that, if there is still a command to be processed in the command queue, the server assigns it to the new client and changes its flag to ```ACTIVE```
2. If the client is already in the queue, the request counter is reset to 0.

### Commands Handling
When a clent has performed a nmap scan, it sends the data and a ```DATA_ACK``` is sent by the server.
```
   |                |      DATA      |
   |      DATA      |<---------------|
   |<---------------|                |
   |     DATA_ACK   |                |
   |--------------->|     DATA_ACK   |
   |                |--------------->|
   +                +                +
 server           broker           client
```

##
(c) 2020, Luca Gioacchini
