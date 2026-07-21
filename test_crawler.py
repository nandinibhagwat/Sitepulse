import asyncio
import sys
from crawler.engine import CrawlerEngine

async def main():
    # 1. Define your target and MySQL credentials
    start_url = "https://www.python.org"       # You can change this to any URL you want to test
    db_host = "localhost"                      # Usually 'localhost' or '127.0.0.1'
    db_user = "root"                           # Your MySQL username
    db_password = "Me@448262"                  # IMPORTANT: Replace with your actual MySQL password
    db_name = "sitepulse_db"                   # The database you want to use
    
    # 2. Define your crawler constraints
    max_pages = 20                             # Stop after scraping this many pages
    max_depth = 2                              # How many clicks deep the crawler is allowed to go
    
    print(f"[*] Starting crawler on: {start_url}")
    print(f"[*] Limits set -> Max Pages: {max_pages} | Max Depth: {max_depth}")
    
    # 3. Initialize the engine with your database credentials and constraints
    engine = CrawlerEngine(
        start_url=start_url,
        db_host=db_host,
        db_user=db_user,
        db_password=db_password,
        db_name=db_name,
        max_pages=max_pages,
        max_depth=max_depth
    )
    
    # 4. Run the crawler
    await engine.run()
    print("[+] Crawling complete.")

if __name__ == "__main__":
    # This ensures the script runs gracefully on Windows without throwing RuntimeErrors
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    asyncio.run(main())