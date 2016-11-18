import re
import urllib
from pyquery import PyQuery as pq

website = "http://www.slideshare.net/khanyasmin/hedge-fund-manager-questionnaire"

result = urllib.urlopen(website).read()
d = pq(result)

ps = d(".slide_image")
for p in ps.items():
    img_src = p.attr("data-full")
    img_name = re.search("[^/\\&\?]+\.\w{3,4}(?=([\?&].*$|$))", img_src).group(0)
    urllib.urlretrieve(img_src, img_name)
