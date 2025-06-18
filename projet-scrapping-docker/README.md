# 🕷️ Web Scraping & AI Chatbot Pipeline

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Un pipeline complet de scraping web, vectorisation et chatbot IA utilisant **Crawl4AI**, **Mistral AI** et **Pinecone** pour créer un système de recherche sémantique intelligent.

## 🚀 Fonctionnalités

### 📊 Web Scraping
- **Extraction automatique** des sitemaps depuis robots.txt
- **Scraping parallélisé** avec gestion des délais et retry
- **Support multi-sites** avec configuration flexible
- **Stockage organisé** en fichiers Markdown par site

### 🧠 Intelligence Artificielle
- **Vectorisation** du contenu avec Mistral AI embeddings
- **Base vectorielle** Pinecone pour recherche sémantique
- **Chatbot interactif** avec historique et citations
- **Recherche contextuelle** dans tout le contenu scrapé

### 🐳 Containerisation
- **Docker Compose** pour orchestration complète
- **Services séparés** : scraper, vectorizer, chatbot
- **Volumes persistants** pour données et conversations
- **Scripts multi-plateformes** (Windows/Linux/Mac)

## 🛠️ Technologies

- **Python 3.10+** - Langage principal
- **Crawl4AI** - Web scraping intelligent
- **Mistral AI** - Embeddings et génération de texte
- **Pinecone** - Base de données vectorielle
- **Docker** - Containerisation
- **Playwright** - Automation navigateur

## 📦 Installation Rapide

### Prérequis
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Python 3.10+](https://www.python.org/downloads/) (pour usage local)

### 🚀 Démarrage avec Docker

```bash
# Cloner le projet
git clone https://github.com/votre-username/web-scraping-ai-chatbot.git
cd web-scraping-ai-chatbot

# Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos clés API

# Construire et lancer tous les services
./run-docker.sh all        # Linux/Mac
.\run-docker.bat all       # Windows
```

### 💻 Installation Locale

```bash
# Installer les dépendances
pip install -r requirements_vector.txt

# Installer Playwright
python -m playwright install

# Lancer le chatbot
python chatbot.py
```

## 🎯 Utilisation

### 1. Configuration des APIs

Créez un fichier `.env` avec vos clés :

```env
MISTRAL_API_KEY=votre_cle_mistral
PINECONE_API_KEY=votre_cle_pinecone
PINECONE_HOST=votre_host_pinecone
```

### 2. Scraping de Sites

```bash
# Scraper des sites spécifiques
python app.py --sites https://example.com --output-dir scraped_data

# Ou utiliser Docker
docker-compose -f docker-compose.complete.yml up scraper
```

### 3. Vectorisation

```bash
# Vectoriser le contenu scrapé
python vector_store.py

# Ou avec Docker
docker-compose -f docker-compose.complete.yml up vectorizer
```

### 4. Chatbot Interactif

```bash
# Lancer le chatbot
python chatbot.py

# Ou avec Docker
docker-compose -f docker-compose.chatbot.yml up
```

## 🐳 Commandes Docker

```bash
# Construire toutes les images
./run-docker.sh build

# Lancer le pipeline complet
./run-docker.sh all

# Lancer uniquement le chatbot
./run-docker.sh chatbot

# Nettoyer les conteneurs
./run-docker.sh clean
```

## 📁 Structure du Projet

```
├── 📁 src/                     # Code source principal
│   ├── app.py                  # Application de scraping
│   ├── chatbot.py             # Chatbot interactif
│   ├── vector_store.py        # Vectorisation
│   └── content_scraper.py     # Scraper de contenu
├── 📁 docker/                 # Configuration Docker
│   ├── Dockerfile             # Image scraper
│   ├── Dockerfile.chatbot     # Image chatbot
│   └── Dockerfile.vector      # Image vectorizer
├── 📁 scripts/                # Scripts utilitaires
│   ├── run-docker.sh         # Script Linux/Mac
│   └── run-docker.bat        # Script Windows
├── 📁 data/                   # Données (gitignore)
│   ├── scraped_content_md/   # Contenu scrapé
│   ├── scraped_links/        # URLs extraites
│   └── conversations/        # Historique chatbot
├── docker-compose.*.yml       # Configurations Docker
├── requirements*.txt          # Dépendances Python
└── .env.example              # Template configuration
```

## 🔧 Configuration Avancée

### Variables d'Environnement

| Variable | Description | Défaut |
|----------|-------------|---------|
| `MISTRAL_API_KEY` | Clé API Mistral AI | Requis |
| `PINECONE_API_KEY` | Clé API Pinecone | Requis |
| `PINECONE_HOST` | Host Pinecone | Requis |
| `SCRAPER_DELAY` | Délai entre requêtes (s) | 1 |
| `MAX_WORKERS` | Threads parallèles | 5 |

### Personnalisation du Scraping

Modifiez `sites_example.txt` pour ajouter vos sites :
```
https://example1.com
https://example2.com
https://example3.com
```

## 📊 Monitoring et Logs

```bash
# Voir les logs en temps réel
docker-compose logs -f chatbot

# Statistiques des conteneurs
docker stats

# Vérifier l'état des services
docker-compose ps
```

## 🤝 Contribution

1. **Fork** le projet
2. **Créer** une branche feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** vos changements (`git commit -m 'Add AmazingFeature'`)
4. **Push** vers la branche (`git push origin feature/AmazingFeature`)
5. **Ouvrir** une Pull Request

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 🆘 Support

- 📖 [Documentation complète](./docs/)
- 🐛 [Signaler un bug](https://github.com/votre-username/web-scraping-ai-chatbot/issues)
- 💬 [Discussions](https://github.com/votre-username/web-scraping-ai-chatbot/discussions)

## 🙏 Remerciements

- [Crawl4AI](https://github.com/unclecode/crawl4ai) - Framework de scraping
- [Mistral AI](https://mistral.ai/) - Modèles d'IA
- [Pinecone](https://www.pinecone.io/) - Base vectorielle

---

⭐ **N'oubliez pas de donner une étoile si ce projet vous aide !**
