import win32com.client
import sys

_pyver = sys.version_info[:2]
print 'python%d%d.dll'%_pyver
ADOConn = win32com.client.Dispatch("ADODB.Connection")
print "Hello World"