
def generate_bar(data):
    ## Data is a pandas dataframe
    import pandas as pd
    import numpy as np
    aaa=(data['open']+data['close']+data['high']+data['low'])/4
    ave_open=aaa[0]
    ave_close=aaa[len(data) - 1]
    ave_high=aaa.max()
    ave_low=aaa.min()
    ave_mean=aaa.mean()
    ave_med=np.median(aaa)
    ave_std=aaa.std()
    OHLC = pd.DataFrame(data = [[ave_open,ave_close,ave_high,ave_low,ave_mean,ave_std,ave_med]], 
                        columns = ['ave_open','ave_close','ave_high','ave_low','ave_mean','ave_std','ave_med'])

    return OHLC