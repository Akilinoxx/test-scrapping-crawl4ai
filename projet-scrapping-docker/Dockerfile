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

# Copier le reste du code source
COPY . .

# Créer le répertoire de sortie
RUN mkdir -p /app/scraped_links

# Commande à exécuter au démarrage du conteneur
CMD ["python", "app.py"]