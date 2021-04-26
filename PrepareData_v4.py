#### Import required packages
import pandas as pd
import numpy as np
from scipy.signal import argrelmin, argrelmax

class highs_and_lows():
    ''' Class for analyzing failed swings.

    Attributes
    ==========
    dataframe: pandas df
        use prepared df

    Methods
    =======
    get_highs_and_lows:
        helper function which indentifies highs and lows in dataframe
    get_full_data:
        main function which returns dataframe with two levels of granularity

    '''
    
    def __init__(self, dataframe):
        self.dataframe = dataframe
    
    def get_highs_and_lows(self):
        '''Defining highs and lows using argrelextrema
        '''
        
        # Simple funtion which looks at the nerby points to locate change from hight to low and from low to high.
        # For trading purpose we do not want to see two highs/lows against each other.
        def islocalmax(x):
            """Both neighbors are lower,
            assumes a centered window of size 3"""
            return (x[0] < x[1]) & (x[2] < x[1])

        def islocalmin(x):
            """Both neighbors are higher,
            assumes a centered window of size 3"""
            return (x[0] > x[1]) & (x[2] > x[1])

        def isextrema(x):
            return islocalmax(x) or islocalmin(x)
        
        # Starting function
        df = self.dataframe.copy()
        N = 5 # max number of iterations
        #df = pd.read_csv('prices.csv') # load your stock prices in OHLC format
        h = df['h'].dropna().copy() # make a series of Highs
        l = df['l'].dropna().copy()  # make a series of Lows
        for i in range(N):
                h = h.iloc[argrelmax(h.values)[0]] # locate maxima in Highs
                l = l.iloc[argrelmin(l.values)[0]] # locate minima in Lows
                h = h[~h.index.isin(l.index)] # drop index that appear in both
                l = l[~l.index.isin(h.index)] # drop index that appear in both
                if i == 1: # save lowest level of granularity
                    self.h1 = h
                    self.l1 = l
                elif i == 2: # save required granularity
                    h2 = h
                    l2 = l
                
        # This part of code is to be optimized
        # Defining extremes for first level of granularity
        price1 = self.h1
        price1 = price1.append(self.l1)
        price1 = price1.sort_index()
        # Finding if value is extreme
        ext_loc1 = price1.rolling(3, center=True).apply(isextrema, raw=False).astype(np.bool_)
        # Pulling the extreme value
        self.thres_ext_val1 = price1[ext_loc1]
        # Creating tables cointaining only highs and lows confirmed by zigzag step
        # Highs
        highs1 = self.h1.to_frame()
        highs1 = highs1.assign(result=highs1.isin(self.thres_ext_val1).astype(int))
        highs1 = highs1[highs1.result != 0]
        highs1.drop('result', axis=1, inplace=True)
        # Lows
        lows1 = self.l1.to_frame()
        lows1 = lows1.assign(result=lows1.isin(self.thres_ext_val1).astype(int))
        lows1 = lows1[lows1.result != 0]
        lows1.drop('result', axis=1, inplace=True)
        

        # Defining extremes for second level of granularity
        price2 = h2
        price2 = price2.append(l2)
        price2 = price2.sort_index()
        # Finding if value is extreme
        ext_loc2 = price2.rolling(3, center=True).apply(isextrema, raw=False).astype(np.bool_)
        # Pulling the extreme value
        self.thres_ext_val2 = price2[ext_loc2]
        # Creating tables cointaining only highs and lows confirmed by zigzag step
        # Highs
        highs2 = h2.to_frame()
        highs2 = highs2.assign(result=highs2.isin(self.thres_ext_val2).astype(int))
        highs2 = highs2[highs2.result != 0]
        highs2.drop('result', axis=1, inplace=True)
        # Lows
        lows2 = l2.to_frame()
        lows2 = lows2.assign(result=lows2.isin(self.thres_ext_val2).astype(int))
        lows2 = lows2[lows2.result != 0]
        lows2.drop('result', axis=1, inplace=True)
        
        return highs1, lows1, highs2, lows2
    
    def get_full_data(self):
        '''Running highs and lows function, forward filling N/A values and generating one table containing all
        '''
        df = self.dataframe.copy()
        df['highs'] = self.h1
        df['lows'] = self.l1
        # Data with missing values is required to creat the plot
        # Data with forward fill is required to define trading points
        full_table = df.copy()
        full_table['highs'] = df['highs'].ffill()
        full_table['lows'] = df['lows'].ffill()
        full_table.dropna(inplace=True)
        return full_table
        
def prepare_data(dataframe):
    '''Complete function to create required dataset, it runs higs_and_lows module 
    '''
    fs = highs_and_lows(dataframe)
    highs1, lows1, highs2, lows2 = fs.get_highs_and_lows()
    data = fs.get_full_data()
    
    # First level of granurality - for initialing trade
    ###LONG
    # Adding new column direction
    highs1.loc[:,('direction')] = None
    highs1.direction.iloc[0] = 0 # Initially there is no direction taken by the price
    for bar in range(1, len(highs1)):
        if highs1.h.iloc[bar-1] < highs1.h.iloc[bar-2]:
            highs1.direction.iloc[bar] = -1
        elif highs1.h.iloc[bar-1] > highs1.h.iloc[bar-2]:
            highs1.direction.iloc[bar] = 1
        else:
            highs1.direction.iloc[bar] = highs1.direction.iloc[bar-1]
    ###SHORT        
    lows1.loc[:,('direction')] = None
    lows1.direction.iloc[0] = 0
    for bar in range(1, len(lows1)):
        if lows1.l.iloc[bar-1] > lows1.l.iloc[bar-2]:
            lows1.direction.iloc[bar] = 1
        elif lows1.l.iloc[bar-1] < lows1.l.iloc[bar-2]:
            lows1.direction.iloc[bar] = -1
        else:
            lows1.direction.iloc[bar] = lows1.direction.iloc[bar-1]

    data.loc[:,('dhs1')] = highs1.loc[:,('direction')].copy(deep=True)
    data.loc[:,('dls1')] = lows1.loc[:,('direction')].copy(deep=True)
    data = data.copy(deep=True)
    data['dhs1'] = data['dhs1'].ffill()
    data['dls1'] = data['dls1'].ffill()
    data.dropna(inplace=True)

    # Second level of granurality:
    ###LONG
    # Adding new column direction
    highs2.loc[:,('direction')] = None
    highs2.direction.iloc[0] = 0 # Initially there is no direction taken by the price
    for bar in range(1, len(highs2)):
        if highs2.h.iloc[bar-1] < highs2.h.iloc[bar-2]:
            highs2.direction.iloc[bar] = -1
        elif highs2.h.iloc[bar-1] > highs2.h.iloc[bar-2]:
            highs2.direction.iloc[bar] = 1
        else:
            highs2.direction.iloc[bar] = highs2.direction.iloc[bar-1]
    ###SHORT        
    lows2.loc[:,('direction')] = None
    lows2.direction.iloc[0] = 0
    for bar in range(1, len(lows2)):
        if lows2.l.iloc[bar-1] > lows2.l.iloc[bar-2]:
            lows2.direction.iloc[bar] = 1
        elif lows2.l.iloc[bar-1] < lows2.l.iloc[bar-2]:
            lows2.direction.iloc[bar] = -1
        else:
            lows2.direction.iloc[bar] = lows2.direction.iloc[bar-1]

    data.loc[:,('dhs2')] = highs2.loc[:,('direction')].copy(deep=True)
    data.loc[:,('dls2')] = lows2.loc[:,('direction')].copy(deep=True)
    data = data.copy(deep=True)
    data['dhs2'] = data['dhs2'].ffill()
    data['dls2'] = data['dls2'].ffill()
    data.dropna(inplace=True)
    # Adding column which specifies hour of a candle
    data['hour'] = data.index.hour
    
    return data