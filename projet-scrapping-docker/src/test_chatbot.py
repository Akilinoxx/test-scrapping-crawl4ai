#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de test pour le chatbot - permet de tester des requêtes ponctuelles
"""

from chatbot import ChatBot

def test_connection():
    """Test de connexion aux APIs"""
    print("🔧 Test de connexion aux APIs...")
    
    chatbot = ChatBot()
    
    # Test de recherche simple
    test_query = "test de connexion"
    results = chatbot.search_knowledge_base(test_query, top_k=1)
    
    if results:
        print("✅ Connexion réussie à Pinecone et Mistral")
        print(f"Nombre de résultats trouvés: {len(results)}")
        return True
    else:
        print("❌ Problème de connexion ou base de données vide")
        return False

def test_queries():
    """Test avec quelques requêtes d'exemple"""
    chatbot = ChatBot()
    
    test_questions = [
        "Qu'est-ce que le scraping web ?",
        "Comment fonctionne l'indexation ?",
        "Quelles sont les technologies utilisées ?",
        "Parle-moi des APIs",
        "Qu'est-ce que Pinecone ?"
    ]
    
    print("\n🧪 **Tests avec des questions d'exemple:**")
    print("=" * 50)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n📝 **Test {i}/5:** {question}")
        print("-" * 30)
        
        try:
            response = chatbot.chat(question)
            print(f"🤖 **Réponse:** {response[:200]}...")
            print("✅ Test réussi")
        except Exception as e:
            print(f"❌ Erreur: {str(e)}")
        
        print("-" * 50)
    
    # Afficher les stats
    chatbot.show_stats()

def interactive_test():
    """Mode interactif pour tester des requêtes personnalisées"""
    print("\n🎯 **Mode Test Interactif**")
    print("Tapez 'back' pour revenir au menu principal")
    
    chatbot = ChatBot()
    
    while True:
        query = input("\n❓ **Question de test:** ").strip()
        
        if query.lower() == 'back':
            break
        elif not query:
            continue
        
        try:
            response = chatbot.chat(query)
            print(f"\n🤖 **Réponse:**\n{response}")
        except Exception as e:
            print(f"❌ Erreur: {str(e)}")

def main():
    """Menu principal pour les tests"""
    while True:
        print("\n🧪 **Menu de Test du Chatbot**")
        print("=" * 40)
        print("1. Test de connexion")
        print("2. Tests automatiques avec questions d'exemple")
        print("3. Mode test interactif")
        print("4. Lancer le chatbot complet")
        print("5. Quitter")
        print("=" * 40)
        
        choice = input("Choisissez une option (1-5): ").strip()
        
        if choice == '1':
            test_connection()
        elif choice == '2':
            if test_connection():
                test_queries()
        elif choice == '3':
            if test_connection():
                interactive_test()
        elif choice == '4':
            print("\n🚀 Lancement du chatbot complet...")
            from chatbot import main as chatbot_main
            chatbot_main()
        elif choice == '5':
            print("👋 Au revoir !")
            break
        else:
            print("⚠️ Option invalide, veuillez choisir entre 1 et 5.")

if __name__ == "__main__":
    main()
