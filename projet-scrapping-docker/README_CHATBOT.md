# 🤖 Chatbot de Recherche Sémantique

Ce chatbot utilise votre base vectorielle Pinecone pour répondre aux questions basées sur le contenu web scrapé.

## 🚀 Fonctionnalités

- **Recherche sémantique** : Trouve les informations pertinentes dans votre base de connaissances
- **Réponses contextuelles** : Génère des réponses basées sur le contenu trouvé
- **Citations des sources** : Indique d'où proviennent les informations
- **Historique de conversation** : Sauvegarde les échanges
- **Interface interactive** : Chat en temps réel dans le terminal

## 📁 Fichiers

- `chatbot.py` : Chatbot principal interactif
- `test_chatbot.py` : Script de test et menu de développement
- `README_CHATBOT.md` : Ce fichier de documentation

## 🔧 Configuration

Les clés API sont déjà configurées dans le code :
- **Mistral AI** : Pour les embeddings et la génération de réponses
- **Pinecone** : Pour la recherche vectorielle dans votre base de données

## 🎯 Utilisation

### 1. Chatbot Interactif Complet

```bash
python chatbot.py
```

Fonctionnalités disponibles :
- Posez vos questions en langage naturel
- Tapez `stats` pour voir les statistiques
- Tapez `save` pour sauvegarder la conversation
- Tapez `quit`, `exit` ou `bye` pour quitter

### 2. Tests et Développement

```bash
python test_chatbot.py
```

Options disponibles :
1. **Test de connexion** : Vérifie que les APIs fonctionnent
2. **Tests automatiques** : Lance des questions d'exemple
3. **Mode test interactif** : Testez vos propres questions
4. **Lancer le chatbot complet** : Lance l'interface principale
5. **Quitter**

## 💡 Exemples de Questions

Voici des types de questions que vous pouvez poser :

```
- "Qu'est-ce que le scraping web ?"
- "Comment fonctionne l'indexation ?"
- "Parle-moi des APIs utilisées"
- "Quelles sont les technologies mentionnées ?"
- "Explique-moi Pinecone"
- "Comment configurer Mistral AI ?"
```

## 🔍 Comment ça Marche

1. **Votre question** est convertie en embedding par Mistral AI
2. **Recherche vectorielle** dans Pinecone pour trouver le contenu pertinent
3. **Génération de réponse** par Mistral AI basée sur le contexte trouvé
4. **Affichage** de la réponse avec les sources citées

## 📊 Fonctionnalités Avancées

### Sauvegarde des Conversations
```bash
# Dans le chatbot, tapez :
save
# Crée un fichier conversation_YYYYMMDD_HHMMSS.json
```

### Statistiques
```bash
# Dans le chatbot, tapez :
stats
# Affiche le nombre de questions, dates, etc.
```

## 🛠️ Architecture Technique

```
ChatBot Class
├── search_knowledge_base()    # Recherche dans Pinecone
├── generate_response()        # Génération avec Mistral
├── chat()                    # Traitement complet d'une question
├── show_stats()              # Statistiques
└── save_conversation()       # Sauvegarde
```

## 🔒 Sécurité

- Les clés API sont configurées dans les constantes du fichier
- Aucune donnée sensible n'est loggée
- Les conversations sont sauvegardées localement uniquement

## 🐛 Dépannage

### Erreur de connexion Mistral
- Vérifiez votre clé API Mistral
- Vérifiez votre quota/limite de taux

### Erreur de connexion Pinecone
- Vérifiez votre clé API Pinecone
- Vérifiez que l'index "scraped-content" existe

### Aucun résultat trouvé
- Vérifiez que votre base vectorielle contient des données
- Essayez des questions plus générales
- Lancez d'abord `vector_store.py` pour indexer du contenu

## 📈 Optimisations

Le chatbot inclut plusieurs optimisations :
- **Rate limiting** : Délais entre les requêtes API
- **Gestion d'erreurs** : Récupération gracieuse des erreurs
- **Chunking intelligent** : Recherche dans les meilleurs extraits
- **Température basse** : Réponses plus précises et factuelles

## 🎨 Personnalisation

Vous pouvez modifier :
- `top_k` : Nombre de résultats de recherche (défaut: 3)
- `temperature` : Créativité des réponses (défaut: 0.3)
- `max_tokens` : Longueur des réponses (défaut: 1000)

---

**Bon chat ! 🚀**
