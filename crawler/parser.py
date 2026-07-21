from bs4 import BeautifulSoup
from urllib.parse import urljoin

def get_links(html: str, base_url: str) -> list:
    """
    Parses HTML to extract all unique absolute URLs found in 'href' attributes.
    """
    soup = BeautifulSoup(html, 'html.parser')
    links = set()
    
    for tag in soup.find_all('a', href=True):
        full_url = urljoin(base_url, tag['href'])
        links.add(full_url)
        
    return list(links)
