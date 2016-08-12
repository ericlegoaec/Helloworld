# -*- coding: utf-8 -*-
"""
Created on Thu Aug 11 15:50:47 2016

@author: yijaz
"""

from collections import namedtuple
import pandas as pd
from math import floor, ceil

tick = pd.read_csv('tick.csv')

def get_tick_size(price):
    down_index = tick[tick['upper_bound'] >= price].first_valid_index()
    up_index = tick[tick['upper_bound'] > price].first_valid_index()
    down_tick = tick.ix[down_index, 'tick_size']
    up_tick = tick.ix[up_index, 'tick_size']
    ticks = namedtuple('ticks', ('down', 'up'))
    return ticks(down_tick, up_tick)


def get_up_tick(price):
    return price + get_tick_size(price).up
    

def get_down_tick(price):
    return price - get_tick_size(price).down
    
    
def snap_to_closest_tick(price):
    tick_size = get_tick_size(price)
    candidates = [
        ceil(price / tick_size.up) * tick_size.up,
        floor(price / tick_size.down) * tick_size.down]
    
    d = [abs(c-price) for c in candidates]
    
    if d[0] <= d[1]:
        return candidates[0]
    else:
        return candidates[1]
    
    

if __name__ == '__main__':
    import unittest
    unittest.main()    
    