# Crawl4AI - Extracteur de Sitemap et Scraper

Ce projet permet d'extraire les sitemaps de sites web, puis de scraper le contenu des pages référencées dans ces sitemaps. Les données scrapées sont stockées dans des fichiers JSON pour une utilisation ultérieure, comme l'intégration dans une base de données vectorielle.

## Fonctionnalités

- Extraction automatique des sitemaps à partir des fichiers robots.txt
- Gestion des sitemaps imbriqués (sitemap index)
- Scraping parallélisé des URLs avec gestion des délais
- Sauvegarde des données au format JSON
- Mode "sitemap only" pour extraire uniquement les URLs sans scraper le contenu
- Statistiques détaillées sur le processus de scraping

## Prérequis

- Python 3.10 ou supérieur
- Docker (pour l'exécution en conteneur)

## Installation

### Option 1: Utilisation avec Docker

1. Construire l'image Docker :
```bash
docker-compose build
```

2. Exécuter le conteneur :
```bash
docker-compose up
```

### Option 2: Installation locale

1. Installer les dépendances :
```bash
pip install -r requirements.txt
```

2. Installer Playwright (utilisé par Crawl4AI) :
```bash
python -m playwright install
```

## Utilisation

### Ligne de commande

```bash
python app.py --sites https://www.example.com https://www.another-site.com --output-dir scraped_data
```

### Options disponibles

- `--sites`, `-s` : Liste des URLs des sites à traiter
- `--sites-file`, `-f` : Chemin vers un fichier contenant les URLs des sites (une par ligne)
- `--output-dir`, `-o` : Répertoire de sortie pour les données scrapées (par défaut: 'scraped_links')
- `--max-workers`, `-w` : Nombre maximum de workers pour le threading (par défaut: 5)
- `--delay`, `-d` : Délai entre les requêtes en secondes (par défaut: 1.0)
- `--sitemap-only` : Extraire uniquement les URLs des sitemaps sans scraper les pages

### Exemple avec un fichier de sites

1. Créer un fichier `sites.txt` contenant les URLs des sites à scraper (une par ligne) :
```
https://www.example.com
https://www.python.org
# Ceci est un commentaire
https://www.another-site.com
```

2. Exécuter le script avec ce fichier :
```bash
python app.py --sites-file sites.txt --output-dir scraped_data
```

## Structure des données

Les données scrapées sont organisées comme suit :

```
scraped_links/
  ├── example_com/
  │   ├── scraped_data_100.json
  │   ├── scraped_data_200.json
  │   └── ...
  ├── python_org/
  │   ├── scraped_data_100.json
  │   ├── scraped_data_200.json
  │   └── ...
  ├── example_com_stats.json
  ├── python_org_stats.json
  └── global_stats.json
```

Chaque fichier JSON contient les données scrapées au format suivant :

```json
[
  {
    "url": "https://www.example.com/page1",
    "title": "Titre de la page",
    "content": "Contenu textuel de la page",
    "html": "HTML brut de la page",
    "timestamp": 1621234567.89
  },
  ...
]
```

## Intégration avec une base vectorielle

Les données scrapées peuvent être facilement intégrées dans une base de données vectorielle comme Pinecone. Un module de vectorisation est inclus dans ce projet.

### Vectorisation avec LangChain et Pinecone

1. Installer les dépendances supplémentaires :
```bash
pip install -r requirements_vector.txt
```

2. Exécuter le script de vectorisation :
```bash
python vectorize_content.py --pinecone-api-key YOUR_PINECONE_API_KEY --openai-api-key YOUR_OPENAI_API_KEY
```

3. Options disponibles pour la vectorisation :
   - `--data-dir` : Répertoire contenant les données scrapées (par défaut: './scraped_links')
   - `--pinecone-api-key` : Clé API Pinecone (obligatoire)
   - `--pinecone-environment` : Environnement Pinecone (par défaut: 'gcp-starter')
   - `--pinecone-index` : Nom de l'index Pinecone (par défaut: 'scraped-sites')
   - `--openai-api-key` : Clé API OpenAI pour les embeddings (obligatoire)
   - `--chunk-size` : Taille des chunks pour le découpage du texte (par défaut: 1000)
   - `--chunk-overlap` : Chevauchement des chunks (par défaut: 200)

### Utilisation avec Docker

1. Construire l'image Docker pour la vectorisation :
```bash
docker-compose -f docker-compose.vector.yml build
```

2. Exécuter le conteneur avec vos clés API :
```bash
PINECONE_API_KEY=your_pinecone_key OPENAI_API_KEY=your_openai_key docker-compose -f docker-compose.vector.yml up
```

## Limitations

- Le scraping respecte les règles de robots.txt mais n'implémente pas de mécanisme avancé de rate limiting
- Les sites avec une protection anti-bot avancée peuvent bloquer le scraping
- La performance dépend de la qualité de la connexion internet et des ressources système disponibles
