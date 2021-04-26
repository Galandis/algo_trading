import pandas as pd
import numpy as np
import time

class IterativeBase():
    ''' Base class for iterative backtesting of trading strategies.

    Attributes
    ==========
    symbol: str
        ticker symbol with which to work with
    timeframe: str
        granularity of data i.e: D, H1, M5
    spread: int
        spread on the ticker used to calculate costs of trading
    amount: float
        initial amount to be invested per trade
    use_spread: boolean (default = True) 
        whether trading costs (spread) are included

    Methods
    =======
    get_data:
        retrieves and prepares the data
    get_values:
        returns the date, the price and the spread for the given bar
    print_current_balance:
        prints out the current (cash) balance
    buy_instrument:
        places a buy order
    sell_instrument:
        places a sell order
    print_current_position_value:
        prints out the current position value
    print_current_nav:
        prints out the current net asset value (nav)
    close_pos:
        closes out a long or short position
    '''

    def __init__(self, symbol, timeframe, spread, amount, use_spread = True):
        self.symbol = symbol
        self.timeframe = timeframe
        self.spread = spread
        self.initial_balance = amount
        self.current_balance = amount
        self.units = 0
        self.trades = 0
        self.position = 0
        self.use_spread = use_spread
        self.get_data()

    def get_data(self):
        ''' Retrieves and prepares the data.
        '''
        raw = pd.read_csv("Data/{}_{}.csv".format(self.symbol, self.timeframe), parse_dates = ["time"], index_col = "time")
        raw.drop(['o','h','l'], axis=1, inplace=True)
        raw.rename(columns = {'c' : 'price', 'volume' : 'vol'}, inplace = True)
        raw["returns"] = np.log(raw["price"] / raw["price"].shift(1))
        self.data = raw
    
    def get_values(self, bar):
        ''' Returns the date, the price and the spread for the given bar.
        '''
        date = str(self.data.index[bar].date())
        price = round(self.data.price.iloc[bar], 5)
        spread = self.spread
        return date, price, spread
    
    def print_current_balance(self, bar):
        ''' Prints out the current (cash) balance.
        '''
        date, price, spread = self.get_values(bar)
        print("{} | Current Balance: {}".format(date, round(self.current_balance, 2)))
        
    def buy_instrument(self, bar, units = None, amount = None):
        ''' Places a buy order.
        '''
        date, price, spread = self.get_values(bar)
        if self.use_spread:
            price += spread/2 # ask price
        if amount is not None: # use units if units are passed, otherwise calculate units
            units = int(amount / price)
        self.current_balance -= units * price # reduce cash balance by "purchase price"
        self.units += units
        self.trades += 1
        print("{} |  Buying {} for {}".format(date, units, round(price, 5)))
    
    def sell_instrument(self, bar, units = None, amount = None):
        ''' Places a sell order.
        '''
        date, price, spread = self.get_values(bar)
        if self.use_spread:
            price -= spread/2 # bid price
        if amount is not None: # use units if units are passed, otherwise calculate units
            units = int(amount / price)
        self.current_balance += units * price # increases cash balance by "purchase price"
        self.units -= units
        self.trades += 1
        print("{} |  Selling {} for {}".format(date, units, round(price, 5)))
    
    def print_current_position_value(self, bar):
        ''' Prints out the current position value.
        '''
        date, price, spread = self.get_values(bar)
        cpv = self.units * price
        print("{} |  Current Position Value = {}".format(date, round(cpv, 2)))
    
    def print_current_nav(self, bar):
        ''' Prints out the current net asset value (nav).
        '''
        date, price, spread = self.get_values(bar)
        nav = self.current_balance + self.units * price
        print("{} |  Net Asset Value = {}".format(date, round(nav, 2)))
        
    def close_pos(self, bar, SMA_S, SMA_L):
        ''' Closes out a long or short position.
        '''
        date, price, spread = self.get_values(bar)
        print(75 * "-")
        print("{} | +++ CLOSING FINAL POSITION +++".format(date))
        self.current_balance += self.units * price # closing final position (works with short and long!)
        self.current_balance -= (abs(self.units) * spread/2 * self.use_spread) # substract half-spread costs
        print("{} | closing position of {} for {}".format(date, self.units, price))
        self.units = 0 # setting position to neutral
        self.trades += 1
        self.perf = (self.current_balance - self.initial_balance) / self.initial_balance * 100
        self.print_current_balance(bar)
        print("{} | net performance (%) = {}".format(date, round(self.perf, 2) ))
        print("{} | number of trades executed = {}".format(date, self.trades))
        print(75 * "-")