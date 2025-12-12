"""
Teste Direto de RetrievalMetrics
==================================
Script para testar o módulo rag_metrics_retrieval.py diretamente.
"""

import sys
import os

# Adicionar caminho do Agent_C
agent_c_path = os.path.join(os.path.dirname(__file__), "Agent_C")
sys.path.insert(0, agent_c_path)

try:
    from rag_metrics_retrieval import RetrievalMetrics
    print("✅ RetrievalMetrics importado com sucesso!\n")
except ImportError as e:
    print(f"❌ Erro ao importar RetrievalMetrics: {e}")
    sys.exit(1)

# Executar teste
print("="*70)
print("🔍 TESTE DE MÉTRICAS DE RETRIEVAL")
print("="*70)

metrics = RetrievalMetrics()

# Dados de teste
relevant_docs = {"doc1", "doc3", "doc5", "doc8"}
retrieved_docs = ["doc3", "doc1", "doc7", "doc5", "doc9", "doc2", "doc8", "doc4"]

print("\n📊 Configuração de Teste:")
print(f"  • Documentos Relevantes: {relevant_docs}")
print(f"  • Documentos Recuperados: {retrieved_docs}")

# Calcular métricas
print("\n📈 Calculando métricas...\n")

results = metrics.evaluate_query(
    relevant_docs=relevant_docs,
    retrieved_docs=retrieved_docs,
    k_values=[1, 3, 5, 10]
)

# Exibir resultados
metrics.print_results(results, "Resultados da Avaliação")

# Teste adicional: Dataset
print("\n" + "="*70)
print("📚 TESTE COM DATASET")
print("="*70)

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

dataset_results = metrics.evaluate_dataset(dataset, k_values=[1, 3, 5, 10])
metrics.print_results(dataset_results, "Dataset Completo (Média)")

print("\n✨ Teste concluído com sucesso!")
