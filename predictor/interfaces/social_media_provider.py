from abc import ABC, abstractmethod
from typing import List
from predictor.domain.models import SocialPost

class ISocialMediaProvider(ABC):
    """Interface for social media data providers."""
    
    @abstractmethod
    def get_posts(self, query: str, limit: int = 10) -> List[SocialPost]:
        """
        Fetch posts related to a query (e.g., stock ticker).
        
        Args:
            query: The search query (e.g., "$AAPL", "Bitcoin").
            limit: Maximum number of posts to retrieve.
            
        Returns:
            List[SocialPost]: A list of social media posts.
        """
        pass
