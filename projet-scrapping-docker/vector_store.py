#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import glob
import uuid
import argparse
import asyncio
import requests
from tqdm import tqdm
import json
import re
import time
from random import uniform

# Configuration
CHUNK_SIZE = 500  # Taille approximative des chunks en caractères
MAX_TOKENS = 4000  # Limite de tokens pour l'API Mistral (bien en dessous de la limite de 8192)
CHUNK_OVERLAP = 200  # Chevauchement entre les chunks
MISTRAL_API_KEY = "aGqrF2ADcSspcpLPL5YM31lj4AUDPAce"  # Clé API Mistral
PINECONE_API_KEY = "pcsk_38hV8j_ArTqGXkzUQfQWxQZKM93aCrDeVseVFcnbsNEdHmDfpZgRVxVQUJ72PEHLufXwv2"  # Clé API Pinecone
PINECONE_HOST = "https://scraped-content-wewx8nz.svc.aped-4627-b74a.pinecone.io"  # Host Pinecone
INDEX_NAME = "scraped-content"  # Nom de l'index Pinecone

# Dimension des embeddings Mistral - IMPORTANT pour la configuration de Pinecone
EMBEDDING_DIMENSION = 1024

class VectorStore:
    def __init__(self, markdown_dir, mistral_api_key=None, pinecone_api_key=None, pinecone_host=None):
        """
        Initialise le stockage vectoriel
        
        Args:
            markdown_dir (str): Chemin vers le répertoire contenant les fichiers markdown
            mistral_api_key (str): Clé API Mistral
            pinecone_api_key (str): Clé API Pinecone
            pinecone_host (str): Host Pinecone
        """
        self.markdown_dir = markdown_dir
        self.mistral_api_key = mistral_api_key or MISTRAL_API_KEY
        self.pinecone_api_key = pinecone_api_key or PINECONE_API_KEY
        self.pinecone_host = pinecone_host or PINECONE_HOST
        
        # Configuration de l'API Mistral
        self.mistral_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.mistral_api_key}"
        }
        
        # Configuration de l'API Pinecone
        self.pinecone_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Api-Key": self.pinecone_api_key
        }
    
    def estimate_tokens(self, text):
        """
        Estimation grossière du nombre de tokens dans un texte
        En moyenne, 1 token = ~4 caractères en anglais/français
        
        Args:
            text (str): Texte à évaluer
            
        Returns:
            int: Estimation du nombre de tokens
        """
        return len(text) // 4  # Estimation simple: 1 token ~ 4 caractères
    
    def chunk_markdown(self, content, source_filename):
        """
        Découpe un contenu markdown en chunks intelligents basés sur les sections
        avec limite de taille en tokens
        
        Args:
            content (str): Contenu markdown
            source_filename (str): Nom du fichier source
            
        Returns:
            list: Liste de chunks avec métadonnées
        """
        # Découper le contenu en sections basées sur les titres markdown
        sections = re.split(r'(#+\s.*?)\n', content)
        
        chunks = []
        current_section = ""
        
        for i, section in enumerate(sections):
            # Si c'est un titre
            if i % 2 == 0 and i > 0:
                current_section = sections[i-1].strip()
            
            # Si c'est du contenu
            if i % 2 == 1 and i < len(sections) - 1:
                current_text = sections[i+1]
                
                # Si le texte est trop long ou contient trop de tokens, le découper
                estimated_tokens = self.estimate_tokens(current_text)
                if len(current_text) > CHUNK_SIZE or estimated_tokens > MAX_TOKENS:
                    # Découper en paragraphes
                    paragraphs = re.split(r'\n\n+', current_text)
                    
                    current_chunk = ""
                    current_chunk_tokens = 0
                    
                    for paragraph in paragraphs:
                        paragraph_tokens = self.estimate_tokens(paragraph)
                        
                        # Si le paragraphe seul est déjà trop grand, le découper en phrases
                        if paragraph_tokens > MAX_TOKENS:
                            sentences = re.split(r'(?<=[.!?])\s+', paragraph)
                            
                            for sentence in sentences:
                                sentence_tokens = self.estimate_tokens(sentence)
                                
                                # Si l'ajout de la phrase dépasse la limite, créer un nouveau chunk
                                if current_chunk_tokens + sentence_tokens > MAX_TOKENS:
                                    if current_chunk:  # Éviter les chunks vides
                                        chunks.append({
                                            "id": str(uuid.uuid4()),
                                            "text": current_chunk.strip(),
                                            "source": source_filename,
                                            "section": current_section,
                                            "estimated_tokens": current_chunk_tokens
                                        })
                                    
                                    # Commencer un nouveau chunk
                                    current_chunk = sentence + " "
                                    current_chunk_tokens = sentence_tokens
                                else:
                                    current_chunk += sentence + " "
                                    current_chunk_tokens += sentence_tokens
                        
                        # Sinon, traiter le paragraphe normalement
                        elif current_chunk_tokens + paragraph_tokens > MAX_TOKENS:
                            if current_chunk:  # Éviter les chunks vides
                                chunks.append({
                                    "id": str(uuid.uuid4()),
                                    "text": current_chunk.strip(),
                                    "source": source_filename,
                                    "section": current_section,
                                    "estimated_tokens": current_chunk_tokens
                                })
                            
                            # Commencer un nouveau chunk
                            current_chunk = paragraph + "\n\n"
                            current_chunk_tokens = paragraph_tokens
                        else:
                            current_chunk += paragraph + "\n\n"
                            current_chunk_tokens += paragraph_tokens
                    
                    # Ajouter le dernier chunk s'il n'est pas vide
                    if current_chunk.strip():
                        chunks.append({
                            "id": str(uuid.uuid4()),
                            "text": current_chunk.strip(),
                            "source": source_filename,
                            "section": current_section,
                            "estimated_tokens": current_chunk_tokens
                        })
                else:
                    # Si le texte est assez court, l'ajouter directement
                    chunks.append({
                        "id": str(uuid.uuid4()),
                        "text": current_text,
                        "source": source_filename,
                        "section": current_section,
                        "estimated_tokens": estimated_tokens
                    })
        
        # Filtrer les chunks qui dépassent encore la limite (au cas où)
        filtered_chunks = [chunk for chunk in chunks if chunk["estimated_tokens"] <= MAX_TOKENS]
        
        if len(filtered_chunks) < len(chunks):
            print(f"Attention: {len(chunks) - len(filtered_chunks)} chunks ont été filtrés car ils dépassaient la limite de tokens.")
        
        return filtered_chunks
    
    async def generate_embeddings(self, chunks):
        """
        Génère des embeddings pour une liste de chunks de texte
        
        Args:
            chunks (list): Liste de chunks de texte
            
        Returns:
            list: Liste de chunks avec leurs embeddings
        """
        print(f"Génération d'embeddings pour {len(chunks)} chunks...")
        results = []
        
        # Traiter par lots plus petits pour éviter les limitations de l'API
        batch_size = 5  # Réduit la taille des lots
        for i in tqdm(range(0, len(chunks), batch_size)):
            batch = chunks[i:i+batch_size]
            texts = [chunk["text"] for chunk in batch]
            
            # Ajouter un délai aléatoire entre les requêtes pour éviter le rate limiting
            await asyncio.sleep(uniform(1.5, 3.0))
            
            # Logique de retry avec backoff exponentiel
            max_retries = 5
            retry_delay = 2
            
            for attempt in range(max_retries):
                try:
                    # Générer les embeddings avec Mistral API
                    payload = {
                        "model": "mistral-embed",
                        "input": texts,
                        "output_dtype": "float"
                    }
                    
                    response = requests.post(
                        "https://api.mistral.ai/v1/embeddings",
                        headers=self.mistral_headers,
                        json=payload
                    )
                    
                    if response.status_code == 429:  # Rate limit exceeded
                        wait_time = retry_delay * (2 ** attempt)  # Backoff exponentiel
                        print(f"Rate limit atteint. Attente de {wait_time} secondes avant de réessayer...")
                        await asyncio.sleep(wait_time)
                        continue
                    
                    if response.status_code != 200:
                        print(f"Erreur API: {response.status_code} - {response.text}")
                        break
                    
                    response_data = response.json()
                    
                    # Ajouter les embeddings aux chunks
                    for j, embedding_data in enumerate(response_data.get('data', [])):
                        if j < len(batch):
                            # Les embeddings sont directement dans l'objet embedding_data
                            batch[j]["embedding"] = embedding_data.get('embedding')
                    
                    results.extend(batch)
                    break  # Sortir de la boucle de retry si réussi
                    
                except Exception as e:
                    print(f"Erreur lors de la génération d'embeddings: {str(e)}")
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (2 ** attempt)
                        print(f"Nouvelle tentative dans {wait_time} secondes...")
                        await asyncio.sleep(wait_time)
                    else:
                        print("Nombre maximum de tentatives atteint. Passage au lot suivant.")
        
        return results
    
    def store_in_pinecone(self, chunks_with_embeddings):
        """
        Stocke les chunks avec embeddings dans Pinecone
        
        Args:
            chunks_with_embeddings (list): Liste de chunks avec leurs embeddings
        """
        print(f"Stockage de {len(chunks_with_embeddings)} chunks dans Pinecone...")
        
        # Préparer les données pour Pinecone
        vectors_to_upsert = []
        
        for chunk in chunks_with_embeddings:
            vectors_to_upsert.append({
                "id": chunk["id"],
                "values": chunk["embedding"],
                "metadata": {
                    "text": chunk["text"][:1000],  # Limiter la taille du texte dans les métadonnées
                    "source": chunk["source"],
                    "section": chunk["section"]
                }
            })
        
        # Upserter par lots pour éviter les limitations de taille
        batch_size = 100
        for i in range(0, len(vectors_to_upsert), batch_size):
            batch = vectors_to_upsert[i:i+batch_size]
            
            # Utiliser l'API REST de Pinecone pour upsert
            upsert_url = f"{self.pinecone_host}/vectors/upsert"
            payload = {
                "vectors": batch,
                "namespace": ""
            }
            
            try:
                response = requests.post(
                    upsert_url,
                    headers=self.pinecone_headers,
                    json=payload
                )
                
                if response.status_code != 200:
                    print(f"Erreur Pinecone: {response.status_code} - {response.text}")
                else:
                    print(f"Stocké {min(i+batch_size, len(vectors_to_upsert))}/{len(vectors_to_upsert)} vecteurs")
            except Exception as e:
                print(f"Erreur lors du stockage dans Pinecone: {str(e)}")
    
    async def process_markdown_files(self, max_files=0, test_mode=False):
        """
        Traite tous les fichiers markdown dans le répertoire spécifié
        
        Args:
            max_files (int): Nombre maximum de fichiers à traiter (0 = tous)
            test_mode (bool): Si True, traite uniquement un seul fichier et un seul chunk
        """
        if not os.path.exists(self.markdown_dir):
            print(f"Le répertoire {self.markdown_dir} n'existe pas.")
            return
        
        # Récupérer tous les fichiers markdown
        markdown_files = glob.glob(os.path.join(self.markdown_dir, "*.md"))
        
        if not markdown_files:
            print(f"Aucun fichier markdown trouvé dans {self.markdown_dir}.")
            return
        
        # Limiter le nombre de fichiers si demandé
        if max_files > 0 and max_files < len(markdown_files):
            print(f"Limitation à {max_files} fichiers sur {len(markdown_files)} disponibles")
            markdown_files = markdown_files[:max_files]
        
        # En mode test, ne traiter qu'un seul fichier
        if test_mode:
            print("Mode test activé - traitement d'un seul fichier avec un seul chunk")
            markdown_files = markdown_files[:1]
        
        print(f"Traitement de {len(markdown_files)} fichiers markdown...")
        
        for filename in tqdm(markdown_files):
            try:
                # Lire le contenu du fichier
                with open(filename, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Extraire le nom du fichier sans l'extension
                base_filename = os.path.basename(filename)
                
                # Découper le contenu en chunks
                chunks = self.chunk_markdown(content, base_filename)
                
                # En mode test, ne traiter qu'un seul chunk
                if test_mode and chunks:
                    chunks = chunks[:1]
                    print(f"Mode test: traitement d'un seul chunk du fichier {base_filename}")
                
                # Générer les embeddings
                chunks_with_embeddings = await self.generate_embeddings(chunks)
                
                # Stocker dans Pinecone
                self.store_in_pinecone(chunks_with_embeddings)
                
                print(f"Fichier {filename} traité avec succès")
            except Exception as e:
                print(f"Erreur lors du traitement de {filename}: {str(e)}")
    
    def search_in_pinecone(self, query, top_k=5):
        """
        Recherche dans Pinecone en utilisant une requête
        
        Args:
            query (str): Requête de recherche
            top_k (int): Nombre de résultats à retourner
            
        Returns:
            list: Résultats de la recherche
        """
        print(f"Recherche pour: '{query}'")
        
        # Générer l'embedding de la requête
        payload = {
            "model": "mistral-embed",
            "input": [query],
            "output_dtype": "float"
        }
        
        response = requests.post(
            "https://api.mistral.ai/v1/embeddings",
            headers=self.mistral_headers,
            json=payload
        )
        
        if response.status_code != 200:
            print(f"Erreur lors de la génération de l'embedding: {response.text}")
            return []
        
        response_data = response.json()
        query_embedding = response_data.get('data', [])[0].get('embedding')
        
        # Rechercher dans Pinecone avec l'API REST
        query_url = f"{self.pinecone_host}/query"
        payload = {
            "vector": query_embedding,
            "topK": top_k,
            "includeMetadata": True,
            "namespace": ""
        }
        
        try:
            response = requests.post(
                query_url,
                headers=self.pinecone_headers,
                json=payload
            )
            
            if response.status_code != 200:
                print(f"Erreur Pinecone: {response.status_code} - {response.text}")
                return []
            
            results = response.json()
            
            # Formater les résultats
            formatted_results = []
            for match in results.get('matches', []):
                formatted_results.append({
                    "score": match.get('score'),
                    "text": match.get('metadata', {}).get('text', ''),
                    "source": match.get('metadata', {}).get('source', ''),
                    "section": match.get('metadata', {}).get('section', '')
                })
            
            return formatted_results
        except Exception as e:
            print(f"Erreur lors de la recherche dans Pinecone: {str(e)}")
            return []

async def main():
    """
    Fonction principale
    """
    parser = argparse.ArgumentParser(description="Vectoriser des fichiers markdown et les stocker dans Pinecone")
    parser.add_argument("--markdown_dir", help="Chemin vers le répertoire contenant les fichiers markdown")
    parser.add_argument("--query", help="Requête de recherche")
    parser.add_argument("--max_files", type=int, default=0, help="Nombre maximum de fichiers à traiter (0 = tous)")
    parser.add_argument("--test", action="store_true", help="Mode test avec un seul fichier et un seul chunk")
    args = parser.parse_args()
    
    if not args.markdown_dir and not args.query:
        parser.print_help()
        return
    
    vector_store = VectorStore(
        markdown_dir=args.markdown_dir if args.markdown_dir else None,
        mistral_api_key=MISTRAL_API_KEY,
        pinecone_api_key=PINECONE_API_KEY,
        pinecone_host=PINECONE_HOST
    )
    
    if args.markdown_dir:
        # Vectoriser et stocker les fichiers markdown
        await vector_store.process_markdown_files(max_files=args.max_files, test_mode=args.test)
    
    if args.query:
        # Rechercher dans Pinecone
        results = vector_store.search_in_pinecone(args.query)
        
        print("\nRésultats de la recherche:")
        for i, result in enumerate(results):
            print(f"\n{i+1}. Score: {result['score']:.4f}")
            print(f"Source: {result['source']}")
            print(f"Section: {result['section']}")
            print(f"Texte: {result['text'][:200]}...")
    else:
        # Mode traitement des fichiers
        print("Traitement terminé avec succès!")

if __name__ == "__main__":
    asyncio.run(main())
