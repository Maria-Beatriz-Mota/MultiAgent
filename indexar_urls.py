"""
Script para indexar URLs específicas rapidamente
"""
from Agent_C.agent_c_db import index_web_page, CHROMA_PATH

# URLs para indexar
URLS = [
    "https://www.vet.cornell.edu/departments-centers-and-institutes/cornell-feline-health-center/health-information/feline-health-topics/chronic-kidney-disease",
    "https://www.pdsa.org.uk/pet-help-and-advice/pet-health-hub/conditions/chronic-kidney-disease-in-cats",
    "https://academy.royalcanin.com/en/veterinary/chronic-kidney-disease-in-asymptomatic-cats",   
]

print("=" * 70)
print("📚 INDEXANDO PÁGINAS WEB SOBRE DRC FELINA")
print("=" * 70)

total_chunks = 0
sucesso = 0
falhas = 0

for i, url in enumerate(URLS, 1):
    print(f"\n[{i}/{len(URLS)}] Processando: {url[:80]}...")
    
    try:
        result = index_web_page(url, CHROMA_PATH)
        
        if "error" in result:
            print(f"❌ Erro: {result['error']}")
            falhas += 1
        else:
            chunks = result.get("indexed_chunks", 0)
            total_chunks += chunks
            sucesso += 1
            print(f"✅ Indexado: {chunks} chunks")
    
    except Exception as e:
        print(f"❌ Exceção: {str(e)[:100]}")
        falhas += 1

print("\n" + "=" * 70)
print("📊 RESUMO DA INDEXAÇÃO")
print("=" * 70)
print(f"✅ Sucesso: {sucesso}/{len(URLS)}")
print(f"❌ Falhas: {falhas}/{len(URLS)}")
print(f"📦 Total de chunks indexados: {total_chunks}")
print("=" * 70)
print("\n🚀 Sistema RAG atualizado! Execute: python run_lg.py")
