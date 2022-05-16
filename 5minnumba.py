import pandas as pd
import utils
import plotly.graph_objects as go

import numpy as np
#import matplotlib.pyplot as plt
import pandas_datareader as web
import pprint
from numba import jit,njit,vectorize


np.set_printoptions(precision=None, threshold=None, edgeitems=12, linewidth=None, suppress=None, nanstr=None, infstr=None, formatter=None, sign=None, floatmode=None, legacy=None);


# data_load = np.load("wt.npy", mmap_mode=None, allow_pickle=True, fix_imports=True, encoding='ASCII')
# data_load.set_printoptions(precision=None,suppress=None);
while True:
    # pickled_function = pickle.dumps(function)
    try:
        data_load = np.load("wt.npy", mmap_mode=None, allow_pickle=True, fix_imports=True, encoding='ASCII')
    except:
        print("Failed to load")
    else:
        break

# data_load.shape = (913,30)
print(data_load.shape[0]) # = 913 rows

global is_running
is_running = 0
#make range start at 1 instead of 0 if you need previous row for some operation

#using candle index as proxy for duration at the moment
for i in range((data_load.shape[0] + 1)): 
    is_trade = data_load[i][25]
    if (is_trade != 0 ):
        is_running = is_trade
    if()
        #print(is_running)
    # if (is_trade == (-is_running)):
    #     is_running = False

    pass

# for i in range(455,463):
#     print(data_load[i])
# print(data_load[461])
column_names = ['0. index', '1. timestamp', '2. volume', 
'3. mid_o',    '4. mid_h',    '5. mid_l', '6. mid_c', '7. ask_h', '8. ask_l', '9. ask_c', '10. bid_h', '11. bid_l', '12. bid_c', 
'13. ap', '14. esa', '15. d', '16. ci', '17. tci', '18. wt1', '19. wt2', '20. EMA_9', '21. high'  '22. low', 
'23. wt2_prev', '24. DIFF',  '25. IS_TRADE_prev', '26. IS_TRADE ', '27. ENTRY', '28. STOPLOSS', '29. TAKEPROFIT'];

extra_columns = ['0. index', '1. timestamp', '2. volume', '3. mid_o',    '4. mid_h',    '5. mid_l', '6. mid_c', '7. ask_h']
# [23-30]
#row[n] to denote a cell when applying row-wise function 


'''
def my_func(a):

    """Average first and last element of a 1-D array"""

    return (a[0] + a[-1]) * 0.5

b = np.array([[1,2,3], [4,5,6], [7,8,9]])

np.apply_along_axis(my_func, 0, b)
array([4., 5., 6.])

np.apply_along_axis(my_func, 1, b)
array([2.,  5.,  8.])
'''

class Trade():  
    def __init__(self, row):
        self.candle_date = row.time
        self.direction = row.IS_TRADE
        self.entry = row.ENTRY
        self.exit = None
        self.TP = row.TAKEPROFIT
        self.SL = row.STOPLOSS
        self.running = True
        self.result = None
        self.index = row.name
        self.opened = row.time
        self.stopped = None
        self.breakeven = False

    def update(self, row):
        #if self.running == True:
        #if self.running == True and self.direction != 0:
        if self.running == True:

            self.update_result(row)
        '''else:
            self.check_entry(row)'''  
    '''
    def check_entry(self, row):
        if self.direction == 1 or self.direction == -1:
            self.index = row.name
            self.opened = row.time
            self.running = True
    '''
    def update_result(self, row):
        #if self.entry!=0:

        if self.direction == 1:
            
            #(row.bid_h-self.entry)!=0 and 
            '''if (((self.entry-row.bid_l)/self.entry)*100) > 0.05 :
                self.result = -0.05'''
            #if row.bid_l <= self.SL:
                #self.result = ( (self.SL-self.entry)/self.entry )*100
            #this was elif
            if (((row.bid_h-self.entry)/self.entry)*100) >= 0.25 :
                self.result = ( (self.TP-self.entry)/self.entry )*100
            #everything below first statement was originally elif
            #elif row.bid_l <= self.SL:
                #self.result = ( (self.SL-self.entry)/self.entry )*100
            elif row.bid_h >= self.TP:
                #row.IS_TRADE = self.direction
                self.TP = take_profit(self.direction, self.TP)
                self.SL = stop_loss(self.direction, self.TP)
        
            #this was if
            elif row.bid_l <= self.SL:
                self.result = ( (self.SL-self.entry)/self.entry )*100
            elif row.bid_c <= self.entry and self.breakeven == True:
                self.result = 0.0
            elif (( (row.bid_c-self.entry)/self.entry )*100) >= 0.05:
                #self.breakeven = False
                self.breakeven = True

        elif self.direction == -1:
            #(row.ask_l-self.entry)!=0 and 
            #if row.ask_h >= self.SL:
                #self.result = ( (self.entry-self.SL)/self.entry )*100
            #above if statement is new
            if (((row.ask_l-self.entry)/self.entry)*100) <= -0.25 :
                self.result = -((self.TP-self.entry)/self.entry)*100
            #el
            elif row.ask_l <= self.TP:
                #row.IS_TRADE = self.direction
                self.TP = take_profit(self.direction, self.TP)
                self.SL = stop_loss(self.direction, self.TP)
            #if
            elif row.ask_h >= self.SL:
                self.result = ( (self.entry-self.SL)/self.entry )*100
            elif row.ask_c >= self.entry and self.breakeven == True:
                self.result = 0.0
            elif (((row.ask_c-self.entry)/self.entry)*100) <= -0.05:
                #self.breakeven = False
                self.breakeven = True
        '''else:
            print ("direction is 0 error")'''

        if self.result is not None:
            self.running = False
            self.stopped = row.time
            if self.direction == 1:
                self.exit = row.bid_c
            elif self.direction == -1:
                self.exit = row.ask_c


# df_wt.reset_index(inplace=True)    
#don't need to reset index, but maybe just delete rows with N/A values in last column
#this is not necessary since we can simply check if the last value is the fill = -987654321

# open_trades = []
# closed_trades = []
# #----------------------------------------------------------------
# '''
# for index, row in df_wt.iterrows():-
#     for ot in open_trades:
#         ot.update(row)
#         if ot.stopped is not None:
#             closed_trades.append(ot)
    
#     open_trades = [x for x in open_trades if x.stopped is None][2022-05-13T]

#     if row.IS_TRADE != 0:
#         open_trades = [x for x in open_trades if x.running == True]
#         open_trades.append(Trade(row))
# '''

# # @jit
# def backtesting(row):
#     global open_trades
#     global closed_trades
#     #ot = None
#     for ot in open_trades:
#         ot.update(row)
#         if ot.stopped is not None:
#             closed_trades.append(ot)
    
#     open_trades = [x for x in open_trades if x.stopped is None]

#     if row.IS_TRADE != 0:
#         open_trades = [x for x in open_trades if x.running == True]
#         open_trades.append(Trade(row))