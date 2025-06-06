import os
import sys
import os
import argparse
import logging
import time
import json
from sitemap_extractor import SitemapExtractor, process_multiple_sites

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('crawl4ai_app')

def parse_arguments():
    """
    Parse les arguments de ligne de commande
    
    Returns:
        argparse.Namespace: Arguments parsés
    """
    parser = argparse.ArgumentParser(description='Crawl4AI - Extracteur de sitemap et scraper')
    
    # Arguments principaux
    parser.add_argument('--sites', '-s', nargs='+', required=False,
                        help='Liste des URLs des sites à traiter')
    parser.add_argument('--sites-file', '-f', type=str,
                        help='Chemin vers un fichier contenant les URLs des sites (une par ligne)')
    parser.add_argument('--output-dir', '-o', type=str, default='scraped_links',
                        help='Répertoire de sortie pour les données scrapées')
    
    # Options de configuration
    parser.add_argument('--max-workers', '-w', type=int, default=5,
                        help='Nombre maximum de workers pour le threading')
    parser.add_argument('--delay', '-d', type=float, default=1.0,
                        help='Délai entre les requêtes (en secondes)')
    parser.add_argument('--max-urls', '-m', type=int, default=0,
                        help='Nombre maximum d\'URLs à scraper par site (0 = illimité)')
    
    # Mode de fonctionnement
    parser.add_argument('--sitemap-only', action='store_true',
                        help='Extraire uniquement les URLs des sitemaps sans scraper les pages')
    
    return parser.parse_args()

def load_sites_from_file(file_path):
    """
    Charge les URLs des sites à partir d'un fichier texte
    
    Args:
        file_path (str): Chemin vers le fichier
        
    Returns:
        list: Liste des URLs des sites
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
    except Exception as e:
        logger.error(f"Erreur lors de la lecture du fichier {file_path}: {e}")
        sys.exit(1)

def sitemap_only_mode(sites, output_dir, max_workers, delay):
    """
    Mode d'extraction des sitemaps uniquement (sans scraping)
    
    Args:
        sites (list): Liste des URLs des sites
        output_dir (str): Répertoire de sortie
        max_workers (int): Nombre maximum de workers
        delay (float): Délai entre les requêtes
    """
    extractor = SitemapExtractor(output_dir=output_dir, max_workers=max_workers, delay=delay)
    all_urls = {}
    
    for site_url in sites:
        logger.info(f"Extraction du sitemap pour {site_url}")
        urls = extractor.extract_all_urls_from_sitemap(site_url)
        
        # Extraire le nom du domaine
        from urllib.parse import urlparse
        parsed_url = urlparse(site_url)
        site_name = parsed_url.netloc.replace('.', '_')
        
        # Sauvegarder les URLs dans un fichier
        site_dir = os.path.join(output_dir, site_name)
        if not os.path.exists(site_dir):
            os.makedirs(site_dir)
            
        urls_file = os.path.join(site_dir, "sitemap_urls.json")
        with open(urls_file, 'w', encoding='utf-8') as f:
            json.dump(urls, f, ensure_ascii=False, indent=2)
            
        all_urls[site_url] = {
            'site_name': site_name,
            'url_count': len(urls)
        }
        
        logger.info(f"Extraction terminée pour {site_url}. {len(urls)} URLs trouvées.")
    
    # Sauvegarder un résumé global
    summary_file = os.path.join(output_dir, "sitemap_summary.json")
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(all_urls, f, ensure_ascii=False, indent=2)
        
    logger.info(f"Extraction des sitemaps terminée pour {len(sites)} sites.")

def main():
    """
    Fonction principale
    """
    args = parse_arguments()
    
    # Charger les sites à partir des arguments ou d'un fichier
    sites = []
    if args.sites:
        sites = args.sites
    elif args.sites_file:
        sites = load_sites_from_file(args.sites_file)
    else:
        # Si aucun site n'est spécifié, utiliser des exemples
        logger.warning("Aucun site spécifié. Utilisation des sites d'exemple.")
        sites = [
            "https://www.example.com",
            "https://www.python.org"
        ]
    
    logger.info(f"Traitement de {len(sites)} sites")
    
    # Créer le répertoire de sortie s'il n'existe pas
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    
    # Exécuter le mode approprié
    if args.sitemap_only:
        sitemap_only_mode(sites, args.output_dir, args.max_workers, args.delay)
    else:
        # Mode complet: extraction des sitemaps + scraping
        stats = process_multiple_sites(
            sites=sites,
            output_dir=args.output_dir,
            max_workers=args.max_workers,
            delay=args.delay,
            max_urls=args.max_urls
        )
        
        # Afficher un résumé
        logger.info("Résumé du traitement:")
        for site_stat in stats:
            logger.info(f"Site: {site_stat['site_url']}")
            logger.info(f"  - URLs trouvées: {site_stat['total_urls']}")
            logger.info(f"  - URLs scrapées: {site_stat['scraped_urls']}")
            logger.info(f"  - Temps total: {site_stat['total_time']:.2f} secondes")

if __name__ == "__main__":
    main()
