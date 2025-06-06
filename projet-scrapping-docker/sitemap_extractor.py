import os
import json
import requests
import logging
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
from crawl4ai import AsyncWebCrawler
import html2text

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('sitemap_extractor')

class SitemapExtractor:
    def __init__(self, output_dir='scraped_links', max_workers=5, delay=1):
        """
        Initialise l'extracteur de sitemap
        
        Args:
            output_dir (str): Répertoire de sortie pour les données scrapées
            max_workers (int): Nombre maximum de workers pour le threading
            delay (float): Délai entre les requêtes (en secondes)
        """
        self.output_dir = output_dir
        self.max_workers = max_workers
        self.delay = delay
        
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
        
        # Si aucun sitemap n'est trouvé, essayer des approches alternatives
        if not pending_sitemaps:
            logger.warning(f"Aucun sitemap trouvé pour {base_url}, utilisation de méthodes alternatives")
            return self.extract_urls_without_sitemap(base_url)
        
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
            
            # Respecter un délai entre les requêtes
            time.sleep(self.delay)
        
        # Si peu d'URLs ont été trouvées, compléter avec des méthodes alternatives
        if len(all_urls) < 5:
            logger.warning(f"Peu d'URLs trouvées dans les sitemaps de {base_url}, utilisation de méthodes alternatives")
            additional_urls = self.extract_urls_without_sitemap(base_url)
            all_urls.update(additional_urls)
        
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
        processed_urls = set()
        pending_urls = set([base_url])
        base_domain = urlparse(base_url).netloc
        
        # Ajouter quelques URLs de base pour s'assurer d'avoir au moins quelque chose à scraper
        logger.info(f"Ajout d'URLs de base pour {base_url}")
        all_urls.add(base_url)
        all_urls.add(base_url + "/")
        
        # Limiter le nombre d'URLs à explorer pour éviter une exploration infinie
        max_urls_to_explore = 100  # Augmenté pour une meilleure couverture
        max_urls_to_return = 500   # Augmenté pour une meilleure couverture
        
        # Méthode 1: Utiliser Crawl4AI pour explorer la page d'accueil avec JavaScript
        try:
            logger.info(f"Méthode 1: Exploration avec Crawl4AI pour {base_url}")
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
                            pending_urls.add(href)
                            all_urls.add(href)
            except Exception as e:
                logger.error(f"Erreur lors de l'exploration avec Crawl4AI pour {base_url}: {e}")
            finally:
                loop.close()
        except Exception as e:
            logger.error(f"Erreur générale avec Crawl4AI pour {base_url}: {e}")
        
        # Méthode 2: Explorer les pages trouvées pour découvrir plus de liens
        try:
            logger.info(f"Méthode 2: Exploration récursive des liens pour {base_url}")
            while pending_urls and len(processed_urls) < max_urls_to_explore:
                url = pending_urls.pop()
                if url in processed_urls:
                    continue
                
                logger.info(f"Exploration de {url} pour trouver des liens")
                processed_urls.add(url)
                
                try:
                    # Utiliser Crawl4AI pour chaque page pour gérer le JavaScript
                    async def crawl_page(url):
                        async with AsyncWebCrawler() as crawler:
                            result = await crawler.arun(url=url)
                            return result
                    
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        result = loop.run_until_complete(crawl_page(url))
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
                                    # Ajouter à la liste des URLs à explorer si on n'a pas atteint la limite
                                    if len(processed_urls) < max_urls_to_explore and href not in processed_urls:
                                        pending_urls.add(href)
                    except Exception as e:
                        logger.error(f"Erreur lors de l'exploration de {url} avec Crawl4AI: {e}")
                        # Fallback à requests si Crawl4AI échoue
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
                                        # Ajouter à la liste des URLs à explorer si on n'a pas atteint la limite
                                        if len(processed_urls) < max_urls_to_explore and href not in processed_urls:
                                            pending_urls.add(href)
                        except Exception as e:
                            logger.error(f"Erreur lors de l'exploration de {url} avec requests: {e}")
                    finally:
                        loop.close()
                except Exception as e:
                    logger.error(f"Erreur générale lors de l'exploration de {url}: {e}")
                
                # Respecter un délai entre les requêtes
                time.sleep(self.delay)
        except Exception as e:
            logger.error(f"Erreur lors de l'exploration récursive pour {base_url}: {e}")
        
        # Méthode 3: Explorer les chemins courants pour les sites web
        try:
            logger.info(f"Méthode 3: Exploration des chemins courants pour {base_url}")
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
        
        # Vérifier si nous avons trouvé suffisamment d'URLs
        if len(all_urls) < 10:
            logger.warning(f"Peu d'URLs trouvées pour {base_url}, utilisation de méthodes supplémentaires")
            # Méthode 4: Essayer de deviner les URLs basées sur le nom de domaine
            try:
                domain_name = base_domain.split('.')[0]
                if domain_name not in ['www', 'com', 'fr', 'net', 'org']:
                    additional_paths = [
                        f'/{domain_name}', f'/about-{domain_name}', f'/{domain_name}-info',
                        f'/our-{domain_name}', f'/{domain_name}-services', f'/{domain_name}-products'
                    ]
                    for path in additional_paths:
                        url = urljoin(base_url, path)
                        if url not in all_urls:
                            all_urls.add(url)
            except Exception as e:
                logger.error(f"Erreur lors de la génération d'URLs basées sur le domaine pour {base_url}: {e}")
        
        logger.info(f"Extraction terminée pour {base_url}: {len(all_urls)} URLs trouvées")
        
        # Limiter le nombre d'URLs retournées
        return list(all_urls)[:max_urls_to_return]
    
    def scrape_url(self, url):
        """
        Scrape une URL et extrait son contenu en utilisant Crawl4AI
        
        Args:
            url (str): URL à scraper
            
        Returns:
            dict: Données scrapées (URL, titre, contenu, etc.)
        """
        try:
            # Utiliser Crawl4AI pour scraper la page
            async def crawl_page(url):
                async with AsyncWebCrawler() as crawler:
                    result = await crawler.arun(url=url)
                    return result
            
            # Exécuter la fonction asynchrone dans une boucle d'événements
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(crawl_page(url))
            finally:
                loop.close()
            
            # Récupérer le titre de la page
            title = url  # Valeur par défaut
            try:
                # Essayer de récupérer le titre depuis l'attribut html
                if hasattr(result, 'html') and result.html:
                    soup = BeautifulSoup(result.html, 'html.parser')
                    if soup.title:
                        title = soup.title.text.strip()
            except:
                pass
            
            # Récupérer le contenu markdown
            markdown_content = ""
            if hasattr(result, 'markdown') and result.markdown:
                markdown_content = result.markdown
            
            # Récupérer le contenu texte
            text_content = ""
            if hasattr(result, 'text') and result.text:
                text_content = result.text
            
            # Extraire les informations pertinentes
            data = {
                'url': url,
                'title': title,
                'content_markdown': markdown_content,
                'content_text': text_content,
                'timestamp': time.time()
            }
            
            return data
        except Exception as e:
            logger.error(f"Erreur lors du scraping de {url}: {e}")
            return None
    
    def scrape_urls(self, urls, site_name):
        """
        Scrape une liste d'URLs et sauvegarde les résultats
        
        Args:
            urls (list): Liste d'URLs à scraper
            site_name (str): Nom du site (pour le fichier de sortie)
            
        Returns:
            int: Nombre d'URLs scrapées avec succès
        """
        success_count = 0
        all_content = []
        
        # Créer un répertoire spécifique pour ce site
        site_dir = os.path.join(self.output_dir, site_name)
        if not os.path.exists(site_dir):
            os.makedirs(site_dir)
        
        logger.info(f"Démarrage du scraping de {len(urls)} URLs pour {site_name}")
        
        # Utiliser ThreadPoolExecutor pour paralléliser les requêtes
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            for i, result in enumerate(executor.map(self.scrape_url, urls)):
                if result:
                    # Préparer le contenu markdown pour cette URL
                    page_content = f"\n\n## {result['title']}\n\n"
                    page_content += f"URL: {result['url']}\n\n"
                    page_content += f"Date: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(result['timestamp']))}\n\n"
                    page_content += f"---\n\n"
                    page_content += result['content_markdown']
                    page_content += "\n\n" + "="*80 + "\n\n"  # Séparateur entre les pages
                    
                    # Ajouter au contenu global
                    all_content.append(page_content)
                    
                    success_count += 1
                
                # Afficher la progression
                if (i + 1) % 10 == 0 or i == len(urls) - 1:
                    logger.info(f"Progression: {i+1}/{len(urls)} URLs traitées ({success_count} réussies)")
                    
                    # Sauvegarder périodiquement le contenu pour éviter de perdre des données
                    if all_content:
                        # Créer un fichier markdown avec tout le contenu jusqu'à présent
                        markdown_file = os.path.join(site_dir, f"{site_name}_content.md")
                        with open(markdown_file, 'w', encoding='utf-8') as f:
                            f.write(f"# Contenu scrapé de {site_name}\n\n")
                            f.write(f"Date de scraping: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                            f.write(f"Nombre d'URLs scrapées: {success_count}/{len(urls)}\n\n")
                            f.write("="*80 + "\n\n")
                            f.write(''.join(all_content))
        
        # Créer un fichier index des URLs scrapées
        index_file = os.path.join(site_dir, "index.json")
        index_data = {
            'site_name': site_name,
            'total_urls': len(urls),
            'scraped_urls': success_count,
            'timestamp': time.time(),
            'markdown_file': f"{site_name}_content.md"
        }
        
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)
        
        # Sauvegarder également les URLs dans un fichier texte
        urls_file = os.path.join(site_dir, f"{site_name}_urls.txt")
        with open(urls_file, 'w', encoding='utf-8') as f:
            for url in urls:
                f.write(f"{url}\n")
        
        logger.info(f"Scraping terminé pour {site_name}. {success_count}/{len(urls)} URLs scrapées avec succès")
        return success_count
    
    def process_site(self, site_url, max_urls=0):
        """
        Traite un site complet: extraction du sitemap et scraping des URLs
        
        Args:
            site_url (str): URL du site à traiter
            max_urls (int): Nombre maximum d'URLs à scraper (0 = illimité)
            
        Returns:
            dict: Statistiques du traitement
        """
        # Extraire le nom du domaine pour l'utiliser comme nom de site
        parsed_url = urlparse(site_url)
        site_name = parsed_url.netloc.replace('.', '_')
        
        logger.info(f"Démarrage du traitement pour le site: {site_url}")
        
        # TOUJOURS utiliser la méthode alternative pour tous les sites
        # Cette approche garantit que nous aurons des URLs même pour les sites sans sitemap
        logger.info(f"Extraction des URLs avec méthodes alternatives pour {site_url}")
        start_time = time.time()
        alt_urls = self.extract_urls_without_sitemap(site_url)
        
        # Essayer également d'extraire les URLs du sitemap comme complément
        try:
            sitemap_urls = self.extract_all_urls_from_sitemap(site_url)
            logger.info(f"{len(sitemap_urls)} URLs trouvées dans le sitemap de {site_url}")
            # Combiner les URLs des deux méthodes
            all_urls = list(set(alt_urls + sitemap_urls))
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction du sitemap de {site_url}: {e}")
            all_urls = alt_urls
        
        sitemap_time = time.time() - start_time
        logger.info(f"Total: {len(all_urls)} URLs uniques pour {site_url}")
        
        # S'assurer qu'il y a au moins une URL à scraper (la page d'accueil)
        if len(all_urls) == 0:
            logger.warning(f"Aucune URL trouvée pour {site_url}, ajout de la page d'accueil")
            all_urls = [site_url]
            
        urls = all_urls
        
        # Limiter le nombre d'URLs si max_urls est spécifié
        if max_urls > 0 and len(urls) > max_urls:
            logger.info(f"Limitation à {max_urls} URLs sur les {len(urls)} trouvées")
            urls = urls[:max_urls]
        
        # Scraper les URLs
        start_time = time.time()
        success_count = self.scrape_urls(urls, site_name)
        scraping_time = time.time() - start_time
        
        # Statistiques du traitement
        stats = {
            'site_url': site_url,
            'site_name': site_name,
            'total_urls': len(urls),
            'scraped_urls': success_count,
            'sitemap_extraction_time': sitemap_time,
            'scraping_time': scraping_time,
            'total_time': sitemap_time + scraping_time
        }
        
        # Sauvegarder les statistiques
        stats_file = os.path.join(self.output_dir, f"{site_name}_stats.json")
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Traitement terminé pour {site_url}")
        return stats

# Fonction utilitaire pour exécuter le scraping sur plusieurs sites
def process_multiple_sites(sites, output_dir='scraped_links', max_workers=5, delay=1, max_urls=0):
    """
    Traite plusieurs sites en séquence
    
    Args:
        sites (list): Liste des URLs des sites à traiter
        output_dir (str): Répertoire de sortie
        max_workers (int): Nombre maximum de workers pour le threading
        delay (float): Délai entre les requêtes
        max_urls (int): Nombre maximum d'URLs à scraper par site (0 = illimité)
        
    Returns:
        list: Statistiques pour chaque site traité
    """
    extractor = SitemapExtractor(output_dir=output_dir, max_workers=max_workers, delay=delay)
    all_stats = []
    
    for site_url in sites:
        stats = extractor.process_site(site_url, max_urls=max_urls)
        all_stats.append(stats)
    
    # Sauvegarder les statistiques globales
    global_stats_file = os.path.join(output_dir, "global_stats.json")
    with open(global_stats_file, 'w', encoding='utf-8') as f:
        json.dump(all_stats, f, ensure_ascii=False, indent=2)
    
    return all_stats
