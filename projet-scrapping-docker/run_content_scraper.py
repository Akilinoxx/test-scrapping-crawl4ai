#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import argparse
import logging
import os
from content_scraper import scrape_sites

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('run_content_scraper')

def main():
    """
    Point d'entrée principal pour le scraping de contenu
    """
    parser = argparse.ArgumentParser(
        description='Scrape le contenu complet des sitemaps et stocke chaque site dans un seul fichier markdown'
    )
    
    parser.add_argument('--input-dir', type=str, default='scraped_links',
                        help='Répertoire contenant les URLs extraites des sitemaps')
    parser.add_argument('--output-dir', type=str, default='scraped_content_md',
                        help='Répertoire de sortie pour les fichiers markdown')
    parser.add_argument('--site', type=str, default='',
                        help='Nom spécifique d\'un site à scraper (optionnel, sinon tous les sites seront scrapés)')
    
    args = parser.parse_args()
    
    # S'assurer que le répertoire de sortie existe
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    
    logger.info(f"Démarrage du scraping complet des sitemaps depuis {args.input_dir}")
    logger.info(f"Chaque site sera stocké dans un seul fichier markdown dans {args.output_dir}")
    
    if args.site:
        logger.info(f"Scraping uniquement du site: {args.site}")
    else:
        logger.info("Scraping de tous les sites disponibles")
    
    # Lancer le scraping de façon asynchrone
    asyncio.run(scrape_sites(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        specific_site=args.site
    ))
    
    logger.info("Scraping de contenu terminé")
    logger.info(f"Résultats disponibles dans {os.path.abspath(args.output_dir)}")

if __name__ == "__main__":
    main()
