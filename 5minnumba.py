from curses import tparm
from importlib.metadata import entry_points
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
print(data_load.shape) # [0] = 913 rows

data_load.resize(data_load.shape[0], (data_load.shape[1]+7))
print(data_load.shape) 

data_load[:,30] = 0
data_load[:,31] = 0
data_load[:,34] = 0
data_load[:,35] = 0

data_load[:,32] = -1
data_load[:,33] = -1

data_load[:,36] = -1



for i in range(455,463):
    print(data_load[i])
print(data_load[461])
column_names = ['0. index', '1. timestamp', '2. volume', 
'3. mid_o',    '4. mid_h',    '5. mid_l', '6. mid_c', '7. ask_h', '8. ask_l', '9. ask_c', '10. bid_h', '11. bid_l', '12. bid_c', 
'13. ap', '14. esa', '15. d', '16. ci', '17. tci', '18. wt1', '19. wt2', '20. EMA_9', '21. high'  '22. low', 
'23. wt2_prev', '24. DIFF',  '25. IS_TRADE_prev', '26. IS_TRADE ', '27. ENTRY', '28. STOPLOSS', '29. TAKEPROFIT'];

extra_columns = ['30. long P/L %', '31. short P/L %', '32. opened (index)', '33. closed(index)',    
'34. close P/L%',    '35. duration', '36. EXIT'];
#don't forget to add null values to all the extra_columns
# [23-30]
#row[n] to denote a cell when applying row-wise function 



global is_running
is_running = 0

#use these variables to store opened time and closed time for a trade
#then in closing candle store them in their respective columns along with P/L
#in the end, extract columns with non-null P/L values
global opened
global stopped
stopped = -1

global entry
global tp
global sl
tp = -1
sl = -1 
entry = -1

global trade_num
trade_num = 0

#make range start at 1 instead of 0 if you need previous row for some operation

#using candle index as proxy for duration at the moment

''' optimal way of applying numpy functions, should be able to do intercolumn functions too so long as same row?
x = np.array([1, 2, 3, 4, 5])
f = lambda x: x ** 2
squares = f(x)'''

# data_load
@jit
def backtesting():
    for i in range((data_load.shape[0])): 
        is_trade = data_load[i][25]
        long = ( (data_load[i][10]/entry)-1 )*100
        short = ( (data_load[i][8]/entry)-1 )*100
        #row.ask_l-self.entry)/self.entry)*100  <= -0.25
        if (is_trade != 0 ):
            # if(stopped == -1):
            #     stopped = data_load[i][0]
            #     if(is_running == 1):
            #         if():     #row.ask_l-self.entry)/self.entry)*100
            #     elif(is_running == -1):
            #         if():

            is_running = is_trade
            tp = data_load[i][29]
            sl = data_load[i][28]
            entry = data_load[i][27]

            opened = data_load[i][0]

            trade_num += 1

        if(is_running == 1):
            if(long >= .25 or data_load[i][10] <= sl or data_load[i][10] >= tp):
                is_running = 0
                stopped = data_load[i][0]
                data_load[i][35] = stopped - opened
                data_load[i][27] = entry 
                data_load[i][36] = data_load[i][10]
                data_load[i][34] = ((data_load[i][data_load][36]/entry) - 1)*100

                opened = -1
                stopped = -1
            

        elif(is_running == -1):
            if(short <= -.25 or data_load[i][8] >= sl or data_load[i][8] <= tp):
                is_running = 0
                stopped = data_load[i][0]
                data_load[i][32] = opened
                data_load[i][33] = stopped

                data_load[i][35] = stopped - opened
                data_load[i][27] = entry 
                data_load[i][36] = data_load[i][8]
                data_load[i][34] = (1 - (data_load[i][data_load][36]/entry))*100


                opened = -1
                stopped = -1
            #print(is_running)
        # if (is_trade == (-is_running)):
        #     is_running = False

# leverage = 20
# #sum column 34 and divide by trade_num and multiply by leverage
# avg_profit = 
# #just don't divide by ttrade_num`
# total_profit = 
# #sum duration and divide by trade_num 
# avg_duration = 
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