# -*- coding: utf-8 -*-
from financials import Financials
from vintage import Vintage
import copy
import pandas as pd
import numpy as np


class ProductFinancialsWithVintages(Financials):
    def __init__(self, financial_data, first_period, vintages_static_params_list, vintages_dynamic_params, rate, total_book_T0):
        Financials.__init__(self, financial_data, first_period)
        self.financials_history = pd.DataFrame(np.nan,
                                               columns=[],
                                               index=self.financials.index.values.copy())
        self.vintages_num = len(vintages_static_params_list)
        self.rate = rate

        # for initializing past vintages
        self.default_dynamic_params = vintages_dynamic_params
        self.default_vintage_financials_data = copy.deepcopy(vintages_static_params_list[0][2])
        self.duration = int(vintages_dynamic_params.loc['Residual duration'][0])

        self.vintages = self.create_future_vintages_list(vintages_static_params_list, vintages_dynamic_params, rate)

        rest_total_book_T0 = total_book_T0 - self.financials.loc['Total_book']
        self.calculate_first_vintage()
        self.create_past_vintages_list(rest_total_book_T0)
        self.synchronize_vintages_with_actual_period()

    # methods for past and future vintage initialization
    def create_future_vintages_list(self, vintages_static_params_list, vintages_dynamic_params, rate):

        vintages = []
        for vintage_static_params in vintages_static_params_list:
            duration = self.duration
            initial_volume = int(vintage_static_params[1])
            birth_period = int(vintage_static_params[0])
            financilas = vintage_static_params[2]
            new_vintage = Vintage(duration, initial_volume, birth_period, financilas, copy.deepcopy(vintages_dynamic_params), rate)
            vintages.append(new_vintage)
        return vintages

    def create_past_vintages_list(self, total_book):
        past_vintages_num = self.duration

        # assume that all past vimtages have similar initial volumes
        intitial_volume = self.calculate_initial_volume(total_book)

        for period in range(1, self.duration+1):
            duration = self.duration
            initial_volume = intitial_volume
            birth_period = -period
            financilas = self.init_default_vintage_financials_data(copy.deepcopy(self.default_vintage_financials_data), initial_volume)
            new_vintage = Vintage(duration, initial_volume, birth_period, financilas, copy.deepcopy(self.default_dynamic_params), self.rate)
            self.vintages.insert(0, new_vintage)
        self.vintages_num += past_vintages_num

    # calculation methods
    def calculate_financials_for_period(self, period):
        self.calculate_vintages_for_period(period)
        self.aggregate_vintages_for_period(period)

    def aggregate_vintages_for_period(self, period):
        self.clear_financials()
        for vintage in self.vintages:
            if (vintage.birth_period <= period and period <= vintage.birth_period + vintage.duration):
                for item in self.financials.index:
                    self.financials[item] += vintage.financials.get_history_value(item, period)

    def calculate_vintages_for_period(self, period):
        for vintage in self.vintages:
            if(vintage.birth_period < period and period <= vintage.birth_period + vintage.duration):
                vintage.financials.update_actual_period(period)
                vintage.financials.calculate_financials_for_period(period)
                vintage.financials.update_financials_history(period)

    # methods for past vintages
    def calculate_TB_ratio(self, period):
        # all future vintages are similar, so take the first one
        vintage = self.vintages[0]
        if (vintage.financials.financials_history.loc['Total_book']['T'+str(period-1)] != 0):
            value = vintage.financials.financials_history.loc['Total_book']['T'+str(period)] / vintage.financials.financials_history.loc['Total_book']['T'+str(period-1)]
            return value

    def calculate_first_vintage(self):
        vintage = self.vintages[0]
        for i in range(vintage.birth_period+1, self.duration+1, 1):
            vintage.financials.update_actual_period(i)
            vintage.financials.calculate_financials_for_period(i)
            vintage.financials.update_financials_history(i)

    def calculate_initial_volume(self, total_book):
        multipliers_sum = 0
        for period in reversed(range(1, self.duration)):
            multiplier = 1
            for i in reversed(range(1, period+1)):
                value = self.calculate_TB_ratio(i)
                multiplier *= value
            multipliers_sum += multiplier
        initial_volume = total_book / multipliers_sum
        return initial_volume

    def init_default_vintage_financials_data(self, data, initial_volume):
        to_init = ['Initial_volume', 'Total_book', 'PL_new', 'PL']
        to_zero = ['Attrit', 'Def', 'PL_old', 'NPL', 'NPL_old', 'NPL_new', 'Prov_bad', 'Net_income']
        for item in to_init:
            data.loc[item] = initial_volume
        for item in to_zero:
            data.loc[item] = float(0)
        data['Prov_good'] = data['PL'] * self.default_dynamic_params.loc['EL'][0]
        data['Prov'] = data['Prov_bad'] + data['Prov_good']
        return data

    def synchronize_vintages_with_actual_period(self):
        # range(-self.duration, self.financials.current_period, 1) - all actual lifetime of this type of product
        first_period = self.vintages[0].financials.current_period
        last_period = self.current_period+1
        for period in range(first_period, last_period, 1):
            self.update_actual_period(period)
            self.calculate_financials_for_period(period)
            self.update_financials_history(period)
