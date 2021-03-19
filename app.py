import os, csv
from flask import Flask, render_template, request
from patterns import patterns
import yfinance as yf
import pandas as pd
import talib


'''reminder
Set-ExecutionPolicy Unrestricted -Scope Process
$env:FLASK_APP = "app.py"
$env:FLASK_ENV = "development"
flask run
'''

app = Flask(__name__)


@app.route('/')
def index():
    pattern = request.args.get('pattern', None)
    stocks = {}
    # read in all company tickers from companies.csv
    with open('datasets/companies.csv') as f:
        for row in csv.reader(f):
            stocks[row[0]] = {'company' : row[1]}

    if pattern:
        datafiles = os.listdir('datasets/daily')
        for filename in datafiles:
            df = pd.read_csv(f'datasets/daily/{filename}')
            pattern_function = getattr(talib, pattern)
            symbol = filename.split('.')[0]
            try:
                result = pattern_function(df['Open'], df['High'], df['Low'], df['Close'])
                last = result.tail(1).values[0]
                # print(last)
                if last > 0:
                    stocks[symbol][pattern] = 'bullish'
                elif last < 0:
                    stocks[symbol][pattern] = 'bearish'
                else:
                    stocks[symbol][pattern] = None
            except:
                pass

    return render_template('index.html', patterns=patterns, stocks=stocks, current_pattern=pattern)

@app.route('/snapshot')
def snapshot():
    # loop through all companies in companies.csv
    # and download stock data for each one
    # and store in separate csv file in daily folder
    with open ('datasets/companies.csv') as f:
        companies = f.read().splitlines()
        for company in companies:
            symbol = company.split(',')[0]
            df = yf.download(symbol, start="2021-01-01", end="2021-01-31")
            df.to_csv(f'datasets/daily/{symbol}.csv')
    return {
        'code': 'success' 
    }

if __name__ == '__main__':
    app.run(debug=True)