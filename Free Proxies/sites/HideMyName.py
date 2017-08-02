import os
import configparser

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(os.path.realpath(__file__)),"sites.conf"))

CountryCode = config["HideMyName"]["CountryCode"]

class HideMyName(object):
    def __init__(self, session, proxy_queue):
        self.session = session
        self.name = "HideMyName"
        if CountryCode == 'All':
            self.url = "https://hidemy.name/en/proxy-list/?type=hs5{}#list"
        else:
            self.url = "https://hidemy.name/en/proxy-list/?country=%s&type=hs5{}#list" % CountryCode
        self.pq = proxy_queue
        print("[{}] Proxier is ready".format(self.name))

    def start(self):
        trs = []
        try:
            r = self.session.get(self.url.format(""))
            t = self.session.html(r)
            trs.extend(t.xpath("//div[@id='content-section']/section[1]/div/table/tbody/tr"))
        except:
            print("[{}] Exception occured".format(self.name))

        for offset in [64, 128, 192, 256, 320]:
            try:
                r = self.session.get(self.url.format(offset))
                t = self.session.html(r)
                trs.extend(t.xpath("//div[@id='content-section']/section[1]/div/table/tbody/tr"))
            except:
                print("[{}] Exception occured".format(self.name))


        print("[{}] Total number of {} proxies were found".format(self.name, len(trs)))
        for tr in trs:
            IP = tr.xpath("./td[1]/text()")[0]
            PORT = tr.xpath("./td[2]/text()")[0]
            TYPE = tr.xpath("./td[5]/text()")[0]
            PROXY = '{}:{}'.format(IP, PORT)
            self.pq.put((TYPE, PROXY))

