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
	# Register the adapter
	sqlite3.register_adapter(decimal.Decimal, adapt_decimal)
	# Register the converter
	sqlite3.register_converter("DECTEXT", convert_decimal)
	conn = sqlite3.connect(source, detect_types=sqlite3.PARSE_DECLTYPES)
	#conn.row_factory = sqlite3.Row
	cur = conn.cursor()

	return conn, cur

def arr_to_csv(file_name, header, data_arr):
	f1 = open(file_name, "w")
	if header != "":
		f1.write(header+'\n')

	for data_row in data_arr:
		line = '' 
		for ele in data_row:
			line = line + str(ele) + ',' 

		line = line[:-1] + '\n'
		f1.write(line)    

	f1.close()
	return

def import_files(cur):
	
	cur.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='warrant_updates' ")
	tbl_exists = cur.fetchone() 
	if tbl_exists[0] == 0:
		wup_header, wup_arr = csv_to_arr("../test_wat/warrant_updates.csv")
		create_tbl(cur, "warrant_updates", wup_header, wup_arr, ["ID_BB", "TRADE_DATE"])
		print "Imported Warrant Updates"
	
	cur.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='underlying_updates' ")
	tbl_exists = cur.fetchone() 
	if tbl_exists[0] == 0:
		und_header, und_arr = csv_to_arr("../test_wat/underlying_updates.csv")
		create_tbl(cur, "underlying_updates", und_header, und_arr, ["ID_BB", "TRADE_DATE"])
		print "Imported Underlying"

	cur.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='warrants' ")
	tbl_exists = cur.fetchone() 
	if tbl_exists[0] == 0:
		wrt_header, wrt_arr = csv_to_arr("../test_wat/warrants.csv")
		create_tbl(cur, "warrants", wrt_header, wrt_arr, ["ID_BB", "UNDERLYING_ID_BB"])
		print "Imported Warrants"
	return

def main():
	# "ID_BB","CLOSE","CHG_PCT","CHG_NET","TRADE_DATE","LAST_UPDATED"
	# "ID_BB","LAST_PRICE","PX_CHG","PCT_CHG","VOLUME","TURNOVER","ISSUE_AMOUNT","BOARD_LOT","STRIKE","BARRIER","SHR_WRNT","DELTA","GAMMA","VEGA","THETA","IV","OI","AVG_BOUGHT","AVG_SOLD","QTY_BOUGHT","QTY_SOLD","BARRIER_STATUS","TRADE_DATE","LAST_UPDATED","NUM_TRADES"
	# "ID_BB","TICKER_BB","CODE","UNDERLYING_ID_BB","UNDERLYING_TICKER","ISSUER","LIQUIDITY_PROVIDER","CALL_PUT","ISSUE_DATE","LISTING_DATE","EXPIRY_DATE","LAST_TRADE_DATE","BARRIER_HIT_DATE","LAST_UPDATED","RESIDUAL"
	uat_header = "ID_BB,LAST_PRICE,PX_CHG,PCT_CHG,VOLUME,TURNOVER,ISSUE_AMOUNT,BOARD_LOT,STRIKE,BARRIER,SHR_WRNT,DELTA,GAMMA,VEGA,THETA,IV,OI,AVG_BOUGHT,AVG_SOLD,QTY_BOUGHT,QTY_SOLD,BARRIER_STATUS,TRADE_DATE,TICKER_BB,CODE,UNDERLYING_ID_BB,UNDERLYING_TICKER,ISSUER,LIQUIDITY_PROVIDER,CALL_PUT,ISSUE_DATE,LISTING_DATE,EXPIRY_DATE,LAST_TRADE_DATE,BARRIER_HIT_DATE,CLOSE,CHG_PCT,CHG_NET"
	
	conn, cur = db_cur("../test_wat/warrant_uat.db")

	import_files(cur)

	cur.execute("select * from warrant_updates")

	# cur.execute("""select warrant_updates."ID_BB","LAST_PRICE","PX_CHG","PCT_CHG","VOLUME","TURNOVER","ISSUE_AMOUNT","BOARD_LOT",
	# 	"STRIKE","BARRIER","SHR_WRNT","DELTA","GAMMA","VEGA","THETA","IV","OI","AVG_BOUGHT","AVG_SOLD","QTY_BOUGHT","QTY_SOLD","BARRIER_STATUS",warrant_updates."TRADE_DATE",
	# 	"TICKER_BB","CODE","UNDERLYING_ID_BB","UNDERLYING_TICKER","ISSUER","LIQUIDITY_PROVIDER","CALL_PUT","ISSUE_DATE","LISTING_DATE","EXPIRY_DATE","LAST_TRADE_DATE","BARRIER_HIT_DATE",
	# 	"CLOSE","CHG_PCT","CHG_NET"
	# 	from warrants 
	# 	join warrant_updates on warrants.ID_BB = warrant_updates.ID_BB  
	# 	join underlying_updates on underlying_updates.ID_BB = warrants.UNDERLYING_ID_BB and warrant_updates.TRADE_DATE = underlying_updates.TRADE_DATE
	# 	""")

	uat_arr = cur.fetchall()
	print len(uat_arr)

	# arr_to_csv("../test_wat/warrant_uat.csv", uat_header, uat_arr)

	conn.commit()
	conn.close()
	return

main()