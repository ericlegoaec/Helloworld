import os
import re
import sqlite3
import win32com.client

# Import xlsx file to an array, first line is header
# You may ignore ths function at this moment as it may be too complicated
def xlsx_to_arr(xlsx_file, worksheet=1, xyrange=""):
	arr = []
	xl = win32com.client.Dispatch('Excel.Application')
	xl.ScreenUpdating = False

	wb = xl.Workbooks.Open(xlsx_file)
	ws = wb.Worksheets(worksheet)
	rng = ws.UsedRange if xyrange == "" else ws.Range(xyrange)

	for i in range(rng.Row, rng.Row+rng.Rows.Count):
		row_arr = []
		for j in range(rng.Column, rng.Column+rng.Columns.Count):
			row_arr.append("" if ws.Cells(i, j).Value == None else str(ws.Cells(i, j).Value) ) 

		if "".join(row_arr) != "":
			arr.append(row_arr)

	wb.Close(False)

	xl.Application.Quit()
	
	header = arr[0]
	header = ','.join(header)
	return re.sub(r"[\*\.#/\$%\"\(\)& \_-]", "", header), arr[1:]

# For SQL insert statement, insert into tbl VALUES (?,?,?) arr
def question_marks(st):
	question_marks = '?'
	for i in range(0, len(st.split(','))-1):
		question_marks = question_marks + ",?"
	return question_marks

# Create a DB, default is in-memory DB
def db_cur(source = ":memory:"):
	conn = sqlite3.connect(source, detect_types=sqlite3.PARSE_DECLTYPES)
	conn.row_factory = sqlite3.Row
	cur = conn.cursor()

	return conn, cur

# Cerate table under a DB
def create_tbl(cur, tbl_name, header, arr = None, index_arr = None):
	cur.execute("""select count(*) FROM sqlite_master WHERE type='table' AND name = '%s' """ % (tbl_name))
	tbl_exists = cur.fetchone() 
	if tbl_exists[0] == 0:
		cur.execute("CREATE TABLE " + tbl_name + " (" + header.replace("id,", "id PRIMARY KEY,") + " );")
		if index_arr is not None:
			for index in index_arr:
				cur.execute("CREATE INDEX " + tbl_name + "_" + index + " ON " + tbl_name + " (" + index + ");")
		
	if arr is not None:
		cur.executemany("INSERT INTO " + tbl_name + " VALUES ("+question_marks(header)+")", arr)
	return 

def main():
	# I do not find any good online SQL tutorial, so I write one
	# The problem is SQL cannot survive alone, but it is implemented by different programming module
	# For example, Python provides SQLite out of box
	# We can use Excel file to serve as data source
	# Read the first worksheet (CBBC) data
	cbbc_path = os.path.join(os.getcwd(), "matrix.xlsx")

	cbbc_header, cbbc_arr = xlsx_to_arr(cbbc_path)
	print (cbbc_header)

	# Create a database and return a connection and cursor
	conn, cur = db_cur()

	# Create a table, and import CBBC data
	create_tbl(cur, "cbbc", cbbc_header, cbbc_arr)

	print ("Select all stock code from table")
	cur.execute("select StockCode from cbbc")
	for row in cur.fetchall():
		print (row[0])

	print ("But SQLite treats those numbers as double (floating point number), convert it as integer")
	cur.execute("select cast(StockCode as decimal) from cbbc")
	for row in cur.fetchall():
		print (row[0])

	print ("Select underlyinbg stock")
	cur.execute("select cast(underlying as decimal) from cbbc")
	for row in cur.fetchall():
		print (row[0])

	print ("Select distinct underlyinbg stock")
	cur.execute("select distinct cast(underlying as decimal) from cbbc")
	for row in cur.fetchall():
		print (row[0])


	print ("Select stock where underlying is HSI")
	cur.execute("select * from cbbc where underlying = 'HSI' ")
	for row in cur.fetchall():
		print (','.join([str(ele) for ele in row]))
	return

main()