import os
import configparser

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(os.path.realpath(__file__)),"sites.conf"))

CountryCode = config["ProxyDB"]["CountryCode"]

class ProxyDB(object):
    def __init__(self, session, proxy_queue):
        self.session = session
        self.name = "ProxyDB"
        if CountryCode == "All":
            self.url = "http://proxydb.net/?protocol=http&protocol=https&protocol=socks5&offset={}"
        else:
            self.url = "http://proxydb.net/?protocol=http&protocol=https&protocol=socks5&country=%s&offset={}" % CountryCode
            
        self.pq = proxy_queue
        print("[{}] Proxier is ready".format(self.name))

    def start(self):
        trs = []
        for offset in [0, 50, 100, 150, 200]:
            try:
                r = self.session.get(self.url.format(offset))
                t = self.session.html(r)
                trs.extend(t.xpath("//table/tbody/tr"))
            except:
                print("[{}] Exception occured".format(self.name))

        print("[{}] Total number of {} proxies were found".format(self.name, len(trs)))
        for tr in trs:
            PROXY = tr.xpath("./td[1]/a/text()")[0]
            TYPE = tr.xpath("./td[2]/text()")[0].strip()
            self.pq.put((TYPE, PROXY))

