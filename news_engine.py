import feedparser
import datetime

def fetch_outbreak_news():
    """
    Fetches real-time health alerts for Odisha using Google News RSS.
    Filters for critical keywords like 'outbreak', 'death', 'surge', etc.
    Returns the top critical headline or None.
    """
    # RSS Feed URL for Odisha Health News (last 7 days)
    rss_url = "https://news.google.com/rss/search?q=Odisha+Health+Disease+Outbreak+Dengue+Malaria+when:7d"
    
    try:
        feed = feedparser.parse(rss_url)
        
        # Keywords that indicate a critical situation
        critical_keywords = ["outbreak", "death", "surge", "alert", "panic", "emergency", "cases rise"]
        
        print(f"Fetching news from: {rss_url}")
        
        if not feed.entries:
            print("No news entries found.")
            return None

        for entry in feed.entries:
            title = entry.title.lower()
            # Check if any critical keyword is in the title
            if any(keyword in title for keyword in critical_keywords):
                print(f"CRITICAL NEWS FOUND: {entry.title}")
                return entry.title
                
        print("No critical news found.")
        return None

    except Exception as e:
        print(f"Error fetching news: {e}")
        return None

if __name__ == "__main__":
    # Test the function
    alert = fetch_outbreak_news()
    if alert:
        print(f"Alert: {alert}")
    else:
        print("No alerts.")
