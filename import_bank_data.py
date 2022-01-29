# -*- coding: utf-8 -*-
"""
Some specific functions to parse bank data
"""
import params as gp
import pandas as pd


def initialize_bank_financials(data_struct):
    Bank_data = gp.get_Static_param()

    # Create working array for a single period T0
    num_of_values = len(data_struct.index)
    financials = pd.Series(data=Bank_data['T0'].values[0:num_of_values], index=data_struct.index)

    return financials
