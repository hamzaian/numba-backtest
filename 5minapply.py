import pandas as pd
import utils
import plotly.graph_objects as go

import numpy as np
#import matplotlib.pyplot as plt
import pandas_datareader as web
import pprint

pair = "NZD_USD"
granularity = "M5"

df = pd.read_pickle(utils.get_his_data_filename(pair, granularity))

non_cols = ['time', 'volume']
mod_cols = [x for x in df.columns if x not in non_cols]
df[mod_cols] = df[mod_cols].apply(pd.to_numeric)

df_wt = df[['time', 'volume', 'mid_o', 'mid_h', 'mid_l', 'mid_c', 'ask_h', 'ask_l','ask_c', 'bid_h', 'bid_l', 'bid_c']].copy()

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
    return 0

def open_trade(row):
    return 0

df_wt['wt2_prev'] = df_wt.wt2.shift(1)

df_wt['DIFF'] = df_wt.wt1 - df_wt.wt2
df_wt['IS_TRADE_prev'] = 0
df_wt['IS_TRADE'] = df_wt.apply(is_trade, axis=1)
df_wt['IS_TRADE_prev'] = df_wt.IS_TRADE.shift(1).fillna(0).astype(int)
df_wt['IS_TRADE'] = df_wt.apply(is_trade, axis=1)
df_wt.dropna(inplace=True)

df_trades_extract = df_wt[df_wt.IS_TRADE != 0].copy()
df_trades = df_trades_extract[['time', 'mid_o', 'mid_h', 'mid_l', 'mid_c', 'wt1', 'wt2', 'high', 'low', 'wt2_prev', 'DIFF', 'IS_TRADE', 'IS_TRADE_prev']].copy()
#df_trades = df_wt[['time', 'mid_o', 'mid_h', 'mid_l', 'mid_c', 'wt1', 'wt2', 'high', 'low', 'wt2_prev', 'DIFF', 'IS_TRADE', 'IS_TRADE_prev']].copy()
#above line creates df with non trades as well


def get_stop_loss(row):
    if row.IS_TRADE == 1:
        return (row.mid_c * 0.9995)
    elif row.IS_TRADE == -1:
        return (row.mid_c * 1.0005)
    else:
        return 0


def get_take_profit(row):
    if row.IS_TRADE == 1:
        return (row.mid_c * 1.0005)
    elif row.IS_TRADE == -1:
        return (row.mid_c * 0.9995)
    else:
        return 0

def get_entry_stop(row):
    if row.IS_TRADE == 1:
        return row.ask_c
    elif row.IS_TRADE == -1:
        return row.bid_c
    else:
        return 0


df_wt['ENTRY'] = df_wt.apply(get_entry_stop, axis=1)
df_wt['STOPLOSS'] = df_wt.apply(get_stop_loss, axis=1)
df_wt['TAKEPROFIT'] = df_wt.apply(get_take_profit, axis=1)

class Trade():
    def __init__(self, row):
        self.candle_date = row.time
        self.direction = row.IS_TRADE
        self.entry = row.ENTRY
        self.exit = None
        self.TP = row.TAKEPROFIT
        self.SL = row.STOPLOSS
        self.running = False
        self.result = None
        self.stopped = None
        self.breakeven = False
        

    def update(self, row):
        if self.running == True:
            self.update_result(row)
        else:
            self.check_entry(row)    
    
    def check_entry(self, row):
        if self.direction == 1  or self.direction == -1:
            self.index = row.name
            self.opened = row.time
            self.running = True

    def update_result(self, row):
        if self.direction == 1:
            if (row.bid_h-self.entry)!=0 and self.entry!=0:
                if (((row.bid_h-self.entry)/self.entry)*100) >= .25 :
                    self.result = ( (self.TP-self.entry)/self.entry )*100
            elif row.bid_h >= self.TP:
                row.IS_TRADE = self.direction
                self.TP = row.TAKEPROFIT
            elif row.bid_l <= self.SL:
                self.result = ( (self.SL-self.entry)/self.entry )*100
                
            elif row.bid_c <= self.entry and self.breakeven == True:
                self.result = 0.0
            elif self.entry!=0 and (( (row.bid_c-self.entry)/self.entry )*100) >= 0.05:
                #self.breakeven = False
                self.breakeven = True

        elif self.direction == -1:
            if (row.ask_l-self.entry)!=0 and self.entry!=0:
                if (((row.ask_l-self.entry)/self.entry)*100) <= -.25 :
                    self.result = -((self.TP-self.entry)/self.entry)*100
            if row.ask_l <= self.TP:
                row.IS_TRADE = self.direction
                self.TP = row.TAKEPROFIT
            elif row.ask_h >= self.SL and self.entry!=0:
                self.result = ( (self.entry-self.SL)/self.entry )*100

            elif row.ask_c >= self.entry and self.breakeven == True:
                self.result = 0.0
            elif self.entry!=0 and (((row.ask_c-self.entry)/self.entry)*100) <= -0.05:
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

open_trades = []
closed_trades = []
def test_trades(row, open_trades, closed_trades):
#for index, row in df_wt.iterrows():
    for ot in open_trades:
        ot.update(row)
        if ot.stopped is not None:
            closed_trades.append(ot)
    
    open_trades = [x for x in open_trades if x.stopped is None]

    if row.IS_TRADE != 0:
        open_trades = [x for x in open_trades if x.running == True]
        open_trades.append(Trade(row))
        return open_trades, closed_trades

#df_wt.apply(test_trades(row,open_trades, closed_trades), axis=1)
for i in range(len(df_wt)):
    row = df_wt.iloc[i]
    open_trades, closed_trades = test_trades(row, open_trades, closed_trades)
'''
for row in df_wt:
    #open_trades, closed_trades = test_trades(row, open_trades, closed_trades)
    result = [(x) for x in df['col']]
'''
def account_grow():
    return 0

df_trades = pd.DataFrame.from_dict([vars(x) for x in closed_trades])

df_trades.reset_index(inplace=True)
df_trades["duration"] = df_trades["stopped"] - df_trades["opened"]
df_trades["cum_duration"] = df_trades["duration"].cumsum()
df_trades["avg_duration"] = df_trades["cum_duration"]/(df_trades.index + 1)

print(df_trades.head())
print(df_trades.tail())

'''list_wrong = [(x,y) for (x,y) in df_trades.iterrows() if y.result>1]
df_wrong = pd.DataFrame(np.array(list_wrong).reshape(,3), columns = list("abc"))
'''
def wrong_find(row):
    if row.result>1:
        print(row)
    elif row.result<-1:
        print(row)

#df_wrong = 
df_trades.apply(wrong_find, axis=1)
#print(df_wrong)

def win_find(row):
    if row.result>0.1 and row.result<100:
        print(row)
    elif row.result<-0.1 and row.result<100:
        print(row)
df_trades.apply(win_find, axis=1)

leverage = 20.0
print('RETURNS:')
print(df_trades.result.sum()*leverage)
#incorporate leverage directly into compounding of P/L

print(df_trades.result.max())