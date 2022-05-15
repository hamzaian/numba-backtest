import pandas as pd
import utils
import plotly.graph_objects as go

import numpy as np
#import matplotlib.pyplot as plt
import pandas_datareader as web
import pprint
from numba import jit,njit,vectorize

import datetime

pair = "EUR_USD"
granularity = "H4"
print("****PAIR:"), print(pair)
df = pd.read_pickle(utils.get_his_data_filename(pair, granularity))

non_cols = ['time', 'volume']
mod_cols = [x for x in df.columns if x not in non_cols]
df[mod_cols] = df[mod_cols].apply(pd.to_numeric)

df_wt = df[['time', 'volume', 'mid_o', 'mid_h', 'mid_l', 'mid_c', 'ask_h', 'ask_l','ask_c', 'bid_h', 'bid_l', 'bid_c']].copy()
# df_wt['time'] = datetime.datetime(df_wt['time']).strftime("%s")
# xprint(df_wt.dtypes)
print(df_wt.tail())
#-------------
df_wt['ap'] = (df_wt['mid_h'] + df_wt['mid_l'] + df_wt['mid_c'])/3

#df_wt.dropna(inplace=True)


def calculate_ema(prices, days, smoothing=2):
    ema = [sum(prices[:days]) / days]
    for price in prices[days:]:
        ema.append((price * (smoothing / (1 + days))) + ema[-1] * (1 - (smoothing / (1 + days))))
    return ema

n1=10
n2=21
#df_wt['esa'] = calculate_ema(df_wt['ap'], 10) # Add this line to save EMA values in a list
df_wt['esa'] = df_wt['ap'].ewm(span=n1, min_periods=n1).mean()


df_wt['d'] = (abs(df_wt['ap'] - df_wt['esa'])).ewm(span=n1, min_periods=n1).mean()
df_wt['ci'] = (df_wt['ap'] - df_wt['esa']) / (0.015 * df_wt['d'])
df_wt['tci'] = df_wt['ci'].ewm(span=n2, min_periods=n2).mean()
 
df_wt['wt1'] = df_wt['tci']
#df_wt['wt2'] = df_wt['wt1'].sma(window = 4).mean
df_wt['wt2'] = df_wt.wt1.rolling(window=4).mean()


df_wt['EMA_9'] = df_wt.mid_c.ewm(span=9).mean()
#df_wt['EMA_9'] = df_wt.mid_c.rolling(window = 9).ewm().mean()
'''if (df_wt.mid_c.rolling(window=15).max()) > (df_wt.mid_o.rolling(window=15).max()):
    df_wt['high'] = df_wt.mid_c.rolling(window=15).max()
else:
    df_wt['high'] = df_wt.mid_o.rolling(window=15).max()
if (df_wt.mid_o.rolling(window=15).max()) < (df_wt.mid_c.rolling(window=15).max()):
    df_wt['low'] = df_wt.mid_o.rolling(window=15).max()
else:
    df_wt['low'] = df_wt.mid_c.rolling(window=15).max()
'''
df_wt['high'] = df_wt.mid_h.rolling(window=15).max()

df_wt['low'] = df_wt.mid_l.rolling(window=15).min()


def is_trade(row):
    if row.wt2 > 0 and row.wt2_prev < 0 and row.mid_h >= row.high and (row.mid_c-row.mid_o)>0 and (((row.mid_h-row.mid_c)/row.mid_c)*1.3) < (((row.mid_o-row.mid_l)/row.mid_o)*1.0) and row.IS_TRADE_prev == 0:
        return 1
    elif row.wt2 < 0 and row.wt2_prev > 0 and row.mid_l <= row.low and (row.mid_c-row.mid_o)<0 and (((row.mid_h-row.mid_c)/row.mid_c)*1.0) > (((row.mid_o-row.mid_l)/row.mid_o)*1.3) and row.IS_TRADE_prev == 0:
        return -1
    elif row.wt2 > 13.1217 and row.wt2_prev < 13.1217 and row.mid_h >= row.high and (row.mid_c-row.mid_o)>0 and (((row.mid_h-row.mid_c)/row.mid_c)*1.3) < (((row.mid_o-row.mid_l)/row.mid_o)*1.0) and row.IS_TRADE_prev == 0:
        return 1
    elif row.wt2 < 13.1217 and row.wt2_prev > 13.1217 and row.mid_l <= row.low and (row.mid_c-row.mid_o)<0 and (((row.mid_h-row.mid_c)/row.mid_c)*1.0) > (((row.mid_o-row.mid_l)/row.mid_o)*1.3) and row.IS_TRADE_prev == 0:
        return -1
    #return 0

def open_trade(row):
    return 0

df_wt['wt2_prev'] = df_wt.wt2.shift(1)

df_wt['DIFF'] = df_wt.wt1 - df_wt.wt2
df_wt['IS_TRADE_prev'] = 0
df_wt['IS_TRADE'] = df_wt.apply(is_trade, axis=1)
df_wt['IS_TRADE_prev'] = df_wt.IS_TRADE.shift(1).fillna(0).astype(int)
df_wt['IS_TRADE'] = df_wt.apply(is_trade, axis=1)
#df_wt.dropna(inplace=True)

# df_trades_extract = df_wt[df_wt.IS_TRADE != 0].copy()
# df_trades = df_trades_extract[['time', 'mid_o', 'mid_h', 'mid_l', 'mid_c', 'wt1', 'wt2', 'high', 'low', 'wt2_prev', 'DIFF', 'IS_TRADE', 'IS_TRADE_prev']].copy()

#df_trades = df_wt[['time', 'mid_o', 'mid_h', 'mid_l', 'mid_c', 'wt1', 'wt2', 'high', 'low', 'wt2_prev', 'DIFF', 'IS_TRADE', 'IS_TRADE_prev']].copy()
#above line creates df with non trades as well
print(df_wt.head(45))
print(df_wt.tail(45))


def get_stop_loss(row):
    if row.IS_TRADE == 1:
        return (row.ask_c * 0.9995)
    elif row.IS_TRADE == -1:
        return (row.bid_c * 1.0005)
    else:
        #return None
        return None


def get_take_profit(row):
    if row.IS_TRADE == 1:
        return (row.ask_c * 1.0005)
    elif row.IS_TRADE == -1:
        return (row.bid_c * 0.9995)
    else:
        #return None
        return None

def get_entry_stop(row):
    if row.IS_TRADE == 1:
        return row.ask_c
    elif row.IS_TRADE == -1:
        return row.bid_c
    else:
        return None

def take_profit(direction, price):
    if direction == 1:
        return (price * 1.0005)
    elif direction == -1:
        return (price * 0.9995)
    
def stop_loss(direction, price):
    if direction == 1:
        return (price * 0.9995)
    elif direction == -1:
        return (price * 1.0005)



df_wt['ENTRY'] = df_wt.apply(get_entry_stop, axis=1)
df_wt['STOPLOSS'] = df_wt.apply(get_stop_loss, axis=1)
df_wt['TAKEPROFIT'] = df_wt.apply(get_take_profit, axis=1)

print ("111111111111111111111111111-----------------------------------------------------------================")
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


df_wt.reset_index(inplace=True)
print ("22222222222222222222222222222")

#----------------------------------------------------------------
'''
df_plot = df_wt.iloc[-5000:-3500].copy()

fig = go.Figure()
fig.add_trace(go.Candlestick(
    x=df_plot.time, open=df_plot.mid_o, high=df_plot.mid_h, low=df_plot.mid_l, close=df_plot.mid_c,
    line=dict(width=1), opacity=1,
    increasing_fillcolor='#24A06B',
    decreasing_fillcolor="#CC2E3C",
    increasing_line_color='#2EC886',  
    decreasing_line_color='#FF3A4C'
))
fig.update_layout(width=1000,height=400,
    margin=dict(l=10,r=10,b=10,t=10),
    font=dict(size=10,color="#e1e1e1"),
    paper_bgcolor="#1e1e1e",
    plot_bgcolor="#1e1e1e")
fig.update_xaxes(
    gridcolor="#1f292f",
    showgrid=True,fixedrange=True,rangeslider=dict(visible=True)
)
fig.update_yaxes(
    gridcolor="#1f292f",
    showgrid=True
)
fig.show()
'''
#----------------------------------------------------------------

open_trades = []
closed_trades = []
#----------------------------------------------------------------
'''
for index, row in df_wt.iterrows():
    for ot in open_trades:
        ot.update(row)
        if ot.stopped is not None:
            closed_trades.append(ot)
    
    open_trades = [x for x in open_trades if x.stopped is None]

    if row.IS_TRADE != 0:
        open_trades = [x for x in open_trades if x.running == True]
        open_trades.append(Trade(row))
'''
# @jit
def backtesting(row):
    global open_trades
    global closed_trades
    #ot = None
    for ot in open_trades:
        ot.update(row)
        if ot.stopped is not None:
            closed_trades.append(ot)
    
    open_trades = [x for x in open_trades if x.stopped is None]

    if row.IS_TRADE != 0:
        open_trades = [x for x in open_trades if x.running == True]
        open_trades.append(Trade(row))

    '''

    for ot in open_trades:
        ot.update(row)
        if ot.stopped is not None:
            closed_trades.append(ot)
    
    open_trades = [x for x in open_trades if x.stopped is None]

    if row.IS_TRADE != 0:
        open_trades = [x for x in open_trades if x.running == True]
        open_trades.append(Trade(row))
    '''
#----------------------------------------------------------------
print(df_wt)
conv = df_wt.to_numpy(na_value = -987654321)
print(conv)

print(type(conv))

np.save("wt.npy", conv)

print ("333333333333333333333333333333333333333333333")
df_wt.apply(backtesting, axis=1)


def account_grow():
    return 0

print ("4444444444444444444444444444444444444444444444")

df_trades = pd.DataFrame.from_dict([vars(x) for x in closed_trades])

df_trades.reset_index(inplace=True)
df_trades["duration"] = df_trades["stopped"] - df_trades["opened"]
df_trades["cum_duration"] = df_trades["duration"].cumsum()
df_trades["avg_duration"] = df_trades["cum_duration"]/(df_trades.index + 1)

print(df_trades.head(45))
print(df_trades.tail(45))

'''list_wrong = [(x,y) for (x,y) in df_trades.iterrows() if y.result>1]
df_wrong = pd.DataFrame(np.array(list_wrong).reshape(,3), columns = list("abc"))
'''
print("----WRONG_FIND")
def wrong_find(row):
    if row.result>1 or row.SL == 0 or row.result<-1 or row.TP == 0 or row.entry==0 :
        print(row)
    '''
    elif row.result<-1 or row.TP == 0:
        print(row)
    '''

#df_wrong = 
df_trades.apply(wrong_find, axis=1)
print("----------------------------------------------------")

#print(df_wrong)
print("----BIG WIN AND LOSSES_FIND")
def win_find(row):
    if row.result>0.1 and row.result<100:
        print(row)
    elif row.result<-0.1 and row.result>-100:
        print(row)
#df_trades.apply(win_find, axis=1)
print("----------------------------------------------------")


print("----big loss find")
def big_loss(row):
    if row.result<=-0.06:
        print(row)
df_trades.apply(big_loss, axis=1)

print("----------------------------------------------------")

'''
reguar_list = []
def regular_trades(row, reguar_list[]): 
    if row.TP != 0 and row.SL != 0 and row.result>=-0.07 and row.result<100:
    #if row.TP == 0 or row.SL == 0 or row.result<-0.07 or row.result>=100:
        regular_list.append(Trade(row))
        #df_trades.drop(index=row.index)

df_trades.apply(regular_trades, axis=1)
#df_trades.reset_index(inplace=True)

df_trades = pd.DataFrame.from_dict([vars(x) for x in regular_trades])

print(df_trades.head(45))
print(df_trades.tail(45))
'''

'''
print(df_regular.head(45))
print(df_regular.tail(45))
'''
print("----------------------------------------------------")

leverage = 20.0
print('RETURNS:')
print(df_trades.result.sum()*leverage)
#incorporate leverage directly into compounding of P/L
print("----------------------------------------------------")

#print(f"Duration from {df_wt[0].time} to {df_wt[-1].time}")
print('Max/Min results:')
print(df_trades.result.max())
print(df_trades.result.min())
print("----------------------------------------------------")

print("min SL:")
print(df_trades.SL.min())
print("min TP:")
print(df_trades.TP.min())
print("----------------------------------------------------")
