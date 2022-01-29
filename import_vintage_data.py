# -*- coding: utf-8 -*-
import pandas as pd


def parse_vintage_dynamic_param(data):
    data = data.set_index('Name')
    return data


def parse_vintage_static_param(data):
    data = data.set_index('Name')
    vintages_static_param_list = []

    data_list = list(data)
    for column in data_list:
        starting_period = data[column][0]
        initial_volume = data[column][1]
        financials = pd.Series(data[column][2:], index=data.index[2:]).astype('float64')
        vintages_static_param_list.append([starting_period, initial_volume,
                                           financials])
    return vintages_static_param_list
