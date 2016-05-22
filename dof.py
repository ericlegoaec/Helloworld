#!/usr/bin/python

import sys

length = 0.036
pixel = 7360

f = 0.090
s = 3
N = 2.8

c = length/pixel

n_factor = N*c*(s-f)

d_n = s*(f**2)/(n_factor+f**2)
d_f = s*(f**2)/(-n_factor+f**2)

print 'Near field DoF = ' + str(d_n)
print 'Far field DoF = ' + str(d_f)
print 'Total DoF = ' + str(-d_n+d_f)