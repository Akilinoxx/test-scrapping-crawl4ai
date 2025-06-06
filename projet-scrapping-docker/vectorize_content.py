#!/usr/bin/env python
"""
Script pour charger les données scrapées dans une base vectorielle Pinecone
en utilisant LangChain pour les embeddings.
"""
import os
import glob
import argparse
import time
from typing import List, Dict, Any
import json
from tqdm import tqdm
import pinecone
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import TextLoader, DirectoryLoader
from langchain.vectorstores import Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.schema import Document
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('vectorize_content')

def parse_arguments():
    """
    Parse les arguments de ligne de commande
    """
    parser = argparse.ArgumentParser(description='Chargement des données scrapées dans Pinecone')
    
    parser.add_argument('--data-dir', type=str, default='./scraped_links',
                        help='Répertoire contenant les données scrapées')
    
    parser.add_argument('--pinecone-api-key', type=str, required=True,
                        help='Clé API Pinecone')
    
    parser.add_argument('--pinecone-environment', type=str, default='gcp-starter',
                        help='Environnement Pinecone')
    
    parser.add_argument('--pinecone-index', type=str, default='scraped-sites',
                        help='Nom de l\'index Pinecone')
    
    parser.add_argument('--openai-api-key', type=str, required=True,
                        help='Clé API OpenAI pour les embeddings')
    
    parser.add_argument('--chunk-size', type=int, default=1000,
                        help='Taille des chunks pour le découpage du texte')
    
    parser.add_argument('--chunk-overlap', type=int, default=200,
                        help='Chevauchement des chunks')
    
    return parser.parse_args()

def load_markdown_files(data_dir: str) -> List[Dict[str, Any]]:
    """
    Charge tous les fichiers markdown des sites scrapés
    """
    markdown_files = []
    
    # Parcourir tous les sous-répertoires (un par site)
    site_dirs = [d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))]
    
    for site_dir in site_dirs:
        site_path = os.path.join(data_dir, site_dir)
        
        # Chercher les fichiers markdown
        md_files = glob.glob(os.path.join(site_path, '*.md'))
        
        for md_file in md_files:
            # Charger les métadonnées du site depuis index.json si disponible
            metadata = {}
            index_json_path = os.path.join(site_path, 'index.json')
            if os.path.exists(index_json_path):
                try:
                    with open(index_json_path, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                except Exception as e:
                    logger.warning(f"Erreur lors du chargement des métadonnées pour {site_dir}: {e}")
            
            markdown_files.append({
                'file_path': md_file,
                'site_name': site_dir,
                'metadata': metadata
            })
    
    return markdown_files

def process_markdown_file(file_info: Dict[str, Any], chunk_size: int, chunk_overlap: int) -> List[Document]:
    """
    Traite un fichier markdown et le découpe en chunks
    """
    try:
        # Charger le contenu du fichier
        with open(file_info['file_path'], 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Créer le text splitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # Découper le texte en chunks
        chunks = text_splitter.split_text(content)
        
        # Créer des documents LangChain avec métadonnées
        documents = []
        for i, chunk in enumerate(chunks):
            # Extraire le titre de la page si disponible
            title = ""
            lines = chunk.split('\n')
            for line in lines:
                if line.startswith('## '):
                    title = line[3:].strip()
                    break
            
            # Créer les métadonnées du document
            doc_metadata = {
                'site_name': file_info['site_name'],
                'chunk_id': i,
                'source': file_info['file_path'],
                'title': title
            }
            
            # Ajouter les métadonnées du site
            if file_info['metadata']:
                doc_metadata.update({
                    'total_urls': file_info['metadata'].get('total_urls', 0),
                    'scraped_urls': file_info['metadata'].get('scraped_urls', 0),
                    'timestamp': file_info['metadata'].get('timestamp', 0)
                })
            
            # Créer le document
            doc = Document(page_content=chunk, metadata=doc_metadata)
            documents.append(doc)
        
        return documents
    
    except Exception as e:
        logger.error(f"Erreur lors du traitement du fichier {file_info['file_path']}: {e}")
        return []

def main():
    """
    Fonction principale
    """
    args = parse_arguments()
    
    # Initialiser l'embedding model
    embeddings = OpenAIEmbeddings(openai_api_key=args.openai_api_key)
    
    # Initialiser Pinecone
    pinecone.init(api_key=args.pinecone_api_key, environment=args.pinecone_environment)
    
    # Vérifier si l'index existe, sinon le créer
    if args.pinecone_index not in pinecone.list_indexes():
        logger.info(f"Création de l'index Pinecone '{args.pinecone_index}'")
        pinecone.create_index(
            name=args.pinecone_index,
            dimension=1536,  # Dimension des embeddings OpenAI
            metric="cosine"
        )
    
    # Charger les fichiers markdown
    logger.info(f"Chargement des fichiers markdown depuis {args.data_dir}")
    markdown_files = load_markdown_files(args.data_dir)
    logger.info(f"Nombre de fichiers markdown trouvés: {len(markdown_files)}")
    
    # Traiter chaque fichier
    all_documents = []
    for file_info in tqdm(markdown_files, desc="Traitement des fichiers markdown"):
        logger.info(f"Traitement du fichier {file_info['file_path']}")
        documents = process_markdown_file(file_info, args.chunk_size, args.chunk_overlap)
        all_documents.extend(documents)
        logger.info(f"Nombre de chunks extraits: {len(documents)}")
    
    # Créer l'index vectoriel
    logger.info(f"Création de l'index vectoriel dans Pinecone avec {len(all_documents)} documents")
    vectorstore = Pinecone.from_documents(
        documents=all_documents,
        embedding=embeddings,
        index_name=args.pinecone_index
    )
    
    logger.info("Indexation terminée avec succès!")
    logger.info(f"Nombre total de documents indexés: {len(all_documents)}")

if __name__ == "__main__":
    main()
