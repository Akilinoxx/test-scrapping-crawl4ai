# Utiliser une image de base avec Python 3.10
FROM python:3.10-slim

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    build-essential \
    libxml2-dev \
    libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir html2text==2020.1.16

# Installer Playwright pour Crawl4AI
RUN python -m playwright install --with-deps chromium

# Copier les fichiers de l'application
COPY src/app.py .
COPY src/content_scraper.py .
COPY src/sitemap_extractor_simple.py .
COPY src/run_scraper.py .
COPY src/run_content_scraper.py .
COPY src/scrape_one_site.py .
COPY src/scrape_new_site.py .
COPY sites_example.txt .

# Créer le répertoire de sortie
RUN mkdir -p /app/scraped_links

# Commande à exécuter au démarrage du conteneur
CMD ["python", "app.py"]