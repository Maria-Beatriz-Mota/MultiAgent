# Alternativas de LLM para o Sistema Multi-Agente

## 🎯 Opções disponíveis (do mais simples ao mais avançado)

### ✅ **Opção 1: Google FLAN-T5 (ATUAL - Recomendada)**
```python
repo_id="google/flan-t5-large"
```
- ✅ **Gratuita** via HuggingFace
- ✅ Rápida e estável
- ✅ Boa para textos técnicos
- ⚠️ Respostas mais curtas

### 🚀 **Opção 2: OpenAI GPT (Melhor qualidade)**

Instalar: `pip install langchain-openai`

```python
# No agente_A.py, substituir o bloco de LLM por:
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-3.5-turbo",  # ou "gpt-4" para melhor qualidade
    temperature=0.2,
    api_key=os.environ.get("OPENAI_API_KEY")
)
```

**Vantagens:**
- ✅ Melhor qualidade de resposta
- ✅ Explicações mais naturais e detalhadas
- ⚠️ Requer API key paga ($0.002/1k tokens)

**Como obter API key:**
1. Criar conta em https://platform.openai.com/
2. Ir em API Keys
3. Criar nova key
4. Definir variável: `$env:OPENAI_API_KEY="sk-..."`

---

### 🌟 **Opção 3: Anthropic Claude (Excelente para medicina)**

Instalar: `pip install langchain-anthropic`

```python
from langchain_anthropic import ChatAnthropic

llm = ChatAnthropic(
    model="claude-3-haiku-20240307",  # Rápido e barato
    temperature=0.2,
    api_key=os.environ.get("ANTHROPIC_API_KEY")
)
```

**Vantagens:**
- ✅ Excelente para textos médicos/científicos
- ✅ Contexto grande (200k tokens)
- ⚠️ Requer API key paga

---

### 💻 **Opção 4: Ollama (100% Local e Gratuito)**

Instalar Ollama: https://ollama.ai/download

```bash
# Baixar modelo (escolher um):
ollama pull llama3.2:3b      # Leve (2GB)
ollama pull mistral:7b       # Médio (4GB)
ollama pull llama3.1:8b      # Pesado (8GB)
```

No código Python:
```python
# pip install langchain-ollama
from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="llama3.2:3b",
    temperature=0.2
)
```

**Vantagens:**
- ✅ Totalmente gratuito
- ✅ Privacidade (roda localmente)
- ✅ Sem limite de uso
- ⚠️ Requer GPU ou CPU potente
- ⚠️ Ocupa espaço em disco

---

### 🔧 **Opção 5: Groq (Extremamente Rápido)**

Instalar: `pip install langchain-groq`

```python
from langchain_groq import ChatGroq

llm = ChatGroq(
    model="mixtral-8x7b-32768",
    temperature=0.2,
    api_key=os.environ.get("GROQ_API_KEY")
)
```

**Vantagens:**
- ✅ MUITO rápido (inferência em segundos)
- ✅ Tier gratuito generoso
- ✅ Fácil de usar

**Como obter API key:**
1. Criar conta em https://console.groq.com/
2. Gerar API key
3. Definir: `$env:GROQ_API_KEY="gsk_..."`

---

## 📊 Comparação Rápida

| Opção | Custo | Velocidade | Qualidade | Instalação |
|-------|-------|-----------|-----------|------------|
| FLAN-T5 (atual) | Grátis | ⭐⭐⭐ | ⭐⭐⭐ | ✅ Simples |
| OpenAI GPT | Pago | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ Simples |
| Claude | Pago | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ Simples |
| Ollama | Grátis | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⚠️ Requer install |
| Groq | Grátis | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ Simples |

---

## 🎯 Recomendação por caso de uso

### Para Desenvolvimento/Testes:
→ **FLAN-T5** (já configurado) ou **Groq** (grátis e rápido)

### Para Produção (melhor qualidade):
→ **OpenAI GPT-3.5** (barato) ou **GPT-4** (melhor)

### Para Privacidade/Dados Sensíveis:
→ **Ollama** (100% local)

### Para Demonstrações:
→ **Groq** (muito rápido, impressiona)

---

## 🔄 Como trocar de modelo

1. Escolher uma das opções acima
2. Instalar biblioteca necessária (`pip install ...`)
3. Obter API key (se necessário)
4. Substituir bloco de configuração no `agente_A.py`
5. Testar com `python run_lg.py`
