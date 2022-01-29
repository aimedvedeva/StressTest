class Financials:
    def __init__(self, financial_data, first_period):
        self.current_period = first_period
        self.financials = financial_data

    def get_financials_history(self):
        return self.financials_history

    def update_actual_period(self, period):
        self.current_period = period

    def update_financials_history(self, period):
        self.financials_history['T' + str(period)] = self.financials.values.copy()

    def get_history_value(self, name, period):
        value = self.financials_history.loc[str(name)]['T'+str(period)]
        return value

    def get_actual_value(self, name):
        value = self.financials.loc[str(name)]
        return value

    def clear_actual_value(self, name):
        self.financials.loc[str(name)] = 0

    def clear_financials(self):
        index_array = self.financials.index
        for item in index_array:
            self.clear_actual_value(item)
