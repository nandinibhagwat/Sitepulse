import aiohttp
import asyncio
import time
import socket  # Added for Windows networking stability
from crawler.parser import get_links
from urllib.parse import urlparse
from crawler.database import DatabaseManager
from bs4 import BeautifulSoup

class CrawlerEngine:
    # Added max_pages and max_depth with safe default values
    def __init__(self, start_url, db_host, db_user, db_password, db_name, max_pages=50, max_depth=3):
        self.start_url = start_url
        self.visited = set()
        self.queue = asyncio.Queue()
        self.semaphore = asyncio.Semaphore(5)
        
        self.max_pages = max_pages
        self.max_depth = max_depth
        self.pages_crawled = 0
        
        self.db = DatabaseManager(
            host=db_host,
            user=db_user,
            password=db_password,
            db=db_name
        )

    async def fetch(self, session, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # --- TIMEOUT FIX INCORPORATED HERE ---
        timeout = aiohttp.ClientTimeout(total=30)
        
        async with self.semaphore:
            try:
                start_time = time.perf_counter()
                
                # Using the timeout object instead of an integer
                async with session.get(url, headers=headers, timeout=timeout) as response:
                    html = None
                    if response.status == 200:
                        html = await response.text()
                    else:
                        print(f"Failed to fetch {url}: Status {response.status}")
                        
                    end_time = time.perf_counter()
                    response_time_ms = int((end_time - start_time) * 1000)
                    
                    return response.status, html, response_time_ms
                    
            except Exception as e:
                print(f"Error fetching {url}: {repr(e)}")
                
        return 0, None, 0
        
    def is_valid_url(self, url: str) -> bool:
        ignored_extensions = ('.zip', '.tgz', '.exe', '.asc', '.sigstore', '.json', '.msi', '.tar.gz', '.msix', '.apk', '.dmg', '.bin', '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.chm', '.tar', '.rar', '.7z', '.iso', '.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico', '.mp4', '.mp3', '.avi', '.wav')
        
        # --- Filter out non-landing page paths ---
        ignored_paths = ['/login', '/cart', '/checkout', '/admin', '/account', '/wp-admin', '/register']
        
        if url.lower().endswith(ignored_extensions):
            return False
            
        parsed_url = urlparse(url)
        
        # Check if the URL path contains any of the excluded strings
        for path in ignored_paths:
            if path in parsed_url.path.lower():
                return False
        # ----------------------------------------------
                
        target_domain = urlparse(self.start_url).netloc
        return parsed_url.netloc == target_domain or parsed_url.netloc == ''

    async def worker(self, session, worker_id):
        while True:
            # Wait for a URL from the queue
            current_url, current_depth = await self.queue.get()
            
            # Stop processing if we hit the limit, but mark task as done to drain the queue
            if self.pages_crawled >= self.max_pages:
                self.queue.task_done()
                continue
                
            print(f"[Worker {worker_id}] Crawling [Depth {current_depth}]: {current_url}")
            
            status, html, response_time_ms = await self.fetch(session, current_url)
            
            # --- SEO & ANALYTICS PARSING LOGIC ---
            page_title = "Missing Title"
            h1_present = False
            meta_desc = "Missing"  
            has_analytics = "None"  # Default is now a string instead of False
            
            if html:
                # EDGE CASE HANDLING: Wrap BeautifulSoup in a try/except in case of malformed HTML crashing the parser
                try:
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Extract the Title
                    title_tag = soup.find('title')
                    page_title = title_tag.string.strip() if title_tag and title_tag.string else "Missing Title"
                    
                    # Check for an H1 tag
                    h1_present = True if soup.find('h1') else False

                    # Extract Meta Description
                    meta_tag = soup.find('meta', attrs={'name': 'description'})
                    if meta_tag and meta_tag.get('content'):
                        meta_desc = meta_tag['content'].strip()
                        
                    # --- Upgraded Analytics & Pixel Detection ---
                    script_tags = soup.find_all('script')
                    tracking_types = []
                    
                    for script in script_tags:
                        content = script.string.lower() if script.string else ""
                        src = script.get('src', '').lower()
                        
                        # Google Tag Manager / Analytics
                        if 'gtm-' in content or 'gtm-' in src or 'google-analytics.com' in src:
                            if "Google" not in tracking_types: tracking_types.append("Google")
                            
                        # Meta / Facebook Pixel
                        if 'fbevents.js' in content or 'fbq(' in content:
                            if "Meta Pixel" not in tracking_types: tracking_types.append("Meta Pixel")
                            
                        # Google Ads Conversion Tracking
                        if 'aw-' in content or 'gtag(\'config\', \'aw-' in content:
                            if "Google Ads" not in tracking_types: tracking_types.append("Google Ads")

                    if tracking_types:
                        has_analytics = ", ".join(tracking_types)
                    # --------------------------------------------
                            
                except Exception as e:
                    print(f"[!] Error parsing HTML for {current_url}: {e}")

            # Passed ALL variables to the database manager
            await self.db.insert_health_data(current_url, status, response_time_ms, page_title, h1_present, meta_desc, has_analytics)
            
            # Formatted the print statement to show the analytics status
            print(f"[{status}] Recorded ({response_time_ms}ms) | Tracking: {has_analytics} | H1: {h1_present} | Desc: {meta_desc[:20]}...")
            
            self.pages_crawled += 1
            
            # Only parse and add new links if we haven't hit the max depth
            if html and current_depth < self.max_depth:
                links = get_links(html, current_url)
                for link in links:
                    if link not in self.visited and self.is_valid_url(link):
                        self.visited.add(link)
                        # Add the new link to the queue with incremented depth
                        await self.queue.put((link, current_depth + 1))
            
            # Notify the queue that the item has been fully processed
            self.queue.task_done()

    async def run(self):
        await self.db.connect()
        await self.db.init_db()
        
        # Queue now holds a tuple: (url, current_depth)
        await self.queue.put((self.start_url, 0))
        self.visited.add(self.start_url)
        
        try:
            # Force IPv4 to prevent Windows DNS hanging
            connector = aiohttp.TCPConnector(family=socket.AF_INET, ssl=False)
            
            async with aiohttp.ClientSession(connector=connector) as session:
                # Spawn 5 concurrent worker tasks (matches your semaphore limit)
                workers = [asyncio.create_task(self.worker(session, i)) for i in range(5)]
                
                # Wait until the queue is completely empty and all tasks are marked as done
                await self.queue.join()
                
                # Cancel the infinite worker loops once the queue is empty
                for w in workers:
                    w.cancel()
                    
        finally:
            await self.db.close()
            print(f"\n[+] Diagnostic complete! Crawled {self.pages_crawled} pages. Database connection closed.")