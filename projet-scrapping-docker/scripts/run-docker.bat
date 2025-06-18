@echo off
REM Script Windows pour lancer le projet Docker complet
REM Usage: run-docker.bat [scraper|vectorizer|chatbot|all]

setlocal enabledelayedexpansion

REM Vérifier si Docker est installé
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker n'est pas installé. Veuillez l'installer d'abord.
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Compose n'est pas installé. Veuillez l'installer d'abord.
    exit /b 1
)

REM Vérifier si le fichier .env existe
if not exist .env (
    echo [WARNING] Fichier .env non trouvé. Création à partir de .env.example...
    if exist .env.example (
        copy .env.example .env >nul
        echo [INFO] Fichier .env créé. Veuillez vérifier et modifier vos clés API si nécessaire.
    ) else (
        echo [ERROR] Fichier .env.example non trouvé.
        exit /b 1
    )
)

REM Fonction pour construire les images
:build_images
echo [INFO] Construction des images Docker...
docker-compose -f docker-compose.complete.yml build
if errorlevel 1 (
    echo [ERROR] Erreur lors de la construction des images
    exit /b 1
)
echo [SUCCESS] Images construites avec succès
goto :eof

REM Fonction pour lancer le scraper
:run_scraper
echo [INFO] Lancement du scraper...
docker-compose -f docker-compose.complete.yml up scraper
goto :eof

REM Fonction pour lancer le vectorizer
:run_vectorizer
echo [INFO] Lancement du vectorizer...
docker-compose -f docker-compose.complete.yml up vectorizer
goto :eof

REM Fonction pour lancer le chatbot
:run_chatbot
echo [INFO] Lancement du chatbot...
docker-compose -f docker-compose.complete.yml up chatbot
goto :eof

REM Fonction pour lancer tout le pipeline
:run_all
echo [INFO] Lancement du pipeline complet...
echo [INFO] 1. Scraping des sites web...
docker-compose -f docker-compose.complete.yml up scraper
echo [INFO] 2. Vectorisation du contenu...
docker-compose -f docker-compose.complete.yml up vectorizer
echo [INFO] 3. Lancement du chatbot...
docker-compose -f docker-compose.complete.yml up chatbot
goto :eof

REM Fonction pour nettoyer
:cleanup
echo [INFO] Nettoyage des conteneurs...
docker-compose -f docker-compose.complete.yml down
echo [SUCCESS] Nettoyage terminé
goto :eof

REM Fonction d'aide
:show_help
echo Usage: %0 [COMMAND]
echo.
echo Commands:
echo   build      Construire les images Docker
echo   scraper    Lancer uniquement le scraper
echo   vectorizer Lancer uniquement le vectorizer
echo   chatbot    Lancer uniquement le chatbot
echo   all        Lancer tout le pipeline (scraper -^> vectorizer -^> chatbot)
echo   cleanup    Nettoyer les conteneurs
echo   help       Afficher cette aide
echo.
echo Exemples:
echo   %0 build
echo   %0 all
echo   %0 chatbot
goto :eof

REM Traitement des arguments
set command=%1
if "%command%"=="" set command=help

if "%command%"=="build" (
    call :build_images
) else if "%command%"=="scraper" (
    call :build_images
    call :run_scraper
) else if "%command%"=="vectorizer" (
    call :build_images
    call :run_vectorizer
) else if "%command%"=="chatbot" (
    call :build_images
    call :run_chatbot
) else if "%command%"=="all" (
    call :build_images
    call :run_all
) else if "%command%"=="cleanup" (
    call :cleanup
) else if "%command%"=="help" (
    call :show_help
) else if "%command%"=="--help" (
    call :show_help
) else if "%command%"=="-h" (
    call :show_help
) else (
    echo [ERROR] Commande inconnue: %command%
    call :show_help
    exit /b 1
)
