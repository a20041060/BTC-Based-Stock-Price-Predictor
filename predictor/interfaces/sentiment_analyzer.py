from abc import ABC, abstractmethod
from typing import List, Union
from predictor.domain.models import NewsItem, SocialPost, SentimentResult

class ISentimentAnalyzer(ABC):
    """Interface for sentiment analysis."""
    
    @abstractmethod
    def analyze(self, items: List[Union[NewsItem, SocialPost]]) -> SentimentResult:
        """Analyzes the sentiment of a list of news items or social posts."""
        pass
