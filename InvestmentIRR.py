# Imported Modules and Std Libs
import scipy.optimize as optimize
from datetime import datetime, date
import pandas as pd
import csv
# from bancocentralbrasil import Cambio, Selic

# Main
def main():
    # Initializing Variables
    assets = []
    csv_file = 'Ativos.csv'
    prices_col = 1 # assets = ['ativo','preco','vencimento']
    date_col = 2 # assets = ['ativo','preco','vencimento']
    included_cols = [] 
    irrRate = {}
    # cambio = cambio()
    # dolar_venda = cambio.get_dolar_venda()
    # dolar_compra = cambio.get_dolar_compra()
    # selic = Selic()
    # selicRate = selic.get_selic_real()

    # Initial Investment Data Entry
    initialOutcome = 'R$ 300.000,00' # Inicial Outcome
    investmentDay = '26/06/2020' # Investment D-Day
    included_cols = [0,1,2] # Colums data to be read from csv file with asset name, price and expiration date. ['ativo','preco','vencimento']

    ## Step 1 - Read an CSV file with the assets
    assets = importCSV(csv_file, included_cols)

    # Step 1.1 - To convert data strings to data values to be processed
    initialOutcome = convertStrToFloat(initialOutcome)
    investmentDay = convertStrToDate(investmentDay)

    # Step 1.2 - To convert assets string prices to float numbers
    assets = assetsStrToFloat(assets, prices_col)

    # Step 1.3 - To convert all assets expiration string dates to date objects
    assets = convertAllStrToDate(assets, date_col)
        
    # Step 1.4 - Create Cashflows list from input data
    cf = createCashFlowsList(initialOutcome, investmentDay, assets)

    ## Step 2 - Calculate and print Internal Rate of Return
    irrRate = irr(cf)
    print('The IRR for the investiment proposed with outcome on {} is {:.2%}.'.format(investmentDay.strftime('%d/%m/%Y'), irrRate['x'][0]))

    ## Step 3 - To Consume a public web service that return the Selic rate of the day.
    # selicRate = Selic.get_selic_real()
    # print(selicRate)

##  - Functions
def npv(cf, rate=0.1):
    
    ''' Function to calculate net present value from initial outcome, investment data
     and assets data provided into cashflows list and initial rate trigger for calculation.
    '''
    
    if len(cf) >= 2:
        first_date = min([x[1] for x in cf])
        dcf = [x[0] * (1 /((1 + rate) ** ((x[1] - first_date).days / 365))) for x in cf]
        return sum(dcf)
    elif len(cf) == 1:
        return cf[0][1]
    else:
        return 0


def irr(cf):
    
    '''
    Function to calculate Interest Rate of Return using cashflows data and npv function using
    scipy.optimize package to find IRR considering a 10% IRR as trigger.
    '''

    f = lambda x: npv(cf, rate=x)
    r = optimize.root(f, [0])
    return r


def importCSV(csv_file, included_cols):
    
    ''' Function to import specified data columns from csv file and store
    them into an object to be normalized and processed as needed. 
    '''

    with open(csv_file, newline='') as csv_file:
        asset = []
        assets = []
        dt = csv.reader(csv_file, delimiter = ';')        
        for row in dt:
            for i in included_cols:
                asset.append(row[i])
            assets.append(asset)
            asset = []
    return assets    


        # for row in dt:
        #     if start > 0:
        #         for i in included_cols:
        #             if i == 1:
        #                 price_num = currToFloat(row[i])
        #                 asset.append(price_num)
        #             else:
        #                 asset.append(row[i])
        #         assets.append([asset])
        #         # asset = []
        #     start += 1


def convertStrToFloat(price='R$ 0,0'):
    
    '''
    Function to convert currency string with or without 'R$' mark
    to float number.
    '''
    
    price = price.strip().strip('R$')
    try:
        [num,dec]=price.rsplit(',')
        aside = str(dec)
        dec = int(dec)
        x = int('1'+'0'*len(aside))
        val = float(dec)/x
        num = num.replace('.','')
        num = int(num)
        val = num + val
    except:
        val = int(price)
    return val


def assetsStrToFloat(assets, curr_col=1):

    '''
    Function to convert currency strings to float within data from csv 
    and normalize currency values from assets prices coming from csv file
    before processing data.
    '''

    for i in range(1,len(assets)): # Starting from 1 to skip header
        assets[i][curr_col] = convertStrToFloat(assets[i][curr_col])    
    
    return assets


def convertStrToDate(date_str):
    
    ''' Function to convert date strings to date objects using datetime module. '''
    
    return datetime.strptime(date_str, '%d/%m/%Y')
    # return pd.to_datetime('date_str', format='%d/%m/%Y', errors='ignore') 

def convertAllStrToDate(assets, date_col=2):
    
    '''
    Function to convert string dates to object dates within asset list privided.
    It's required to inform which is the date column index and it's considered that 
    assets list had it's header removed.  
    '''
    
    for i in range(1,len(assets)):
        assets[i][date_col] = convertStrToDate(assets[i][date_col]) 
    
    return assets


def createCashFlowsList(initialOutcome, investmentDay, assets):

    ''' 
    Function to create cashflows list from assets data input from csv and
    initial outcome and investment day provided.
    '''
    assets.remove(assets[0]) # To remove header from assets list

    for i in range(len(assets)): # To remove all first list attributes with asset names from assets list
        del assets[i][0]

    return [[initialOutcome*(-1), investmentDay]] + assets # Initial outcome is negative in cashflows because it's an outflow cash  

if __name__ == "__main__":
    main()


