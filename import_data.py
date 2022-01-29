# -*- coding: utf-8 -*-
"""
Just some functions for data importing
"""
import pandas as pd
import params as gp
import product as pr
import parse as ps
import import_product_data as im_pr
import import_bank_data as im_bk
import import_vintage_data as im_vt
import copy


def import_data(filename):

    gp.initialize_Global_param(pd.read_excel(filename, sheet_name='Param_Global'))
    gp.initialize_Dynamic_param(pd.read_excel(filename, sheet_name='Param_D'))
    gp.initialize_Static_param(pd.read_excel(filename, sheet_name='Bank_Financials_T0'))
    gp.initialize_Static_param(pd.read_excel(filename, sheet_name='Param_Structural'))
    gp.initialize_Static_param(pd.read_excel(filename, sheet_name='Param_Bank'))
    gp.initialize_Static_param(pd.read_excel(filename, sheet_name='Param_Bank'))
    
    B_struct = pd.read_excel(filename, sheet_name='B_struct')
    B_struct = B_struct.set_index('Name')
    B_struct_exec = ps.create_formualas_for_execution(B_struct, is_for_product=False)
    financials_for_bank = im_bk.initialize_bank_financials(B_struct)

    Products = im_pr.parse_product_list()
    Product_object_list = []
    for index, product_type in enumerate(Products):
        vintages_static_params_list = im_vt.parse_vintage_static_param(
                                 pd.read_excel(filename, sheet_name='Param_F_vintages_p' +
                                               str(index+1)))
        vintages_dynamic_params = im_vt.parse_vintage_dynamic_param(
                                  pd.read_excel(filename, sheet_name='Param_D_vintages_p' +
                                                str(index+1)))
        product_type = Products[index][0]
        product_maturity = Products[index][1]
        product_rate = im_pr.parse_rate(index)

        financials = im_pr.initialize_product_financials(index)
        start_period = 0

        total_book_T0 = financials_for_bank.loc['Loans']
        product_object = pr.Product(copy.deepcopy(financials), start_period, product_type, product_maturity, product_rate,
                                    copy.deepcopy(vintages_static_params_list), vintages_dynamic_params, total_book_T0)

        Product_object_list.append(product_object)

        # clone product
        test_prod_num = 19
        for item in range(test_prod_num):
            new_prod = pr.Product(copy.deepcopy(financials), start_period, product_type, product_maturity, product_rate,
                                  copy.deepcopy(vintages_static_params_list), vintages_dynamic_params, total_book_T0)
            Product_object_list.append(new_prod)

    return B_struct_exec, financials_for_bank, Product_object_list
