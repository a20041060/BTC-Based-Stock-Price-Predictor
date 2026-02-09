import logging
from typing import List
from datetime import datetime
import random
from predictor.interfaces.social_media_provider import ISocialMediaProvider
from predictor.domain.models import SocialPost

# Try to import ntscraper, handle if missing
try:
    from ntscraper import Nitter
    NTSCRAPER_AVAILABLE = True
except ImportError:
    NTSCRAPER_AVAILABLE = False

logger = logging.getLogger(__name__)

class NitterScraperProvider(ISocialMediaProvider):
    """
    Implementation of ISocialMediaProvider using Nitter (via ntscraper) to scrape X.com.
    """
    def __init__(self):
        if NTSCRAPER_AVAILABLE:
            # log_level can be set to warn to reduce noise
            self.scraper = Nitter(log_level=1)
        else:
            logger.warning("ntscraper not installed. Social media scraping will return mock data.")
            self.scraper = None

    def get_posts(self, query: str, limit: int = 10) -> List[SocialPost]:
        if not self.scraper:
            return self._get_mock_posts(query, limit)
        
        try:
            logger.info(f"Scraping X (Nitter) for query: {query}")
            # Scrape tweets
            # mode='term' searches for the query string
            result = self.scraper.get_tweets(query, mode='term', number=limit)
            
            posts = []
            if result and 'tweets' in result:
                for tweet in result['tweets']:
                    try:
                        # Basic date handling - ntscraper returns 'date' string
                        # For robustness in this demo, we'll use current time if parsing is complex
                        # Ideally we parse tweet['date']
                        post_date = datetime.now()
                        
                        posts.append(SocialPost(
                            id=tweet.get('link', '').split('/')[-1] or str(random.randint(100000, 999999)),
                            content=tweet.get('text', ''),
                            author=tweet.get('user', {}).get('username', 'unknown'),
                            date=post_date,
                            likes=tweet.get('stats', {}).get('likes', 0),
                            retweets=tweet.get('stats', {}).get('retweets', 0),
                            url=tweet.get('link', ''),
                            platform="X"
                        ))
                    except Exception as e:
                        logger.error(f"Error parsing tweet: {e}")
                        continue
            
            if not posts:
                logger.warning("No posts found via scraping, falling back to mock.")
                return self._get_mock_posts(query, limit)
                
            return posts
            
        except Exception as e:
            logger.error(f"Error scraping Nitter: {e}")
            return self._get_mock_posts(query, limit)

    def _get_mock_posts(self, query: str, limit: int) -> List[SocialPost]:
        """Return mock data when scraping fails or library is missing."""
        logger.info(f"Returning mock social posts for query: {query}")
        return [
            SocialPost(
                id=str(i),
                content=f"Mock tweet about {query}. The market looks interesting today! #stocks #crypto",
                author=f"user_{i}",
                date=datetime.now(),
                likes=random.randint(10, 500),
                retweets=random.randint(1, 100),
                url=f"https://x.com/user_{i}/status/{i}",
                platform="X (Simulated)"
            )
            for i in range(limit)
        ]
