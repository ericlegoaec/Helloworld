import os
import sys
import csv
import requests

CONST_DIC = {
	"dw_list_file": "~/Projects/tmp/CFBC_20180622/dwFullList_20180622.csv",
	"td30_file": "~/Projects/tmp/CFBC_20180622/MC30_AllFB_20180622.csv",
}

HEADER = "ticktime,tradetype,ticker,"

def csv_to_arr(csv_file, start=0, end=0, has_header=True, delim=',', encoding='utf-8', ignore_cols=[]):
	arr = []
	reader = []

	if "http" in csv_file:
		response = requests.get(csv_file)
		text = response.content.decode(encoding)
	else:
		text = open(csv_file, 'rU')

	reader = csv.reader(text, delimiter=delim)

	arr = list(reader)

	if end != 0:
		arr = arr[start:end]
	else:
		arr = arr[start:]

	# arr = list(zip(*arr))
	# arr = [x for x in arr if any(x)]
	# for col in ignore_cols:
	# 	del arr[col]
	# arr = list(zip(*arr))
	
	header = ""

	if has_header:
		header = ','.join(arr[0])
		return re.sub(r"[?\*\.#/\$%\"\(\)& \_-]", "", header), arr[1:]
	else:
		return arr

	return

def main():

	return

main()