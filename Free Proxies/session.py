import requests
from lxml import html
from common_tools import *

import os


headers = {}
headers["User-Agent"] = "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36"
headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
headers["Accept-Encoding"] = "gzip, deflate"
headers["Upgrade-Insecure-Requests"] = "1"

class Session(object):
    def __init__(self):
        self.identifier = new_identifier()
        self.session = requests.Session()
        self.session.headers.update(headers)
        print("[{}] Proxier Session is ready".format(self.identifier))

    def get(self, url, read_timeout=60, max_retry_count=3):
        print("[{}] New url is requested: {}".format(self.identifier, url))
        for rt in range(0,max_retry_count):
            try:
                r = self.session.get(url, timeout=read_timeout)
                print("[{}] Connection okay: {}".format(self.identifier, url))
                return r
            except:
                print("[{}] Connection failed. Retrying: {}".format(self.identifier, url))

        print("[{}] Connection failed: {}".format(self.identifier, url))
        return False

    def test_proxy(self, url, proxy, connect_timeout=2, read_timeout=60):
        identifier = new_identifier()
        #~ print("[{}][{}] Proxy test request. PROXY:{} URL:{}".format(self.identifier, identifier, str(proxy), url))
        try:
            r = self.session.get(url, proxies=proxy, timeout=(connect_timeout, read_timeout))
            if r.ok:
                #~ print("[{}][{}] Proxy test success".format(self.identifier, identifier))
                return True
            else:
                #~ print("[{}][{}] Proxy test fail. PROXY:{} URL:{}".format(self.identifier, identifier, str(proxy), url))
                return False
        except:
            #~ print("[{}][{}] Proxy test fail. PROXY:{} URL:{}".format(self.identifier, identifier, str(proxy), url))
            return False

    def html(self, r):
        return html.fromstring(r.content)
