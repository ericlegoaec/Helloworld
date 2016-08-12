# -*- coding: utf-8 -*-
"""
Created on Thu Aug 11 10:58:51 2016

@author: yijaz
"""

from enum import Enum
from numpy import log, sqrt, power, array
from scipy.stats import norm


class OptionType(Enum):
    put = -1
    call = 1
    

def dirty_pricer(*, strike_price, option_type, conversion_ratio=1, forward_price, sigma, remaining_maturity):
    
    try:
        option_type_value = array([ot.value for ot in option_type])
    except TypeError as err:
        option_type_value = option_type.value
    
    d1 = (log(forward_price) - log(strike_price) + 0.5 * (power(sigma, 2) * remaining_maturity)) / (sigma * sqrt(remaining_maturity))
    d2 = d1 - (sigma * sqrt(remaining_maturity))
    option_price = option_type_value * (forward_price * norm.cdf(option_type_value * d1) - strike_price * norm.cdf(option_type_value * d2))

    return option_price * conversion_ratio
    
    
