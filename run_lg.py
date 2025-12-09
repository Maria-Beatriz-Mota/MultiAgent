"""
Sistema Multi-Agente para Diagnóstico IRIS em Gatos (CORRIGIDO)
---------------------------------------------------------------

Pipeline Completo: Usuário → A_entrada → B → C → A_saida → Usuário

Agentes:
- A_entrada: Processa formulário + texto livre do usuário
- B: Inferência ontológica (OWL + reasoner HermiT)
- C: Validação com RAG (diretrizes IRIS) + 7 casos
- A_saida: Formatação final da resposta

Fluxo de dados:
1. Usuário → formulário + pergunta
2. A_entrada → clinical_data
3. B → inference_result
4. C → validated_result (com caso 1-7)
5. A_saida → final_answer formatada
6. Usuário recebe resposta
"""

from langgraph.graph import StateGraph, END
from lg_states import MASState
from lg_nodes import (
    node_agente_a_entrada,
    node_agente_b,
    node_agente_c,
    node_agente_a_saida
)


# =====================================================================
# DEFINIÇÃO DO GRAFO LANGGRAPH (CORRIGIDO)
# =====================================================================

def create_graph():
    """
    Cria o grafo do sistema multi-agente
    
    Estrutura:
    ┌─────────────────┐
    │  A_entrada      │ ← Processa input
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │  B              │ ← Inferência
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │  C              │ ← Validação + RAG
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │  A_saida        │ ← Formatação
    └────────┬────────┘
             │
             ▼
           [END]
    """
    workflow = StateGraph(MASState)
    
    # Adicionar 4 nodes (A agora tem entrada e saída)
    workflow.add_node("agente_a_entrada", node_agente_a_entrada)
    workflow.add_node("agente_b", node_agente_b)
    workflow.add_node("agente_c", node_agente_c)
    workflow.add_node("agente_a_saida", node_agente_a_saida)  # NOVO
    
    # Definir fluxo sequencial
    workflow.set_entry_point("agente_a_entrada")
    workflow.add_edge("agente_a_entrada", "agente_b")
    workflow.add_edge("agente_b", "agente_c")
    workflow.add_edge("agente_c", "agente_a_saida")  # NOVO
    workflow.add_edge("agente_a_saida", END)
    
    return workflow.compile()


# Compilar grafo globalmente (necessário para LangGraph Studio)
app = create_graph()


# =====================================================================
# FUNÇÃO DE EXECUÇÃO PRINCIPAL (CORRIGIDA)
# =====================================================================

def run_pipeline(
    formulario: dict = None,
    texto_livre: str = None
) -> str:
    """
    Executa o pipeline completo e retorna resposta formatada
    
    Args:
        formulario: Dict com dados estruturados do formulário
            {
                "sdma": float,
                "creatinina": float,
                "idade": int,
                "peso": float,
                "pressao": float,
                "upc": float,
                "sintomas": str (separados por vírgula),
                "comorbidades": str (separadas por vírgula)
            }
        texto_livre: Pergunta do usuário em texto livre
    
    Returns:
        Mensagem formatada para o usuário
    
    Exemplos:
        # Exemplo 1: Formulário completo + pergunta
        resultado = run_pipeline(
            formulario={
                "sdma": 22,
                "creatinina": 2.5,
                "upc": 0.3,
                "pressao": 165
            },
            texto_livre="Qual o estágio IRIS e qual tratamento?"
        )
        
        # Exemplo 2: Só texto livre (extração via regex)
        resultado = run_pipeline(
            texto_livre="Gato com creatinina 3.5 e SDMA 22"
        )
    """
    print("\n" + "🚀"*35)
    print("INICIANDO SISTEMA MULTI-AGENTE IRIS")
    print("🚀"*35)
    
    # Estado inicial com formulário + texto livre
    initial_state = MASState(
        formulario=formulario,
        user_input=texto_livre
    )
    
    # Executar grafo completo
    try:
        result_state = app.invoke(initial_state)
        
        # A resposta final já vem formatada do node "agente_a_saida"
        final_message = result_state.get("final_answer")
        
        if not final_message:
            # Fallback se algo deu errado
            return "❌ Erro: Não foi possível processar a consulta."
        
        return final_message
        
    except Exception as e:
        print(f"\n❌ ERRO NA EXECUÇÃO DO PIPELINE: {e}")
        import traceback
        traceback.print_exc()
        return f"""
❌ ERRO CRÍTICO NO PROCESSAMENTO

Ocorreu um erro inesperado ao processar sua consulta.

Detalhes técnicos:
{str(e)}

Por favor, tente novamente ou entre em contato com o suporte.
"""


# =====================================================================
# FUNÇÃO AUXILIAR: Executar com texto simples (compatibilidade)
# =====================================================================

def run_pipeline_simple(user_text: str) -> str:
    """
    Função simplificada para compatibilidade com código antigo
    Aceita apenas texto e tenta extrair dados via regex
    
    Args:
        user_text: Texto com dados clínicos do gato
    
    Returns:
        Mensagem formatada
    """
    return run_pipeline(texto_livre=user_text)


# =====================================================================
# TESTES E EXEMPLOS
# =====================================================================

def exemplo_completo():
    """Exemplo de uso com formulário completo"""
    print("\n" + "="*70)
    print("EXEMPLO 1: FORMULÁRIO COMPLETO + PERGUNTA")
    print("="*70)
    
    formulario = {
        "sdma": 22,
        "creatinina": 2.5,
        "idade": 10,
        "peso": 4.5,
        "pressao": 165,
        "upc": 0.3,
        "sintomas": "vômito, letargia",
        "comorbidades": "hipertireoidismo"
    }
    
    pergunta = "Por que este gato está no estágio 2 e qual o tratamento indicado?"
    
    resposta = run_pipeline(formulario=formulario, texto_livre=pergunta)
    print(resposta)


def exemplo_texto_livre():
    """Exemplo de uso com texto livre (extração via regex)"""
    print("\n" + "="*70)
    print("EXEMPLO 2: TEXTO LIVRE (EXTRAÇÃO VIA REGEX)")
    print("="*70)
    
    texto = "Gato com creatinina 3.5, SDMA 28, pressão 170, idade 12 anos"
    
    resposta = run_pipeline(texto_livre=texto)
    print(resposta)


def exemplo_dados_insuficientes():
    """Exemplo com dados insuficientes (CASO 6)"""
    print("\n" + "="*70)
    print("EXEMPLO 3: DADOS INSUFICIENTES (CASO 6)")
    print("="*70)
    
    formulario = {
        "idade": 10,
        "peso": 4.5
        # Falta creatinina e SDMA!
    }
    
    resposta = run_pipeline(formulario=formulario)
    print(resposta)


def exemplo_pergunta_fora_escopo():
    """Exemplo com pergunta fora de escopo (CASO 5)"""
    print("\n" + "="*70)
    print("EXEMPLO 4: PERGUNTA FORA DE ESCOPO (CASO 5)")
    print("="*70)
    
    formulario = {
        "sdma": 20,
        "creatinina": 2.0
    }
    
    pergunta = "O gato gosta de brincar com laser?"
    
    resposta = run_pipeline(formulario=formulario, texto_livre=pergunta)
    print(resposta)


# =====================================================================
# EXECUÇÃO INTERATIVA (quando executado diretamente)
# =====================================================================

if __name__ == "__main__":
    import sys
    
    print("\n" + "="*70)
    print("🐱 SISTEMA DE DIAGNÓSTICO IRIS - DOENÇA RENAL CRÔNICA EM GATOS")
    print("="*70)
    
    print("\nModos de uso:")
    print("  1. Formulário completo (recomendado)")
    print("  3. Executar exemplos")
    print("  4. Sair")
    
    escolha = input("\nEscolha uma opção (1-4): ").strip()
    
    if escolha == "1":
        print("\n--- MODO FORMULÁRIO ---")
        print("Forneça os dados clínicos:")
        
        try:
            sdma = input("SDMA (µg/dL): ").strip()
            creat = input("Creatinina (mg/dL): ").strip()
            idade = input("Idade (anos): ").strip()
            peso = input("Peso (kg): ").strip()
            pressao = input("Pressão arterial (mmHg): ").strip()
            upc = input("UPC: ").strip()
            sintomas = input("Sintomas (separados por vírgula): ").strip()
            comorbidades = input("Comorbidades (separadas por vírgula): ").strip()
            pergunta = input("Pergunta: ").strip()
            
            formulario = {}
            if sdma: formulario["sdma"] = float(sdma)
            if creat: formulario["creatinina"] = float(creat)
            if idade: formulario["idade"] = int(idade)
            if peso: formulario["peso"] = float(peso)
            if pressao: formulario["pressao"] = float(pressao)
            if upc: formulario["upc"] = float(upc)
            if sintomas: formulario["sintomas"] = sintomas
            if comorbidades: formulario["comorbidades"] = comorbidades
            
            resposta = run_pipeline(formulario=formulario, texto_livre=pergunta)
            
            print("\n" + "="*70)
            print("📊 RESULTADO DA AVALIAÇÃO")
            print("="*70)
            print(resposta)
            
        except ValueError as e:
            print(f"\n❌ Erro: Valor inválido fornecido - {e}")
        except Exception as e:
            print(f"\n❌ Erro: {e}")
    
    elif escolha == "3":
        print("\n--- EXECUTANDO EXEMPLOS ---")
        
        exemplo_completo()
        input("\nPressione ENTER para continuar...")
        
        exemplo_texto_livre()
        input("\nPressione ENTER para continuar...")
        
        exemplo_dados_insuficientes()
        input("\nPressione ENTER para continuar...")
        
        exemplo_pergunta_fora_escopo()
    
    elif escolha == "4":
        print("\nEncerrando...")
        sys.exit(0)
    
    else:
        print("\n❌ Opção inválida")
    
    print("\n" + "="*70)