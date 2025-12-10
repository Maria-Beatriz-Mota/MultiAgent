"""
Agent_C/agent_c_db.py - VERSÃO COMPLETA
Funções para RAG: busca + indexação de PDFs
"""

import os
import requests
from pathlib import Path
from typing import List, Dict, Any

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader, WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModel
import torch


# =====================================================================
# CONFIGURAÇÃO
# =====================================================================
CHROMA_PATH = "Agent_C/chroma_db"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Configuração do text splitter
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


# =====================================================================
# FUNÇÃO DE BUSCA (já existente, corrigida)
# =====================================================================
def rag_search(chroma_path: str, query: str, k: int = 8, max_context_length_chars: int = 3000):
    """
    Busca documentos relevantes no banco Chroma e retorna um contexto limitado.
    
    Args:
        chroma_path: Caminho para o banco Chroma
        query: Query de busca
        k: Número máximo de docs a recuperar
        max_context_length_chars: Limite de chars do contexto combinado
    
    Returns:
        Dict com context, docs, context_length, docs_used
    """
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBED_MODEL,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True, 'batch_size': 32}
    )

    vectordb = Chroma(persist_directory=chroma_path, embedding_function=embeddings)

    # Recupera top-k documentos
    docs = vectordb.similarity_search(query, k=k)

    # Ordena docs por tamanho ascendente
    docs_sorted = sorted(docs, key=lambda d: len(getattr(d, "page_content", "") or ""))

    context_parts = []
    total_len = 0
    docs_used = 0

    for doc in docs_sorted:
        content = getattr(doc, "page_content", "") or ""
        content_len = len(content)

        if total_len + content_len > max_context_length_chars:
            remaining = max_context_length_chars - total_len
            if remaining > 50:
                context_parts.append(content[:remaining].rsplit("\n", 1)[0] + "\n... [TRUNCADO]")
                docs_used += 1
            break

        context_parts.append(content)
        total_len += content_len
        docs_used += 1

    context = "\n\n".join(context_parts)

    print(f"[RAG] 📊 Documentos recuperados (raw): {len(docs)}")
    print(f"[RAG] 📄 Documentos incluídos no contexto: {docs_used}")
    print(f"[RAG] 📏 Tamanho do contexto final (chars): {len(context)}")

    return {
        "context": context,
        "docs": docs,
        "context_length": len(context),
        "docs_used": docs_used, 
    }


# =====================================================================
# FUNÇÕES DE INDEXAÇÃO (NOVAS)
# =====================================================================

def _get_embeddings():
    """Retorna a função de embeddings configurada"""
    return HuggingFaceEmbeddings(
        model_name=EMBED_MODEL,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True, 'batch_size': 32}
    )


def _split_documents(documents: List) -> List:
    """
    Divide documentos em chunks menores
    
    Args:
        documents: Lista de documentos do LangChain
    
    Returns:
        Lista de chunks
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    chunks = text_splitter.split_documents(documents)
    print(f"[INDEXAÇÃO] 📄 {len(documents)} documentos → {len(chunks)} chunks")
    
    return chunks


def index_local_folder(folder_path: str, chroma_path: str = CHROMA_PATH) -> Dict[str, Any]:
    """
    Indexa todos os PDFs de uma pasta local
    
    Args:
        folder_path: Caminho para a pasta com PDFs
        chroma_path: Caminho para salvar o banco Chroma
    
    Returns:
        Dict com status da indexação
    """
    print("\n" + "="*70)
    print("[INDEXAÇÃO] 📂 Indexando PDFs locais...")
    print("="*70)
    
    folder = Path(folder_path)
    
    if not folder.exists():
        return {"error": f"Pasta não encontrada: {folder_path}"}
    
    # Carregar PDFs
    try:
        loader = DirectoryLoader(
            str(folder),
            glob="**/*.pdf",
            loader_cls=PyPDFLoader,
            show_progress=True
        )
        
        print(f"[INDEXAÇÃO] 🔍 Carregando PDFs de: {folder}")
        documents = loader.load()
        
        if not documents:
            return {"error": "Nenhum PDF encontrado na pasta"}
        
        print(f"[INDEXAÇÃO] ✅ {len(documents)} páginas carregadas")
        
    except Exception as e:
        return {"error": f"Erro ao carregar PDFs: {e}"}
    
    # Dividir em chunks
    try:
        chunks = _split_documents(documents)
    except Exception as e:
        return {"error": f"Erro ao dividir documentos: {e}"}
    
    # Criar banco vetorial
    try:
        print(f"[INDEXAÇÃO] 🧠 Criando embeddings...")
        embeddings = _get_embeddings()
        
        vectordb = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=chroma_path
        )
        
        print(f"[INDEXAÇÃO] 💾 Banco salvo em: {chroma_path}")
        print(f"[INDEXAÇÃO] ✅ {len(chunks)} chunks indexados com sucesso!")
        
        return {
            "indexed_chunks": len(chunks),
            "source_documents": len(documents),
            "chroma_path": chroma_path
        }
        
    except Exception as e:
        return {"error": f"Erro ao criar banco vetorial: {e}"}


def index_online_pdf(url: str, chroma_path: str = CHROMA_PATH) -> Dict[str, Any]:
    """
    Baixa e indexa um PDF de uma URL
    
    Args:
        url: URL do PDF
        chroma_path: Caminho para salvar o banco Chroma
    
    Returns:
        Dict com status da indexação
    """
    print("\n" + "="*70)
    print("[INDEXAÇÃO] 🌐 Baixando PDF online...")
    print("="*70)
    
    # Criar pasta temporária
    temp_dir = Path("Agent_C/temp_pdfs")
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    # Nome do arquivo temporário
    pdf_name = url.split("/")[-1]
    if not pdf_name.endswith(".pdf"):
        pdf_name = "document.pdf"
    
    temp_pdf = temp_dir / pdf_name
    
    # Baixar PDF
    try:
        print(f"[INDEXAÇÃO] ⬇️ Baixando: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        with open(temp_pdf, 'wb') as f:
            f.write(response.content)
        
        print(f"[INDEXAÇÃO] ✅ PDF salvo em: {temp_pdf}")
        
    except Exception as e:
        return {"error": f"Erro ao baixar PDF: {e}"}
    
    # Carregar PDF
    try:
        loader = PyPDFLoader(str(temp_pdf))
        documents = loader.load()
        
        print(f"[INDEXAÇÃO] ✅ {len(documents)} páginas carregadas")
        
    except Exception as e:
        temp_pdf.unlink(missing_ok=True)  # Limpar arquivo temporário
        return {"error": f"Erro ao carregar PDF: {e}"}
    
    # Dividir em chunks
    try:
        chunks = _split_documents(documents)
    except Exception as e:
        temp_pdf.unlink(missing_ok=True)
        return {"error": f"Erro ao dividir documento: {e}"}
    
    # Criar/atualizar banco vetorial
    try:
        print(f"[INDEXAÇÃO] 🧠 Criando embeddings...")
        embeddings = _get_embeddings()
        
        # Verificar se banco já existe
        if Path(chroma_path).exists():
            print(f"[INDEXAÇÃO] 📦 Adicionando ao banco existente...")
            vectordb = Chroma(
                persist_directory=chroma_path,
                embedding_function=embeddings
            )
            vectordb.add_documents(chunks)
        else:
            print(f"[INDEXAÇÃO] 📦 Criando novo banco...")
            vectordb = Chroma.from_documents(
                documents=chunks,
                embedding=embeddings,
                persist_directory=chroma_path
            )
        
        print(f"[INDEXAÇÃO] 💾 Banco salvo em: {chroma_path}")
        print(f"[INDEXAÇÃO] ✅ {len(chunks)} chunks indexados com sucesso!")
        
        # Limpar arquivo temporário
        temp_pdf.unlink(missing_ok=True)
        
        return {
            "indexed_chunks": len(chunks),
            "source_documents": len(documents),
            "chroma_path": chroma_path,
            "source_url": url
        }
        
    except Exception as e:
        temp_pdf.unlink(missing_ok=True)
        return {"error": f"Erro ao criar banco vetorial: {e}"}


def index_web_page(url: str, chroma_path: str = CHROMA_PATH) -> Dict[str, Any]:
    """
    Indexa uma página web HTML
    
    Args:
        url: URL da página web
        chroma_path: Caminho para salvar o banco Chroma
    
    Returns:
        Dict com status da indexação
    """
    print("\n" + "="*70)
    print("[INDEXAÇÃO] 🌐 Indexando página web...")
    print("="*70)
    
    try:
        print(f"[INDEXAÇÃO] 🔍 Carregando: {url}")
        loader = WebBaseLoader(url)
        documents = loader.load()
        
        if not documents:
            return {"error": "Nenhum conteúdo encontrado na página"}
        
        print(f"[INDEXAÇÃO] ✅ Página carregada")
        
    except Exception as e:
        return {"error": f"Erro ao carregar página: {e}"}
    
    # Dividir em chunks
    try:
        chunks = _split_documents(documents)
    except Exception as e:
        return {"error": f"Erro ao dividir documento: {e}"}
    
    # Criar/atualizar banco vetorial
    try:
        print(f"[INDEXAÇÃO] 🧠 Criando embeddings...")
        embeddings = _get_embeddings()
        
        # Verificar se banco já existe
        if Path(chroma_path).exists():
            print(f"[INDEXAÇÃO] 📦 Adicionando ao banco existente...")
            vectordb = Chroma(
                persist_directory=chroma_path,
                embedding_function=embeddings
            )
            vectordb.add_documents(chunks)
        else:
            print(f"[INDEXAÇÃO] 📦 Criando novo banco...")
            vectordb = Chroma.from_documents(
                documents=chunks,
                embedding=embeddings,
                persist_directory=chroma_path
            )
        
        print(f"[INDEXAÇÃO] 💾 Banco salvo em: {chroma_path}")
        print(f"[INDEXAÇÃO] ✅ {len(chunks)} chunks indexados com sucesso!")
        
        return {
            "indexed_chunks": len(chunks),
            "source_url": url,
            "chroma_path": chroma_path
        }
        
    except Exception as e:
        return {"error": f"Erro ao criar banco vetorial: {e}"}


def clear_chroma_db(chroma_path: str = CHROMA_PATH) -> Dict[str, Any]:
    """
    Remove o banco Chroma existente (útil para reindexação)
    
    Args:
        chroma_path: Caminho do banco Chroma
    
    Returns:
        Dict com status
    """
    import shutil
    
    db_path = Path(chroma_path)
    
    if db_path.exists():
        try:
            shutil.rmtree(db_path)
            print(f"[LIMPEZA] ✅ Banco removido: {chroma_path}")
            return {"status": "success", "message": "Banco removido com sucesso"}
        except Exception as e:
            return {"error": f"Erro ao remover banco: {e}"}
    else:
        return {"status": "info", "message": "Banco não existe"}


# =====================================================================
# FUNÇÃO DE TESTE
# =====================================================================
def test_rag_search():
    """Testa a busca RAG (para verificar se banco foi indexado)"""
    print("\n" + "="*70)
    print("[TESTE] 🧪 Testando busca RAG...")
    print("="*70)
    
    if not Path(CHROMA_PATH).exists():
        print("[TESTE] ❌ Banco Chroma não encontrado. Execute setup_rag.py primeiro.")
        return
    
    query = "IRIS stage chronic kidney disease cat creatinine"
    
    try:
        result = rag_search(CHROMA_PATH, query, k=3)
        
        print(f"\n[TESTE] ✅ Busca realizada com sucesso!")
        print(f"[TESTE] 📊 Documentos encontrados: {len(result['docs'])}")
        print(f"[TESTE] 📄 Documentos usados: {result['docs_used']}")
        print(f"[TESTE] 📏 Tamanho do contexto: {result['context_length']} chars")
        
        if result['context']:
            print(f"\n[TESTE] 📝 Preview do contexto (primeiros 300 chars):")
            print("-" * 70)
            print(result['context'][:300] + "...")
        else:
            print(f"\n[TESTE] ⚠️ Nenhum contexto retornado")
            
    except Exception as e:
        print(f"[TESTE] ❌ Erro na busca: {e}")
        import traceback
        traceback.print_exc()


# =====================================================================
# EXECUÇÃO DIRETA (para testes)
# =====================================================================
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            test_rag_search()
        elif sys.argv[1] == "clear":
            clear_chroma_db()
    else:
        print("Uso:")
        print("  python agent_c_db.py test   # Testar busca")
        print("  python agent_c_db.py clear  # Limpar banco")