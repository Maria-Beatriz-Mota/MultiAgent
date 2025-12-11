# ==========================================================
# AGENTE C – VALIDADOR CIENTÍFICO (RAG + Regras)
# Interface pública: agent_c_answer(...)
# ==========================================================

import re
import csv
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# ----------------------
# Imports condicionais com fallback
# ----------------------
RAG_AVAILABLE = False

try:
    from .agent_c_db import rag_search, CHROMA_PATH
    RAG_AVAILABLE = True
    print("[AGENTE C] RAG disponível")
except ImportError as e:
    print(f"[AGENTE C] RAG não disponível: {e}")
    print(f"[AGENTE C] Instale: pip install langchain langchain-chroma chromadb")
    CHROMA_PATH = None



# ----------------------
# Configuração do banco de dados CSV
# ----------------------
CSV_DATABASE_PATH = Path("Agent_C/validations_database.csv")
CSV_HEADERS = [
    "timestamp",
    "creatinina",
    "sdma",
    "estagio_b",
    "estagio_rag",
    "estagio_final",
    "validacao",
    "caso",
    "confianca",
    "pergunta_usuario",
    "resposta_fornecida",
    "num_docs_rag",
    "regra_aplicada"
]

def salvar_validacao_csv(resultado: Dict[str, Any], dados_clinicos: Dict[str, Any], user_question: str = ""):
    """
    Salva validação bem-sucedida no banco de dados CSV
    
    Args:
        resultado: Resultado da validação do Agente C
        dados_clinicos: Dados clínicos do paciente
        user_question: Pergunta do usuário
    """
    
    # Só salvar se validação foi bem-sucedida (casos 1 e 2)
    caso = resultado.get("caso")
    valida_b = resultado.get("valida_b")
    
    if caso not in [1, 2] or valida_b is False:
        print("[AGENTE C] Validação não salva (não confirmada ou com inconsistência)")
        return
    
    try:
        # Criar diretório se não existir
        CSV_DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        # Verificar se arquivo existe para decidir se escreve header
        file_exists = CSV_DATABASE_PATH.exists()
        
        # Preparar dados para salvar
        dados_validacao = resultado.get("dados_validacao", {})
        resposta_pergunta = resultado.get("resposta_pergunta", "")
        
        row_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "creatinina": dados_validacao.get("creatinina", ""),
            "sdma": dados_validacao.get("sdma", ""),
            "estagio_b": dados_validacao.get("estagio_b", ""),
            "estagio_rag": dados_validacao.get("estagio_rag", ""),
            "estagio_final": resultado.get("estagio_final", ""),
            "validacao": "Confirmada" if valida_b is True else "Inconclusiva" if valida_b is None else "Reprovada",
            "caso": caso,
            "confianca": resultado.get("confianca", ""),
            "pergunta_usuario": user_question[:200] if user_question else "",  # Limitar tamanho
            "resposta_fornecida": resposta_pergunta[:300] if resposta_pergunta else "",  # Limitar tamanho
            "num_docs_rag": resultado.get("num_docs", 0),
            "regra_aplicada": "RAG" if resultado.get("estagio_rag") else "Regras IRIS"
        }
        
        # Escrever no CSV
        with open(CSV_DATABASE_PATH, mode='a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=CSV_HEADERS)
            
            # Escrever header se arquivo é novo
            if not file_exists:
                writer.writeheader()
                print(f"[AGENTE C] Arquivo CSV criado: {CSV_DATABASE_PATH}")
            
            writer.writerow(row_data)
            print(f"[AGENTE C] Validação salva no banco de dados CSV")
            
    except Exception as e:
        print(f" Erro ao salvar no CSV: {e}")

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
# 🔬 VALIDAÇÃO DE SUBETÁGIOS (AP E HT)
# ----------------------
def validar_subestagios_iris(
    upc: Optional[float],
    pressao: Optional[float],
    subestagio_ap_b: Optional[str],
    subestagio_ht_b: Optional[str]
) -> Dict[str, Any]:
    """
    Valida os subetágios AP (proteinúria) e HT (hipertensão) do Agente B
    
    Returns:
        {
            "ap_valido": bool,
            "ht_valido": bool,
            "ap_esperado": str,
            "ht_esperado": str,
            "mensagem": str
        }
    """
    resultado = {
        "ap_valido": None,
        "ht_valido": None,
        "ap_esperado": None,
        "ht_esperado": None,
        "mensagem": ""
    }
    
    # Validar AP (proteinúria)
    if upc is not None:
        if upc < 0.2:
            ap_esperado = "AP0"
        elif 0.2 <= upc <= 0.4:
            ap_esperado = "AP1"
        else:
            ap_esperado = "AP2"
        
        resultado["ap_esperado"] = ap_esperado
        resultado["ap_valido"] = (subestagio_ap_b == ap_esperado)
        
        if not resultado["ap_valido"] and subestagio_ap_b:
            resultado["mensagem"] += f" Proteinúria: B={subestagio_ap_b} vs Esperado={ap_esperado}. "
    
    # Validar HT (hipertensão)
    if pressao is not None:
        if pressao < 140:
            ht_esperado = "HT0"
        elif 140 <= pressao < 160:
            ht_esperado = "HT1"
        elif 160 <= pressao < 180:
            ht_esperado = "HT2"
        else:
            ht_esperado = "HT3"
        
        resultado["ht_esperado"] = ht_esperado
        resultado["ht_valido"] = (subestagio_ht_b == ht_esperado)
        
        if not resultado["ht_valido"] and subestagio_ht_b:
            resultado["mensagem"] += f" Hipertensão: B={subestagio_ht_b} vs Esperado={ht_esperado}. "
    
    if not resultado["mensagem"]:
        resultado["mensagem"] = " Subetágios validados"
    
    return resultado

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
                "mensagem": f" Validação confirmada: Creatinina e SDMA concordam em IRIS {stage_creat}",
                "regra_aplicada": "Concordância perfeita (tabela IRIS oficial)"
            }
        else:
            return {
                "valido": False,
                "estagio_esperado": f"IRIS{stage_creat}",
                "mensagem": f" Agent B inferiu {estagio_b} mas creatinina ({creat}) e SDMA ({sdma}) indicam IRIS {stage_creat}",
                "regra_aplicada": "Discordância com tabela IRIS"
            }
    
    elif discrepancia == 1:
        # Usar o maior (regra IRIS)
        estagio_esperado = max(stage_creat, stage_sdma)
        if estagio_b_num == estagio_esperado:
            return {
                "valido": True,
                "estagio_esperado": f"IRIS{estagio_esperado}",
                "mensagem": f" Validação confirmada: Discrepância de 1 estágio aceita, usando IRIS {estagio_esperado} (maior valor)",
                "regra_aplicada": "Regra IRIS: usar maior valor quando diff<=1"
            }
        else:
            return {
                "valido": False,
                "estagio_esperado": f"IRIS{estagio_esperado}",
                "mensagem": f" Agent B inferiu {estagio_b} mas deveria ser IRIS {estagio_esperado} (maior entre creat={stage_creat} e sdma={stage_sdma})",
                "regra_aplicada": "Erro na aplicação da regra IRIS"
            }
    
    else:
        # Discrepância ≥2 - NÃO deve classificar
        if estagio_b_num is not None:
            return {
                "valido": False,
                "estagio_esperado": None,
                "mensagem": f" Discrepância de {discrepancia} estágios: Agent B não deveria ter classificado! (Creat→IRIS{stage_creat}, SDMA→IRIS{stage_sdma})",
                "regra_aplicada": "Regra IRIS: não classificar quando diff≥2"
            }
        else:
            return {
                "valido": True,
                "estagio_esperado": None,
                "mensagem": f" Agent B corretamente não classificou (discrepância de {discrepancia} estágios)",
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
# Resposta de perguntas específicas via RAG
# ----------------------
def responder_pergunta_usuario(user_question: str, context_rag: str, docs: list) -> Optional[str]:
    """
    Responde perguntas específicas do usuário baseado no contexto RAG
    Usa LLM quando disponível para gerar respostas mais precisas
    
    Args:
        user_question: Pergunta do usuário
        context_rag: Contexto recuperado do RAG
        docs: Documentos encontrados
    
    Returns:
        Resposta baseada na literatura ou None se não encontrado
    """
    if not user_question or len(user_question.strip()) < 5:
        return None
    
    # Se não há documentos, não pode responder
    if not context_rag or len(docs) == 0:
        return None
    
    print(f"[AGENTE C] Tentando responder pergunta do usuário...")
    
    # Tentar usar LLM se disponível (mais preciso)
    try:
        import os
        from langchain_groq import ChatGroq
        from langchain_core.messages import HumanMessage
        
        if os.environ.get("GROQ_API_KEY"):
            llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.3)
            
            prompt = f"""Você é um especialista veterinário em doença renal crônica felina.

CONTEXTO DA LITERATURA IRIS:
{context_rag[:2000]}

PERGUNTA DO VETERINÁRIO:
{user_question}

INSTRUÇÕES:
- Responda com base no contexto fornecido
- Se a informação específica não estiver no contexto, forneça orientação geral baseada em conhecimento veterinário
- Para perguntas sobre raças específicas: as diretrizes IRIS são geralmente aplicadas igualmente a todas as raças, salvo exceções documentadas
- Seja conciso e objetivo (2-4 sentenças)
- Use termos técnicos veterinários
- RESPONDA SEMPRE EM PORTUGUÊS BRASILEIRO

Resposta:"""
            
            response = llm.invoke([HumanMessage(content=prompt)])
            resposta_texto = response.content.strip()
            
            # Qualquer resposta válida do LLM é aceita
            if len(resposta_texto) > 20:
                print(f"[AGENTE C]  Resposta gerada com LLM")
                return f" {resposta_texto}"
    
    except Exception as e:
        print(f"[AGENTE C]  LLM não disponível para responder: {str(e)[:50]}")
    
    # Fallback: busca por palavras-chave (método antigo)
    keywords_medicas = [
        'tratamento', 'treatment', 'therapy', 'terapia',
        'dieta', 'diet', 'alimentação', 'nutrition',
        'sintoma', 'symptom', 'sinal', 'sign',
        'prognóstico', 'prognosis', 'expectativa',
        'medicação', 'medication', 'drug', 'remédio',
        'monitoramento', 'monitoring', 'follow-up',
        'comorbidade', 'comorbidity',
        'risco', 'risk', 'complicação', 'complication',
        'pressão', 'pressure', 'hipertensão', 'hypertension',
        'proteinúria', 'proteinuria', 'upc',
        'fósforo', 'phosphorus', 'phosphate',
        'raça', 'breed', 'birmanês', 'birmanese', 'persa', 'persian'
    ]
    
    question_lower = user_question.lower()
    is_medical_question = any(keyword in question_lower for keyword in keywords_medicas)
    
    if not is_medical_question:
        return None
    
    # Buscar resposta no contexto RAG
    sentences = context_rag.split('.')
    relevant_sentences = []
    
    for keyword in keywords_medicas:
        if keyword in question_lower:
            for sentence in sentences:
                if keyword in sentence.lower() and len(sentence.strip()) > 20:
                    relevant_sentences.append(sentence.strip())
    
    if relevant_sentences:
        unique_sentences = list(dict.fromkeys(relevant_sentences))[:3]
        resposta = '. '.join(unique_sentences)
        if resposta:
            print(f"[AGENTE C]  Resposta encontrada por palavra-chave")
            return f" Baseado na literatura IRIS:\n\n{resposta}."
    
    print(f"[AGENTE C]  Pergunta fora do escopo dos documentos indexados")
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
    print("[AGENTE C] VALIDADOR CIENTÍFICO")
    print("=" * 60)

    # ----------- Dados do Agent B -----------
    estagio_b = normalize_stage(inference.get("estagio") if inference else None)
    subestagio_ap_b = inference.get("subestagio_ap")
    subestagio_ht_b = inference.get("subestagio_ht")
    creat = clinical_data.get("creatinina")
    sdma = clinical_data.get("sdma")
    upc = clinical_data.get("upc") or clinical_data.get("proteinuria")
    pressao = clinical_data.get("pressao") or clinical_data.get("pressao_arterial")
    classificacao_b_valida = inference.get("classificacao_valida", True)
    motivo_invalido_b = inference.get("motivo_invalido")

    print(f"[AGENTE C]  Estágio B: {estagio_b}")
    if subestagio_ap_b or subestagio_ht_b:
        print(f"[AGENTE C]  Subetágios B: AP={subestagio_ap_b}, HT={subestagio_ht_b}")
    print(f"[AGENTE C]  Classificação B válida: {classificacao_b_valida}")
    print(f"[AGENTE C]  Creatinina: {creat}, SDMA: {sdma}")
    if upc is not None or pressao is not None:
        print(f"[AGENTE C]  UPC: {upc}, Pressão: {pressao}")
    print(f"[AGENTE C]  RAG: {'ATIVO' if RAG_AVAILABLE else 'INDISPONÍVEL (usando regras científicas)'}")
    
    # ----------- VALIDAR SUBETÁGIOS -----------
    validacao_subestagios = validar_subestagios_iris(upc, pressao, subestagio_ap_b, subestagio_ht_b)
    print(f"[AGENTE C]  {validacao_subestagios['mensagem']}")

    # ----------- CASO 3: Discrepância detectada pelo B -----------
    if not classificacao_b_valida:
        return {
            "estagio_rag": None,
            "estagio_b": estagio_b,
            "estagio_final": None,
            "valida_b": False,
            "inconsistencia": True,
            "resposta_clinica": f" DISCREPÂNCIA DETECTADA:\n\n{motivo_invalido_b}\n\n📋 Ações:\n• Repetir exames\n• Verificar interferências pré-analíticas\n• Avaliar condições atípicas",
            "tratamento_recomendado": [],
            "num_docs": 0,
            "caso": 3,
            "mensagem": f" DISCREPÂNCIA: {motivo_invalido_b}",
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
    context_rag = ""
    resposta_pergunta = None
    
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
            
            print(f"[AGENTE C]  Buscando na literatura: {query}")
            rag_result = rag_search(CHROMA_PATH, query, k=5, max_context_length_chars=3000)
            context_rag = rag_result.get("context", "")
            docs = rag_result.get("docs", [])
            
            # Tentar responder pergunta específica do usuário
            if user_question and context_rag:
                resposta_pergunta = responder_pergunta_usuario(user_question, context_rag, docs)
            
            # Extrair estágio do contexto RAG (busca simples por padrões)
            if context_rag:
                print(f"[AGENTE C] Contexto RAG recuperado ({len(context_rag)} chars)")
                # Tentar identificar estágio mencionado no contexto
                context_upper = context_rag.upper()
                for i in range(1, 5):
                    if f"STAGE {i}" in context_upper or f"IRIS {i}" in context_upper:
                        if creat is not None:
                            # Verificar se os valores batem com a descrição
                            if (i == 1 and creat < 1.6) or \
                               (i == 2 and 1.6 <= creat <= 2.8) or \
                               (i == 3 and 2.9 <= creat <= 5.0) or \
                               (i == 4 and creat > 5.0):
                                estagio_rag = f"IRIS{i}"
                                print(f"[AGENTE C]  Estágio extraído do RAG: {estagio_rag}")
                                break
            elif user_question:
                # RAG não retornou documentos
                print(f"[AGENTE C] Nenhum documento encontrado para a pergunta")
                resposta_pergunta = " Não há informações disponíveis na base de conhecimento indexada para responder esta pergunta. Recomenda-se consultar a literatura IRIS oficial ou indexar mais documentos."
                
        except Exception as e:
            print(f"[AGENTE C] Erro no RAG: {e}")

    # ----------- VALIDAÇÃO: SEMPRE usar REGRAS IRIS (não comparação textual RAG) -----------
    # LÓGICA CORRIGIDA: RAG serve para Q&A, NÃO para validar estágios
    # Validação deve ser feita contra as REGRAS numéricas oficiais IRIS
    print("[AGENTE C] Validando por regras IRIS oficiais...")
    validacao_regras = validar_por_regras_iris(creat, sdma, estagio_b)
    
    valida_b = validacao_regras["valido"]
    estagio_esperado = validacao_regras["estagio_esperado"]
    
    # Construir mensagem detalhada
    resposta_texto = f"ANÁLISE CLÍNICA - DOENÇA RENAL CRÔNICA FELINA\n\n"
    resposta_texto += f"BIOMARCADORES OBSERVADOS:\n"
    resposta_texto += f"• Creatinina: {creat} mg/dL\n"
    resposta_texto += f"• SDMA: {sdma} µg/dL\n"
    if upc is not None:
        resposta_texto += f"• UPC: {upc}\n"
    if pressao is not None:
        resposta_texto += f"• Pressão Arterial: {pressao} mmHg\n"
    resposta_texto += f"\n"
    
    # Adicionar subetágios se disponíveis
    if subestagio_ap_b or subestagio_ht_b:
        resposta_texto += f"SUBETÁGIOS IRIS:\n"
        if subestagio_ap_b:
            ap_desc = {"AP0": "não proteinúrico", "AP1": "borderline proteinúrico", "AP2": "proteinúrico"}.get(subestagio_ap_b, subestagio_ap_b)
            resposta_texto += f"• {subestagio_ap_b}: {ap_desc}\n"
        if subestagio_ht_b:
            ht_desc = {"HT0": "risco mínimo", "HT1": "risco baixo", "HT2": "risco moderado", "HT3": "risco grave"}.get(subestagio_ht_b, subestagio_ht_b)
            resposta_texto += f"• {subestagio_ht_b}: {ht_desc}\n"
        resposta_texto += f"\n"
    
    resposta_texto += f"VALIDAÇÃO: {validacao_regras['mensagem']}\n\n"
    resposta_texto += f"BASE CIENTÍFICA: {validacao_regras['regra_aplicada']}\n"
    
    # Adicionar resposta do RAG à pergunta do usuário (se houver)
    if resposta_pergunta:
        resposta_texto += f"\n\nRESPOSTA À PERGUNTA:\n{resposta_pergunta}\n"
    
    # Adicionar referências bibliográficas dos documentos utilizados
    if docs and len(docs) > 0:
        resposta_texto += "\n\n REFERÊNCIAS BIBLIOGRÁFICAS:\n"
        resposta_texto += "-" * 70 + "\n"
        referencias_unicas = set()
        for i, doc in enumerate(docs, 1):
            metadata = getattr(doc, 'metadata', {})
            source = metadata.get('source', 'Documento desconhecido')
            page = metadata.get('page', None)
            
            # Extrair apenas o nome do arquivo
            if source:
                source_name = Path(source).name if isinstance(source, str) else str(source)
            else:
                source_name = f"Documento {i}"
            
            # Criar referência única
            if page is not None:
                ref = f"[{i}] {source_name}, página {page + 1}"
            else:
                ref = f"[{i}] {source_name}"
            
            if ref not in referencias_unicas:
                referencias_unicas.add(ref)
                resposta_texto += f"  {ref}\n"
        resposta_texto += "-" * 70 + "\n"
    
    if valida_b:
        caso = 1
        estagio_final = estagio_b
        inconsistencia = False
        resposta_texto += f"\nCONCLUSÃO: A inferência ontológica está correta e validada pelas diretrizes IRIS.\n"
    elif valida_b is False:
        caso = 3
        estagio_final = estagio_esperado
        inconsistencia = True
        resposta_texto += f"\n ATENÇÃO: Discrepância identificada. Recomenda-se revisar os dados e repetir exames laboratoriais.\n"
    else:
        caso = 2
        estagio_final = estagio_esperado
        inconsistencia = False
        resposta_texto += f"\nNOTA: Classificação baseada nos biomarcadores disponíveis.\n"

    # ----------- Tratamento -----------
    tratamento = TRATAMENTO_IRIS.get(estagio_final, [])

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
        "subestagio_ap": subestagio_ap_b,  # NOVO: Propagar subetágios
        "subestagio_ht": subestagio_ht_b,  # NOVO: Propagar subetágios
        "valida_b": valida_b,
        "inconsistencia": inconsistencia,
        "resposta_clinica": resposta_texto.strip(),
        "tratamento_recomendado": tratamento,
        "num_docs": len(docs),
        "caso": caso,
        "mensagem": resposta_texto.strip(),
        "plano_terapeutico": tratamento,
        "confianca": confianca,
        "context_rag": context_rag if 'context_rag' in locals() else "",
        "resposta_pergunta": resposta_pergunta if 'resposta_pergunta' in locals() else None,
        "dados_validacao": {
            "creatinina": creat,
            "sdma": sdma,
            "estagio_b": estagio_b,
            "estagio_rag": estagio_rag
        }
    }

    print(f"[AGENTE C]  Validação concluída - CASO {caso}, Estágio: {estagio_final}")
    if subestagio_ap_b or subestagio_ht_b:
        print(f"[AGENTE C] Subetágios: AP={subestagio_ap_b}, HT={subestagio_ht_b}")
    print(f"[AGENTE C] Validação: {' Confirmada' if valida_b else '❌ Reprovada' if valida_b is False else '⚠️ Inconclusiva'}")
    if inconsistencia:
        estagio_comparacao = estagio_rag if estagio_rag else (estagio_esperado if 'estagio_esperado' in locals() else 'N/A')
        print(f"[AGENTE C]  Inconsistência: B={estagio_b} vs RAG/Regras={estagio_comparacao}")

    # Salvar validação no CSV se foi bem-sucedida
    if valida_b is not False and caso in [1, 2]:
        salvar_validacao_csv(resultado, clinical_data, user_question)

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