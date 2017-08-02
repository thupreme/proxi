import socket
import pickle
import ast
import configparser

config = configparser.ConfigParser()
config.read("proxier_server.conf")

host = config["proxier_server"]["host"]
port = int(config["proxier_server"]["port"])
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))

print("Our identifier is {}".format(pickle.loads(s.recv(1024))))

while True:
    command = input("[[Proxier Test CLI >  ")
    if command == "GETN":
        n = input("[[Proxier Test CLI > Enter N >  ")
        for i in range(0, int(n)):
            c = "GET"
            s.send(pickle.dumps(c))
            data = s.recv(1024)
            print(pickle.loads(data))
    elif command == "STST":
        test_url = input("[[Proxier Test CLI > Enter Test URL >  ")
        s.send(pickle.dumps({"CMD":"STST", "TEST_URL":test_url}))
        data = s.recv(1024)
        print(pickle.loads(data))
    else:
        c = command
        s.send(pickle.dumps(c))
        data = s.recv(1024)
        print(pickle.loads(data))
