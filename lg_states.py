"""
LangGraph State - Estado Compartilhado (CORRIGIDO)
--------------------------------------------------

Representa o estado que flui entre os agentes no pipeline:
Usuário → A_entrada → B → C → A_saida → Usuário
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class MASState(BaseModel):
    """
    Estado compartilhado entre os agentes
    
    Fluxo de dados:
    1. Usuário fornece formulário + texto_livre
    2. A_entrada: processa → clinical_data
    3. B: inferência → inference_result
    4. C: validação → validated_result
    5. A_saida: formatação → final_answer
    """
    
    # ===== ENTRADA DO USUÁRIO =====
    # NOVO: Formulário estruturado com dados clínicos
    formulario: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Dados estruturados do formulário (SDMA, creatinina, etc.)"
    )
    
    # Pergunta em texto livre do usuário
    user_input: Optional[str] = Field(
        default=None,
        description="Pergunta ou texto livre do usuário"
    )
    
    # ===== DADOS PROCESSADOS (A → B) =====
    # Dados clínicos estruturados extraídos por A
    clinical_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Dados clínicos estruturados para Agente B"
    )
    
    # ===== INFERÊNCIA (B → C) =====
    # Resultado da inferência ontológica do Agente B
    inference_result: Dict[str, Any] = Field(
        default_factory=dict,
        description="Resultado da inferência ontológica (estágio, reasoner_ok, etc.)"
    )
    
    # ===== VALIDAÇÃO (C → A) =====
    # Resultado validado pelo Agente C (com caso 1-7)
    validated_result: Dict[str, Any] = Field(
        default_factory=dict,
        description="Resultado validado com RAG (caso, estágio, mensagem, plano, etc.)"
    )
    
    # ===== SAÍDA FINAL (A → Usuário) =====
    # Resposta final formatada para o usuário
    final_answer: Optional[str] = Field(
        default=None,
        description="Mensagem final formatada pelo Agente A"
    )
    
    # ===== METADADOS (OPCIONAL) =====
    # Para debugging e logging
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Metadados extras para debugging"
    )
    
    class Config:
        arbitrary_types_allowed = True