import os
import json
import requests
import logging
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import time
import asyncio
from crawl4ai import AsyncWebCrawler

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('sitemap_extractor')

class SitemapExtractor:
    def __init__(self, output_dir='scraped_links', max_workers=5, delay=0.1):
        """
        Initialise l'extracteur de sitemap
        
        Args:
            output_dir (str): Répertoire de sortie pour les données scrapées
            max_workers (int): Nombre maximum de workers pour le threading
            delay (float): Délai entre les requêtes (en secondes)
        """
        self.output_dir = output_dir
        self.max_workers = max_workers
        self.delay = delay  # Réduit à 0.1 seconde par défaut
        
        # Création du répertoire de sortie s'il n'existe pas
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def normalize_url(self, url):
        """
        Normalise une URL en supprimant les paramètres de requête et les fragments
        
        Args:
            url (str): URL à normaliser
            
        Returns:
            str: URL normalisée
        """
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    
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
            tuple: (liste des URLs de pages, liste des URLs de sous-sitemaps)
        """
        urls = []
        sub_sitemaps = []
        
        try:
            response = requests.get(sitemap_url, timeout=10)
            if response.status_code != 200:
                logger.warning(f"Impossible d'accéder au sitemap {sitemap_url} (code {response.status_code})")
                return urls, sub_sitemaps
            
            # Vérifier si c'est un sitemap index (qui contient d'autres sitemaps)
            if '<sitemapindex' in response.text:
                root = ET.fromstring(response.text)
                namespaces = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
                
                for sitemap in root.findall('.//sm:sitemap/sm:loc', namespaces):
                    sub_sitemaps.append(sitemap.text)
            
            # Vérifier s'il s'agit d'un sitemap normal (qui contient des URLs)
            elif '<urlset' in response.text:
                root = ET.fromstring(response.text)
                namespaces = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
                
                for url in root.findall('.//sm:url/sm:loc', namespaces):
                    urls.append(url.text)
            
            # Si le parsing XML échoue, essayons avec BeautifulSoup
            else:
                soup = BeautifulSoup(response.text, 'html.parser')
                # Chercher les URLs dans les balises <loc>
                for loc in soup.find_all('loc'):
                    if loc.parent.name == 'sitemap':
                        sub_sitemaps.append(loc.text)
                    elif loc.parent.name == 'url':
                        urls.append(loc.text)
            
            return urls, sub_sitemaps
        
        except Exception as e:
            logger.error(f"Erreur lors du parsing du sitemap {sitemap_url}: {e}")
            return urls, sub_sitemaps
    
    def extract_all_urls_from_sitemap(self, base_url):
        """
        Extrait toutes les URLs d'un site en parcourant ses sitemaps
        
        Args:
            base_url (str): URL de base du site
            
        Returns:
            list: Liste de toutes les URLs trouvées
        """
        all_urls = set()
        processed_sitemaps = set()
        pending_sitemaps = set(self.get_robots_txt(base_url))
        
        # Si aucun sitemap n'est trouvé, utiliser directement la méthode avancée
        if not pending_sitemaps:
            logger.warning(f"Aucun sitemap trouvé pour {base_url}, utilisation de la méthode avancée avec Crawl4AI")
            return self.extract_urls_with_crawl4ai_advanced(base_url)
        
        while pending_sitemaps:
            sitemap_url = pending_sitemaps.pop()
            if sitemap_url in processed_sitemaps:
                continue
                
            logger.info(f"Traitement du sitemap: {sitemap_url}")
            processed_sitemaps.add(sitemap_url)
            
            urls, sub_sitemaps = self.parse_sitemap(sitemap_url)
            all_urls.update(urls)
            
            # Ajouter les sous-sitemaps à la liste des sitemaps à traiter
            for sub_sitemap in sub_sitemaps:
                if sub_sitemap not in processed_sitemaps:
                    pending_sitemaps.add(sub_sitemap)
            
            # Délai minimal ou pas de délai
            # time.sleep(self.delay)
        
        # Si peu d'URLs ont été trouvées, utiliser directement la méthode avancée
        # au lieu de compléter les résultats du sitemap
        if len(all_urls) < 3:
            logger.warning(f"Seulement {len(all_urls)} URLs trouvées dans les sitemaps de {base_url}, utilisation de la méthode avancée avec Crawl4AI")
            advanced_urls = self.extract_urls_with_crawl4ai_advanced(base_url)
            # Remplacer complètement les résultats si la méthode avancée trouve plus d'URLs
            if len(advanced_urls) > len(all_urls):
                logger.info(f"La méthode avancée a trouvé {len(advanced_urls)} URLs contre {len(all_urls)} pour le sitemap, utilisation des résultats de la méthode avancée")
                return advanced_urls
            else:
                # Sinon, combiner les résultats
                all_urls.update(advanced_urls)
                logger.info(f"Après méthodes avancées: {len(all_urls)} URLs trouvées pour {base_url}")
        
        return list(all_urls)
        
    def extract_urls_without_sitemap(self, base_url):
        """
        Extrait les URLs d'un site sans utiliser de sitemap
        en utilisant plusieurs méthodes complémentaires pour maximiser la couverture
        
        Args:
            base_url (str): URL de base du site
            
        Returns:
            list: Liste des URLs trouvées
        """
        logger.info(f"Extraction des URLs sans sitemap pour {base_url}")
        all_urls = set([base_url])  # Commencer par la page d'accueil
        base_domain = urlparse(base_url).netloc
        
        # Ajouter quelques URLs de base pour s'assurer d'avoir au moins quelque chose
        logger.info(f"Ajout d'URLs de base pour {base_url}")
        all_urls.add(base_url)
        all_urls.add(base_url + "/")
        
        # Méthode 1: Utiliser Crawl4AI pour explorer la page d'accueil avec JavaScript
        try:
            logger.info(f"Exploration avec Crawl4AI pour {base_url}")
            async def crawl_home_page(url):
                async with AsyncWebCrawler() as crawler:
                    result = await crawler.arun(url=url)
                    return result
            
            # Exécuter la fonction asynchrone dans une boucle d'événements
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(crawl_home_page(base_url))
                
                # Extraire les liens de la page d'accueil
                if hasattr(result, 'html') and result.html:
                    soup = BeautifulSoup(result.html, 'html.parser')
                    for a_tag in soup.find_all('a', href=True):
                        href = a_tag['href']
                        # Ignorer les liens vides, les ancres et les liens externes
                        if not href or href.startswith('#') or href.startswith('mailto:') or href.startswith('tel:'):
                            continue
                        # Convertir les URLs relatives en URLs absolues
                        if not href.startswith('http'):
                            href = urljoin(base_url, href)
                        # Ne garder que les URLs du même domaine
                        if urlparse(href).netloc == base_domain:
                            all_urls.add(href)
            except Exception as e:
                logger.error(f"Erreur lors de l'exploration avec Crawl4AI pour {base_url}: {e}")
            finally:
                loop.close()
        except Exception as e:
            logger.error(f"Erreur générale avec Crawl4AI pour {base_url}: {e}")
        
        # Méthode 2: Explorer les chemins courants pour les sites web
        try:
            logger.info(f"Exploration des chemins courants pour {base_url}")
            common_paths = [
                '/', '/about', '/about-us', '/contact', '/contact-us', '/products', '/services',
                '/blog', '/news', '/faq', '/help', '/support', '/menu', '/locations', '/store',
                '/shop', '/cart', '/account', '/login', '/register', '/privacy', '/terms',
                '/sitemap', '/search', '/gallery', '/portfolio', '/team', '/careers', '/jobs',
                '/events', '/offers', '/promotions', '/pricing', '/testimonials', '/reviews'
            ]
            
            for path in common_paths:
                url = urljoin(base_url, path)
                if url not in all_urls:
                    all_urls.add(url)
        except Exception as e:
            logger.error(f"Erreur lors de l'exploration des chemins courants pour {base_url}: {e}")
        
        # Si aucune URL n'a été trouvée, au moins garder l'URL de base
        if len(all_urls) <= 1:  # Seulement l'URL de base
            logger.warning(f"Peu ou pas d'URLs trouvées pour {base_url}, utilisation de la méthode avancée")
            return self.extract_urls_with_crawl4ai_advanced(base_url)
            
        logger.info(f"Extraction terminée pour {base_url}: {len(all_urls)} URLs trouvées")
        return list(all_urls)
        
    def extract_urls_with_crawl4ai_advanced(self, base_url):
        """
        Méthode avancée d'extraction des URLs utilisant Crawl4AI pour les sites avec JavaScript
        et peu ou pas de sitemap disponible. Capture uniquement les vraies URLs web (pages)
        et ignore les ressources comme les images, CSS, JS, etc.
        
        Args:
            base_url (str): URL de base du site
            
        Returns:
            list: Liste des URLs trouvées
        """
        logger.info(f"Démarrage de l'extraction avancée avec Crawl4AI pour {base_url}")
        all_urls = set([base_url])  # Commencer par la page d'accueil
        processed_urls = set()
        pending_urls = set([base_url])
        base_domain = urlparse(base_url).netloc
        
        # Extensions de fichiers à ignorer (ressources, pas des pages web)
        resource_extensions = [
            '.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.ico', '.bmp', '.tiff',  # Images
            '.css', '.js', '.json', '.xml', '.csv', '.txt',  # Fichiers de données et styles
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',  # Documents
            '.zip', '.rar', '.tar', '.gz', '.7z',  # Archives
            '.mp3', '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm',  # Médias
            '.woff', '.woff2', '.ttf', '.eot', '.otf',  # Polices
            '.webmanifest', '.map'  # Autres ressources web
        ]
        
        # Limiter le nombre d'URLs à explorer pour éviter une exploration infinie
        max_urls_to_explore = 5  # Réduit pour accélérer le processus
        
        # Explorer les pages trouvées pour découvrir plus de liens
        try:
            logger.info(f"Exploration rapide avec Crawl4AI pour {base_url}")
            
            # Utiliser Crawl4AI uniquement pour la page d'accueil pour accélérer
            async def crawl_home_page(url):
                async with AsyncWebCrawler() as crawler:
                    result = await crawler.arun(url=url)
                    return result
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(crawl_home_page(base_url))
                if hasattr(result, 'html') and result.html:
                    soup = BeautifulSoup(result.html, 'html.parser')
                    
                    # Extraire uniquement les liens <a href> (vraies pages web)
                    for a_tag in soup.find_all('a', href=True):
                        href = a_tag['href']
                        # Ignorer les liens vides, les ancres et les liens externes
                        if not href or href.startswith('#') or href.startswith('mailto:') or href.startswith('tel:'):
                            continue
                        # Convertir les URLs relatives en URLs absolues
                        if not href.startswith('http'):
                            href = urljoin(base_url, href)
                        # Ne garder que les URLs du même domaine
                        if urlparse(href).netloc == base_domain:
                            # Vérifier si c'est une ressource à ignorer
                            parsed_href = urlparse(href)
                            path = parsed_href.path.lower()
                            if any(path.endswith(ext) for ext in resource_extensions):
                                continue  # Ignorer les ressources
                            
                            # Nettoyer l'URL (enlever les paramètres de requête et fragments)
                            clean_href = f"{parsed_href.scheme}://{parsed_href.netloc}{parsed_href.path}"
                            all_urls.add(clean_href)
                    
                    # Rechercher d'autres URLs dans le HTML qui pourraient être des pages web
                    import re
                    url_pattern = re.compile(r'https?://[^\s\'\"<>\)\(]+\.[^\s\'\"<>\)\(]+[^\s\'\"<>\)\(]*')
                    for match in url_pattern.finditer(result.html):
                        found_url = match.group(0).strip('"\'\'\"')
                        # Ne garder que les URLs du même domaine
                        if urlparse(found_url).netloc == base_domain:
                            # Vérifier si c'est une ressource à ignorer
                            parsed_found = urlparse(found_url)
                            path = parsed_found.path.lower()
                            if any(path.endswith(ext) for ext in resource_extensions):
                                continue  # Ignorer les ressources
                            
                            # Nettoyer l'URL
                            clean_found = f"{parsed_found.scheme}://{parsed_found.netloc}{parsed_found.path}"
                            all_urls.add(clean_found)
            except Exception as e:
                logger.error(f"Erreur lors de l'exploration de {base_url} avec Crawl4AI: {e}")
            finally:
                loop.close()
        except Exception as e:
            logger.error(f"Erreur lors de l'exploration rapide pour {base_url}: {e}")
        
        # Si aucune URL n'a été trouvée, au moins garder l'URL de base
        if len(all_urls) == 0:
            all_urls.add(base_url)
        
        logger.info(f"Extraction avancée terminée pour {base_url}: {len(all_urls)} URLs trouvées")
        return list(all_urls)
