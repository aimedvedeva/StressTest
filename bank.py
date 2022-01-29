# -*- coding: utf-8 -*-
import pandas as pd


class Bank:
    def __init__(self, financials_object, product_objects_list):
        self.financials = financials_object
        self.products = product_objects_list
        self.financials.clear_balancer_values()

    def calculate_total_product_metrics(self):
        total_metrics_index = ['total_loan_balance_net', 'total_loan_interest',
                               'total_deposit_balance_net', 'total_deposit_interest']
        total_metrics = pd.Series([float(0) for i in total_metrics_index], index=total_metrics_index)

        for product in self.products:
            if (product.type == 'Deposit'):
                pass
            elif (product.type == 'Loan'):
                total_metrics['total_loan_balance_net'] += product.financials.get_actual_value('Total_book') - product.financials.get_actual_value('Prov')
                total_metrics['total_loan_interest'] += product.financials.get_actual_value('Net_income')

        return total_metrics

    def forecast_financials(self, periods_num):
        for period in range(self.financials.current_period, periods_num):

            for product in self.products:
                product.financials.update_actual_period(period)
                product.financials.calculate_financials_for_period(period)
                product.financials.update_financials_history(period)

            # start calculate bank's balance sheet from T1
            if (period > 0):
                total_product_metrics = self.calculate_total_product_metrics()
                self.financials.enrich_product_data(total_product_metrics)

                self.financials.update_actual_period(period)
                self.financials.calculate_financials()

                self.financials.balancer()

                self.financials.update_financials_history(period)
                self.financials.clear_balancer_values()

    def get_financials_history(self):
        data = self.financials.get_financials_history()
        return data

    def get_products_history(self):
        products_history_list = []
        for product in self.products:
            data = product.financials.get_financials_history()
            products_history_list.append(data)
        return products_history_list
