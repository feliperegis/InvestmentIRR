import csv
import datetime
import scipy.optimize as optimize
import pandas as pd
import requests
import locale
import pickle
import time

from datetime import datetime, date


# - Functions


def npv(cf, rate=0.1):
    """ Function to calculate net present value from initial outcome, investment data
     and assets data provided into cashflows list and initial rate trigger as a guess for calculation.
    """

    if len(cf) >= 2:  # To calculate NPV if there are at least one asset to be invested in
        first_date = min([x[2] for x in cf])
        dcf = [x[1] * (1 /
                       ((1 + rate) ** ((x[2] - first_date).days / 365))) for x in cf]
        return sum(dcf)
    elif len(cf) == 1:
        return cf[0][1]  # In this case, there are no assets within csv file, only initial investment value provided
    else:
        return 0


def irr(cf):
    """
    Function to calculate Interest Rate of Return using cash flows data and npv function using
    scipy.optimize package to find IRR considering a 10% IRR as trigger.
    """

    f = lambda x: npv(cf, rate=x)
    r = optimize.root(f, [0])
    return r


def import_csv(csv_file, included_cols):
    """ Function to import specified data columns from csv file and store
    them into an object to be normalized and processed as needed.
    """

    with open(csv_file, newline='') as csv_file:
        asset = []
        assets = []
        dt = csv.reader(csv_file, delimiter=';')
        for row in dt:
            for i in included_cols:
                asset.append(row[i])
            assets.append(asset)
            asset = []
    return assets


def str_to_float(price='R$ 0,0'):
    """
    Function to convert currency string with or without 'R$' mark
    to float number.
    """

    price = price.strip().strip('R$')
    try:
        [num, dec] = price.rsplit(',')
        aside = str(dec)
        dec = int(dec)
        x = int('1' + '0' * len(aside))
        val = float(dec) / x
        num = num.replace('.', '')
        num = int(num)
        val = num + val
    except ValueError:
        raise ValueError('Incorrect value format, should have a comma as decimal separator')
        # val = int(price)
    return val


def all_str_to_float(assets, curr_col=1):
    """
    Function to convert currency strings to float within data from csv
    and normalize currency values from assets prices coming from csv file
    before processing data.
    """

    for i in range(1, len(assets)):  # Starting from 1 to skip header
        assets[i][curr_col] = str_to_float(assets[i][curr_col])

    return assets


def str_to_date(date_str):
    """ Function to convert date strings to date objects using datetime module. """

    try:
        datee = datetime.strptime(date_str, '%d/%m/%Y').date()
    except ValueError:
        raise ValueError('Incorrect data format, should be dd/mm/yyyy')

    return datee
    # return pd.to_datetime('date_str', format='%d/%m/%Y', errors='ignore')


def all_str_to_date(assets, date_col=2):
    """
    Function to convert string dates to object dates within asset list privided.
    It's required to inform which is the date column index and it's considered that
    assets list had it's header removed.
    """

    for i in range(1, len(assets)):
        assets[i][date_col] = str_to_date(assets[i][date_col])

    return assets


def cash_flow(initial_outcome_val, investment_day_date, assets):
    """
    Function to create cashflows list from assets data input from csv and
    initial outcome and investment day provided. **It keeps the header.**.
    """

    # Initial outcome is negative in the cash flow because it's an outflow cash
    return [assets[0], ['Initial Outcome', initial_outcome_val * (-1), investment_day_date]] + assets[1:]


def request_bcb(code_bcb, n=None, initial_date=None, end_date=None):
    config = ''
    if n is not None:
        url = 'http://api.bcb.gov.br/dados/serie/bcdata.sgs.{}/dados/ultimos/{}?formato=json'.format(code_bcb, n)
        config = 'lastResults'
    elif initialDate is not None and endDate is not None:
        url = 'http://api.bcb.gov.br/dados/serie/bcdata.sgs.{}/dados?formato=json&dataInicial={}&dataFinal={}'.format(
            code_bcb, initial_date, end_date)
        config = 'date_range'
    else:
        url = 'http://api.bcb.gov.br/dados/serie/bcdata.sgs.{}/dados?formato=json'.format(code_bcb)
        config = 'allData'

    df = pd.read_json(url)
    df['data'] = pd.to_datetime(df['data'], dayfirst=True)  # To set day as the first parameter (dd/mm/yyyy)

    df.set_index(['data', 'valor'], inplace=True, append=True, drop=False)  # To set date col as index

    if config == 'lastResults':
        response = requests.get(url)
        if response.ok:
            return [df.values[0][0], df.values.tolist()[0][1]]
        else:
            return 'Bad Response!'

    else:  # Return is all data series within a time range or not
        response = requests.get(url)
        if response.ok:
            return df
        else:
            return 'Bad Response!'


def currency(val=0, curr='R$'):
    """ Function to convert float values to brazilian Real (BRL) currency strings. """

    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

    return locale.currency(val, grouping=True, symbol=curr)


def all_val_to_brl(cf):
    """ Function to convert all cashflow list values in float to (BRL) Real currency in string datatype."""

    for i in range(len(cf)):
        cf[i][1] = currency(cf[i][1], 'R$')

    return cf


def all_dates_to_str(cf):
    """ Function to convert all date objects in the cash flow list to string datatype."""

    for i in range(len(cf)):
        cf[i][2] = cf[i][2].strftime('%d/%m/%Y')

    return cf


def float_to_perc_str(value):
    """Function to convert a float number to a percent number string. Example 0.023562 to 2,36%."""

    return '{:.2%}'.format(value).replace('.', ',')


def consolidate(results_df, irr_rate_str, selic_rate_val_str):
    """Function to consolidate all data before storing it into pickle file in the root folder:
    cash flow, calculated IRR and current Selic rate."""

    for i in range(len(results_df)):
        if i == 0:
            results_df[i].append('TIR')
            results_df[i].append('Selic')
        else:
            results_df[i].append(irr_rate_str)
            results_df[i].append(selic_rate_val_str)

    return results_df


def pickling_file(results_df, file_name):
    with open(file_name, 'wb') as f:
        pickle.dump(results_df, f)
        time.sleep(3)
    return f'File saved with success in the root directory. Name: {file_name}.pkl'

def unpicking_file(pickle_file):
    with open(pickle_file, 'rb') as f:
        my_new_list = pickle.load(f)
    return my_new_list
