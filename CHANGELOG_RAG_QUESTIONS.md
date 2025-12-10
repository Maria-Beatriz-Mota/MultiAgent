# Changelog - Sistema de Perguntas via RAG

## 🎯 Nova Funcionalidade Implementada

### **Agente C agora responde perguntas específicas do usuário usando RAG**

---

## 📋 O que foi adicionado:

### 1. **Função `responder_pergunta_usuario()`**
- Analisa a pergunta do usuário
- Busca resposta nos documentos indexados (RAG)
- Retorna resposta baseada na literatura IRIS

### 2. **Detecção de perguntas médicas relevantes**
Keywords suportadas:
- Tratamento / Treatment / Therapy
- Dieta / Diet / Nutrition
- Sintomas / Symptoms / Signs
- Prognóstico / Prognosis
- Medicação / Medication / Drug
- Monitoramento / Monitoring
- Risco / Risk / Complicação
- Pressão / Hipertensão
- Proteinúria / UPC
- Fósforo / Phosphorus

### 3. **Três cenários de resposta:**

#### ✅ **Cenário 1: Pergunta encontrada nos documentos**
```
RESPOSTA À PERGUNTA:
Baseado na literatura IRIS:

[Trecho relevante extraído dos PDFs]
```

#### ⚠️ **Cenário 2: Pergunta fora do escopo**
```
⚠️ Não há informações disponíveis na base de conhecimento indexada 
para responder esta pergunta. Recomenda-se consultar a literatura 
IRIS oficial ou indexar mais documentos.
```

#### ❌ **Cenário 3: Pergunta não relacionada à medicina**
- Simplesmente ignora (não responde)
- Foca apenas na validação IRIS

---

## 🔄 Fluxo de funcionamento:

```
1. Usuário faz pergunta: "qual o tratamento para IRIS 3?"
   ↓
2. Agente C busca no RAG com k=5 documentos
   ↓
3. Se encontrar contexto relevante:
   → Extrai sentenças relacionadas
   → Adiciona ao resultado: "RESPOSTA À PERGUNTA"
   ↓
4. Se não encontrar:
   → Informa que não há dados
   ↓
5. Resultado vai para Agente A que humaniza com LLM
```

---

## 📊 Exemplos de uso:

### Exemplo 1: Pergunta sobre tratamento
**Input:**
```python
pergunta = "qual o tratamento recomendado?"
```

**Output (se encontrado nos PDFs):**
```
RESPOSTA À PERGUNTA:
Baseado na literatura IRIS:

Treatment for IRIS stage 2 includes renal diet, blood pressure 
monitoring, and proteinuria assessment. Regular follow-up every 
3-6 months is recommended.
```

### Exemplo 2: Pergunta sem resposta
**Input:**
```python
pergunta = "o gato gosta de brincar?"
```

**Output:**
```
(Não responde - pergunta não médica)
```

### Exemplo 3: Pergunta médica sem dados
**Input:**
```python
pergunta = "qual a dose de amlodipina?"
```

**Output:**
```
⚠️ Não há informações disponíveis na base de conhecimento indexada 
para responder esta pergunta. Recomenda-se consultar a literatura 
IRIS oficial ou indexar mais documentos.
```

---

## ⚙️ Parâmetros ajustados:

```python
# Aumentado de k=3 para k=5
rag_result = rag_search(CHROMA_PATH, query, k=5, max_context_length_chars=3000)
```

**Motivo:** Aumentar chances de encontrar resposta relevante

---

## 🧪 Como testar:

1. **Com documentos indexados:**
```bash
python setup_rag.py  # Indexar PDFs primeiro
python run_lg.py
```

2. **Digite perguntas:**
   - "qual o tratamento?"
   - "quais os sintomas?"
   - "qual o prognóstico?"
   - "qual a dieta recomendada?"

3. **Sem documentos:**
   - Sistema informa que não há dados

---

## 🔧 Arquivos modificados:

- `Agent_C/agent_c.py`
  - ✅ Adicionada `responder_pergunta_usuario()`
  - ✅ Integrada no fluxo de validação
  - ✅ Resultado retorna `resposta_pergunta`

---

## 📝 Notas importantes:

1. **RAG precisa estar indexado**: Execute `setup_rag.py` primeiro
2. **Perguntas precisam ser relevantes**: Keywords médicas
3. **Resposta é extraída do PDF**: Não é gerada/inventada
4. **LLM humaniza a resposta**: Agente A torna mais legível
