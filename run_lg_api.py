"""
Sistema Multi-Agente para Diagnóstico IRIS - Interface API
----------------------------------------------------------
Versão otimizada para comunicação com API Express via stdin/stdout

Entrada: JSON via stdin
Saída: JSON estruturado via stdout (sem prints intermediários)
"""

import sys
import json
import os
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr

# =====================================================================
# CONFIGURAÇÃO DE ENCODING UTF-8 (FIX WINDOWS)
# =====================================================================
# Força UTF-8 para stdin/stdout/stderr no Windows
if sys.platform == 'win32':
    import codecs
    sys.stdin = codecs.getreader('utf-8')(sys.stdin.detach())
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())


def safe_json_output(data):
    """
    Garante output JSON com UTF-8 correto no Windows
    """
    try:
        json_str = json.dumps(data, ensure_ascii=False, indent=None)
        if hasattr(sys.stdout, 'buffer'):
            sys.stdout.buffer.write((json_str + '\n').encode('utf-8'))
            sys.stdout.buffer.flush()
        else:
            print(json_str)
    except Exception as e:
        # Fallback: usar ASCII se UTF-8 falhar
        json_str = json.dumps(data, ensure_ascii=True, indent=None)
        print(json_str)


# Importar componentes do sistema
from langgraph.graph import StateGraph, END
from lg_states import MASState
from lg_nodes import (
    node_agente_a_entrada,
    node_agente_b,
    node_agente_c,
    node_agente_a_saida
)


def create_graph():
    """Cria o grafo do sistema multi-agente"""
    workflow = StateGraph(MASState)
    
    workflow.add_node("agente_a_entrada", node_agente_a_entrada)
    workflow.add_node("agente_b", node_agente_b)
    workflow.add_node("agente_c", node_agente_c)
    workflow.add_node("agente_a_saida", node_agente_a_saida)
    
    workflow.set_entry_point("agente_a_entrada")
    workflow.add_edge("agente_a_entrada", "agente_b")
    workflow.add_edge("agente_b", "agente_c")
    workflow.add_edge("agente_c", "agente_a_saida")
    workflow.add_edge("agente_a_saida", END)
    
    return workflow.compile()


def format_response_for_client(result: dict) -> dict:
    """
    Formata a resposta de forma estruturada e amigável para o cliente
    Similar ao formato do Agente A original
    """
    validated = result.get("validated_result", {})
    clinical = result.get("clinical_data", {})
    inference = result.get("inference_result", {})
    
    # Extrair dados principais
    estagio_final = validated.get("estagio_final", "Não determinado")
    confianca = validated.get("confianca", "BAIXA")
    caso = validated.get("caso", 0)
    
    # Dados do paciente
    paciente = {
        "nome": clinical.get("nome") or "Não informado",
        "sexo": clinical.get("sexo") or "Não informado",
        "raca": clinical.get("raca") or "Não informada",
        "idade": clinical.get("idade"),
        "peso": clinical.get("peso")
    }
    
    # Biomarcadores
    biomarcadores = {
        "creatinina": clinical.get("creatinina"),
        "sdma": clinical.get("sdma"),
        "upc": clinical.get("upc"),
        "pressao_arterial": clinical.get("pressao_arterial")
    }
    
    # Classificação IRIS
    classificacao = {
        "estagio": estagio_final,
        "subestagio_ap": validated.get("subestagio_ap") or inference.get("subestagio_ap"),
        "subestagio_ht": validated.get("subestagio_ht") or inference.get("subestagio_ht"),
        "confianca": confianca,
        "caso": caso
    }
    
    # Validação
    validacao = {
        "estagio_ontologia": inference.get("estagio", "Não inferido"),
        "estagio_rag": validated.get("estagio_rag", "Não encontrado"),
        "concordancia": validated.get("valida_b", False),
        "inconsistencia": validated.get("inconsistencia", False)
    }
    
    # Resposta clínica
    resposta_clinica = validated.get("resposta_clinica", "")
    resposta_pergunta = validated.get("resposta_pergunta", "")
    
    # Recomendações
    recomendacoes = validated.get("tratamento_recomendado") or validated.get("plano_terapeutico", [])
    
    # Referências
    referencias = []
    num_docs = validated.get("num_docs", 0)
    if num_docs > 0:
        for i in range(1, num_docs + 1):
            referencias.append(f"Referência {i} das diretrizes IRIS")
    
    return {
        "paciente": paciente,
        "biomarcadores": biomarcadores,
        "classificacao": classificacao,
        "validacao": validacao,
        "resposta_clinica": resposta_clinica,
        "resposta_pergunta": resposta_pergunta,
        "recomendacoes": recomendacoes,
        "referencias": referencias,
        "metadados": {
            "caso": caso,
            "confianca": confianca,
            "num_documentos_rag": num_docs
        }
    }


def run_pipeline_silent(formulario: dict = None, texto_livre: str = ""):
    """
    Executa pipeline sem prints intermediários
    Retorna apenas o resultado final formatado
    """
    app = create_graph()
    
    initial_state = {
        "formulario": formulario or {},
        "user_input": texto_livre or "",
        "clinical_data": {},
        "inference_result": {},
        "validated_result": {},
        "final_answer": "",
        "messages": []
    }
    
    # Redirecionar stdout/stderr para capturar prints
    stdout_capture = StringIO()
    stderr_capture = StringIO()
    
    try:
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            result = app.invoke(initial_state)
        
        # Formatar resposta de forma estruturada
        formatted_response = format_response_for_client(result)
        
        return {
            "success": True,
            "resultado": formatted_response,
            "resposta_completa": result.get("final_answer", ""),
            # Dados brutos disponíveis para debug (opcional)
            "dados_completos": {
                "clinical_data": result.get("clinical_data", {}),
                "inference_result": result.get("inference_result", {}),
                "validated_result": result.get("validated_result", {})
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "logs": {
                "stdout": stdout_capture.getvalue(),
                "stderr": stderr_capture.getvalue()
            }
        }


def main():
    """
    Modo API: lê JSON do stdin, executa pipeline, retorna JSON no stdout
    """
    try:
        # Ler entrada JSON do stdin (com encoding UTF-8)
        if hasattr(sys.stdin, 'buffer'):
            input_data = sys.stdin.buffer.read().decode('utf-8')
        else:
            input_data = sys.stdin.read()
        
        if not input_data.strip():
            result = {
                "success": False,
                "error": "Nenhum dado fornecido via stdin"
            }
            safe_json_output(result)
            sys.exit(1)
        
        # Parse JSON
        try:
            data = json.loads(input_data)
        except json.JSONDecodeError as e:
            result = {
                "success": False,
                "error": f"JSON inválido: {str(e)}"
            }
            safe_json_output(result)
            sys.exit(1)
        
        # Extrair formulário e texto livre
        formulario = data.get("formulario", {})
        texto_livre = data.get("texto_livre", "")
        
        # Validar dados mínimos
        if not formulario.get("sdma") and not formulario.get("creatinina"):
            result = {
                "success": False,
                "error": "Dados insuficientes: SDMA ou Creatinina são obrigatórios"
            }
            safe_json_output(result)
            sys.exit(1)
        
        # Executar pipeline
        result = run_pipeline_silent(formulario=formulario, texto_livre=texto_livre)
        
        # Retornar resultado como JSON
        safe_json_output(result)
        sys.exit(0 if result["success"] else 1)
        
    except Exception as e:
        result = {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }
        safe_json_output(result)
        sys.exit(1)


if __name__ == "__main__":
    main()
