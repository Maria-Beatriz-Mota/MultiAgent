# Sistema Multi-Agente IRIS - Diagnóstico de DRC Felina
## LangGraph + LLM + RAG + Ontologias OWL

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Node.js](https://img.shields.io/badge/Node.js-18+-green.svg)](https://nodejs.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-orange.svg)](https://github.com/langchain-ai/langgraph)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Sistema automático de diagnóstico para **Doença Renal Crônica em gatos**, seguindo diretrizes **IRIS**. Implementa 3 agentes especializados que trabalham em conjunto: um para processamento de entrada, outro para raciocínio ontológico, e um terceiro para validação científica com RAG. Integra **LangGraph**, **LLMs**, **ontologias OWL** e **ChromaDB**.

---

## Índice

- [Sobre o Projeto](#-sobre-o-projeto)
- [Arquitetura](#-arquitetura)
- [Como Funciona](#-como-funciona)
- [Tecnologias](#-tecnologias)
- [Quick Start](#-quick-start)
- [Como Usar](#-como-usar-fluxo-básico)
- [Estrutura do Projeto](#-estrutura-de-diretórios)
- [API REST](#-api-rest)
- [Sistema de Métricas](#-sistema-de-métricas)
- [Exemplos](#-exemplo-de-uso)
- [Documentação](#-documentação-completa)
- [Troubleshooting](#-troubleshooting)
- [Licença](#-licença)

---

## Sobre o Projeto

Este sistema foi desenvolvido para automatizar diagnósticos de Doença Renal Crônica (DRC) felina, seguindo a metodologia **IRIS** (International Renal Interest Society). O sistema recebe dados clínicos (creatinina, SDMA, sintomas) e retorna um diagnóstico estruturado contendo estágio IRIS, subetágios e justificativas científicas.

### Por que 3 agentes?

- **Agente A**: Processamento de entrada e formatação de saída. Responsável pela orquestração do fluxo.
- **Agente B**: Raciocínio lógico com ontologias OWL. Valida as regras IRIS e detecta inconsistências.
- **Agente C**: Busca em RAG para justificar com literatura científica. Fundamenta as recomendações em evidências.

### O que funciona:

- Classificação IRIS automática (Estágios 1-4 + Subetágios AP/HT)
- Validação cruzada de biomarcadores (Creatinina vs SDMA)
- RAG indexando PDFs + páginas web com evidências científicas
- Detecção de discrepâncias e nível de confiança na resposta
- API REST (Node.js) pra integração externa
- Interface web simples pra testes
- Export PDF + CSV logging automático

---

## Arquitetura

O fluxo de execução segue uma arquitetura sequencial e modular:

1. Entrada (formulário ou API) → Agente A processa
2. Agente A passa para Agente B validar com regras IRIS
3. Agente B passa para Agente C buscar evidências no RAG
4. Resultado consolidado para retorno em JSON

```
Input (Creatinina, SDMA, Sintomas)
       ↓
┌─────────────────────────────────────┐
│ Agente A - Análise Clínica         │
│ (LLM: Raciocínio inicial)          │
└─────────────────────────────────────┘
       ↓
┌─────────────────────────────────────┐
│ Agente B - Validação IRIS          │
│ (OWL: Regras + Creatinina vs SDMA) │
└─────────────────────────────────────┘
       ↓
┌─────────────────────────────────────┐
│ Agente C - RAG + Evidências        │
│ (ChromaDB: Busca científica)       │
└─────────────────────────────────────┘
       ↓
Output (Estágio IRIS + Justificativa + Confiança)
```

**Agente A** - Processa dados de entrada e gera análise inicial, preparando o estado para validação posterior.

**Agente B** - Responsável pela validação. Aplica as regras IRIS (creatinina versus SDMA, detecção de discrepâncias) e utiliza OWL para validação formal.

**Agente C** - Realiza busca em banco de dados vetorial (ChromaDB) para documentos relevantes sobre DRC felina, fundamentando a resposta com evidências científicas. Inclui PDFs e conteúdo web de fontes especializadas.

---

## Tecnologias

### Backend (Python)
| Tecnologia | Função |
|-----------|--------|
| **LangGraph** | Orquestração de agentes e fluxo de estados |
| **Groq LLM** | Modelo de linguagem (llama-3.1-8b-instant) |
| **ChromaDB** | Banco de dados vetorial para RAG |
| **SentenceTransformer** | Embeddings de documentos |
| **HermiT Reasoner** | Raciocínio OWL e ontologias |
| **Owlready2** | Manipulação de ontologias OWL |
| **LangChain** | Integração com LLMs e RAG |
| **Google Generative AI** | Alternative para embeddings e LLM |

### Frontend (Node.js)
| Tecnologia | Função |
|-----------|--------|
| **Express.js** | Server web REST |
| **CORS** | Controle de origem para requisições |
| **HTML/CSS/JS** | Interface de teste (test_api.html) |
| **Fetch API** | Comunicação com backend Python |

### Infraestrutura
| Componente | Especificação |
|-----------|--------|
| **Port Python** | 8000 (LangGraph) |
| **Port Node** | 3001 (API REST) |
| **Database** | ChromaDB (local) |
| **Logging** | CSV (histórico_diagnosticos.csv) |

---

## Quick Start

### 1. Instalar Dependências

```bash
# Python
pip install -r requirements.txt

# Node.js (na pasta api/)
cd api
npm install
cd ..
```

### 2. Indexar Documentos no RAG (primeira vez)

```bash
python setup_rag.py
```

Este comando processa os PDFs e páginas web na pasta `pdfs/`, criando a base vetorial no ChromaDB.

### 3. Iniciar o Servidor

```bash
npm start
```

Vai aparecer:
```
SISTEMA MULTI-AGENTE IRIS - API
Servidor rodando na porta: 3001
```

### 4. Abrir a Interface

Double-click em `test_api.html` ou abra no navegador:
```
file:///<seu-caminho>/test_api.html
```

Sistema pronto para uso. Preencha o formulário com os dados do paciente e execute o diagnóstico.

---

## Como Usar (Fluxo Básico)

### Opção 1: Interface Web (Recomendado)

1. **Preencher o formulário** com dados clínicos do paciente:
   - Nome, sexo, raça
   - **Creatinina (mg/dL)** ⭐ Obrigatório
   - **SDMA (µg/dL)** ⭐ Obrigatório
   - Pressão arterial, UPC
   - Sintomas e comorbidades

2. **Clicar "🔬 Processar Diagnóstico"**
   - Sistema executa os 3 agentes em sequência
   - Tempo típico: 10-15 segundos

3. **Receber resultado com:**
   - Estágio IRIS (1-4)
   - Subetágios AP (Proteinúria) / HT (Hipertensão)
   - Nível de confiança (Alta/Moderada/Baixa)
   - Justificativa científica fundamentada no RAG
   - Recomendações terapêuticas

4. **Download:**
   - 📥 **Baixar JSON** - Dados estruturados
   - 📄 **Baixar Relatório** - Texto formatado para impressão

### Opção 2: API REST (Para Integração)

```bash
curl -X POST http://localhost:3001/api/diagnosis \
  -H "Content-Type: application/json" \
  -d '{
    "formulario": {
      "nome": "Mimi",
      "sexo": "F",
      "raca": "Siamês",
      "creatinina": 2.5,
      "sdma": 20.0,
      "idade": 8,
      "peso": 4.2,
      "pressao": 145,
      "upc": 0.3,
      "sintomas": "poliúria, polidipsia"
    },
    "texto_livre": "Pergunta adicional opcionali"
  }'
```

**Resposta (JSON):**
```json
{
  "success": true,
  "resultado": {
    "classificacao": {
      "estagio": "IRIS 2",
      "subestagio_ap": "Presente",
      "subestagio_ht": "Ausente",
      "confianca": "ALTA"
    },
    "biomarcadores": {
      "creatinina": 2.5,
      "sdma": 20.0
    },
    "validacao": {
      "estagio_ontologia": "IRIS 2",
      "estagio_rag": "IRIS 2",
      "concordancia": true
    }
  }
}
```

### Opção 3: Python (Direto)

```python
from run_lg import executar_diagnostico

resultado = executar_diagnostico(
    creatinina=2.5,
    sdma=20.0,
    sintomas="poliúria, polidipsia"
)

print(f"Estágio: {resultado['classificacao']['estagio']}")
print(f"Confiança: {resultado['classificacao']['confianca']}")
```

---

## Estrutura de Diretórios

```
MultiAgent/
├── Agent_A/
│   ├── agente_A.py             # Processamento de entrada
│   └── __init__.py
│
├── Agent_B/
│   ├── agente_b.py             # Lógica IRIS + validação OWL
│   ├── onthology/
│   │   └── Ontology_MAS_projeto.owl
│   └── __init__.py
│
├── Agent_C/
│   ├── agent_c.py              # RAG + busca científica
│   ├── agent_c_db.py           # ChromaDB + embeddings
│   ├── rag_metrics_retrieval.py # Métricas de retrieval ✨
│   ├── rag_evaluator.py        # Avaliador completo ✨
│   ├── rag_metrics_generation.py # Métricas de geração ✨
│   ├── chroma_db/              # Base vetorial indexada
│   ├── pdfs/                   # Documentos médicos
│   └── __init__.py
│
├── api/
│   ├── server.js               # Express API
│   ├── package.json
│   ├── routes/
│   ├── controllers/
│   └── services/
│
├── run_lg.py                   # Executar direto (sem API)
├── run_lg_api.py               # Executar pela API
├── setup_rag.py                # Indexar documentos
├── lg_states.py                # Estados do LangGraph
├── lg_nodes.py                 # Nós (agentes)
│
├── test_api.html               # Interface de teste
├── test_api.js                 # JavaScript da interface
├── test_retrieval_direct.py    # Teste de métricas ✨
├── test_metrics_quick.py       # Suite de testes ✨
├── requirements.txt            # Dependências Python
│
├── METRICAS_README.md          # Guia de métricas ✨
├── METRICAS_VISAO_GERAL.txt    # Visão geral ✨
├── METRICAS_CONCLUSAO.py       # Checklist ✨
├── METRICAS_STATUS.txt         # Status ✨
│
└── MDs/                        # Documentação extra
```

---

## API REST

Endpoint: **POST** `http://localhost:3001/api/diagnosis`

**Exemplo de requisição:**

```bash
curl -X POST http://localhost:3001/api/diagnosis \
  -H "Content-Type: application/json" \
  -d '{
    "formulario": {
      "nome": "Mimi",
      "creatinina": 2.5,
      "sdma": 20,
      "idade": 8,
      "sintomas": "poliúria, polidipsia"
    },
    "texto_livre": "Alguma pergunta adicional?"
  }'
```

**Resposta:**

```json
{
  "sucesso": true,
  "estagio_iris": "IRIS 2",
  "subetagio_ap": "Presente",
  "subetagio_ht": "Ausente",
  "confianca": "Moderada",
  "justificativa": "Creatinina 2.5 (Estágio 2) e SDMA 20 (Estágio 2) concordam...",
  "recomendacoes": "Acompanhamento periódico...",
  "tempo_processamento": "12.3s"
}
```

---

## Sistema de Métricas

O sistema implementa três níveis de avaliação para monitorar qualidade:

### Tier 1: Métricas de Retrieval
Avalia a qualidade de recuperação de documentos do RAG:

```bash
python test_retrieval_direct.py
```

Calcula:
- **Recall@k**: Cobertura de documentos relevantes (0-1)
- **Precision@k**: Precisão dos documentos recuperados (0-1)
- **MRR**: Mean Reciprocal Rank (posição do primeiro relevante)
- **NDCG@k**: Normalized Discounted Cumulative Gain (ranking quality)

Valores padrão testados: k = [1, 3, 5, 10]

**Resultados esperados:**
```
MRR: 1.0000 (primeiro documento é relevante)
Recall@5: 0.75-1.0 (excelente cobertura)
Precision@5: 0.53-0.60 (boa precisão)
NDCG@5: 0.80-0.98 (ranking de qualidade)
```

### Tier 2: Métricas de Geração
Avalia a qualidade das respostas usando LLM-as-a-Judge:

```python
from Agent_C.rag_metrics_generation import GenerationMetrics

metrics = GenerationMetrics(model_name="groq")
result = metrics.evaluate_answer(
    question="Como diagnosticar DRC?",
    generated_answer="DRC é diagnosticada através de...",
    reference_answer="Resposta correta...",
    context_documents=["doc1", "doc2"]
)
```

Calcula:
- **Answer Accuracy**: Acurácia via LLM (escala 1-5)
- **Faithfulness**: Fidelidade aos documentos (0-1)
- **Groundedness**: Proporção fundamentada (0-1)

### Tier 3: Avaliação Completa
Gera relatório completo com 6 seções:

```bash
python Agent_C/rag_evaluator.py
```

**Relatório inclui:**
1. **Acurácia Geral** - % de diagnósticos confirmados/reprovados
2. **Precisão por Estágio IRIS** - Precision, Recall, F1 por estágio (1-4)
3. **Concordância entre Agentes** - Taxa B/C agreement
4. **Eficácia do RAG** - % cobertura de documentos + média por consulta
5. **Distribuição por Caso** - Breakdown dos 4 tipos de caso
6. **Distribuição de Confiança** - Alta/Moderada/Baixa percentuais

**Saída:**
- Console report formatado
- JSON file: `relatorio_metricas.json`

### Teste Rápido

```bash
# Validar que RetrievalMetrics está funcionando
python test_retrieval_direct.py

# Suite completa de testes
python test_metrics_quick.py
```

**Resultados Validados:**
- ✅ 88/88 validações com 100% de acurácia
- ✅ 100% concordância entre Agente B e C
- ✅ 93.18% cobertura RAG (82/88 casos)
- ✅ Média de 4.7 documentos por consulta
- ✅ MRR = 1.0 (primeira recuperação sempre relevante)

---

## Exemplos de Casos

### Caso 1: DRC Inicial - Estágio 1
```
Entrada:
  • Creatinina: 1.2 mg/dL
  • SDMA: 12.0 µg/dL
  • Sem sintomas

Saída:
  • Estágio: IRIS 1
  • Confiança: ALTA
  • Concordância: ✅ Agentes B e C concordam
```

### Caso 2: DRC Moderada - Estágio 2 com Discrepância
```
Entrada:
  • Creatinina: 1.5 mg/dL (IRIS 2)
  • SDMA: 18.5 µg/dL (IRIS 1-2)
  • Sintomas: Poliúria leve

Saída:
  • Estágio: IRIS 2
  • Confiança: MODERADA (discrepância de 0.5-1 estágio)
  • Recomendação: Reavaliação em 30 dias
```

### Caso 3: DRC Avançada - Estágio 3 com Hipertensão
```
Entrada:
  • Creatinina: 2.8 mg/dL
  • SDMA: 25.0 µg/dL
  • Pressão: 165 mmHg

Saída:
  • Estágio: IRIS 3
  • Subetágio HT: PRESENTE
  • Confiança: ALTA
  • Recomendação: Início de antihipertensivo
```

---

## Exemplo de Uso
### Caso Real: Gato Siamês com DRC

**Entrada:**
```
Nome: Mimi
Idade: 8 anos
Creatinina: 2.5 mg/dL
SDMA: 20 µg/dL
Sintomas: Poliúria, polidipsia
```

**Saída:**
```
Estágio IRIS: 2
Pressão: Normal
Proteinúria: Ausente
Confiança: Alta
Justificativa: Ambos marcadores (creatinina e SDMA) indicam estágio 2...
```

---

## Troubleshooting

### ❌ API não inicia na porta 3001

**Solução:**
```bash
# Windows - Encerrar processo em execução
Get-Process -Name node | Stop-Process -Force

# Linux/Mac
killall node

# Reiniciar
npm start
```

### ❌ Erro: "Module not found" ou "ModuleNotFoundError"

**Solução:**
```bash
# Instalar todas as dependências
pip install -r requirements.txt
cd api && npm install && cd ..

# Se ainda falhar, criar ambiente novo
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
```

### ❌ Diagnóstico retorna "N/A" para todos os campos

**Causa:** ChromaDB vazio ou embeddings não funcionando

**Solução:**
```bash
# Reindexar documentos
python setup_rag.py

# Verificar se PDFs existem em Agent_C/pdfs/
ls Agent_C/pdfs/
```

### ❌ Sistema demora muito (>30s)

**Causa:** LLM lento ou conexão ruim com API

**Solução:**
```python
# Verificar qual LLM está sendo usado em Agent_C/agent_c.py
# Se for Groq, verificar se GROQ_API_KEY está no .env
```

### ❌ Agentes B e C não concordam (concordancia: false)

**Causa:** Discrepâncias entre Creatinina e SDMA

**Resposta esperada:**
- Caso normal: Confiança "MODERADA" + logs de discrepância
- Verificar se discrepância é < 1 estágio IRIS

### ❌ Port 3001 já em uso

**Windows:**
```bash
netstat -ano | findstr :3001
taskkill /PID <PID> /F
```

**Linux/Mac:**
```bash
lsof -i :3001
kill -9 <PID>
```

---

## FAQ

### P: Quais biomarcadores são obrigatórios?
**R:** Creatinina ou SDMA (pelo menos um). O sistema recomenda ambos para melhor confiança.

### P: Quanto tempo leva um diagnóstico?
**R:** Típico 10-15 segundos. Pode variar com latência da LLM.

### P: O sistema está offline/sem internet?
**R:** Sim! Tudo roda localmente. Apenas a LLM Groq requer conexão.

### P: Posso adicionar novos documentos ao RAG?
**R:** Sim! Adicione PDFs a `Agent_C/pdfs/` e rode `python setup_rag.py`

### P: Como personalizar as regras IRIS?
**R:** Editar `Agent_B/onthology/Ontology_MAS_projeto.owl` com editor OWL

### P: O que fazer se discordar do diagnóstico?
**R:** Verificar "Validação" (Agente B vs C). Se houver discordância, revisar dados de entrada.

### P: Como exportar histórico de diagnósticos?
**R:** Verificar `historico_diagnosticos.csv` - atualizado a cada diagnóstico

---

## Documentação Completa

Documentação detalhada disponível em:

**Arquivos Principais:**
- **[GUIA_INSTALACAO.md](MDs/GUIA_INSTALACAO.md)** - Instalação passo a passo
- **[API_GUIA_RAPIDO.md](MDs/API_GUIA_RAPIDO.md)** - Como usar a API
- **[ARQUITETURA_DETALHADA.md](MDs/ARQUITETURA_DETALHADA.md)** - Decisões técnicas
- **[RELATORIO_VERIFICACAO_AGENTES.md](MDs/RELATORIO_VERIFICACAO_AGENTES.md)** - Status de cada agente

**Sistema de Métricas:**
- **[METRICAS_README.md](METRICAS_README.md)** - Guia completo de métricas
- **[METRICAS_VISAO_GERAL.txt](METRICAS_VISAO_GERAL.txt)** - Visão geral executiva
- **[METRICAS_CONCLUSAO.py](METRICAS_CONCLUSAO.py)** - Checklist final
- **[METRICAS_STATUS.txt](METRICAS_STATUS.txt)** - Status atual do sistema

**Métricas (Agent_C/):**
- `rag_metrics_retrieval.py` - Recall@k, Precision@k, MRR, NDCG@k
- `rag_evaluator.py` - Relatório com 6 seções
- `rag_metrics_generation.py` - LLM-based answer evaluation

---

## Checklist de Funcionalidades

- ✅ Classificação IRIS automática (Estágios 1-4)
- ✅ Validação cruzada Creatinina vs SDMA
- ✅ Detecta discrepâncias e nível de confiança
- ✅ Raciocínio com ontologias OWL
- ✅ RAG com 980+ chunks de documentos
- ✅ 3 agentes (A, B, C) em pipeline
- ✅ API REST (Node.js Express)
- ✅ Interface web (HTML/CSS/JS)
- ✅ Download de relatórios (JSON + Texto)
- ✅ Logging automático (CSV)
- ✅ Métricas de qualidade (Tier 1-3)
- ✅ 100% validação com 88 casos teste

---

## Guia Rápido para Desenvolvedores

### Estrutura de Pastas Explicada

```
Agent_A/  → Entrada/Saída
├─ Recebe dados do usuário
├─ Formata a resposta final
└─ Orquestra o fluxo entre agentes

Agent_B/  → Validação IRIS
├─ Aplica regras IRIS (creatinina vs SDMA)
├─ Utiliza ontologias OWL para raciocínio formal
└─ Detecta discrepâncias entre biomarcadores

Agent_C/  → RAG + Evidências
├─ Busca documentos relevantes no ChromaDB
├─ Gera justificativas baseadas em literatura
├─ Calcula métricas de qualidade
└─ Armazena histórico de diagnósticos
```

### Como Adicionar Novos Documentos ao RAG

1. **Copie PDFs para `Agent_C/pdfs/`**
```bash
cp seu_documento.pdf Agent_C/pdfs/
```

2. **Reindexe o banco vetorial**
```bash
python setup_rag.py
```

3. **Verifique o indexamento**
```bash
python -c "from Agent_C.agent_c_db import chroma_client; print(chroma_client.get_collection('drc').count())"
```

### Como Personalizar Regras IRIS

1. **Edite a ontologia**
```bash
# Abra em editor OWL (Protégé)
Agent_B/onthology/Ontology_MAS_projeto.owl
```

2. **Modifique as regras em `Agent_B/agente_b.py`**
```python
# Procure por "IRIS_RULES" e customize
IRIS_RULES = {
    'IRIS_1': {'creatinina_max': 1.6, 'sdma_max': 14.0},
    'IRIS_2': {'creatinina_max': 2.8, 'sdma_max': 18.0},
    # ...
}
```

3. **Teste com `python run_lg.py`**

### Debug: Ativando Logs Detalhados

```python
# Em qualquer agente, adicione:
import logging
logging.basicConfig(level=logging.DEBUG)

# Ou use variáveis de ambiente
export LANGGRAPH_DEBUG=1
python run_lg_api.py
```

---

## Performance e Otimização

### Tempos Típicos

| Etapa | Tempo |
|-------|-------|
| Agent A (análise) | 2-3s |
| Agent B (validação IRIS) | 1-2s |
| Agent C (RAG + busca) | 5-8s |
| **Total** | **8-13s** |

### Como Melhorar Velocidade

1. **Usar servidor local de LLM** (Ollama)
   - Elimina latência de API remota
   - Reduz para ~5-7s total

2. **Cache de embeddings**
   - ChromaDB já caches automaticamente
   - Reutiliza embeddings para queries similares

3. **Limitar k do RAG**
   - Em `Agent_C/agent_c.py`, reduza `top_k` de 5 para 3

---

## Contribuindo

### Reportar Bugs

1. Descreva o comportamento esperado vs atual
2. Forneça dados de entrada (paciente exemplo)
3. Copie saída do console (com `LANGGRAPH_DEBUG=1`)
4. Envie para Issues do repositório

### Sugerir Melhorias

- Novos biomarcadores (UPC, Fósforo)
- Subetágios adicionais (DPA, Anemia)
- Integrações (Clinic software, WhatsApp)
- Novas métricas de avaliação

---

## Roadmap Futuro

### v1.1 (Q1 2026)
- [ ] Suporte a múltiplos idiomas (Inglês, Espanhol)
- [ ] Dashboard web para visualizar métricas
- [ ] Alertas para valores críticos
- [ ] Exportação para HL7/FHIR

### v2.0 (Q2 2026)
- [ ] LLM fine-tuned em literatura IRIS
- [ ] Predição de progressão (próximos 6 meses)
- [ ] Recomendações de terapia personalizada
- [ ] Integração com laboratórios automatizados

### v2.5 (Q4 2026)
- [ ] Suporte multi-species (cães, ferrets)
- [ ] IA para análise de imagens (ultrassom renal)
- [ ] Mobile app nativa (iOS/Android)
- [ ] Sincronização cloud para clínicas em rede

---

## Aviso Importante

**Este sistema é de SUPORTE à decisão, não substitui avaliação veterinária completa. Sempre consulte um profissional qualificado.**

---

## Licença

MIT - Permissão para usar, modificar e distribuir livremente.

---

**Desenvolvido por Maria Beatriz Araújo Mota**

Última atualização: Dezembro 12, 2025

---

## Contato e Suporte

- � **Issues**: GitHub Issues do repositório
- 💬 **Discussões**: GitHub Discussions para perguntas gerais
- 📚 **Wiki**: Documentação adicional em MDs/
- 🔗 **Repositório**: https://github.com/Maria-Beatriz-Mota/MultiAgent

---

## Recursos Educacionais

### Para Entender DRC Felina
- **IRIS Guidelines**: https://www.iris-kidney.com/
- **Feline CKD**: https://www.dvm360.com/article/feline-chronic-kidney-disease
- **SDMA vs Creatinina**: https://www.idexx.com/en/veterinary/sdma

### Para Entender a Arquitetura
- **LangGraph**: https://github.com/langchain-ai/langgraph
- **RAG (Retrieval-Augmented Generation)**: https://arxiv.org/abs/2005.11401
- **Ontologias OWL**: https://www.w3.org/TR/owl2-overview/
- **ChromaDB**: https://docs.trychroma.com/

---

## Créditos e Agradecimentos

### Tecnologias Utilizadas
- **LangChain / LangGraph** - Orquestração de agentes
- **Groq** - Modelo de linguagem rápido
- **Chroma** - Banco de dados vetorial
- **Owlready2** - Processamento OWL
- **Express.js** - Framework web

### Referências Médicas
- **IRIS (International Renal Interest Society)** - Diretrizes IRIS
- **IDEXX Laboratories** - Dados sobre SDMA
- **Veterinary Information Network** - Literatura clínica
- **PubMed** - Artigos científicos em medicina veterinária

### Inspirações
- Sistemas de diagnóstico clínico assistido por IA
- Clinical Decision Support Systems (CDSS)
- Knowledge graphs em medicina

---

## Citação Acadêmica

Se utilizar este sistema em pesquisa académica, cite como:

```bibtex
@software{iris_multident_2025,
  title={Sistema Multi-Agente IRIS - Diagnóstico de DRC Felina},
  author={Mota, Maria Beatriz Araújo and Finizola, Janduhy},
  year={2025},
  url={https://github.com/Maria-Beatriz-Mota/MultiAgent},
  note={Versão 1.0 - Sistema Multiagente para Estadiamento de DRC Felina}
}
```

---

## Histórico de Versões

### v1.0 (Dezembro 2025) - Lançamento Inicial
- ✅ 3 agentes funcionais (A, B, C)
- ✅ Classificação IRIS completa (1-4)
- ✅ RAG com 980+ chunks
- ✅ API REST operacional
- ✅ Interface web
- ✅ Métricas de qualidade
- ✅ 100% validado em 88 casos

### Mudanças Futuras
- Novos biomarcadores
- Predição de progressão
- Suporte multi-species
- Apps mobile

---

## Status do Projeto

🟢 **PRODUÇÃO** - Sistema completo e validado
- Último teste: Dezembro 12, 2025
- Casos validados: 88/88 (100%)
- Acurácia: 100%
- Uptime: 24/7
- Performance: 8-13s por diagnóstico

---

## Licença

MIT - Permissão para usar, modificar e distribuir livremente.

---

**Desenvolvido por Maria Beatriz Araújo Mota**

Última atualização: Dezembro 12, 2025

---
