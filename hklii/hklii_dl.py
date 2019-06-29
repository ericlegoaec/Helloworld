
import requests
import os
import sys
import re
from six import string_types
from bs4 import BeautifulSoup

CHROME_HEADER = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

URL_DIC = {
    "hkcfa": "http://www.hklii.org/eng/hk/cases/hkcfa/",
}

def main():
    
    for key, url in URL_DIC.items():
        res = requests.get(url, headers=CHROME_HEADER)
        print (len(res.text))
        f = open(os.path.join(os.path.dirname(__file__), "x.html"), "w+")
        f.write(res.text)
        f.close
        soup = BeautifulSoup(res.text, 'html.parser')
        years = soup.select("a[href*=location]")
        print (str(years))
        
    return

if __name__ == "__main__":
    main()