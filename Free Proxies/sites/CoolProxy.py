import os
import base64
import configparser


config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(os.path.realpath(__file__)),"sites.conf"))

CountryCode = config["CoolProxy"]["CountryCode"]

class CoolProxy(object):
    def __init__(self, session, proxy_queue):
        self.session = session
        self.name = "CoolProxy"
        if CountryCode == 'All':
            self.url = "https://www.cool-proxy.net/proxies/http_proxy_list/sort:download_speed_average/direction:desc/page:{}"
        else:
            self.url = "https://www.cool-proxy.net/proxies/http_proxy_list/sort:download_speed_average/direction:desc/country_code:%s/page:{}" % CountryCode
        self.pq = proxy_queue
        print("[{}] Proxier is ready".format(self.name))

    def start(self):
        trs = []
        rot13 = str.maketrans( "ABCDEFGHIJKLMabcdefghijklmNOPQRSTUVWXYZnopqrstuvwxyz", "NOPQRSTUVWXYZnopqrstuvwxyzABCDEFGHIJKLMabcdefghijklm")
        for page in range(1,10):
            try:
                r = self.session.get(self.url.format(page))
                t = self.session.html(r)
                trs.extend(t.xpath("//table/tr[td[2]]"))
            except:
                print("[{}] Exception occured".format(self.name))

        print("[{}] Total number of {} proxies were found".format(self.name, len(trs)))
        for tr in trs:
            IP = tr.xpath("./td[1]/script/text()")[0]
            IP = IP.split('"')[1].translate(rot13)
            IP = base64.b64decode(IP).decode("utf-8")
            PORT = tr.xpath("./td[2]/text()")[0]
            TYPE = "HTTP"
            PROXY = '{}:{}'.format(IP, PORT)
            self.pq.put((TYPE, PROXY))

