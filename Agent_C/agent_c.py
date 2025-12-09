# ==========================================================
# AGENTE C – VALIDADOR CIENTÍFICO (RAG + Regras)
# Interface pública: agent_c_answer(...)
# ==========================================================

import re
from typing import Dict, Any, Optional
from sentence_transformers import SentenceTransformer
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# ----------------------
# Imports condicionais com fallback
# ----------------------
RAG_AVAILABLE = False
LLM_AVAILABLE = False

try:
    from transformers import pipeline, AutoTokenizer
    import torch
    LLM_AVAILABLE = True
    print("[AGENTE C] ✅ LLM disponível")
except ImportError as e:
    print(f"[AGENTE C] ⚠️ LLM não disponível: {e}")

try:
    from .agent_c_db import rag_search, CHROMA_PATH
    RAG_AVAILABLE = True
    print("[AGENTE C] ✅ RAG disponível")
except ImportError as e:
    print(f"[AGENTE C] ⚠️ RAG não disponível: {e}")
    print(f"[AGENTE C] 💡 Instale: pip install langchain langchain-chroma chromadb")
    CHROMA_PATH = None

# ----------------------
# Config do modelo (se disponível)
# ----------------------
llm_pipeline = None
tokenizer = None

if LLM_AVAILABLE:
    try:
        MODEL_ID = "mistralai/Mistral-7B-Instruct-v0.2"
        print("[AGENTE C] 📄 Carregando tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)

        print("[AGENTE C] 📄 Carregando modelo LLM...")
        llm_pipeline = pipeline(
            task="text-generation",
            model=MODEL_ID,
            tokenizer=tokenizer,
            device_map=None,
            model_kwargs={"torch_dtype": torch.float32},
        )
        print("[AGENTE C] ✅ Modelo carregado")
    except Exception as e:
        print(f"[AGENTE C] ⚠️ Erro ao carregar LLM: {e}")
        LLM_AVAILABLE = False

# ----------------------
# Tratamentos IRIS
# ----------------------
TRATAMENTO_IRIS = {
    "IRIS1": [
        "Monitorar creatinina e SDMA a cada 6–12 meses",
        "Avaliar fatores de risco e comorbidades",
    ],
    "IRIS2": [
        "Introduzir dieta renal",
        "Monitorar pressão arterial",
        "Avaliar proteinúria (UPC)",
    ],
    "IRIS3": [
        "Dieta renal estrita",
        "Controle rigoroso de pressão arterial",
        "Considerar quelantes de fósforo",
    ],
    "IRIS4": [
        "Suporte clínico intensivo",
        "Controle sintomático",
        "Cuidados paliativos quando indicado",
    ],
}

# ----------------------
# 🔬 VALIDAÇÃO POR REGRAS (FALLBACK CIENTÍFICO)
# ----------------------
def validar_por_regras_iris(
    creat: Optional[float],
    sdma: Optional[float],
    estagio_b: Optional[str]
) -> Dict[str, Any]:
    """
    Validação baseada nas regras oficiais IRIS quando RAG não está disponível
    
    Esta função implementa a MESMA lógica que está na literatura IRIS oficial
    """
    
    if not estagio_b:
        return {
            "valido": None,
            "estagio_esperado": None,
            "mensagem": "Agent B não forneceu classificação"
        }
    
    if creat is None or sdma is None:
        return {
            "valido": None,
            "estagio_esperado": estagio_b,
            "mensagem": "Validação completa requer creatinina E SDMA"
        }
    
    # Classificar segundo tabela IRIS oficial
    stage_creat = None
    if creat < 1.6:
        stage_creat = 1
    elif 1.6 <= creat <= 2.8:
        stage_creat = 2
    elif 2.9 <= creat <= 5.0:
        stage_creat = 3
    else:
        stage_creat = 4
    
    stage_sdma = None
    if sdma < 18.0:
        stage_sdma = 1
    elif 18.0 <= sdma <= 25.0:
        stage_sdma = 2
    elif 26.0 <= sdma <= 38.0:
        stage_sdma = 3
    else:
        stage_sdma = 4
    
    discrepancia = abs(stage_creat - stage_sdma)
    
    # Extrair número do estágio B
    estagio_b_num = int(re.search(r'\d', estagio_b).group()) if re.search(r'\d', estagio_b) else None
    
    if discrepancia == 0:
        # Concordância perfeita
        if estagio_b_num == stage_creat:
            return {
                "valido": True,
                "estagio_esperado": f"IRIS{stage_creat}",
                "mensagem": f"✅ Validação confirmada: Creatinina e SDMA concordam em IRIS {stage_creat}",
                "regra_aplicada": "Concordância perfeita (tabela IRIS oficial)"
            }
        else:
            return {
                "valido": False,
                "estagio_esperado": f"IRIS{stage_creat}",
                "mensagem": f"❌ Agent B inferiu {estagio_b} mas creatinina ({creat}) e SDMA ({sdma}) indicam IRIS {stage_creat}",
                "regra_aplicada": "Discordância com tabela IRIS"
            }
    
    elif discrepancia == 1:
        # Usar o maior (regra IRIS)
        estagio_esperado = max(stage_creat, stage_sdma)
        if estagio_b_num == estagio_esperado:
            return {
                "valido": True,
                "estagio_esperado": f"IRIS{estagio_esperado}",
                "mensagem": f"✅ Validação confirmada: Discrepância de 1 estágio aceita, usando IRIS {estagio_esperado} (maior valor)",
                "regra_aplicada": "Regra IRIS: usar maior valor quando diff≤1"
            }
        else:
            return {
                "valido": False,
                "estagio_esperado": f"IRIS{estagio_esperado}",
                "mensagem": f"❌ Agent B inferiu {estagio_b} mas deveria ser IRIS {estagio_esperado} (maior entre creat={stage_creat} e sdma={stage_sdma})",
                "regra_aplicada": "Erro na aplicação da regra IRIS"
            }
    
    else:
        # Discrepância ≥2 - NÃO deve classificar
        if estagio_b_num is not None:
            return {
                "valido": False,
                "estagio_esperado": None,
                "mensagem": f"❌ Discrepância de {discrepancia} estágios: Agent B não deveria ter classificado! (Creat→IRIS{stage_creat}, SDMA→IRIS{stage_sdma})",
                "regra_aplicada": "Regra IRIS: não classificar quando diff≥2"
            }
        else:
            return {
                "valido": True,
                "estagio_esperado": None,
                "mensagem": f"✅ Agent B corretamente não classificou (discrepância de {discrepancia} estágios)",
                "regra_aplicada": "Regra IRIS: não classificar quando diff≥2"
            }

# ----------------------
# Normalização
# ----------------------
def normalize_stage(stage: Optional[str]) -> Optional[str]:
    """Normaliza strings de estágio IRIS"""
    if not stage:
        return None
    
    stage = str(stage).upper().replace(" ", "").replace("-", "")
    match = re.search(r'IRIS\s*[1-4]|STAGE\s*[1-4]|[1-4]', stage)
    if match:
        numero = re.search(r'[1-4]', match.group(0))
        if numero:
            return f"IRIS{numero.group(0)}"
    
    return None

# ----------------------
# LLM call
# ----------------------
def call_llm(prompt: str, max_new_tokens: int = 150) -> str:
    """Chama LLM se disponível"""
    if not LLM_AVAILABLE or llm_pipeline is None:
        return "LLM não disponível"
    
    try:
        out = llm_pipeline(
            prompt,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
        )
        txt = out[0].get("generated_text", out[0].get("text", ""))
        return txt.strip()
    except Exception as e:
        print(f"[AGENTE C] ⚠️ Erro ao chamar LLM: {e}")
        return "Erro ao processar com LLM"

# ----------------------
# Extração estágio RAG
# ----------------------
def extrair_estagio_rag(response: str) -> Optional[str]:
    """Extrai estágio da resposta LLM"""
    response_upper = response.upper()
    
    patterns = [
        r'IRIS\s*STAGE\s*[1-4]',
        r'IRIS\s*[1-4]',
        r'STAGE\s*[1-4]',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, response_upper)
        if match:
            numero = re.search(r'[1-4]', match.group(0))
            if numero:
                return f"IRIS{numero.group(0)}"
    
    if 'SEM CONFIANÇA' in response_upper or 'NOT SUFFICIENT' in response_upper:
        return None
        
    return None

# ----------------------
# 🔬 FUNÇÃO PRINCIPAL DE VALIDAÇÃO
# ----------------------
def gerar_recomendacao(
    inference: Dict[str, Any],
    clinical_data: Dict[str, Any],
    user_question: Optional[str] = ""
) -> Dict[str, Any]:

    print("\n" + "=" * 60)
    print("[AGENTE C] 🔬 VALIDADOR CIENTÍFICO")
    print("=" * 60)

    # ----------- Dados do Agent B -----------
    estagio_b = normalize_stage(inference.get("estagio") if inference else None)
    creat = clinical_data.get("creatinina")
    sdma = clinical_data.get("sdma")
    classificacao_b_valida = inference.get("classificacao_valida", True)
    motivo_invalido_b = inference.get("motivo_invalido")

    print(f"[AGENTE C] 📊 Estágio B: {estagio_b}")
    print(f"[AGENTE C] 📊 Classificação B válida: {classificacao_b_valida}")
    print(f"[AGENTE C] 📊 Creatinina: {creat}, SDMA: {sdma}")
    print(f"[AGENTE C] 🔧 RAG: {'ATIVO' if RAG_AVAILABLE else 'INDISPONÍVEL (usando regras científicas)'}")

    # ----------- CASO 3: Discrepância detectada pelo B -----------
    if not classificacao_b_valida:
        return {
            "estagio_rag": None,
            "estagio_b": estagio_b,
            "estagio_final": None,
            "valida_b": False,
            "inconsistencia": True,
            "resposta_clinica": f"⚠️ DISCREPÂNCIA DETECTADA:\n\n{motivo_invalido_b}\n\n📋 Ações:\n• Repetir exames\n• Verificar interferências pré-analíticas\n• Avaliar condições atípicas",
            "tratamento_recomendado": [],
            "num_docs": 0,
            "caso": 3,
            "mensagem": f"⚠️ DISCREPÂNCIA: {motivo_invalido_b}",
            "plano_terapeutico": [],
            "confianca": "INVÁLIDA"
        }

    # ----------- CASO 4: Sem dados para validar -----------
    if (estagio_b is None) and (creat is None or sdma is None):
        return {
            "estagio_rag": None,
            "estagio_final": None,
            "valida_b": None,
            "inconsistencia": False,
            "resposta_clinica": "Dados clínicos insuficientes para validação. Forneça creatinina e SDMA.",
            "tratamento_recomendado": [],
            "num_docs": 0,
            "caso": 4,
            "mensagem": "Dados insuficientes",
            "plano_terapeutico": [],
            "confianca": "BAIXA"
        }

    # ----------- VALIDAÇÃO: Tentar RAG primeiro -----------
    estagio_rag = None
    docs = []
    resposta_llm = ""
    validacao_rag = None
    
    if RAG_AVAILABLE and CHROMA_PATH:
        try:
            # Query RAG
            q_parts = ["feline chronic kidney disease IRIS guideline cat"]
            if creat is not None:
                q_parts.append(f"creatinine {creat}")
            if sdma is not None:
                q_parts.append(f"SDMA {sdma}")
            if user_question:
                q_parts.append(user_question)
            query = " ".join(q_parts)
            
            print(f"[AGENTE C] 🔎 Buscando na literatura: {query}")
            rag_result = rag_search(CHROMA_PATH, query, k=3, max_context_length_chars=2000)
            context = rag_result.get("context", "")
            docs = rag_result.get("docs", [])

            if context.strip() and LLM_AVAILABLE:
                prompt = f"""You are a veterinary clinical assistant specialized in FELINE medicine.

STRICT RULES:
- Species: CAT (FELINE) ONLY
- Use ONLY the context provided
- Determine IRIS stage (1-4) based on context
- If insufficient, reply "SEM CONFIANÇA"

Context:
{context}

Question:
Based on the context, what is the IRIS stage for a cat with:
- Creatinine: {creat} mg/dL
- SDMA: {sdma} µg/dL

Answer with:
1. IRIS stage number (1-4)
2. Brief clinical explanation

Answer:"""
                
                print("[AGENTE C] 🔹 Consultando LLM...")
                resposta_llm = call_llm(prompt, max_new_tokens=200)
                estagio_rag = extrair_estagio_rag(resposta_llm)
                print(f"[AGENTE C] 📌 Estágio RAG: {estagio_rag}")
                
        except Exception as e:
            print(f"[AGENTE C] ⚠️ Erro no RAG: {e}")

    # ----------- VALIDAÇÃO: Se RAG falhou, usar REGRAS -----------
    if estagio_rag is None and not RAG_AVAILABLE:
        print("[AGENTE C] 🔬 Validando por regras IRIS oficiais...")
        validacao_regras = validar_por_regras_iris(creat, sdma, estagio_b)
        
        valida_b = validacao_regras["valido"]
        estagio_esperado = validacao_regras["estagio_esperado"]
        
        resposta_texto = f"🔬 VALIDAÇÃO POR DIRETRIZES IRIS OFICIAIS\n\n"
        resposta_texto += validacao_regras["mensagem"] + "\n"
        resposta_texto += f"\n📚 Base: {validacao_regras['regra_aplicada']}\n"
        
        if valida_b:
            caso = 1
            estagio_final = estagio_b
            inconsistencia = False
        elif valida_b is False:
            caso = 3
            estagio_final = estagio_esperado
            inconsistencia = True
            resposta_texto += f"\n⚠️ RECOMENDAÇÃO: Revisar classificação (esperado: {estagio_esperado})\n"
        else:
            caso = 2
            estagio_final = estagio_esperado
            inconsistencia = False
    
    else:
        # ----------- VALIDAÇÃO: Comparar B vs RAG -----------
        valida_b = None
        inconsistencia = False
        caso = None
        resposta_texto = ""

        if estagio_b and estagio_rag:
            valida_b = (estagio_b == estagio_rag)
            if valida_b:
                caso = 1
                resposta_texto = f"✅ VALIDAÇÃO CIENTÍFICA CONFIRMADA\n\n"
                resposta_texto += f"Agent B: {estagio_b}\n"
                resposta_texto += f"Literatura IRIS: {estagio_rag}\n"
                resposta_texto += f"\n📚 Concordância entre inferência ontológica e literatura científica\n"
            else:
                caso = 3
                inconsistencia = True
                resposta_texto = f"❌ DISCREPÂNCIA CIENTÍFICA DETECTADA\n\n"
                resposta_texto += f"Agent B inferiu: {estagio_b}\n"
                resposta_texto += f"Literatura indica: {estagio_rag}\n"
                resposta_texto += f"\n⚠️ AÇÃO: Revisar dados clínicos e repetir avaliação\n"
        
        elif estagio_b and not estagio_rag:
            caso = 1
            valida_b = True
            resposta_texto = f"✅ Agent B classificou: {estagio_b}\n"
            resposta_texto += "📚 Literatura não forneceu estágio específico (validação inconclusiva)\n"
        
        elif not estagio_b and estagio_rag:
            caso = 2
            valida_b = None
            resposta_texto = f"📚 Literatura indica: {estagio_rag}\n"
            resposta_texto += "⚠️ Agent B não realizou inferência\n"
        
        else:
            caso = 4
            resposta_texto = "⚠️ Validação inconclusiva - dados insuficientes\n"

        if resposta_llm and caso != 4:
            resposta_texto += f"\n📄 Resumo da literatura:\n{resposta_llm}\n"

        estagio_final = estagio_rag or estagio_b

    # ----------- Tratamento -----------
    tratamento = TRATAMENTO_IRIS.get(estagio_final, [])

    if tratamento and not inconsistencia:
        resposta_texto += f"\n💊 Tratamento recomendado ({estagio_final}):\n"
        for idx, item in enumerate(tratamento, 1):
            resposta_texto += f"  {idx}. {item}\n"

    # ----------- Confiança -----------
    if valida_b is True:
        confianca = "ALTA"
    elif inconsistencia or valida_b is False:
        confianca = "INVÁLIDA"
    elif estagio_final:
        confianca = "MODERADA"
    else:
        confianca = "BAIXA"

    resultado = {
        "estagio_rag": estagio_rag,
        "estagio_b": estagio_b,
        "estagio_final": estagio_final,
        "valida_b": valida_b,
        "inconsistencia": inconsistencia,
        "resposta_clinica": resposta_texto.strip(),
        "tratamento_recomendado": tratamento,
        "num_docs": len(docs),
        "caso": caso,
        "mensagem": resposta_texto.strip(),
        "plano_terapeutico": tratamento,
        "confianca": confianca
    }

    print(f"[AGENTE C] ✅ Validação concluída - CASO {caso}")
    print(f"[AGENTE C] 🎯 Validação: {'✅ Confirmada' if valida_b else '❌ Reprovada' if valida_b is False else '⚠️ Inconclusiva'}")
    if inconsistencia:
        print(f"[AGENTE C] ⚠️ Inconsistência: B={estagio_b} vs RAG/Regras={estagio_rag or estagio_esperado}")

    return resultado

# ----------------------
# Interface pública
# ----------------------
def agent_c_answer(
    resultado_b: Dict[str, Any],
    clinical_data: Dict[str, Any],
    pergunta: Optional[str] = ""
) -> Dict[str, Any]:
    """
    Interface pública do Agente C - VALIDADOR CIENTÍFICO
    
    Prioridade:
    1. Validação por RAG (literatura científica)
    2. Validação por regras IRIS oficiais (se RAG indisponível)
    3. NUNCA aceita Agent B sem validar
    """
    return gerar_recomendacao(
        inference=resultado_b,
        clinical_data=clinical_data,
        user_question=pergunta or ""
    )