<<<<<<< HEAD
# MultiAgent
=======
# Sistema Multi-Agente para Diagnóstico IRIS em Gatos 🐱

Sistema de suporte à decisão clínica para classificação de Doença Renal Crônica (DRC) em gatos segundo diretrizes IRIS.

## 🏗️ Arquitetura

```
Usuário → [Agente A] → [Agente B] → [Agente C] → [Agente A] → Resposta
          Extração     Ontologia    Validação     Formatação
          de dados     + Reasoner   + RAG
```

### Agentes:

- **Agente A**: Processa input do usuário, extrai parâmetros clínicos, formata resposta final
- **Agente B**: Inferência ontológica usando OWL + Pellet reasoner
- **Agente C**: Validação com RAG (Retrieval-Augmented Generation) das diretrizes IRIS

## 📋 Pré-requisitos

### Software necessário:
1. **Python 3.10+**
2. **Java JDK 8+** (para o reasoner Pellet)
   ```bash
   # Verificar se Java está instalado
   java -version
   ```

### Verificar Java:
```bash
# Windows
java -version

# Instalar se necessário:
# https://www.oracle.com/java/technologies/downloads/
```

## 🚀 Instalação

### 1. Clone ou baixe o projeto

```bash
cd C:\Users\Maria Beatriz\Desktop\Projeto_MAS
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

### 3. Configure a base de conhecimento (RAG)

```bash
python setup_rag.py
```

Coloque os PDFs das diretrizes IRIS em:
```
Projeto_MAS/Agent_C/pdfs/
```

### 4. Verifique a ontologia

Certifique-se que a ontologia OWL está em:
```
Projeto_MAS/Agent_B/onthology/ONTHOLOGY_MAS.owl
```

## 💻 Uso

### Método 1: Linha de comando

```bash
python run_lg.py
```

Exemplo de input:
```
Gato com creatinina 3.5, SDMA 22, pressão 165
```

### Método 2: LangGraph Studio (Recomendado)

```bash
langgraph dev
```

Acesse `http://localhost:8123` no navegador

O Studio permite:
- ✅ Visualizar o fluxo entre agentes em tempo real
- ✅ Inspecionar o estado em cada etapa
- ✅ Debug interativo
- ✅ Replay de execuções

## 📊 Estrutura do Projeto

```
Projeto_MAS/
├── langgraph.json          # Configuração do LangGraph Studio
├── requirements.txt        # Dependências Python
├── setup_rag.py           # Script de setup do RAG
├── run_lg.py              # Ponto de entrada principal
├── lg_states.py           # Definição do estado compartilhado
├── lg_nodes.py            # Nodes do grafo
├── Agent_A/
│   ├── __init__.py
│   └── agente_A.py        # Processamento de entrada/saída
├── Agent_B/
│   ├── __init__.py
│   ├── agente_b.py        # Inferência ontológica
│   └── onthology/
│       └── ONTHOLOGY_MAS.owl
└── Agent_C/
    ├── __init__.py
    ├── agent_c.py         # Validação + RAG
    ├── agent_c_db.py      # Gerenciamento da base vetorial
    ├── pdfs/              # Documentos IRIS (você adiciona)
    └── chroma_db/         # Base vetorial (gerada automaticamente)
```

## 🔄 Fluxo de Execução

### 1. Agente A (Entrada)
- Recebe texto livre do usuário
- Extrai parâmetros: creatinina, SDMA, pressão, UPC, etc.
- Valida dados básicos

### 2. Agente B (Ontologia)
- Cria instância do paciente na ontologia
- Executa reasoner Pellet
- **CRÍTICO**: Deve inferir estágio IRIS (1-4)

### 3. Agente C (Validação + RAG)

Implementa 4 cenários:

1. **✅ Ontologia OK + RAG consistente**
   - Valida estágio com diretrizes IRIS
   - Resposta completa e validada

2. **⚠️ Ontologia OK + RAG inconsistente**
   - Detecta divergência
   - Usa valor do RAG (mais confiável)
   - Alerta sobre inconsistência

3. **🔄 Ontologia FALHOU + RAG tem info**
   - Usa apenas diretrizes IRIS
   - Sem inferência ontológica

4. **❌ Ontologia FALHOU + RAG sem info**
   - Falha completa
   - Solicita dados melhores

### 4. Agente A (Saída)
- Formata resposta amigável
- Inclui:
  - Estágio IRIS
  - Substágios (proteinúria, hipertensão)
  - Risco global
  - Alertas clínicos
  - Plano terapêutico sugerido

## 🧪 Testando

### Teste rápido:

```python
from run_lg import run_pipeline

resultado = run_pipeline("Gato com creatinina 4.2 e SDMA 28")
print(resultado)
```

### Casos de teste sugeridos:

1. **IRIS 1** (inicial):
   ```
   creatinina: 1.4, SDMA: 16
   ```

2. **IRIS 2** (leve):
   ```
   creatinina: 2.5, SDMA: 20
   ```

3. **IRIS 3** (moderada):
   ```
   creatinina: 3.5, SDMA: 28, pressão: 165
   ```

4. **IRIS 4** (severa):
   ```
   creatinina: 6.0, SDMA: 45, UPC: 0.8
   ```

## 🐛 Resolução de Problemas

### Erro: "cannot import name 'validate_inference'"
- **Causa**: Função não existe mais
- **Solução**: Use o código atualizado dos artifacts

### Erro: "Reasoner falhou"
- **Causa**: Java não instalado ou ontologia com erros
- **Solução**: 
  1. Verifique Java: `java -version`
  2. Valide ontologia no Protégé

### Erro: "Base vetorial não disponível"
- **Causa**: RAG não configurado
- **Solução**: Execute `python setup_rag.py`

### Ontologia não infere estágio
- **Verificar**: Classes e propriedades na ontologia
- **Verificar**: Valores de creatinina/SDMA válidos
- **Fallback**: Sistema usa cálculo clínico direto

## 📚 Diretrizes IRIS

O sistema implementa as diretrizes oficiais:
- **Estágios** (1-4): Baseados em creatinina e SDMA
- **Substágios**:
  - Proteinúria (UPC): < 0.2 / 0.2-0.4 / > 0.4
  - Hipertensão (PAS): < 150 / 150-159 / 160-179 / ≥ 180

Referência: [IRIS Kidney - International Renal Interest Society](http://www.iris-kidney.com/)

## ⚠️ Avisos Importantes

1. **Esta é uma ferramenta de SUPORTE à decisão clínica**
2. **NÃO substitui avaliação veterinária completa**
3. **Sempre consulte médico-veterinário**
4. **Para uso educacional e pesquisa**

## 📝 Licença

Projeto acadêmico - Mestrado em Inteligência Computacional

## 👥 Contato

Para dúvidas sobre o sistema, consulte a documentação ou abra uma issue.
>>>>>>> 740e5dc4bdac0368a9338fedba4877f5bc86beee
