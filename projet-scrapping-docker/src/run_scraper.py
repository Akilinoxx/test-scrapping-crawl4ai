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
    parser = argparse.ArgumentParser(description='Extracteur de sitemap Crawl4AI')
    
    parser.add_argument('--mode', type=str, choices=['single', 'multi', 'file'], default='single',
                        help='Mode d\'extraction: single (un seul site), multi (plusieurs sites), file (à partir d\'un fichier)')
    
    parser.add_argument('--site', type=str, default='https://dentego.fr',
                        help='URL du site à analyser (mode single)')
    
    parser.add_argument('--sites', nargs='+',
                        help='Liste des URLs des sites à analyser (mode multi)')
    
    parser.add_argument('--file', type=str, default='sites_example.txt',
                        help='Fichier contenant les URLs des sites à analyser (mode file)')
    
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
    
    # Forcer le mode sitemap uniquement
    cmd.extend(['--sitemap-only'])
    
    # Afficher la commande
    print(f"Exécution de la commande: {' '.join(cmd)}")
    
    # Exécuter la commande
    try:
        subprocess.run(cmd, check=True)
        print("Extraction des sitemaps terminée avec succès!")
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'extraction: {e}")
    except KeyboardInterrupt:
        print("\nExtraction interrompue par l'utilisateur")

if __name__ == "__main__":
    main()
