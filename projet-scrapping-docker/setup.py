"""Setup configuration for Web Scraping AI Chatbot."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements_vector.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="web-scraping-ai-chatbot",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Pipeline complet de scraping web, vectorisation et chatbot IA",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/votre-username/web-scraping-ai-chatbot",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "pre-commit>=2.20.0",
            "isort>=5.10.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "web-scraper=src.app:main",
            "ai-chatbot=src.chatbot:main",
            "vectorize-content=src.vector_store:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.txt", "*.yml", "*.yaml", "*.md"],
    },
)
