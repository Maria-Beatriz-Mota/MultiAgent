"""
Sistema Completo de Avaliação RAG
==================================
Integra todas as métricas (retrieval + validação) para avaliação end-to-end
de um sistema RAG.

Autor: Sistema Multi-Agente IRIS
Data: Dezembro 2025
"""

import json
import csv
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd
import numpy as np

from rag_metrics_retrieval import RetrievalMetrics


class RAGEvaluator:
    """
    Avaliador completo de sistema RAG.
    
    Combina métricas de retrieval e validação para avaliação end-to-end.
    """
    
    def __init__(
        self,
        k_values: List[int] = [1, 3, 5, 10],
        csv_path: str = "Agent_C/validations_database.csv"
    ):
        """
        Inicializa o avaliador.
        
        Args:
            k_values: Valores de k para métricas de retrieval
            csv_path: Caminho para o CSV de validações
        """
        self.retrieval_metrics = RetrievalMetrics()
        self.k_values = k_values
        self.csv_path = Path(csv_path)
    
    def carregar_validacoes(self) -> pd.DataFrame:
        """Carrega validações do CSV"""
        if not self.csv_path.exists():
            print(f"Arquivo não encontrado: {self.csv_path}")
            return pd.DataFrame()
        
        df = pd.read_csv(self.csv_path)
        print(f"✓ {len(df)} validações carregadas")
        return df
    
    def gerar_relatorio_completo(self) -> Dict[str, Any]:
        """Gera relatório completo de métricas"""
        df = self.carregar_validacoes()
        
        if df.empty:
            return {}
        
        print("\n" + "=" * 80)
        print("RELATÓRIO DE MÉTRICAS - SISTEMA MULTI-AGENTE IRIS")
        print("=" * 80)
        
        # Período de avaliação
        print(f"\nPeríodo: {df['timestamp'].min()} até {df['timestamp'].max()}")
        print(f"Total de validações: {len(df)}")
        
        # 1. ACURÁCIA GERAL
        print("\n" + "=" * 80)
        print("1. ACURÁCIA GERAL")
        print("=" * 80)
        
        confirmadas = len(df[df['validacao'] == 'Confirmada'])
        reprovadas = len(df[df['validacao'] == 'Reprovada'])
        inconclusivas = len(df[df['validacao'] == 'Inconclusiva'])
        
        accuracy = confirmadas / len(df) if len(df) > 0 else 0
        
        print(f"\nAccuracy: {accuracy:.2%}")
        print(f"  ✓ Confirmadas: {confirmadas}")
        print(f"  ✗ Reprovadas: {reprovadas}")
        print(f"  ⚠ Inconclusivas: {inconclusivas}")
        
        # 2. PRECISÃO POR ESTÁGIO
        print("\n" + "=" * 80)
        print("2. PRECISÃO, RECALL E F1-SCORE POR ESTÁGIO IRIS")
        print("=" * 80)
        
        metricas_por_estagio = {}
        for estagio in df['estagio_final'].unique():
            if pd.isna(estagio):
                continue
            
            estagio_df = df[df['estagio_final'] == estagio]
            total = len(estagio_df)
            corretos = len(estagio_df[estagio_df['validacao'] == 'Confirmada'])
            
            precision = corretos / total if total > 0 else 0
            recall = corretos / total if total > 0 else 0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            
            metricas_por_estagio[estagio] = {
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'total': total,
                'corretos': corretos
            }
            
            print(f"\n{estagio}:")
            print(f"  Precision: {precision:.2%} ({corretos}/{total})")
            print(f"  Recall: {recall:.2%}")
            print(f"  F1-Score: {f1:.2%}")
        
        # 3. CONCORDÂNCIA ENTRE AGENTES
        print("\n" + "=" * 80)
        print("3. CONCORDÂNCIA ENTRE AGENTE B E AGENTE C")
        print("=" * 80)
        
        concordantes = len(df[df['estagio_b'] == df['estagio_final']])
        discordantes = len(df[df['estagio_b'] != df['estagio_final']])
        
        taxa_concordancia = concordantes / len(df) if len(df) > 0 else 0
        taxa_discordancia = discordantes / len(df) if len(df) > 0 else 0
        
        print(f"\nTaxa de Concordância: {taxa_concordancia:.2%} ({concordantes}/{len(df)})")
        print(f"Taxa de Discordância: {taxa_discordancia:.2%} ({discordantes}/{len(df)})")
        
        # 4. EFICÁCIA DO RAG
        print("\n" + "=" * 80)
        print("4. EFICÁCIA DO RAG (RETRIEVAL-AUGMENTED GENERATION)")
        print("=" * 80)
        
        casos_com_rag = len(df[df['num_docs_rag'] > 0])
        casos_sem_rag = len(df[df['num_docs_rag'] == 0])
        cobertura_rag = casos_com_rag / len(df) if len(df) > 0 else 0
        
        # Documentos usados onde disponível
        docs_utilizados = df[df['num_docs_rag'] > 0]['num_docs_rag']
        media_docs = docs_utilizados.mean() if len(docs_utilizados) > 0 else 0
        
        print(f"\nCobertura RAG: {cobertura_rag:.2%} ({casos_com_rag}/{len(df)})")
        print(f"Média de Documentos: {media_docs:.1f} docs/consulta")
        
        # 5. DISTRIBUIÇÃO POR CASO
        print("\n" + "=" * 80)
        print("5. DISTRIBUIÇÃO POR TIPO DE CASO")
        print("=" * 80)
        
        dist_casos = df['caso'].value_counts().sort_index()
        for caso, count in dist_casos.items():
            porcentagem = (count / len(df)) * 100
            print(f"  Caso {caso}: {count} ({porcentagem:.1f}%)")
        
        # 6. CONFIANÇA
        print("\n" + "=" * 80)
        print("6. DISTRIBUIÇÃO DE CONFIANÇA")
        print("=" * 80)
        
        if 'confianca' in df.columns:
            dist_confianca = df['confianca'].value_counts()
            for conf, count in dist_confianca.items():
                porcentagem = (count / len(df)) * 100
                print(f"  {conf}: {count} ({porcentagem:.1f}%)")
        
        print("\n" + "=" * 80)
        print("✓ Relatório completo gerado")
        print("=" * 80)
        
        return {
            'accuracy': accuracy,
            'metricas_por_estagio': metricas_por_estagio,
            'concordancia': taxa_concordancia,
            'discordancia': taxa_discordancia,
            'cobertura_rag': cobertura_rag,
            'media_docs': media_docs,
            'num_validacoes': len(df)
        }
    
    def salvar_relatorio(self, output_path: str = "relatorio_metricas.json"):
        """Salva relatório em JSON"""
        resultado = self.gerar_relatorio_completo()
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(resultado, f, indent=2, ensure_ascii=False)
        
        print(f"\nRelatório salvo em: {output_path}")


if __name__ == "__main__":
    print("\nAvaliador RAG do Sistema Multi-Agente IRIS\n")
    
    evaluator = RAGEvaluator()
    resultado = evaluator.gerar_relatorio_completo()
    evaluator.salvar_relatorio()
