import os
import json
import asyncio
from crawl4ai import AsyncWebCrawler
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse

# Suppression du logging pour accélérer l'exécution

class ContentScraper:
    def __init__(self, input_dir='scraped_links', output_dir='scraped_content', max_workers=10, delay=0):
        """
        Initialise le scraper de contenu
        
        Args:
            input_dir (str): Répertoire contenant les URLs extraites des sitemaps
            output_dir (str): Répertoire de sortie pour le contenu scrapé
            max_workers (int): Nombre maximum de workers pour le threading
            delay (float): Délai entre les requêtes (en secondes) - mis à 0 pour accélérer
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.max_workers = max_workers
        self.delay = 0  # Aucun délai entre les requêtes pour accélérer
        
        # Création du répertoire de sortie s'il n'existe pas
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def clean_text(self, text):
        """
        Nettoie le texte extrait
        
        Args:
            text (str): Texte à nettoyer
            
        Returns:
            str: Texte nettoyé
        """
        if not text:
            return ""
        
        # Supprimer les espaces multiples et les sauts de ligne
        text = re.sub(r'\s+', ' ', text)
        # Supprimer les espaces en début et fin de chaîne
        text = text.strip()
        return text
    
    def extract_content(self, html):
        """
        Extrait le contenu principal d'une page HTML
        
        Args:
            html (str): Contenu HTML de la page
            
        Returns:
            dict: Dictionnaire contenant le titre, la description et le contenu principal
        """
        if not html:
            return {
                "title": "",
                "description": "",
                "content": "",
                "headings": []
            }
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extraire le titre
        title = ""
        title_tag = soup.find('title')
        if title_tag:
            title = self.clean_text(title_tag.text)
        
        # Extraire la description
        description = ""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            description = self.clean_text(meta_desc.get('content'))
        
        # Extraire les titres (h1, h2, h3)
        headings = []
        for h in soup.find_all(['h1', 'h2', 'h3']):
            headings.append({
                'level': int(h.name[1]),
                'text': self.clean_text(h.text)
            })
        
        # Extraire le contenu principal (stratégie simple)
        content = ""
        
        # Essayer de trouver le contenu principal avec des sélecteurs courants
        main_selectors = [
            'main', 'article', '#content', '.content', '#main', '.main',
            '.post', '.entry', '.page-content', '.article-content'
        ]
        
        main_content = None
        for selector in main_selectors:
            if selector.startswith('#'):
                main_content = soup.find(id=selector[1:])
            elif selector.startswith('.'):
                main_content = soup.find(class_=selector[1:])
            else:
                main_content = soup.find(selector)
            
            if main_content:
                break
        
        # Si aucun contenu principal n'est trouvé, prendre le body
        if not main_content:
            main_content = soup.find('body')
        
        if main_content:
            # Supprimer les scripts, styles et commentaires
            for element in main_content.find_all(['script', 'style', 'nav', 'header', 'footer']):
                element.decompose()
            
            # Extraire le texte
            content = self.clean_text(main_content.get_text())
        
        return {
            "title": title,
            "description": description,
            "content": content,
            "headings": headings
        }
    
    def convert_to_markdown(self, content_data, url):
        """
        Convertit les données extraites en format Markdown
        
        Args:
            content_data (dict): Données extraites
            url (str): URL de la page
            
        Returns:
            str: Contenu formaté en Markdown
        """
        markdown = f"# {content_data['title']}\n\n"
        markdown += f"**URL:** {url}\n\n"
        
        if content_data['description']:
            markdown += f"**Description:** {content_data['description']}\n\n"
        
        if content_data['headings']:
            markdown += "## Structure de la page\n\n"
            for heading in content_data['headings']:
                indent = "  " * (heading['level'] - 1)
                markdown += f"{indent}- {heading['text']}\n"
            markdown += "\n"
        
        if content_data['content']:
            markdown += "## Contenu\n\n"
            # Limiter la taille du contenu pour éviter des fichiers trop volumineux
            content = content_data['content']
            if len(content) > 5000:
                content = content[:5000] + "...\n\n[Contenu tronqué]"
            markdown += content + "\n\n"
        
        return markdown
    
    async def scrape_url(self, url):
        """
        Scrape une URL en utilisant Crawl4AI avec des paramètres optimisés pour la vitesse
        
        Args:
            url (str): URL à scraper
            
        Returns:
            dict: Données extraites
        """
        try:
            # Utiliser des paramètres optimisés pour la vitesse
            async with AsyncWebCrawler() as crawler:
                # Paramètres optimisés pour la vitesse:
                # - timeout réduit
                # - pas d'attente pour le chargement complet
                # - pas de capture d'écran
                result = await crawler.arun(
                    url=url,
                    timeout=10,  # Timeout réduit à 10 secondes
                    wait_until="domcontentloaded"  # Ne pas attendre le chargement complet
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
    
    async def scrape_url_batch(self, urls):
        """
        Scrape un lot d'URLs en parallèle
        
        Args:
            urls (list): Liste des URLs à scraper
            
        Returns:
            dict: Résultats du scraping
        """
        tasks = []
        for url in urls:
            tasks.append(self.scrape_url(url))
        
        results = await asyncio.gather(*tasks)
        return dict(zip(urls, results))
    
    async def scrape_site_urls(self, site_name, urls, max_urls=0):
        """
        Scrape les URLs d'un site et stocke tout le contenu dans un seul fichier markdown
        
        Args:
            site_name (str): Nom du site
            urls (list): Liste des URLs à scraper
            max_urls (int): Nombre maximum d'URLs à scraper (0 = toutes)
            
        Returns:
            dict: Résultats du scraping
        """
        print(f"Scraping de {len(urls)} URLs pour {site_name}")
        
        # Créer le répertoire de sortie
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        # Préparer le contenu markdown pour le site entier
        site_markdown = f"# Contenu du site {site_name}\n\n"
        site_markdown += f"## Liste des URLs ({len(urls)})\n\n"
        
        for i, url in enumerate(urls):
            site_markdown += f"{i+1}. [{url}]({url})\n"
        
        site_markdown += "\n## Contenu des pages\n\n"
        
        # Diviser les URLs en lots pour le traitement parallèle
        batch_size = 5  # Nombre d'URLs à traiter en parallèle
        batches = [urls[i:i + batch_size] for i in range(0, len(urls), batch_size)]
        
        all_results = {}
        for batch_index, batch in enumerate(batches):
            print(f"Traitement du lot {batch_index+1}/{len(batches)} ({len(batch)} URLs)")
            
            # Scraper le lot d'URLs en parallèle
            batch_results = await self.scrape_url_batch(batch)
            all_results.update(batch_results)
            
            # Ajouter les résultats au markdown
            for url, content_data in batch_results.items():
                i = urls.index(url)
                
                # Ajouter le contenu au markdown global
                site_markdown += f"### {i+1}. {content_data['title'] or url}\n\n"
                site_markdown += f"**URL:** {url}\n\n"
                
                if content_data['description']:
                    site_markdown += f"**Description:** {content_data['description']}\n\n"
                
                if content_data['headings']:
                    site_markdown += "#### Structure de la page\n\n"
                    for heading in content_data['headings']:
                        indent = "  " * (heading['level'] - 1)
                        site_markdown += f"{indent}- {heading['text']}\n"
                    site_markdown += "\n"
                
                if content_data['content']:
                    site_markdown += "#### Contenu\n\n"
                    # Limiter la taille du contenu pour éviter des fichiers trop volumineux
                    content = content_data['content']
                    if len(content) > 1000:  # Limité à 1000 caractères par page
                        content = content[:1000] + "...\n\n[Contenu tronqué]"
                    site_markdown += content + "\n\n"
                    site_markdown += "---\n\n"  # Séparateur entre les pages
        
        # Sauvegarder le fichier markdown unique pour le site
        file_path = os.path.join(self.output_dir, f"{site_name}.md")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(site_markdown)
        
        print(f"Sauvegardé {file_path} avec le contenu de {len(urls)} URLs")
        
        return all_results
    
    async def process_site(self, site_dir):
        """
        Traite un site individuel
        
        Args:
            site_dir (str): Nom du répertoire du site
            
        Returns:
            tuple: (site_name, résultats) ou None en cas d'erreur
        """
        site_path = os.path.join(self.input_dir, site_dir)
        urls_file = os.path.join(site_path, 'sitemap_urls.json')
        
        if not os.path.exists(urls_file):
            print(f"ERREUR: Fichier {urls_file} non trouvé pour le site {site_dir}")
            return None
        
        try:
            print(f"Traitement du site: {site_dir}")
            with open(urls_file, 'r', encoding='utf-8') as f:
                urls = json.load(f)
            
            print(f"Site {site_dir}: {len(urls)} URLs trouvées")
            
            # Scraper les URLs du site
            site_results = await self.scrape_site_urls(site_dir, urls)
            print(f"Terminé pour {site_dir}: {len(site_results)} URLs scrapées")
            return (site_dir, site_results)
        except Exception as e:
            print(f"ERREUR lors du traitement de {site_dir}: {str(e)}")
            return None
    
    async def scrape_all_sites(self, max_urls_per_site=0):
        """
        Scrape tous les sites en parallèle et stocke chaque site dans un seul fichier markdown
        
        Args:
            max_urls_per_site (int): Ignoré dans cette version
            
        Returns:
            dict: Résultats du scraping pour tous les sites
        """
        print(f"Démarrage du scraping pour tous les sites dans {self.input_dir}")
        
        # Trouver tous les répertoires de sites
        site_dirs = [d for d in os.listdir(self.input_dir) 
                    if os.path.isdir(os.path.join(self.input_dir, d))]        
        
        # Traiter tous les sites en parallèle
        tasks = [self.process_site(site_dir) for site_dir in site_dirs]
        results = await asyncio.gather(*tasks)
        
        # Filtrer les résultats None (erreurs)
        valid_results = [r for r in results if r is not None]
        
        # Construire le dictionnaire de résultats et la liste des sites
        all_results = {site: result for site, result in valid_results}
        all_sites = [site for site, _ in valid_results]
        
        # Créer un index global
        index_markdown = "# Index global des sites scrapés\n\n"
        for site_name in all_sites:
            index_markdown += f"- [{site_name}](./{site_name}.md)\n"
        
        index_path = os.path.join(self.output_dir, 'index.md')
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(index_markdown)
        
        print(f"Scraping terminé pour {len(all_sites)} sites. Index global créé à {index_path}")
        return all_results

# Fonction principale pour lancer le scraping
async def scrape_sites(input_dir='scraped_links', output_dir='scraped_content_md', specific_site=''):
    """
    Lance le scraping des sites
    
    Args:
        input_dir (str): Répertoire contenant les URLs extraites des sitemaps
        output_dir (str): Répertoire de sortie pour les fichiers markdown
        specific_site (str): Nom spécifique d'un site à scraper (optionnel)
    """
    scraper = ContentScraper(input_dir=input_dir, output_dir=output_dir)
    
    # Si un site spécifique est demandé
    if specific_site:
        site_path = os.path.join(input_dir, specific_site)
        urls_file = os.path.join(site_path, 'sitemap_urls.json')
        
        if os.path.exists(urls_file):
            try:
                with open(urls_file, 'r', encoding='utf-8') as f:
                    urls = json.load(f)
                
                print(f"Scraping du site spécifique {specific_site} avec {len(urls)} URLs")
                await scraper.scrape_site_urls(specific_site, urls)
                print(f"Scraping terminé pour {specific_site}. Résultats sauvegardés dans {output_dir}/{specific_site}.md")
            except Exception as e:
                print(f"Erreur lors du scraping du site spécifique {specific_site}: {e}")
        else:
            print(f"Site {specific_site} non trouvé ou pas de fichier sitemap_urls.json")
    else:
        # Scraper tous les sites
        await scraper.scrape_all_sites()
        print(f"Scraping terminé pour tous les sites. Résultats sauvegardés dans {output_dir}")

