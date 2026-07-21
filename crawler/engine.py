import aiohttp
import asyncio
import time
from crawler.parser import get_links
from urllib.parse import urlparse
from crawler.database import DatabaseManager

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
        async with self.semaphore:
            try:
                start_time = time.perf_counter()
                
                async with session.get(url, headers=headers, timeout=10) as response:
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
        
        if url.lower().endswith(ignored_extensions):
            return False
            
        target_domain = urlparse(self.start_url).netloc
        parsed_url = urlparse(url)
        return parsed_url.netloc == target_domain or parsed_url.netloc == ''

    async def run(self):
        await self.db.connect()
        await self.db.init_db()
        
        # Queue now holds a tuple: (url, current_depth)
        await self.queue.put((self.start_url, 0))
        self.visited.add(self.start_url)
        
        try:
            async with aiohttp.ClientSession() as session:
                while not self.queue.empty():
                    # Stop if we hit the page limit
                    if self.pages_crawled >= self.max_pages:
                        print(f"\n[!] Reached max_pages limit ({self.max_pages}). Stopping crawl.")
                        break
                        
                    # Unpack the URL and its depth from the queue
                    current_url, current_depth = await self.queue.get()
                    print(f"Crawling [Depth {current_depth}]: {current_url}")
                    
                    status, html, response_time_ms = await self.fetch(session, current_url)
                    
                    await self.db.insert_health_data(current_url, status, response_time_ms)
                    print(f"[{status}] Recorded health ({response_time_ms}ms) for: {current_url}")
                    
                    self.pages_crawled += 1
                    
                    # Only parse and add new links if we haven't hit the max depth
                    if html and current_depth < self.max_depth:
                        links = get_links(html, current_url)
                        for link in links:
                            if link not in self.visited and self.is_valid_url(link):
                                self.visited.add(link)
                                # Add the new link to the queue with incremented depth
                                await self.queue.put((link, current_depth + 1))
                    
                    self.queue.task_done()
                    
        finally:
            await self.db.close()
            print(f"\n[+] Diagnostic complete! Crawled {self.pages_crawled} pages. Database connection closed.")