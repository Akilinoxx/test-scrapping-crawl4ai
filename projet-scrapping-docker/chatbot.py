#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import requests
import json
from datetime import datetime
import asyncio

# Configuration
MISTRAL_API_KEY = "aGqrF2ADcSspcpLPL5YM31lj4AUDPAce"
PINECONE_API_KEY = "pcsk_38hV8j_ArTqGXkzUQfQWxQZKM93aCrDeVseVFcnbsNEdHmDfpZgRVxVQUJ72PEHLufXwv2"
PINECONE_HOST = "https://scraped-content-wewx8nz.svc.aped-4627-b74a.pinecone.io"

class ChatBot:
    def __init__(self, mistral_api_key=None, pinecone_api_key=None, pinecone_host=None):
        """
        Initialise le chatbot avec les connexions aux APIs
        
        Args:
            mistral_api_key (str): Clé API Mistral
            pinecone_api_key (str): Clé API Pinecone  
            pinecone_host (str): Host Pinecone
        """
        self.mistral_api_key = mistral_api_key or MISTRAL_API_KEY
        self.pinecone_api_key = pinecone_api_key or PINECONE_API_KEY
        self.pinecone_host = pinecone_host or PINECONE_HOST
        
        # Configuration des headers pour les APIs
        self.mistral_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.mistral_api_key}"
        }
        
        self.pinecone_headers = {
            "Api-Key": self.pinecone_api_key,
            "Content-Type": "application/json"
        }
        
        # Historique de conversation
        self.conversation_history = []
        
    def search_knowledge_base(self, query, top_k=3):
        """
        Recherche dans la base de connaissances Pinecone
        
        Args:
            query (str): Requête de recherche
            top_k (int): Nombre de résultats à retourner
            
        Returns:
            list: Résultats de la recherche avec métadonnées
        """
        print(f"🔍 Recherche dans la base de connaissances: '{query}'")
        
        try:
            # Générer l'embedding de la requête avec Mistral
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
                print(f"❌ Erreur lors de la génération de l'embedding: {response.text}")
                return []
            
            response_data = response.json()
            query_embedding = response_data.get('data', [])[0].get('embedding')
            
            # Rechercher dans Pinecone
            query_url = f"{self.pinecone_host}/query"
            payload = {
                "vector": query_embedding,
                "topK": top_k,
                "includeMetadata": True,
                "namespace": ""
            }
            
            response = requests.post(
                query_url,
                headers=self.pinecone_headers,
                json=payload
            )
            
            if response.status_code != 200:
                print(f"❌ Erreur lors de la recherche Pinecone: {response.text}")
                return []
            
            results = response.json()
            matches = results.get('matches', [])
            
            print(f"✅ Trouvé {len(matches)} résultats pertinents")
            return matches
            
        except Exception as e:
            print(f"❌ Erreur lors de la recherche: {str(e)}")
            return []
    
    def generate_response(self, user_query, context_chunks):
        """
        Génère une réponse en utilisant Mistral avec le contexte trouvé
        
        Args:
            user_query (str): Question de l'utilisateur
            context_chunks (list): Chunks de contexte trouvés dans Pinecone
            
        Returns:
            str: Réponse générée
        """
        try:
            # Construire le contexte à partir des chunks trouvés
            context = ""
            sources = set()
            
            for i, chunk in enumerate(context_chunks):
                metadata = chunk.get('metadata', {})
                text = metadata.get('text', '')
                source = metadata.get('source', 'Source inconnue')
                section = metadata.get('section', '')
                
                sources.add(source)
                context += f"[Extrait {i+1} - {source}]\n{text}\n\n"
            
            # Construire le prompt pour Mistral
            system_prompt = """Tu es un assistant IA spécialisé dans l'analyse de contenu web scrapé. 
Tu réponds aux questions en te basant uniquement sur le contexte fourni.
Si l'information n'est pas dans le contexte, dis-le clairement.
Sois précis et cite tes sources quand possible."""
            
            user_prompt = f"""Contexte disponible:
{context}

Question de l'utilisateur: {user_query}

Réponds à la question en te basant sur le contexte fourni. Si l'information n'est pas disponible dans le contexte, dis-le clairement."""
            
            # Appel à l'API Mistral pour la génération de texte
            payload = {
                "model": "mistral-small-latest",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 1000
            }
            
            response = requests.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers=self.mistral_headers,
                json=payload
            )
            
            if response.status_code != 200:
                print(f"❌ Erreur lors de la génération de réponse: {response.text}")
                return "Désolé, je n'ai pas pu générer une réponse. Erreur de l'API."
            
            response_data = response.json()
            generated_response = response_data['choices'][0]['message']['content']
            
            # Ajouter les sources à la réponse
            if sources:
                sources_text = "\n\n📚 **Sources consultées:**\n" + "\n".join([f"- {source}" for source in sources])
                generated_response += sources_text
            
            return generated_response
            
        except Exception as e:
            print(f"❌ Erreur lors de la génération de réponse: {str(e)}")
            return "Désolé, une erreur s'est produite lors de la génération de la réponse."
    
    def chat(self, user_input):
        """
        Traite une question de l'utilisateur et retourne une réponse
        
        Args:
            user_input (str): Question de l'utilisateur
            
        Returns:
            str: Réponse du chatbot
        """
        # Rechercher dans la base de connaissances
        relevant_chunks = self.search_knowledge_base(user_input, top_k=3)
        
        if not relevant_chunks:
            return "❌ Désolé, je n'ai trouvé aucune information pertinente dans ma base de connaissances pour répondre à votre question."
        
        # Générer une réponse basée sur le contexte trouvé
        response = self.generate_response(user_input, relevant_chunks)
        
        # Sauvegarder dans l'historique
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "user_query": user_input,
            "response": response,
            "sources_count": len(relevant_chunks)
        })
        
        return response
    
    def show_stats(self):
        """Affiche des statistiques sur les conversations"""
        print(f"\n📊 **Statistiques de conversation:**")
        print(f"- Nombre de questions posées: {len(self.conversation_history)}")
        if self.conversation_history:
            print(f"- Première question: {self.conversation_history[0]['timestamp']}")
            print(f"- Dernière question: {self.conversation_history[-1]['timestamp']}")
    
    def save_conversation(self, filename=None):
        """Sauvegarde l'historique de conversation"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversation_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.conversation_history, f, ensure_ascii=False, indent=2)
            print(f"💾 Conversation sauvegardée dans {filename}")
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde: {str(e)}")

def main():
    """Fonction principale pour lancer le chatbot interactif"""
    print("🤖 **Chatbot de Recherche Sémantique**")
    print("=" * 50)
    print("Connecté à votre base vectorielle Pinecone")
    print("Tapez 'quit', 'exit' ou 'bye' pour quitter")
    print("Tapez 'stats' pour voir les statistiques")
    print("Tapez 'save' pour sauvegarder la conversation")
    print("=" * 50)
    
    # Initialiser le chatbot
    chatbot = ChatBot()
    
    # Boucle de conversation
    while True:
        try:
            # Demander une question à l'utilisateur
            user_input = input("\n❓ **Votre question:** ").strip()
            
            # Commandes spéciales
            if user_input.lower() in ['quit', 'exit', 'bye', 'q']:
                print("\n👋 Au revoir ! Merci d'avoir utilisé le chatbot.")
                break
            elif user_input.lower() == 'stats':
                chatbot.show_stats()
                continue
            elif user_input.lower() == 'save':
                chatbot.save_conversation()
                continue
            elif not user_input:
                print("⚠️ Veuillez poser une question.")
                continue
            
            # Traiter la question
            print("\n🤔 Réflexion en cours...")
            response = chatbot.chat(user_input)
            
            # Afficher la réponse
            print(f"\n🤖 **Réponse:**\n{response}")
            
        except KeyboardInterrupt:
            print("\n\n👋 Au revoir ! Merci d'avoir utilisé le chatbot.")
            break
        except Exception as e:
            print(f"\n❌ Erreur inattendue: {str(e)}")

if __name__ == "__main__":
    main()
