"""
Exemplo de validação completa do Agente C com RAG funcionando
Demonstra os 4 casos de validação:
- Caso 1: B validado sem ressalvas (confiança ALTA)
- Caso 2: B validado com ressalvas OU B não classificou mas regras têm info (confiança MODERADA)
- Caso 3: Discrepância crítica (INVALIDA - repetir exames)
- Caso 4: Dados insuficientes (BAIXA confiança)
"""

import sys
sys.path.append('.')

from Agent_C.agent_c import agent_c_answer

print("="*80)
print("EXEMPLO 1: Concordância Total - IRIS 2")
print("="*80)

# Dados clínicos consistentes para IRIS 2
clinical_data_1 = {
    "creatinina": 2.2,
    "sdma": 22.0,
    "upc": 0.15,
    "pressao": 150
}

inference_result_1 = {
    "estagio": "IRIS2",
    "subestagio_ap": "AP0",
    "subestagio_ht": "HT1",
    "classificacao_valida": True,
    "confianca": 0.92
}

result_1 = agent_c_answer(
    resultado_b=inference_result_1,
    clinical_data=clinical_data_1,
    pergunta="Qual o prognóstico para este caso?"
)

print(f"\n📊 RESULTADO:")
print(f"- Caso: {result_1.get('caso')}")
print(f"- Estágio Final: {result_1.get('estagio_final')}")
print(f"- Validação B: {'✅ Aprovada' if result_1.get('valida_b') else '❌ Reprovada'}")
print(f"- Confiança: {result_1.get('confianca')}")
if result_1.get('resposta_pergunta'):
    print(f"- Resposta RAG: {result_1.get('resposta_pergunta')[:150]}...")

print("\n" + "="*80)
print("EXEMPLO 2: Dados Borderline - IRIS 1/2")
print("="*80)

clinical_data_2 = {
    "creatinina": 1.6,
    "sdma": 18.0,
    "upc": 0.08,
    "pressao": 140
}

inference_result_2 = {
    "estagio": "IRIS2",
    "subestagio_ap": "AP0",
    "subestagio_ht": "HT0",
    "classificacao_valida": True,
    "confianca": 0.78
}

result_2 = agent_c_answer(
    resultado_b=inference_result_2,
    clinical_data=clinical_data_2,
    pergunta="Este caso está no limiar, qual a recomendação?"
)

print(f"\n📊 RESULTADO:")
print(f"- Caso: {result_2.get('caso')}")
print(f"- Estágio Final: {result_2.get('estagio_final')}")
print(f"- Validação B: {'✅ Aprovada' if result_2.get('valida_b') else '❌ Reprovada'}")
if result_2.get('resposta_pergunta'):
    print(f"- Resposta RAG: {result_2.get('resposta_pergunta')[:150]}...")

print("\n" + "="*80)
print("EXEMPLO 3: IRIS 3 Avançado")
print("="*80)

clinical_data_3 = {
    "creatinina": 3.8,
    "sdma": 34.0,
    "upc": 0.45,
    "pressao": 175
}

inference_result_3 = {
    "estagio": "IRIS3",
    "subestagio_ap": "AP2",
    "subestagio_ht": "HT2",
    "classificacao_valida": True,
    "confianca": 0.95
}

result_3 = agent_c_answer(
    resultado_b=inference_result_3,
    clinical_data=clinical_data_3,
    pergunta="Quais as recomendações terapêuticas para IRIS 3 com proteinúria?"
)

print(f"\n📊 RESULTADO:")
print(f"- Caso: {result_3.get('caso')}")
print(f"- Estágio Final: {result_3.get('estagio_final')}")
print(f"- Validação B: {'✅ Aprovada' if result_3.get('valida_b') else '❌ Reprovada'}")
print(f"- Confiança: {result_3.get('confianca')}")
if result_3.get('resposta_pergunta'):
    print(f"- Resposta RAG: {result_3.get('resposta_pergunta')[:200]}...")

print("\n" + "="*80)
print("✅ Validações salvas em Agent_C/validations_database.csv")
print("="*80)
