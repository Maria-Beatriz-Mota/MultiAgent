"""
LangGraph Nodes - Conectores dos Agentes (VERSÃO CORRIGIDA)
-----------------------------------------------------------
Pipeline:
A (entrada) -> B (ontologia) -> C (RAG/IRIS) -> A (formatação final)

CORREÇÕES:
- Node C agora recebe inference_result completo de B
- Node A_saida usa consolidar_resultados() corretamente
"""

from lg_states import MASState


# =====================================================================
# NODE 1 - AGENTE A (ENTRADA)
# =====================================================================
def node_agente_a_entrada(state: MASState) -> MASState:
    print("\n" + "="*70)
    print("🟦 AGENTE A - ENTRADA")
    print("="*70)

    try:
        from Agent_A.agente_A import processar_input_usuario
    except ImportError as e:
        print(f"[ERRO A] {e}")
        state.final_answer = "❌ Erro ao importar Agente A"
        return state

    try:
        clinical_data = processar_input_usuario(
            formulario=state.formulario,
            texto_livre=state.user_input
        )
    except Exception as e:
        print(f"[ERRO A] Falha no processamento: {e}")
        state.final_answer = "❌ Erro ao processar dados"
        state.clinical_data = {}
        return state

    # Validação mínima
    if not clinical_data.get("creatinina") and not clinical_data.get("sdma"):
        print("[AGENTE A] ⚠️ Sem creatinina ou SDMA - continuando...")
    
    state.clinical_data = clinical_data
    print(f"[AGENTE A] ✅ Dados processados: creat={clinical_data.get('creatinina')}, sdma={clinical_data.get('sdma')}")
    return state


# =====================================================================
# NODE 2 - AGENTE B (INFERÊNCIA)
# =====================================================================
def node_agente_b(state: MASState) -> MASState:
    print("\n" + "="*70)
    print("🟨 AGENTE B - ONTOLOGIA")
    print("="*70)

    try:
        from Agent_B.agente_b import handle_inference
    except ImportError as e:
        print(f"[ERRO B] {e}")
        state.inference_result = {
            "estagio": None,
            "reasoner_ok": False,
            "classificacao_valida": False,
            "motivo_invalido": "Erro ao importar Agente B"
        }
        return state

    try:
        result = handle_inference(state.clinical_data)
        print(f"[AGENTE B] ✅ Inferência: {result.get('estagio')}")
        print(f"[AGENTE B] Classificação válida: {result.get('classificacao_valida')}")
    except Exception as e:
        print(f"[ERRO B] Falha inferência: {e}")
        import traceback
        traceback.print_exc()
        result = {
            "estagio": None,
            "reasoner_ok": False,
            "classificacao_valida": False,
            "motivo_invalido": str(e)
        }

    state.inference_result = result
    return state


# =====================================================================
# NODE 3 - AGENTE C (RAG / VALIDAÇÃO)
# =====================================================================
def node_agente_c(state: MASState) -> MASState:
    print("\n" + "="*70)
    print("🟩 AGENTE C - RAG / IRIS")
    print("="*70)

    try:
        from Agent_C.agent_c import agent_c_answer
    except ImportError as e:
        print(f"[ERRO C] {e}")
        state.validated_result = {
            "caso": 4,
            "estagio_final": None,
            "mensagem": "Erro ao importar Agent C",
            "plano_terapeutico": [],
            "confianca": "BAIXA"
        }
        return state

    try:
        # 🔥 CORREÇÃO: Passar inference_result COMPLETO (com classificacao_valida)
        validated = agent_c_answer(
            resultado_b=state.inference_result,  # Inclui classificacao_valida e motivo_invalido
            clinical_data=state.clinical_data,
            pergunta=state.user_input or ""
        )
        
        caso = validated.get("caso", "?")
        estagio = validated.get("estagio_final", "N/A")
        print(f"[AGENTE C] ✅ Validação concluída - CASO {caso}, Estágio: {estagio}")
        
    except Exception as e:
        print(f"[ERRO C] Falha no RAG: {e}")
        import traceback
        traceback.print_exc()
        validated = {
            "caso": 4,
            "estagio_final": None,
            "mensagem": f"Erro no Agente C: {e}",
            "plano_terapeutico": [],
            "confianca": "BAIXA"
        }

    state.validated_result = validated
    return state


# =====================================================================
# NODE 4 - AGENTE A (SAÍDA) - CORRIGIDO
# =====================================================================
def node_agente_a_saida(state: MASState) -> MASState:
    print("\n" + "="*70)
    print("🟦 AGENTE A - SAÍDA")
    print("="*70)

    try:
        from Agent_A.agente_A import consolidar_resultados, formatar_resposta_final
    except ImportError as e:
        print(f"[ERRO A SAÍDA] {e}")
        state.final_answer = "❌ Erro ao importar formatadores do Agente A"
        return state

    try:
        # 🔥 CORREÇÃO: Consolidar B + C ANTES de formatar
        resultado_consolidado = consolidar_resultados(
            resultado_b=state.inference_result,
            resultado_c=state.validated_result,
            dados_clinicos=state.clinical_data
        )
        
        print(f"[AGENTE A] Resultado consolidado:")
        print(f"  • Estágio final: {resultado_consolidado.get('estagio_final')}")
        print(f"  • Confiança: {resultado_consolidado.get('confianca')}")
        print(f"  • Caso: {resultado_consolidado.get('caso')}")
        
        # Formatar para apresentação (incluindo dados clínicos)
        resposta_final = formatar_resposta_final(resultado_consolidado, state.clinical_data)
        
    except Exception as e:
        print(f"[ERRO SAÍDA] {e}")
        import traceback
        traceback.print_exc()
        resposta_final = f"❌ Erro ao processar resposta final: {e}"

    state.final_answer = resposta_final
    return state


# =====================================================================
# EXPORTS
# =====================================================================
__all__ = [
    "node_agente_a_entrada",
    "node_agente_b",
    "node_agente_c",
    "node_agente_a_saida"
]