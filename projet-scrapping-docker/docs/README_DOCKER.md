# 🐳 Configuration Docker - Projet Scraping & Chatbot

Cette configuration Docker permet de lancer facilement l'ensemble du pipeline : scraping web, vectorisation et chatbot.

## 🏗️ Architecture Docker

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    SCRAPER      │───▶│   VECTORIZER    │───▶│    CHATBOT      │
│                 │    │                 │    │                 │
│ • Crawl4AI      │    │ • Mistral AI    │    │ • Pinecone      │
│ • Playwright    │    │ • Pinecone      │    │ • Mistral AI    │
│ • Markdown      │    │ • Embeddings    │    │ • Interface     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 Fichiers Docker

- `Dockerfile` : Image principale pour le scraper
- `Dockerfile.vector` : Image pour la vectorisation
- `Dockerfile.chatbot` : Image pour le chatbot
- `docker-compose.complete.yml` : Configuration complète
- `.env.example` : Variables d'environnement exemple
- `run-docker.sh` / `run-docker.bat` : Scripts de lancement

## 🚀 Installation et Utilisation

### 1. Prérequis

- Docker Desktop installé
- Docker Compose installé

### 2. Configuration

```bash
# Copier le fichier d'environnement
cp .env.example .env

# Modifier vos clés API dans .env si nécessaire
# Les clés par défaut sont déjà configurées
```

### 3. Lancement Rapide

**Sur Windows :**
```cmd
# Lancer tout le pipeline
run-docker.bat all

# Ou lancer uniquement le chatbot
run-docker.bat chatbot
```

**Sur Linux/Mac :**
```bash
# Rendre le script exécutable
chmod +x run-docker.sh

# Lancer tout le pipeline
./run-docker.sh all

# Ou lancer uniquement le chatbot
./run-docker.sh chatbot
```

### 4. Utilisation Manuelle

```bash
# Construire les images
docker-compose -f docker-compose.complete.yml build

# Lancer le scraper seul
docker-compose -f docker-compose.complete.yml up scraper

# Lancer la vectorisation seule
docker-compose -f docker-compose.complete.yml up vectorizer

# Lancer le chatbot seul
docker-compose -f docker-compose.complete.yml up chatbot

# Lancer tout en séquence
docker-compose -f docker-compose.complete.yml up scraper
docker-compose -f docker-compose.complete.yml up vectorizer
docker-compose -f docker-compose.complete.yml up chatbot
```

## 🎯 Commandes Disponibles

| Commande | Description |
|----------|-------------|
| `build` | Construire toutes les images Docker |
| `scraper` | Lancer uniquement le scraping web |
| `vectorizer` | Lancer uniquement la vectorisation |
| `chatbot` | Lancer uniquement le chatbot |
| `all` | Lancer tout le pipeline complet |
| `cleanup` | Nettoyer les conteneurs |
| `help` | Afficher l'aide |

## 📂 Volumes et Persistance

Les données sont persistées dans les répertoires suivants :

```
projet-scrapping-docker/
├── scraped_links/          # URLs scrapées
├── scraped_content_md/     # Contenu en markdown
└── conversations/          # Historique des conversations
```

## 🔧 Configuration Avancée

### Variables d'Environnement

Modifiez le fichier `.env` pour personnaliser :

```env
# APIs
MISTRAL_API_KEY=votre_clé_mistral
PINECONE_API_KEY=votre_clé_pinecone
PINECONE_HOST=votre_host_pinecone

# Scraper
HEADLESS=true
FORMAT=markdown
PAGE_TIMEOUT=60000
DELAY_BEFORE_RETURN=5.0
```

### Personnaliser les Sites à Scraper

Modifiez `sites_example.txt` ou utilisez la commande directe :

```bash
# Scraper un site spécifique
docker-compose -f docker-compose.complete.yml run scraper python app.py --sites "https://example.com"
```

## 🐛 Dépannage

### Erreur de Construction
```bash
# Reconstruire sans cache
docker-compose -f docker-compose.complete.yml build --no-cache
```

### Problème de Permissions
```bash
# Sur Linux/Mac, donner les permissions
chmod +x run-docker.sh
```

### Erreur API
- Vérifiez vos clés API dans `.env`
- Vérifiez votre quota Mistral AI
- Vérifiez la connexion à Pinecone

### Nettoyer Complètement
```bash
# Supprimer tous les conteneurs et images
docker-compose -f docker-compose.complete.yml down --rmi all
docker system prune -a
```

## 📊 Monitoring

### Logs des Services
```bash
# Voir les logs du scraper
docker-compose -f docker-compose.complete.yml logs scraper

# Voir les logs du vectorizer
docker-compose -f docker-compose.complete.yml logs vectorizer

# Voir les logs du chatbot
docker-compose -f docker-compose.complete.yml logs chatbot
```

### Statut des Conteneurs
```bash
# Voir les conteneurs actifs
docker-compose -f docker-compose.complete.yml ps

# Voir l'utilisation des ressources
docker stats
```

## 🚀 Déploiement en Production

### Avec Docker Swarm
```bash
# Initialiser le swarm
docker swarm init

# Déployer la stack
docker stack deploy -c docker-compose.complete.yml scraping-stack
```

### Avec Kubernetes
```bash
# Convertir avec Kompose
kompose convert -f docker-compose.complete.yml
kubectl apply -f .
```

## 🔒 Sécurité

- Les clés API sont gérées via variables d'environnement
- Aucun port exposé par défaut (sauf chatbot sur 8080)
- Réseau isolé entre les services
- Images basées sur Python slim pour réduire la surface d'attaque

## 📈 Performance

### Optimisations Incluses
- Images multi-stage pour réduire la taille
- Cache des dépendances Python
- Volumes pour éviter la recopie des données
- Réseau dédié pour les communications inter-services

### Monitoring des Ressources
```bash
# Surveiller l'utilisation
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

---

**Bon scraping et bon chat ! 🎉**
