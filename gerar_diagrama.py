"""
Script para gerar diagrama visual da arquitetura LangGraph
Gera arquivo PNG com o fluxo do sistema multi-agente
"""

from lg_nodes import (
    node_agente_a_entrada,
    node_agente_b,
    node_agente_c,
    node_agente_a_saida
)
from lg_states import MASState
from langgraph.graph import StateGraph, END

def create_mas_graph():
    """Cria o grafo do sistema multi-agente"""
    
    # Criar StateGraph
    graph_builder = StateGraph(MASState)
    
    # Adicionar nós
    graph_builder.add_node("agente_a_entrada", node_agente_a_entrada)
    graph_builder.add_node("agente_b_inferencia", node_agente_b)
    graph_builder.add_node("agente_c_validacao", node_agente_c)
    graph_builder.add_node("agente_a_saida", node_agente_a_saida)
    
    # Definir ponto de entrada
    graph_builder.set_entry_point("agente_a_entrada")
    
    # Adicionar edges (fluxo)
    graph_builder.add_edge("agente_a_entrada", "agente_b_inferencia")
    graph_builder.add_edge("agente_b_inferencia", "agente_c_validacao")
    graph_builder.add_edge("agente_c_validacao", "agente_a_saida")
    graph_builder.add_edge("agente_a_saida", END)
    
    # Compilar
    return graph_builder.compile()


if __name__ == "__main__":
    print("🎨 Gerando diagrama da arquitetura LangGraph...")
    
    # Criar o grafo
    app = create_mas_graph()
    
    # Gerar diagrama PNG
    try:
        # Método 1: get_graph (LangGraph 0.0.20+)
        graph_image = app.get_graph().draw_mermaid_png()
        
        with open("arquitetura_sistema_mas.png", "wb") as f:
            f.write(graph_image)
        
        print("✅ Diagrama salvo em: arquitetura_sistema_mas.png")
        
    except AttributeError:
        # Método 2: Fallback para versões antigas
        try:
            from IPython.display import Image
            import io
            
            # Tentar gerar ASCII art ao menos
            print("\n📊 DIAGRAMA ASCII DO FLUXO:\n")
            print("┌─────────────────────────────────────────────────────────┐")
            print("│                    USUÁRIO (Veterinário)                 │")
            print("│              Input: Dados clínicos do gato               │")
            print("└────────────────────┬────────────────────────────────────┘")
            print("                     │")
            print("                     ▼")
            print("┌─────────────────────────────────────────────────────────┐")
            print("│              🟦 AGENTE A - ENTRADA                       │")
            print("│  • Extrai parâmetros (creatinina, SDMA, idade, etc.)   │")
            print("│  • Normaliza e valida dados                             │")
            print("│  • Output: clinical_data                                │")
            print("└────────────────────┬────────────────────────────────────┘")
            print("                     │")
            print("                     ▼")
            print("┌─────────────────────────────────────────────────────────┐")
            print("│         🟩 AGENTE B - INFERÊNCIA ONTOLÓGICA             │")
            print("│  • Carrega ontologia OWL (83 classes, 473 axiomas)     │")
            print("│  • Executa Pellet reasoner                              │")
            print("│  • Classifica estágio IRIS (1-4)                        │")
            print("│  • Detecta discrepâncias (creat vs SDMA)                │")
            print("│  • Output: inference_result (estágio, alertas)          │")
            print("└────────────────────┬────────────────────────────────────┘")
            print("                     │")
            print("                     ▼")
            print("┌─────────────────────────────────────────────────────────┐")
            print("│            🟨 AGENTE C - VALIDAÇÃO RAG                   │")
            print("│  • Busca diretrizes IRIS em Chroma DB (top-5)          │")
            print("│  • Valida resultado do Agente B                         │")
            print("│  • Calcula confiança (score)                            │")
            print("│  • Salva validação em CSV (auditoria)                   │")
            print("│  • Output: validated_result (estágio final, citações)   │")
            print("└────────────────────┬────────────────────────────────────┘")
            print("                     │")
            print("                     ▼")
            print("┌─────────────────────────────────────────────────────────┐")
            print("│              🟦 AGENTE A - SAÍDA                         │")
            print("│  • Consolida resultados (B + C)                         │")
            print("│  • Humaniza texto com LLM (opcional)                    │")
            print("│  • Formata resposta final em português                  │")
            print("│  • Inclui citações e rastreabilidade                    │")
            print("└────────────────────┬────────────────────────────────────┘")
            print("                     │")
            print("                     ▼")
            print("┌─────────────────────────────────────────────────────────┐")
            print("│                  RESPOSTA AO VETERINÁRIO                 │")
            print("│  Exemplo: 'Paciente IRIS 3 (DRC moderada), AP1, HT0.   │")
            print("│           Baseado em creatinina 3.5 mg/dL e SDMA 22.'  │")
            print("└─────────────────────────────────────────────────────────┘")
            
            print("\n⚠️ Para gerar PNG, instale: pip install pygraphviz")
            print("   Ou use LangGraph Studio: langgraph dev")
            
        except Exception as e2:
            print(f" Erro ao gerar diagrama: {e2}")
            print("\n ALTERNATIVAS:")
            print("   1. Use LangGraph Studio (langgraph dev)")
            print("   2. Instale: pip install pygraphviz")
            print("   3. Use o diagrama ASCII acima para documentação")
    
    print("\n📚 Referências:")
    print("   • LangGraph Docs: https://langchain-ai.github.io/langgraph/")
    print("   • Arquivo: lg_nodes.py (nós dos agentes)")
    print("   • Arquivo: lg_states.py (estado compartilhado)")
