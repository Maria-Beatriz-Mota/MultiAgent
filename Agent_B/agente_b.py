"""
Agente B – Inferência Ontológica (CORRIGIDO COM VALIDAÇÃO DE DISCREPÂNCIA)
--------------------------------------------------------------------------

NOVA REGRA IMPLEMENTADA:
- Detectar discrepâncias entre creatinina e SDMA
- Se discrepância > 1 estágio: NÃO INFERIR (alertar erro)
- Se discrepância ≤ 1 estágio: Usar o maior (regra IRIS padrão)

Exemplo:
- Creat=2.5 (IRIS 2), SDMA=28 (IRIS 3) → OK, usar IRIS 3 ✅
- Creat=1.5 (IRIS 1), SDMA=50 (IRIS 4) → ERRO, não classificar! ❌
"""

import os
import json
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from owlready2 import (
    World, Thing,
    DataProperty, ObjectProperty,
    sync_reasoner_hermit
)

# =====================================================================
# CONFIGURAÇÃO
# =====================================================================
ONTO_PATH = Path(r"Agent_B/onthology/Ontology_MAS_projeto.owl")


def _load_ontology():
    """Carrega a ontologia"""
    world = World()
    
    if not ONTO_PATH.exists():
        raise FileNotFoundError(f"Arquivo OWL não encontrado em: {ONTO_PATH}")
    
    print(f"[AGENTE B] Carregando ontologia de: {ONTO_PATH}")
    
    try:
        onto = world.get_ontology(f"file://{ONTO_PATH.absolute()}").load()
        print(f"[AGENTE B] ✓ Ontologia carregada")
        print(f"[AGENTE B]   - Classes: {len(list(onto.classes()))}")
        return world, onto
    except Exception as e:
        raise Exception(f"Erro ao carregar ontologia: {e}")


# =====================================================================
# 🔧 CLASSIFICAÇÃO IRIS COM VALIDAÇÃO DE DISCREPÂNCIA
# =====================================================================
def classificar_estagio_iris_com_validacao(
    creat: Optional[float], 
    sdma: Optional[float]
) -> Tuple[Optional[str], bool, Optional[str]]:
    """
    Classifica estágio IRIS com validação de discrepância
    
    Regras IRIS oficiais:
    1. Se creatinina e SDMA concordam (mesmo estágio): OK
    2. Se diferença = 1 estágio: OK (usar o maior)
    3. Se diferença >= 2 estágios: ERRO - não classificar!
    
    Args:
        creat: Creatinina em mg/dL
        sdma: SDMA em µg/dL
    
    Returns:
        (estagio, valido, motivo_erro)
        - estagio: "EstagioIRIS1", "EstagioIRIS2", etc. ou None
        - valido: True se classificação é confiável
        - motivo_erro: Descrição do erro se inválido
    
    Exemplos:
        >>> classificar_estagio_iris_com_validacao(2.5, 22)
        ("EstagioIRIS2", True, None)  # Ambos IRIS 2
        
        >>> classificar_estagio_iris_com_validacao(2.5, 28)
        ("EstagioIRIS3", True, None)  # Creat=2, SDMA=3, diff=1 OK
        
        >>> classificar_estagio_iris_com_validacao(1.5, 50)
        (None, False, "Discrepância grande: Creat=IRIS 1, SDMA=IRIS 4")
    """
    
    if creat is None and sdma is None:
        return None, False, "Creatinina e SDMA ausentes"
    
    # Determinar estágio pela creatinina
    stage_creat = None
    if creat is not None:
        if creat < 1.6:
            stage_creat = 1
        elif 1.6 <= creat <= 2.8:
            stage_creat = 2
        elif 2.9 <= creat <= 5.0:
            stage_creat = 3
        else:  # creat > 5.0
            stage_creat = 4
    
    # Determinar estágio pelo SDMA
    stage_sdma = None
    if sdma is not None:
        if sdma < 18.0:
            stage_sdma = 1
        elif 18.0 <= sdma <= 25.0:
            stage_sdma = 2
        elif 26.0 <= sdma <= 38.0:
            stage_sdma = 3
        else:  # sdma > 38.0
            stage_sdma = 4
    
    # ===== VALIDAÇÃO DE DISCREPÂNCIA =====
    
    # Caso 1: Só tem um biomarcador
    if stage_creat is None and stage_sdma is not None:
        print(f"[AGENTE B] ⚠️ Apenas SDMA disponível → IRIS {stage_sdma}")
        print(f"[AGENTE B]    Recomendado: confirmar com creatinina")
        return f"EstagioIRIS{stage_sdma}", True, None
    
    if stage_sdma is None and stage_creat is not None:
        print(f"[AGENTE B] ⚠️ Apenas Creatinina disponível → IRIS {stage_creat}")
        print(f"[AGENTE B]    Recomendado: confirmar com SDMA")
        return f"EstagioIRIS{stage_creat}", True, None
    
    # Caso 2: Tem ambos - VALIDAR DISCREPÂNCIA
    discrepancia = abs(stage_creat - stage_sdma)
    
    print(f"[AGENTE B] Valores:")
    print(f"[AGENTE B]   Creatinina {creat} mg/dL → IRIS {stage_creat}")
    print(f"[AGENTE B]   SDMA {sdma} µg/dL → IRIS {stage_sdma}")
    print(f"[AGENTE B]   Discrepância: {discrepancia} estágios")
    
    # ===== REGRA DE VALIDAÇÃO =====
    
    if discrepancia == 0:
        # ✅ Concordância perfeita
        print(f"[AGENTE B] ✅ Concordância perfeita")
        return f"EstagioIRIS{stage_creat}", True, None
    
    elif discrepancia == 1:
        # ✅ Discrepância de 1 estágio - ACEITAR (usar o maior)
        estagio_final = max(stage_creat, stage_sdma)
        print(f"[AGENTE B] ✅ Discrepância de 1 estágio aceita (regra IRIS)")
        print(f"[AGENTE B]    Usando IRIS {estagio_final} (maior valor)")
        return f"EstagioIRIS{estagio_final}", True, None
    
    else:
        # ❌ Discrepância ≥2 estágios - NÃO CLASSIFICAR!
        motivo = f"Discrepância de {discrepancia} estágios: Creatinina indica IRIS {stage_creat}, SDMA indica IRIS {stage_sdma}"
        
        print(f"[AGENTE B] ❌ ERRO: Discrepância muito grande ({discrepancia} estágios)")
        print(f"[AGENTE B]    Creat={creat} → IRIS {stage_creat}")
        print(f"[AGENTE B]    SDMA={sdma} → IRIS {stage_sdma}")
        print(f"[AGENTE B]    → NÃO É POSSÍVEL CLASSIFICAR COM SEGURANÇA")
        print(f"[AGENTE B]    Possíveis causas:")
        print(f"[AGENTE B]      • Erro laboratorial")
        print(f"[AGENTE B]      • Interferência pré-analítica")
        print(f"[AGENTE B]      • Condição clínica atípica")
        print(f"[AGENTE B]      • Desidratação (eleva creatinina)")
        print(f"[AGENTE B]      • Massa muscular reduzida (reduz creatinina)")
        
        return None, False, motivo


# =====================================================================
# CRIAR PACIENTE NA ONTOLOGIA (mantido)
# =====================================================================
def _create_patient_instance(world, onto, patient_id: str, clinical: Dict[str, Any]):
    """Cria instância de paciente na ontologia"""
    Gato = onto.search_one(iri="*Gato")
    if not Gato:
        Gato = Thing
    
    inst_name = f"GatoPaciente_{patient_id}"
    patient = Gato(inst_name, namespace=onto)
    
    prop_mappings = {
        "creatinine": ["nivelCreatinina", "creatinina"],
        "creatinina": ["nivelCreatinina", "creatinina"],
        "sdma": ["nivelSDMA", "sdma"],
        "idade": ["idade", "temIdade"],
        "peso": ["peso", "temPeso"],
        "pressao": ["pressaoArterial", "pressao"],
        "upc": ["razaoProteina", "proteinuria", "upc"],
        "proteinuria": ["razaoProteina", "proteinuria"],
    }
    
    for key, value in clinical.items():
        if key in prop_mappings and value is not None:
            for prop_name in prop_mappings[key]:
                prop = onto.search_one(iri=f"*{prop_name}")
                if prop:
                    try:
                        val = float(value)
                        prop[patient].append(val)
                        print(f"[AGENTE B]     ✓ {prop.name} = {val}")
                        break
                    except:
                        continue
    
    return patient


# =====================================================================
# EXTRAIR INFORMAÇÕES (mantido)
# =====================================================================
def _extract_claims_from_instance(instance):
    """Extrai informações inferidas"""
    is_a = []
    for cls in instance.is_a:
        try:
            is_a.append(cls.name if hasattr(cls, 'name') else str(cls))
        except:
            is_a.append(str(cls))
    
    annotations = list(instance.comment) if hasattr(instance, 'comment') else []
    
    data_properties = {}
    for prop in instance.get_properties():
        if isinstance(prop, DataProperty):
            prop_name = prop.name
            prop_value = getattr(instance, prop_name, None)
            if prop_value:
                data_properties[prop_name] = prop_value
    
    return {
        "is_a": is_a,
        "properties": {
            "annotations": annotations,
            "data_properties": data_properties
        }
    }


def _extract_iris_stage(is_a_list: List[str]) -> Optional[str]:
    """Extrai estágio IRIS das classes inferidas"""
    for cls in is_a_list:
        cls_str = str(cls).lower()
        if "estagio" in cls_str and "iris" in cls_str:
            for i in range(1, 5):
                if f"iris{i}" in cls_str or f"iris {i}" in cls_str:
                    return f"IRIS {i}"
    return None


def _classificar_subestagio_proteinuria(upc: Optional[float]) -> Optional[str]:
    """
    Classifica subetágios de proteinúria (AP) conforme IRIS
    
    Diretrizes IRIS para proteinúria:
    - AP0: Não proteinúrico (UPC < 0.2)
    - AP1: Borderline proteinúrico (UPC 0.2-0.4)
    - AP2: Proteinúrico (UPC > 0.4)
    
    Args:
        upc: Razão proteína/creatinina urinária
        
    Returns:
        Subetágio AP (AP0, AP1, AP2) ou None
    """
    if upc is None:
        return None
    
    if upc < 0.2:
        return "AP0"  # Não proteinúrico
    elif 0.2 <= upc <= 0.4:
        return "AP1"  # Borderline
    else:  # upc > 0.4
        return "AP2"  # Proteinúrico


def _classificar_subestagio_hipertensao(pressao: Optional[float]) -> Optional[str]:
    """
    Classifica subetágios de hipertensão (HT) conforme IRIS
    
    Diretrizes IRIS para pressão arterial sistólica:
    - HT0: Risco mínimo (< 140 mmHg)
    - HT1: Risco baixo (140-159 mmHg)
    - HT2: Risco moderado (160-179 mmHg)
    - HT3: Risco grave (≥ 180 mmHg)
    
    Args:
        pressao: Pressão arterial sistólica em mmHg
        
    Returns:
        Subetágio HT (HT0, HT1, HT2, HT3) ou None
    """
    if pressao is None:
        return None
    
    if pressao < 140:
        return "HT0"  # Risco mínimo
    elif 140 <= pressao < 160:
        return "HT1"  # Risco baixo
    elif 160 <= pressao < 180:
        return "HT2"  # Risco moderado
    else:  # pressao >= 180
        return "HT3"  # Risco grave


def _extract_substage(is_a_list: List[str]) -> Optional[str]:
    """Extrai subestágio (mantido para compatibilidade com ontologia)"""
    parts = []
    for cls in is_a_list:
        cls_lower = str(cls).lower()
        if "proteinurico" in cls_lower:
            if "nao" in cls_lower or "não" in cls_lower:
                parts.append("não proteinúrico")
            elif "borderline" in cls_lower:
                parts.append("borderline proteinúrico")
            else:
                parts.append("proteinúrico")
        if "risco" in cls_lower:
            if "minimo" in cls_lower:
                parts.append("risco mínimo")
            elif "baixo" in cls_lower:
                parts.append("risco baixo")
            elif "moderado" in cls_lower:
                parts.append("risco moderado")
            elif "grave" in cls_lower:
                parts.append("risco grave")
    return ", ".join(parts) if parts else None


# =====================================================================
# 🔧 FUNÇÃO PRINCIPAL CORRIGIDA
# =====================================================================
def handle_inference(clinical_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Função principal com validação de discrepância
    
    SAÍDA AMPLIADA:
    {
        "estagio": str ou None,
        "subestagio": str ou None,
        "reasoner_ok": bool,
        "classificacao_valida": bool,  # ← NOVO!
        "motivo_invalido": str ou None,  # ← NOVO!
        "properties": {...},
        "question": str
    }
    """
    print("\n" + "="*70)
    print("[AGENTE B] Iniciando inferência ontológica...")
    print("="*70)
    
    if not clinical_data:
        return {
            "estagio": None,
            "subestagio": None,
            "reasoner_ok": False,
            "classificacao_valida": False,
            "motivo_invalido": "Dados clínicos ausentes",
            "properties": {"annotations": [], "data_properties": {}},
            "question": ""
        }
    
    question = clinical_data.get("question", "")
    creatinina_val = clinical_data.get("creatinina") or clinical_data.get("creatinine")
    sdma_val = clinical_data.get("sdma")
    
    print(f"[AGENTE B] Dados recebidos:")
    print(f"[AGENTE B]   Creatinina: {creatinina_val}")
    print(f"[AGENTE B]   SDMA: {sdma_val}")
    
    if creatinina_val is None and sdma_val is None:
        return {
            "estagio": None,
            "subestagio": None,
            "reasoner_ok": False,
            "classificacao_valida": False,
            "motivo_invalido": "Creatinina e SDMA ausentes",
            "properties": {"annotations": [], "data_properties": {}},
            "question": question
        }
    
    # ===== CARREGAR ONTOLOGIA =====
    try:
        world, onto = _load_ontology()
    except Exception as e:
        return {
            "estagio": None,
            "subestagio": None,
            "reasoner_ok": False,
            "classificacao_valida": False,
            "motivo_invalido": f"Erro na ontologia: {e}",
            "properties": {"annotations": [], "data_properties": {}},
            "question": question
        }
    
    # ===== CRIAR INSTÂNCIA =====
    patient_id = str(uuid.uuid4())[:8]
    print(f"[AGENTE B] Criando paciente: {patient_id}")
    
    try:
        patient = _create_patient_instance(world, onto, patient_id, clinical_data)
    except Exception as e:
        return {
            "estagio": None,
            "subestagio": None,
            "reasoner_ok": False,
            "classificacao_valida": False,
            "motivo_invalido": f"Erro ao criar instância: {e}",
            "properties": {"annotations": [], "data_properties": {}},
            "question": question
        }
    
    # ===== 🔧 VALIDAR E CLASSIFICAR COM VERIFICAÇÃO DE DISCREPÂNCIA =====
    estagio_name, classificacao_valida, motivo_invalido = classificar_estagio_iris_com_validacao(
        float(creatinina_val) if creatinina_val is not None else None,
        float(sdma_val) if sdma_val is not None else None
    )
    
    # Se classificação inválida, RETORNAR SEM INFERIR
    if not classificacao_valida:
        print(f"[AGENTE B] ❌ CLASSIFICAÇÃO INVÁLIDA - NÃO SERÁ INFERIDO")
        return {
            "estagio": None,
            "subestagio": None,
            "reasoner_ok": False,
            "classificacao_valida": False,
            "motivo_invalido": motivo_invalido,
            "properties": {"annotations": [], "data_properties": {}},
            "question": question,
            "alerta": "⚠️ ERRO DE CLASSIFICAÇÃO: " + motivo_invalido
        }
    
    # ===== CLASSIFICAÇÃO VÁLIDA - PROSSEGUIR =====
    if estagio_name:
        print(f"[AGENTE B] ✓ Estágio calculado: {estagio_name}")
        
        estagio_class = onto.search_one(iri=f"*{estagio_name}")
        if estagio_class:
            patient.is_a.append(estagio_class)
            print(f"[AGENTE B]   ✓ Paciente classificado como {estagio_name}")
    
    # ===== EXECUTAR REASONER =====
    print("[AGENTE B] Executando reasoner HermiT...")
    reasoner_ok = False
    
    try:
        sync_reasoner_hermit(world, infer_property_values=True)
        reasoner_ok = True
        print("[AGENTE B] ✓ Reasoner executado")
    except Exception as e:
        print(f"[AGENTE B] ⚠️ Erro no reasoner: {e}")
    
    # ===== EXTRAIR INFERÊNCIAS =====
    extracted = _extract_claims_from_instance(patient)
    is_a = extracted["is_a"]
    properties = extracted["properties"]
    
    detected_stage = _extract_iris_stage(is_a)
    
    if detected_stage is None and estagio_name:
        numero = estagio_name.replace("EstagioIRIS", "")
        detected_stage = f"IRIS {numero}"
    
    substage = _extract_substage(is_a)
    
    # ===== CLASSIFICAR SUBETÁGIOS IRIS (AP e HT) =====
    upc = clinical_data.get("upc") or clinical_data.get("proteinuria")
    pressao = clinical_data.get("pressao") or clinical_data.get("pressao_arterial")
    
    subestagio_ap = _classificar_subestagio_proteinuria(upc)
    subestagio_ht = _classificar_subestagio_hipertensao(pressao)
    
    # Montar descrição de subetágios
    subestagios_iris = []
    if subestagio_ap:
        descricao_ap = {
            "AP0": "não proteinúrico",
            "AP1": "borderline proteinúrico", 
            "AP2": "proteinúrico"
        }.get(subestagio_ap, subestagio_ap)
        subestagios_iris.append(f"{subestagio_ap} ({descricao_ap})")
        print(f"[AGENTE B]   Proteinúria: {subestagio_ap} - UPC={upc}")
    
    if subestagio_ht:
        descricao_ht = {
            "HT0": "risco mínimo",
            "HT1": "risco baixo",
            "HT2": "risco moderado",
            "HT3": "risco grave"
        }.get(subestagio_ht, subestagio_ht)
        subestagios_iris.append(f"{subestagio_ht} ({descricao_ht})")
        print(f"[AGENTE B]   Hipertensão: {subestagio_ht} - PA={pressao} mmHg")
    
    subestagios_completo = ", ".join(subestagios_iris) if subestagios_iris else substage
    
    # ===== RESULTADO =====
    result = {
        "estagio": detected_stage,
        "subestagio": subestagios_completo,
        "subestagio_ap": subestagio_ap,  # ← NOVO
        "subestagio_ht": subestagio_ht,  # ← NOVO
        "reasoner_ok": reasoner_ok,
        "classificacao_valida": classificacao_valida,
        "motivo_invalido": motivo_invalido,
        "properties": properties,
        "question": question
    }
    
    print(f"[AGENTE B] ✅ Inferência concluída")
    print(f"[AGENTE B]   Estágio: {detected_stage}")
    if subestagios_completo:
        print(f"[AGENTE B]   Subetágios: {subestagios_completo}")
    print(f"[AGENTE B]   Classificação válida: {classificacao_valida}")
    print("="*70 + "\n")
    
    return result


# =====================================================================
# TESTE
# =====================================================================
if __name__ == "__main__":
    print("="*70)
    print("TESTES DE VALIDAÇÃO DE DISCREPÂNCIA")
    print("="*70)
    
    # Teste 1: Concordância perfeita
    print("\n🧪 TESTE 1: Concordância (Creat=2.5, SDMA=22)")
    resultado1 = handle_inference({
        "creatinina": 2.5,
        "sdma": 22,
        "question": "Teste 1"
    })
    print(f"Resultado: {resultado1['estagio']}, Válido: {resultado1['classificacao_valida']}")
    
    # Teste 2: Discrepância de 1 estágio (OK)
    print("\n🧪 TESTE 2: Discrepância 1 estágio (Creat=2.5→IRIS2, SDMA=28→IRIS3)")
    resultado2 = handle_inference({
        "creatinina": 2.5,
        "sdma": 28,
        "question": "Teste 2"
    })
    print(f"Resultado: {resultado2['estagio']}, Válido: {resultado2['classificacao_valida']}")
    
    # Teste 3: Discrepância grande (ERRO!)
    print("\n🧪 TESTE 3: Discrepância 3 estágios (Creat=1.5→IRIS1, SDMA=50→IRIS4)")
    resultado3 = handle_inference({
        "creatinina": 1.5,
        "sdma": 50,
        "question": "Teste 3"
    })
    print(f"Resultado: {resultado3['estagio']}, Válido: {resultado3['classificacao_valida']}")
    print(f"Motivo: {resultado3['motivo_invalido']}")