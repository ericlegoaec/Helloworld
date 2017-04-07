import requests
import re
import datetime

def post_content(link, parms):
	req = requests.post(link, params)
	result = req.text
	return result;

p_type = "C"
p_code = "CSA"

now = datetime.date.today()
p_year = now.year
p_month = now.month
p_day = now.day


link = "https://www.hkex.com.hk/eng/sorc/margin_data/margin_data_search.aspx"
params = {"type":p_type,"code":p_code,"year":p_year,"month":p_month,"day":p_day}

result = post_content(link, params)
# txtfile = open(outputpath+"index.htm", 'w')
# txtfile.write(toc)
# txtfile.close()
print result


