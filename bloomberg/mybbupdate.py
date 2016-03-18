# SimpleRefDataOverrideExample.py

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
,                      dest="port",
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
        print securityData.getElementAsString(SECURITY)
        fieldData = securityData.getElement(FIELD_DATA)
        for field in fieldData.elements():
            if field.isValid():
                print field.name(), "=", field.getValueAsString()
            else:
                print field.name(), " is NULL"

        fieldExceptionArray = securityData.getElement(FIELD_EXCEPTIONS)
        for fieldException in fieldExceptionArray.values():
            errorInfo = fieldException.getElement(ERROR_INFO)
            print errorInfo.getElementAsString("category"), ":", \
                fieldException.getElementAsString(FIELD_ID)

        print


def main():
    global options
    options = parseCmdLine()

    # Fill SessionOptions
    sessionOptions = blpapi.SessionOptions()
    sessionOptions.setServerHost(options.host)
    sessionOptions.setServerPort(options.port)

    print "Connecting to %s:%d" % (options.host, options.port)

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

    # append securities to request
    request.append("securities", "IBM US Equity")
    request.append("securities", "MSFT US Equity")

    # append fields to request
    request.append("fields", "PX_LAST")
    request.append("fields", "DS002")
    request.append("fields", "EQY_WEIGHTED_AVG_PX")

    print "Sending Request:", request
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
    print "SimpleRefDataOverrideExample"
    try:
        main()
    except KeyboardInterrupt:
        print "Ctrl+C pressed. Stopping..."
