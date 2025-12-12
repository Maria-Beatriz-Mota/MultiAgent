"""
Módulo de Métricas de Avaliação do Sistema Multi-Agente IRIS
Calcula Accuracy, Precision, Recall, F1-Score a partir do CSV de validações
"""

import csv
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict

CSV_PATH = Path("Agent_C/validations_database.csv")

def carregar_validacoes() -> pd.DataFrame:
    """Carrega o CSV de validações"""
    if not CSV_PATH.exists():
        print("❌ Arquivo de validações não encontrado")
        return pd.DataFrame()
    
    df = pd.read_csv(CSV_PATH)
    print(f"✅ {len(df)} validações carregadas")
    return df

def calcular_accuracy(df: pd.DataFrame) -> float:
    """
    Accuracy: Proporção de classificações corretas
    (Validações confirmadas) / (Total de validações)
    """
    if len(df) == 0:
        return 0.0
    
    confirmadas = len(df[df['validacao'] == 'Confirmada'])
    total = len(df)
    
    accuracy = confirmadas / total
    return accuracy

def calcular_precision_recall_por_estagio(df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
    """
    Precision e Recall por estágio IRIS
    
    Precision: Dos que o sistema classificou como IRIS X, quantos estavam corretos?
    Recall: Dos casos reais de IRIS X, quantos o sistema identificou?
    
    OBS: Estamos considerando 'estagio_final' como a classificação do sistema
         e 'validacao == Confirmada' como ground truth correto
    """
    if len(df) == 0:
        return {}
    
    metricas = {}
    estagios = ['IRIS1', 'IRIS2', 'IRIS3', 'IRIS4']
    
    for estagio in estagios:
        # Casos onde o sistema classificou como este estágio
        classificados = df[df['estagio_final'] == estagio]
        
        # Desses, quantos foram confirmados (corretos)?
        corretos = classificados[classificados['validacao'] == 'Confirmada']
        
        # Precision: corretos / total classificados como este estágio
        precision = len(corretos) / len(classificados) if len(classificados) > 0 else 0.0
        
        # Recall: Para calcular, precisamos saber quantos casos reais existem de cada estágio
        # Consideramos que casos confirmados representam o ground truth
        casos_reais = df[(df['estagio_final'] == estagio) & (df['validacao'] == 'Confirmada')]
        
        # Dos casos reais, quantos foram corretamente identificados?
        recall = len(corretos) / len(casos_reais) if len(casos_reais) > 0 else 0.0
        
        # F1-Score: média harmônica de precision e recall
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        metricas[estagio] = {
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'total_classificados': len(classificados),
            'corretos': len(corretos)
        }
    
    return metricas

def calcular_concordancia_agentes(df: pd.DataFrame) -> Dict[str, float]:
    """
    Calcula concordância entre Agente B (ontologia) e Agente C (validador)
    """
    if len(df) == 0:
        return {}
    
    # Casos onde B classificou e foi validado por C
    concordancia_total = len(df[df['validacao'] == 'Confirmada'])
    discordancia_total = len(df[df['validacao'] == 'Reprovada'])
    inconclusiva = len(df[df['validacao'] == 'Inconclusiva'])
    
    total = len(df)
    
    return {
        'concordancia_rate': concordancia_total / total if total > 0 else 0.0,
        'discordancia_rate': discordancia_total / total if total > 0 else 0.0,
        'inconclusiva_rate': inconclusiva / total if total > 0 else 0.0,
        'total_casos': total,
        'concordantes': concordancia_total,
        'discordantes': discordancia_total,
        'inconclusivos': inconclusiva
    }

def calcular_cobertura_rag(df: pd.DataFrame) -> Dict[str, float]:
    """
    Calcula eficácia do RAG em fornecer documentos relevantes
    """
    if len(df) == 0:
        return {}
    
    # Casos onde RAG retornou documentos
    com_rag = df[df['num_docs_rag'] > 0]
    sem_rag = df[df['num_docs_rag'] == 0]
    
    # Taxa de cobertura
    cobertura = len(com_rag) / len(df) if len(df) > 0 else 0.0
    
    # Média de documentos retornados
    media_docs = df['num_docs_rag'].mean() if len(df) > 0 else 0.0
    
    return {
        'cobertura_rag': cobertura,
        'casos_com_rag': len(com_rag),
        'casos_sem_rag': len(sem_rag),
        'media_documentos': media_docs
    }

def gerar_relatorio_completo():
    """
    Gera relatório completo de métricas do sistema
    """
    print("="*80)
    print("📊 RELATÓRIO DE MÉTRICAS - SISTEMA MULTI-AGENTE IRIS")
    print("="*80)
    
    df = carregar_validacoes()
    
    if len(df) == 0:
        print("\n⚠️  Nenhuma validação encontrada. Execute diagnósticos primeiro.")
        return
    
    print(f"\n📅 Período: {df['timestamp'].min()} até {df['timestamp'].max()}")
    print(f"📋 Total de validações: {len(df)}")
    
    # 1. ACCURACY GERAL
    print("\n" + "="*80)
    print("1️⃣  ACURÁCIA GERAL")
    print("="*80)
    accuracy = calcular_accuracy(df)
    print(f"Accuracy: {accuracy:.2%}")
    print(f"  ✅ Validações confirmadas: {len(df[df['validacao'] == 'Confirmada'])}")
    print(f"  ❌ Validações reprovadas: {len(df[df['validacao'] == 'Reprovada'])}")
    print(f"  ⚠️  Validações inconclusivas: {len(df[df['validacao'] == 'Inconclusiva'])}")
    
    # 2. PRECISION, RECALL, F1 POR ESTÁGIO
    print("\n" + "="*80)
    print("2️⃣  PRECISION, RECALL E F1-SCORE POR ESTÁGIO IRIS")
    print("="*80)
    metricas_estagio = calcular_precision_recall_por_estagio(df)
    
    for estagio, metricas in metricas_estagio.items():
        if metricas['total_classificados'] > 0:
            print(f"\n🔹 {estagio}:")
            print(f"   Precision: {metricas['precision']:.2%} ({metricas['corretos']}/{metricas['total_classificados']} corretos)")
            print(f"   Recall:    {metricas['recall']:.2%}")
            print(f"   F1-Score:  {metricas['f1_score']:.2%}")
    
    # 3. CONCORDÂNCIA ENTRE AGENTES
    print("\n" + "="*80)
    print("3️⃣  CONCORDÂNCIA ENTRE AGENTE B (ONTOLOGIA) E AGENTE C (VALIDADOR)")
    print("="*80)
    concordancia = calcular_concordancia_agentes(df)
    print(f"Taxa de Concordância: {concordancia['concordancia_rate']:.2%} ({concordancia['concordantes']}/{concordancia['total_casos']})")
    print(f"Taxa de Discordância: {concordancia['discordancia_rate']:.2%} ({concordancia['discordantes']}/{concordancia['total_casos']})")
    print(f"Taxa Inconclusiva:    {concordancia['inconclusiva_rate']:.2%} ({concordancia['inconclusivos']}/{concordancia['total_casos']})")
    
    # 4. EFICÁCIA DO RAG
    print("\n" + "="*80)
    print("4️⃣  EFICÁCIA DO RAG (RETRIEVAL-AUGMENTED GENERATION)")
    print("="*80)
    cobertura = calcular_cobertura_rag(df)
    print(f"Cobertura RAG:         {cobertura['cobertura_rag']:.2%} ({cobertura['casos_com_rag']}/{cobertura['casos_com_rag'] + cobertura['casos_sem_rag']})")
    print(f"Média de Documentos:   {cobertura['media_documentos']:.1f} docs/consulta")
    
    # 5. DISTRIBUIÇÃO POR CASO
    print("\n" + "="*80)
    print("5️⃣  DISTRIBUIÇÃO POR TIPO DE CASO")
    print("="*80)
    dist_casos = df['caso'].value_counts().sort_index()
    for caso, count in dist_casos.items():
        porcentagem = (count / len(df)) * 100
        print(f"   Caso {caso}: {count} ({porcentagem:.1f}%)")
    
    print("\n" + "="*80)
    print("✅ Relatório completo gerado")
    print("="*80)
    
    return {
        'accuracy': accuracy,
        'metricas_por_estagio': metricas_estagio,
        'concordancia': concordancia,
        'cobertura_rag': cobertura
    }

if __name__ == "__main__":
    gerar_relatorio_completo()
