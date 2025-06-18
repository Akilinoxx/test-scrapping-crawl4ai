# 🤝 Guide de Contribution

Merci de votre intérêt pour contribuer à ce projet ! Voici comment vous pouvez nous aider.

## 🚀 Comment Contribuer

### 1. Fork et Clone
```bash
# Fork le projet sur GitHub
# Puis cloner votre fork
git clone https://github.com/votre-username/web-scraping-ai-chatbot.git
cd web-scraping-ai-chatbot
```

### 2. Créer une Branche
```bash
git checkout -b feature/ma-nouvelle-fonctionnalite
```

### 3. Développer
- Suivez les conventions de code Python (PEP 8)
- Ajoutez des tests si nécessaire
- Documentez vos changements

### 4. Tester
```bash
# Tester localement
python -m pytest tests/

# Tester avec Docker
docker-compose -f docker-compose.complete.yml up --build
```

### 5. Commit et Push
```bash
git add .
git commit -m "feat: ajouter nouvelle fonctionnalité"
git push origin feature/ma-nouvelle-fonctionnalite
```

### 6. Pull Request
- Créez une Pull Request sur GitHub
- Décrivez clairement vos changements
- Référencez les issues liées

## 📝 Conventions

### Messages de Commit
Utilisez le format [Conventional Commits](https://www.conventionalcommits.org/) :
- `feat:` nouvelle fonctionnalité
- `fix:` correction de bug
- `docs:` documentation
- `style:` formatage
- `refactor:` refactoring
- `test:` tests
- `chore:` maintenance

### Code Style
- Suivez PEP 8 pour Python
- Utilisez des noms de variables descriptifs
- Commentez le code complexe
- Limitez les lignes à 88 caractères

## 🐛 Signaler des Bugs

1. Vérifiez que le bug n'a pas déjà été signalé
2. Utilisez le template d'issue bug
3. Incluez :
   - Description claire du problème
   - Étapes pour reproduire
   - Environnement (OS, Python, Docker)
   - Logs d'erreur

## 💡 Proposer des Fonctionnalités

1. Ouvrez une issue de type "feature request"
2. Décrivez le problème que ça résout
3. Proposez une solution
4. Discutez avec la communauté

## 🧪 Tests

```bash
# Installer les dépendances de test
pip install -r requirements-dev.txt

# Lancer les tests
python -m pytest tests/ -v

# Lancer avec couverture
python -m pytest tests/ --cov=src/
```

## 📚 Documentation

- Mettez à jour le README si nécessaire
- Ajoutez des docstrings aux fonctions
- Créez des exemples d'utilisation
- Mettez à jour les fichiers de configuration

## 🎯 Domaines d'Amélioration

### Priorité Haute
- [ ] Tests unitaires et d'intégration
- [ ] Gestion d'erreurs robuste
- [ ] Performance du scraping
- [ ] Interface web pour le chatbot

### Priorité Moyenne
- [ ] Support d'autres APIs d'IA
- [ ] Monitoring et métriques
- [ ] Cache intelligent
- [ ] Configuration avancée

### Priorité Basse
- [ ] Interface graphique
- [ ] Plugins personnalisés
- [ ] Déploiement cloud
- [ ] Intégrations tierces

## 🔧 Configuration de Développement

### Environnement Local
```bash
# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Installer en mode développement
pip install -e .
pip install -r requirements-dev.txt
```

### Pre-commit Hooks
```bash
# Installer pre-commit
pip install pre-commit

# Installer les hooks
pre-commit install

# Lancer manuellement
pre-commit run --all-files
```

## 🤔 Questions ?

- 💬 [Discussions GitHub](https://github.com/votre-username/web-scraping-ai-chatbot/discussions)
- 📧 Email : votre-email@example.com
- 🐛 [Issues](https://github.com/votre-username/web-scraping-ai-chatbot/issues)

## 🙏 Remerciements

Merci à tous les contributeurs qui rendent ce projet possible !

---

**Happy Coding!** 🚀
