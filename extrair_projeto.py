"""Extrai texto do PDF do projeto"""
from pypdf import PdfReader
import sys

try:
    reader = PdfReader('pdfs_projeto/Projeto-1.pdf')
    print(f"Total de páginas: {len(reader.pages)}\n")
    print("="*70)
    
    for i, page in enumerate(reader.pages, 1):
        print(f"\n--- PÁGINA {i} ---\n")
        text = page.extract_text()
        print(text)
        print("\n" + "="*70)
        
except Exception as e:
    print(f"Erro: {e}")
    sys.exit(1)
