# ❓ Questions Fréquentes (FAQ)

Cette FAQ répond aux questions les plus courantes concernant le projet Web Scraping AI Chatbot.

## 🚀 Installation et Configuration

### Q: Quelles sont les versions Python supportées ?
**R:** Le projet nécessite Python 3.10 ou supérieur. Python 3.11 est recommandé pour de meilleures performances.

### Q: Où obtenir les clés API nécessaires ?
**R:** 
- **Mistral AI** : [console.mistral.ai](https://console.mistral.ai/)
- **Pinecone** : [app.pinecone.io](https://app.pinecone.io/)

Les deux services offrent des plans gratuits pour débuter.

### Q: Comment configurer Pinecone correctement ?
**R:** Créez un index avec ces paramètres exacts :
- **Nom** : `scraped-content`
- **Dimensions** : `1024`
- **Métrique** : `cosine`
- **Cloud** : `AWS`
- **Région** : `us-east-1`

### Q: Le fichier .env est-il obligatoire ?
**R:** Oui, copiez `.env.example` vers `.env` et remplissez vos clés API. Ce fichier est ignoré par Git pour la sécurité.

## 🐳 Docker

### Q: Docker est-il obligatoire ?
**R:** Non, vous pouvez utiliser le projet localement. Docker simplifie le déploiement et évite les conflits de dépendances.

### Q: Pourquoi le chatbot Docker ne répond pas sur Windows ?
**R:** Problème d'interactivité Docker sur Windows PowerShell. Solutions :
1. Utiliser `python src/chatbot.py` directement
2. Utiliser WSL2 avec Docker
3. Utiliser Git Bash au lieu de PowerShell

### Q: Comment voir les logs Docker ?
**R:** 
```bash
# Logs en temps réel
docker-compose logs -f chatbot

# Logs détaillés
docker-compose --verbose up
```

### Q: Les conteneurs s'arrêtent immédiatement, pourquoi ?
**R:** Vérifiez :
1. Le fichier `.env` existe et contient les bonnes clés
2. Les volumes sont correctement montés
3. Les ports ne sont pas déjà utilisés

## 🤖 Utilisation du Chatbot

### Q: Le chatbot ne trouve pas de résultats pertinents
**R:** Vérifiez :
1. Que des données ont été vectorisées (`python src/vector_store.py`)
2. Que l'index Pinecone contient des vecteurs
3. Reformulez votre question différemment

### Q: Comment sauvegarder une conversation ?
**R:** Tapez `save` dans le chatbot. Les conversations sont sauvées dans `conversations/`.

### Q: Quelles sont les commandes disponibles ?
**R:** 
- `stats` : Statistiques de la base vectorielle
- `save` : Sauvegarder la conversation
- `help` : Afficher l'aide
- `quit`/`exit`/`bye` : Quitter

### Q: Comment améliorer la qualité des réponses ?
**R:** 
1. Scraper plus de contenu de qualité
2. Ajuster les paramètres de recherche (top_k)
3. Modifier la température Mistral AI
4. Améliorer le prompt système

## 🕷️ Web Scraping

### Q: Quels sites peuvent être scrapés ?
**R:** Tous les sites avec un sitemap XML accessible. Respectez les robots.txt et conditions d'utilisation.

### Q: Le scraping est très lent, que faire ?
**R:** 
1. Augmenter `SCRAPER_DELAY` pour respecter les serveurs
2. Réduire `MAX_WORKERS` si les serveurs sont surchargés
3. Utiliser `--sitemap-only` pour extraire uniquement les URLs

### Q: Comment scraper des sites spécifiques ?
**R:** 
```bash
# Sites directs
python src/app.py --sites https://site1.com https://site2.com

# Fichier de sites
echo "https://site1.com" > mes_sites.txt
python src/app.py --sites-file mes_sites.txt
```

### Q: Erreur "robots.txt" lors du scraping
**R:** Le scraper respecte robots.txt par défaut. Modifiez `respect_robots_txt: False` dans la configuration si nécessaire (non recommandé).

## 🧠 Vectorisation

### Q: Combien de temps prend la vectorisation ?
**R:** Dépend du volume de données et des limites API Mistral. Comptez ~1-2 secondes par chunk de texte.

### Q: Erreur de quota API Mistral
**R:** 
1. Vérifiez vos limites sur console.mistral.ai
2. Ajoutez des délais entre les requêtes
3. Utilisez un plan payant pour plus de quota

### Q: Comment optimiser la taille des chunks ?
**R:** Ajustez dans `vector_store.py` :
- `chunk_size=500` : Taille des segments
- `overlap=50` : Chevauchement entre segments

### Q: Les embeddings sont-ils stockés localement ?
**R:** Non, ils sont stockés dans Pinecone. Seuls les textes originaux sont en local.

## 🔧 Développement

### Q: Comment contribuer au projet ?
**R:** Consultez [CONTRIBUTING.md](../CONTRIBUTING.md) pour les guidelines détaillées.

### Q: Comment ajouter de nouveaux tests ?
**R:** Ajoutez vos tests dans `tests/` en suivant la convention `test_*.py`.

### Q: Comment déboguer le code ?
**R:** 
```bash
# Mode debug Python
PYTHONPATH=./src python -m pdb src/chatbot.py

# Logs verbeux
LOG_LEVEL=DEBUG python src/app.py
```

### Q: Comment formater le code ?
**R:** 
```bash
# Installer les outils
pip install black flake8 isort

# Formater
black src/
isort src/
flake8 src/
```

## 🚨 Problèmes Courants

### Q: "ModuleNotFoundError" lors de l'exécution
**R:** 
1. Vérifiez que vous êtes dans le bon répertoire
2. Installez les dépendances : `pip install -r requirements_vector.txt`
3. Ajoutez le dossier src au PYTHONPATH

### Q: "ConnectionError" avec Pinecone
**R:** 
1. Vérifiez votre connexion internet
2. Validez la clé API et l'host Pinecone
3. Vérifiez que l'index existe

### Q: "Invalid API key" avec Mistral
**R:** 
1. Vérifiez la clé dans le fichier `.env`
2. Régénérez la clé sur console.mistral.ai
3. Vérifiez les quotas et limites

### Q: Erreur de permissions Docker
**R:** 
```bash
# Linux : ajouter l'utilisateur au groupe docker
sudo usermod -aG docker $USER
newgrp docker

# Windows : redémarrer Docker Desktop
```

### Q: "Port already in use" avec Docker
**R:** 
```bash
# Trouver le processus utilisant le port
netstat -tulpn | grep :8080

# Arrêter les conteneurs existants
docker-compose down
```

## 📊 Performance

### Q: Comment optimiser les performances ?
**R:** 
1. **Scraping** : Ajuster délais et workers
2. **Vectorisation** : Traiter par lots
3. **Chatbot** : Optimiser la taille du contexte
4. **Docker** : Allouer plus de ressources

### Q: Combien de RAM est nécessaire ?
**R:** 
- **Minimum** : 4 GB
- **Recommandé** : 8 GB
- **Optimal** : 16 GB (pour gros volumes)

### Q: Le chatbot est lent à répondre
**R:** 
1. Réduire `top_k` dans la recherche
2. Optimiser la taille du contexte
3. Utiliser un serveur plus proche géographiquement

## 🔒 Sécurité

### Q: Comment protéger mes clés API ?
**R:** 
1. Utilisez toujours le fichier `.env`
2. Ne commitez jamais `.env` sur Git
3. Utilisez des secrets pour la production
4. Régénérez les clés régulièrement

### Q: Le projet est-il sûr à utiliser ?
**R:** Oui, mais :
1. Respectez les robots.txt
2. Ne scrapez pas de données sensibles
3. Respectez les CGU des sites
4. Utilisez des délais appropriés

## 🆘 Support

### Q: Où obtenir de l'aide ?
**R:** 
1. Consultez cette FAQ
2. Lisez la [documentation](INSTALLATION.md)
3. Cherchez dans les [Issues GitHub](https://github.com/votre-username/web-scraping-ai-chatbot/issues)
4. Créez une nouvelle issue avec les détails

### Q: Comment signaler un bug ?
**R:** Créez une issue GitHub avec :
- Description du problème
- Étapes pour reproduire
- Messages d'erreur complets
- Version Python/Docker
- Système d'exploitation

### Q: Le projet est-il maintenu ?
**R:** Oui, le projet est activement maintenu. Les contributions sont les bienvenues !

---

**Cette FAQ ne répond pas à votre question ? [Créez une issue](https://github.com/votre-username/web-scraping-ai-chatbot/issues/new) !** 🆘
