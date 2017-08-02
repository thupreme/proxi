import os
import configparser

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(os.path.realpath(__file__)),"sites.conf"))

CountryCode = config["FreeProxyList"]["CountryCode"]

class FreeProxyList(object):
    def __init__(self, session, proxy_queue):
        self.session = session
        self.name = "FreeProxyList"
        self.url = "https://free-proxy-list.net/anonymous-proxy.html"
        self.pq = proxy_queue
        print("[{}] Proxier is ready".format(self.name))

    def start(self):
        trs = []
        try:
            r = self.session.get(self.url)
            t = self.session.html(r)
            if CountryCode != 'All':
                trs.extend(t.xpath("//table[@id='proxylisttable']/tbody/tr[td[3][text()='{}']]".format(CountryCode)))
            else:
                trs.extend(t.xpath("//table[@id='proxylisttable']/tbody/tr"))
                
        except:
            print("[{}] Exception occured".format(self.name))

        print("[{}] Total number of {} proxies were found".format(self.name, len(trs)))
        for tr in trs:
            IP = tr.xpath("./td[1]/text()")[0]
            PORT = tr.xpath("./td[2]/text()")[0]
            TYPE = "HTTP"
            PROXY = '{}:{}'.format(IP, PORT)
            self.pq.put((TYPE, PROXY))

