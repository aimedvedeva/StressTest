# -*- coding: utf-8 -*-
"""
Some specific functions to parse our formulas from Excel
"""
import pandas as pd
import parse as ps
import numpy as np


# Combine list of strings into a single one
def list_to_string(list):
    tmp = ' '.join(str(element) for element in list)
    return tmp


# Function for splitting formulas into components
def formula_split(s):
    s = s.replace(' ', '')
    s = s.replace('[t-1', '_L')
    s = s.replace('+', '').replace('-', '').replace('*', '').replace('/', '').replace('1', '')
    s = s.replace('(', '').replace(')', '').replace('min', '').replace('max', '')
    # exclude digots and commas from the string, E.G. 0.5
    s = ''.join([i for i in s if not i.isdigit()])
    s = s.replace('.', '')
    split = s.split(']')[:-1]
    split = [x.replace('[t', '') for x in split]
    return split


def create_formualas_for_execution(data_struct, is_for_product):
    # Identify components of all formulas
    data_struct['Components'] = data_struct['Formula'].apply(lambda x: ''
                                                             if (x in ['SUM_h', 'External'])
                                                             else ps.list_to_string(ps.formula_split(x)))
    data_struct['Internal'] = data_struct['Components'].apply(lambda x: ''
                                                              if (x == '')
                                                              else ps.list_to_string(y for y in x.split(' ') if (y in data_struct.index)))

    # Identify coefficients and lagged items in formulas
    data_struct['Coefficients'] = pd.Series(['' for i in data_struct.index], index=data_struct.index, dtype='string')
    data_struct['Lagged_items'] = pd.Series(['' for i in data_struct.index], index=data_struct.index, dtype='string')

    for index, components in enumerate(data_struct['Components']):
        if components == '':
            continue

        internals = data_struct['Internal'][index]

        split_internals = internals.split(' ')
        split_components = components.split(' ')

        difference = ' '.join([i for i in split_components if i not in split_internals])
        split_difference = difference.split(' ')

        lagged_val = ' '.join([i for i in split_difference if '_L' in i])
        split_lagges_val = lagged_val.split(' ')

        coefficients = ' '.join([i for i in split_difference if i not in split_lagges_val])

        lagged_val = lagged_val.replace('_L', '')

        data_struct['Coefficients'].iloc[index] = coefficients
        data_struct['Lagged_items'].iloc[index] = lagged_val

    # Identify components of all aggregated accounts (SUM_h)
    condition = data_struct['Formula'] == 'SUM_h'
    true_object = pd.Series(['' for i in data_struct.index], index=data_struct.index, dtype='string')

    for index, item in enumerate(data_struct['Hierarchy']):
        bool1 = data_struct['Hierarchy'].str.startswith(item)
        dot_count = data_struct['Hierarchy'].str.count('.')
        string_count = item.count('.')
        bool2 = (dot_count == 2 * (string_count + 1))
        bool3 = data_struct['Hierarchy'] != item
        final_list = data_struct.loc[bool1 & bool2 & bool3].index
        true_object[index] = ps.list_to_string(final_list)

    false_object = data_struct['Internal']
    data_struct['Internal'] = np.where(condition, true_object, false_object)

    # Set calculation order
    condition = data_struct['Internal'] == ''
    true_action = 0
    false_action = np.nan
    data_struct['Order'] = np.where(condition, true_action, false_action)

    condition_global = data_struct['Order'].isnull()
    while any(condition_global):
        index_range = data_struct.loc[data_struct['Order'].isnull()].index
        for i in index_range:
            # print(i)
            to_str = str(data_struct.loc[i, 'Internal'])
            split = to_str.split(' ')
            a = data_struct.loc[split, 'Order']
            if not(np.isnan(a).any()):
                data_struct.loc[i, 'Order'] = max(a) + 1
                condition_global = data_struct['Order'].isnull()

    # Transform formulas for use in eval()
    data_struct['Formula_exec'] = ''
    index_range = data_struct.loc[data_struct['Components'].notnull()].index
    for i in index_range:
        current_formula = data_struct.loc[i, 'Formula']

        if current_formula == 'SUM_h' or current_formula == 'External':
            data_struct.loc[i, 'Formula_exec'] = current_formula
            continue

        formula_internals = []
        formula_coeffs = []
        formula_lagged_values = []

        if (data_struct.loc[i, 'Internal'] != ''):
            formula_internals = data_struct.loc[i, 'Internal'].split(' ')
        if (data_struct.loc[i, 'Coefficients'] != ''):
            formula_coeffs = data_struct.loc[i, 'Coefficients'].split(' ')
        if (data_struct.loc[i, 'Lagged_items'] != ''):
            formula_lagged_values = data_struct.loc[i, 'Lagged_items'].split(' ')

        for string in formula_internals:
            current_formula = current_formula.replace(string + "[t]", "self.financials['" + string + "']")

        for string in formula_lagged_values:
            current_formula = current_formula.replace(string + "[t-1]", "self.financials_history.loc['" + string + "']['Tprev_period_num']")

        for string in formula_coeffs:
            if (is_for_product):
                addition = 'pproduct_num_'
                current_formula = current_formula.replace(string + "[t]", "Dynamic_param.loc['" + addition + string + "']['Tperiod_num']")
            else:
                current_formula = current_formula.replace(string + "[t]", "Dynamic_param.loc['" + string + "']['Tperiod_num']")
        data_struct.loc[i, 'Formula_exec'] = current_formula

    # Create version of B_struct for execution in the main code
    condition = data_struct['Formula_exec'] != 'External'
    data_struct_exec = data_struct.loc[condition, ].sort_values('Order')

    return data_struct_exec
