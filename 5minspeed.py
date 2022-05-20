from curses import tparm
from importlib.metadata import entry_points
from random import randint
import pandas as pd
import utils
import plotly.graph_objects as go

import numpy as np
#import matplotlib.pyplot as plt
import pandas_datareader as web
import pprint
from numba import jit,njit,vectorize
import random


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


data_load[:,30] = 0.0
data_load[:,31] = 0.0
data_load[:,34] = 0.00000000000
data_load[:,35] = 0.0

data_load[:,32] = -1.0
data_load[:,33] = -1.0

data_load[:,36] = -1.0


for i in range(455,463):
    print(data_load[i])
column_names = ['0. index', '1. timestamp', '2. volume', 
'3. mid_o',    '4. mid_h',    '5. mid_l', '6. mid_c', '7. ask_h', '8. ask_l', '9. ask_c', '10. bid_h', '11. bid_l', '12. bid_c', 
'13. ap', '14. esa', '15. d', '16. ci', '17. tci', '18. wt1', '19. wt2', '20. EMA_9', '21. high'  '22. low', 
'23. wt2_prev', '24. DIFF',  '25. IS_TRADE_prev', '26. IS_TRADE ', '27. ENTRY', '28. STOPLOSS', '29. TAKEPROFIT'];

extra_columns = ['30. long P/L %', '31. short P/L %', '32. opened (index)', '33. closed(index)',    
'34. close P/L%',    '35. duration', '36. EXIT'];


''' optimal way of applying numpy functions, should be able to do intercolumn functions too so long as same row?
x = np.array([1, 2, 3, 4, 5])
f = lambda x: x ** 2
squares = f(x)'''
size = data_load.shape[0]
print (size)   
# data_load
# @njit
def backtesting():
    is_running = 0.0
    stopped = -1.0
    tp = -1.0
    sl = -1.0
    global entry
    entry = -1.0
    global trade_num
    trade_num = 0.0
    global opened


    for i in range(size): 
        is_trade = data_load[i][25]
        long = ( (data_load[i][10]/entry)-1 )*100
        short = ( (data_load[i][8]/entry)-1 )*100
        #row.ask_l-self.entry)/self.entry)*100  <= -0.25
        if(data_load[i][9] == 1.13127):
            print (data_load[i])

        if (is_trade != 0.0 and is_running == 0.0):
            # if(stopped == -1):
            #     stopped = data_load[i][0]
            #     if(is_running == 1):
            #         if():     #row.ask_l-self.entry)/self.entry)*100
            #     elif(is_running == -1):
            #         if():

            is_running = is_trade
            tp = data_load[i][29]
            sl = data_load[i][28]
            # entry = data_load[i][27]
            if(is_trade == 1.0):
                entry = data_load[i][9]
            else:
                entry = data_load[i][12]

            opened = data_load[i][0]

            trade_num += 1.0

        if(is_running == 1.0):
            if(long >= .25 or (data_load[i][10] <= sl) or (data_load[i][10] >= tp)):
            # switch = random.randint(0,1)
            # if((data_load[i][10] <= sl) or (data_load[i][10] >= tp)):
                is_running = 0.0
                stopped = data_load[i][0]
                data_load[i][35] = stopped - opened
                data_load[i][27] = entry 
                data_load[i][36] = data_load[i][10]
                data_load[i][34] = ((data_load[i][36]/entry) - 1)*100
                print (entry)
                print(data_load[i][36])
                print(data_load[i][34])

                print(opened)
                print(stopped)
                print("\n")

                opened = -1.0
                stopped = -1.0
            

        elif(is_running == -1.0):
            switch = random.randint(0,1)
            # if()
            # if(short <= -.25 or (data_load[i][8] >= sl) or (data_load[i][8] <= tp)):
            if((data_load[i][8] >= sl) or (data_load[i][8] <= tp)):

                is_running = 0.0
                stopped = data_load[i][0]
                data_load[i][32] = opened
                data_load[i][33] = stopped

                data_load[i][35] = stopped - opened
                data_load[i][27] = entry 
                data_load[i][36] = data_load[i][8]
                data_load[i][34] = (1 - (data_load[i][36]/entry))*100
                print (entry)
                print(data_load[i][36])
                print(data_load[i][34])

                print(opened)
                print(stopped)
                print("\n")

                opened = -1.0
                stopped = -1.0
            #print(is_running)
        # if (is_trade == (-is_running)):
        #     is_running = False
backtesting()


# for i in range(size):
#     print(data_load[i])

leverage = 20
print(trade_num)
# #sum column 34 and divide by trade_num and multiply by leverage
# avg_profit = 
# #just don't divide by ttrade_num`
total_profit = data_load[:, 34].sum()
print("total_profit  =  ", total_profit*leverage)

    # for i in data_load[:,34]:
    #     if (i < 0):
    #         print(i)
# if(data_load[:, 35] != 0):
#     print(data_load[:, 35])4
