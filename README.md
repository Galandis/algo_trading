# algo_trading
This repository contains codes used for algorithmic trading via Oanda API.

It is a part of a masters degree thesis.
There is a code which only works having brokerage account in Oanda as connection is necessary.

The goal is to create three separate algorithms for automated trading.\
1st will be based on price action.\
2nd will be based on indicators.\
3rd will be based on machine learning.

Once rules are created then as base for choosing a right model will be iterative backtesting run across already existing data.\
After that there will be connection established with demo account in Oanda and strategies will be tested in live market.

This is not a working and complete product.\
All rights reserved.

data_downloader - can be used to download data from Oanda API. It is structured to make multiple query in order to download even 10yr of 3m bars. \
highandlow_csv - this is a class created in order to find highs and lows in price movement. It scans surrounding and picks the extremum.\
PA_entry_fixed_RR - iterative backtesting for price action strategy.\
ML_logistic - logistic regression used to define if next bar will be increase or decrease. The data is downloaded directly from Oanda API.
