#!/usr/bin/env python
"""
Script de test pour extraire les URLs d'un site sans utiliser de sitemap
"""
import os
import json
import requests
import logging
import asyncio
import time
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from crawl4ai import AsyncWebCrawler

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test_extract_urls')

async def extract_urls_with_crawl4ai(url):
    """
    Extrait les URLs d'une page en utilisant Crawl4AI
    """
    logger.info(f"Extraction des URLs avec Crawl4AI pour {url}")
    all_urls = set()
    base_domain = urlparse(url).netloc
    
    try:
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=url)
            
            if hasattr(result, 'html') and result.html:
                soup = BeautifulSoup(result.html, 'html.parser')
                for a_tag in soup.find_all('a', href=True):
                    href = a_tag['href']
                    # Ignorer les liens vides, les ancres et les liens externes
                    if not href or href.startswith('#') or href.startswith('mailto:') or href.startswith('tel:'):
                        continue
                    # Convertir les URLs relatives en URLs absolues
                    if not href.startswith('http'):
                        href = urljoin(url, href)
                    # Ne garder que les URLs du même domaine
                    if urlparse(href).netloc == base_domain:
                        all_urls.add(href)
                        logger.info(f"URL trouvée: {href}")
            
            logger.info(f"Total: {len(all_urls)} URLs trouvées avec Crawl4AI")
            return list(all_urls)
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction avec Crawl4AI: {e}")
        return []

def extract_urls_with_requests(url):
    """
    Extrait les URLs d'une page en utilisant requests et BeautifulSoup
    """
    logger.info(f"Extraction des URLs avec requests pour {url}")
    all_urls = set()
    base_domain = urlparse(url).netloc
    
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                # Ignorer les liens vides, les ancres et les liens externes
                if not href or href.startswith('#') or href.startswith('mailto:') or href.startswith('tel:'):
                    continue
                # Convertir les URLs relatives en URLs absolues
                if not href.startswith('http'):
                    href = urljoin(url, href)
                # Ne garder que les URLs du même domaine
                if urlparse(href).netloc == base_domain:
                    all_urls.add(href)
                    logger.info(f"URL trouvée: {href}")
        
        logger.info(f"Total: {len(all_urls)} URLs trouvées avec requests")
        return list(all_urls)
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction avec requests: {e}")
        return []

def generate_common_urls(url):
    """
    Génère des URLs communes pour un site
    """
    logger.info(f"Génération d'URLs communes pour {url}")
    all_urls = set([url])
    
    common_paths = [
        '/', '/about', '/about-us', '/contact', '/contact-us', '/products', '/services',
        '/blog', '/news', '/faq', '/help', '/support', '/menu', '/locations', '/store',
        '/shop', '/cart', '/account', '/login', '/register', '/privacy', '/terms',
        '/sitemap', '/search', '/gallery', '/portfolio', '/team', '/careers', '/jobs',
        '/events', '/offers', '/promotions', '/pricing', '/testimonials', '/reviews'
    ]
    
    for path in common_paths:
        generated_url = urljoin(url, path)
        all_urls.add(generated_url)
        logger.info(f"URL générée: {generated_url}")
    
    logger.info(f"Total: {len(all_urls)} URLs générées")
    return list(all_urls)

async def main():
    """
    Fonction principale
    """
    url = "https://www.volfoni.fr"
    
    # Méthode 1: Crawl4AI
    crawl4ai_urls = await extract_urls_with_crawl4ai(url)
    
    # Méthode 2: Requests
    requests_urls = extract_urls_with_requests(url)
    
    # Méthode 3: URLs communes
    common_urls = generate_common_urls(url)
    
    # Combiner toutes les URLs
    all_urls = list(set(crawl4ai_urls + requests_urls + common_urls))
    
    # Sauvegarder les résultats
    results = {
        'url': url,
        'crawl4ai_urls': crawl4ai_urls,
        'requests_urls': requests_urls,
        'common_urls': common_urls,
        'all_urls': all_urls,
        'total_urls': len(all_urls)
    }
    
    with open('volfoni_urls.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Total final: {len(all_urls)} URLs uniques trouvées pour {url}")
    logger.info(f"Résultats sauvegardés dans volfoni_urls.json")

if __name__ == "__main__":
    asyncio.run(main())
