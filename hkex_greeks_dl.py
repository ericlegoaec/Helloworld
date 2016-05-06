import requests
import re
import datetime
import os
import zipfile
import sqlite3
import decimal
import csv
import win32com.client as win32

hkex = "https://www.hkex.com.hk/eng/market/rm/rm_dcrm/riskdata/greeks/RP009_yyMMDD.zip"
greek_path = "D:/greeks/"
horizon_path = "D:/DailyTradeExport/"

def adapt_decimal(d):
    return str(d)

def convert_decimal(s):
    return decimal.Decimal(s)

def question_marks(st):
    question_marks = '?'
    for i in range(0, len(st.split(','))-1):
        question_marks = question_marks + ",?"
    return question_marks

def dec(s):
    if isinstance(s, basestring):
        s = str(s).replace("#","")
    if s == "" or str(float(s)) == "nan":
        return 0
    try:
        return decimal.Decimal(str(s))
    except:
        return 0

    return s

def csv_to_arr(csv_file, start=1, has_header=True):
    arr = []
    with open(csv_file, 'rU') as f:
        reader = csv.reader(f)
        arr = list(reader)

    if isinstance(arr, list) :
        header = ""
        if has_header:
            header = ','.join(arr[0])
            arr = arr[start:]
            return header, arr
        else:
            return arr[start:]

    return

def export_to_file(file_name, header, data_arr):
    f1 = open(file_name, "w")
    f1.write(header+'\n')

    for data_row in data_arr:
        line = '' 
        for ele in data_row:
            line = line + str(ele) + ',' 

        line = line[:-1] + '\n'
        f1.write(line)    
    
    f1.close()
    return

def arr_to_xlsx(filename, header, arr):
    xl = win32.gencache.EnsureDispatch('Excel.Application')
    wb = xl.Workbooks.Add()
    ws = wb.Worksheets(1)

    for i, cell in enumerate(header.split(',')):
        ws.Cells(1,i+1).Value = cell

    for i, row in enumerate(arr):
        for j, cell in enumerate(row):
            if str(cell)[0] == '=':
                ws.Cells(i+2,j+1).Formula = cell
            else:
                ws.Cells(i+2,j+1).Value = cell
    
    ws.Range("C:E").NumberFormat = "#,##0"
    ws.Columns.AutoFit()

    ws.Range("$A$1:$E$2000").FormatConditions.Add(win32.constants.xlExpression, "", '=$E1<>$D1') 
    ws.Range("$A$1:$E$2000").FormatConditions(1).Interior.ColorIndex = 6
    ws.Range("$A$1:$E$2000").FormatConditions(1).StopIfTrue = False

    ws.Columns.AutoFit()

    xl.DisplayAlerts = False
    wb.SaveAs(filename)
    xl.DisplayAlerts = True
    wb.Close(True)

    return

def db_cur():
    # Register the adapter
    sqlite3.register_adapter(decimal.Decimal, adapt_decimal)
    # Register the converter
    sqlite3.register_converter("DECTEXT", convert_decimal)
    conn = sqlite3.connect(":memory:", detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    return conn, cur

def month_code_mapping(ins_type, month_code):
    offset = {'F':69, 'C':64, 'P':76}
    if ins_type == 'F':
        ins_type_code = 'F'
    else:
        ins_type_code = 'C' if month_code[0] < 'M' else 'P'

    month = "%0*d" % (2, ord(month_code[0]) - offset[ins_type_code])

    return ins_type_code + "1" + month_code[1] + month

def prod_lookup(ats_code):
    st = ats_code.split('@')[0] if '@' in ats_code else ats_code

    ins_type = 'O'
    ins_code = st[:3]
    month_code = st[-2:]
    strike = st[3:-2]
    o_col = month_code_mapping(ins_type, month_code)
    
    return ins_code, strike, o_col[0], o_col[1:]

def http_get(url, directory):
    month = "1604"

    for i in range(1,30):
        dt = month + str(i).rjust(2, '0') 
        if datetime.datetime.strptime(dt, "%y%m%d").date().weekday() < 5:
            target = url.replace("yyMMDD", dt)
            local_filename = directory + target.split('/')[-1]

            if not os.path.exists(directory):
                os.makedirs(directory)

            req = requests.get(target, stream=True)
            with open(local_filename, 'wb') as f:
                for chunk in req.iter_content(chunk_size=1024): 
                    if chunk: # filter out keep-alive new chunks
                        f.write(chunk)
            f.close()

            if zipfile.is_zipfile(local_filename):
                z = zipfile.ZipFile(local_filename)
                outfile = directory + "GREK020_O_yyMMDD.CSV".replace("yyMMDD", dt)
                z.extract("GREK020_O.CSV", directory)
                z.close()
                os.rename(directory + "GREK020_O.CSV", outfile)

            os.remove(local_filename)
    return

def greek_to_db(cur, path):
    grk_header = "trade_date,trade_time,cp,ins,exp,str_price,trading_unit,delta,gamma,vega,theta,rho"

    cur.execute("CREATE TABLE grk (" + grk_header + ");")

    for f in os.listdir(path):
        grk_arr = csv_to_arr(os.path.join(path, f), 1, False) 
        cur.executemany("INSERT INTO grk VALUES ("+question_marks(grk_header)+")", grk_arr)

    cur.execute("delete from grk where trade_date = 'ZZZZZZZZ'")
    cur.execute("update grk set str_price = cast(str_price as float) / 100")

    return

def horizon_to_db(cur, path):
    horizon_file_tmp = "HORIZON_derivatives_execs_201604DD1805.csv"

    pos_header = "pos_date,prod,und,call_put,strike_price,expiry,qty,greek_delta"

    for i in range(1, 30):
        hor_file = os.path.join(path + horizon_file_tmp.replace("DD", str(i).rjust(2, '0')))
        if os.path.isfile(hor_file) and os.stat(hor_file).st_size > 0:
            hor_header, hor_arr = csv_to_arr(hor_file)
            if i == 1:
                cur.execute("CREATE TABLE hor (" + hor_header + ");")

            cur.executemany("INSERT INTO hor VALUES ("+question_marks(hor_header)+")", hor_arr)

    cur.execute("update hor set TIMESTAMP = replace(substr(TIMESTAMP,1,10),'-','')")
    cur.execute("update hor set ULID = substr(ULID,1,length(ULID)-5)")
    # GROUP BY PER DAY POSITION
    cur.execute("CREATE TABLE pos (" + pos_header + ");")
    cur.execute("""INSERT INTO pos (pos_date,prod,qty,greek_delta)
        select dt, prod_id, sum(qty), avg(greek_delta) from (select TIMESTAMP as dt,
        PRODUCTID as prod_id
        ,QUANTITY*(case when WAY = 'B' then 1 else -1 end) as qty
        ,delta as greek_delta
        from hor where length(PRODUCTID) > 10 and substr(PRODUCTID,1,3) <> 'HSI' and substr(PRODUCTID,1,3) <> 'HHI' 
        and substr(PRODUCTID,1,3) <> 'MHI' and substr(PRODUCTID,1,3)  <> 'OTC') tmp group by dt, prod_id""")

    cur.execute("select rowid, prod from pos")
    for row in cur.fetchall():
        und,strike_price,cp,expiry = prod_lookup(row["prod"])
        cur.execute("""update pos set und = '%s', strike_price = %s, call_put = '%s', expiry = '%s' where rowid = %s """ % (und,strike_price,cp,expiry,row["rowid"]))

    cur.execute("select * from pos")
    for row in cur.fetchall():
        print row

    return

def find_diff(cur):
    # print "XXX"
    # cur.execute("select * from grk where trade_date = '20160413' and ins = 'XCC' and str_price = 4.70 and substr(grk.exp,3,4) = '1604' ")
    # for row in cur.fetchall():
    #     print row
    # print "XXX"

    cur.execute("""select trade_date,ins,call_put,strike_price,expiry,qty,greek_delta,delta from pos join grk on pos.und = grk.ins 
        and pos.strike_price = grk.str_price
        and pos.call_put = grk.cp
        and pos.expiry = substr(grk.exp,3,4)
        and pos.pos_date = grk.trade_date """)

    rows = cur.fetchall()
    # for row in rows:
    #     print row 
    export_to_file("D:/diff.csv", "trade_date,ins,call_put,strike_price,expiry,qty,horizon_delta,hkex_delta",rows)

    return

conn, cur = db_cur()

# http_get(hkex, greekpath)
# greek_to_db(cur, greek_path)
# horizon_to_db(cur, horizon_path)
# find_diff(cur)
cur.execute("select case when 'P' < 'M' then 'C' else 'P' end")
print cur.fetchone()[0]