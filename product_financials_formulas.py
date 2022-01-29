# -*- coding: utf-8 -*-
from financials import Financials
import pandas as pd


class ProductFinancialsWithFormulas(Financials):
    def __init__(self, financial_data, financial_formulas, first_period):
        Financials.__init__(financial_data, first_period)
        self.financials_history = pd.DataFrame(self.financials.values.copy(),
                                               columns=['T'+str(self.current_period)],
                                               index=self.financials.index.values.copy())
        self.formulas = financial_formulas

    def calculate_financials_for_period(self, product_index):
        # Calculate items defined by formulas
        for item in self.formulas.index:
            exec_formula = "self.financials['" + item + "'] = " + self.formulas.loc[item]
            exec_formula = exec_formula.replace('product_num', str(product_index))
            exec_formula = exec_formula.replace('prev_period_num', str(self.current_period_number-1))
            exec_formula = exec_formula.replace('period_num', str(self.current_period_number))
            exec(exec_formula)
