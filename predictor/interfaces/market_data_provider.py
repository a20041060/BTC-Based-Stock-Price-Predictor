from abc import ABC, abstractmethod
from typing import Optional, List
import pandas as pd
from predictor.domain.models import NewsItem

class IMarketDataProvider(ABC):
    """Interface for fetching market data."""
    
    @abstractmethod
    def get_realtime_btc_price(self) -> Optional[float]:
        """Fetches the current price of Bitcoin."""
        pass
        
    @abstractmethod
    def get_realtime_stock_price(self, ticker: str) -> Optional[float]:
        """Fetches the current price of a stock."""
        pass

    @abstractmethod
    def get_extended_stock_info(self, ticker: str) -> dict:
        """Fetches stock price with extended hours information."""
        pass
        
    @abstractmethod
    def get_historical_data(self, ticker: str, start_date: str) -> pd.DataFrame:
        """Fetches historical data for a stock and Bitcoin."""
        pass
        
    @abstractmethod
    def get_multiple_historical_data(self, tickers: List[str], start_date: str) -> pd.DataFrame:
        """Fetches historical data for multiple stocks."""
        pass
        
    @abstractmethod
    def get_news(self, ticker: str) -> List[NewsItem]:
        """Fetches news for a specific ticker."""
        pass

    @abstractmethod
    def get_fear_and_greed_index(self) -> Optional[dict]:
        """Fetches the Crypto Fear and Greed Index."""
        pass
