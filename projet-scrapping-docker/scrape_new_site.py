#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import asyncio
import argparse
from sitemap_extractor_simple import SitemapExtractor
from content_scraper import ContentScraper

async def scrape_new_site(url, output_dir='scraped_content_md'):
    """
    Extrait les URLs du sitemap d'un nouveau site et scrape son contenu
    
    Args:
        url (str): URL du site à scraper
        output_dir (str): Répertoire de sortie pour les fichiers markdown
    """
    print(f"Démarrage du scraping pour le nouveau site: {url}")
    
    # Extraire le nom de domaine pour le dossier
    domain = url.replace('http://', '').replace('https://', '').rstrip('/')
    if domain.startswith('www.'):
        site_name = domain
    else:
        site_name = domain.replace('.', '_')
    
    # Créer le répertoire temporaire pour stocker les URLs extraites
    temp_dir = os.path.join('scraped_links', site_name)
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    # Extraire les URLs du sitemap
    print(f"Extraction des URLs du sitemap pour {url}...")
    extractor = SitemapExtractor()
    urls = await extractor.extract_all_urls_from_sitemap(url)
    
    # Si peu d'URLs trouvées, utiliser la méthode avancée
    if len(urls) < 5:
        print(f"Peu d'URLs trouvées ({len(urls)}), utilisation de la méthode avancée...")
        urls = await extractor.extract_urls_with_crawl4ai_advanced(url)
    
    # Sauvegarder les URLs extraites
    urls_file = os.path.join(temp_dir, 'sitemap_urls.json')
    extractor.save_urls_to_file(urls, urls_file)
    print(f"{len(urls)} URLs extraites et sauvegardées dans {urls_file}")
    
    # Scraper le contenu des URLs
    print(f"Scraping du contenu pour {len(urls)} URLs...")
    scraper = ContentScraper(input_dir='scraped_links', output_dir=output_dir)
    await scraper.scrape_site_urls(site_name, urls)
    
    print(f"Scraping terminé pour {url}. Résultats sauvegardés dans {output_dir}/{site_name}.md")
    return site_name

def main():
    """
    Point d'entrée principal
    """
    parser = argparse.ArgumentParser(
        description='Extrait les URLs du sitemap d\'un nouveau site et scrape son contenu'
    )
    
    parser.add_argument('url', type=str,
                        help='URL du site à scraper (ex: https://www.example.com)')
    parser.add_argument('--output-dir', type=str, default='scraped_content_md',
                        help='Répertoire de sortie pour les fichiers markdown')
    
    args = parser.parse_args()
    
    # S'assurer que le répertoire de sortie existe
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    
    # Lancer le scraping
    asyncio.run(scrape_new_site(args.url, args.output_dir))

if __name__ == "__main__":
    main()
