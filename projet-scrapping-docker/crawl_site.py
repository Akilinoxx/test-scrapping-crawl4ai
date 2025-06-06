import os
import sys
import json
import argparse
import subprocess
import time
from urllib.parse import urlparse

def parse_arguments():
    """
    Parse les arguments de ligne de commande
    
    Returns:
        argparse.Namespace: Arguments parsés
    """
    parser = argparse.ArgumentParser(description='Crawl4AI - Scraper de site web')
    
    # Arguments principaux
    parser.add_argument('--sites', '-s', nargs='+', required=True,
                        help='Liste des URLs des sites à traiter')
    parser.add_argument('--output-dir', '-o', type=str, default='scraped_links',
                        help='Répertoire de sortie pour les données scrapées')
    parser.add_argument('--max-urls', '-m', type=int, default=0,
                        help='Nombre maximum d\'URLs à scraper par site (0 = illimité)')
    
    return parser.parse_args()

def crawl_site(site_url, output_dir, max_urls=0):
    """
    Scrape un site web en utilisant Crawl4AI
    
    Args:
        site_url (str): URL du site à scraper
        output_dir (str): Répertoire de sortie
        max_urls (int): Nombre maximum d'URLs à scraper (0 = illimité)
    """
    # Extraire le nom du domaine pour l'utiliser comme nom de site
    parsed_url = urlparse(site_url)
    site_name = parsed_url.netloc.replace('.', '_')
    
    # Créer un répertoire spécifique pour ce site
    site_dir = os.path.join(output_dir, site_name)
    if not os.path.exists(site_dir):
        os.makedirs(site_dir)
    
    # Fichier de sortie pour le contenu markdown
    output_file = os.path.join(site_dir, f"{site_name}_content.md")
    
    # Construire la commande Crawl4AI
    cmd = ["crwl", site_url, "-o", "markdown"]
    
    # Ajouter l'option pour limiter le nombre d'URLs si spécifié
    if max_urls > 0:
        cmd.extend(["--deep-crawl", "bfs", "--max-pages", str(max_urls)])
    
    print(f"Exécution de la commande: {' '.join(cmd)}")
    
    # Exécuter la commande et capturer la sortie
    start_time = time.time()
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Écrire le contenu markdown dans un fichier
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# Contenu scrapé de {site_name}\n\n")
            f.write(f"Date de scraping: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("="*80 + "\n\n")
            f.write(result.stdout)
        
        # Créer un fichier d'index
        index_file = os.path.join(site_dir, "index.json")
        index_data = {
            'site_name': site_name,
            'site_url': site_url,
            'scraping_time': time.time() - start_time,
            'timestamp': time.time(),
            'markdown_file': f"{site_name}_content.md"
        }
        
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)
        
        print(f"Scraping terminé pour {site_url}. Résultats sauvegardés dans {output_file}")
        
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors du scraping de {site_url}: {e}")
        print(f"Sortie d'erreur: {e.stderr}")
    except Exception as e:
        print(f"Erreur inattendue: {e}")

def main():
    """
    Fonction principale
    """
    args = parse_arguments()
    
    # Créer le répertoire de sortie s'il n'existe pas
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    
    # Traiter chaque site
    for site_url in args.sites:
        print(f"Traitement du site: {site_url}")
        crawl_site(site_url, args.output_dir, args.max_urls)

if __name__ == "__main__":
    main()
