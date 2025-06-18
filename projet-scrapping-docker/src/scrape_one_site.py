#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import asyncio
import argparse
from sitemap_extractor_simple import SitemapExtractor
from content_scraper import ContentScraper
from crawl4ai import AsyncWebCrawler

async def main():
    """
    Point d'entrée principal pour scraper un site spécifique
    """
    parser = argparse.ArgumentParser(description='Scrape un site spécifique')
    parser.add_argument('url', type=str, help='URL du site à scraper (ex: https://www.example.com)')
    args = parser.parse_args()
    
    url = args.url
    print(f"Démarrage du scraping pour {url}")
    
    # Extraire le nom de domaine pour le dossier
    domain = url.replace('http://', '').replace('https://', '').rstrip('/')
    if domain.startswith('www.'):
        site_name = domain.replace('.', '_')
    else:
        site_name = domain.replace('.', '_')
    
    # Créer le répertoire pour stocker les URLs extraites
    output_dir = 'scraped_links'
    site_dir = os.path.join(output_dir, site_name)
    if not os.path.exists(site_dir):
        os.makedirs(site_dir)
    
    # Extraire les URLs du sitemap
    print(f"Extraction des URLs du sitemap pour {url}...")
    extractor = SitemapExtractor(output_dir=output_dir)
    urls = extractor.extract_all_urls_from_sitemap(url)
    
    # Si peu d'URLs trouvées, utiliser la méthode avancée
    if len(urls) < 5:
        print(f"Peu d'URLs trouvées ({len(urls)}), utilisation de la méthode avancée...")
        urls = extractor.extract_urls_with_crawl4ai_advanced(url)
    
    # Filtrer les URLs pour ne garder que celles du domaine
    filtered_urls = []
    for url_found in urls:
        if site_name.replace('_', '.') in url_found:
            filtered_urls.append(url_found)
    
    # Sauvegarder les URLs extraites
    urls_file = os.path.join(site_dir, 'sitemap_urls.json')
    with open(urls_file, 'w', encoding='utf-8') as f:
        json.dump(filtered_urls, f, indent=2)
    
    print(f"{len(filtered_urls)} URLs extraites et sauvegardées dans {urls_file}")
    
    # Scraper le contenu des URLs avec des paramètres avancés pour contourner les protections anti-bot
    print(f"Scraping du contenu pour {len(filtered_urls)} URLs avec paramètres avancés...")
    
    # Créer un scraper personnalisé avec des paramètres avancés
    class AdvancedContentScraper(ContentScraper):
        async def scrape_url(self, url):
            """
            Version améliorée pour contourner les protections anti-bot
            """
            try:
                # Paramètres avancés pour contourner les protections
                async with AsyncWebCrawler() as crawler:
                    result = await crawler.arun(
                        url=url,
                        timeout=30,  # Timeout plus long
                        wait_until="networkidle2",  # Attendre que le réseau soit inactif
                        stealth=True,  # Mode furtif
                        headers={
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                            'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
                            'Referer': 'https://www.google.com/'
                        }
                    )
                    
                    if hasattr(result, 'html') and result.html:
                        content_data = self.extract_content(result.html)
                        return content_data
                    else:
                        return {
                            "title": url,
                            "description": "Contenu non disponible",
                            "content": "Impossible de récupérer le contenu HTML.",
                            "headings": []
                        }
            except Exception as e:
                return {
                    "title": url,
                    "description": "Erreur lors du scraping",
                    "content": f"Erreur: {str(e)}",
                    "headings": []
                }
    
    # Utiliser le scraper avancé
    scraper = AdvancedContentScraper(input_dir=output_dir, output_dir='scraped_content_md')
    await scraper.scrape_site_urls(site_name, filtered_urls)
    
    print(f"Scraping terminé pour {url}. Résultats sauvegardés dans scraped_content_md/{site_name}.md")

if __name__ == "__main__":
    asyncio.run(main())
