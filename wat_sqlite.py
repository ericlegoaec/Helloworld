import sqlite3
import csv
import decimal

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

def adapt_decimal(d):
	return str(d)

def convert_decimal(s):
	return decimal.Decimal(s)

def create_tbl(cur, tbl_name, header, arr, index_arr = []):
	cur.execute("CREATE TABLE " + tbl_name + " (" + header + " );")
	for index in index_arr:
		cur.execute("CREATE INDEX " + tbl_name + "_" + index + " ON " + tbl_name + " (" + index + ");")
	cur.executemany("INSERT INTO " + tbl_name + " VALUES ("+question_marks(header)+")", arr)
	return 

def db_cur(source = ":memory:"):

	conn = sqlite3.connect(source)
	cur = conn.cursor()

	return conn, cur

def import_files(cur):
	cur.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='warrants' ")
	tbl_exists = cur.fetchone() 
	if tbl_exists[0] == 0:
		wrt_header, wrt_arr = csv_to_arr("D:\\wat\\warrants.csv")
		create_tbl(cur, "warrants", wrt_header, wrt_arr, ["ID_BB", "UNDERLYING_ID_BB"])
		print "Imported Warrants"
	
	# cur.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='warrant_updates' ")
	# tbl_exists = cur.fetchone() 
	# if tbl_exists[0] == 0:
	# 	wup_header, wup_arr = csv_to_arr("D:\\wat\\warrant_updates.csv")
	# 	create_tbl(cur, "warrant_updates", wup_header, wup_arr, ["ID_BB"])
	# 	print "Imported Warrant Updates"
	
	cur.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='und_updates' ")
	tbl_exists = cur.fetchone() 
	if tbl_exists[0] == 0:
		und_header, und_arr = csv_to_arr("D:\\wat\\underlying_updates.csv")
		create_tbl(cur, "und_updates", und_header, und_arr, ["ID_BB"])
		print "Imported Underlying"

	return

def main():
	conn, cur = db_cur("D:\\wat\\warrant_uat.db")

	import_files(cur)

	cur.execute("""select * from und_updates limit 1""")

	rows = cur.fetchall()
	for row in rows:
		print row

	conn.close()
	return

main()