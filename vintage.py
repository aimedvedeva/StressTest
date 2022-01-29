# -*- coding: utf-8 -*-
from vintage_financials import VintageFinancials


class Vintage:
    def __init__(self, duration, initial_volume, birth_period, financials, dynamic_param, rate):
        self.duration = duration
        self.initial_volume = initial_volume
        self.birth_period = birth_period

        adjusted_dynamic_param = rename_dynamic_param_columns(dynamic_param, birth_period)
        self.financials = VintageFinancials(financials, birth_period, adjusted_dynamic_param, rate)


def rename_dynamic_param_columns(dynamic_param, birth_period):
    dynamic_param.columns = ['T'+str(birth_period),
                             'T'+str(birth_period+1),
                             'T'+str(birth_period+2),
                             'T'+str(birth_period+3)]
    ['T'+str(-1+i) for i in range(0, 3)]
    return dynamic_param
