# 🎯 Guide d'Utilisation

Guide complet pour utiliser le pipeline Web Scraping AI Chatbot.

## 🚀 Démarrage Rapide

### 1. Scraping de Sites Web
```bash
# Scraper des sites spécifiques
python src/app.py --sites https://example.com https://autre-site.com

# Utiliser un fichier de sites
python src/app.py --sites-file sites_example.txt

# Avec Docker
docker-compose -f docker-compose.complete.yml up scraper
```

### 2. Vectorisation du Contenu
```bash
# Vectoriser le contenu scrapé
python src/vector_store.py

# Avec Docker
docker-compose -f docker-compose.complete.yml up vectorizer
```

### 3. Chatbot Interactif
```bash
# Lancer le chatbot
python src/chatbot.py

# Avec Docker
docker-compose -f docker-compose.chatbot.yml up
```

## 📊 Scraping Avancé

### Configuration des Sites
Créez un fichier `sites_custom.txt` :
```
https://site1.com
https://site2.com
# Commentaires supportés
https://site3.com
```

### Options de Scraping
```bash
python src/app.py \
  --sites-file sites_custom.txt \
  --output-dir mes_donnees \
  --max-workers 10 \
  --delay 2.0 \
  --sitemap-only  # Extraire uniquement les URLs
```

### Paramètres Disponibles
- `--sites` : URLs directes à scraper
- `--sites-file` : Fichier contenant les URLs
- `--output-dir` : Dossier de sortie (défaut: `scraped_links`)
- `--max-workers` : Nombre de threads (défaut: 5)
- `--delay` : Délai entre requêtes en secondes (défaut: 1.0)
- `--sitemap-only` : Mode extraction d'URLs uniquement

## 🧠 Vectorisation Personnalisée

### Configuration Pinecone
```python
# Dans src/vector_store.py
PINECONE_CONFIG = {
    "api_key": "votre_cle",
    "host": "votre_host",
    "index_name": "scraped-content",
    "dimension": 1024,
    "metric": "cosine"
}
```

### Traitement par Lots
```bash
# Vectoriser un dossier spécifique
python src/vector_store.py --data-dir ./mes_donnees

# Traitement par chunks
python src/vector_store.py --chunk-size 500 --chunk-overlap 50
```

## 🤖 Utilisation du Chatbot

### Interface Interactive
Une fois lancé, le chatbot propose plusieurs commandes :

```
🤖 Chatbot de Recherche Sémantique
==================================================
Connecté à votre base vectorielle Pinecone
Tapez 'quit', 'exit' ou 'bye' pour quitter
Tapez 'stats' pour voir les statistiques
Tapez 'save' pour sauvegarder la conversation
==================================================

Votre question: 
```

### Commandes Spéciales
- `stats` : Affiche les statistiques de la base vectorielle
- `save` : Sauvegarde la conversation actuelle
- `quit`/`exit`/`bye` : Quitte le chatbot
- `help` : Affiche l'aide

### Exemples de Questions
```
Qu'est-ce que le machine learning ?
Explique-moi les concepts de base du web scraping
Quelles sont les meilleures pratiques en IA ?
Comment fonctionne la vectorisation de texte ?
```

## 🔧 Configuration Avancée

### Variables d'Environnement
```env
# APIs
MISTRAL_API_KEY=votre_cle_mistral
PINECONE_API_KEY=votre_cle_pinecone
PINECONE_HOST=votre_host_pinecone

# Scraping
SCRAPER_DELAY=1
MAX_WORKERS=5
USER_AGENT=Mozilla/5.0 (compatible; WebScraper/1.0)

# Chatbot
MAX_CONTEXT_LENGTH=4000
TEMPERATURE=0.7
MAX_TOKENS=500
```

### Personnalisation du Scraper
```python
# Dans src/content_scraper.py
SCRAPER_CONFIG = {
    "headers": {
        "User-Agent": "Votre User-Agent",
        "Accept": "text/html,application/xhtml+xml"
    },
    "timeout": 30,
    "retry_attempts": 3,
    "respect_robots_txt": True
}
```

## 📁 Structure des Données

### Données Scrapées
```
scraped_content_md/
├── site1_com.md          # Contenu du site 1
├── site2_com.md          # Contenu du site 2
└── ...

scraped_links/
├── site1_com/
│   ├── sitemap_urls.json # URLs extraites
│   └── stats.json        # Statistiques
└── site2_com/
    ├── sitemap_urls.json
    └── stats.json
```

### Conversations Sauvegardées
```
conversations/
├── conversation_2024-01-15_14-30-25.json
├── conversation_2024-01-15_15-45-12.json
└── ...
```

## 🐳 Utilisation Docker Avancée

### Services Individuels
```bash
# Scraper avec configuration custom
docker-compose -f docker-compose.complete.yml run scraper \
  python app.py --sites https://example.com --delay 2

# Vectorizer avec paramètres
docker-compose -f docker-compose.complete.yml run vectorizer \
  python vector_store.py --chunk-size 800

# Chatbot en mode test
docker-compose -f docker-compose.complete.yml run chatbot \
  python test_chatbot.py
```

### Volumes et Persistance
```yaml
# Dans docker-compose.yml
volumes:
  - ./scraped_content_md:/app/scraped_content_md:ro  # Lecture seule
  - ./conversations:/app/conversations:rw            # Lecture/écriture
  - ./logs:/app/logs:rw                             # Logs
```

### Monitoring Docker
```bash
# Logs en temps réel
docker-compose logs -f --tail=100 chatbot

# Statistiques des conteneurs
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# Inspection des volumes
docker volume ls
docker volume inspect projet-scrapping-docker_scraped_content_md
```

## 📊 Monitoring et Métriques

### Logs d'Application
```bash
# Activer les logs détaillés
export LOG_LEVEL=DEBUG
python src/chatbot.py

# Logs par composant
tail -f logs/scraper.log
tail -f logs/vectorizer.log
tail -f logs/chatbot.log
```

### Métriques Pinecone
```python
# Dans le chatbot, tapez 'stats'
Index Statistics:
- Total vectors: 1,234
- Dimension: 1024
- Index fullness: 0.12%
- Namespaces: default
```

### Performance
```bash
# Temps de réponse du chatbot
time echo "Test question" | python src/chatbot.py

# Usage mémoire
ps aux | grep python
htop -p $(pgrep -f chatbot.py)
```

## 🔄 Workflows Typiques

### Workflow Complet
```bash
# 1. Scraper de nouveaux sites
python src/app.py --sites-file nouveaux_sites.txt

# 2. Vectoriser le nouveau contenu
python src/vector_store.py

# 3. Tester avec le chatbot
python src/test_chatbot.py

# 4. Lancer le chatbot interactif
python src/chatbot.py
```

### Workflow de Développement
```bash
# 1. Scraper un site de test
python src/app.py --sites https://example.com --sitemap-only

# 2. Vérifier les données
ls -la scraped_links/example_com/

# 3. Test de vectorisation
python src/vector_store.py --dry-run

# 4. Test du chatbot
python src/test_chatbot.py
```

### Workflow de Production
```bash
# 1. Lancer avec Docker
./scripts/run-docker.sh all

# 2. Monitoring
docker-compose logs -f

# 3. Backup des données
tar -czf backup_$(date +%Y%m%d).tar.gz scraped_content_md/ conversations/
```

## 🚨 Bonnes Pratiques

### Scraping Responsable
- ✅ Respecter les délais entre requêtes
- ✅ Vérifier les robots.txt
- ✅ Utiliser des User-Agents appropriés
- ✅ Limiter le nombre de workers
- ❌ Ne pas surcharger les serveurs

### Gestion des APIs
- ✅ Surveiller les quotas
- ✅ Implémenter le retry avec backoff
- ✅ Gérer les erreurs gracieusement
- ✅ Utiliser des variables d'environnement
- ❌ Ne jamais hardcoder les clés

### Performance
- ✅ Utiliser des chunks appropriés
- ✅ Optimiser la taille des embeddings
- ✅ Nettoyer régulièrement les données
- ✅ Monitorer l'usage mémoire

## 🆘 Dépannage

### Problèmes Courants
1. **Chatbot ne répond pas** → Vérifier les clés API
2. **Scraping lent** → Augmenter le délai ou réduire les workers
3. **Erreurs Pinecone** → Vérifier l'index et les quotas
4. **Docker lent** → Allouer plus de ressources

### Debug Mode
```bash
# Mode debug complet
PYTHONPATH=./src python -m pdb src/chatbot.py

# Logs verbeux
LOG_LEVEL=DEBUG python src/app.py --sites https://example.com
```

---

**Besoin d'aide ? Consultez la [FAQ](FAQ.md) ou créez une [issue](https://github.com/votre-username/web-scraping-ai-chatbot/issues) !** 🆘
