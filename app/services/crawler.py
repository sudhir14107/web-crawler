import json
import re
import threading
import time
from queue import Queue
from urllib.parse import urlparse, urljoin, urlsplit
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from app.core.config import Config

class CrawlerService:
    def __init__(self):
        self.queue = Queue()
        self.visited = set()
        self.original_url = set()
        self.results = {}
        
        # Load environment variables
        self.max_time_page = Config.MAX_TIME_PAGE
        self.sleep_time = 60
        self.max_threads = Config.MAX_THREADS
        self.max_time_per_scroll = 5 * 60
        
        # Thread-safe lock
        self.lock = threading.Lock()

        # Selenium WebDriver setup
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        
        print("CrawlerService initialized successfully")

    def crawl_page(self, url):
        try:
            print(f"Starting to crawl: {url}")
            self.driver.get(url)
            # Wait for the page to load (max 1 minute)
            print(f"Waiting for 10 seconds to allow the page to load: {url}")
            time.sleep(10)
            
            # Scroll the page for 1 minute to load all content (in case of infinite scrolling)
            end_time = time.time() + 10  # 1 minute from now
            while time.time() < end_time:
                self.driver.execute_script("window.scrollBy(0, 500);")
                time.sleep(3)  # Wait for content to load

            # Retrieve all <a> tags on the page
            links = self.driver.find_elements(By.TAG_NAME, "a")
            print(f"\nFound {len(links)} links on {url}:")
            # Filter out only the first 10 links
            limited_links = links[:100]  # Only take the first 10 links
            
            # Process these limited links
            self.process_page(limited_links)

        except Exception as e:
            print(f"Error processing {url}: {e}")
            
    def is_product_url(self, href):
        """Check if the URL is a product page using regex."""
        product_patterns = [r"/p/", r"/dp/", r"/product/"]
        return any(re.search(pattern, href) for pattern in product_patterns)
    
    def discard_url(self, href):
        """Check if the URL should be discarded based on the following conditions:
        - URL is not from the original domain
        - URL contains '/gp/' indicating it's not a product page
        """
        # Create a regex pattern to discard URLs containing the specified patterns
        discard_pattern = r'/(?:gp|business|ap|minitv|primein|wishlist|customer-preferences|helpcentre|login|payments|returnpolicy|shipping)/'

        # Use regex to check if the href matches the discard pattern
        if re.search(discard_pattern, href):
            return True  # Discard URLs matching the pattern
        
        # Check if the URL belongs to the same domain as any original URL
        for base_url in self.original_url:
            if href.startswith(base_url):
                return False  # Valid URL from original domain
        # discard if not original url
        return True  # Discard URLs not matching original domain or containing '/gp/'

    def process_page(self, links): 
        for link in links:
            try:
                href = link.get_attribute("href")
                if href and href not in self.visited:
                    # Check if URL should be discarded based on the domain or '/gp/' pattern
                    if self.discard_url(href):
                        print(f"Discarding URL: {href}")
                        continue
                    
                    if self.is_product_url(href):
                        print(f"Found product URL: {href}")
                        parsed_url = urlparse(href)
                        netloc = parsed_url.netloc
                        path = parsed_url.path
                        
                        print(f"parsed_url URL: {parsed_url}")
                        if netloc not in self.results :
                            self.results[netloc].append(f"{netloc}{path}")
                            print(f"Added to results: {netloc}{path}")
                    else:
                        # Locking while adding to the queue
                        with self.lock:  # Ensure thread-safe access to the queue
                            print(f"Adding URL to queue: {href}")
                            self.queue.put(href)
                           
            except Exception as e:
                print(f"Error processing link: {e}")

    def save_results(self):
        try:
            with open("results.json", "w") as f:
                json.dump(self.results, f, indent=4)
            print("Results saved to JSON file")
        except Exception as e:
            print(f"Error saving results to JSON: {e}")

    def worker(self):
        while not self.queue.empty():
            url = self.queue.get()
            if url not in self.visited:
                self.visited.add(url)
                self.crawl_page(url)
            self.queue.task_done()

    def handle_crawl(self, urls):
        print(f"Starting crawl with URLs: {urls}")
        for url in urls:
            self.original_url.add(url)
            self.queue.put(url)

        threads = []
        for i in range(self.max_threads):
            print(f"Starting thread {i+1}")
            thread = threading.Thread(target=self.worker)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        self.save_results()
        return {"message": "Crawling completed!", "results": self.results}