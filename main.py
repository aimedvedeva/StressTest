# -*- coding: utf-8 -*-
import import_data as imdata
from bank import Bank
from bank_financials import BankFinancials
import export_data as exdata
import time



def main():

    # Import data
    filename = r'New_INPUT_MVP_20201207.xlsm'
    parsed_data = imdata.import_data(filename)

    # Create and initialize objects
    financial_formulas = parsed_data[0]
    financial_data = parsed_data[1]
    first_period = 0
    financials = BankFinancials(financial_data, financial_formulas, first_period)

    products = parsed_data[2]
    bank = Bank(financials, products)

    # Forecast financials
    # (0,1,2,3,4,5,6)
    tic = time.perf_counter()
    periods_num = 7
    bank.forecast_financials(periods_num)
    toc = time.perf_counter()
    print((toc-tic)/3600)
    # Obtain results
    financials_history = bank.get_financials_history()
    products_history = bank.get_products_history()

    # Print bank's financials
    filename_output = r'Output.xlsx'
    exdata.delete_file(filename_output)
    exdata.create_file(filename_output)

    # Print products' financials
    exdata.export_data(financials_history, filename_output, 'B_module_output')
    for index, item in enumerate(products_history):
        exdata.export_data(item, filename_output, 'p'+str(index+1)+'_output')
    exdata.delete_sheet(filename_output, 'Sheet1')
    exdata.delete_sheet(filename_output, 'Лист1')

    exdata.adjust_columns(r'Output.xlsx')


if __name__ == "__main__":
    main()
