#!/bin/bash

# Script pour lancer le projet Docker complet
# Usage: ./run-docker.sh [scraper|vectorizer|chatbot|all]

set -e

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages colorés
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérifier si Docker est installé
if ! command -v docker &> /dev/null; then
    log_error "Docker n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    log_error "Docker Compose n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi

# Vérifier si le fichier .env existe
if [ ! -f .env ]; then
    log_warning "Fichier .env non trouvé. Création à partir de .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        log_info "Fichier .env créé. Veuillez vérifier et modifier vos clés API si nécessaire."
    else
        log_error "Fichier .env.example non trouvé."
        exit 1
    fi
fi

# Fonction pour construire les images
build_images() {
    log_info "Construction des images Docker..."
    docker-compose -f docker-compose.complete.yml build
    log_success "Images construites avec succès"
}

# Fonction pour lancer le scraper
run_scraper() {
    log_info "Lancement du scraper..."
    docker-compose -f docker-compose.complete.yml up scraper
}

# Fonction pour lancer le vectorizer
run_vectorizer() {
    log_info "Lancement du vectorizer..."
    docker-compose -f docker-compose.complete.yml up vectorizer
}

# Fonction pour lancer le chatbot
run_chatbot() {
    log_info "Lancement du chatbot..."
    docker-compose -f docker-compose.complete.yml up chatbot
}

# Fonction pour lancer tout le pipeline
run_all() {
    log_info "Lancement du pipeline complet..."
    log_info "1. Scraping des sites web..."
    docker-compose -f docker-compose.complete.yml up scraper
    
    log_info "2. Vectorisation du contenu..."
    docker-compose -f docker-compose.complete.yml up vectorizer
    
    log_info "3. Lancement du chatbot..."
    docker-compose -f docker-compose.complete.yml up chatbot
}

# Fonction pour nettoyer
cleanup() {
    log_info "Nettoyage des conteneurs..."
    docker-compose -f docker-compose.complete.yml down
    log_success "Nettoyage terminé"
}

# Fonction d'aide
show_help() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  build      Construire les images Docker"
    echo "  scraper    Lancer uniquement le scraper"
    echo "  vectorizer Lancer uniquement le vectorizer"
    echo "  chatbot    Lancer uniquement le chatbot"
    echo "  all        Lancer tout le pipeline (scraper -> vectorizer -> chatbot)"
    echo "  cleanup    Nettoyer les conteneurs"
    echo "  help       Afficher cette aide"
    echo ""
    echo "Exemples:"
    echo "  $0 build"
    echo "  $0 all"
    echo "  $0 chatbot"
}

# Traitement des arguments
case "${1:-help}" in
    build)
        build_images
        ;;
    scraper)
        build_images
        run_scraper
        ;;
    vectorizer)
        build_images
        run_vectorizer
        ;;
    chatbot)
        build_images
        run_chatbot
        ;;
    all)
        build_images
        run_all
        ;;
    cleanup)
        cleanup
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        log_error "Commande inconnue: $1"
        show_help
        exit 1
        ;;
esac
