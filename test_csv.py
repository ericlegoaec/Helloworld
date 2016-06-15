import csv
import sqlite3
import decimal

def arr_to_csv(filename, header, arr):
	csv_output = open(filename, 'wb')
	wr = csv.writer(csv_output, quoting=csv.QUOTE_ALL)
	wr.writerow(header.split(','))
	for row in arr:
		wr.writerow(row.split(','))

	return

def question_marks(st):
    question_marks = '?'
    for i in range(0, len(st.split(','))-1):
        question_marks = question_marks + ",?"
    return question_marks

def adapt_decimal(d):
	return str(d)

def convert_decimal(s):
	return decimal.Decimal(s)

def db_cur(source=":memory:"):
	# Register the adapter
	sqlite3.register_adapter(decimal.Decimal, adapt_decimal)

	# Register the converter
	sqlite3.register_converter("DECTEXT", convert_decimal)
	conn = sqlite3.connect(source, detect_types=sqlite3.PARSE_DECLTYPES)
	conn.row_factory = sqlite3.Row
	cur = conn.cursor()

	return conn, cur

def csv_to_arr(csv_file):
	arr = []
	header = ""

	with open(csv_file, 'rU') as f:
		header = f.readline()
		reader = csv.reader(f) 
		arr = list(reader)
	#print header
	return header, arr

def create_tbl(cur, tbl_name, header, arr = [], index_arr = []):
	cur.execute("""select count(*) FROM sqlite_master WHERE type='table' AND name = '%s' """ % (tbl_name))
	tbl_exists = cur.fetchone() 
	if tbl_exists[0] == 0:
		cur.execute("CREATE TABLE " + tbl_name + " (" + header + " );")
		for index in index_arr:
			cur.execute("CREATE INDEX " + tbl_name + "_" + index + " ON " + tbl_name + " (" + index + ");")
		
	if arr != []:
		cur.executemany("INSERT INTO " + tbl_name + " VALUES ("+question_marks(header)+")", arr)
	return 


conn, cur = db_cur()

header, arr = csv_to_arr("Instrument_Pos_20160613.csv")

create_tbl(cur, "test", header, arr)


cur.execute("select * from test")
arr = cur.fetchall()
for row in arr:
	print row[0]