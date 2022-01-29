# -*- coding: utf-8 -*-
from product_financials_vintages import ProductFinancialsWithVintages


class Product:
    def __init__(self, financials, first_period, prod_type, maturity, rate,
                 vintages_static_params_list, vintages_dynamic_params, total_book_T0):
        self.rate = rate
        self.type = prod_type
        self.maturity = maturity
        self.financials = ProductFinancialsWithVintages(financials, first_period, vintages_static_params_list, vintages_dynamic_params, rate, total_book_T0)

    def get_financials_history(self):
        data = self.financials.get_financials_history()
        return data
