#### Import required packages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import argrelextrema
#### Register matplotlib converter not to retreive any error message while plotting
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

class highs_and_lows():
    ''' Class for analyzing failed swings.

    Attributes
    ==========
    tf: str
        choose correct csv file saved on drive: h1, m5, m3

    Methods
    =======
    get_data:
        load price data in choosen granularity
    get_highs:
        table containing only highs
    get_lows:
        table containing only lows
    get_highs_and_lows:
        finding highs and lows
    line_plot:
        creates a chart with high, close, low prices and peaks and valleys
    '''
    def __init__(self, ticker, tf, order):
        self.ticker = ticker
        self.tf = tf
        self.order = order
        self.get_data()
    
    def __repr__(self):
        return "highs_and_lows(ticker = {}, timeframe = {})".format(self.ticker, self.tf)
    
    def get_data(self):
        '''Uploading already prepared csv file, it depends on the data downloaded in data_downloader
        '''
        self.data = pd.read_csv("{}_{}.csv".format(self.ticker, self.tf), parse_dates = ["time"], index_col = "time")
        return self.data
    
    def get_highs(self):
        '''Defining highs and higher highs using argrelextrema
        '''
        hh = self.data['h']
        local_max = argrelextrema(hh.values, np.greater_equal, order=self.order)[0]
        # find highs dates
        highs_dates = []
        for i in local_max:
            highs_dates.append(self.data.index[i])
        highs_dates = pd.to_datetime(highs_dates)
        highs = highs_dates.to_frame()
        # Find high/low value at the date
        highs['hs'] = self.data['h']
        highs = highs.drop([0], axis=1) #unnecessary column
        # adding another high layer
        hhh = highs['hs']
        local_max = argrelextrema(hhh.values, np.greater_equal, order=self.order)[0]
        # find highs dates
        highs_dates = []
        for i in local_max:
            highs_dates.append(hhh.index[i])
        highs_dates = pd.to_datetime(highs_dates)
        hhighs = highs_dates.to_frame()
        # Find high/low value at the date
        hhighs['hs'] = self.data['h']
        highs['hhs'] = hhighs['hs']
        #copy df to use its layout
        nonah = self.data.copy()
        nonah['highs'] = highs['hs']
        nonah['hhighs'] = highs['hhs']
        # Data with missing values is required to creat the plot
        # Data with forward fill is required for defining trading points
        nonah.dropna(subset=['highs'], axis=0, inplace=True)
        nonah = nonah.drop(['o','h','l','c'], axis=1)
        return nonah
    
    def get_lows(self):
        '''Defining lows and lower lows using argrelextrema
        '''
        ll = self.data['l']
        local_min = argrelextrema(ll.values, np.less_equal, order=self.order)[0]
        # find lows dates
        lows_dates = []
        for i in local_min:
            lows_dates.append(self.data.index[i])
        lows_dates = pd.to_datetime(lows_dates)
        lows = lows_dates.to_frame()
        # Find high/low value at the date
        lows['ls'] = self.data['l']
        lows = lows.drop([0], axis=1) #unnecessary column
        # adding another low layer
        lll = lows['ls']
        local_min = argrelextrema(lll.values, np.less_equal, order=self.order)[0]
        # find highs dates
        lows_dates = []
        for i in local_min:
            lows_dates.append(lll.index[i])
        lows_dates = pd.to_datetime(lows_dates)
        llows = lows_dates.to_frame()
        # Find high/low value at the date
        llows['ls'] = self.data['l']
        lows['lls'] = llows['ls']
        #copy df to use its layout
        nonal = self.data.copy()
        nonal['lows'] = lows['ls']
        nonal['llows'] = lows['lls']
        # Data with missing values is required to creat the plot
        # Data with forward fill is required for defining trading points
        nonal.dropna(subset=['lows'], axis=0, inplace=True)
        nonal = nonal.drop(['o','h','l','c'], axis=1)
        return nonal
        
    def get_highs_and_lows(self):
        '''Running highs and lows functions, forward filling na values and generating one table containing all
        '''
        highs = self.get_highs()
        lows = self.get_lows()
        self.data['highs'] = highs['highs']
        self.data['hhighs'] = highs['hhighs']
        self.data['lows'] = lows['lows']
        self.data['llows'] = lows['llows']
        # Data with missing values is required to creat the plot
        # Data with forward fill is required for define trading points
        nona = self.data.copy()
        nona['highs'] = nona['highs'].ffill()
        nona['hhighs'] = nona['hhighs'].ffill()
        nona['lows'] = nona['lows'].ffill()
        nona['llows'] = nona['llows'].ffill()
        nona.dropna(inplace=True)
        return nona
        
    # Create a plot with highs and lows shown on graph.
    def line_plot(self, since, to):
        '''Create a plot with highs and lows shown on graph.
        Three lines are respectively: high, close and low price at timestamp.
        Different colours are showing extremes in different granularity
        '''
        pdata = self.data[since:to]
        plt.figure(figsize=(30,15))
        plt.plot(pdata["h"]) #upper price
        plt.plot(pdata['c'], color='black',linewidth=2, markersize=12) #close prices
        plt.plot(pdata["l"]) #lower price
        plt.scatter(pdata.index, pdata['highs'], marker = "v", color = "red")
        plt.scatter(pdata.index, pdata['hhighs'], marker = "v", color = "purple")
        plt.scatter(pdata.index, pdata['lows'], marker = "^", color = "green")
        plt.scatter(pdata.index, pdata['llows'], marker = "^", color = "blue")
        plt.show()