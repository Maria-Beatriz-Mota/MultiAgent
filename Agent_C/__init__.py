"""
Agente C - Módulo de RAG e Validação
"""
from .agent_c_db import rag_search, CHROMA_PATH
from .agent_c import gerar_recomendacao, agent_c_answer

__all__ = ['rag_search', 'gerar_recomendacao', 'agent_c_answer', 'CHROMA_PATH']