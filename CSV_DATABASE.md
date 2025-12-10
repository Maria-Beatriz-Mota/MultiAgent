# 💾 Sistema de Banco de Dados CSV - Validações

## 🎯 Funcionalidade

O Agente C agora salva **automaticamente** todas as validações bem-sucedidas em um arquivo CSV, criando um banco de dados histórico de casos.

---

## 📊 Estrutura do CSV

### Arquivo: `Agent_C/validations_database.csv`

### Colunas:

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| `timestamp` | Data e hora da validação | `2025-12-09 14:30:45` |
| `creatinina` | Valor de creatinina (mg/dL) | `2.4` |
| `sdma` | Valor de SDMA (µg/dL) | `23.0` |
| `estagio_b` | Estágio inferido pelo Agente B | `IRIS2` |
| `estagio_rag` | Estágio validado por RAG | `IRIS2` |
| `estagio_final` | Estágio final confirmado | `IRIS2` |
| `validacao` | Status da validação | `Confirmada` |
| `caso` | Número do caso (1-4) | `1` |
| `confianca` | Nível de confiança | `ALTA` |
| `pergunta_usuario` | Pergunta feita pelo usuário | `qual o tratamento?` |
| `resposta_fornecida` | Resposta do RAG | `Treatment includes...` |
| `num_docs_rag` | Nº de docs recuperados | `3` |
| `regra_aplicada` | RAG ou Regras IRIS | `RAG` |

---

## ✅ Quando é salvo?

### **Salva automaticamente quando:**
- ✅ Validação confirmada (Caso 1)
- ✅ Validação inconclusiva mas válida (Caso 2)
- ✅ Confiança ALTA ou MODERADA

### **NÃO salva quando:**
- ❌ Discrepância detectada (Caso 3)
- ❌ Dados insuficientes (Caso 4)
- ❌ Validação reprovada

---

## 🔧 Utilitários Disponíveis

### **Arquivo:** `Agent_C/csv_utils.py`

### 1. **Visualizar Estatísticas**
```bash
python Agent_C/csv_utils.py stats
```

**Output:**
```
📊 ESTATÍSTICAS DO BANCO DE DADOS DE VALIDAÇÕES
================================================================

📝 Total de validações: 25

🎯 Distribuição por estágio IRIS:
IRIS2    12
IRIS3     8
IRIS1     3
IRIS4     2

✅ Distribuição por validação:
Confirmada      20
Inconclusiva     5

📈 Estatísticas de Creatinina:
  Média: 2.45 mg/dL
  Mínimo: 1.2 mg/dL
  Máximo: 5.8 mg/dL
```

---

### 2. **Buscar Casos Similares**
```bash
python Agent_C/csv_utils.py buscar 2.4 23
```

Busca casos com valores similares (±30%) de creatinina e SDMA.

---

### 3. **Exportar para Excel**
```bash
python Agent_C/csv_utils.py export
```

Cria arquivo `validations_export.xlsx` para análise em Excel.

---

### 4. **Limpar Banco de Dados**
```bash
python Agent_C/csv_utils.py clear
```

Remove o arquivo CSV (pede confirmação).

---

## 📈 Uso Programático

### Em Python:

```python
from Agent_C.csv_utils import ler_validacoes, buscar_casos_similares

# Ler todas validações
df = ler_validacoes()
print(df.head())

# Buscar casos similares
casos = buscar_casos_similares(creatinina=2.5, sdma=22)
print(f"Encontrados {len(casos)} casos similares")

# Estatísticas
from Agent_C.csv_utils import estatisticas_validacoes
estatisticas_validacoes()
```

---

## 🎯 Casos de Uso

### 1. **Análise Retrospectiva**
Ver quais foram os casos mais comuns tratados pelo sistema.

### 2. **Validação do Sistema**
Comparar decisões do sistema ao longo do tempo.

### 3. **Machine Learning Futuro**
Usar dados históricos para treinar modelos preditivos.

### 4. **Auditoria Clínica**
Revisão de casos para garantia de qualidade.

### 5. **Pesquisa**
Análise de padrões em pacientes felinos com DRC.

---

## 📝 Exemplo de Registro

```csv
timestamp,creatinina,sdma,estagio_b,estagio_rag,estagio_final,validacao,caso,confianca,pergunta_usuario,resposta_fornecida,num_docs_rag,regra_aplicada
2025-12-09 14:30:45,2.4,23.0,IRIS2,IRIS2,IRIS2,Confirmada,1,ALTA,qual o tratamento?,Baseado na literatura IRIS: Treatment includes...,3,RAG
2025-12-09 15:15:22,3.2,28.0,IRIS3,IRIS3,IRIS3,Confirmada,1,ALTA,,,,5,RAG
2025-12-09 16:45:10,1.8,20.0,IRIS2,,IRIS2,Inconclusiva,2,MODERADA,tem risco?,,0,Regras IRIS
```

---

## 🛠️ Configuração

### Alterar localização do CSV:

No arquivo `Agent_C/agent_c.py`:
```python
CSV_DATABASE_PATH = Path("seu_caminho/validations.csv")
```

### Alterar colunas salvas:

Modificar `CSV_HEADERS` no `agent_c.py`.

---

## 🔒 Privacidade

- ⚠️ **Atenção:** O CSV contém dados clínicos
- 🔐 Armazene em local seguro
- 📋 Considere LGPD/GDPR se aplicável
- 🗑️ Implemente política de retenção de dados

---

## 📊 Análise com Pandas

```python
import pandas as pd

# Ler dados
df = pd.read_csv("Agent_C/validations_database.csv")

# Filtrar por estágio
iris2_cases = df[df['estagio_final'] == 'IRIS2']

# Média de creatinina por estágio
df.groupby('estagio_final')['creatinina'].mean()

# Casos com perguntas respondidas
with_questions = df[df['pergunta_usuario'] != '']

# Validações nos últimos 7 dias
df['timestamp'] = pd.to_datetime(df['timestamp'])
last_week = df[df['timestamp'] >= pd.Timestamp.now() - pd.Timedelta(days=7)]
```

---

## ✅ Benefícios

1. **Histórico Completo**: Todos casos validados registrados
2. **Análise de Tendências**: Visualizar padrões ao longo do tempo
3. **Auditoria**: Rastreabilidade de decisões
4. **Pesquisa**: Base de dados para estudos
5. **Melhoria Contínua**: Identificar áreas de melhoria do sistema

---

## 🔄 Backup Automático

Considere implementar backup automático:

```bash
# No Windows (Task Scheduler)
copy Agent_C\validations_database.csv Backup\validations_%date%.csv

# No Linux (cron)
0 0 * * * cp Agent_C/validations_database.csv /backup/validations_$(date +\%Y\%m\%d).csv
```
