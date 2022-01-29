# -*- coding: utf-8 -*-
from financials import Financials
import pandas as pd


class VintageFinancials(Financials):
    def __init__(self, financial_data, birth_period, dynamic_params, rate):
        Financials.__init__(self, financial_data, birth_period)
        self.financials_history = pd.DataFrame(self.financials.values.copy(),
                                               columns=['T'+str(self.current_period)],
                                               index=self.financials.index.values.copy())
        self.rate = rate
        self.dynamic_params = dynamic_params
        self.birth_period = birth_period

    def calculate_financials_for_period(self, period):
        prev_PL = self.get_history_value('PL', period-1)
        prev_NPL = self.get_history_value('NPL', period-1)

        self.financials['Def'] = prev_PL * self.dynamic_params.loc['PD']['T'+str(period-1)]
        self.financials['Attrit'] = (prev_PL - self.get_actual_value('Def')) / self.dynamic_params.loc['Residual duration']['T'+str(period-1)]
        self.financials['PL_old'] = prev_PL - self.get_actual_value('Def') - self.get_actual_value('Attrit')
        self.financials['PL_new'] = 0
        self.financials['PL'] = self.get_actual_value('PL_new') + self.get_actual_value('PL_old')
        self.financials['NPL_old'] = prev_NPL * (1 - 1 / self.dynamic_params.loc['Residual duration']['T'+str(period-1)])
        self.financials['NPL_new'] = prev_PL * self.dynamic_params.loc['PD']['T'+str(period-1)]
        self.financials['NPL'] = self.get_actual_value('NPL_new') + self.get_actual_value('NPL_old')
        self.financials['Total_book'] = self.get_actual_value('NPL') + self.get_actual_value('PL')
        self.financials['Prov_good'] = self.get_actual_value('PL') * self.dynamic_params.loc['EL']['T'+str(period)]
        self.financials['Prov_bad'] = self.get_actual_value('NPL') * self.dynamic_params.loc['LGD']['T'+str(period)]
        self.financials['Prov'] = self.get_actual_value('Prov_bad') + self.get_actual_value('Prov_good')

        if (period == self.birth_period):
            self.financials['Net_income'] = 0
        else:
            self.financials['Net_income'] = (self.get_actual_value('PL') + prev_PL) * self.rate * 0.5
