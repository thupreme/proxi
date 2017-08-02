import hashlib
import time
import random


def current_time():
    return time.time()

def random_int(start, end):
    return random.randint(start, end)

def new_identifier():
    m = hashlib.md5()
    m.update(bytes(str(current_time()) + str(random_int(10000000, 999999999)), "utf-8"))
    identifier = m.hexdigest()
    return identifier[:10]
