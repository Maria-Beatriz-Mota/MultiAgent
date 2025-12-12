"""
Teste Rápido de Métricas - Multi-Agent IRIS System
====================================================
Script para executar testes rápidos do sistema de métricas.

Uso:
    python test_metrics_quick.py

Autor: Sistema Multi-Agente IRIS
Data: Dezembro 2025
"""

import sys
import os
import json
from datetime import datetime

# Adicionar diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Tenta importar com cuidado para evitar problemas de dependências
    import importlib.util
    
    # Importar RetrievalMetrics diretamente
    spec_retrieval = importlib.util.spec_from_file_location(
        "rag_metrics_retrieval",
        os.path.join(os.path.dirname(__file__), "Agent_C", "rag_metrics_retrieval.py")
    )
    rag_metrics_retrieval = importlib.util.module_from_spec(spec_retrieval)
    spec_retrieval.loader.exec_module(rag_metrics_retrieval)
    RetrievalMetrics = rag_metrics_retrieval.RetrievalMetrics
    
    # Importar RAGEvaluator
    spec_evaluator = importlib.util.spec_from_file_location(
        "rag_evaluator",
        os.path.join(os.path.dirname(__file__), "Agent_C", "rag_evaluator.py")
    )
    rag_evaluator = importlib.util.module_from_spec(spec_evaluator)
    spec_evaluator.loader.exec_module(rag_evaluator)
    RAGEvaluator = rag_evaluator.RAGEvaluator
    
except Exception as e:
    print(f"⚠️  Erro ao carregar módulos: {e}")
    print("Continuando com modo limitado...")
    RetrievalMetrics = None
    RAGEvaluator = None


def test_retrieval_metrics():
    """Testa métricas de retrieval com dados exemplo."""
    print("\n" + "="*70)
    print("🔍 TESTE 1: Métricas de Retrieval")
    print("="*70)
    
    if not RetrievalMetrics:
        print("❌ RetrievalMetrics não disponível")
        return False
    
    metrics = RetrievalMetrics()
    
    # Dados de teste
    relevant_docs = {"doc1", "doc3", "doc5", "doc8"}
    retrieved_docs = ["doc3", "doc1", "doc7", "doc5", "doc9", "doc2", "doc8", "doc4"]
    
    results = metrics.evaluate_query(
        relevant_docs=relevant_docs,
        retrieved_docs=retrieved_docs,
        k_values=[1, 3, 5, 10]
    )
    
    metrics.print_results(results, "Query Única - Retrieval Metrics")
    
    return True


def test_dataset_evaluation():
    """Testa avaliação de dataset completo."""
    print("\n" + "="*70)
    print("📊 TESTE 2: Avaliação de Dataset")
    print("="*70)
    
    if not RetrievalMetrics:
        print("❌ RetrievalMetrics não disponível")
        return False
    
    metrics = RetrievalMetrics()
    
    # Dataset de teste com 3 queries
    dataset = [
        {
            "query": "DRC em gatos",
            "relevant_docs": {"doc1", "doc3", "doc5"},
            "retrieved_docs": ["doc3", "doc1", "doc7", "doc5"]
        },
        {
            "query": "IRIS staging",
            "relevant_docs": {"doc2", "doc4", "doc6"},
            "retrieved_docs": ["doc4", "doc2", "doc8", "doc6", "doc9"]
        },
        {
            "query": "Creatinina e SDMA",
            "relevant_docs": {"doc5", "doc7"},
            "retrieved_docs": ["doc7", "doc5", "doc1"]
        }
    ]
    
    results = metrics.evaluate_dataset(dataset, k_values=[1, 3, 5, 10])
    
    metrics.print_results(results, "Dataset Completo - Média de Métricas")
    
    return True


def test_rag_evaluator():
    """Testa RAGEvaluator com dados reais do CSV."""
    print("\n" + "="*70)
    print("⭐ TESTE 3: RAG Evaluator Completo")
    print("="*70)
    
    if not RAGEvaluator:
        print("❌ RAGEvaluator não disponível")
        return False
    
    evaluator = RAGEvaluator()
    
    try:
        # Carregar dados do CSV
        print("\n📂 Carregando dados de validação...")
        evaluator.carregar_validacoes()
        
        # Gerar relatório completo
        print("📈 Gerando relatório completo...")
        relatorio = evaluator.gerar_relatorio_completo()
        
        print("\n✅ Relatório gerado com sucesso!")
        print(f"📊 Total de validações: {len(evaluator.validacoes)}")
        
        return True
    
    except FileNotFoundError:
        print("⚠️  CSV de validações não encontrado")
        return False
    
    except Exception as e:
        print(f"❌ Erro ao testar RAGEvaluator: {str(e)}")
        return False


def test_metrics_summary():
    """Imprime resumo dos sistemas de métricas disponíveis."""
    print("\n" + "="*70)
    print("📋 Sistemas de Métricas Disponíveis")
    print("="*70)
    
    print("""
    1. RetrievalMetrics (rag_metrics_retrieval.py)
       ├── recall_at_k: Proporção de docs relevantes recuperados
       ├── precision_at_k: Proporção de top-k que são relevantes
       ├── mrr: Posição do primeiro doc relevante
       └── ndcg_at_k: Considerando relevância e posição
    
    2. GenerationMetrics (rag_metrics_generation.py)
       ├── answer_accuracy: Acurácia usando LLM-as-a-judge
       ├── faithfulness: Fidelidade aos documentos
       └── groundedness: Proporção fundamentada
    
    3. RAGEvaluator (rag_evaluator.py)
       ├── Acurácia Geral
       ├── Precisão por Estágio IRIS
       ├── Concordância entre Agentes
       ├── Eficácia do RAG
       ├── Distribuição por Caso
       └── Distribuição de Confiança
    """)
    
    return True


def main():
    """Executa todos os testes."""
    print("\n" + "="*70)
    print("🚀 TESTE RÁPIDO - SISTEMA DE MÉTRICAS")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    tests = [
        ("Retrieval Metrics", test_retrieval_metrics),
        ("Dataset Evaluation", test_dataset_evaluation),
        ("RAG Evaluator", test_rag_evaluator),
        ("Metrics Summary", test_metrics_summary)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            print(f"\n▶️  Executando: {test_name}...")
            success = test_func()
            results.append({
                "test": test_name,
                "status": "✅ PASSOU" if success else "❌ FALHOU"
            })
        except Exception as e:
            print(f"\n❌ Erro em {test_name}: {str(e)}")
            results.append({
                "test": test_name,
                "status": f"❌ ERRO: {str(e)}"
            })
    
    # Resumo final
    print("\n" + "="*70)
    print("📊 RESUMO DOS TESTES")
    print("="*70)
    
    for result in results:
        print(f"{result['test']:.<40} {result['status']}")
    
    print("\n" + "="*70)
    print("✨ Testes Concluídos!")
    print("="*70)


if __name__ == "__main__":
    main()
