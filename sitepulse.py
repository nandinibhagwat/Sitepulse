import asyncio
import argparse
import sys
import time
from engine import CrawlerEngine # Assuming your crawler class is in engine.py
from report import generate_report

async def main():
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description="SitePulse: SEO & PPC Diagnostic Crawler")
    parser.add_argument("url", help="The starting URL to crawl (e.g., https://example.com)")
    parser.add_argument("--pages", type=int, default=50, help="Maximum number of pages to crawl (default: 50)")
    parser.add_argument("--depth", type=int, default=3, help="Maximum crawl depth (default: 3)")
    
    args = parser.parse_args()
    
    # Database credentials (keep these matching your local setup)
    DB_HOST = "localhost"
    DB_USER = "root"
    DB_PASS = "Me@448262"
    DB_NAME = "sitepulse_db"

    print("\n" + "="*50)
    print(f"🚀 INITIALIZING SITEPULSE FOR: {args.url}")
    print("="*50 + "\n")

    start_time = time.time()

    # Step 1: Initialize and run the crawler
    crawler = CrawlerEngine(
        start_url=args.url,
        db_host=DB_HOST,
        db_user=DB_USER,
        db_password=DB_PASS,
        db_name=DB_NAME,
        max_pages=args.pages,
        max_depth=args.depth
    )
    
    print("[*] Starting diagnostic crawl...")
    await crawler.run()
    
    # Step 2: Generate the report
    print("\n[*] Compiling diagnostic data...")
    await generate_report()
    
    elapsed_time = round(time.time() - start_time, 2)
    print(f"\n[+] Total Execution Time: {elapsed_time} seconds.")
    print("="*50 + "\n")

if __name__ == "__main__":
    # Windows loop policy fix
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[-] Process interrupted by user. Exiting...")