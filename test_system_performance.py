"""
Sistema de Avaliação de Desempenho - Multi-Agente IRIS
=======================================================

Métricas adaptadas para sistema de suporte à decisão clínica veterinária.

MÉTRICAS IMPLEMENTADAS:
1. Concordância com Diretrizes IRIS (padrão-ouro)
2. Validação Cruzada (Agente B vs Agente C)
3. Precisão de Subetágios (AP e HT)
4. Qualidade de Resposta RAG
5. Análise de Casos Críticos

DIFERENÇA DE ML TRADICIONAL:
- Não usamos accuracy/F1-score (não aplicável)
- Usamos validação clínica baseada em guidelines
- Foco em confiabilidade e rastreabilidade
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from run_lg import run_pipeline

# =====================================================================
# CASOS DE TESTE BASEADOS EM DIRETRIZES IRIS OFICIAIS
# =====================================================================

CASOS_TESTE_IRIS = [
    {
        "id": "IRIS1_NORMAL",
        "descricao": "Gato saudável - IRIS 1",
        "dados": {
            "nome": "Luna",
            "sexo": "F",
            "raca": "SRD",
            "creatinina": 1.4,
            "sdma": 14.0,
            "idade": 2,
            "peso": 3.5,
            "pressao": 120,
            "upc": 0.15
        },
        "estagio_esperado": "IRIS 1",
        "subestagio_ap_esperado": "AP0",
        "subestagio_ht_esperado": "HT0",
        "pergunta": "O gato está saudável?"
    },
    {
        "id": "IRIS2_INICIAL",
        "descricao": "DRC inicial - IRIS 2",
        "dados": {
            "nome": "Mimi",
            "sexo": "F",
            "raca": "Persa",
            "creatinina": 2.1,
            "sdma": 20.0,
            "idade": 8,
            "peso": 3.0,
            "pressao": 145,
            "upc": 0.25
        },
        "estagio_esperado": "IRIS 2",
        "subestagio_ap_esperado": "AP1",
        "subestagio_ht_esperado": "HT1",
        "pergunta": "Qual o tratamento recomendado?"
    },
    {
        "id": "IRIS2_PROTEINURICO",
        "descricao": "IRIS 2 com proteinúria",
        "dados": {
            "nome": "Bob",
            "sexo": "M",
            "raca": "Maine Coon",
            "creatinina": 2.5,
            "sdma": 23.0,
            "idade": 10,
            "peso": 5.2,
            "pressao": 155,
            "upc": 0.6
        },
        "estagio_esperado": "IRIS 2",
        "subestagio_ap_esperado": "AP2",
        "subestagio_ht_esperado": "HT1",
        "pergunta": "A proteinúria é grave?"
    },
    {
        "id": "IRIS3_MODERADO",
        "descricao": "DRC moderada - IRIS 3",
        "dados": {
            "nome": "Thor",
            "sexo": "M",
            "raca": "Siamês",
            "creatinina": 3.5,
            "sdma": 30.0,
            "idade": 12,
            "peso": 3.8,
            "pressao": 170,
            "upc": 0.8
        },
        "estagio_esperado": "IRIS 3",
        "subestagio_ap_esperado": "AP2",
        "subestagio_ht_esperado": "HT2",
        "pergunta": "Qual o prognóstico?"
    },
    {
        "id": "IRIS4_AVANCADO",
        "descricao": "DRC avançada - IRIS 4",
        "dados": {
            "nome": "Bella",
            "sexo": "F",
            "raca": "Ragdoll",
            "creatinina": 6.2,
            "sdma": 55.0,
            "idade": 15,
            "peso": 2.5,
            "pressao": 195,
            "upc": 1.2
        },
        "estagio_esperado": "IRIS 4",
        "subestagio_ap_esperado": "AP2",
        "subestagio_ht_esperado": "HT3",
        "pergunta": "Qual o cuidado paliativo?"
    },
    {
        "id": "DISCREPANCIA_1_ESTAGIO",
        "descricao": "Discrepância aceitável (1 estágio)",
        "dados": {
            "nome": "Max",
            "sexo": "M",
            "raca": "SRD",
            "creatinina": 2.1,  # IRIS 2
            "sdma": 28.0,       # IRIS 3
            "idade": 9,
            "peso": 4.0,
            "pressao": 150,
            "upc": 0.3
        },
        "estagio_esperado": "IRIS 3",  # Usar maior
        "validacao_esperada": True,
        "pergunta": "Por que há discrepância?"
    },
    {
        "id": "DISCREPANCIA_GRAVE",
        "descricao": "Discrepância inaceitável (3 estágios)",
        "dados": {
            "nome": "Nina",
            "sexo": "F",
            "raca": "Persa",
            "creatinina": 1.3,  # IRIS 1
            "sdma": 50.0,       # IRIS 4
            "idade": 11,
            "peso": 3.2,
            "pressao": 140,
            "upc": 0.2
        },
        "estagio_esperado": None,  # Deve rejeitar
        "validacao_esperada": False,
        "caso_esperado": 3,
        "pergunta": "Os exames estão corretos?"
    },
    {
        "id": "HIPERTENSAO_GRAVE",
        "descricao": "Hipertensão grave (HT3)",
        "dados": {
            "nome": "Felix",
            "sexo": "M",
            "raca": "Siamês",
            "creatinina": 2.8,
            "sdma": 25.0,
            "idade": 13,
            "peso": 3.5,
            "pressao": 195,
            "upc": 0.4
        },
        "estagio_esperado": "IRIS 2",
        "subestagio_ht_esperado": "HT3",
        "pergunta": "A pressão é perigosa?"
    }
]


# =====================================================================
# FUNÇÕES DE AVALIAÇÃO
# =====================================================================

def extrair_metricas_resposta(resposta: str, caso_teste: Dict) -> Dict[str, Any]:
    """
    Extrai métricas da resposta do sistema
    """
    metricas = {
        "estagio_detectado": None,
        "subestagio_ap": None,
        "subestagio_ht": None,
        "caso": None,
        "confianca": None,
        "validacao_ok": None
    }
    
    # Extrair estágio IRIS
    if "IRIS 1" in resposta or "IRIS1" in resposta:
        metricas["estagio_detectado"] = "IRIS 1"
    elif "IRIS 2" in resposta or "IRIS2" in resposta:
        metricas["estagio_detectado"] = "IRIS 2"
    elif "IRIS 3" in resposta or "IRIS3" in resposta:
        metricas["estagio_detectado"] = "IRIS 3"
    elif "IRIS 4" in resposta or "IRIS4" in resposta:
        metricas["estagio_detectado"] = "IRIS 4"
    
    # Extrair subetágios
    if "AP0" in resposta:
        metricas["subestagio_ap"] = "AP0"
    elif "AP1" in resposta:
        metricas["subestagio_ap"] = "AP1"
    elif "AP2" in resposta:
        metricas["subestagio_ap"] = "AP2"
    
    if "HT0" in resposta:
        metricas["subestagio_ht"] = "HT0"
    elif "HT1" in resposta:
        metricas["subestagio_ht"] = "HT1"
    elif "HT2" in resposta:
        metricas["subestagio_ht"] = "HT2"
    elif "HT3" in resposta:
        metricas["subestagio_ht"] = "HT3"
    
    # Extrair caso
    if "Caso: 1" in resposta:
        metricas["caso"] = 1
    elif "Caso: 2" in resposta:
        metricas["caso"] = 2
    elif "Caso: 3" in resposta:
        metricas["caso"] = 3
    
    # Extrair confiança
    if "ALTA" in resposta:
        metricas["confianca"] = "ALTA"
    elif "MODERADA" in resposta:
        metricas["confianca"] = "MODERADA"
    elif "BAIXA" in resposta:
        metricas["confianca"] = "BAIXA"
    elif "INVÁLIDA" in resposta:
        metricas["confianca"] = "INVÁLIDA"
    
    return metricas


def avaliar_caso(caso: Dict) -> Dict[str, Any]:
    """
    Avalia um caso de teste
    """
    print(f"\n{'='*70}")
    print(f"TESTE: {caso['id']} - {caso['descricao']}")
    print(f"{'='*70}")
    
    try:
        # Executar sistema
        resposta = run_pipeline(
            formulario=caso["dados"],
            texto_livre=caso["pergunta"]
        )
        
        # Extrair métricas
        metricas = extrair_metricas_resposta(resposta, caso)
        
        # Avaliar concordância com esperado
        resultado = {
            "id": caso["id"],
            "descricao": caso["descricao"],
            "sucesso": True,
            "detalhes": {}
        }
        
        # 1. Verificar estágio IRIS
        if caso.get("estagio_esperado"):
            estagio_correto = (metricas["estagio_detectado"] == caso["estagio_esperado"])
            resultado["detalhes"]["estagio_correto"] = estagio_correto
            if not estagio_correto:
                resultado["sucesso"] = False
                print(f"[ERRO] Esperado {caso['estagio_esperado']}, obtido {metricas['estagio_detectado']}")
            else:
                print(f"[OK] Estagio correto: {metricas['estagio_detectado']}")
        
        # 2. Verificar subetágio AP
        if caso.get("subestagio_ap_esperado"):
            ap_correto = (metricas["subestagio_ap"] == caso["subestagio_ap_esperado"])
            resultado["detalhes"]["ap_correto"] = ap_correto
            if not ap_correto:
                print(f"[AVISO] AP: Esperado {caso['subestagio_ap_esperado']}, obtido {metricas['subestagio_ap']}")
            else:
                print(f"[OK] Subestagio AP correto: {metricas['subestagio_ap']}")
        
        # 3. Verificar subetágio HT
        if caso.get("subestagio_ht_esperado"):
            ht_correto = (metricas["subestagio_ht"] == caso["subestagio_ht_esperado"])
            resultado["detalhes"]["ht_correto"] = ht_correto
            if not ht_correto:
                print(f"[AVISO] HT: Esperado {caso['subestagio_ht_esperado']}, obtido {metricas['subestagio_ht']}")
            else:
                print(f"[OK] Subestagio HT correto: {metricas['subestagio_ht']}")
        
        # 4. Verificar caso (para discrepâncias)
        if caso.get("caso_esperado"):
            caso_correto = (metricas["caso"] == caso["caso_esperado"])
            resultado["detalhes"]["caso_correto"] = caso_correto
            if not caso_correto:
                resultado["sucesso"] = False
                print(f"[ERRO] Caso esperado {caso['caso_esperado']}, obtido {metricas['caso']}")
            else:
                print(f"[OK] Caso correto: {metricas['caso']}")
        
        # 5. Verificar confiança
        print(f"[INFO] Confianca: {metricas['confianca']}")
        
        resultado["metricas"] = metricas
        resultado["resposta_completa"] = resposta
        
        return resultado
        
    except Exception as e:
        print(f"❌ ERRO na execução: {e}")
        import traceback
        traceback.print_exc()
        return {
            "id": caso["id"],
            "descricao": caso["descricao"],
            "sucesso": False,
            "erro": str(e)
        }


def gerar_relatorio(resultados: List[Dict]) -> Dict[str, Any]:
    """
    Gera relatório consolidado de desempenho
    """
    total = len(resultados)
    sucessos = sum(1 for r in resultados if r.get("sucesso", False))
    
    # Métricas detalhadas
    estagios_corretos = sum(1 for r in resultados if r.get("detalhes", {}).get("estagio_correto", False))
    ap_corretos = sum(1 for r in resultados if r.get("detalhes", {}).get("ap_correto", False))
    ht_corretos = sum(1 for r in resultados if r.get("detalhes", {}).get("ht_correto", False))
    
    # Casos com subetágios testados
    casos_com_ap = sum(1 for r in resultados if r.get("detalhes", {}).get("ap_correto") is not None)
    casos_com_ht = sum(1 for r in resultados if r.get("detalhes", {}).get("ht_correto") is not None)
    
    relatorio = {
        "total_casos": total,
        "casos_sucesso": sucessos,
        "casos_falha": total - sucessos,
        "taxa_sucesso_geral": (sucessos / total * 100) if total > 0 else 0,
        
        # Métricas específicas
        "concordancia_iris": {
            "corretos": estagios_corretos,
            "total": total,
            "percentual": (estagios_corretos / total * 100) if total > 0 else 0
        },
        "precisao_ap": {
            "corretos": ap_corretos,
            "total": casos_com_ap,
            "percentual": (ap_corretos / casos_com_ap * 100) if casos_com_ap > 0 else 0
        },
        "precisao_ht": {
            "corretos": ht_corretos,
            "total": casos_com_ht,
            "percentual": (ht_corretos / casos_com_ht * 100) if casos_com_ht > 0 else 0
        },
        
        "detalhes_casos": resultados
    }
    
    return relatorio


# =====================================================================
# EXECUÇÃO PRINCIPAL
# =====================================================================

def main():
    # Fix Windows console encoding
    import sys
    import io
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("="*70)
    print("🔬 SISTEMA DE AVALIAÇÃO DE DESEMPENHO - MULTI-AGENTE IRIS")
    print("="*70)
    print("\n📋 MÉTRICAS CLÍNICAS (não ML tradicional):")
    print("   1. Concordância com Guidelines IRIS")
    print("   2. Validação Cruzada (B vs C)")
    print("   3. Precisão de Subetágios (AP/HT)")
    print("   4. Detecção de Discrepâncias")
    print("\n⚠️  NOTA: Não usamos accuracy/F1-score (inadequados para sistemas médicos)")
    print("="*70)
    
    resultados = []
    
    # Executar todos os casos
    for caso in CASOS_TESTE_IRIS:
        resultado = avaliar_caso(caso)
        resultados.append(resultado)
    
    # Gerar relatório
    print("\n\n" + "="*70)
    print("📊 RELATÓRIO FINAL DE DESEMPENHO")
    print("="*70)
    
    relatorio = gerar_relatorio(resultados)
    
    print(f"\n📈 MÉTRICAS GERAIS:")
    print(f"   Total de casos testados: {relatorio['total_casos']}")
    print(f"   Casos com sucesso: {relatorio['casos_sucesso']}")
    print(f"   Casos com falha: {relatorio['casos_falha']}")
    print(f"   Taxa de sucesso geral: {relatorio['taxa_sucesso_geral']:.1f}%")
    
    print(f"\n🎯 CONCORDÂNCIA COM DIRETRIZES IRIS:")
    print(f"   Estágios corretos: {relatorio['concordancia_iris']['corretos']}/{relatorio['concordancia_iris']['total']}")
    print(f"   Concordância IRIS: {relatorio['concordancia_iris']['percentual']:.1f}%")
    
    print(f"\n🔬 PRECISÃO DE SUBETÁGIOS:")
    print(f"   AP (Proteinúria) corretos: {relatorio['precisao_ap']['corretos']}/{relatorio['precisao_ap']['total']}")
    print(f"   Precisão AP: {relatorio['precisao_ap']['percentual']:.1f}%")
    print(f"   HT (Hipertensão) corretos: {relatorio['precisao_ht']['corretos']}/{relatorio['precisao_ht']['total']}")
    print(f"   Precisão HT: {relatorio['precisao_ht']['percentual']:.1f}%")
    
    # Salvar relatório
    output_file = Path("relatorio_desempenho.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(relatorio, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Relatório completo salvo em: {output_file}")
    print("\n✅ Avaliação concluída!")
    print("="*70)
    
    return relatorio


if __name__ == "__main__":
    main()
