"""
Módulo de scraping web simple con BeautifulSoup.
"""
import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)


class Scraper:
    """Scraper simple con requests + BeautifulSoup."""
    
    def __init__(self, timeout: int = 10):
        """
        Inicializa el scraper.
        
        Args:
            timeout: Timeout en segundos para requests
        """
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
    
    def scrape(self, url: str) -> Dict[str, str]:
        """
        Extrae contenido de una URL.
        
        Args:
            url: URL a scraping
            
        Returns:
            Dict con title, description, content, domain
            
        Raises:
            Exception: Si falla el scraping
        """
        logger.info(f"Scraping URL: {url}")
        
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            domain = urlparse(url).netloc
            title = self._extract_title(soup)
            description = self._extract_meta_description(soup)
            content = self._extract_body_text(soup)
            og_data = self._extract_og_data(soup)
            
            result = {
                'url': url,
                'domain': domain,
                'title': title,
                'description': description,
                'content': content,
                'og_title': og_data.get('title'),
                'og_description': og_data.get('description'),
                'og_image': og_data.get('image')
            }
            
            logger.info(f"Successfully scraped {url} - {len(content)} chars")
            return result
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout scraping {url}")
            raise Exception(f"Timeout alcanzado ({self.timeout}s)")
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error scraping {url}: {e}")
            raise Exception(f"Error al acceder a la URL: {str(e)}")
        
        except Exception as e:
            logger.error(f"Unexpected error scraping {url}: {e}")
            raise Exception(f"Error inesperado: {str(e)}")
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extrae el título de la página."""
        if soup.title and soup.title.string:
            return soup.title.string.strip()
        
        h1 = soup.find('h1')
        if h1:
            return h1.get_text().strip()
        
        return "Sin título"
    
    def _extract_meta_description(self, soup: BeautifulSoup) -> str:
        """Extrae meta description."""
        meta = soup.find('meta', attrs={'name': 'description'})
        if meta and meta.get('content'):
            return meta['content'].strip()
        return ""
    
    def _extract_og_data(self, soup: BeautifulSoup) -> Dict[str, Optional[str]]:
        """Extrae datos de Open Graph."""
        og_data = {}
        
        og_title = soup.find('meta', property='og:title')
        if og_title:
            og_data['title'] = og_title.get('content')
        
        og_desc = soup.find('meta', property='og:description')
        if og_desc:
            og_data['description'] = og_desc.get('content')
        
        og_image = soup.find('meta', property='og:image')
        if og_image:
            og_data['image'] = og_image.get('content')
        
        return og_data
    
    def _extract_body_text(self, soup: BeautifulSoup) -> str:
        """
        Extrae texto limpio del body.
        Remueve scripts, styles, nav, footer.
        """
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            element.decompose()
        
        body = soup.find('body')
        if not body:
            return soup.get_text()
        
        text = body.get_text(separator='\n', strip=True)
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        text = '\n'.join(lines)
        
        return text
