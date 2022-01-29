# -*- coding: utf-8 -*-
"""
Created on Mon Dec 21 11:52:47 2020
let's try dict data structure
@author: Alexandra
"""
import time
import pandas as pd
param = pd.read_excel('New_INPUT_MVP_20201207.xlsm', sheet_name='Param_Macro_Neutral_Scen')
param = param.set_index('Code')

tic = time.perf_counter()
value_df = param.loc['FX_rate']['2020Q4']
toc = time.perf_counter()
print((toc-tic)/3600)


dict_param = param.to_dict('index')

tic = time.perf_counter()
value_dt = dict_param['FOR_level']['2020Q4']
toc = time.perf_counter()
print((toc-tic)/3600)

