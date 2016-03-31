print "executing"
for x in range(1,100000000):
	x_str = "%0*d"%(9,x)
	a = int(x_str[0])
	b = int(x_str[1])
	c = int(x_str[2])
	d = int(x_str[3])
	e = int(x_str[4])
	f = int(x_str[5])
	g = int(x_str[6])
	h = int(x_str[7])
	p = int(x_str[8])

	if (a*10+b-c*10-d == e*10+f) and (a*10+b-c*10-d+g*10+h == p*111) and (len(x_str) == len(set([a,b,c,d,e,f,g,h,p]))):
		print """%s %s %s %s %s %s %s %s %s""" %(a,b,c,d,e,f,g,h,p)
print "finished"