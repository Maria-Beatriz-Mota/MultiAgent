"""
Utilitários para análise do banco de dados CSV de validações
"""

import csv
import pandas as pd
from pathlib import Path
from typing import Dict, List

CSV_PATH = Path("Agent_C/validations_database.csv")


def ler_validacoes() -> pd.DataFrame:
    """
    Lê o banco de dados CSV de validações
    
    Returns:
        DataFrame com todas as validações
    """
    if not CSV_PATH.exists():
        print(f"⚠️ Arquivo CSV não encontrado: {CSV_PATH}")
        return pd.DataFrame()
    
    df = pd.read_csv(CSV_PATH)
    print(f"✅ {len(df)} validações carregadas")
    return df


def estatisticas_validacoes():
    """
    Exibe estatísticas do banco de dados
    """
    df = ler_validacoes()
    
    if df.empty:
        print("Nenhuma validação registrada ainda.")
        return
    
    print("\n" + "="*70)
    print("📊 ESTATÍSTICAS DO BANCO DE DADOS DE VALIDAÇÕES")
    print("="*70)
    
    print(f"\n📝 Total de validações: {len(df)}")
    
    print(f"\n🎯 Distribuição por estágio IRIS:")
    print(df['estagio_final'].value_counts())
    
    print(f"\n✅ Distribuição por validação:")
    print(df['validacao'].value_counts())
    
    print(f"\n📊 Distribuição por caso:")
    print(df['caso'].value_counts())
    
    print(f"\n🔬 Regras aplicadas:")
    print(df['regra_aplicada'].value_counts())
    
    print(f"\n🎯 Confiança:")
    print(df['confianca'].value_counts())
    
    if 'creatinina' in df.columns:
        print(f"\n📈 Estatísticas de Creatinina:")
        print(f"  Média: {df['creatinina'].mean():.2f} mg/dL")
        print(f"  Mínimo: {df['creatinina'].min():.2f} mg/dL")
        print(f"  Máximo: {df['creatinina'].max():.2f} mg/dL")
    
    if 'sdma' in df.columns:
        print(f"\n📈 Estatísticas de SDMA:")
        print(f"  Média: {df['sdma'].mean():.2f} µg/dL")
        print(f"  Mínimo: {df['sdma'].min():.2f} µg/dL")
        print(f"  Máximo: {df['sdma'].max():.2f} µg/dL")
    
    print("\n" + "="*70)


def buscar_casos_similares(creatinina: float, sdma: float, tolerancia: float = 0.3) -> pd.DataFrame:
    """
    Busca casos similares no histórico
    
    Args:
        creatinina: Valor de creatinina
        sdma: Valor de SDMA
        tolerancia: Tolerância para considerar similar (30% por padrão)
    
    Returns:
        DataFrame com casos similares
    """
    df = ler_validacoes()
    
    if df.empty:
        return pd.DataFrame()
    
    # Filtrar casos similares
    similares = df[
        (df['creatinina'] >= creatinina * (1 - tolerancia)) &
        (df['creatinina'] <= creatinina * (1 + tolerancia)) &
        (df['sdma'] >= sdma * (1 - tolerancia)) &
        (df['sdma'] <= sdma * (1 + tolerancia))
    ]
    
    print(f"🔍 {len(similares)} casos similares encontrados")
    return similares


def limpar_banco_dados():
    """
    Remove o arquivo CSV (limpa banco de dados)
    """
    if CSV_PATH.exists():
        CSV_PATH.unlink()
        print("✅ Banco de dados CSV removido")
    else:
        print("⚠️ Banco de dados não existe")


def exportar_para_excel(output_path: str = "validations_export.xlsx"):
    """
    Exporta o CSV para Excel
    
    Args:
        output_path: Caminho do arquivo Excel de saída
    """
    df = ler_validacoes()
    
    if df.empty:
        print("Nenhum dado para exportar")
        return
    
    df.to_excel(output_path, index=False)
    print(f"✅ Dados exportados para: {output_path}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        comando = sys.argv[1]
        
        if comando == "stats":
            estatisticas_validacoes()
        elif comando == "export":
            exportar_para_excel()
        elif comando == "clear":
            resposta = input("⚠️ Tem certeza que deseja limpar o banco de dados? (s/n): ")
            if resposta.lower() == 's':
                limpar_banco_dados()
        elif comando == "buscar":
            if len(sys.argv) >= 4:
                creat = float(sys.argv[2])
                sdma = float(sys.argv[3])
                casos = buscar_casos_similares(creat, sdma)
                print(casos)
            else:
                print("Uso: python csv_utils.py buscar <creatinina> <sdma>")
        else:
            print("Comando desconhecido")
    else:
        print("Comandos disponíveis:")
        print("  stats        - Exibir estatísticas")
        print("  export       - Exportar para Excel")
        print("  clear        - Limpar banco de dados")
        print("  buscar       - Buscar casos similares")
