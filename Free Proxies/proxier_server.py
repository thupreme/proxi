import socket
import pickle
import threading
import configparser

import os
import time
from queue import Queue

from proxier import Proxier
from common_tools import *


class ProxierClientHandler(threading.Thread):
    def __init__(self, clientsocket, addr):
        threading.Thread.__init__(self)
        self.__client = clientsocket
        self.__addr = addr
        self.__identifier = new_identifier()
        self.__queue = Queue(10)
        self.ProxierWatcher = ProxierWatcher(self.__queue)
        print("New client is connected. Client identifier is {}".format(self.__identifier))
        self.__client.send(pickle.dumps(self.__identifier))
        print("[{}] Client info: {}".format(self.__identifier, self.__addr))
            
    def run(self):
        self.ProxierWatcher.daemon = True
        self.ProxierWatcher.start()
        while True:
            try:
                data = self.__client.recv(1024)
                command = pickle.loads(data)
                print("[{}] Incoming command: {}".format(self.__identifier, command))
                if type(command) != dict:
                    if command == "GET":
                        proxy_info = self.__queue.get()
                        self.__client.send(pickle.dumps(proxy_info))
                        if proxy_info == None:
                            self.__queue.put(None)
                    elif command == "LEN":
                        self.__client.send(pickle.dumps(self.__queue.qsize()))
                    elif command == "START":
                        while not self.__queue.empty():
                            p = self.__queue.get()
                        self.ProxierWatcher.start_proxier = True
                        self.__client.send(pickle.dumps(True))
                    else:
                        self.__client.send(pickle.dumps(False))
                else:
                    if command['CMD'] == "STST":
                        TEST_URL = command['TEST_URL']
                        self.ProxierWatcher.test_url = TEST_URL
                        self.__client.send(pickle.dumps("Test URL is {}".format(TEST_URL)))
                    else:
                        self.__client.send(pickle.dumps(False))
            except EOFError:
                break

            except ConnectionResetError:
                break

            except:
                print("[{}] Exception: ".format(self.__identifier))
        self.__client.close()
        self.ProxierWatcher.giveup = True


class ProxierWatcher(threading.Thread):
    def __init__(self, q):
        threading.Thread.__init__(self)
        self.__start_proxier = False
        self.__giveup = False
        self.__test_url = None
        self.__proxy_queue = q

    @property
    def start_proxier(self):
        return self.__start_proxier

    @start_proxier.setter
    def start_proxier(self, x):
        self.__start_proxier = x

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

    def run(self):
        while True:
            if self.start_proxier:
                print("[Watcher] Starting new proxier")
                self.__proxier = Proxier(self.__proxy_queue)
                if self.test_url != None:
                    self.__proxier.test_url = self.test_url
                self.__proxier.daemon = True
                self.__proxier.start()
                self.start_proxier = False

            if self.giveup:
                self.__proxier.giveup = True
                self.giveup = False

            time.sleep(1)



config = configparser.ConfigParser()
config.read("proxier_server.conf")

host = config["proxier_server"]["host"]
port = int(config["proxier_server"]["port"])
mxcl = int(config["proxier_server"]["mxcl"])

proxier_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
proxier_server.bind((host, port))
proxier_server.listen(mxcl)

print("Proxier Server Started")
print("Listening: {}:{}".format(host, port))

while True:
    try:
        print(1)
        clientsocket, addr = proxier_server.accept()
        print(2)
        proxier_client_handler = ProxierClientHandler(clientsocket, addr)
        print(3)
        proxier_client_handler.daemon = True
        print(4)
        proxier_client_handler.start()
        print(5)
    except:
        x
        pass
