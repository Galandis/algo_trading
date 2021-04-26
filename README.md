# algo_trading
This repository contains codes used for algorithmic trading via Oanda API.\
The repository was created with help of https://www.udemy.com/course/algorithmic-trading-with-python-and-machine-learning/

It is a part of a masters degree thesis.\
There is a code which only works having brokerage account in Oanda as connection is necessary.

The goal is to create three separate algorithms for automated trading.\
1st will be based on indicators.\
2nd will be based on price action.\
3rd will be based on machine learning.

Once rules are created then the strategy will be backtested across already downloaded data.\
After that there will be connection established with demo account in Oanda and strategies will be tested in live(demo) market.

This is not a working or complete product.\
All rights reserved.

PrepareData_v4 - module required to prepare data which is used in PA strategy\
data_downloader_v2 - can be used to download data from Oanda API. It is structured to make multiple query in order to download even 10yr of 3m bars.\
price_action_v5 - iterative backtesting for price action strategy.\
ML_logistic - logistic regression used to define if next bar will be increase or decrease. The data is downloaded directly from Oanda API.\
IterativeBase and IterativeBacktest - modules required for SMA strategy\
SMA_cross_v5 - strategy based on cross of two simple moving averages\
DNN_model - module reuired for DNN strategy
DNN_v2 - strategy based on Deep Neural Network
