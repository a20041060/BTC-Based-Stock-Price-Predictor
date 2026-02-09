from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class NewsItem(BaseModel):
    """Represents a single news item."""
    title: str
    link: str
    provider: str
    date: str
    content: Optional[str] = None
    summary: Optional[str] = None

class SocialPost(BaseModel):
    """Represents a social media post (e.g., X.com tweet)."""
    id: str
    content: str
    author: str
    date: datetime
    likes: int = 0
    retweets: int = 0
    url: str
    platform: str = "X"

class SentimentResult(BaseModel):
    """Represents the result of sentiment analysis."""
    score: float
    label: str
    analyzed_items: List[Dict[str, Any]]

class StockData(BaseModel):
    """Represents historical stock data."""
    ticker: str
    dates: List[datetime]
    prices: List[float]

class PredictionResult(BaseModel):
    """Represents the result of a price prediction."""
    current_btc_price: float
    current_stock_price: float
    predicted_stock_price_beta: float
    predicted_stock_price_power_law: float
    beta: float
    correlation: float
