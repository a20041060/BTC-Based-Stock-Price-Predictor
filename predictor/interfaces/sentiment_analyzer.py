from abc import ABC, abstractmethod
from typing import List
from predictor.domain.models import NewsItem, SentimentResult

class ISentimentAnalyzer(ABC):
    """Interface for sentiment analysis."""
    
    @abstractmethod
    def analyze(self, news_items: List[NewsItem]) -> SentimentResult:
        """Analyzes the sentiment of a list of news items."""
        pass
