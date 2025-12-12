"""
Métricas de Avaliação de Retrieval para Sistema RAG
====================================================
Implementa as principais métricas para avaliar a qualidade da recuperação de documentos:
- Recall@k
- Precision@k
- MRR (Mean Reciprocal Rank)
- NDCG@k (Normalized Discounted Cumulative Gain)

Autor: Sistema Multi-Agente IRIS
Data: Dezembro 2025
"""

import numpy as np
from typing import List, Dict, Set, Any, Optional
import math


class RetrievalMetrics:
    """
    Classe para calcular métricas de retrieval.
    
    Uso:
        metrics = RetrievalMetrics()
        
        # Documentos relevantes conhecidos (ground truth)
        relevant_docs = {"doc1", "doc3", "doc5"}
        
        # Documentos recuperados pelo sistema (ordenados por relevância)
        retrieved_docs = ["doc3", "doc1", "doc7", "doc5", "doc9"]
        
        # Calcular métricas
        recall = metrics.recall_at_k(relevant_docs, retrieved_docs, k=5)
        precision = metrics.precision_at_k(relevant_docs, retrieved_docs, k=5)
        mrr = metrics.mrr(relevant_docs, retrieved_docs)
        ndcg = metrics.ndcg_at_k(relevant_docs, retrieved_docs, k=5)
    """
    
    def __init__(self):
        pass
    
    def recall_at_k(
        self, 
        relevant_docs: Set[str], 
        retrieved_docs: List[str], 
        k: int
    ) -> float:
        """
        Calcula Recall@k: proporção de documentos relevantes recuperados nos top-k.
        
        Recall@k = (Número de docs relevantes em top-k) / (Total de docs relevantes)
        
        Args:
            relevant_docs: Conjunto de IDs de documentos relevantes (ground truth)
            retrieved_docs: Lista ordenada de IDs de documentos recuperados
            k: Número de documentos top-k a considerar
            
        Returns:
            float: Valor entre 0 e 1
        """
        if not relevant_docs:
            return 0.0
        
        top_k = set(retrieved_docs[:k])
        relevant_retrieved = top_k.intersection(relevant_docs)
        
        return len(relevant_retrieved) / len(relevant_docs)
    
    def precision_at_k(
        self, 
        relevant_docs: Set[str], 
        retrieved_docs: List[str], 
        k: int
    ) -> float:
        """
        Calcula Precision@k: proporção de documentos relevantes nos top-k recuperados.
        
        Precision@k = (Número de docs relevantes em top-k) / k
        
        Args:
            relevant_docs: Conjunto de IDs de documentos relevantes (ground truth)
            retrieved_docs: Lista ordenada de IDs de documentos recuperados
            k: Número de documentos top-k a considerar
            
        Returns:
            float: Valor entre 0 e 1
        """
        if k == 0:
            return 0.0
        
        top_k = set(retrieved_docs[:k])
        relevant_retrieved = top_k.intersection(relevant_docs)
        
        return len(relevant_retrieved) / k
    
    def mrr(
        self, 
        relevant_docs: Set[str], 
        retrieved_docs: List[str]
    ) -> float:
        """
        Calcula MRR (Mean Reciprocal Rank): inverso da posição do primeiro doc relevante.
        
        MRR = 1 / (posição do primeiro documento relevante)
        
        Útil para avaliar se o sistema coloca documentos relevantes no topo.
        
        Args:
            relevant_docs: Conjunto de IDs de documentos relevantes (ground truth)
            retrieved_docs: Lista ordenada de IDs de documentos recuperados
            
        Returns:
            float: Valor entre 0 e 1 (1 = primeiro doc é relevante)
        """
        for idx, doc_id in enumerate(retrieved_docs, start=1):
            if doc_id in relevant_docs:
                return 1.0 / idx
        
        return 0.0
    
    def ndcg_at_k(
        self, 
        relevant_docs: Set[str], 
        retrieved_docs: List[str], 
        k: int,
        relevance_scores: Optional[Dict[str, float]] = None
    ) -> float:
        """
        Calcula NDCG@k (Normalized Discounted Cumulative Gain).
        
        NDCG considera tanto a relevância quanto a posição dos documentos.
        Documentos relevantes no topo têm mais peso.
        
        Args:
            relevant_docs: Conjunto de IDs de documentos relevantes (ground truth)
            retrieved_docs: Lista ordenada de IDs de documentos recuperados
            k: Número de documentos top-k a considerar
            relevance_scores: Dicionário opcional com scores de relevância por documento
                            Se None, usa relevância binária (1 ou 0)
            
        Returns:
            float: Valor entre 0 e 1 (1 = ordenação perfeita)
        """
        if k == 0:
            return 0.0
        
        # DCG (Discounted Cumulative Gain) do sistema
        dcg = 0.0
        for idx, doc_id in enumerate(retrieved_docs[:k], start=1):
            if doc_id in relevant_docs:
                # Relevância binária ou score fornecido
                relevance = relevance_scores.get(doc_id, 1.0) if relevance_scores else 1.0
                # DCG formula: rel / log2(i + 1)
                dcg += relevance / math.log2(idx + 1)
        
        # IDCG (Ideal DCG) - melhor ordenação possível
        ideal_relevances = []
        for doc_id in relevant_docs:
            relevance = relevance_scores.get(doc_id, 1.0) if relevance_scores else 1.0
            ideal_relevances.append(relevance)
        
        # Ordenar relevâncias em ordem decrescente
        ideal_relevances.sort(reverse=True)
        
        idcg = 0.0
        for idx, relevance in enumerate(ideal_relevances[:k], start=1):
            idcg += relevance / math.log2(idx + 1)
        
        # Normalizar
        if idcg == 0:
            return 0.0
        
        return dcg / idcg
    
    def evaluate_query(
        self,
        relevant_docs: Set[str],
        retrieved_docs: List[str],
        k_values: List[int] = [1, 3, 5, 10],
        relevance_scores: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Avalia uma única query com todas as métricas.
        
        Args:
            relevant_docs: Conjunto de IDs de documentos relevantes
            retrieved_docs: Lista ordenada de IDs de documentos recuperados
            k_values: Lista de valores k para calcular métricas
            relevance_scores: Scores de relevância opcionais
            
        Returns:
            Dict com todas as métricas calculadas
        """
        results = {
            "mrr": self.mrr(relevant_docs, retrieved_docs),
            "recall": {},
            "precision": {},
            "ndcg": {}
        }
        
        for k in k_values:
            results["recall"][f"@{k}"] = self.recall_at_k(relevant_docs, retrieved_docs, k)
            results["precision"][f"@{k}"] = self.precision_at_k(relevant_docs, retrieved_docs, k)
            results["ndcg"][f"@{k}"] = self.ndcg_at_k(relevant_docs, retrieved_docs, k, relevance_scores)
        
        return results
    
    def evaluate_dataset(
        self,
        dataset: List[Dict[str, Any]],
        k_values: List[int] = [1, 3, 5, 10]
    ) -> Dict[str, Any]:
        """
        Avalia um dataset completo de queries.
        
        Args:
            dataset: Lista de dicionários, cada um contendo:
                - "query": str - a pergunta
                - "relevant_docs": Set[str] - docs relevantes
                - "retrieved_docs": List[str] - docs recuperados
                - "relevance_scores": Dict[str, float] (opcional)
                
            k_values: Lista de valores k para calcular métricas
            
        Returns:
            Dict com médias de todas as métricas
        """
        all_results = []
        
        for item in dataset:
            relevant_docs = item["relevant_docs"]
            retrieved_docs = item["retrieved_docs"]
            relevance_scores = item.get("relevance_scores", None)
            
            result = self.evaluate_query(
                relevant_docs, 
                retrieved_docs, 
                k_values, 
                relevance_scores
            )
            all_results.append(result)
        
        # Calcular médias
        avg_results = {
            "mrr": np.mean([r["mrr"] for r in all_results]),
            "recall": {},
            "precision": {},
            "ndcg": {},
            "num_queries": len(dataset)
        }
        
        for k in k_values:
            k_str = f"@{k}"
            avg_results["recall"][k_str] = np.mean([r["recall"][k_str] for r in all_results])
            avg_results["precision"][k_str] = np.mean([r["precision"][k_str] for r in all_results])
            avg_results["ndcg"][k_str] = np.mean([r["ndcg"][k_str] for r in all_results])
        
        return avg_results
    
    def print_results(self, results: Dict[str, Any], title: str = "Resultados da Avaliação"):
        """
        Imprime os resultados de forma formatada.
        
        Args:
            results: Dicionário com resultados da avaliação
            title: Título do relatório
        """
        print("\n" + "=" * 70)
        print(f"📊 {title}")
        print("=" * 70)
        
        if "num_queries" in results:
            print(f"\n📝 Número de queries avaliadas: {results['num_queries']}")
        
        print(f"\n🎯 MRR (Mean Reciprocal Rank): {results['mrr']:.4f}")
        
        print("\n📈 Recall@k:")
        for k, value in results["recall"].items():
            print(f"  • Recall{k}: {value:.4f}")
        
        print("\n🎲 Precision@k:")
        for k, value in results["precision"].items():
            print(f"  • Precision{k}: {value:.4f}")
        
        print("\n⭐ NDCG@k:")
        for k, value in results["ndcg"].items():
            print(f"  • NDCG{k}: {value:.4f}")
        
        print("\n" + "=" * 70)


if __name__ == "__main__":
    # Exemplo de uso
    metrics = RetrievalMetrics()
    
    relevant_docs = {"doc1", "doc3", "doc5", "doc8"}
    retrieved_docs = ["doc3", "doc1", "doc7", "doc5", "doc9", "doc2", "doc8", "doc4"]
    
    results = metrics.evaluate_query(
        relevant_docs=relevant_docs,
        retrieved_docs=retrieved_docs,
        k_values=[1, 3, 5, 10]
    )
    
    metrics.print_results(results, "Query Única")
