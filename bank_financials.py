# -*- coding: utf-8 -*-
from financials import Financials
import params as pr
import pandas as pd


class BankFinancials(Financials):
    def __init__(self, financial_data, financial_formulas, first_period):
        Financials.__init__(self, financial_data, first_period)
        self.financials_history = pd.DataFrame(self.financials.values.copy(),
                                               columns=['T'+str(self.current_period)],
                                               index=self.financials.index.values.copy())
        self.formulas = financial_formulas

    def calculate_financials(self):
        Dynamic_param = pr.get_Dynamic_param()

        # Calculate items defined by formulas
        for item in self.formulas.index:
            if self.formulas.loc[item, 'Formula_exec'] == 'SUM_h':
                formula_SUM = self.formulas.loc[item, 'Internal'].split(' ')
                self.financials[item] = self.financials[formula_SUM].sum()
            else:
                exec_formula = "self.financials['" + item + "'] = " + self.formulas.loc[item, 'Formula_exec']
                exec_formula = exec_formula.replace('prev_period_num', str(self.current_period-1))
                exec_formula = exec_formula.replace('period_num', str(self.current_period))
                exec(exec_formula)

    def enrich_product_data(self, total_product_metrics):
        self.financials['Deposit_balance_net'] = total_product_metrics['total_deposit_balance_net']
        self.financials['Deposit_interest'] = total_product_metrics['total_deposit_interest']
        self.financials['Loan_balance_net'] = total_product_metrics['total_loan_balance_net']
        self.financials['Loan_interest'] = total_product_metrics['total_loan_interest']

    def clear_balancer_values(self):
        self.financials['CBR_deposit_bal'] = 0
        self.financials['Cash_bal'] = 0
        self.financials['Bank_borrow_bal'] = 0

    def balancer(self):
        prev_Cash_main = self.financials_history['T' + str(self.current_period - 1)]['Cash_main']
        prev_CBR_deposit_main = self.financials_history['T' + str(self.current_period - 1)]['CBR_deposit_main']
        prev_Liq_assets = self.financials_history['T' + str(self.current_period - 1)]['Liq_assets']

        if (prev_Cash_main == 0):
            prev_Cash_main = self.financials_history['T' + str(self.current_period - 1)]['Cash']
        if (prev_CBR_deposit_main == 0):
            prev_CBR_deposit_main = self.financials_history['T' + str(self.current_period - 1)]['CBR_deposit']

        while (abs((self.financials['Liab_total'] + self.financials['Capital']) - self.financials['Assets_total']) > 0.1):

            balance_delta = (self.financials['Liab_total'] + self.financials['Capital']) - self.financials['Assets_total']

            if ((self.financials['Liab_total'] + self.financials['Capital']) > self.financials['Assets_total']):

                if (prev_Liq_assets == 0):
                    shareCashMain = 0.6
                    shareCBRDepositMain = 1 - shareCashMain
                else:
                    shareCashMain = prev_Cash_main / prev_Liq_assets
                    shareCBRDepositMain = prev_CBR_deposit_main / prev_Liq_assets

                newCashBal = balance_delta * shareCashMain
                newCBRDepositMain = balance_delta * shareCBRDepositMain

                self.financials['Cash_bal'] += newCashBal
                self.financials['CBR_deposit_bal'] += newCBRDepositMain

            elif ((self.financials['Liab_total'] + self.financials['Capital']) < self.financials['Assets_total']):
                newBankBorrowBal = abs(balance_delta)
                self.financials['Bank_borrow_bal'] += newBankBorrowBal

            self.calculate_financials()
