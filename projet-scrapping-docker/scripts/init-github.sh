#!/bin/bash

# Script d'initialisation GitHub pour Web Scraping AI Chatbot
# Usage: ./scripts/init-github.sh [repository-url]

set -e

echo "🚀 Initialisation du projet pour GitHub..."

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction d'affichage coloré
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérifier si Git est installé
if ! command -v git &> /dev/null; then
    print_error "Git n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi

# Vérifier si on est dans le bon répertoire
if [ ! -f "README.md" ] || [ ! -f "setup.py" ]; then
    print_error "Ce script doit être exécuté depuis la racine du projet."
    exit 1
fi

# Initialiser le dépôt Git si nécessaire
if [ ! -d ".git" ]; then
    print_status "Initialisation du dépôt Git..."
    git init
    print_success "Dépôt Git initialisé"
else
    print_warning "Dépôt Git déjà initialisé"
fi

# Créer .gitignore s'il n'existe pas
if [ ! -f ".gitignore" ]; then
    print_error "Fichier .gitignore manquant!"
    exit 1
fi

# Vérifier que .env est dans .gitignore
if ! grep -q "^\.env$" .gitignore; then
    print_warning "Ajout de .env au .gitignore..."
    echo ".env" >> .gitignore
fi

# Créer .env.example s'il n'existe pas
if [ ! -f ".env.example" ]; then
    print_warning "Création du fichier .env.example..."
    cat > .env.example << 'EOF'
# Configuration API
MISTRAL_API_KEY=your_mistral_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_HOST=your_pinecone_host_here

# Configuration Scraper
SCRAPER_DELAY=1
MAX_WORKERS=5

# Configuration Chatbot
MAX_CONTEXT_LENGTH=4000
TEMPERATURE=0.7
MAX_TOKENS=500
EOF
fi

# Ajouter tous les fichiers
print_status "Ajout des fichiers au dépôt..."
git add .

# Premier commit
if [ -z "$(git log --oneline 2>/dev/null)" ]; then
    print_status "Création du commit initial..."
    git commit -m "🎉 Initial commit: Web Scraping AI Chatbot Pipeline

- ✨ Complete web scraping pipeline with Crawl4AI
- 🧠 AI-powered chatbot with Mistral AI and Pinecone
- 🐳 Docker containerization with multi-service orchestration
- 📚 Comprehensive documentation and setup guides
- 🔧 Development tools and CI/CD ready configuration"
    print_success "Commit initial créé"
else
    print_warning "Des commits existent déjà"
fi

# Créer la branche main si on est sur master
current_branch=$(git branch --show-current)
if [ "$current_branch" = "master" ]; then
    print_status "Renommage de la branche master en main..."
    git branch -m main
fi

# Ajouter le remote origin si fourni
if [ ! -z "$1" ]; then
    REPO_URL="$1"
    print_status "Ajout du remote origin: $REPO_URL"
    
    # Supprimer l'ancien remote s'il existe
    git remote remove origin 2>/dev/null || true
    
    # Ajouter le nouveau remote
    git remote add origin "$REPO_URL"
    print_success "Remote origin ajouté"
    
    # Pousser vers GitHub
    print_status "Push vers GitHub..."
    git push -u origin main
    print_success "Code poussé vers GitHub!"
    
    echo ""
    print_success "🎉 Projet initialisé avec succès sur GitHub!"
    echo -e "${BLUE}Repository URL:${NC} $REPO_URL"
else
    print_warning "URL du repository non fournie. Ajoutez-la manuellement avec:"
    echo "git remote add origin https://github.com/username/repository.git"
    echo "git push -u origin main"
fi

echo ""
print_status "📋 Prochaines étapes recommandées:"
echo "1. 🔑 Configurer les secrets GitHub pour les clés API"
echo "2. 🏷️  Créer des tags pour les releases"
echo "3. 📝 Personnaliser le README avec vos informations"
echo "4. 🔧 Configurer les GitHub Actions (CI/CD)"
echo "5. 📊 Ajouter des badges de statut"

echo ""
print_status "🛠️  Configuration GitHub Actions:"
echo "Créez .github/workflows/ci.yml pour l'intégration continue"

echo ""
print_status "🏷️  Créer une release:"
echo "git tag -a v1.0.0 -m 'First release'"
echo "git push origin v1.0.0"

echo ""
print_success "✅ Initialisation GitHub terminée!"
