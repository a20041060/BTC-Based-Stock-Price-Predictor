
import yfinance as yf
import json

def check_info(ticker_symbol):
    print(f"Checking info for {ticker_symbol}...")
    t = yf.Ticker(ticker_symbol)
    try:
        # Accessing .info forces a fetch
        info = t.info
        keys_of_interest = ['currentPrice', 'regularMarketPrice', 'preMarketPrice', 'postMarketPrice', 'previousClose', 'regularMarketOpen', 'regularMarketDayHigh', 'regularMarketDayLow', 'regularMarketVolume', 'marketState']
        filtered_info = {k: info.get(k) for k in keys_of_interest}
        print(json.dumps(filtered_info, indent=2))
    except Exception as e:
        print(f"Error fetching info: {e}")

check_info("COIN")
