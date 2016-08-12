import win32com.client
import sys
import sqlite3
import decimal

def adapt_decimal(d):
	return str(d)

def convert_decimal(s):
	return decimal.Decimal(s)

def db_cur(source = ":memory:"):
	# Register the adapter
	sqlite3.register_adapter(decimal.Decimal, adapt_decimal)
	# Register the converter
	sqlite3.register_converter("DECTEXT", convert_decimal)
	conn = sqlite3.connect(source, detect_types=sqlite3.PARSE_DECLTYPES)
	#conn.row_factory = sqlite3.Row
	cur = conn.cursor()

	return conn, cur


_pyver = sys.version_info[:2]
print 'python%d%d.dll'%_pyver
ADOConn = win32com.client.Dispatch("ADODB.Connection")
print "Hello World"

db, cur = db_cur()

cur.execute("select substr('8/5/2016',-4)||'-'||substr('00'||trim(substr('8/5/2016',-7,2),'/'),-2,2)||'-'||substr('00'||trim(substr('8/5/2016',1,2),'/'),-2,2) < date('now') ")
x = cur.fetchone()

print x