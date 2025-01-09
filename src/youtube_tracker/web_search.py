import requests
from bs4 import BeautifulSoup
import logging
import json
import time
from googlesearch import search

logger = logging.getLogger(__name__)

class WebSearcher:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def search(self, query, num_results=5):
        """
        Search Google for the given query and return results with context.
        
        Args:
            query (str): Search query
            num_results (int): Number of results to return
            
        Returns:
            list: List of dictionaries containing URL and context
        """
        try:
            logger.info(f"Performing Google search for: {query}")
            results = []
            
            # Use googlesearch-python to get search results
            search_results = search(query, num_results=num_results, advanced=True)
            
            for result in search_results:
                try:
                    # Extract information from search result
                    url = result.url
                    title = result.title or "No title available"
                    snippet = result.description or "No description available"
                    
                    # Get additional context from the webpage
                    page_context = self.get_page_context(url)
                    
                    results.append({
                        'url': url,
                        'title': title,
                        'snippet': snippet,
                        'context': page_context
                    })
                    
                    # Be nice to servers
                    time.sleep(2)
                    
                except Exception as e:
                    logger.warning(f"Error processing search result: {str(e)}")
                    continue
            
            logger.info(f"Found {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Error performing web search: {str(e)}")
            return []
            
    def get_page_context(self, url):
        """
        Get additional context from the webpage.
        
        Args:
            url (str): URL to fetch
            
        Returns:
            str: Extracted context or empty string if failed
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(['script', 'style']):
                script.decompose()
                
            # Get text content
            text = soup.get_text(separator=' ', strip=True)
            
            # Clean up whitespace
            text = ' '.join(text.split())
            
            # Limit to first 1000 characters
            return text[:1000]
            
        except Exception as e:
            logger.warning(f"Error fetching page context for {url}: {str(e)}")
            return ""
