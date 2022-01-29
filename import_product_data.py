# -*- coding: utf-8 -*-
"""
Some specific functions to parse product data
"""
import params as gp
import pandas as pd


def parse_rate(product_number):
    Dynamic_param = gp.get_Dynamic_param()
    product_index = product_number + 1
    rate = Dynamic_param.loc['p'+str(product_index)+'_rate'][0]
    return rate


def define_data_shift(product_number):
    Bank_data = gp.get_Static_param()

    product_index = product_number + 1
    data_start_pos = [i for i, s in enumerate(Bank_data.index.values.tolist()) if 'p'+str(product_index) in s][0]

    next_product_index = product_index + 1
    next_chunk_pos = [i for i, s in enumerate(Bank_data.index.values.tolist()) if 'p'+str(next_product_index) in s]

    if(len(next_chunk_pos) != 0):
        data_shift = next_chunk_pos - data_start_pos
    else:
        data_shift = len(Bank_data) - data_start_pos
    return data_shift


def exclude_product_identifier(financials, product_index):
    new_index = []
    for index, item in enumerate(financials):
        new_item = item.replace('p'+str(product_index)+'_', '')
        new_index.append(new_item)
    return new_index


def initialize_product_financials(product_number):
    Bank_data = gp.get_Static_param()

    # Add values from T0
    product_index = product_number + 1
    data_pos = [i for i, s in enumerate(Bank_data.index.values.tolist()) if 'p'+str(product_index) in s][0]

    data_shift = define_data_shift(product_number)

    data = Bank_data.iloc[data_pos:data_pos+data_shift]['T0'].values

    financials_index = Bank_data.index[data_pos:data_pos+data_shift]
    modified_index = exclude_product_identifier(financials_index, product_index)
    financials_index = pd.Index(modified_index)

    financials = pd.Series(data, index=financials_index)

    return financials


def parse_product_list():
    Product_list = []
    Global_param = gp.get_Global_param()
    products_num = int(Global_param.loc[Global_param['id'] == 'num_prod', 'value'].values[0])

    if(products_num == 0):
        return []

    product_list = Global_param.iloc[1:]
    for index, item in enumerate(product_list):
        if (index == len(product_list)):
            break

        if ('type' in product_list.iloc[index]['id']):
            product_code = int(product_list.iloc[index]['value'])

            if (product_code == 0):
                product_type = 'Deposit'
            else:
                product_type = 'Loan'

        elif ('maturity' in product_list.iloc[index]['id']):
            product_maturity = int(product_list.iloc[index]['value'])
            product_data = [product_type, product_maturity]
            Product_list.append(product_data)

    return Product_list
