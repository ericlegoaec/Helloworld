import os
import sys
import csv
import re
import sqlite3
import requests
import datetime
import glob
import pandas as pd
import numpy as np

CONST_DIC = {
	"sqlite_file": "/Users/frederickli/Projects/tmp/tickdata.db",
	"dw_list_file": "/Users/frederickli/Projects/tmp/CFBC_20180622/dwFullList_20180622.csv",
	"td30_file": "/Users/frederickli/Projects/tmp/CFBC_20180622/MC30_AllFB_20180622.csv",
	"tmp_file": "/Users/frederickli/Projects/tmp/CFBC_20180622/tmp.csv",
}

HEADER = "ordertime,msgtype,security,tradeid,orderid,price,quantity,trdtype,ticktime,side,ordertype,orderboookposition,aggshare" #+ (','.join(["arb_" + str(x) for x in range(13,18)]))

def timer(func):
	def wrapper(*args, **kwargs):
		t1 = datetime.datetime.now()
		func(*args, **kwargs)
		t2 = datetime.datetime.now()
		print( "Function %s Time it took to run the function: %s" % (func.__name__, str(t2 - t1)) )
	return wrapper
	
def question_marks(st):
	question_marks = '?'
	for i in range(0, len(st.split(','))-1):
		question_marks = question_marks + ",?"
	return question_marks

def db_cur(source = ":memory:"):
	# sqlite3.register_adapter(decimal.Decimal, adapt_decimal)
	# sqlite3.register_converter("DECTEXT", convert_decimal)
	conn = sqlite3.connect(source, detect_types=sqlite3.PARSE_DECLTYPES)
	conn.row_factory = sqlite3.Row
	cur = conn.cursor()

	return conn, cur

def create_tbl(cur, tbl_name, header, arr = None, index_arr = None):
	cur.execute("""select count(*) FROM sqlite_master WHERE type='table' AND name = '%s' """ % (tbl_name))
	tbl_exists = cur.fetchone() 
	if tbl_exists[0] == 0:
		cur.execute("CREATE TABLE " + tbl_name + " (" + header + " );")
		if index_arr is not None:
			for index in index_arr:
				cur.execute("CREATE INDEX " + tbl_name + "_" + index + " ON " + tbl_name + " (" + index + ");")
	else:
		cur.execute("""Delete From %s""" % (tbl_name))
		
	if arr is not None and len(arr) > 0:
		cur.executemany("INSERT INTO " + tbl_name + "( " + header + " ) VALUES ("+question_marks(header)+")", arr)
	return 

def csv_to_arr(csv_file, has_header=True, delim=',', rows=None, cols=None ):
	arr = []
	reader = []

	text = open(csv_file, 'rU')

	reader = csv.reader(text, delimiter=delim)

	arr = list(reader)
	arr = np.array(arr)

	if rows != None:
		arr = arr[rows,:]

	if cols != None:
		arr = arr[:,cols]
	
	header = ""

	if has_header:
		header = ','.join(arr[0])
		return re.sub(r"[?\*\.#/\$%\"\(\)& \_-]", "", header), arr[1:]
	else:
		return arr

	return


@timer
def make_tmp():
	fulllist_df = pd.read_csv(max(glob.iglob(CONST_DIC["dw_list_file"])), encoding='utf-16', index_col=False, skip_blank_lines=True, error_bad_lines=False, sep='\t', skiprows=1)
	fulllist_df = fulllist_df.iloc[0:-3]
	fulllist_df.columns = [re.sub(r"[\^\*\.#/\$%\"\(\)& :]", "", c) for c in fulllist_df.columns]
	fulllist_df = fulllist_df.rename(columns={"DWCode":"security"})

	arr = csv_to_arr(CONST_DIC["td30_file"], has_header=False, cols=list(range(0,13)) )
	df = pd.DataFrame(data=arr, columns=HEADER.split(','))

	df = pd.merge(df, fulllist_df, on=["security"], how="left")
	print (df.iloc[1])
	lite_df = df.loc[(df.UL == "00700") | (df.security == "700")][HEADER.split(',')]
	lite_df = lite_df.iloc[1:100000]
	lite_df.to_csv(CONST_DIC["tmp_file"], index=False, header=False)

	return
def main():

	return

main()