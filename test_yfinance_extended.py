
import yfinance as yf
import datetime
import pytz

def check_ticker(ticker_symbol):
    print(f"Checking {ticker_symbol}...")
    ticker = yf.Ticker(ticker_symbol)
    
    # Check fast_info
    print("Fast Info keys:", ticker.fast_info.keys())
    print(f"Last Price: {ticker.fast_info.get('lastPrice')}")
    
    # specific extended hours keys might not be in fast_info directly or named differently
    # common ones are 'preMarketPrice', 'postMarketPrice' in 'info' dict but 'info' is slow.
    # fast_info is better.
    
    # fast_info properties:
    # 'lastPrice', 'previousClose', 'open', 'dayHigh', 'dayLow', 'yearHigh', 'yearLow', 'lastVolume', 'averageVolume', 'marketCap', 'currency', 'exchange'
    
    # It seems fast_info is limited.
    # Let's check history with prepost=True
    
    # Get today's data with pre/post
    df = ticker.history(period="1d", interval="1m", prepost=True)
    if not df.empty:
        print("History (last 5 rows):")
        print(df.tail())
        last_index = df.index[-1]
        print(f"Last timestamp: {last_index}")
        
        # Check time to see if it's extended hours
        # NYSE is 9:30 - 16:00 ET
        
        tz = pytz.timezone('US/Eastern')
        now = datetime.datetime.now(tz)
        print(f"Current ET time: {now}")
        
    else:
        print("No history data found.")

check_ticker("COIN")
check_ticker("BTC-USD")
