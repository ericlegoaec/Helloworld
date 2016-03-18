#!usr/bin/env python
#coding=utf-8
 
import datetime
import sys
import threading
 
Curtime = datetime.datetime.now()
print '初始时间为：',Curtime
 
Scrtime = Curtime + datetime.timedelta(0,30,0)
 
print '目标时间为:',Scrtime
 
threading._sleep(30)
Dsttime = datetime.datetime.now()
tmp     = Dsttime - Scrtime + Scrtime
print "当前时间为:",tmp
 
if tmp == Dsttime:
        print '计费结束'
else:
        print 'NO'