# 📂 Proposta de Reorganização do Projeto

## 🎯 **OBJETIVO**
Organizar arquivos em pastas lógicas para melhor navegação e apresentação profissional.

---

## 📊 **ESTRUTURA ATUAL (Desorganizada)**
```
MultiAgent/
├── (57 arquivos misturados na raiz!)
├── Agent_A/
├── Agent_B/
└── Agent_C/
```

---

## ✨ **ESTRUTURA PROPOSTA (Organizada)**

```
MultiAgent/
│
├── 📄 README.md                          # Documentação principal
├── 📄 requirements.txt                   # Dependências
├── .env                                  # Configurações
├── .gitignore
│
├── 🚀 src/                               # CÓDIGO PRINCIPAL
│   ├── run_lg.py                         # ⭐ Arquivo principal
│   ├── lg_states.py                      # Estados LangGraph
│   ├── lg_nodes.py                       # Nós LangGraph
│   ├── setup_rag.py                      # Setup inicial RAG
│   ├── __init__.py
│   │
│   ├── Agent_A/                          # Agente Interface
│   │   ├── __init__.py
│   │   └── agente_A.py
│   │
│   ├── Agent_B/                          # Agente Ontológico
│   │   ├── __init__.py
│   │   ├── agente_b.py
│   │   ├── verifica_onto.py
│   │   └── onthology/
│   │       └── Ontology_MAS_projeto.owl
│   │
│   └── Agent_C/                          # Agente RAG
│       ├── __init__.py
│       ├── agent_c.py
│       ├── agent_c_db.py
│       ├── csv_utils.py
│       ├── validations_database.csv
│       ├── pdfs/                         # PDFs IRIS
│       └── chroma_db/                    # Banco vetorial
│
├── 🧪 tests/                             # TESTES
│   ├── test_system_performance.py        # Testes principais (métricas)
│   ├── test_csv_save.py
│   ├── teste_saida.py
│   └── relatorio_desempenho.json         # Resultados dos testes
│
├── 📚 docs/                              # DOCUMENTAÇÃO
│   ├── relatorios/
│   │   ├── RELATORIO_TECNICO.md          # Relatório técnico 8 páginas
│   │   ├── CHECKLIST_PROJETO_COMPLETO.md # Checklist final
│   │   ├── METRICAS_AVALIACAO.md         # Métricas detalhadas
│   │   └── RELATORIO_PARAMETROS.md
│   │
│   ├── guias/
│   │   ├── GUIA_ARQUIVOS_PROJETO.md      # Guia dos arquivos
│   │   ├── ROTEIRO_VIDEO_SIMPLES.md      # Roteiro do vídeo
│   │   ├── INFERENCIA_MANUAL_VS_AUTOMATICA.md
│   │   └── CSV_DATABASE.md
│   │
│   ├── arquitetura/
│   │   ├── ARQUITETURA_DETALHADA.md      # Documentação arquitetura
│   │   ├── ARQUITETURA_DETALHADA.txt     # ASCII diagram
│   │   ├── arquitetura_sistema_mas.png   # Diagrama PNG
│   │   └── diagrama_completo.mmd         # Mermaid source
│   │
│   └── notebooks/
│       └── demonstracao_reasoner_dl.ipynb # Demonstração reasoner
│
├── 🛠️ scripts/                           # SCRIPTS AUXILIARES
│   ├── gerar_diagrama.py                 # Gera diagramas
│   ├── gerar_diagrama_detalhado.py
│   ├── extrair_projeto.py                # Extração PDF
│   ├── indexar_urls.py                   # Indexar URLs
│   └── graph.py                          # Exemplo LangGraph
│
├── 📦 assets/                            # RECURSOS
│   ├── pdfs_projeto/                     # PDFs do projeto
│   ├── figs/                             # Figuras
│   └── projeto_texto.txt                 # Texto extraído
│
└── 🗑️ deprecated/                        # ARQUIVOS ANTIGOS (opcional)
    ├── CHECKLIST_PROJETO.md              # Versão antiga
    ├── ROTEIRO_VIDEO.md                  # Versão antiga
    ├── reademe2.md                       # Duplicado
    ├── CHANGELOG_RAG_QUESTIONS.md
    └── LLM_ALTERNATIVES.md
```

---

## 🎯 **COMANDOS PARA REORGANIZAR**

### **OPÇÃO 1: Reorganização Completa (Recomendada)**

```powershell
# 1. Criar estrutura de pastas
New-Item -ItemType Directory -Force -Path "src", "tests", "docs/relatorios", "docs/guias", "docs/arquitetura", "docs/notebooks", "scripts", "assets", "deprecated"

# 2. Mover CÓDIGO PRINCIPAL para src/
Move-Item -Path "run_lg.py", "lg_states.py", "lg_nodes.py", "setup_rag.py", "__init__.py" -Destination "src/"
Move-Item -Path "Agent_A", "Agent_B", "Agent_C" -Destination "src/"

# 3. Mover TESTES para tests/
Move-Item -Path "test_system_performance.py", "test_csv_save.py", "teste_saida.py", "relatorio_desempenho.json" -Destination "tests/"

# 4. Mover DOCUMENTAÇÃO para docs/
Move-Item -Path "RELATORIO_TECNICO.md", "CHECKLIST_PROJETO_COMPLETO.md", "METRICAS_AVALIACAO.md", "RELATORIO_PARAMETROS.md" -Destination "docs/relatorios/"
Move-Item -Path "GUIA_ARQUIVOS_PROJETO.md", "ROTEIRO_VIDEO_SIMPLES.md", "INFERENCIA_MANUAL_VS_AUTOMATICA.md", "CSV_DATABASE.md" -Destination "docs/guias/"
Move-Item -Path "ARQUITETURA_DETALHADA.md", "ARQUITETURA_DETALHADA.txt", "arquitetura_sistema_mas.png", "diagrama_completo.mmd" -Destination "docs/arquitetura/"
Move-Item -Path "demonstracao_reasoner_dl.ipynb" -Destination "docs/notebooks/"

# 5. Mover SCRIPTS para scripts/
Move-Item -Path "gerar_diagrama.py", "gerar_diagrama_detalhado.py", "extrair_projeto.py", "indexar_urls.py", "graph.py" -Destination "scripts/"

# 6. Mover ASSETS para assets/
Move-Item -Path "pdfs_projeto", "figs", "projeto_texto.txt" -Destination "assets/"

# 7. Mover DEPRECATED para deprecated/
Move-Item -Path "CHECKLIST_PROJETO.md", "ROTEIRO_VIDEO.md", "reademe2.md", "CHANGELOG_RAG_QUESTIONS.md", "LLM_ALTERNATIVES.md" -Destination "deprecated/"

# 8. Arquivos que ficam na raiz (OK)
# README.md, requirements.txt, .env, .gitignore, langg.json
```

---

### **OPÇÃO 2: Reorganização Mínima (Mais Segura)**

```powershell
# Criar apenas pastas essenciais
New-Item -ItemType Directory -Force -Path "docs", "scripts", "tests"

# Mover apenas documentação
Move-Item -Path "RELATORIO_TECNICO.md", "CHECKLIST_PROJETO_COMPLETO.md", "METRICAS_AVALIACAO.md", "ARQUITETURA_DETALHADA.md", "GUIA_ARQUIVOS_PROJETO.md", "ROTEIRO_VIDEO_SIMPLES.md", "demonstracao_reasoner_dl.ipynb", "arquitetura_sistema_mas.png" -Destination "docs/"

# Mover scripts auxiliares
Move-Item -Path "gerar_diagrama.py", "gerar_diagrama_detalhado.py", "extrair_projeto.py", "indexar_urls.py", "graph.py" -Destination "scripts/"

# Mover testes
Move-Item -Path "test_system_performance.py", "test_csv_save.py", "teste_saida.py" -Destination "tests/"
```

---

## ⚠️ **IMPORTANTE: Atualizar Imports!**

Após mover para `src/`, será necessário atualizar:

### **1. Atualizar run_lg.py:**
```python
# Antes:
from lg_states import MASState
from lg_nodes import node_agente_a_entrada, ...

# Depois (se mover para src/):
from src.lg_states import MASState
from src.lg_nodes import node_agente_a_entrada, ...
```

### **2. Atualizar caminhos dos agentes:**
```python
# Em lg_nodes.py
# Antes:
from Agent_A.agente_A import processar_input_usuario
from Agent_B.agente_b import agent_b_inferencia
from Agent_C.agent_c import agent_c_answer

# Depois (se mover para src/):
from src.Agent_A.agente_A import processar_input_usuario
from src.Agent_B.agente_b import agent_b_inferencia
from src.Agent_C.agent_c import agent_c_answer
```

### **3. Atualizar caminhos de arquivos:**
```python
# Agent_B/agente_b.py
# Antes:
ONTO_PATH = Path(r"Agent_B/onthology/Ontology_MAS_projeto.owl")

# Depois:
ONTO_PATH = Path(r"src/Agent_B/onthology/Ontology_MAS_projeto.owl")
```

---

## 🎯 **RECOMENDAÇÃO FINAL**

### **AGORA (Antes da Entrega):**
✅ **OPÇÃO 2 - Reorganização Mínima**
- Menos arriscado
- Não quebra imports
- Já melhora muito a organização
- Tempo: ~15 minutos

### **DEPOIS DA ENTREGA:**
✅ **OPÇÃO 1 - Reorganização Completa**
- Estrutura profissional
- Melhor para portfolio
- Tempo para corrigir imports
- Tempo: ~2 horas

---

## 📋 **CHECKLIST DE REORGANIZAÇÃO**

### **Antes de começar:**
- [ ] ✅ Fazer backup completo do projeto
- [ ] ✅ Commit no Git (se usando)
- [ ] ✅ Testar que sistema funciona: `python run_lg.py`

### **Depois de reorganizar:**
- [ ] Testar novamente: `python run_lg.py` (ou `python src/run_lg.py`)
- [ ] Verificar que testes funcionam
- [ ] Atualizar README.md com nova estrutura
- [ ] Commit das mudanças

---

## 🚀 **PRÓXIMOS PASSOS**

Qual opção você prefere?

1. **OPÇÃO 2 (MÍNIMA)** - Só mover documentação/scripts (RECOMENDADO AGORA)
2. **OPÇÃO 1 (COMPLETA)** - Reorganização total (DEPOIS DA ENTREGA)
3. **DEIXAR COMO ESTÁ** - Focar só no vídeo

**Me diga e eu executo os comandos para você!** 🛠️
