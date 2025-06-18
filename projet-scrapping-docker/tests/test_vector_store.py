"""Tests pour le module vector_store."""

import pytest
import os
import sys
from unittest.mock import Mock, patch, MagicMock

# Ajouter le dossier src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from vector_store import VectorStore


class TestVectorStore:
    """Tests pour la classe VectorStore."""

    @pytest.fixture
    def mock_env_vars(self):
        """Mock des variables d'environnement."""
        with patch.dict(os.environ, {
            'PINECONE_API_KEY': 'test_key',
            'PINECONE_HOST': 'https://test-host.pinecone.io',
            'MISTRAL_API_KEY': 'test_mistral_key'
        }):
            yield

    @pytest.fixture
    def vector_store(self, mock_env_vars):
        """Instance de VectorStore pour les tests."""
        with patch('vector_store.Pinecone'), \
             patch('vector_store.requests.post'):
            return VectorStore()

    def test_init(self, mock_env_vars):
        """Test d'initialisation de VectorStore."""
        with patch('vector_store.Pinecone') as mock_pinecone, \
             patch('vector_store.requests.post'):
            
            vector_store = VectorStore()
            
            # Vérifier que Pinecone est initialisé
            mock_pinecone.assert_called_once()
            assert vector_store.index_name == "scraped-content"

    def test_get_embedding_success(self, vector_store):
        """Test de génération d'embedding réussie."""
        # Mock de la réponse API
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': [{'embedding': [0.1, 0.2, 0.3]}]
        }
        
        with patch('vector_store.requests.post', return_value=mock_response):
            embedding = vector_store.get_embedding("test text")
            
            assert embedding == [0.1, 0.2, 0.3]

    def test_get_embedding_failure(self, vector_store):
        """Test de gestion d'erreur lors de la génération d'embedding."""
        # Mock d'une réponse d'erreur
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        
        with patch('vector_store.requests.post', return_value=mock_response):
            embedding = vector_store.get_embedding("test text")
            
            assert embedding is None

    def test_chunk_text(self, vector_store):
        """Test de découpage de texte en chunks."""
        text = "This is a test. " * 100  # Texte long
        chunks = vector_store.chunk_text(text, chunk_size=50, overlap=10)
        
        assert len(chunks) > 1
        assert all(len(chunk) <= 60 for chunk in chunks)  # 50 + 10 overlap

    def test_process_markdown_file(self, vector_store):
        """Test de traitement d'un fichier markdown."""
        # Créer un fichier markdown temporaire
        test_content = """# Test Title

This is test content for the markdown file.

## Section 1
Some content here.

## Section 2
More content here.
"""
        
        with patch('builtins.open', mock_open(read_data=test_content)):
            with patch.object(vector_store, 'get_embedding', return_value=[0.1, 0.2, 0.3]):
                with patch.object(vector_store, 'upsert_vectors') as mock_upsert:
                    
                    vector_store.process_markdown_file("test.md")
                    
                    # Vérifier que upsert_vectors a été appelé
                    mock_upsert.assert_called()

    def test_search_similar_content(self, vector_store):
        """Test de recherche de contenu similaire."""
        # Mock de la réponse de recherche Pinecone
        mock_matches = [
            {
                'id': 'test_id_1',
                'score': 0.9,
                'metadata': {
                    'text': 'Test content 1',
                    'source': 'test1.md'
                }
            },
            {
                'id': 'test_id_2', 
                'score': 0.8,
                'metadata': {
                    'text': 'Test content 2',
                    'source': 'test2.md'
                }
            }
        ]
        
        mock_query_response = {'matches': mock_matches}
        
        with patch.object(vector_store, 'get_embedding', return_value=[0.1, 0.2, 0.3]):
            with patch.object(vector_store.index, 'query', return_value=mock_query_response):
                
                results = vector_store.search_similar_content("test query", top_k=2)
                
                assert len(results) == 2
                assert results[0]['score'] == 0.9
                assert results[0]['text'] == 'Test content 1'


def mock_open(read_data=""):
    """Helper pour mocker l'ouverture de fichiers."""
    mock = MagicMock()
    mock.return_value.__enter__.return_value.read.return_value = read_data
    return mock


if __name__ == "__main__":
    pytest.main([__file__])
