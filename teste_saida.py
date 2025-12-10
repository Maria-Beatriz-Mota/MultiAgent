"""Teste simples da saída do sistema"""
import sys
import io

# Fix Windows encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from run_lg import run_pipeline

# Teste simples
resultado = run_pipeline(
    formulario={
        'nome': 'Mimi',
        'sexo': 'F',
        'raca': 'Persa',
        'creatinina': 2.1,
        'sdma': 20.0,
        'pressao': 145,
        'upc': 0.25,
        'idade': 8,
        'peso': 3.0
    },
    texto_livre='Qual o tratamento recomendado?'
)

print("\n" + "="*70)
print("RESULTADO DA EXECUÇÃO:")
print("="*70)
print(resultado)
