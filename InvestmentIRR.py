# Imported Modules and lib for tests
import scipy.optimize as optimize
from datetime import datetime, date
import pandas as pd
import csv
import locale
import pickle
import time

# Main
def main():
    # Initializing Variables
    assets = []
    csv_file = 'Ativos.csv'
    prices_col = 1 # assets = ['ativo','preco','vencimento']
    date_col = 2 # assets = ['ativo','preco','vencimento']
    included_cols = [] 
    irrRate = {}

    # Initial Investment Data Entry
    initialOutcome = 'R$ 300.000,00' # Inicial Outcome
    investmentDay = '26/06/2020' # Investment Initial Outcome D-Day
    included_cols = [0,1,2] # Colums data to be read from csv file with asset name, price and expiration date. ['ativo','preco','vencimento']

    ## Step 1 - Read an CSV file with the assets:
    assets = importCSV(csv_file, included_cols)

    # Step 1.1 - To convert data strings to data values to be processed:
    initialOutcome = strToFloat(initialOutcome)
    investmentDay = strToDate(investmentDay)

    # Step 1.2 - To convert assets string prices to float numbers:
    assets = allStrToFloat(assets, prices_col)

    # Step 1.3 - To convert all assets expiration string dates to date objects:
    assets = allStrToDate(assets, date_col)
        
    # Step 1.4 - Create Cashflows list from input data:
    cf = cashFlow(initialOutcome, investmentDay, assets)
    cf.remove(cf[0]) # To remove header from cf list

    ## Step 2 - Calculate and print Internal Rate of Return:
    irrRate = irr(cf)
    
    ## Step 3 - To Consume a public web service that return the Selic rate of the day:
    
    # Step 3.1 - Doing tests to pulling data of API from Public Web Service from Banco Central do Brasil
    # ipca = request_bcb(433, None, None, None) # For tests
    # igpm = request_bcb(186, None, None, None) # For tests
    # selicRateSample = request_bcb(11, None,'20/03/2020','26/06/2020') # Pull hostoric data series within a time range
    # selicRateSample = request_bcb(11, None, None, None) # Pull all the historical data series
    
    # Step 3.2 - Pull the number of last (N) registers stored off the API.
    selicRateSample = request_bcb(11, 1 ,None, None) 
    
    # Step 3.3 - Converting float numbers to String and getting Selic Rate timestamp 
    selicRateValStr = floatToPercStr(selicRateSample[1])
    selicRateDateStr = selicRateSample[0]
    
    ## Step 4 - Show the IRR calculated and the Selic rate in console: 
    print('The IRR for the proposed investiment with outcome on {} is {:.2%}.'.format(investmentDay.strftime('%d/%m/%Y'), irrRate['x'][0]))
    print('The most recent Selic Interest Rate pulled off from Brazil Federal Bank on {} is {:.2%} per day.'.format(selicRateSample[0],selicRateSample[1]))

    ## Step 5 - Store the information of the CSV file, the calculated IRR and Selic rate in a in memory database - Feel free to use structure or framework you like.
    
    # Step 5.1 - Convert all floats nums into currency strings
    cf = cashFlow(initialOutcome, investmentDay, assets)
    allValuesToBRL(cf)
    
    # Step 5.2 - Convert all date objects to strings
    allDatesToStr(cf)

    # Step 5.3 - Storing all data and results from calculations into a df. 
    # print(type(resultsDF))
    irrRateStr = floatToPercStr(irrRate['x'][0])
    resultsDF = pd.DataFrame(finalResults(cf, irrRateStr, selicRateValStr))
    # print(resultsDF)
    picklingfile(resultsDF, 'Investment001.pkl')
    time.sleep(5)
    print('Printed after 3 seconds.')
    print(unpickingfile('Investment001.pkl'))

    
##  - Functions
def npv(cf, rate=0.1):
    
    ''' Function to calculate net present value from initial outcome, investment data
     and assets data provided into cashflows list and initial rate trigger as a guess for calculation.
    '''

    if len(cf) >= 2: # To calculate NPV if there are at least one asset to be invested in 
        first_date = min([x[2] for x in cf])
        dcf = [x[1] * (1 /
                        ((1 + rate) ** ((x[2] - first_date).days / 365))) for x in cf]
        return sum(dcf)
    elif len(cf) == 1:
        return cf[0][1] # In case there're no assets  within csv file, only initial investiment value provided
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


def strToFloat(price='R$ 0,0'):
    
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


def allStrToFloat(assets, curr_col=1):

    '''
    Function to convert currency strings to float within data from csv 
    and normalize currency values from assets prices coming from csv file
    before processing data.
    '''

    for i in range(1,len(assets)): # Starting from 1 to skip header
        assets[i][curr_col] = strToFloat(assets[i][curr_col])    
    
    return assets


def strToDate(date_str):
    
    ''' Function to convert date strings to date objects using datetime module. '''

    return datetime.strptime(date_str, '%d/%m/%Y').date()
    # return pd.to_datetime('date_str', format='%d/%m/%Y', errors='ignore') 


def allStrToDate(assets, date_col=2):
    
    '''
    Function to convert string dates to object dates within asset list privided.
    It's required to inform which is the date column index and it's considered that 
    assets list had it's header removed.  
    '''
    
    for i in range(1,len(assets)):
        assets[i][date_col] = strToDate(assets[i][date_col]) 
    
    return assets


def cashFlow(initialOutcome, investmentDay, assets):

    ''' 
    Function to create cashflows list from assets data input from csv and
    initial outcome and investment day provided. **It keeps the header.**.
    '''
    return [assets[0],['InitialOutcome', initialOutcome*(-1), investmentDay]] + assets[1:] # Initial outcome is negative in cashflows because it's an outflow cash  


def request_bcb (code_bcb, N=None, initialDate=None, endDate=None):
    config = ''
    if N is not None:
        url = 'http://api.bcb.gov.br/dados/serie/bcdata.sgs.{}/dados/ultimos/{}?formato=json'.format(code_bcb, N)
        config = 'lastResults'
    elif initialDate is not None and endDate is not None:
        url = 'http://api.bcb.gov.br/dados/serie/bcdata.sgs.{}/dados?formato=json&dataInicial={}&dataFinal={}'.format(code_bcb, initialDate, endDate)
        config = 'dateRange'
    else:
        url = 'http://api.bcb.gov.br/dados/serie/bcdata.sgs.{}/dados?formato=json'.format(code_bcb)
        config = 'allData'
    
    df = pd.read_json(url)
    df['data'] = pd.to_datetime(df['data'], dayfirst=True)      # To set day as the first parameter coming within such as dd/mm/yyyy
    df.set_index(['data','valor'], inplace=True, append=True, drop=False)       # To set date col as index

    if config == 'lastResults':        
        return [df.values[0][0],df.values.tolist()[0][1]]
    elif config == 'dateRange':     # Return is dataseries within a time range
        return df
    else: 
        return df     


def currency(val=0, curr='R$'):       
    
    ''' Function to convert float values to brazilian Real (BRL) currency strings. '''  
    
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

    return locale.currency(val, grouping=True, symbol=curr)


def allValuesToBRL(cf):

    ''' Function to convert all cashflow list values in float to (BRL) Real currency in string datatype.'''
    
    for i in range(1,len(cf)):
        cf[i][1] = currency(cf[i][1], 'R$')
    
    return cf


def allDatesToStr(cf):
    
    ''' Function to convert all date objects in the cashflow list to string datatype.'''

    for i in range(1, len(cf)):
        cf[i][2] = cf[i][2].strftime('%d/%m/%Y')
    
    return cf


def floatToPercStr(value):

    '''Function to convert a float number to a percent number string. Example 0.023562 to 2,36%.'''

    return '{:.2%}'.format(value).replace('.',',')
    

def finalResults(resultsDF, irrRateStr, selicRateValStr):
    
    '''Function to consolidate all data before storing it into pickle file in the root folder: 
    cashflow, calculated IRR and current SelicRate.'''

    for i in range(len(resultsDF)):
        if i == 0:
            resultsDF[i].append('TIR')
            resultsDF[i].append('Selic')            
        else:
            resultsDF[i].append(irrRateStr)
            resultsDF[i].append(selicRateValStr)
    
    return resultsDF


def picklingfile(resultsDF, file_name):
    with open(file_name, 'wb') as f:
        pickle.dump(resultsDF, f)
    return f'File saved with success in the root directory. Name: {file_name}.pkl'


def unpickingfile(pickle_file):
    with open(pickle_file, 'rb') as f:
        mynewlist = pickle.load(f)
    return mynewlist


if __name__ == "__main__":
    main()


