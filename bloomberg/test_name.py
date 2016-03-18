import MySQLdb, datetime
# import blpapi
from optparse import OptionParser

if __name__ == "__main__":
    # parseCmdLine()

    result = []
    # 1. Open Stock CSV
    f = open('security master table.csv')
    for line in f:
        result.append(line)
    f.close()

    # print result

    # 2. Open MySQL Connection
    conn = MySQLdb.connect(host='127.0.0.1',user='root',passwd='',port=3306)
    cur = conn.cursor()
    conn.select_db('pfs')

    bbcodes = list()
    for line in result:
        tt = line.split(',')
        bbcode = tt[9]
        # print tt
        # print bbcode
        if bbcode == 'BBCode':
            continue

        if tt[1][0] == '"':
            cpname = tt[1]+','+tt[2]
            cpname = cpname[1:-1]
            # if tt[-1][-1] == '"':
            #     cur.execute('insert into pfs_relatename(stock_id, companyname, sector, industry) values(%s,%s,%s,%s)', 
            #         (bbcode, cpname, tt[17], tt[19].strip()) )
            # else:
            cur.execute('insert into pfs_relatename(stock_id, companyname, sector, industry) values(%s,%s,%s,%s)', 
                (bbcode, cpname, tt[17], tt[19].strip()) )
        else:
            cur.execute('insert into pfs_relatename(stock_id, companyname, sector, industry) values(%s,%s,%s,%s)', 
                (bbcode, tt[1], tt[16], tt[18].strip()) )
        
        #datetime.date.today().strftime("%Y-%m-%d %H:%M:%S")) )
        # cur.execute('insert into test values(%s,%s)', ('1', bbcode))

    conn.commit()
    cur.close()
    conn.close()
