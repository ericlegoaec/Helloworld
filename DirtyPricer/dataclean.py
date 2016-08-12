# -*- coding: utf-8 -*-
"""
Created on Thu Aug 11 17:59:02 2016

@author: yijaz
"""
import pandas as pd
from dirtypricer import OptionType

def bloomberg_ticker_to_warrant_code(bloomberg_ticker: str) -> str:
    return bloomberg_ticker.split(' ')[0]
    
    
def horizon_id_to_warrant_code(horizon_id: str) -> str:
    return horizon_id.split('@')[0]
    

import warnings
warnings.warn('update data source for referential')
def get_referential(csv_path = r'S:\Trading (EDD)\Warrants\Analysis\Daily\20160810.csv'):
    csv_header_dict = {
        'HT_TICKER': 'warrant_code',
        'WRT_PUT_OR_CALL': 'option_type',
        'WRT_EXPIRE_DT': 'maturity',
        'WRT_EXER_PX': 'strike_price',
        'WRT_SH_PER': 'conversion_ratio'
    }
    ref = (pd
           .read_csv(csv_path)
           [list(csv_header_dict.keys())]
           .rename(columns=csv_header_dict)
           )
    
    ref['warrant_code'] = ref['warrant_code'].apply(bloomberg_ticker_to_warrant_code)
    ref['maturity'] = pd.to_datetime(ref['maturity'])
    ref['option_type'] = ref['option_type'].apply(lambda x: OptionType[x.lower()])
    ref = ref.set_index('warrant_code')
    
    return ref


test_referential = pd.DataFrame([
    [OptionType.call, 100, pd.to_datetime('2020-01-01'), 0.0001],
    [OptionType.call, 105, pd.to_datetime('2020-01-01'), 0.0001],
    [OptionType.call, 110, pd.to_datetime('2020-01-01'), 0.0001],
    [OptionType.put, 95, pd.to_datetime('2020-01-01'), 0.0001],
    [OptionType.put, 90, pd.to_datetime('2020-01-01'), 0.0001],
    [OptionType.put, 85, pd.to_datetime('2020-01-01'), 0.0001]
], columns=['option_type', 'strike_price', 'maturity', 'conversion_ratio'],
index=['call_100', 'call_105', 'call_110', 'put_95', 'put_90', 'put_85'])


def get_horizon_input(horizon_path = 'horizon.csv'):
    
    horizon_header_dict = {
        'Warrant': 'warrant_code',
        'Spot': 'spot_price',
        'Fwd': 'forward_price',
        'Vol': 'sigma',
        'Theo': 'horizon_theo_price'
    }
    
    horizon = (pd
           .read_csv(horizon_path)
           [list(horizon_header_dict.keys())]
           .rename(columns=horizon_header_dict)
           )
    
    horizon['warrant_code'] = horizon['warrant_code'].apply(horizon_id_to_warrant_code)
    horizon = horizon.set_index('warrant_code')
    
    return horizon
    
    
test_horizon_input = pd.DataFrame([
    [100, 101, 0.15, 0],
    [103, 104, 0.10, 0],
    [106, 108, 0.13, 0],
    [100, 101, 0.15, 0],
    [103, 104, 0.10, 0],
    [106, 108, 0.13, 0],
], columns=['spot_price', 'forward_price', 'sigma', 'horizon_theo_price'],
index=['call_100', 'call_105', 'call_110', 'put_95', 'put_90', 'put_85'])


if __name__ == '__main__':
    r = get_referential()
    h = get_horizon_input()