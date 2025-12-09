"""
Script para indexar documentos IRIS na base vetorial
----------------------------------------------------
Execute este script antes de usar o sistema pela primeira vez

Uso:
    python setup_rag.py          # Setup interativo
    python setup_rag.py --auto   # Indexar pasta local automaticamente
    python setup_rag.py --clear  # Limpar banco existente
"""

import os
import sys
from pathlib import Path

# Ajustar o path se necessário
sys.path.insert(0, str(Path(__file__).parent))

from Agent_C.agent_c_db import (
    index_local_folder, 
    index_online_pdf, 
    clear_chroma_db,
    test_rag_search,
    CHROMA_PATH as DEFAULT_CHROMA_PATH
)


# =====================================================================
# CONFIGURAÇÕES
# =====================================================================
# Você pode ajustar esses caminhos conforme sua estrutura
PDF_FOLDER = Path("Agent_C/pdfs")
CHROMA_PATH = Path(DEFAULT_CHROMA_PATH)


# URLs das diretrizes IRIS oficiais
URLS_IRIS_OFICIAIS = [
    "http://www.iris-kidney.com/pdf/IRIS_Staging_of_CKD_modified_2019.pdf",
    # Adicione mais URLs conforme necessário
]


# =====================================================================
# FUNÇÃO PRINCIPAL
# =====================================================================
def setup_rag_database():
    """
    Setup interativo do sistema RAG
    """
    print("=" * 70)
    print("🐱 CONFIGURAÇÃO DO SISTEMA RAG - DIRETRIZES IRIS")
    print("=" * 70)
    
    # Criar diretórios se não existirem
    PDF_FOLDER.mkdir(parents=True, exist_ok=True)
    CHROMA_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"\n📁 Configuração:")
    print(f"  • Pasta de PDFs: {PDF_FOLDER.absolute()}")
    print(f"  • Base vetorial: {CHROMA_PATH.absolute()}")
    
    # Verificar se banco já existe
    if CHROMA_PATH.exists():
        print(f"\n⚠️  Banco vetorial já existe!")
        resposta = input("Deseja limpar e reindexar tudo? (s/n): ")
        if resposta.lower() == 's':
            result = clear_chroma_db(str(CHROMA_PATH))
            if "error" in result:
                print(f"❌ {result['error']}")
                return
            print("✅ Banco limpo com sucesso!")
    
    # Menu principal
    while True:
        print("\n" + "-" * 70)
        print("OPÇÕES DE INDEXAÇÃO")
        print("-" * 70)
        print("1. Indexar PDFs da pasta local")
        print("2. Indexar PDF online (URL)")
        print("3. Testar busca RAG")
        print("4. Sair")
        
        escolha = input("\nEscolha uma opção (1-4): ").strip()
        
        if escolha == "1":
            indexar_pasta_local()
        elif escolha == "2":
            indexar_pdf_online()
        elif escolha == "3":
            test_rag_search()
        elif escolha == "4":
            break
        else:
            print("❌ Opção inválida")
    
    # Verificação final
    print("\n" + "=" * 70)
    print("VERIFICAÇÃO FINAL")
    print("=" * 70)
    
    if CHROMA_PATH.exists():
        print(f"✅ Base vetorial criada em: {CHROMA_PATH.absolute()}")
        print("\n🚀 Sistema pronto para uso!")
        print("\nPróximo passo:")
        print("  python run_lg.py")
        print("  ou")
        print("  langgraph dev")
    else:
        print("⚠️  Base vetorial não foi criada.")
        print("   Certifique-se de indexar pelo menos um documento.")
    
    print("=" * 70)


# =====================================================================
# FUNÇÕES AUXILIARES
# =====================================================================

def indexar_pasta_local():
    """Indexa PDFs da pasta local"""
    print("\n" + "-" * 70)
    print("📂 INDEXAÇÃO: Pasta Local")
    print("-" * 70)
    
    # Verificar se há PDFs
    pdfs = list(PDF_FOLDER.glob("*.pdf"))
    
    if not pdfs:
        print(f"\n⚠️  Nenhum PDF encontrado em: {PDF_FOLDER.absolute()}")
        print("\n💡 Instruções:")
        print(f"   1. Coloque os PDFs das diretrizes IRIS em: {PDF_FOLDER.absolute()}")
        print(f"   2. Execute este script novamente")
        return
    
    print(f"\n✅ Encontrados {len(pdfs)} PDF(s):")
    for pdf in pdfs:
        print(f"   • {pdf.name}")
    
    resposta = input("\nDeseja indexar esses PDFs? (s/n): ")
    
    if resposta.lower() != 's':
        print("❌ Operação cancelada")
        return
    
    print(f"\n📄 Indexando PDFs...")
    result = index_local_folder(
        folder_path=str(PDF_FOLDER),
        chroma_path=str(CHROMA_PATH)
    )
    
    if "error" in result:
        print(f"❌ Erro: {result['error']}")
    else:
        print(f"\n✅ Indexação concluída com sucesso!")
        print(f"   • Documentos: {result['source_documents']}")
        print(f"   • Chunks: {result['indexed_chunks']}")


def indexar_pdf_online():
    """Indexa PDF de uma URL"""
    print("\n" + "-" * 70)
    print("🌐 INDEXAÇÃO: PDF Online")
    print("-" * 70)
    
    print("\n📋 URLs sugeridas (diretrizes IRIS):")
    for i, url in enumerate(URLS_IRIS_OFICIAIS, 1):
        print(f"   {i}. {url}")
    
    print("\n💡 Você pode:")
    print("   • Digitar o número da URL sugerida")
    print("   • Colar sua própria URL")
    print("   • Pressionar Enter para cancelar")
    
    entrada = input("\nURL ou número: ").strip()
    
    if not entrada:
        print("❌ Operação cancelada")
        return
    
    # Verificar se é número (URL sugerida)
    if entrada.isdigit():
        idx = int(entrada) - 1
        if 0 <= idx < len(URLS_IRIS_OFICIAIS):
            url = URLS_IRIS_OFICIAIS[idx]
        else:
            print("❌ Número inválido")
            return
    else:
        url = entrada
    
    if not url.startswith("http"):
        print("❌ URL inválida (deve começar com http:// ou https://)")
        return
    
    print(f"\n📥 Baixando e indexando: {url}")
    result = index_online_pdf(
        url=url,
        chroma_path=str(CHROMA_PATH)
    )
    
    if "error" in result:
        print(f"❌ Erro: {result['error']}")
    else:
        print(f"\n✅ Indexação concluída com sucesso!")
        print(f"   • URL: {result['source_url']}")
        print(f"   • Páginas: {result['source_documents']}")
        print(f"   • Chunks: {result['indexed_chunks']}")


def setup_automatico():
    """Setup automático (indexa pasta local sem interação)"""
    print("=" * 70)
    print("🤖 SETUP AUTOMÁTICO")
    print("=" * 70)
    
    # Criar diretórios
    PDF_FOLDER.mkdir(parents=True, exist_ok=True)
    CHROMA_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # Verificar PDFs
    pdfs = list(PDF_FOLDER.glob("*.pdf"))
    
    if not pdfs:
        print(f"\n⚠️  Nenhum PDF encontrado em: {PDF_FOLDER.absolute()}")
        print(f"\n💡 Coloque os PDFs nesta pasta e execute novamente.")
        return False
    
    print(f"\n✅ Encontrados {len(pdfs)} PDF(s)")
    
    # Limpar banco existente
    if CHROMA_PATH.exists():
        print(f"\n🗑️  Limpando banco existente...")
        clear_chroma_db(str(CHROMA_PATH))
    
    # Indexar
    print(f"\n📄 Indexando...")
    result = index_local_folder(
        folder_path=str(PDF_FOLDER),
        chroma_path=str(CHROMA_PATH)
    )
    
    if "error" in result:
        print(f"❌ Erro: {result['error']}")
        return False
    
    print(f"\n✅ Setup concluído!")
    print(f"   • Chunks indexados: {result['indexed_chunks']}")
    return True


# =====================================================================
# EXECUÇÃO
# =====================================================================
if __name__ == "__main__":
    # Verificar argumentos
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg == "--auto":
            success = setup_automatico()
            sys.exit(0 if success else 1)
        
        elif arg == "--clear":
            print("🗑️  Limpando banco vetorial...")
            result = clear_chroma_db(str(CHROMA_PATH))
            if "error" in result:
                print(f"❌ {result['error']}")
                sys.exit(1)
            else:
                print(f"✅ {result['message']}")
                sys.exit(0)
        
        elif arg in ["--help", "-h"]:
            print("Uso:")
            print("  python setup_rag.py          # Setup interativo")
            print("  python setup_rag.py --auto   # Setup automático")
            print("  python setup_rag.py --clear  # Limpar banco")
            print("  python setup_rag.py --help   # Mostrar esta mensagem")
            sys.exit(0)
        
        else:
            print(f"❌ Argumento desconhecido: {arg}")
            print("Use --help para ver opções disponíveis")
            sys.exit(1)
    
    # Setup interativo (padrão)
    try:
        setup_rag_database()
    except KeyboardInterrupt:
        print("\n\n⚠️  Operação cancelada pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)