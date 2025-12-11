# Sistema Multi-Agente para Diagnóstico Médico
## Integração LLM + RAG + Ontologias via LangGraph

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-green.svg)](https://github.com/langchain-ai/langgraph)
[![License](https://img.shields.io/badge/License-Academic-yellow.svg)](LICENSE)

Sistema inteligente de suporte à decisão clínica que combina **3 agentes especializados** para análise, validação e fundamentação de diagnósticos médicos. Utiliza **LangGraph** para orquestração, **LLMs** para raciocínio clínico, **ontologias OWL** para validação formal e **RAG** para evidências científicas.

---

## Índice

- [Sobre o Projeto](#-sobre-o-projeto)
- [Arquitetura](#-arquitetura)
- [Como Funciona](#-como-funciona)
- [Tecnologias](#-tecnologias)
- [Instalação](#-instalação)
- [Uso](#-uso)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [API REST](#-api-rest)
- [Exemplos](#-exemplos)
- [Documentação](#-documentação)
- [Troubleshooting](#-troubleshooting)
- [Licença](#-licença)

---

## Sobre o Projeto

Este sistema implementa uma arquitetura multi-agente para auxiliar no diagnóstico de **Doença Renal Crônica (DRC)** em gatos, seguindo as diretrizes oficiais **IRIS** (International Renal Interest Society).

### Diferenciais:

- **3 Agentes Especializados** que cooperam via LangGraph
- **Raciocínio Clínico** com LLM (Groq/LLaMA 3.1 70B)
- **Validação Formal** com ontologias OWL + reasoner Pellet
- **Evidências Científicas** via RAG (ChromaDB)
- **Estados Compartilhados** entre agentes
- **API REST** para integração externa

### Aplicação:

Sistema de suporte à decisão clínica para veterinários, permitindo:
- Análise de sintomas e parâmetros laboratoriais
- Classificação automática de estágios IRIS
- Validação cruzada entre múltiplas fontes de conhecimento
- Fundamentação científica das recomendações

---

## Arquitetura

### Fluxo Geral:

```
┌─────────────┐
│   Input     │  Sintomas + Dados Clínicos
│  (JSON/API) │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────┐
│         LangGraph (Orquestração)        │
│  ┌───────────────────────────────────┐  │
│  │     Estados Compartilhados        │  │
│  │  (AgentState: TypedDict)          │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
       │
       ├──► Agente A (Análise Clínica)
       │      ↓ state["diagnosis"]
       │
       ├──► Agente B (Validação OWL)
       │      ↓ state["validation"]
       │
       └──► Agente C (RAG + Evidências)
              ↓ state["evidence"]
       │
       ▼
┌─────────────┐
│   Output    │  Diagnóstico + Validação + Evidências
│  (JSON/API) │
└─────────────┘
```

### Agente A - Raciocínio Clínico

**Responsabilidade:** Análise inicial de sintomas com LLM

**Tecnologias:**
- Groq (LLaMA 3.1 70B)
- LangChain
- Chain-of-Thought prompting

**Entrada:** 
```json
{
  "symptoms": "febre alta, tosse seca, dor no peito",
  "patient_age": 45,
  "patient_sex": "M"
}
```

**Saída:** Lista priorizada de diagnósticos possíveis

---

### Agente B - Validação Ontológica

**Responsabilidade:** Validação formal com conhecimento estruturado

**Tecnologias:**
- Owlready2
- Ontologias OWL
- Reasoner Pellet (DL)

**Entrada:** Diagnósticos do Agente A

**Saída:** Validação lógica + compatibilidade ontológica

**Regras IRIS Implementadas:**
- Classificação de estágios (1-4)
- Validação cruzada Creatinina/SDMA
- Detecção de discrepâncias (≥2 estágios = erro)

---

### Agente C - RAG e Evidências

**Responsabilidade:** Busca em literatura científica

**Tecnologias:**
- ChromaDB (base vetorial)
- Embeddings (Google Generative AI)
- RAG (Retrieval-Augmented Generation)

**Entrada:** Diagnósticos validados

**Saída:** Artigos científicos relevantes + evidências

**Base de Conhecimento:**
- PDFs médicos indexados
- Busca semântica
- Top-k documentos mais relevantes

---

## Como Funciona

### 1. Recepção de Dados

```python
# Input via API ou linha de comando
input_data = {
    "symptoms": "febre, tosse, dificuldade respiratória",
    "patient_age": 45,
    "patient_sex": "M"
}
```

### 2. Orquestração LangGraph

```python
from langgraph.graph import StateGraph

# Criar grafo
workflow = StateGraph(AgentState)

# Adicionar agentes como nós
workflow.add_node("agent_a", agent_a_node)
workflow.add_node("agent_b", agent_b_node)
workflow.add_node("agent_c", agent_c_node)

# Definir fluxo
workflow.add_edge("agent_a", "agent_b")
workflow.add_edge("agent_b", "agent_c")

# Compilar e executar
app = workflow.compile()
result = app.invoke(input_data)
```

### 3. Estados Compartilhados

```python
class AgentState(TypedDict):
    symptoms: str              # Input inicial
    patient_age: int
    patient_sex: str
    diagnosis: List[str]       # Output Agente A
    validation: Dict           # Output Agente B
    evidence: List[str]        # Output Agente C
    final_result: Dict         # Consolidado
```

### 4. Resultado Final

```json
{
  "diagnosis": ["Pneumonia bacteriana", "COVID-19"],
  "confidence": 0.85,
  "iris_stage": "IRIS 3",
  "validation": {
    "ontology_compatible": true,
    "reasoner_status": "success"
  },
  "evidence": [
    "Artigo: Diagnóstico de pneumonia...",
    "Estudo: Biomarcadores respiratórios..."
  ],
  "recommendations": "Antibioticoterapia + Exames complementares"
}
```

---

## Tecnologias

### Backend Python

| Tecnologia | Versão | Uso |
|------------|--------|-----|
| **LangGraph** | 0.2+ | Orquestração de agentes |
| **LangChain** | 0.3+ | Framework LLM |
| **Groq** | - | LLM Provider (LLaMA 3.1 70B) |
| **Owlready2** | 0.46+ | Ontologias OWL |
| **ChromaDB** | 0.4+ | Base vetorial (RAG) |
| **Python** | 3.10+ | Linguagem principal |

### API Node.js

| Tecnologia | Uso |
|------------|-----|
| **Express.js** | API REST |
| **CORS** | Cross-origin requests |
| **Node.js** | Runtime |

---

## Instalação

### Pré-requisitos

- **Python 3.10+** ([Download](https://www.python.org/downloads/))
- **Node.js 16+** ([Download](https://nodejs.org/))
- **Java JDK 11+** (para reasoner Pellet) ([Download](https://www.oracle.com/java/technologies/downloads/))
- **Git** ([Download](https://git-scm.com/downloads))

### Passo a Passo

**1. Clonar o repositório:**

```bash
git clone https://github.com/Maria-Beatriz-Mota/MultiAgent.git
cd MultiAgent
```

**2. Criar ambiente virtual Python:**

```bash
# Windows
python -m venv venv_mas
.\venv_mas\Scripts\Activate.ps1

# Linux/Mac
python3 -m venv venv_mas
source venv_mas/bin/activate
```

**3. Instalar dependências Python:**

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**4. Instalar dependências Node.js:**

```bash
cd api
npm install
cd ..
```

**5. Configurar variáveis de ambiente:**

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar .env e adicionar suas API keys:
# GROQ_API_KEY=sua_chave_aqui
# GOOGLE_API_KEY=sua_chave_aqui
```

**Onde obter API keys:**
- **Groq (Gratuito):** https://console.groq.com/keys
- **Google Gemini (Gratuito):** https://makersuite.google.com/app/apikey

**6. Indexar PDFs médicos (RAG):**

```bash
python setup_rag.py
```

**7. Verificar instalação:**

```bash
# Teste rápido Python
python run_lg.py

# Teste com JSON
Get-Content test_request.json | python run_lg_api.py
```

**Guia completo:** Veja [GUIA_INSTALACAO.md](GUIA_INSTALACAO.md)

---

## Uso

### Modo 1: Python Direto (Terminal)

```bash
python run_lg.py
```

### Modo 2: API REST (Recomendado)

**Iniciar servidor:**

```bash
cd api
npm start
```

**Fazer requisição:**

```bash
# PowerShell
Invoke-WebRequest -Uri http://localhost:3001/api/diagnosis `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"symptoms":"febre, tosse","patient_age":45,"patient_sex":"M"}'

# cURL
curl -X POST http://localhost:3001/api/diagnosis \
  -H "Content-Type: application/json" \
  -d '{"symptoms":"febre, tosse","patient_age":45,"patient_sex":"M"}'
```

### Modo 3: Interface HTML

Abra `test_api.html` no navegador para testar via interface visual.

---

## Estrutura do Projeto

```
MultiAgent/
├── README.md                           # Este arquivo (documentação principal)
├── API_GUIA_RAPIDO.md                  # Documentação da API REST
├── ARQUITETURA_DETALHADA.md            # Decisões de design e arquitetura
├── GUIA_INSTALACAO.md                  # Instalação passo a passo
├── RELATORIO_TECNICO.md                # Resultados e métricas
│
├── requirements.txt                    # Dependências Python
├── .env                                # Variáveis de ambiente (não commitado)
├── .env.example                        # Template do .env
├── .gitignore                          # Git ignore
│
├── lg_states.py                        # Estados LangGraph (AgentState)
├── lg_nodes.py                         # Nós do grafo (funções dos agentes)
├── graph.py                            # Definição do grafo LangGraph
├── run_lg.py                           # Executar Python direto
├── run_lg_api.py                       # Executar via API
├── setup_rag.py                        # Indexar PDFs no ChromaDB
│
├── Agent_A/                            # Agente A - Análise Clínica
│   ├── __init__.py
│   └── agente_A.py                     # LLM + raciocínio clínico
│
├── Agent_B/                            # Agente B - Validação Ontológica
│   ├── __init__.py
│   ├── agente_b.py                     # Owlready2 + reasoner
│   └── onthology/
│       └── Ontology_MAS_projeto.owl    # Ontologia médica
│
├── Agent_C/                            # Agente C - RAG e Evidências
│   ├── __init__.py
│   ├── agent_c.py                      # Validação científica
│   ├── agent_c_db.py                   # ChromaDB + embeddings
│   ├── pdfs/                           # PDFs médicos
│   ├── chroma_db/                      # Base vetorial indexada
│   └── validations_database.csv        # Histórico de validações
│
├── api/                                # API Node.js REST
│   ├── server.js                       # Servidor Express
│   ├── package.json                    # Dependências Node
│   ├── routes/                         # Rotas da API
│   ├── controllers/                    # Lógica de controle
│   └── services/                       # Serviços (ponte Python)
│
├── figs/                               # Diagramas (Mermaid exportados)
│
├── test_api.html                       # Interface de teste HTML
├── test_request.json                   # JSON de teste
│
└── MDs/                                # Documentação Adicional
    ├── OUTLINE_SLIDES.md               # Estrutura dos slides
    ├── LISTA_AFAZERES_AMANHA.md        # Lista de tarefas
    ├── METRICAS_AVALIACAO.md           # Métricas detalhadas
    ├── RESUMO_TECNICO_API.md           # Resumo API
    └── RELATORIO_VERIFICACAO_AGENTES.md # Status dos agentes
```

---

## API REST

### Endpoint Principal

**POST** `/api/diagnosis`

**Request:**

```json
{
  "symptoms": "febre alta, tosse seca, dor no peito",
  "patient_age": 45,
  "patient_sex": "M",
  "creatinine": 2.5,
  "sdma": 22
}
```

**Response (Success - 200):**

```json
{
  "success": true,
  "diagnosis": ["Pneumonia", "Bronquite"],
  "confidence": 0.85,
  "iris_stage": "IRIS 2",
  "validation": {
    "ontology_compatible": true,
    "reasoner_status": "success"
  },
  "evidence": [
    "Artigo: Diagnóstico diferencial de pneumonia...",
    "Estudo: Biomarcadores respiratórios..."
  ],
  "recommendations": "Antibioticoterapia empírica + Rx tórax",
  "processing_time": "18.5s"
}
```

**Response (Error - 400/500):**

```json
{
  "success": false,
  "error": "Dados insuficientes para diagnóstico",
  "details": "Necessário informar sintomas e idade"
}
```

**Documentação completa:** [API_GUIA_RAPIDO.md](MDs/API_GUIA_RAPIDO.md)

---

## Exemplos

### Exemplo 1: IRIS Estágio 2 (Leve)

```json
{
  "symptoms": "polidipsia, poliúria",
  "patient_age": 8,
  "creatinine": 2.5,
  "sdma": 20
}
```

**Resultado Esperado:** IRIS 2 (ambos marcadores concordam)

---

### Exemplo 2: IRIS Estágio 3 (Moderado)

```json
{
  "symptoms": "anorexia, perda de peso, vômitos",
  "patient_age": 12,
  "creatinine": 3.5,
  "sdma": 28,
  "blood_pressure": 165
}
```

**Resultado Esperado:** IRIS 3 + Hipertensão

---

### Exemplo 3: Discrepância Detectada

```json
{
  "creatinine": 1.5,
  "sdma": 50
}
```
**Resultado Esperado:** Erro - Discrepância ≥2 estágios (não classificável)
---
## Documentação

###  Documentação Principal (Raiz do Projeto):

- [API_GUIA_RAPIDO.md](API_GUIA_RAPIDO.md) - Documentação da API REST
- [ARQUITETURA_DETALHADA.md](ARQUITETURA_DETALHADA.md) - Decisões de design e arquitetura
-  [GUIA_INSTALACAO.md](GUIA_INSTALACAO.md) - Instalação passo a passo
-  [RELATORIO_TECNICO.md](RELATORIO_TECNICO.md) - Resultados e métricas

###  Documentação Adicional

-  [RELATORIO_VERIFICACAO_AGENTES.md](RELATORIO_VERIFICACAO_AGENTES.md) - Status dos agentes
- [OUTLINE_SLIDES.md](OUTLINE_SLIDES.md) - Estrutura da apresentação
- [METRICAS_AVALIACAO.md](METRICAS_AVALIACAO.md) - Métricas detalhadas
-  [RESUMO_TECNICO_API.md](RESUMO_TECNICO_API.md) - Resumo técnico da API

---

## Troubleshooting

### Problema: "Module not found"

```bash
pip install -r requirements.txt --force-reinstall
```

### Problema: "GROQ_API_KEY not found"

Verifique se o arquivo `.env` existe e contém:

```bash
GROQ_API_KEY=sua_chave_aqui
```

### Problema: "Java not found" (Agente B)

- Instale Java JDK 11+
- Adicione ao PATH do sistema
- Reinicie o terminal

### Problema: "Port 3001 already in use"

```bash
# Windows PowerShell
$process = Get-NetTCPConnection -LocalPort 3001 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -First 1
if ($process) { Stop-Process -Id $process -Force }
```

### Problema: ChromaDB não indexa PDFs

```bash
# Verificar PDFs na pasta
ls Agent_C/pdfs/

# Reindexar
python setup_rag.py
```
---

## Contexto Acadêmico

Este projeto foi desenvolvido como parte de pesquisa em:
- Sistemas Multi-Agente
- Integração LLM + Conhecimento Formal
- RAG (Retrieval-Augmented Generation)
- Aplicações de IA em Medicina Veterinária

**Instituição:** [Univesidade de Pernambuco - UPE]  
**Programa:** [PPGEC - Programa de pós graduação em Engenharia da Computação]  
**Disciplina:** [Modelagem Conceitual e Raciocinio Automático (MORA)]

---

## Avisos Importantes

1. **Este é um sistema de SUPORTE à decisão clínica**
2. **NÃO substitui avaliação médica/veterinária completa**
3. **Sempre consulte profissional qualificado**
4. **Para uso educacional e pesquisa**
5. **Dados sensíveis devem ser anonimizados**

---

## Licença

Este projeto é de uso acadêmico. Consulte o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## Autora

**Maria Beatriz Mota**

- GitHub: [@Maria-Beatriz-Mota](https://github.com/Maria-Beatriz-Mota)
- LinkedIn: [https://www.linkedin.com/in/maria-beatriz-ara%C3%BAjo-mota/]
- Email: [mbeatriz.mbia@gmail.com]

---

## Contribuições

Contribuições são bem-vindas! Para contribuir:

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

---

## Suporte

Para dúvidas ou problemas:

- Abra uma [Issue](https://github.com/Maria-Beatriz-Mota/MultiAgent/issues)
- Consulte a [Documentação](MDs/)
- Entre em contato via email

---

## Agradecimentos

- Equipe LangChain/LangGraph
- Comunidade Owlready2
- IRIS (International Renal Interest Society)
- Universidade de Pernambuco - (curso de Pós graduação em engenharia da computação)
- Professor Cleyton em sua disciplina (MORA)
- [Outros agradecimentos]


---

<div align="center">

**Desenvolvido por Maria Beatriz Mota**

</div>
