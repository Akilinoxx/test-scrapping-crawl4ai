# 📦 Guide d'Installation

Ce guide vous accompagne dans l'installation et la configuration du projet Web Scraping AI Chatbot.

## 🎯 Prérequis

### Système
- **Python 3.10+** (recommandé: 3.11)
- **Docker Desktop** (pour l'utilisation avec conteneurs)
- **Git** (pour cloner le projet)

### Clés API Requises
- **Mistral AI** : [Créer un compte](https://console.mistral.ai/)
- **Pinecone** : [Créer un compte](https://www.pinecone.io/)

## 🚀 Installation Rapide

### 1. Cloner le Projet
```bash
git clone https://github.com/votre-username/web-scraping-ai-chatbot.git
cd web-scraping-ai-chatbot
```

### 2. Configuration des Variables d'Environnement
```bash
# Copier le template
cp .env.example .env

# Éditer avec vos clés API
nano .env  # ou votre éditeur préféré
```

Contenu du fichier `.env` :
```env
# Clés API
MISTRAL_API_KEY=votre_cle_mistral_ici
PINECONE_API_KEY=votre_cle_pinecone_ici
PINECONE_HOST=votre_host_pinecone_ici

# Configuration Scraper
SCRAPER_DELAY=1
MAX_WORKERS=5
```

## 🐳 Installation avec Docker (Recommandée)

### Avantages
- ✅ Isolation complète
- ✅ Pas de conflits de dépendances
- ✅ Déploiement facile
- ✅ Reproductibilité garantie

### Étapes
```bash
# Construire toutes les images
./scripts/run-docker.sh build        # Linux/Mac
.\scripts\run-docker.bat build       # Windows

# Lancer le pipeline complet
./scripts/run-docker.sh all          # Linux/Mac
.\scripts\run-docker.bat all         # Windows
```

### Services Disponibles
```bash
# Scraper uniquement
./scripts/run-docker.sh scraper

# Vectorisation uniquement
./scripts/run-docker.sh vectorizer

# Chatbot uniquement
./scripts/run-docker.sh chatbot

# Tout nettoyer
./scripts/run-docker.sh clean
```

## 💻 Installation Locale

### 1. Environnement Virtuel
```bash
# Créer l'environnement
python -m venv venv

# Activer l'environnement
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows
```

### 2. Installation des Dépendances
```bash
# Dépendances principales
pip install -r requirements_vector.txt

# Dépendances de développement (optionnel)
pip install -r requirements-dev.txt

# Installation en mode développement
pip install -e .
```

### 3. Installation de Playwright
```bash
# Installer les navigateurs
python -m playwright install

# Avec dépendances système (Linux)
python -m playwright install --with-deps
```

## 🔧 Configuration Avancée

### Pinecone
1. Créer un index avec ces paramètres :
   - **Nom** : `scraped-content`
   - **Dimensions** : `1024`
   - **Métrique** : `cosine`
   - **Cloud** : `AWS`
   - **Région** : `us-east-1`

### Mistral AI
1. Obtenir une clé API depuis [console.mistral.ai](https://console.mistral.ai/)
2. Vérifier les quotas et limites

## ✅ Vérification de l'Installation

### Test Docker
```bash
# Test de construction
docker-compose -f docker-compose.chatbot.yml build

# Test de lancement
docker-compose -f docker-compose.chatbot.yml up --dry-run
```

### Test Local
```bash
# Test des imports
python -c "import crawl4ai, pinecone, requests; print('✅ Imports OK')"

# Test du chatbot
python src/test_chatbot.py
```

## 🐛 Résolution de Problèmes

### Erreurs Communes

#### Docker Desktop non démarré
```bash
# Windows
# Démarrer Docker Desktop manuellement

# Linux
sudo systemctl start docker
```

#### Erreur de permissions (Linux)
```bash
# Ajouter l'utilisateur au groupe docker
sudo usermod -aG docker $USER
newgrp docker
```

#### Erreur Playwright
```bash
# Réinstaller Playwright
pip uninstall playwright
pip install playwright
python -m playwright install
```

#### Erreur de clés API
- Vérifier que le fichier `.env` existe
- Vérifier que les clés sont valides
- Vérifier les quotas API

### Logs et Debugging
```bash
# Logs Docker
docker-compose logs -f chatbot

# Logs détaillés
docker-compose --verbose up

# Mode debug Python
PYTHONPATH=./src python -m pdb src/chatbot.py
```

## 🔄 Mise à Jour

### Mise à jour du Code
```bash
git pull origin main
pip install -r requirements_vector.txt --upgrade
```

### Mise à jour Docker
```bash
# Reconstruire les images
docker-compose build --no-cache

# Nettoyer les anciennes images
docker system prune -f
```

## 📊 Monitoring

### Ressources Système
```bash
# Usage Docker
docker stats

# Espace disque
docker system df

# Processus Python
htop  # ou Task Manager sur Windows
```

### Logs d'Application
```bash
# Logs en temps réel
tail -f logs/scraper.log
tail -f logs/chatbot.log

# Analyse des erreurs
grep ERROR logs/*.log
```

## 🆘 Support

Si vous rencontrez des problèmes :

1. **Vérifiez** la [FAQ](FAQ.md)
2. **Consultez** les [Issues GitHub](https://github.com/votre-username/web-scraping-ai-chatbot/issues)
3. **Créez** une nouvelle issue avec :
   - Version Python/Docker
   - Système d'exploitation
   - Message d'erreur complet
   - Étapes pour reproduire

---

**Installation réussie ? Passez au [Guide d'Utilisation](USAGE.md) !** 🚀
