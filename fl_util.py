import re
import sqlite3
import csv
import decimal
from xlrd import open_workbook

def question_marks(st):
    question_marks = '?'
    for i in range(0, len(st.split(','))-1):
        question_marks = question_marks + ",?"
    return question_marks

def zero_paddings(header, line):
	zero_str = ""
	for i in range(len(line.split()), len(header.split(','))-1):
		zero_str = zero_str + " 0"
	return zero_str

def dec(s):
	if s == "":
		return s
	try:
		return decimal.Decimal(str(s))
	except:
		return s

def csv_to_arr(csv_file):
	arr = []
	with open(csv_file, 'rU') as f:
		reader = csv.reader(f)
		arr = list(reader)
	header = ','.join(arr[0])
	arr = arr[1:]
	#print header
	return header, arr

def tsv_to_arr(tsv_file):
    arr = []
    with open(tsv_file, 'rU') as f:
        reader = csv.reader(f, dialect="excel-tab")
        arr = list(reader)
	header = ','.join(arr[0])
    arr = arr[1:]
    return header, arr

def xlsx_to_arr(xlsx_file):
	arr = []
	
	workbook = open_workbook(xlsx_file)
	worksheet = workbook.sheet_by_index(0)

	for row in xrange(0, worksheet.nrows):
		xlsx_row = worksheet.row(row)
		row_arr = []
		for cell in xlsx_row:
			row_arr.append(cell.value) 
		arr.append(row_arr)

	header = arr[0]
	return ','.join(header), arr[1:]

def adapt_decimal(d):
	return str(d)

def convert_decimal(s):
	return decimal.Decimal(s)

def dict_factory(cursor, row):
	d = {}
	for idx, col in enumerate(cursor.description):
		d[col[0]] = row[idx]
	return d

def db_cur():
	# Register the adapter
	sqlite3.register_adapter(decimal.Decimal, adapt_decimal)

	# Register the converter
	sqlite3.register_converter("DECTEXT", convert_decimal)
	conn = sqlite3.connect(":memory:", detect_types=sqlite3.PARSE_DECLTYPES)
	conn.row_factory = sqlite3.Row
	cur = conn.cursor()

	return conn, cur

def create_tbl(cur, tbl_name, header, arr):
	header = '"'+'","'.join(header.split(','))+'"'
	cur.execute("CREATE TABLE " + tbl_name + " (" + header + ");")
	cur.executemany("INSERT INTO " + tbl_name + " VALUES ("+question_marks(header)+")", arr)
	return 

def remove_dup(str1, str2):
	strx = str1
	
	for word in str2.split():
		if not word in str1:
			strx = strx + ',' + word
	return strx