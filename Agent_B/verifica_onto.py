import os
import json
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional
from owlready2 import (
    World, Thing,
    DataProperty, ObjectProperty, AnnotationProperty,
    sync_reasoner_hermit
)

# =====================================================================
# CONFIGURAÇÃO DO CAMINHO DA ONTOLOGIA
# =====================================================================
ONTO_PATH = Path(r"Agent_B/onthology/Ontology_MAS_projeto.owl")

def _load_ontology():
    """Carrega a ontologia com tratamento de erros robusto"""
    world = World()
    
    if not ONTO_PATH.exists():
        raise FileNotFoundError(f"Arquivo OWL não encontrado em: {ONTO_PATH}")
    
    print(f"[agente_b] Carregando ontologia de: {ONTO_PATH}")
    
    try:
        onto = world.get_ontology(f"file://{ONTO_PATH.absolute()}").load()
        print(f"[agente_b] ✓ Ontologia carregada com sucesso")
        print(f"   - Classes: {len(list(onto.classes()))}")
        print(f"   - Indivíduos: {len(list(onto.individuals()))}")
        return world, onto
    except Exception as e:
        raise Exception(f"Erro ao carregar ontologia: {e}")


# =====================================================================
# CLASSIFICAÇÃO MANUAL IRIS (FALLBACK)
# =====================================================================
def classificar_estagio_manual(creat: Optional[float], sdma: Optional[float]) -> Optional[str]:
    """
    Classificação manual seguindo a lógica IRIS correta:
    Usa o estágio MAIS ALTO entre creatinina e SDMA
    """
    stage_creat = None
    stage_sdma = None
    
    # Classificar por creatinina
    if creat is not None:
        if creat < 1.6:
            stage_creat = "EstagioIRIS1"
        elif 1.6 <= creat <= 2.8:
            stage_creat = "EstagioIRIS2"
        elif 2.9 <= creat <= 5.0:
            stage_creat = "EstagioIRIS3"
        elif creat > 5.0:
            stage_creat = "EstagioIRIS4"
    
    # Classificar por SDMA
    if sdma is not None:
        if 15.0 <= sdma <= 17.0:
            stage_sdma = "EstagioIRIS1"
        elif 18.0 <= sdma <= 25.0:
            stage_sdma = "EstagioIRIS2"
        elif 26.0 <= sdma <= 38.0:
            stage_sdma = "EstagioIRIS3"
        elif sdma > 38.0:
            stage_sdma = "EstagioIRIS4"
    
    # Escolher o estágio mais alto
    ordem = {"EstagioIRIS1": 1, "EstagioIRIS2": 2, "EstagioIRIS3": 3, "EstagioIRIS4": 4}
    
    candidatos = []
    if stage_creat:
        candidatos.append((stage_creat, ordem[stage_creat]))
    if stage_sdma:
        candidatos.append((stage_sdma, ordem[stage_sdma]))
    
    if not candidatos:
        return None
    
    # Retornar o de maior risco
    estagio_escolhido = max(candidatos, key=lambda x: x[1])[0]
    
    print(f"[CLASSIFICAÇÃO MANUAL]")
    if stage_creat:
        print(f"   Creatinina {creat} → {stage_creat}")
    if stage_sdma:
        print(f"   SDMA {sdma} → {stage_sdma}")
    print(f"   Estágio final: {estagio_escolhido}")
    
    return estagio_escolhido


# =====================================================================
# EXTRAÇÃO DE ESTÁGIO IRIS
# =====================================================================
def _extract_iris_stage(is_a_list: List[str]) -> Optional[str]:
    """
    Extrai o estágio IRIS da lista de classes inferidas
    """
    for cls in is_a_list:
        cls_str = str(cls)
        if "EstagioIRIS" in cls_str or "estagio" in cls_str.lower():
            # Extrair número
            for i in range(1, 5):
                if str(i) in cls_str:
                    return f"IRIS {i}"
            # Se achou mas não tem número, retornar nome
            if "IRIS" in cls_str:
                return cls_str
    return None


# =====================================================================
# CRIA PACIENTE TEMPORÁRIO NA ONTOLOGIA
# =====================================================================
def _create_patient_instance(world, onto, patient_id: str, clinical: Dict[str, Any]):
    """
    Cria uma instância de paciente (gato) na ontologia com os dados clínicos
    """
    # Buscar classe Gato
    Gato = onto.search_one(iri="*Gato")
    if not Gato:
        Gato = Thing
        print("[AVISO] Classe 'Gato' não encontrada na ontologia, usando Thing")
    
    # Criar instância
    inst_name = f"GatoPaciente_{patient_id}"
    patient = Gato(inst_name, namespace=onto)
    print(f"[AGENTE B] ✓ Instância criada: {inst_name}")
    
    # Mapear propriedades
    prop_mappings = {
        "creatinine": "nivelCreatinina",
        "creatinina": "nivelCreatinina",
        "sdma": "nivelSDMA",
        "idade": "idade",
        "age_years": "idade",
        "peso": "peso",
        "weight": "peso",
        "pressao": "pressaoArterial",
        "upc": "razaoProteina",
        "proteinuria": "razaoProteina"
    }
    
    # Aplicar propriedades
    print(f"[AGENTE B] Aplicando propriedades:")
    for key, value in clinical.items():
        if key in prop_mappings:
            prop_name = prop_mappings[key]
            prop = onto.search_one(iri=f"*{prop_name}")
            
            if prop:
                try:
                    val = float(value) if not isinstance(value, (list, dict)) else value
                    setattr(patient, prop.name, [val])
                    print(f"   ✓ {prop.name} = {val}")
                except Exception as e:
                    print(f"   ✗ Erro ao setar {prop_name}: {e}")
            else:
                print(f"   ⚠️ Propriedade {prop_name} não encontrada na ontologia")
    
    return patient


# =====================================================================
# EXTRAI INFORMAÇÕES DO PACIENTE APÓS INFERÊNCIA
# =====================================================================
def _extract_claims_from_instance(instance):
    """Extrai informações inferidas sobre o paciente"""
    is_a = []
    for cls in instance.is_a:
        try:
            is_a.append(cls.name if hasattr(cls, 'name') else str(cls))
        except:
            is_a.append(str(cls))
    
    claims = [f"{instance.name} é {cls}" for cls in is_a]
    
    annotations = list(instance.comment) if hasattr(instance, 'comment') else []
    
    data_properties = {}
    for prop in instance.get_properties():
        if isinstance(prop, DataProperty):
            val = getattr(instance, prop.name, None)
            if val:
                data_properties[prop.name] = val
    
    return {
        "is_a": is_a,
        "claims": claims,
        "properties": {
            "annotations": annotations,
            "data_properties": data_properties
        }
    }


# =====================================================================
# FUNÇÃO PRINCIPAL - handle_inference
# =====================================================================
def handle_inference(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Função principal chamada pelo LangGraph
    
    ESTRATÉGIA:
    1. Tentar inferência ontológica
    2. Se falhar, usar classificação manual
    3. Sempre retornar um estágio
    """
    print("\n[AGENTE B] " + "="*60)
    print("[AGENTE B] Iniciando inferência ontológica...")
    print("[AGENTE B] " + "="*60)
    
    # Extrair dados da requisição
    question = request.get("question", "")
    clinical = request.get("dados_clinicos", {})
    
    if not clinical:
        return {
            "tipo": "inferencia",
            "estagio": None,
            "reasoner_ok": False,
            "explanation": "Dados clínicos não fornecidos",
            "inferred": [],
            "properties": {},
            "metodo": "erro"
        }
    
    # Extrair valores para classificação manual
    creat = clinical.get("creatinina") or clinical.get("creatinine")
    sdma = clinical.get("sdma")
    
    print(f"\n[AGENTE B] Valores recebidos:")
    print(f"   • Creatinina: {creat}")
    print(f"   • SDMA: {sdma}")
    
    # Carregar ontologia
    try:
        world, onto = _load_ontology()
    except Exception as e:
        # FALLBACK: Se ontologia falhar, usar classificação manual
        print(f"[AGENTE B] ⚠️ Erro ao carregar ontologia, usando classificação manual")
        estagio_manual = classificar_estagio_manual(creat, sdma)
        
        return {
            "tipo": "inferencia",
            "estagio": f"IRIS {estagio_manual[-1]}" if estagio_manual else None,
            "reasoner_ok": False,
            "explanation": f"Ontologia falhou. Classificação manual: {estagio_manual}",
            "inferred": [],
            "properties": {},
            "metodo": "manual_por_erro_ontologia"
        }
    
    # Criar instância do paciente
    patient_id = str(uuid.uuid4())[:8]
    print(f"\n[AGENTE B] Criando paciente: {patient_id}")
    
    try:
        patient = _create_patient_instance(world, onto, patient_id, clinical)
    except Exception as e:
        print(f"[AGENTE B] ⚠️ Erro ao criar instância, usando classificação manual")
        estagio_manual = classificar_estagio_manual(creat, sdma)
        
        return {
            "tipo": "inferencia",
            "estagio": f"IRIS {estagio_manual[-1]}" if estagio_manual else None,
            "reasoner_ok": False,
            "explanation": f"Erro ao criar instância: {e}. Usando classificação manual.",
            "inferred": [],
            "properties": {},
            "metodo": "manual_por_erro_instancia"
        }
    
    # Executar reasoner
    print(f"\n[AGENTE B] Executando reasoner HermiT...")
    try:
        sync_reasoner_hermit(world, infer_property_values=True, debug=0)
        reasoner_ok = True
        print("[AGENTE B] ✓ Reasoner executado com sucesso")
    except Exception as e:
        print(f"[AGENTE B] ⚠️ Reasoner falhou, usando classificação manual")
        estagio_manual = classificar_estagio_manual(creat, sdma)
        
        return {
            "tipo": "inferencia",
            "estagio": f"IRIS {estagio_manual[-1]}" if estagio_manual else None,
            "reasoner_ok": False,
            "explanation": f"Reasoner falhou: {e}. Usando classificação manual.",
            "inferred": [],
            "properties": {},
            "metodo": "manual_por_erro_reasoner"
        }
    
    # Extrair informações inferidas
    extracted = _extract_claims_from_instance(patient)
    is_a = extracted["is_a"]
    properties = extracted["properties"]
    
    print(f"\n[AGENTE B] Classes inferidas:")
    for cls in is_a:
        print(f"   • {cls}")
    
    # Tentar extrair estágio da ontologia
    detected_stage = _extract_iris_stage(is_a)
    
    # ESTRATÉGIA HÍBRIDA
    if detected_stage:
        # ✅ Ontologia funcionou
        print(f"[AGENTE B] ✓ Estágio detectado pela ONTOLOGIA: {detected_stage}")
        metodo = "ontologia"
        explanation = "Inferência ontológica bem-sucedida"
    else:
        # ⚠️ Ontologia não inferiu - usar classificação manual
        print(f"[AGENTE B] ⚠️ Ontologia não inferiu estágio")
        print(f"[AGENTE B] 💡 Usando classificação manual (lógica IRIS correta)")
        
        estagio_manual = classificar_estagio_manual(creat, sdma)
        if estagio_manual:
            detected_stage = f"IRIS {estagio_manual[-1]}"
            metodo = "manual"
            explanation = f"Ontologia não inferiu. Classificação manual aplicada (lógica IRIS: maior risco entre creatinina e SDMA)."
        else:
            detected_stage = None
            metodo = "falha_completa"
            explanation = "Não foi possível inferir estágio nem pela ontologia nem manualmente"
    
    # Extrair comorbidades
    comorbidities = []
    for annotation in properties.get("annotations", []):
        if annotation.startswith("comorbidity:"):
            comorbidities.append(annotation.split(":", 1)[1])
    
    # Resultado final
    result = {
        "tipo": "inferencia",
        "question": question,
        "estagio": detected_stage,
        "inferred": extracted["claims"],
        "raw_is_a": is_a,
        "properties": properties,
        "comorbidities": comorbidities,
        "reasoner_ok": reasoner_ok,
        "metodo": metodo,
        "explanation": explanation
    }
    
    print(f"\n[AGENTE B] " + "="*60)
    print(f"[AGENTE B] Resultado final:")
    print(f"[AGENTE B]   • Estágio: {detected_stage or 'NÃO INFERIDO'}")
    print(f"[AGENTE B]   • Método: {metodo}")
    print(f"[AGENTE B]   • Reasoner OK: {reasoner_ok}")
    print(f"[AGENTE B] " + "="*60)
    
    return result