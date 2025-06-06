import asyncio
import json
import os
from crawl4ai import AsyncWebCrawler

async def main():
    # Créer un répertoire pour les résultats si nécessaire
    output_dir = "crawl4ai_test_results"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # URL à tester
    url = "https://www.python.org"
    
    print(f"Scraping de {url} avec Crawl4AI...")
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url)
        
        # Sauvegarder les attributs dans un fichier JSON pour inspection
        attrs = {}
        for attr in dir(result):
            if not attr.startswith('_'):
                try:
                    value = getattr(result, attr)
                    # Convertir en string si ce n'est pas un type JSON sérialisable
                    if not isinstance(value, (str, int, float, bool, list, dict, type(None))):
                        value = str(value)
                    attrs[attr] = value
                except:
                    attrs[attr] = "<Impossible d'accéder à cet attribut>"
        
        # Sauvegarder les attributs dans un fichier JSON
        with open(os.path.join(output_dir, "attributes.json"), 'w', encoding='utf-8') as f:
            json.dump(attrs, f, ensure_ascii=False, indent=2)
        
        # Sauvegarder le HTML dans un fichier
        if hasattr(result, 'html') and result.html:
            with open(os.path.join(output_dir, "content.html"), 'w', encoding='utf-8') as f:
                f.write(result.html)
        
        # Sauvegarder le texte dans un fichier
        if hasattr(result, 'text') and result.text:
            with open(os.path.join(output_dir, "content.txt"), 'w', encoding='utf-8') as f:
                f.write(result.text)
        
        # Sauvegarder le markdown dans un fichier
        if hasattr(result, 'markdown') and result.markdown:
            with open(os.path.join(output_dir, "content.md"), 'w', encoding='utf-8') as f:
                f.write(result.markdown)
        
        # Afficher quelques informations
        print(f"\nScraping terminé. Résultats sauvegardés dans le dossier '{output_dir}'")
        print("\nAttributs disponibles:")
        for attr in dir(result):
            if not attr.startswith('_'):
                print(f"- {attr}")

if __name__ == "__main__":
    asyncio.run(main())
