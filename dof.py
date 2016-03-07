#!/usr/bin/python

import sys

m43 = {length:0.016,pixel:4096}

a7rii = 0.036
pixel = 7360

f = 0.043
s = 3
N = 1.2

c = length/pixel

n_factor = N*c*(s-f)

d_n = s*(f**2)/(n_factor+f**2)
d_f = s*(f**2)/(-n_factor+f**2)

print 'Near field DoF = ' + str(d_n)
print 'Far field DoF = ' + str(d_f)
print 'Total DoF = ' + str(-d_n+d_f)