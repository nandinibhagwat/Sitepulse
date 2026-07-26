import asyncio
import argparse
import sys
from crawler.engine import CrawlerEngine

async def main():
    # 1. Set up the argument parser
    parser = argparse.ArgumentParser(
        description="SitePulse: PPC Landing Page & SEO Crawler",
        epilog="Example usage: python test_crawler.py https://example.com --pages 25 --depth 2"
    )
    
    # 2. Define the CLI arguments
    parser.add_argument("url", help="The target URL to audit (e.g., https://example.com)")
    parser.add_argument("--pages", type=int, default=50, help="Maximum number of pages to crawl (default: 50)")
    parser.add_argument("--depth", type=int, default=3, help="Maximum crawl depth (default: 3)")
    
    # Parse the arguments provided by the user in the terminal
    args = parser.parse_args()
    
    target_url = args.url
    max_pages = args.pages
    max_depth = args.depth
    
    print("\n========================================")
    print("         SITEPULSE CRAWLER BOOT         ")
    print("========================================\n")
    print(f"[*] Target URL: {target_url}")
    print(f"[*] Config: Max Pages = {max_pages} | Max Depth = {max_depth}\n")
    
    # 3. Database credentials
    db_host = 'localhost'
    db_user = 'root'
    db_password = 'Me@448262'
    db_name = 'sitepulse_db'
    
    # 4. Initialize the engine with CLI variables
    engine = CrawlerEngine(
        start_url=target_url,
        db_host=db_host,
        db_user=db_user,
        db_password=db_password,
        db_name=db_name,
        max_pages=max_pages,
        max_depth=max_depth
    )
    
    await engine.run()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())