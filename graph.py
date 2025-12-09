from langgraph.graph import StateGraph
from typing import TypedDict
from langgraph.graph import END

# 1. Defina o estado
class GraphState(TypedDict):
    question: str
    answer: str

# 2. Função que cria o grafo
def create_graph():
    builder = StateGraph(GraphState)

    # exemplo de nó
    def node_example(state: GraphState):
        return {"answer": f"Você perguntou: {state['question']}"}

    builder.add_node("example", node_example)

    builder.set_entry_point("example")
    builder.add_edge("example", END)

    # 3. Compila o grafo
    return builder.compile()

# 4. Isso aqui é o que o LangGraph Studio procura
app = create_graph()
