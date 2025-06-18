@echo off
REM Script d'initialisation GitHub pour Web Scraping AI Chatbot (Windows)
REM Usage: .\scripts\init-github.bat [repository-url]

setlocal enabledelayedexpansion

echo 🚀 Initialisation du projet pour GitHub...

REM Vérifier si Git est installé
git --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Git n'est pas installé. Veuillez l'installer d'abord.
    exit /b 1
)

REM Vérifier si on est dans le bon répertoire
if not exist "README.md" (
    echo [ERROR] Ce script doit être exécuté depuis la racine du projet.
    exit /b 1
)
if not exist "setup.py" (
    echo [ERROR] Ce script doit être exécuté depuis la racine du projet.
    exit /b 1
)

REM Initialiser le dépôt Git si nécessaire
if not exist ".git" (
    echo [INFO] Initialisation du dépôt Git...
    git init
    echo [SUCCESS] Dépôt Git initialisé
) else (
    echo [WARNING] Dépôt Git déjà initialisé
)

REM Vérifier que .gitignore existe
if not exist ".gitignore" (
    echo [ERROR] Fichier .gitignore manquant!
    exit /b 1
)

REM Vérifier que .env est dans .gitignore
findstr /C:".env" .gitignore >nul
if errorlevel 1 (
    echo [WARNING] Ajout de .env au .gitignore...
    echo .env >> .gitignore
)

REM Créer .env.example s'il n'existe pas
if not exist ".env.example" (
    echo [WARNING] Création du fichier .env.example...
    (
        echo # Configuration API
        echo MISTRAL_API_KEY=your_mistral_api_key_here
        echo PINECONE_API_KEY=your_pinecone_api_key_here
        echo PINECONE_HOST=your_pinecone_host_here
        echo.
        echo # Configuration Scraper
        echo SCRAPER_DELAY=1
        echo MAX_WORKERS=5
        echo.
        echo # Configuration Chatbot
        echo MAX_CONTEXT_LENGTH=4000
        echo TEMPERATURE=0.7
        echo MAX_TOKENS=500
    ) > .env.example
)

REM Ajouter tous les fichiers
echo [INFO] Ajout des fichiers au dépôt...
git add .

REM Vérifier s'il y a déjà des commits
git log --oneline >nul 2>&1
if errorlevel 1 (
    echo [INFO] Création du commit initial...
    git commit -m "🎉 Initial commit: Web Scraping AI Chatbot Pipeline

- ✨ Complete web scraping pipeline with Crawl4AI
- 🧠 AI-powered chatbot with Mistral AI and Pinecone
- 🐳 Docker containerization with multi-service orchestration
- 📚 Comprehensive documentation and setup guides
- 🔧 Development tools and CI/CD ready configuration"
    echo [SUCCESS] Commit initial créé
) else (
    echo [WARNING] Des commits existent déjà
)

REM Créer la branche main si on est sur master
for /f "tokens=*" %%i in ('git branch --show-current') do set current_branch=%%i
if "!current_branch!"=="master" (
    echo [INFO] Renommage de la branche master en main...
    git branch -m main
)

REM Ajouter le remote origin si fourni
if not "%~1"=="" (
    set REPO_URL=%~1
    echo [INFO] Ajout du remote origin: !REPO_URL!
    
    REM Supprimer l'ancien remote s'il existe
    git remote remove origin >nul 2>&1
    
    REM Ajouter le nouveau remote
    git remote add origin "!REPO_URL!"
    echo [SUCCESS] Remote origin ajouté
    
    REM Pousser vers GitHub
    echo [INFO] Push vers GitHub...
    git push -u origin main
    echo [SUCCESS] Code poussé vers GitHub!
    
    echo.
    echo [SUCCESS] 🎉 Projet initialisé avec succès sur GitHub!
    echo Repository URL: !REPO_URL!
) else (
    echo [WARNING] URL du repository non fournie. Ajoutez-la manuellement avec:
    echo git remote add origin https://github.com/username/repository.git
    echo git push -u origin main
)

echo.
echo [INFO] 📋 Prochaines étapes recommandées:
echo 1. 🔑 Configurer les secrets GitHub pour les clés API
echo 2. 🏷️  Créer des tags pour les releases
echo 3. 📝 Personnaliser le README avec vos informations
echo 4. 🔧 Configurer les GitHub Actions (CI/CD)
echo 5. 📊 Ajouter des badges de statut

echo.
echo [INFO] 🛠️  Configuration GitHub Actions:
echo Créez .github/workflows/ci.yml pour l'intégration continue

echo.
echo [INFO] 🏷️  Créer une release:
echo git tag -a v1.0.0 -m "First release"
echo git push origin v1.0.0

echo.
echo [SUCCESS] ✅ Initialisation GitHub terminée!

pause
