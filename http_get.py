import requests
import re

username = "thomas.ct.lee@htisec.com"
password = "oZ3*!vn"
website = "https://kbase.frontarena.com/Resources/Documents/FCA4384/23/webhelp2/"
outputpath = "D:/tmp/"

def getcontent(username, password, link):
    req = requests.get(link, auth=(username,password))
    result = req.text
    return result;

def extractlinks(content):
    urls = re.findall(r'href=[\'"]?([^\'" >]+)', content)
    for url in urls:
    	page = getcontent(username, password, website+url)
    	txtfile = open(outputpath+url, 'w')
    	txtfile.write(page.encode('utf-8'))
    	txtfile.close()
    	print "Written "+url+" OK"

    return;

toc = getcontent(username, password, website+"index.htm")
txtfile = open(outputpath+"index.htm", 'w')
txtfile.write(toc)
txtfile.close()
print "Written TOC"


