# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 17:36:16 2019

@author: 51722
"""

# Here you can
# 1. import necessary python packages for your strategy
# 2. Load your own facility files containing functions, trained models, extra data, etc for later use
# 3. Set some global constants
# Note:
# 1. You should put your facility files in the same folder as this strategy.py file
# 2. When load files, ALWAYS use relative path such as "data/facility.pickle"
# DO NOT use absolute path such as "C:/Users/Peter/Documents/project/data/facility.pickle"
from auxiliary import generate_bar
import numpy as np
import pandas as pd
#from sklearn.externals import joblib
import copy as cp

#model = joblib.load('model.pkl')#####
asset_index = 0 # only consider BTC (the **First** crypto currency in dataset)
bar_length = 30  # Number of minutes to generate next new bar

# Here is your main strategy function
# Note:
# 1. DO NOT modify the function parameters (time, data, etc.)
# 2. The strategy function AWAYS returns two things - position and memory:
# 2.1 position is a np.array (length 4) indicating your desired position of four crypto currencies next minute
# 2.2 memory is a class containing the information you want to save currently for future use


def handle_bar(counter,  # a counter for number of minute bars that have already been tested
               time,  # current time in string format such as "2018-07-30 00:30:00"
               data,  # data for current minute bar (in format 2)
               init_cash,  # your initial cash, a constant
               transaction,  # transaction ratio, a constant
               cash_balance,  # your cash balance at current minute
               crypto_balance,  # your crpyto currency balance at current minute
               total_balance,  # your total balance at current minute
               position_current,  # your position for 4 crypto currencies at this minute
               memory  # a class, containing the information you saved so far
               ):
    # Here you should explain the idea of your strategy briefly in the form of Python comment.
    # You can also attach facility files such as text & image & table in your team folder to illustrate your idea

    # The idea of my strategy:
    # Single alpha factor model for investment on BTC

    # The position of BTC is set by an alpha factor "(100*mean/CLOSE)*np.log(mean/1*std)"

    # When the operation on position will cause that the cash_balance is lower than 10000, this operation will be stop

    # Get position of last minute
    position_new = cp.deepcopy(position_current)
    # Generate OHLC data for every 30 minutes
    if (counter == 0):
        #memory.data_save = np.zeros((bar_length, 5))#, dtype=np.float64)
        memory.data_save = pd.DataFrame(columns = ['close', 'high', 'low', 'open', 'volume'])

    if ((counter + 1) % bar_length == 0):
        memory.data_save.loc[bar_length - 1] = data[asset_index,:5]
        bar = generate_bar(memory.data_save) # pandas dataframe
        #print(bar)
        aveopen=bar['ave_open']
        aveclose=bar['ave_close']
        avehigh=bar['ave_high']
        avelow=bar['ave_low']
        avemean=bar['ave_mean']
        avestd=bar['ave_std']
        avemed=bar['ave_med']
        if (avelow[0]>(avemean[0]-1.5*avestd[0])  and 
            avehigh[0] < (avemean[0]+1.5*avestd[0]) and
            (aveopen[0]+avelow[0])>1.9*avemean[0] and
            (aveclose[0]+avehigh[0])<2.1*avemean[0] and
            aveclose[0]<aveopen[0]
            ):
            print('small_drop')
            position_new[asset_index]=max(-(90*avemean[0]/aveclose[0])*np.log(avemean[0]/1*avestd[0]),-8)
        #if  (LOW[0]<mean[0]-2*std[0]  and 
        #     HIGH[0] > mean[0]+2*std[0] and
        #     HIGH[0]-CLOSE[0]<std[0]):
        elif(avelow[0]>(avemean[0]-1.5*avestd[0])  and 
            avehigh[0] < (avemean[0]+1.5*avestd[0]) and
            (aveopen[0]+avehigh[0])<2.1*avemean[0] and
            (aveclose[0]+avelow[0])>1.9*avemean[0] and
            aveclose[0]>aveopen[0]
            ):
            print('small_rise')
            position_new[asset_index]=min((90*avemean[0]/aveclose[0])*np.log(avemean[0]/1*avestd[0]),8) # Use an alpha factor "log(high/low)" to control the position of BTC
            
        elif(avelow[0]<(avemean[0]-2*avestd[0])  and 
            avehigh[0] > (avemean[0]+2*avestd[0]) and
            (aveopen[0]+aveclose[0])<2*avemed[0] and
            #(aveopen[0]+avelow[0])<1.9*avemean[0] and
            #(aveclose[0]+avehigh[0])>2.1*avemean[0] and
            aveclose[0]<aveopen[0]
             ):
            print('large_drop')
            position_new[asset_index]=max(-(90*avemean[0]/aveclose[0])*np.log(avemean[0]/1*avestd[0]),-8)
            
        elif(avelow[0]<(avemean[0]-2*avestd[0])  and 
            avehigh[0] > (avemean[0]+2*avestd[0]) and
            (aveopen[0]+aveclose[0])>2*avemed[0]  and
            #(aveopen[0]+avehigh[0])>1.9*avemean[0] and
            #(aveclose[0]+avelow[0])<2.1*avemean[0] and
            aveclose[0]>aveopen[0]
            ):
            print('large_rise')
            position_new[asset_index]=min((90*avemean[0]/aveclose[0])*np.log(avemean[0]/1*avestd[0]),8)

            
            
        

            
        
        #position_new[asset_index]=-9
        position_change = position_new - position_current
        mask = np.abs(position_change) > .25*data[:,4]
        position_change[mask] = (.25*data[:,4]*np.sign(position_change))[mask]
        position_new = position_current + position_change
        average_price = np.mean(data[:, :4], axis=1)
        transaction_cost = np.sum(np.abs(position_change)*average_price*transaction)
        crypto_balance = np.sum(np.abs(position_new*average_price))
        cash_new=total_balance-crypto_balance-transaction_cost
        #print(position_new)
    #print(cash_new)
        if (cash_new<10000):
            position_new[asset_index]=np.sign(position_current[asset_index])*(abs(position_current[asset_index])/2) # When the operation on position will cause that the cash_balance is lower than 10000, this operation will be stop
            #print(position_new-position_new)
  
    else:
        memory.data_save.loc[(counter + 1) % bar_length - 1] = data[asset_index,:5]#####
    

    # End of strategy
    return position_new, memory