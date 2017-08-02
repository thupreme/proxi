from lxml import html
from queue import Queue
from session import Session
from common_tools import *

import os
import threading
import importlib
import traceback
import configparser

config = configparser.ConfigParser()
config.read("proxier.conf")

connect_timeout = int(config["proxier"]["connect_timeout"])
read_timeout = int(config["proxier"]["read_timeout"])


NR_OF_PROXIERS = 3


identifier = new_identifier()

print("[{}] Proxier started".format(identifier))

scrapers = []
sites_dir = os.path.join(os.path.dirname(__file__), "sites")
site_modules = os.listdir(sites_dir)

for modulefile in site_modules:
    if modulefile == "__init__.py":
        continue
    if os.path.isfile(os.path.join(sites_dir, modulefile)) and modulefile.endswith(".py"):
        module_name = modulefile.split(".")[0]
        module = importlib.import_module("sites." + module_name)
        my_class = getattr(module, module_name)
        scrapers.append(my_class)

print("[{}] {} proxy scrapers found".format(identifier, len(scrapers)))

class Proxier(threading.Thread):
    def __init__(self, q):
        threading.Thread.__init__(self)
        self.session = Session()
        self.proxy_queue = q
        self.__giveup = False
        self.__test_url = "https://www.google.com"
        print("[{}] Proxier is ready".format(identifier))

    @property
    def giveup(self):
        return self.__giveup

    @giveup.setter
    def giveup(self, x):
        self.__giveup = x

    @property
    def test_url(self):
        return self.__test_url

    @test_url.setter
    def test_url(self, x):
        self.__test_url = x
        print("[{}] Test URL is set to {}".format(identifier, x))

    def run(self):
        self.alive = True
        self.__local_proxy_queue = Queue()
        self.__scraper_threads = []
        for scraper in scrapers:
            scraper_instance = scraper(self.session, self.__local_proxy_queue)
            print("[{}] Start proxy scraper:{}".format(identifier, scraper_instance.name))
            st = threading.Thread(target=scraper_instance.start)
            st.daemon = True
            st.start()
            self.__scraper_threads.append(st)

        self.__proxy_testers = []
        print("[{}] Start proxy testers".format(identifier))
        for i in range(0, NR_OF_PROXIERS):
            proxy_tester = threading.Thread(target=self.test_proxies)
            proxy_tester.daemon = True
            proxy_tester.start()
            self.__proxy_testers.append(proxy_tester)

        print("[{}] Start proxier threads handler".format(identifier))
        proxier_handler = threading.Thread(target=self.handle_proxier_threads)
        proxier_handler.daemon = True
        proxier_handler.start()

    def test_proxies(self):
        tester_identifier = new_identifier()
        print("[{}][{}] Proxy tester started".format(identifier, tester_identifier))
        while not self.giveup:
            print("[{}][{}]  Test queue size is {}".format(identifier, tester_identifier, self.__local_proxy_queue.qsize()))
            proxy2test = self.__local_proxy_queue.get()
            print("[{}][{}] Proxy to test: {}".format(identifier, tester_identifier, proxy2test))
            if proxy2test == None:
                print("[{}][{}] Oh None! Bye! ".format(identifier, tester_identifier, proxy2test))
                break
            TYPE, PROXY = proxy2test
            if "SOCKS5" in TYPE:
                proxy = {'http':'socks5://{}'.format(PROXY), 'https':'socks5://{}'.format(PROXY)}
            elif "HTTP" in TYPE:
                proxy = {'http':'http://{}'.format(PROXY), 'https':'https://{}'.format(PROXY)}

            #~ print("[{}][{}] Proxy string is {}".format(identifier, tester_identifier, proxy))
            if self.session.test_proxy(self.__test_url, proxy, connect_timeout, read_timeout):
                self.proxy_queue.put(proxy)
                print("[{}][{}]  Proxy queue size is {}".format(identifier, tester_identifier, self.proxy_queue.qsize()))

    def handle_proxier_threads(self):
        handler_identifier = new_identifier()
        print("[{}][{}] Handling scraper threads ".format(identifier, handler_identifier))
        finished = False
        while not finished and not self.giveup:
            finished = True
            for thread in self.__scraper_threads:
                if thread.is_alive():
                    finished = False
        print("[{}][{}] Scraper threads are finished ".format(identifier, handler_identifier))

        for i in range(0, NR_OF_PROXIERS):
            self.__local_proxy_queue.put(None)

        print("[{}][{}] Handling proxy testers ".format(identifier, handler_identifier))
        finished = False
        while not finished and not self.giveup:
            finished = True
            for thread in self.__proxy_testers:
                if thread.is_alive():
                    finished = False
        print("[{}][{}] Proxy testers are finished ".format(identifier, handler_identifier))
        self.alive = False
        print("[{}][{}] Proxier is not alive anymore ".format(identifier, handler_identifier))
        self.proxy_queue.put(None)
