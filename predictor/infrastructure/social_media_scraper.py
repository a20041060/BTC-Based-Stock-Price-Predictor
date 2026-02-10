import logging
import requests
from typing import List, Optional
from datetime import datetime
import random
from predictor.interfaces.social_media_provider import ISocialMediaProvider
from predictor.domain.models import SocialPost
from predictor.core.config import settings

logger = logging.getLogger(__name__)

class XApiProvider(ISocialMediaProvider):
    """
    Implementation of ISocialMediaProvider using the official X API (v2).
    """
    def __init__(self):
        self.bearer_token = settings.X_API_BEARER_TOKEN
        if not self.bearer_token:
            logger.warning("X_API_BEARER_TOKEN not set. Social media provider will return mock data.")

    def get_posts(self, query: str, limit: int = 10) -> List[SocialPost]:
        if not self.bearer_token:
            return self._get_mock_posts(query, limit)
        
        try:
            logger.info(f"Fetching posts from X API for query: {query}")
            
            # X API v2 Recent Search Endpoint
            url = "https://api.twitter.com/2/tweets/search/recent"
            
            # Minimum max_results is 10
            api_limit = max(10, min(limit, 100))
            
            params = {
                'query': f"{query} -is:retweet lang:en", # Basic filtering
                'max_results': api_limit,
                'tweet.fields': 'created_at,public_metrics,author_id',
                'expansions': 'author_id',
                'user.fields': 'username'
            }
            
            headers = {
                "Authorization": f"Bearer {self.bearer_token}",
                "User-Agent": "v2RecentSearchPython"
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code != 200:
                logger.error(f"X API Error: {response.status_code} - {response.text}")
                return self._get_mock_posts(query, limit)
            
            data = response.json()
            
            posts = []
            if 'data' in data:
                users = {u['id']: u['username'] for u in data.get('includes', {}).get('users', [])}
                
                for tweet in data['data']:
                    try:
                        author_id = tweet.get('author_id')
                        username = users.get(author_id, 'unknown')
                        tweet_id = tweet.get('id')
                        
                        # Parse date
                        # Format example: 2020-12-12T18:55:42.000Z
                        created_at_str = tweet.get('created_at')
                        try:
                            post_date = datetime.strptime(created_at_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                        except ValueError:
                            # Try without microseconds if needed or fallback
                            try:
                                post_date = datetime.strptime(created_at_str, "%Y-%m-%dT%H:%M:%SZ")
                            except:
                                post_date = datetime.now()

                        metrics = tweet.get('public_metrics', {})
                        
                        posts.append(SocialPost(
                            id=tweet_id,
                            content=tweet.get('text', ''),
                            author=username,
                            date=post_date,
                            likes=metrics.get('like_count', 0),
                            retweets=metrics.get('retweet_count', 0),
                            url=f"https://x.com/{username}/status/{tweet_id}",
                            platform="X"
                        ))
                    except Exception as e:
                        logger.error(f"Error parsing tweet object: {e}")
                        continue
            
            if not posts:
                logger.warning("No posts found from X API, returning mock to show something.")
                # We can return empty list or mock. Let's return empty if the API call worked but found nothing.
                # Actually, to avoid UI breakage or empty states in demo, mock might be safer if result is 0?
                # But user asked for API usage. Let's return real empty list if API works.
                return []
                
            return posts[:limit]
            
        except Exception as e:
            logger.error(f"Error calling X API: {e}")
            return self._get_mock_posts(query, limit)

    def _get_mock_posts(self, query: str, limit: int) -> List[SocialPost]:
        """Return mock data when scraping fails or library is missing."""
        logger.info(f"Returning mock social posts for query: {query}")
        
        templates = [
            f"Market sentiment for {query} is looking strong today! 🚀 #bullish",
            f"Not sure about {query} right now, volatility is high. 📉 #trading",
            f"Just bought more {query}, long term hold. 💎🙌",
            f"Technical analysis suggests a breakout for {query} soon.",
            f"Big news coming for {query}? Rumors circulating...",
            f"{query} moving with BTC, correlation is tight.",
            f"Watching {query} closely at these levels. Support holding?"
        ]
        
        return [
            SocialPost(
                id=str(i),
                content=random.choice(templates),
                author=f"trader_{random.randint(100, 999)}",
                date=datetime.now(),
                likes=random.randint(10, 500),
                retweets=random.randint(1, 100),
                url=f"https://x.com/mock_user/status/{i}",
                platform="X (Simulated)"
            )
            for i in range(limit)
        ]
