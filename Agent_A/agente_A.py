"""
Agente A – Interpretação Clínica e Orquestração (CORRIGIDO)
-----------------------------------------------------------
Fluxo: A → B → C → A

Responsabilidades:
1. Receber formulário + texto livre
2. Normalizar dados clínicos
3. Enviar dados ao Agente B
4. Enviar resultado do B ao Agente C
5. Consolidar resposta final ao veterinário (CORRIGIDO)
"""

import os
from typing import Dict, Any, Optional

# =====================================================================
# CONFIGURAÇÃO LLM - MÚLTIPLAS OPÇÕES COM FALLBACK
# =====================================================================

llm = None
LLM_DISPONIVEL = False
LLM_PROVIDER = None

# Tentar múltiplos provedores em ordem de preferência
providers_to_try = []

# 1. OpenAI (melhor qualidade, requer API key)
if os.environ.get("OPENAI_API_KEY"):
    providers_to_try.append(("openai", "OpenAI GPT-3.5"))

# 2. Groq (rápido e gratuito, requer API key)
if os.environ.get("GROQ_API_KEY"):
    providers_to_try.append(("groq", "Groq gpt-oss-120b"))

# 3. HuggingFace (gratuito, menos confiável)
if os.environ.get("HUGGINGFACEHUB_API_TOKEN"):
    providers_to_try.append(("huggingface", "HuggingFace"))

# Tentar cada provedor
for provider, name in providers_to_try:
    try:
        if provider == "openai":
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)
            LLM_PROVIDER = "OpenAI"
            
        elif provider == "groq":
            from langchain_groq import ChatGroq
            llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.3)
            LLM_PROVIDER = "Groq"
            
        elif provider == "huggingface":
            from langchain_huggingface import HuggingFaceEndpoint
            llm = HuggingFaceEndpoint(
                repo_id="google/flan-t5-large",
                temperature=0.2,
                max_new_tokens=512,
                huggingfacehub_api_token=os.environ.get("HUGGINGFACEHUB_API_TOKEN")
            )
            LLM_PROVIDER = "HuggingFace"
        
        # Testar se funciona
        LLM_DISPONIVEL = True
        print(f"[AGENTE A] LLM {LLM_PROVIDER} configurado")
        break
        
    except Exception as e:
        print(f"[AGENTE A] {name} não disponível: {e}")
        continue

if not LLM_DISPONIVEL:
    print("[AGENTE A] Nenhum LLM disponível - usando modo texto direto")
    print("[AGENTE A] Configure: OPENAI_API_KEY, GROQ_API_KEY ou HUGGINGFACEHUB_API_TOKEN")

def gerar_explicacao_clinica(
    resultado_b: Dict[str, Any],
    resultado_c: Dict[str, Any],
    dados_clinicos: Dict[str, Any]
) -> str:
    """
    ⚠️ FUNÇÃO DESATIVADA - NÃO USAR
    
    MOTIVO: LLM pode distorcer informações médicas críticas ao "humanizar" texto.
    O Agente C é o validador científico oficial - sua resposta já está correta
    e validada por RAG + regras IRIS. Não deve ser alterada.
    
    DECISÃO DE ARQUITETURA:
    - Agente C = Validador científico (resposta autoritativa)
    - LLM = Pode alucinar/modificar dados médicos (RISCO)
    - Solução = Usar resposta original de C sem modificações
    
    Args:
        resultado_b: Resultado da inferência ontológica
        resultado_c: Resultado da validação (RAG + regras)
        dados_clinicos: Dados clínicos do paciente
    
    Returns:
        Texto organizado e humanizado baseado na validação de C
    """
    
    # Pegar a mensagem de validação do Agente C
    mensagem_c = resultado_c.get("resposta_clinica", "")
    estagio_final = resultado_c.get("estagio_final")
    valida_b = resultado_c.get("valida_b")
    
    # Se não tem LLM, retornar direto a mensagem do C
    if not LLM_DISPONIVEL or llm is None:
        print("[AGENTE A] ⚠️ LLM não disponível, usando texto direto do Agente C")
        return mensagem_c
    
    # Construir prompt para humanizar o texto
    prompt = f"""Você é um especialista em comunicação veterinária.

Sua tarefa é reescrever a avaliação clínica a seguir em um tom claro, profissional e empático para um veterinário.

AVALIAÇÃO ORIGINAL DO SISTEMA DE VALIDAÇÃO:
{mensagem_c}

INSTRUÇÕES:
- Mantenha todas as informações médicas precisas
- Faça o texto fluir naturalmente em PORTUGUÊS BRASILEIRO
- Use linguagem veterinária profissional
- Seja conciso (3-4 sentenças)
- Mantenha a conclusão do estágio IRIS
- RESPONDA SEMPRE EM PORTUGUÊS

Avaliação reescrita em português:"""
    
    try:
        print(f"[AGENTE A] 🧠 Humanizando texto com LLM ({LLM_PROVIDER})...")
        
        # Diferentes métodos de invocação por provider
        if LLM_PROVIDER in ["OpenAI", "Groq"]:
            from langchain_core.messages import HumanMessage
            resposta = llm.invoke([HumanMessage(content=prompt)])
            texto = resposta.content if hasattr(resposta, 'content') else str(resposta)
        else:
            resposta = llm.invoke(prompt)
            texto = resposta if isinstance(resposta, str) else str(resposta)
        
        print("[AGENTE A] ✅ Texto humanizado com sucesso")
        return texto.strip()
        
    except Exception as e:
        print(f"[AGENTE A] ⚠️ Erro ao humanizar com LLM: {str(e)[:100]}")
        # Fallback: retornar texto do C sem modificação
        return mensagem_c


def _gerar_explicacao_basica(
    resultado_b: Dict[str, Any],
    resultado_c: Dict[str, Any],
    dados_clinicos: Dict[str, Any]
) -> str:
    """Fallback: retorna diretamente a mensagem do Agente C"""
    return resultado_c.get("resposta_clinica", "Validação não disponível")


# =====================================================================
# HELPERS
# =====================================================================

def _to_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        v = value.strip().replace(",", ".")
        try:
            return float(v)
        except:
            return None
    return None


def _erro(msg: str) -> Dict[str, Any]:
    return {
        "estagio_final": None,
        "mensagem": msg,
        "plano_terapeutico": [],
        "alertas": [],
        "confianca": "BAIXA"
    }


# =====================================================================
# PROCESSAMENTO DE ENTRADA
# =====================================================================

def processar_input_usuario(
    formulario: Optional[Dict[str, Any]] = None,
    texto_livre: Optional[str] = ""
) -> Dict[str, Any]:

    formulario = formulario or {}

    dados = {
        "nome": formulario.get("nome"),
        "sexo": formulario.get("sexo"),
        "raca": formulario.get("raca"),
        "creatinina": _to_float(formulario.get("creatinina")),
        "sdma": _to_float(formulario.get("sdma")),
        "idade": _to_float(formulario.get("idade")),
        "peso": _to_float(formulario.get("peso")),
        "pressao_arterial": _to_float(formulario.get("pressao_arterial") or formulario.get("pressao")),
        "upc": _to_float(formulario.get("upc")),
        "sintomas": formulario.get("sintomas", ""),
        "comorbidades": formulario.get("comorbidades", ""),
        "question": (texto_livre or "").strip()
    }

    return dados


# =====================================================================
# CONSOLIDAÇÃO FINAL (B + C) - CORRIGIDA
# =====================================================================

def consolidar_resultados(
    resultado_b: Dict[str, Any],
    resultado_c: Dict[str, Any],
    dados_clinicos: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Consolida resultados de B e C respeitando os 4 casos do Agente C
    Gera explicação clínica usando LLM
    
    Casos:
    1. B e RAG concordam → confiança ALTA
    2. B não inferiu, RAG tem info → confiança MODERADA  
    3. Discrepância entre B e RAG → INCONSISTÊNCIA (pedir nova avaliação)
    4. Sem dados suficientes → BAIXA confiança
    """
    
    dados_clinicos = dados_clinicos or {}
    
    # 🔥 PRIORIZAR campos do Agente C (ele já consolidou tudo)
    estagio_final = resultado_c.get("estagio_final")
    caso = resultado_c.get("caso")
    inconsistencia = resultado_c.get("inconsistencia", False)
    
    alertas = []
    
    # =====================================================================
    # CASO 3: INCONSISTÊNCIA/DISCREPÂNCIA - ERRO CRÍTICO
    # =====================================================================
    if caso == 3 or inconsistencia:
        return {
            "estagio_final": None,
            "mensagem": resultado_c.get("resposta_clinica", "Discrepância detectada nos biomarcadores."),
            "plano_terapeutico": [],
            "alertas": [
                "⚠️ INCONSISTÊNCIA CRÍTICA: Valores de creatinina e SDMA apresentam discrepância significativa.",
                "📋 Ação requerida: Repetir exames laboratoriais antes de prosseguir com o tratamento."
            ],
            "confianca": "INVÁLIDA",
            "caso": caso
        }
    
    # =====================================================================
    # CASO 4: DADOS INSUFICIENTES
    # =====================================================================
    if caso == 4 or not estagio_final:
        return {
            "estagio_final": None,
            "mensagem": resultado_c.get(
                "resposta_clinica",
                "Informações insuficientes para determinar o estágio IRIS."
            ),
            "plano_terapeutico": [],
            "alertas": [
                "⚠️ Dados clínicos insuficientes.",
                "Por favor, forneça valores de creatinina e/ou SDMA."
            ],
            "confianca": "BAIXA",
            "caso": caso
        }
    
    # =====================================================================
    # CASOS 1 e 2: CLASSIFICAÇÃO VÁLIDA
    # =====================================================================
    
    # USAR DIRETAMENTE A RESPOSTA DO AGENTE C (JÁ VALIDADA)
    # O Agente C é o validador científico - sua resposta não deve ser alterada
    # LLM pode introduzir erros ou "alucinar" informações médicas
    mensagem = resultado_c.get("resposta_clinica", "")
    
    print("[AGENTE A] ✅ Usando resposta validada do Agente C (sem LLM)")
    print("[AGENTE A] 📋 Resposta científica preservada para garantir precisão")
    
    # Plano terapêutico
    plano = resultado_c.get("tratamento_recomendado", [])
    
    # Confiança baseada na validação
    valida_b = resultado_c.get("valida_b")
    if valida_b is True:
        confianca = "ALTA"
        if caso == 1:
            alertas.append("✅ Inferência ontológica validada pela literatura científica.")
    elif valida_b is None:
        confianca = "MODERADA"
        if caso == 2:
            alertas.append("💡 Classificação baseada na literatura (ontologia não inferiu estágio).")
    else:
        confianca = "MODERADA"
    
    return {
        "estagio_final": estagio_final,
        "subestagio_ap": resultado_c.get("subestagio_ap"),  # NOVO: Propagar subetágios
        "subestagio_ht": resultado_c.get("subestagio_ht"),  # NOVO: Propagar subetágios
        "mensagem": mensagem,
        "plano_terapeutico": plano,
        "alertas": alertas,
        "confianca": confianca,
        "caso": caso,
        
        # Metadados úteis
        "valida_b": valida_b,
        "num_docs_rag": resultado_c.get("num_docs", 0),
    }


# =====================================================================
# FORMATAÇÃO FINAL PARA O VETERINÁRIO - CORRIGIDA
# =====================================================================

def formatar_resposta_final(resultado: Dict[str, Any], dados_clinicos: Dict[str, Any] = None) -> str:
    """
    Formata a resposta final para apresentação ao veterinário
    """
    
    resposta = []
    resposta.append("🩺 Avaliação Clínica – Doença Renal Crônica Felina")
    resposta.append("=" * 70)
    
    # Adicionar informações do paciente se disponíveis
    if dados_clinicos:
        info_paciente = []
        if dados_clinicos.get("nome"):
            info_paciente.append(f"Paciente: {dados_clinicos['nome']}")
        if dados_clinicos.get("sexo"):
            sexo_desc = "Macho" if dados_clinicos['sexo'] == "M" else "Fêmea" if dados_clinicos['sexo'] == "F" else dados_clinicos['sexo']
            info_paciente.append(f"Sexo: {sexo_desc}")
        if dados_clinicos.get("raca"):
            info_paciente.append(f"Raça: {dados_clinicos['raca']}")
        if dados_clinicos.get("idade"):
            info_paciente.append(f"Idade: {dados_clinicos['idade']} anos")
        if dados_clinicos.get("peso"):
            info_paciente.append(f"Peso: {dados_clinicos['peso']} kg")
        
        if info_paciente:
            resposta.append("")
            resposta.append("📋 Dados do Paciente:")
            resposta.append("-" * 70)
            resposta.append("  • " + " | ".join(info_paciente))
            resposta.append("")
    
    # 🔥 CASO 3: Inconsistência - destaque especial
    if resultado.get("confianca") == "INVÁLIDA":
        resposta.append("")
        resposta.append("⚠️ " + "="*66)
        resposta.append("⚠️  ATENÇÃO: VALORES LABORATORIAIS INCONSISTENTES")
        resposta.append("⚠️ " + "="*66)
        resposta.append("")
        resposta.append(resultado.get("mensagem", ""))
        resposta.append("")
        
        if resultado.get("alertas"):
            resposta.append("📋 Ações Recomendadas:")
            for a in resultado["alertas"]:
                resposta.append(f"   {a}")
        
        resposta.append("")
        resposta.append("=" * 70)
        return "\n".join(resposta)
    
    # Estágio IRIS
    estagio = resultado.get("estagio_final")
    subestagio_ap = resultado.get("subestagio_ap")
    subestagio_ht = resultado.get("subestagio_ht")
    
    if estagio:
        linha_estagio = f"\n📌 Estágio IRIS sugerido: {estagio}"
        
        # Adicionar subetágios se disponíveis
        subetagios_str = []
        if subestagio_ap:
            ap_desc = {"AP0": "não proteinúrico", "AP1": "borderline proteinúrico", "AP2": "proteinúrico"}.get(subestagio_ap, subestagio_ap)
            subetagios_str.append(f"{subestagio_ap} ({ap_desc})")
        if subestagio_ht:
            ht_desc = {"HT0": "risco mínimo", "HT1": "risco baixo", "HT2": "risco moderado", "HT3": "risco grave"}.get(subestagio_ht, subestagio_ht)
            subetagios_str.append(f"{subestagio_ht} ({ht_desc})")
        
        if subetagios_str:
            linha_estagio += f" — Subetágios: {', '.join(subetagios_str)}"
        
        resposta.append(linha_estagio)
    else:
        resposta.append(f"\n⚠️ Estágio IRIS: NÃO DETERMINADO")
    
    # Fundamentação clínica
    resposta.append("")
    resposta.append("📄 Fundamentação:")
    resposta.append("-" * 70)
    mensagem = resultado.get("mensagem", "Nenhuma informação disponível")
    resposta.append(mensagem)
    
    # Alertas
    if resultado.get("alertas"):
        resposta.append("")
        resposta.append("⚠️  Observações:")
        resposta.append("-" * 70)
        for a in resultado["alertas"]:
            resposta.append(f"  • {a}")
    
    # Plano terapêutico
    if resultado.get("plano_terapeutico"):
        resposta.append("")
        resposta.append("💊 Recomendações Terapêuticas:")
        resposta.append("-" * 70)
        for idx, item in enumerate(resultado["plano_terapeutico"], 1):
            resposta.append(f"  {idx}. {item}")
    
    # Confiança
    resposta.append("")
    resposta.append("-" * 70)
    confianca = resultado.get("confianca", "BAIXA")
    emoji = "🟢" if confianca == "ALTA" else "🟡" if confianca == "MODERADA" else "🔴"
    resposta.append(f"{emoji} Confiança da análise: {confianca}")
    
    # Debug info (caso)
    caso = resultado.get("caso")
    if caso:
        resposta.append(f"📊 Caso: {caso}")
    
    resposta.append("=" * 70)
    
    return "\n".join(resposta)