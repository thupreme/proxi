import socket
import pickle
import time

class ProxierInterface(object):
    def __init__(self, scrapername):
        self.__proxier_host = "localhost"
        self.__proxier_port = 30000
        self.__scrapername = scrapername
        self.__test_url = None
        print("[{}] Proxier interface is ready".format(self.__scrapername))

    @property
    def test_url(self):
        return self.__test_url

    @test_url.setter
    def test_url(self, x):
        self.__test_url = x
        try:
            self.__socket.send(pickle.dumps({"CMD":"STST", "TEST_URL":x}))
            data = pickle.loads(self.__socket.recv(1024))
        except:
            pass

    def start_proxier(self):
        self.__socket.send(pickle.dumps("START"))
        data = pickle.loads(self.__socket.recv(1024))
        if data:
            print("[{}] Proxier is started".format(self.__scrapername))
            return True
        else:
            print("[{}] Failed to start proxier".format(self.__scrapername))
            return False

    def connect(self):
        while True:
            try:
                print("[{}] Trying to connect to proxier server".format(self.__scrapername))
                self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.__socket.connect((self.__proxier_host, self.__proxier_port))
                #~ self.__socket.send(pickle.dumps({"CMD":"NEW"}))
                data = self.__socket.recv(1024)
                self.proxier_id = pickle.loads(data)
                print("[{}] Proxier connection establised".format(self.__scrapername))
                print("[{}] Proxier id is {}".format(self.__scrapername, self.proxier_id))
                if self.test_url != None:
                    self.__socket.send(pickle.dumps({"CMD":"STST", "TEST_URL":self.test_url}))
                    data = pickle.loads(self.__socket.recv(1024))
                self.start_proxier()
                break
            except:
                print("[{}] Proxier connection failed. Trying again after 5 seconds".format(self.__scrapername))
                time.sleep(5)     

    def request_proxy(self):
        self.__socket.send(pickle.dumps("GET"))
        return pickle.loads(self.__socket.recv(1024))
        
