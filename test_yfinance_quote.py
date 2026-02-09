import requests
import json

def check_quote(ticker):
    url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={ticker}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        result = data['quoteResponse']['result'][0]
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: {e}")

check_quote("COIN")
