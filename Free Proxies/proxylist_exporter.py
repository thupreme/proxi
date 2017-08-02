from proxier_interface import ProxierInterface
import sys
proxier = ProxierInterface("Client_X")
proxier.test_url = "http://www.footlocker.com"
proxier.connect()

try:
    outputfile = sys.argv[1]
except:
    outputfile = "proxylist.txt"

proxy_list = set()
while True:
    proxy_info = proxier.request_proxy()
    if proxy_info == None:
        break
    proxy = proxy_info['http']
    proxy_clean = proxy.strip('http://')
    if 'socks' not in proxy and proxy_clean not in proxy_list:
        with open(outputfile,"a") as plist:
            plist.write( proxy_clean + "\n")
        proxy_list.add(proxy_clean)
