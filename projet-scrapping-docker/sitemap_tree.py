#!/usr/bin/env python
"""
Script pour visualiser l'arborescence des sitemaps d'un site web
"""
import os
import json
import requests
import logging
import argparse
from urllib.parse import urlparse, urljoin
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import time
from tqdm import tqdm

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('sitemap_tree')

class SitemapTreeExtractor:
    def __init__(self, output_dir='sitemap_trees'):
        """
        Initialise l'extracteur d'arborescence de sitemap
        
        Args:
            output_dir (str): Répertoire de sortie pour les arbres de sitemaps
        """
        self.output_dir = output_dir
        
        # Création du répertoire de sortie s'il n'existe pas
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def get_robots_txt(self, base_url):
        """
        Récupère le fichier robots.txt d'un site et extrait les URLs des sitemaps
        
        Args:
            base_url (str): URL de base du site
            
        Returns:
            list: Liste des URLs de sitemaps trouvées
        """
        robots_url = urljoin(base_url, '/robots.txt')
        sitemap_urls = []
        
        try:
            response = requests.get(robots_url, timeout=10)
            if response.status_code == 200:
                for line in response.text.split('\n'):
                    if line.lower().startswith('sitemap:'):
                        sitemap_url = line.split(':', 1)[1].strip()
                        sitemap_urls.append(sitemap_url)
                        
            if not sitemap_urls:
                # Si aucun sitemap n'est trouvé dans robots.txt, essayons l'URL standard
                sitemap_urls.append(urljoin(base_url, '/sitemap.xml'))
                
            return sitemap_urls
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du robots.txt de {base_url}: {e}")
            # En cas d'erreur, essayons l'URL standard
            return [urljoin(base_url, '/sitemap.xml')]
    
    def parse_sitemap(self, sitemap_url):
        """
        Parse un fichier sitemap XML et extrait les URLs
        
        Args:
            sitemap_url (str): URL du sitemap à parser
            
        Returns:
            tuple: (liste des URLs de pages, liste des URLs de sous-sitemaps, type de sitemap)
        """
        urls = []
        sub_sitemaps = []
        sitemap_type = "unknown"
        
        try:
            logger.info(f"Analyse du sitemap: {sitemap_url}")
            response = requests.get(sitemap_url, timeout=10)
            if response.status_code != 200:
                logger.warning(f"Impossible d'accéder au sitemap {sitemap_url} (code {response.status_code})")
                return urls, sub_sitemaps, sitemap_type
            
            # Vérifier si c'est un sitemap index (qui contient d'autres sitemaps)
            if '<sitemapindex' in response.text:
                sitemap_type = "sitemapindex"
                root = ET.fromstring(response.text)
                namespaces = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
                
                for sitemap in root.findall('.//sm:sitemap/sm:loc', namespaces):
                    sub_sitemaps.append(sitemap.text)
            
            # Vérifier s'il s'agit d'un sitemap normal (qui contient des URLs)
            elif '<urlset' in response.text:
                sitemap_type = "urlset"
                root = ET.fromstring(response.text)
                namespaces = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
                
                for url in root.findall('.//sm:url/sm:loc', namespaces):
                    urls.append(url.text)
            
            # Si le parsing XML échoue, essayons avec BeautifulSoup
            else:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Déterminer le type de sitemap
                if soup.find('sitemapindex'):
                    sitemap_type = "sitemapindex"
                elif soup.find('urlset'):
                    sitemap_type = "urlset"
                
                # Chercher les URLs dans les balises <loc>
                for loc in soup.find_all('loc'):
                    if loc.parent.name == 'sitemap':
                        sub_sitemaps.append(loc.text)
                    elif loc.parent.name == 'url':
                        urls.append(loc.text)
            
            logger.info(f"Sitemap {sitemap_url} analysé: {len(urls)} URLs, {len(sub_sitemaps)} sous-sitemaps, type: {sitemap_type}")
            return urls, sub_sitemaps, sitemap_type
        
        except Exception as e:
            logger.error(f"Erreur lors du parsing du sitemap {sitemap_url}: {e}")
            return urls, sub_sitemaps, sitemap_type
    
    def build_sitemap_tree(self, base_url, max_depth=5):
        """
        Construit l'arborescence complète des sitemaps d'un site
        
        Args:
            base_url (str): URL de base du site
            max_depth (int): Profondeur maximale de l'arborescence
            
        Returns:
            dict: Arborescence des sitemaps
        """
        def _build_tree(sitemap_url, current_depth=0):
            if current_depth > max_depth:
                return {
                    "url": sitemap_url,
                    "type": "max_depth_reached",
                    "urls": [],
                    "children": []
                }
            
            urls, sub_sitemaps, sitemap_type = self.parse_sitemap(sitemap_url)
            
            # Limiter le nombre d'URLs à afficher pour éviter des fichiers trop volumineux
            displayed_urls = urls[:100]
            
            node = {
                "url": sitemap_url,
                "type": sitemap_type,
                "urls_count": len(urls),
                "urls": displayed_urls,
                "children": []
            }
            
            # Récursivement construire l'arborescence pour les sous-sitemaps
            for sub_sitemap in sub_sitemaps:
                child_node = _build_tree(sub_sitemap, current_depth + 1)
                node["children"].append(child_node)
            
            return node
        
        # Récupérer les sitemaps racines depuis robots.txt
        root_sitemaps = self.get_robots_txt(base_url)
        
        # Construire l'arborescence pour chaque sitemap racine
        tree = {
            "site": base_url,
            "root_sitemaps": []
        }
        
        for sitemap_url in root_sitemaps:
            sitemap_tree = _build_tree(sitemap_url)
            tree["root_sitemaps"].append(sitemap_tree)
        
        return tree
    
    def save_tree_to_file(self, tree, site_url):
        """
        Sauvegarde l'arborescence des sitemaps dans un fichier JSON
        
        Args:
            tree (dict): Arborescence des sitemaps
            site_url (str): URL du site
        """
        # Extraire le nom de domaine pour le nom de fichier
        parsed_url = urlparse(site_url)
        site_name = parsed_url.netloc.replace('.', '_')
        
        # Créer le répertoire pour le site s'il n'existe pas
        site_dir = os.path.join(self.output_dir, site_name)
        if not os.path.exists(site_dir):
            os.makedirs(site_dir)
        
        # Sauvegarder l'arborescence au format JSON
        tree_file = os.path.join(site_dir, f"{site_name}_sitemap_tree.json")
        with open(tree_file, 'w', encoding='utf-8') as f:
            json.dump(tree, f, indent=2, ensure_ascii=False)
        
        # Générer une version texte de l'arborescence pour une visualisation facile
        text_tree = self.generate_text_tree(tree)
        text_file = os.path.join(site_dir, f"{site_name}_sitemap_tree.txt")
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(text_tree)
        
        logger.info(f"Arborescence des sitemaps sauvegardée dans {tree_file} et {text_file}")
        
        return tree_file, text_file
    
    def generate_text_tree(self, tree, indent=0):
        """
        Génère une représentation textuelle de l'arborescence des sitemaps
        
        Args:
            tree (dict): Arborescence des sitemaps
            indent (int): Niveau d'indentation
            
        Returns:
            str: Représentation textuelle de l'arborescence
        """
        if "site" in tree:  # C'est la racine
            result = f"Site: {tree['site']}\n\n"
            for i, sitemap in enumerate(tree["root_sitemaps"]):
                result += self.generate_text_tree(sitemap, indent)
                if i < len(tree["root_sitemaps"]) - 1:
                    result += "\n"
            return result
        
        # C'est un nœud de sitemap
        prefix = "  " * indent
        result = f"{prefix}Sitemap: {tree['url']}\n"
        result += f"{prefix}Type: {tree['type']}\n"
        
        if "urls_count" in tree:
            result += f"{prefix}Nombre d'URLs: {tree['urls_count']}\n"
        
        # Afficher quelques URLs (limité pour éviter des fichiers trop volumineux)
        if tree.get("urls") and len(tree["urls"]) > 0:
            result += f"{prefix}Exemples d'URLs:\n"
            for i, url in enumerate(tree["urls"][:10]):  # Limiter à 10 exemples
                result += f"{prefix}  - {url}\n"
            if len(tree["urls"]) > 10:
                result += f"{prefix}  ... et {len(tree['urls']) - 10} de plus\n"
        
        # Récursivement générer l'arborescence pour les enfants
        if tree.get("children") and len(tree["children"]) > 0:
            result += f"{prefix}Sous-sitemaps ({len(tree['children'])}):\n"
            for child in tree["children"]:
                result += self.generate_text_tree(child, indent + 1)
        
        return result
    
    def process_site(self, site_url, max_depth=5):
        """
        Traite un site: extraction de l'arborescence des sitemaps
        
        Args:
            site_url (str): URL du site à traiter
            max_depth (int): Profondeur maximale de l'arborescence
            
        Returns:
            tuple: (fichier JSON, fichier texte)
        """
        logger.info(f"Extraction de l'arborescence des sitemaps pour {site_url}")
        
        # Construire l'arborescence des sitemaps
        tree = self.build_sitemap_tree(site_url, max_depth)
        
        # Sauvegarder l'arborescence
        json_file, text_file = self.save_tree_to_file(tree, site_url)
        
        return json_file, text_file

def process_multiple_sites(sites, output_dir='sitemap_trees', max_depth=5):
    """
    Traite plusieurs sites en séquence
    
    Args:
        sites (list): Liste des URLs des sites à traiter
        output_dir (str): Répertoire de sortie
        max_depth (int): Profondeur maximale de l'arborescence
        
    Returns:
        dict: Résultats pour chaque site traité
    """
    extractor = SitemapTreeExtractor(output_dir)
    results = {}
    
    for site_url in tqdm(sites, desc="Traitement des sites"):
        try:
            json_file, text_file = extractor.process_site(site_url, max_depth)
            results[site_url] = {
                "json_file": json_file,
                "text_file": text_file,
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Erreur lors du traitement du site {site_url}: {e}")
            results[site_url] = {
                "status": "error",
                "error": str(e)
            }
    
    return results

def main():
    """
    Fonction principale
    """
    parser = argparse.ArgumentParser(description='Extracteur d\'arborescence de sitemaps')
    
    parser.add_argument('--sites', '-s', nargs='+', help='Liste des URLs des sites à traiter')
    parser.add_argument('--sites-file', '-f', help='Chemin vers un fichier contenant les URLs des sites (une par ligne)')
    parser.add_argument('--output-dir', '-o', default='sitemap_trees', help='Répertoire de sortie pour les arbres de sitemaps')
    parser.add_argument('--max-depth', '-d', type=int, default=5, help='Profondeur maximale de l\'arborescence')
    
    args = parser.parse_args()
    
    # Vérifier qu'au moins une source de sites est spécifiée
    if not args.sites and not args.sites_file:
        parser.error("Vous devez spécifier soit --sites, soit --sites-file")
    
    # Récupérer la liste des sites
    sites = []
    if args.sites:
        sites.extend(args.sites)
    
    if args.sites_file:
        try:
            with open(args.sites_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        sites.append(line)
        except Exception as e:
            logger.error(f"Erreur lors de la lecture du fichier {args.sites_file}: {e}")
    
    # Traiter les sites
    if sites:
        start_time = time.time()
        results = process_multiple_sites(sites, args.output_dir, args.max_depth)
        elapsed_time = time.time() - start_time
        
        # Afficher un résumé
        success_count = sum(1 for result in results.values() if result["status"] == "success")
        logger.info(f"Traitement terminé en {elapsed_time:.2f} secondes")
        logger.info(f"Sites traités avec succès: {success_count}/{len(sites)}")
        
        # Afficher les sites en erreur
        error_sites = [site for site, result in results.items() if result["status"] == "error"]
        if error_sites:
            logger.warning(f"Sites en erreur ({len(error_sites)}):")
            for site in error_sites:
                logger.warning(f"  - {site}: {results[site]['error']}")
    else:
        logger.warning("Aucun site à traiter")

if __name__ == "__main__":
    main()
