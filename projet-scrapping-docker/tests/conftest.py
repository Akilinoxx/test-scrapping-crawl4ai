"""Configuration pytest pour les tests."""

import pytest
import os
import sys
from unittest.mock import patch

# Ajouter le dossier src au path Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@pytest.fixture(scope="session")
def test_env():
    """Variables d'environnement pour les tests."""
    return {
        'PINECONE_API_KEY': 'test_pinecone_key_12345',
        'PINECONE_HOST': 'https://test-index.svc.pinecone.io',
        'MISTRAL_API_KEY': 'test_mistral_key_12345',
        'SCRAPER_DELAY': '0.1',
        'MAX_WORKERS': '2',
        'MAX_CONTEXT_LENGTH': '1000',
        'TEMPERATURE': '0.5',
        'MAX_TOKENS': '100'
    }


@pytest.fixture(autouse=True)
def setup_test_env(test_env):
    """Configuration automatique de l'environnement de test."""
    with patch.dict(os.environ, test_env):
        yield


@pytest.fixture
def sample_markdown_content():
    """Contenu markdown d'exemple pour les tests."""
    return """# Test Document

This is a test document for unit testing.

## Introduction

This section contains introductory information about the test document.
It includes multiple sentences to test text processing capabilities.

## Main Content

Here we have the main content of the document.
This content should be processed and vectorized properly.

### Subsection

Additional content in a subsection.

## Conclusion

This is the conclusion of the test document.
It wraps up all the information presented above.
"""


@pytest.fixture
def sample_scraped_data():
    """Données scrapées d'exemple."""
    return {
        'url': 'https://example.com',
        'title': 'Test Page Title',
        'content': 'This is test content from a scraped webpage.',
        'metadata': {
            'scraped_at': '2024-01-15T10:30:00Z',
            'word_count': 10,
            'language': 'en'
        }
    }


@pytest.fixture
def mock_pinecone_response():
    """Réponse Pinecone mockée."""
    return {
        'matches': [
            {
                'id': 'test_chunk_1',
                'score': 0.95,
                'metadata': {
                    'text': 'This is relevant test content.',
                    'source': 'test_document.md',
                    'chunk_index': 0
                }
            },
            {
                'id': 'test_chunk_2',
                'score': 0.87,
                'metadata': {
                    'text': 'Another piece of relevant content.',
                    'source': 'test_document.md',
                    'chunk_index': 1
                }
            }
        ]
    }


@pytest.fixture
def mock_mistral_embedding():
    """Embedding Mistral mocké."""
    return [0.1] * 1024  # Vecteur de 1024 dimensions


@pytest.fixture
def mock_mistral_response():
    """Réponse Mistral AI mockée."""
    return {
        'choices': [
            {
                'message': {
                    'content': 'This is a test response from Mistral AI.'
                }
            }
        ]
    }
