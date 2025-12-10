# 📂 Guia de Arquivos Python do Projeto
**O que é ESSENCIAL vs AUXILIAR/OPCIONAL**

---

## ✅ **ARQUIVOS ESSENCIAIS (CORE DO SISTEMA)**
**Estes arquivos SÃO NECESSÁRIOS para o sistema funcionar**

### **1. Sistema Multi-Agente (LangGraph)**
| Arquivo | Função | Status |
|---------|--------|--------|
| `run_lg.py` | 🚀 **PRINCIPAL** - Executa o sistema completo | ✅ ESSENCIAL |
| `lg_states.py` | Estado compartilhado (MASState) | ✅ ESSENCIAL |
| `lg_nodes.py` | Nós do LangGraph (A_entrada, B, C, A_saida) | ✅ ESSENCIAL |

**Dependências:**
```python
run_lg.py
  ├── lg_states.py     # Define MASState
  ├── lg_nodes.py      # Define nodes do grafo
  │   ├── Agent_A/agente_A.py
  │   ├── Agent_B/agente_b.py
  │   └── Agent_C/agent_c.py
```

---

### **2. Agentes Especializados**
| Arquivo | Função | Status |
|---------|--------|--------|
| `Agent_A/agente_A.py` | Agente A - Interface e formatação | ✅ ESSENCIAL |
| `Agent_B/agente_b.py` | Agente B - Inferência ontológica | ✅ ESSENCIAL |
| `Agent_C/agent_c.py` | Agente C - Validação RAG (lógica) | ✅ ESSENCIAL |
| `Agent_C/agent_c_db.py` | Agente C - Funções RAG (Chroma DB) | ✅ ESSENCIAL |
| `Agent_C/csv_utils.py` | Utilidades para CSV (auditoria) | ✅ ESSENCIAL |
| `Agent_A/__init__.py` | Módulo Python | ✅ ESSENCIAL |
| `Agent_B/__init__.py` | Módulo Python | ✅ ESSENCIAL |
| `Agent_C/__init__.py` | Módulo Python | ✅ ESSENCIAL |

---

### **3. Setup Inicial**
| Arquivo | Função | Status |
|---------|--------|--------|
| `setup_rag.py` | ⚙️ Setup inicial do RAG (indexar PDFs) | ⚠️ **USAR UMA VEZ** |
| `indexar_urls.py` | Indexar URLs (alternativa aos PDFs) | ⚠️ **OPCIONAL** |

**Uso:**
```bash
# RODAR UMA VEZ no início (já foi rodado):
python setup_rag.py

# Depois disso, NÃO precisa rodar novamente
# O Chroma DB já está criado em Agent_C/chroma_db/
```

---

## 🧪 **ARQUIVOS DE TESTE/VALIDAÇÃO**
**Úteis para avaliação, mas NÃO necessários para sistema funcionar**

| Arquivo | Função | Status |
|---------|--------|--------|
| `test_system_performance.py` | 📊 Testes de performance (8 casos) | 🧪 TESTE/VALIDAÇÃO |
| `test_csv_save.py` | Testa salvamento CSV | 🧪 TESTE |
| `teste_saida.py` | Testa formatação de saída | 🧪 TESTE |

**Quando usar:**
- ✅ Para **demonstrar métricas** no relatório/vídeo
- ✅ Para **validar** que o sistema está funcionando
- ❌ **NÃO precisa** rodar para usar o sistema normalmente

---

## 🎨 **ARQUIVOS AUXILIARES (DOCUMENTAÇÃO/DIAGRAMAS)**
**Criados para facilitar demonstração e documentação**

| Arquivo | Função | Status |
|---------|--------|--------|
| `gerar_diagrama.py` | Gera diagrama PNG do LangGraph | 📊 AUXILIAR |
| `gerar_diagrama_detalhado.py` | Gera diagrama Mermaid/ASCII/MD | 📊 AUXILIAR |
| `extrair_projeto.py` | Extrai texto do PDF do projeto | 📄 AUXILIAR |
| `Agent_B/verifica_onto.py` | Script de validação da ontologia | 🧪 AUXILIAR |

**Detalhes:**
- **`gerar_diagrama*.py`**: Usados para criar os diagramas que estão no relatório
  - ✅ **Já foram executados** → diagramas gerados
  - ❌ **Não precisa rodar novamente** (a menos que queira atualizar diagramas)

- **`extrair_projeto.py`**: Usado para ler o PDF do projeto inicialmente
  - ❌ **Não é mais necessário** (projeto já foi lido)

- **`Agent_B/verifica_onto.py`**: Script de teste da ontologia
  - ⚠️ **Tem bug** (caminho errado: `Ontology_MAS_pro_teste1.owl`)
  - ✅ **Não afeta sistema** (não é usado pelo `run_lg.py`)
  - 📝 **Pode ser ignorado ou corrigido** (não é crítico)

- **`Agent_C/agent_c_db.py`**: Versão antiga do Agent C

---

## ❓ **ARQUIVOS DUVIDOSOS**

### **`graph.py`** ⚠️
```python
# Conteúdo: Exemplo simples de LangGraph
# Status: NÃO É USADO pelo sistema
```

**Análise:**
- ❌ **NÃO é importado** por nenhum arquivo principal
- ❌ **NÃO é necessário** para o sistema funcionar
- 📝 **Parece ser** um arquivo de exemplo/rascunho inicial
- ✅ **PODE SER DELETADO** sem afetar o sistema

---

## 🗂️ **RESUMO - O QUE MANTER**

### **✅ MANTER (ESSENCIAIS):**
```
MultiAgent/
├── run_lg.py                    # ⭐ PRINCIPAL
├── lg_states.py                 # ⭐ ESSENCIAL
├── lg_nodes.py                  # ⭐ ESSENCIAL
├── setup_rag.py                 # ⚙️ Setup inicial (já usado)
│
├── Agent_A/
│   ├── __init__.py             # ⭐ ESSENCIAL
│   └── agente_A.py             # ⭐ ESSENCIAL
│
├── Agent_B/
│   ├── __init__.py             # ⭐ ESSENCIAL
│   ├── agente_b.py             # ⭐ ESSENCIAL
│   └── onthology/
│       └── Ontology_MAS_projeto.owl  # ⭐ ESSENCIAL
│
└── Agent_C/
    ├── __init__.py             # ⭐ ESSENCIAL
├── Agent_C/
    ├── __init__.py             # ⭐ ESSENCIAL
    ├── agent_c.py              # ⭐ ESSENCIAL (lógica)
    ├── agent_c_db.py           # ⭐ ESSENCIAL (RAG/Chroma)
    ├── csv_utils.py            # ⭐ ESSENCIAL
    ├── pdfs/                   # ⭐ ESSENCIAL (5 PDFs)
    └── chroma_db/              # ⭐ ESSENCIAL (banco vetorial)
### **🧪 MANTER (PARA DEMONSTRAÇÃO):**
```
├── test_system_performance.py   # 📊 Métricas para relatório
├── gerar_diagrama.py            # 🎨 Gera diagramas (já usado)
├── gerar_diagrama_detalhado.py  # 🎨 Gera diagramas (já usado)
```

### **❌ PODE DELETAR (OPCIONAL/DEPRECATED):**
```
├── graph.py                     # ❌ Exemplo não usado
├── test_csv_save.py             # ❌ Teste simples
├── teste_saida.py               # ❌ Teste simples
├── extrair_projeto.py           # ❌ Já foi usado
├── indexar_urls.py              # ❌ Alternativa não usada
├── Agent_B/verifica_onto.py     # ⚠️ Tem bug, não é usado

---

## 🎯 **RECOMENDAÇÃO FINAL**

### **Para ENTREGA do projeto:**

#### **OPÇÃO 1: Manter tudo (mais seguro)**
✅ Mantém todos os arquivos, mesmo os não essenciais  
✅ Mostra todo o processo de desenvolvimento  
✅ Não precisa fazer nada  

#### **OPÇÃO 2: Limpar (mais profissional)**
✅ Deletar arquivos não usados  
✅ Deixar apenas os essenciais + documentação  
✅ Projeto mais limpo e organizado  

**Se escolher OPÇÃO 2, deletar:**
```bash
# Arquivos para deletar:
graph.py
test_csv_save.py
teste_saida.py
extrair_projeto.py
indexar_urls.py
Agent_B/verifica_onto.py
```

---

## 🚀 **COMO EXECUTAR O SISTEMA (ARQUIVOS NECESSÁRIOS)**

### **Execução Normal:**
```bash
# APENAS 1 comando necessário:
python run_lg.py

# Internamente chama:
# - lg_states.py (estado)
# - lg_nodes.py (nós)
#   - Agent_A/agente_A.py
#   - Agent_B/agente_b.py
#   - Agent_C/agent_c.py (que importa agent_c_db.py)
```

### **Testes de Performance:**
```bash
# Opcional - para gerar métricas:
python test_system_performance.py
```

### **Gerar Diagramas:**
```bash
# Opcional - para atualizar diagramas:
python gerar_diagrama.py
python gerar_diagrama_detalhado.py
```

---

## ✅ **CONCLUSÃO**

**Para o sistema funcionar, você precisa de:**
1. ✅ **3 arquivos principais**: `run_lg.py`, `lg_states.py`, `lg_nodes.py`
2. ✅ **4 arquivos dos agentes**: `agente_A.py`, `agente_b.py`, `agent_c.py`, `agent_c_db.py`
3. ✅ **Ontologia OWL**: `Ontology_MAS_projeto.owl`
4. ✅ **Base RAG**: 5 PDFs + Chroma DB

**Todos os outros arquivos são:**
- 🧪 Testes/validação (opcional)
- 🎨 Geração de diagramas (opcional)
- ❌ Deprecated/não usados (pode deletar)

**Minha recomendação:** Mantenha tudo por segurança, mas saiba que `graph.py` e `agent_c_db.py` não são usados pelo sistema final.
