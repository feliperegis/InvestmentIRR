import module
import pandas as pd

########################################################################################################################
# This is a Python script to calculate the interest rate of return for a investment with assets details stored into a ##
# csv file.
# -------------------------------------------------------------------------------------------------------------------- #
# Author: Felipe Regis
# Contact: frs.poli@gmail.com
########################################################################################################################


# Main
def main():
    # Initializing Variables
    assets = []
    csv_file = 'Ativos.csv'
    prices_col = 1  # assets = ['ativo','preco','vencimento']
    date_col = 2    # assets = ['ativo','preco','vencimento']
    included_cols = [0, 1, 2]     # Colums data to be read from csv file with asset name, price and expiration date.
                                  # ['ativo','preco','vencimento']

    # Initial Investment Data Entry
    initial_outcome = 'R$ 300.000,00'    # Inicial Outcome
    investment_day = '26/06/2020'    # Investment Initial Outcome D-Day

########################################################################################################################
    # Step 1 - Read an CSV file with the assets:
    assets = module.import_csv(csv_file, included_cols)

    # Step 1.1 - To convert data strings to data values to be processed:
    initial_outcome_val = module.str_to_float(initial_outcome)
    investment_day_date = module.str_to_date(investment_day)

    # Step 1.2 - To convert assets string prices to float numbers:
    assets = module.all_str_to_float(assets, prices_col)

    # Step 1.3 - To convert all assets expiration string dates to date objects:
    assets = module.all_str_to_date(assets, date_col)

    # Step 1.4 - Create Cash flows list from input data:
    cf = module.cash_flow(initial_outcome_val, investment_day_date, assets)
    cf.remove(cf[0])    # To remove header from cf list

########################################################################################################################
    # Step 2 - Calculate and print Internal Rate of Return:
    irr_rate = module.irr(cf)

    # Step 3 - To Consume a public web service that return the Selic rate of the day:

    # Step 3.1 - Doing tests to pulling data of API from Public Web Service from Banco Central do Brasil
    # ipca = request_bcb(433, None, None, None)     # For tests
    # igpm = request_bcb(186, None, None, None)     # For tests
    # selic_rate_sample = request_bcb(11, None,'20/03/2020','26/06/2020')   # Pull historic data series within a time
                                                                            # range
    # selic_rate_sample = request_bcb(11, None, None, None) # Pull off all the historic data series from BCB

    # Step 3.2 - Pull the number of last (N) registers stored off the API.
    selic_rate_sample = module.request_bcb(11, 1, None, None)

    # Step 3.3 - Converting float numbers to String and getting Selic Rate timestamp
    selic_rate_val_str = module.float_to_perc_str(selic_rate_sample[1])

########################################################################################################################
    # Step 4 - Show the IRR calculated and the Selic rate in console:
    print('The IRR for the proposed investment with outcome on {} is {:.2%} per year.'.format(investment_day_date.strftime('%d/%m/%Y'), irr_rate['x'][0]))
    print('The most recent Selic Interest Rate pulled off from BACEN API on {} is {:.2%} per day.'.format(selic_rate_sample[0], selic_rate_sample[1]))

########################################################################################################################
    # Step 5 - Store the information of the CSV file, the calculated IRR and Selic rate in a in memory database -
    # Feel free to use structure or framework you like.

    # Step 5.1 - Convert all floats nums into currency strings
    cf_brl = module.all_val_to_brl(cf)

    # Step 5.2 - Convert all date objects to strings and adding hearder back after calculations
    cf_date = module.all_dates_to_str(cf_brl)
    cf_edit = [assets[0]] + cf_date

    # Step 5.3 - Storing all data and results from calculations into a file in memory to be restored as needed
    irr_rate_str = module.float_to_perc_str(irr_rate['x'][0])
    results_consolidated = module.consolidate(cf_edit, irr_rate_str, selic_rate_val_str)
    results_df = pd.DataFrame(results_consolidated)  # From list to dataframe view
    # print(type(results_df))
    print(results_df)
    # module.pickling_file(results_df, 'Investment001.pkl')
    # print(module.unpicking_file('Investment001.pkl'))

########################################################################################################################
    # Step 6 - Dockerizing application
    # print(pd.show_versions())
    # print(pickle.__version__)

########################################################################################################################


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
