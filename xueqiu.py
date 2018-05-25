import re
import requests
import datetime
import time
import glob
import os
# from pyquery import PyQuery as pq


hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',}

symbol = "00700"
url = "http://xueqiu.com/S/" + symbol 
response = requests.get(url, headers=hdr)

# print (response.headers["Set-Cookie"])
# print (response.cookies)

url = "https://xueqiu.com/v4/stock/quote.json?code=" + symbol 
response = requests.get(url, headers=hdr, cookies=response.cookies)
print (response.text)
# d = pq(result)

# ps = d(".slide_image")
# for p in ps.items():
#     img_src = p.attr("data-full")
#     img_name = re.search("[^/\\&\?]+\.\w{3,4}(?=([\?&].*$|$))", img_src).group(0)
#     urllib.urlretrieve(img_src, img_name)
