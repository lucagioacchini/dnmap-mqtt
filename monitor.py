import psutil
import time 
import speedtest
from client import *
import uuid  
from os import getuid
from threading import Thread


class Monitor():
    def __init__(self):
        self.net = {
            'ul':.0,
            'dl':.0,
            'ping':.0
        }
        self.ram = .0

    def getRam(self):
        """Get RAM information
        """
        mem = psutil.virtual_memory()
        free = mem.available
        tot = mem.total
        free_perc = round(free/tot*100,2)

        self.ram = free_perc

    def getSpeed(self):
        """ Perform speedtest
        """
        servers = []
        threads = None
        print('Finding servers')
        s = speedtest.Speedtest()
        s.get_servers(servers)
        s.get_best_server()
        print('Testing download')
        s.download(threads=threads)
        print('Testing upload')
        s.upload(threads=threads)
        s.results.share()

        res = s.results.dict()
        
        self.net['dl'] = res['download']
        self.net['ul'] = res['upload']
        self.net['ping'] = res['ping']


    def genCli():
        """Generate and start a client
        """
        CL_ID = uuid.uuid4().hex
        
        t = Thread(target=Mqtt(CL_ID).run, args=())
        t.start()

if getuid()!=0:
    print('You need to have root privileges to run this script.')
    exit()

Monitor.genCli()
Monitor.genCli()