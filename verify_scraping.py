import logging
import sys
from predictor.infrastructure.social_media_scraper import NitterScraperProvider

# Configure logging to see what's happening
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger("verify_scraping")

def verify():
    print("--- Verifying X.com Scraping ---")
    
    provider = NitterScraperProvider()
    
    # check if scraper is initialized
    if provider.scraper:
        print("✅ ntscraper library is loaded.")
        
        # Try to force a specific instance if auto-discovery failed
        # provider.scraper.instance = "https://nitter.privacydev.net" 
    else:
        print("❌ ntscraper library is NOT loaded (using mock).")
        return

    query = "Bitcoin"
    print(f"Attempting to scrape query: '{query}'...")
    
    try:
        posts = provider.get_posts(query, limit=3)
        
        if not posts:
            print("⚠️ No posts returned.")
            return

        print(f"✅ Retrieved {len(posts)} posts.")
        
        is_mock = False
        for post in posts:
            # Check for signatures of mock data from my implementation
            if "Simulated" in post.platform or "Mock tweet about" in post.content:
                is_mock = True
                break
        
        if is_mock:
            print("⚠️ Result contains MOCK data. Scraping likely failed or returned no results.")
        else:
            print("🎉 Result appears to be REAL data from X.com!")
            
        print("\n--- Sample Post ---")
        first_post = posts[0]
        print(f"Author: @{first_post.author}")
        print(f"Date: {first_post.date}")
        print(f"Content: {first_post.content[:100]}...")
        print(f"URL: {first_post.url}")

    except Exception as e:
        print(f"❌ Error during verification: {e}")

if __name__ == "__main__":
    verify()
