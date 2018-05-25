import re
import requests
import datetime
import time
import glob
import os
# from pyquery import PyQuery as pq

url = "http://stock360.hkej.com/data/getQuotes/02333?t=" + str(int(time.mktime(datetime.datetime.now().timetuple())*1000 + (datetime.datetime.now().microsecond / 1000)))
print (url)
response = requests.get(url)
print (response.content)
# d = pq(result)

# ps = d(".slide_image")
# for p in ps.items():
#     img_src = p.attr("data-full")
#     img_name = re.search("[^/\\&\?]+\.\w{3,4}(?=([\?&].*$|$))", img_src).group(0)
#     urllib.urlretrieve(img_src, img_name)
