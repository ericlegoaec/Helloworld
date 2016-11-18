import re
import urllib
from pyquery import PyQuery as pq

website = "http://www.hkex.com.hk/eng/invest/stock_data/cache/pricetable_page_e_XXX_3.htm"


for item in items:
	try:
		data1 = urllib.urlopen(website.replace("XXX", item)).read()
		f1 = open("prices\\" & item & ".htm", "w")
		f1.write(data1)
	except:
		print "Skipped: " & item
