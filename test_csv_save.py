"""
Script de teste para salvamento automático em CSV
"""

from run_lg import run_pipeline

print("\n" + "="*70)
print("🧪 TESTE DE SALVAMENTO AUTOMÁTICO EM CSV")
print("="*70)

# Teste 1: Caso com validação confirmada
print("\n📝 TESTE 1: Validação confirmada (será salva)")
print("-"*70)

resultado1 = run_pipeline(
    formulario={
        "creatinina": 2.4,
        "sdma": 23.0,
        "idade": 8
    },
    texto_livre="qual o tratamento recomendado?"
)

print(resultado1)

# Teste 2: Outro caso válido
print("\n\n📝 TESTE 2: Segunda validação (será salva)")
print("-"*70)

resultado2 = run_pipeline(
    formulario={
        "creatinina": 3.2,
        "sdma": 28.0,
        "idade": 10
    },
    texto_livre="qual o prognóstico?"
)

print(resultado2)

# Verificar arquivo CSV
print("\n" + "="*70)
print("📊 VERIFICANDO BANCO DE DADOS CSV")
print("="*70)

import os
from pathlib import Path

csv_path = Path("Agent_C/validations_database.csv")

if csv_path.exists():
    print(f"✅ Arquivo CSV criado: {csv_path}")
    print(f"📏 Tamanho: {csv_path.stat().st_size} bytes")
    
    # Ler e mostrar
    with open(csv_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        print(f"📝 Total de linhas: {len(lines)}")
        print(f"\n📄 Conteúdo:")
        for line in lines:
            print(line.strip())
else:
    print("❌ Arquivo CSV não foi criado")

# Executar utilitário de estatísticas
print("\n" + "="*70)
print("📊 ESTATÍSTICAS DO BANCO DE DADOS")
print("="*70)

try:
    from Agent_C.csv_utils import estatisticas_validacoes
    estatisticas_validacoes()
except Exception as e:
    print(f"⚠️ Erro ao carregar estatísticas: {e}")
