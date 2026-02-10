import yfinance as yf
import pandas as pd
import requests
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
import pytz
from predictor.interfaces.market_data_provider import IMarketDataProvider
from predictor.domain.models import NewsItem
from predictor.core.config import settings
from predictor.core.logger import get_logger

logger = get_logger(__name__)

class MarketDataProvider(IMarketDataProvider):
    """Concrete implementation of IMarketDataProvider using Yahoo Finance and Binance."""
    
    def get_realtime_btc_price(self) -> Optional[float]:
        try:
            response = requests.get(settings.BINANCE_BTC_URL, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return float(data["price"])
        except Exception as e:
            logger.warning(f"Binance API failed: {e}")
            
        # Fallback to yfinance
        return self._get_yfinance_price("BTC-USD")

    def get_realtime_stock_price(self, ticker: str) -> Optional[float]:
        # Try Finnhub if key exists
        if settings.FINNHUB_API_KEY:
            try:
                url = f"https://finnhub.io/api/v1/quote?symbol={ticker}&token={settings.FINNHUB_API_KEY}"
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    return float(data["c"])
            except Exception as e:
                logger.warning(f"Finnhub API failed: {e}")
        
        # Fallback to yfinance
        return self._get_yfinance_price(ticker)

    def get_extended_stock_info(self, ticker: str) -> Dict[str, Any]:
        """Fetches detailed stock info including pre/post market prices and previous close."""
        try:
            # Check for Crypto
            if ticker == "BTC-USD":
                # Try to get 24hr stats from Binance for price and previous close
                try:
                    response = requests.get("https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT", timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        price = float(data["lastPrice"])
                        prev_close = float(data["prevClosePrice"])
                        return {
                            "price": price,
                            "market_state": "OPEN", # Crypto is always open
                            "regular_market_price": price,
                            "pre_market_price": None,
                            "post_market_price": None,
                            "previous_close": prev_close
                        }
                except Exception as e:
                    logger.warning(f"Binance 24hr API failed: {e}")

                # Fallback
                price = self.get_realtime_btc_price()
                return {
                    "price": price,
                    "market_state": "OPEN", # Crypto is always open
                    "regular_market_price": price,
                    "pre_market_price": None,
                    "post_market_price": None,
                    "previous_close": None
                }

            # For Stocks
            t = yf.Ticker(ticker)
            # Use fast_info for basic data to ensure speed if info fails or is slow
            # But info is needed for pre/post.
            
            # Helper to check market hours
            tz = pytz.timezone('US/Eastern')
            now = datetime.now(tz)
            
            # Simple Market State Logic
            is_weekend = now.weekday() >= 5
            current_time = now.time()
            market_open = datetime.strptime("09:30", "%H:%M").time()
            market_close = datetime.strptime("16:00", "%H:%M").time()
            pre_start = datetime.strptime("04:00", "%H:%M").time()
            post_end = datetime.strptime("20:00", "%H:%M").time()
            
            market_state = "CLOSED"
            if not is_weekend:
                if market_open <= current_time <= market_close:
                    market_state = "OPEN"
                elif pre_start <= current_time < market_open:
                    market_state = "PRE"
                elif market_close < current_time <= post_end:
                    market_state = "POST"
            
            # Fetch Info
            try:
                info = t.info
                current_price = info.get('currentPrice') or info.get('regularMarketPrice')
                pre_price = info.get('preMarketPrice')
                post_price = info.get('postMarketPrice')
                previous_close = info.get('previousClose')
                
                # Try to use Yahoo's marketState if available
                yahoo_state = info.get('marketState')
                if yahoo_state:
                    if yahoo_state == "REGULAR":
                        market_state = "OPEN"
                    elif yahoo_state in ["PRE", "POST", "CLOSED"]:
                        market_state = yahoo_state
                
                # If info fetch worked, use it
                return {
                    "price": current_price,
                    "market_state": market_state,
                    "regular_market_price": info.get('regularMarketPrice'),
                    "pre_market_price": pre_price,
                    "post_market_price": post_price,
                    "previous_close": previous_close
                }
            except Exception as e:
                logger.warning(f"Failed to fetch full info for {ticker}, falling back to fast_info: {e}")
                
            # Fallback to fast_info if .info fails
            price = self._get_yfinance_price(ticker)
            return {
                "price": price,
                "market_state": market_state,
                "regular_market_price": price,
                "pre_market_price": None,
                "post_market_price": None,
                "previous_close": None
            }

        except Exception as e:
            logger.error(f"Error fetching extended info for {ticker}: {e}")
            return {
                "price": None,
                "market_state": "CLOSED",
                "error": str(e),
                "previous_close": None
            }

    def _get_yfinance_price(self, ticker: str) -> Optional[float]:
        try:
            t = yf.Ticker(ticker)
            if hasattr(t, "fast_info"):
                price = t.fast_info.get("last_price")
                if price:
                    return price
            
            data = t.history(period="1d")
            if not data.empty:
                return data["Close"].iloc[-1]
        except Exception as e:
            logger.error(f"Error fetching price for {ticker}: {e}")
        return None

    def get_historical_data(self, ticker: str, start_date: str) -> pd.DataFrame:
        try:
            tickers = [ticker, "BTC-USD"]
            # yf.download now returns MultiIndex columns by default for multiple tickers
            data = yf.download(tickers, start=start_date, progress=False)["Close"]
            
            # Flatten MultiIndex if necessary or handle it
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.droplevel(0)
                
            # Fallback logic if structure isn't as expected
            if ticker not in data.columns or "BTC-USD" not in data.columns:
                stock_data = yf.download(ticker, start=start_date, progress=False)["Close"]
                btc_data = yf.download("BTC-USD", start=start_date, progress=False)["Close"]
                data = pd.DataFrame({ticker: stock_data, "BTC-USD": btc_data})
                
            return data.dropna()
        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
            return pd.DataFrame()

    def get_multiple_historical_data(self, tickers: List[str], start_date: str) -> pd.DataFrame:
        try:
            data = yf.download(tickers, start=start_date, progress=False)["Close"]
            return data.dropna()
        except Exception as e:
            logger.error(f"Error fetching multiple historical data: {e}")
            return pd.DataFrame()

    def get_news(self, ticker: str) -> List[NewsItem]:
        try:
            t = yf.Ticker(ticker)
            raw_news = t.news
            news_items = []
            for item in raw_news:
                content = item.get("content", {})
                if not content:
                    content = item # Handle structure variations
                
                news_items.append(NewsItem(
                    title=content.get("title", "") or item.get("title", ""),
                    link=content.get("clickThroughUrl", {}).get("url", "#") if content.get("clickThroughUrl") else item.get("link", "#"),
                    provider=content.get("provider", {}).get("displayName", "Source") if content.get("provider") else item.get("publisher", "Source"),
                    date=content.get("pubDate", "")[:10] if content.get("pubDate") else str(item.get("providerPublishTime", "")),
                    summary=content.get("summary", "")
                ))
            return news_items
        except Exception as e:
            logger.error(f"Error fetching news for {ticker}: {e}")
            return []
