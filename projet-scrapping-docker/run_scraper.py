#!/usr/bin/env python
"""
Script pour lancer facilement le scraping avec différentes configurations
"""
import os
import argparse
import subprocess
import sys

def parse_arguments():
    """
    Parse les arguments de ligne de commande
    """
    parser = argparse.ArgumentParser(description='Lanceur de scraping Crawl4AI')
    
    parser.add_argument('--mode', type=str, choices=['single', 'multi', 'file'], default='single',
                        help='Mode de scraping: single (un seul site), multi (plusieurs sites), file (à partir d\'un fichier)')
    
    parser.add_argument('--site', type=str, default='https://dentego.fr',
                        help='URL du site à scraper (mode single)')
    
    parser.add_argument('--sites', nargs='+',
                        help='Liste des URLs des sites à scraper (mode multi)')
    
    parser.add_argument('--file', type=str, default='sites_example.txt',
                        help='Fichier contenant les URLs des sites à scraper (mode file)')
    
    parser.add_argument('--max-urls', type=int, default=10,
                        help='Nombre maximum d\'URLs à scraper par site (0 = illimité)')
    
    return parser.parse_args()

def main():
    """
    Fonction principale
    """
    args = parse_arguments()
    
    # Construire la commande en fonction du mode
    cmd = [sys.executable, 'app.py']
    
    if args.mode == 'single':
        cmd.extend(['--sites', args.site])
    elif args.mode == 'multi':
        if not args.sites:
            print("Erreur: Vous devez spécifier au moins un site avec --sites en mode multi")
            sys.exit(1)
        cmd.extend(['--sites'] + args.sites)
    elif args.mode == 'file':
        cmd.extend(['--sites-file', args.file])
    
    # Ajouter l'option max-urls
    cmd.extend(['--max-urls', str(args.max_urls)])
    
    # Afficher la commande
    print(f"Exécution de la commande: {' '.join(cmd)}")
    
    # Exécuter la commande
    try:
        subprocess.run(cmd, check=True)
        print("Scraping terminé avec succès!")
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors du scraping: {e}")
    except KeyboardInterrupt:
        print("\nScraping interrompu par l'utilisateur")

if __name__ == "__main__":
    main()
