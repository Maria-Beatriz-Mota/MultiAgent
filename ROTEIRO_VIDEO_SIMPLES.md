# 🎥 Roteiro de Vídeo - Demonstração Prática do Sistema MAS
**Duração: 5-6 minutos**  
**Objetivo: Mostrar a aplicação funcionando**

---

## 📋 **PREPARAÇÃO (antes de gravar)**

### 1. Arquivos para abrir no VS Code:
- `run_lg.py` (arquivo principal)
- `Agent_B/agente_b.py` (mostrar reasoner)
- `Agent_C/agent_c.py` (mostrar RAG)
- `lg_nodes.py` (mostrar fluxo LangGraph)

### 2. Terminal preparado:
```powershell
cd C:\Users\Maria Beatriz\Desktop\sistema_mas\MultiAgent
python run_lg.py
```

### 3. Ter pronto para mostrar:
- Diagrama `arquitetura_sistema_mas.png` aberto
- Notebook `demonstracao_reasoner_dl.ipynb` aberto (não precisa rodar, só mostrar)
- Arquivo `.owl` na pasta `Agent_B/onthology/`

---

## 🎬 **ROTEIRO DO VÍDEO**

### **[0:00-0:30] INTRODUÇÃO (30 seg)**
**O que falar:**
> "Olá! Vou demonstrar o sistema multi-agente que desenvolvemos para classificação de insuficiência renal crônica em gatos, seguindo o protocolo IRIS. O sistema combina três tecnologias: ontologia OWL 2 DL com reasoner, sistema RAG para validação de guidelines, e agentes LLM orquestrados pelo LangGraph."

**O que mostrar:**
- VS Code com a estrutura de pastas do projeto
- Mostrar rapidamente: `Agent_A/`, `Agent_B/`, `Agent_C/`

---

### **[0:30-1:30] ARQUITETURA (1 min)**
**O que falar:**
> "A arquitetura tem três agentes especializados. O Agente A é a interface com o usuário, extrai dados clínicos e formata respostas. O Agente B faz inferência ontológica usando a ontologia OWL com 83 classes e reasoner HermiT. O Agente C valida os resultados usando RAG com embeddings de 5 PDFs das diretrizes IRIS."

**O que mostrar:**
1. Abrir `arquitetura_sistema_mas.png` (diagrama)
2. Abrir `lg_nodes.py` e mostrar os 4 nós:
   - `node_agente_a_entrada`
   - `node_agente_b`
   - `node_agente_c`
   - `node_agente_a_saida`
3. Mostrar `lg_states.py` (estado compartilhado entre agentes)

---

### **[1:30-2:30] ONTOLOGIA + REASONER (1 min)**
**O que falar:**
> "A ontologia tem 83 classes organizadas hierarquicamente, 52 propriedades e 473 axiomas. Usamos o reasoner HermiT para fazer inferências automáticas. Por exemplo, se um gato tem creatinina 2.5 e SDMA 28, o reasoner infere automaticamente que é IRIS estágio 3."

**O que mostrar:**
1. Abrir `Agent_B/onthology/Ontology_MAS_projeto.owl` no VS Code
2. Mostrar algumas classes (buscar "IRIS" no arquivo)
3. Abrir `Agent_B/agente_b.py` e mostrar:
   - Linha ~20: `sync_reasoner_hermit`
   - Função `classificar_estagio_iris_com_validacao()`
4. Mostrar notebook `demonstracao_reasoner_dl.ipynb` (só a estrutura, não precisa executar)

---

### **[2:30-3:30] SISTEMA RAG (1 min)**
**O que falar:**
> "O sistema RAG usa Chroma DB com 450 chunks indexados de 5 PDFs das diretrizes IRIS. Quando há dúvida ou discrepância, o Agente C busca nos documentos e retorna a resposta sempre com citação da fonte."

**O que mostrar:**
1. Mostrar pasta `Agent_C/pdfs/` com os PDFs
2. Mostrar pasta `Agent_C/chroma_db/` (banco vetorial)
3. Abrir `Agent_C/agent_c.py` e mostrar:
   - Função `rag_search()` (busca semântica)
   - `salvar_validacao_csv()` (auditoria)
4. Mostrar arquivo `Agent_C/validations_database.csv` com registros

---

### **[3:30-5:30] DEMONSTRAÇÃO PRÁTICA (2 min)**
**O que falar:**
> "Agora vou executar o sistema com casos reais."

**O que fazer:**

#### **Caso 1: Classificação Normal** (45 seg)
```powershell
python run_lg.py
```
Quando pedir entrada, digitar:
```json
{
  "sdma": 18,
  "creatinina": 2.0,
  "idade": 8,
  "peso": 4.5
}
```
**Explicar enquanto roda:**
> "Aqui o sistema está processando: Agente A extrai os dados, Agente B faz a inferência ontológica, Agente C valida com RAG, e Agente A formata a resposta final."

**Mostrar resultado:**
- Estágio IRIS classificado
- Justificativa com citações
- Recomendações clínicas

#### **Caso 2: Discrepância Detectada** (45 seg)
Rodar novamente com:
```json
{
  "sdma": 55,
  "creatinina": 1.5,
  "idade": 10,
  "peso": 3.8
}
```
**Explicar:**
> "Neste caso há uma discrepância grande: creatinina sugere IRIS 1, mas SDMA sugere IRIS 4. O sistema detecta automaticamente e aciona o Agente C para consultar as diretrizes IRIS e resolver a ambiguidade."

**Mostrar resultado:**
- Alerta de discrepância
- Consulta ao RAG
- Resposta com citação do protocolo IRIS

#### **Caso 3: Pergunta Livre** (30 seg)
Rodar com pergunta em texto:
```
"O que significa proteinúria borderline em gatos com IRC?"
```
**Explicar:**
> "O sistema também aceita perguntas livres. O Agente C busca na base de conhecimento e retorna a resposta com citação."

---

### **[5:30-6:00] ENCERRAMENTO (30 seg)**
**O que falar:**
> "O sistema está completo e funcional. Todos os requisitos foram atendidos: ontologia OWL 2 DL com reasoner, RAG híbrido, três agentes especializados, orquestração com LangGraph, e respostas sempre com citações. O código está documentado e testado com 10 casos de teste alcançando 90% de concordância com as diretrizes IRIS. Obrigada!"

**O que mostrar:**
- Mostrar rapidamente `CHECKLIST_PROJETO_COMPLETO.md` ou `RELATORIO_TECNICO.md`
- Fechar com o diagrama da arquitetura na tela

---

## ✅ **CHECKLIST PRÉ-GRAVAÇÃO**

- [ ] Fechar abas desnecessárias no navegador
- [ ] Limpar terminal (histórico de comandos antigos)
- [ ] Testar `python run_lg.py` uma vez antes de gravar
- [ ] Verificar que APIs estão funcionando (OpenAI/Groq)
- [ ] Desligar notificações do Windows
- [ ] Volume do microfone testado
- [ ] Tela em resolução clara (1920x1080 se possível)

---

## 🎯 **DICAS DE GRAVAÇÃO**

1. **Use o OBS Studio ou gravador de tela do Windows** (Win + G)
2. **Fale devagar e com clareza** - não precisa ser perfeito
3. **Se errar, não pare** - pode editar depois ou refazer só aquela parte
4. **Mostre o código rodando** - mais importante que explicações longas
5. **Tempo total ideal: 5-6 minutos** - se passar de 7 min, está bom também
6. **Não precisa mostrar erro** - use casos que você já testou que funcionam

---

## 📤 **APÓS GRAVAR**

1. Salvar vídeo como: `Demo_Sistema_MAS_IRC_Felina.mp4`
2. Upload para YouTube (pode ser não listado) ou Google Drive
3. Adicionar link no README.md do repositório
4. Incluir no relatório técnico final

---

**Boa sorte! 🎬 O vídeo vai ficar ótimo! 🚀**
