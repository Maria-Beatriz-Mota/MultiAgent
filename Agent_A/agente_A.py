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

from typing import Dict, Any, Optional
# NOVO BLOCO – LLM ONLINE (HUGGINGFACE)
from langchain_huggingface import HuggingFaceEndpoint

llm = HuggingFaceEndpoint(
    repo_id="mistralai/Mistral-7B-Instruct-v0.2",
    temperature=0.2,
    max_new_tokens=512,
    huggingfacehub_api_token=os.environ["HUGGINGFACEHUB_API_TOKEN"]
)
def gerar_resposta_rag(contexto_literatura, dados_clinicos):
    prompt = f"""
Você é um especialista em nefrologia veterinária.

Use APENAS a literatura científica abaixo para validar ou contestar a classificação IRIS.

LITERATURA:
{contexto_literatura}

DADOS CLÍNICOS:
{dados_clinicos}

Explique:
- Estágio IRIS correto
- Justificativa científica
- Se há concordância com a inferência
"""

    resposta = llm.invoke(prompt)
    return resposta


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
        "creatinina": _to_float(formulario.get("creatinina")),
        "sdma": _to_float(formulario.get("sdma")),
        "idade": _to_float(formulario.get("idade")),
        "sexo": formulario.get("sexo"),
        "peso": _to_float(formulario.get("peso")),
        "pas": _to_float(formulario.get("pressao_arterial")),
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
    resultado_c: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Consolida resultados de B e C respeitando os 4 casos do Agente C
    
    Casos:
    1. B e RAG concordam → confiança ALTA
    2. B não inferiu, RAG tem info → confiança MODERADA  
    3. Discrepância entre B e RAG → INCONSISTÊNCIA (pedir nova avaliação)
    4. Sem dados suficientes → BAIXA confiança
    """
    
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
    
    # Mensagem clínica (já vem formatada do C)
    mensagem = resultado_c.get("resposta_clinica", "")
    
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

def formatar_resposta_final(resultado: Dict[str, Any]) -> str:
    """
    Formata a resposta final para apresentação ao veterinário
    """
    
    resposta = []
    resposta.append("🩺 Avaliação Clínica – Doença Renal Crônica Felina")
    resposta.append("=" * 70)
    
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
    if estagio:
        resposta.append(f"\n📌 Estágio IRIS sugerido: {estagio}")
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