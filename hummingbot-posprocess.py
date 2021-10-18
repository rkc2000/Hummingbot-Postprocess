from datetime import datetime, timedelta
import ccxt
import pandas as pd
import csv
import plotly.express as px
import plotly.graph_objects as go

# Enter/modify the following: 
exchange = ccxt.ascendex()
pair = 'JET/USDT'
start_time = datetime(2021, 10, 17, 4, 0, 00) #Year, Month, Day, Hour, Minute, Second
end_time = datetime(2021, 10, 17, 23, 0, 35)
trades_path = 'PATH TO/hummingbot_data/trades.csv'
candlestick_interval = '5m' #Increase according to time interval so that you are requesting no more than 1000 candlesticks.




# Fetching data from exchange
bars = exchange.fetch_ohlcv(pair, timeframe=candlestick_interval, limit=1000)
df_bars = pd.DataFrame(bars[:-1], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
df_bars['timestamp'] = pd.to_datetime(df_bars['timestamp'], unit='ms')
df_bars = df_bars[df_bars['timestamp'] > start_time]
df_bars = df_bars[df_bars['timestamp'] < end_time]

# Fetching local hummingbot trade data
df_trades = pd.read_csv(trades_path, skiprows = 1, names=['id','amount','base_asset','config_file_path','exchange_trade_id','leverage','market','order_id','order_type','position','price','quote_asset','strategy','symbol','timestamp','trade_fee','trade_type','age'])
df_trades['timestamp'] = pd.to_datetime(df_trades['timestamp'], unit='ms')
df_trades = df_trades[df_trades['timestamp'] > start_time]
df_trades = df_trades[df_trades['timestamp'] < end_time]

# Postprocessing
buy_trades = df_trades[df_trades['trade_type']=="BUY"]
sell_trades = df_trades[df_trades['trade_type']=="SELL"]
market_change = (df_bars['close'].iloc[-1] - df_bars['close'].iloc[0])/df_bars['close'].iloc[-1]*100 
avg_buy = sum(buy_trades['amount']*buy_trades['price'])/sum(buy_trades['amount'])
avg_sell = sum(sell_trades['amount']*sell_trades['price'])/sum(sell_trades['amount'])
avg_spread = avg_sell - avg_buy
n_buys = len(buy_trades.index)
n_sells = len(sell_trades.index)
trade_volume = sum(sell_trades['amount']*sell_trades['price']) + sum(buy_trades['amount']*buy_trades['price'])
trade_pnl = avg_spread*trade_volume/(2*df_bars['close'].iloc[-1])

#Plot buys and sells with price history 
fig1 = px.line(df_bars, x="timestamp", y="high")
fig2 = px.line(df_bars, x="timestamp", y="low")
fig3 = px.scatter(df_trades, x="timestamp", y="price", color="trade_type")
fig3.update_traces(marker=dict(size=12, line=dict(width=2, color='DarkSlateGrey')))
fig5 = go.Figure(data=fig1.data + fig2.data + fig3.data) 
fig5.show()

#Print statistics 
print("***********RUN STATISTICS*******************")
print("Pair:", pair, "  ", "Start:", start_time, "  ", "End:", end_time)
print("market change percent", market_change, "%")
print("average buy", avg_buy)
print("average sell", avg_sell)
print("average spread", avg_spread)
print("number of buys:", n_buys, ",", "number of sells:", n_sells)
print("trade pnl", trade_pnl)
print("trade volume", trade_volume)
print("pnl percent (pnl/trade vol)", trade_pnl/trade_volume*100, "%")



