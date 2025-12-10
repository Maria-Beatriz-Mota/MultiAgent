# 🎬 Roteiro para Vídeo Demo - Sistema Multi-Agente IRIS

**Duração**: 6-7 minutos  
**Prazo**: Sexta-feira (entrega)  
**Tempo para gravar**: ~2h (quarta à noite)

---

## 🎯 Estrutura do Vídeo

### [00:00 - 00:45] INTRODUÇÃO (45s)
**O que mostrar**:
- Tela inicial: "Sistema Multi-Agente para Diagnóstico IRIS em Gatos"
- "Por: Maria Beatriz Mota e Janduhy Finizola"

**O que falar**:
> "Olá, vou apresentar nosso sistema multi-agente para classificação automática de Insuficiência Renal Crônica em gatos, baseado nas diretrizes IRIS 2023. O sistema integra uma ontologia OWL com 83 classes, RAG híbrido e 3 agentes inteligentes orquestrados via LangGraph."

**Arquivo para mostrar**: 
- `arquitetura_sistema_mas.png` (diagrama recém-gerado)
- Ou abrir `CHECKLIST_PROJETO_COMPLETO.md` (seção arquitetura)

---

### [00:45 - 02:30] CENÁRIO 1: Caso Normal - IRIS 3 (1min 45s)

**Preparação**:
```bash
# Abrir terminal
cd C:\Users\Maria Beatriz\Desktop\sistema_mas\MultiAgent
python run_lg.py
```

**Input para digitar**:
```
Gato Felix, macho, 10 anos, 3.8 kg
Creatinina: 3.5 mg/dL
SDMA: 22 µg/dL
Pressão: 155 mmHg
UPC: 0.3
```

**O que falar**:
> "Vamos testar com um caso real. Gato de 10 anos com creatinina 3.5 e SDMA 22. 
> Observem o fluxo: Agente A extrai os dados, Agente B usa a ontologia e o reasoner Pellet para classificar como IRIS 3, e o Agente C valida consultando as diretrizes IRIS no RAG. 
> O sistema retorna: IRIS 3 (DRC moderada), subestágios AP1 e HT1, com citação das fontes."

**Mostrar na tela**:
- Output do terminal com cada agente executando
- Destacar: "IRIS 3", "Concordância B vs C", "Citações"

---

### [02:30 - 04:00] CENÁRIO 2: Discrepância Crítica (1min 30s)

**Input para digitar**:
```
Gato Luna, fêmea, 8 anos
Creatinina: 1.5 mg/dL
SDMA: 50 µg/dL
```

**O que falar**:
> "Agora um caso problemático: creatinina sugere IRIS 1, mas SDMA sugere IRIS 4 - uma discrepância de 3 estágios! 
> O sistema detecta automaticamente que algo está errado e RECUSA classificar, recomendando repetir os exames. 
> Isso previne diagnósticos incorretos por erro laboratorial."

**Mostrar na tela**:
- Mensagem de ERRO do Agente B
- "Discrepância crítica detectada"
- "Recomendação: repetir exames"

---

### [04:00 - 05:30] CENÁRIO 3: LangGraph Studio Visualização (1min 30s)

**Preparação**:
```bash
# Abrir em outra aba do terminal
langgraph dev
```
Depois abrir navegador: `http://localhost:8123`

**O que mostrar**:
1. Interface do LangGraph Studio
2. Colar o input do Cenário 1
3. Clicar em "Run"
4. Mostrar:
   - Fluxo visual dos nós (A → B → C → A)
   - Estado em cada etapa (inspecionar `clinical_data`, `inference_result`)
   - Tempo de execução de cada agente

**O que falar**:
> "O LangGraph Studio permite visualizar o fluxo em tempo real. 
> Aqui vemos cada agente executando, o estado sendo passado entre eles, e podemos inspecionar os dados intermediários. 
> Isso é essencial para debug e entender como o sistema chegou àquela conclusão."

---

### [05:30 - 06:30] DEMONSTRAÇÃO DA VALIDAÇÃO CRUZADA (1min)

**Arquivo para abrir**: 
`Agent_C/validations_database.csv`

**O que mostrar**:
- Abrir CSV no Excel ou VS Code
- Mostrar colunas: `estagio_b`, `estagio_rag`, `validacao`, `confianca`
- Filtrar casos com `validacao = "CONCORDÂNCIA"`

**O que falar**:
> "Toda classificação é auditável. O sistema salva em CSV: o resultado da ontologia (Agente B), o resultado do RAG (Agente C), se houve concordância e o nível de confiança. 
> Em nossos testes, obtivemos 85% de concordância entre ontologia e RAG, e 90% de precisão geral comparado às diretrizes IRIS oficiais."

---

### [06:30 - 07:00] CONCLUSÃO E MÉTRICAS (30s)

**Arquivo para mostrar**: 
- `CHECKLIST_PROJETO_COMPLETO.md` (seção "Estimativa de Nota")
- Ou slide com métricas:

```
📊 RESULTADOS:
✅ 83 classes na ontologia
✅ 473 axiomas validados (0 erros)
✅ 90% concordância com IRIS
✅ 85% validação cruzada B vs C
✅ 100% detecção de discrepâncias
```

**O que falar**:
> "Em resumo: desenvolvemos um sistema robusto que combina raciocínio lógico formal via ontologia, busca semântica via RAG, e validação cruzada para reduzir erros. 
> O sistema é rastreável, auditável e pode ser expandido para outras doenças veterinárias. 
> Obrigado!"

---

## 🎥 Dicas de Gravação (para quarta à noite)

### Ferramentas:
- **Windows**: Win+G (gravador nativo)
- **OBS Studio**: https://obsproject.com/ (melhor qualidade)
- **Loom**: https://loom.com (fácil e online)

### Configurações:
1. **Resolução**: 1920x1080 (Full HD)
2. **Qualidade**: Boa (não precisa ser perfeita)
3. **Audio**: Fale claro e pausadamente
4. **Enquadramento**: Mostrar terminal + código

### Checklist Pré-Gravação:
- [ ] Fechar programas desnecessários
- [ ] Aumentar fonte do terminal (Ctrl + +)
- [ ] Testar audio (gravar 10s de teste)
- [ ] Preparar inputs dos 3 cenários (copiar/colar)
- [ ] Abrir arquivos antecipadamente:
  - `arquitetura_sistema_mas.png`
  - `Agent_C/validations_database.csv`
  - `CHECKLIST_PROJETO_COMPLETO.md`

### Plano B (se algo der errado):
- **Sem LangGraph Studio?** → Mostrar só terminal (ok!)
- **Erro ao executar?** → Mostrar código + explicar funcionamento
- **Nervosismo?** → Grave em partes e junte depois

---

## ⏱️ Timeline Quarta-Feira (hoje)

| Horário | Atividade | Duração |
|---------|-----------|---------|
| 18:00-18:30 | Revisar roteiro, testar sistema | 30min |
| 18:30-19:00 | Gravar tentativa 1 | 30min |
| 19:00-19:15 | Assistir e identificar erros | 15min |
| 19:15-19:45 | Gravar versão final | 30min |
| 19:45-20:00 | Editar/juntar (se necessário) | 15min |
| 20:00 | ✅ Upload e descansar | - |

**Total**: ~2 horas

---

## 📤 Onde Fazer Upload

- **YouTube** (não listado/privado): Mais fácil
- **Google Drive**: Compartilhar link
- **OneDrive**: Se tiver conta UPE

---

## 🚀 Depois do Vídeo (Quinta-Feira)

Com vídeo pronto, você terá **100%** do projeto! 

Se sobrar tempo:
- [ ] Escrever artigo curto (4 páginas) para +20%
- [ ] Adicionar cache na ontologia (melhoria técnica)
- [ ] Documento formal de CQs

Mas **NÃO É OBRIGATÓRIO**. Foca no vídeo primeiro! 💪

---

**BOA SORTE! Você consegue! 🎬🎉**
