import asyncio
from crawler.engine import CrawlerEngine

async def main():
    # Initialize the engine with your database credentials
    crawler = CrawlerEngine(
            start_url="https://books.toscrape.com",  # A safe, multi-page test site
            db_host="localhost",
            db_user="root",
            db_password="Me@448262",             # Keep your password here
            db_name="sitepulse_db",
            max_pages=50,                            # Increased from 25
            max_depth=3                              # Increased from 2
        )
    
    print("[*] Starting SitePulse Concurrent Crawler...")
    await crawler.run()

if __name__ == "__main__":
    asyncio.run(main())