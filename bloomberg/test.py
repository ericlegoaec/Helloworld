import MySQLdb, datetime
import blpapi
from optparse import OptionParser

SECURITY_DATA = blpapi.Name("securityData")
SECURITY = blpapi.Name("security")
FIELD_DATA = blpapi.Name("fieldData")
FIELD_EXCEPTIONS = blpapi.Name("fieldExceptions")
FIELD_ID = blpapi.Name("fieldId")
ERROR_INFO = blpapi.Name("errorInfo")

def parseCmdLine():
    parser = OptionParser(description="Retrieve reference data.")
    parser.add_option("-a",
                      "--ip",
                      dest="host",
                      help="server name or IP (default: %default)",
                      metavar="ipAddress",
                      default="localhost")
    parser.add_option("-p"
,                     dest="port",
                      type="int",
                      help="server port (default: %default)",
                      metavar="tcpPort",
                      default=8194)

    (options, args) = parser.parse_args()
    return options

def processMessage(msg):
    if not msg.hasElement(SECURITY_DATA):
        print "Unexpected message:"
        print msg
        return

    securityDataArray = msg.getElement(SECURITY_DATA)
    for securityData in securityDataArray.values():
        security_name = securityData.getElementAsString(SECURITY)
        print security_name
        fieldData = securityData.getElement(FIELD_DATA)
        for field in fieldData.elements():
            if field.isValid():
                if field.name() != "LAST_PRICE":
                    continue
                print field.name(), "=", field.getValueAsString()

                count = cur.execute('select * from pfs_price where date=%s and stock_id=%s', 
                    (datetime.date.today(), security_name) )
                # print 'there has %s rows record' % count

                if count != 0:
                    cur.execute('insert into pfs_price(stock_id, price, date) values(%s,%s,%s)', 
                        (bbcode, field.getValueAsString(), datetime.date.today()) )
                else:
                    result=cur.fetchone()
                    cur.execute('update pfs_price set price="%s" where id=%s', result[0])

            else:
                print field.name(), " is NULL"

        fieldExceptionArray = securityData.getElement(FIELD_EXCEPTIONS)
        for fieldException in fieldExceptionArray.values():
            errorInfo = fieldException.getElement(ERROR_INFO)
            print errorInfo.getElementAsString("category"), ":", \
                fieldException.getElementAsString(FIELD_ID)

        print

def Query(self, bbs):
    global options
    options = parseCmdLine()

    # Fill SessionOptions
    sessionOptions = blpapi.SessionOptions()
    sessionOptions.setServerHost(options.host)
    sessionOptions.setServerPort(options.port)

    print "1. Connecting to %s:%d" % (options.host, options.port)

    # Create a Session
    session = blpapi.Session(sessionOptions)

    # Start a Session
    if not session.start():
        print "Failed to start session."
        return

    if not session.openService("//blp/refdata"):
        print "Failed to open //blp/refdata"
        return

    refDataService = session.getService("//blp/refdata")
    request = refDataService.createRequest("ReferenceDataRequest")

    # (1) append securities to request
    # request.append("securities", "IBM US Equity")
    # request.append("securities", "MSFT US Equity")
    for bbcode in bbs:
        request.append("securities", bbcode)

    # (2) append fields to request
    # request.append("fields", "PX_LAST")
    # request.append("fields", "DS002")
    # request.append("fields", "EQY_WEIGHTED_AVG_PX")
    request.append("fields", "LAST_PRICE")

    # (3) add overrides
    # overrides = request.getElement("overrides")
    # override1 = overrides.appendElement()
    # override1.setElement("fieldId", "VWAP_START_TIME")
    # override1.setElement("value", "9:30")
    # override2 = overrides.appendElement()
    # override2.setElement("fieldId", "VWAP_END_TIME")
    # override2.setElement("value", "11:30")

    print "2. Sending Request:", request
    cid = session.sendRequest(request)

    try:
        # Process received events
        while(True):
            # We provide timeout to give the chance to Ctrl+C handling:
            ev = session.nextEvent(500)
            for msg in ev:
                if cid in msg.correlationIds():
                    processMessage(msg)
            # Response completly received, so we could exit
            if ev.eventType() == blpapi.Event.RESPONSE:
                break
    finally:
        # Stop the session
        session.stop()

if __name__ == "__main__":
    parseCmdLine()

    result = []
    # 1. Open Stock CSV
    f = open('Stock Information.csv')
    for line in f:
        result.append(line)
    f.close()

    bbcodes = list()
    for line in result[0].split('\r'):
        bbcode = line.split(',')[1]
        if bbcode == 'bbcode':
            continue
        # cur.execute('insert into pfs_price(stock_id, price, date) values(%s,%s,%s)', 
        #     (bbcode, str(8.8), datetime.date.today()) )
        bbcodes.append(bbcode)

        #datetime.date.today().strftime("%Y-%m-%d %H:%M:%S")) )
        # cur.execute('insert into test values(%s,%s)', ('1', bbcode))

    # 2. Open MySQL Connection
    conn = MySQLdb.connect(host='localhost',user='root',passwd='123456',port=3306)
    global cur = conn.cursor()
    conn.select_db('pfs')

    Query(bbcodes)

    conn.commit()
    cur.close()
    conn.close()

