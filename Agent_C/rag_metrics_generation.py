"""
Métricas de Avaliação de Geração de Respostas para Sistema RAG
================================================================
Implementa métricas para avaliar a qualidade das respostas geradas:
- Answer Accuracy (usando LLM-as-a-judge)
- Faithfulness / Groundedness (verifica fidelidade aos documentos)

Autor: Sistema Multi-Agente IRIS
Data: Dezembro 2025
"""

import os
import re
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

try:
    from langchain_groq import ChatGroq
    from langchain_google_genai import ChatGoogleGenerativeAI
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("Aviso: LangChain não disponível. Instale: pip install langchain-groq langchain-google-genai")


class GenerationMetrics:
    """
    Classe para calcular métricas de qualidade de geração de respostas.
    
    Uso:
        metrics = GenerationMetrics(model_name="groq")
        
        result = metrics.evaluate_answer(
            question="Como diagnosticar DRC?",
            generated_answer="DRC é diagnosticada através de exames...",
            reference_answer="O diagnóstico de DRC requer exames de sangue...",
            context_documents=["doc1 text", "doc2 text"]
        )
    """
    
    def __init__(
        self, 
        model_name: str = "groq",
        temperature: float = 0.0
    ):
        """
        Inicializa o avaliador de geração.
        
        Args:
            model_name: "groq" ou "gemini"
            temperature: Temperatura do modelo (0 = mais determinístico)
        """
        self.model_name = model_name
        self.temperature = temperature
        self.llm = None
        
        if LANGCHAIN_AVAILABLE:
            self._initialize_llm()
    
    def _initialize_llm(self):
        """Inicializa o modelo LLM para avaliação."""
        if self.model_name == "groq":
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                print("Aviso: GROQ_API_KEY não encontrada")
                return
            
            self.llm = ChatGroq(
                api_key=api_key,
                model_name="llama-3.1-8b-instant",
                temperature=self.temperature
            )
        
        elif self.model_name == "gemini":
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                print("Aviso: GOOGLE_API_KEY não encontrada")
                return
            
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-pro",
                google_api_key=api_key,
                temperature=self.temperature
            )
    
    def answer_accuracy(
        self,
        question: str,
        generated_answer: str,
        reference_answer: str,
        scale: int = 5
    ) -> Dict[str, Any]:
        """
        Avalia a acurácia da resposta usando LLM-as-a-judge.
        
        Args:
            question: A pergunta original
            generated_answer: Resposta gerada pelo sistema
            reference_answer: Resposta correta de referência
            scale: Escala de avaliação (default 1-5)
            
        Returns:
            Dict com score, justificativa e análise
        """
        if not self.llm:
            return {
                "error": "LLM não inicializado",
                "score": 0,
                "scale": scale
            }
        
        prompt = f"""Avalie a ACURÁCIA desta resposta em escala 1-{scale}.

PERGUNTA:
{question}

RESPOSTA DE REFERÊNCIA:
{reference_answer}

RESPOSTA GERADA:
{generated_answer}

Escala:
{scale} = Completamente correta
{int(scale/2)+1} = Parcialmente correta
1 = Incorreta

FORMATO:
Score: [número]
Justificativa: [explicação]
"""
        
        try:
            response = self.llm.invoke(prompt)
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            score_match = re.search(r'Score:\s*(\d+)', response_text)
            score = int(score_match.group(1)) if score_match else 0
            
            return {
                "score": score,
                "scale": scale,
                "normalized_score": score / scale if scale > 0 else 0,
                "evaluation": response_text
            }
        
        except Exception as e:
            return {
                "error": f"Erro na avaliação: {str(e)}",
                "score": 0
            }
    
    def faithfulness(
        self,
        generated_answer: str,
        context_documents: List[str]
    ) -> Dict[str, Any]:
        """
        Avalia a fidelidade da resposta aos documentos.
        
        Args:
            generated_answer: Resposta gerada pelo sistema
            context_documents: Lista de documentos usados como contexto
            
        Returns:
            Dict com score de fidelidade
        """
        if not self.llm:
            return {
                "error": "LLM não inicializado",
                "faithfulness_score": 0
            }
        
        context = "\n\n---\n\n".join(context_documents)
        
        prompt = f"""Verifique se esta resposta está FIEL aos documentos.

DOCUMENTOS:
{context}

RESPOSTA:
{generated_answer}

Marque cada afirmação como:
- SUPORTADO: No documento
- NÃO SUPORTADO: Não no documento
- INFERIDO: Conclusão baseada no documento

FORMATO:
Claims:
1. [afirmação] - [SUPORTADO/NÃO SUPORTADO/INFERIDO]

Faithfulness Score: [0.0 a 1.0]
"""
        
        try:
            response = self.llm.invoke(prompt)
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            score_match = re.search(r'Faithfulness Score:\s*([\d.]+)', response_text)
            faithfulness_score = float(score_match.group(1)) if score_match else 0.0
            
            return {
                "faithfulness_score": faithfulness_score,
                "evaluation": response_text
            }
        
        except Exception as e:
            return {
                "error": f"Erro na avaliação: {str(e)}",
                "faithfulness_score": 0.0
            }
    
    def groundedness(
        self,
        generated_answer: str,
        context_documents: List[str]
    ) -> Dict[str, Any]:
        """
        Avalia o grau de fundamentação da resposta nos documentos.
        
        Args:
            generated_answer: Resposta gerada pelo sistema
            context_documents: Lista de documentos usados como contexto
            
        Returns:
            Dict com score de groundedness
        """
        if not self.llm:
            return {
                "error": "LLM não inicializado",
                "groundedness_score": 0
            }
        
        context = "\n\n---\n\n".join(context_documents)
        
        prompt = f"""Avalie a FUNDAMENTAÇÃO desta resposta (0.0 a 1.0).

DOCUMENTOS:
{context}

RESPOSTA:
{generated_answer}

Para cada sentença, marque SIM ou NÃO se está fundamentada.

FORMATO:
Sentença 1: [texto] - SIM/NÃO
Sentença 2: [texto] - SIM/NÃO

Groundedness Score: [proporção fundamentada]
"""
        
        try:
            response = self.llm.invoke(prompt)
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            score_match = re.search(r'Groundedness Score:\s*([\d.]+)', response_text)
            groundedness_score = float(score_match.group(1)) if score_match else 0.0
            
            return {
                "groundedness_score": groundedness_score,
                "evaluation": response_text
            }
        
        except Exception as e:
            return {
                "error": f"Erro na avaliação: {str(e)}",
                "groundedness_score": 0.0
            }
    
    def evaluate_answer(
        self,
        question: str,
        generated_answer: str,
        reference_answer: Optional[str] = None,
        context_documents: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Avaliação completa de uma resposta.
        
        Args:
            question: A pergunta original
            generated_answer: Resposta gerada pelo sistema
            reference_answer: Resposta de referência (opcional)
            context_documents: Documentos de contexto (opcional)
            
        Returns:
            Dict com todas as métricas calculadas
        """
        results = {
            "question": question,
            "generated_answer": generated_answer
        }
        
        if reference_answer:
            results["accuracy"] = self.answer_accuracy(
                question, generated_answer, reference_answer
            )
        
        if context_documents:
            results["faithfulness"] = self.faithfulness(
                generated_answer, context_documents
            )
            results["groundedness"] = self.groundedness(
                generated_answer, context_documents
            )
        
        return results


if __name__ == "__main__":
    print("Teste de Métricas de Geração\n")
    
    if not LANGCHAIN_AVAILABLE:
        print("LangChain não disponível")
        exit(1)
    
    metrics = GenerationMetrics(model_name="groq")
    
    if not metrics.llm:
        print("LLM não inicializado. Verifique as credenciais.")
        exit(1)
    
    question = "Como diagnosticar DRC em gatos?"
    reference_answer = "DRC é diagnosticada através de exames de sangue medindo creatinina"
    generated_answer = "A DRC é diagnosticada por níveis elevados de creatinina no sangue"
    context = ["DRC é classificada por creatinina sérica", "Exames de sangue são necessários"]
    
    result = metrics.evaluate_answer(
        question=question,
        generated_answer=generated_answer,
        reference_answer=reference_answer,
        context_documents=context
    )
    
    print("Resultado da Avaliação:")
    for metric, value in result.items():
        if isinstance(value, dict):
            print(f"\n{metric}:")
            for k, v in value.items():
                if not k.startswith("evaluation"):
                    print(f"  {k}: {v}")
        else:
            print(f"{metric}: {value}")
