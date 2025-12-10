# 🚀 API Express - Sistema Multi-Agente IRIS

API REST criada com sucesso! A API está pronta para receber requisições do frontend e processar diagnósticos de Doença Renal Crônica (DRC) em gatos.

## ✅ O que foi implementado

### 📁 Estrutura criada:

```
MultiAgent/
├── api/
│   ├── server.js                    # Servidor Express principal
│   ├── config/
│   │   └── config.js                # Configurações centralizadas
│   ├── routes/
│   │   └── diagnosis.js             # Rotas da API
│   ├── controllers/
│   │   └── diagnosisController.js   # Lógica de negócio
│   ├── services/
│   │   └── pythonBridge.js          # Ponte para sistema Python
│   ├── middleware/
│   │   └── validation.js            # Validação de dados com Joi
│   └── README.md                    # Documentação da API
├── run_lg_api.py                    # Script Python otimizado (stdin/stdout)
├── package.json                     # Dependências Node.js
├── .env                            # Configurações (porta 3001)
└── .env.example                    # Template de configuração
```

## 🎯 Como usar

### 1️⃣ Iniciar o servidor

```bash
cd "C:\Users\Maria Beatriz\Desktop\sistema_mas\MultiAgent"
npm start
```

**Saída esperada:**
```
======================================================================
🐱 SISTEMA MULTI-AGENTE IRIS - API
======================================================================
Servidor rodando na porta: 3001
Ambiente: development
URL: http://localhost:3001
Python: python
Script: run_lg_api.py
Timeout: 60000ms
======================================================================
```

### 2️⃣ Endpoints disponíveis

#### `POST /api/diagnosis` - Processar diagnóstico

**URL:** `http://localhost:3001/api/diagnosis`

**Exemplo de requisição:**

```json
{
  "formulario": {
    "nome": "Mimi",
    "sexo": "F",
    "raca": "Siamês",
    "sdma": 18.5,
    "creatinina": 2.3,
    "idade": 8,
    "peso": 4.2,
    "pressao": 145,
    "upc": 0.3,
    "sintomas": "poliúria, polidipsia",
    "comorbidades": "hipertensão"
  },
  "texto_livre": "Qual o estágio da doença renal?"
}
```

**Exemplo de resposta (sucesso):**

```json
{
  "success": true,
  "data": {
    "final_answer": "🩺 Avaliação Clínica – Doença Renal Crônica Felina...",
    "clinical_data": {
      "nome": "Mimi",
      "sexo": "F",
      "creatinina": 2.3,
      "sdma": 18.5,
      ...
    },
    "inference_result": {
      "estagio": "IRIS 2",
      "subestagio_ap": "AP1",
      "subestagio_ht": "HT1",
      ...
    },
    "validated_result": {
      "estagio_final": "IRIS2",
      "caso": 1,
      "confianca": "ALTA",
      ...
    }
  },
  "metadata": {
    "processing_time_ms": 2345,
    "timestamp": "2025-12-10T15:30:45.123Z",
    "total_time_ms": 2350
  }
}
```

**Exemplo de resposta (erro):**

```json
{
  "success": false,
  "error": "Dados insuficientes: SDMA ou Creatinina são obrigatórios"
}
```

#### `GET /api/health` - Health check

**URL:** `http://localhost:3001/api/health`

**Resposta:**

```json
{
  "success": true,
  "status": "healthy",
  "timestamp": "2025-12-10T15:30:45.123Z",
  "uptime": 3600.5,
  "environment": "development"
}
```

#### `GET /` - Documentação da API

**URL:** `http://localhost:3001/`

Retorna informações sobre a API e seus endpoints.

## 🧪 Testar a API

### Opção 1: PowerShell Script

```bash
.\test_api.ps1
```

### Opção 2: cURL (se instalado)

```bash
.\test_api.bat
```

### Opção 3: Node.js Script

```bash
node test_api.js
```

### Opção 4: Postman ou Thunder Client (VS Code)

1. Criar nova requisição POST
2. URL: `http://localhost:3001/api/diagnosis`
3. Headers: `Content-Type: application/json`
4. Body: Colar o JSON de exemplo acima

## ⚙️ Configuração

Arquivo `.env` (já configurado):

```env
PORT=3001                      # Porta do servidor
NODE_ENV=development           # Ambiente
PYTHON_EXECUTABLE=python       # Comando Python
PYTHON_SCRIPT=run_lg_api.py    # Script a executar
PYTHON_TIMEOUT=60000           # Timeout (60 segundos)
CORS_ORIGIN=*                  # Permitir todas origens
LOG_LEVEL=info                 # Nível de log
```

## 📋 Validação de dados

### Campos obrigatórios:
- **SDMA** OU **Creatinina** (pelo menos um é obrigatório)

### Campos opcionais:
- `nome`: string
- `sexo`: "M" ou "F"
- `raca`: string
- `idade`: inteiro (0-30 anos)
- `peso`: float (kg)
- `pressao`: float (mmHg)
- `upc`: float
- `sintomas`: string (separados por vírgula)
- `comorbidades`: string (separados por vírgula)
- `texto_livre`: string (pergunta do usuário)

### Regras de validação:
- Valores numéricos devem ser positivos
- Sexo aceita apenas "M" ou "F"
- Idade máxima: 30 anos
- Peso máximo: 50 kg
- Pressão máxima: 300 mmHg
- UPC máximo: 50

## 🔄 Fluxo de execução

```
Frontend
  ↓ POST /api/diagnosis
Express API (porta 3001)
  ↓ Validação (Joi)
diagnosisController
  ↓
pythonBridge.executePythonDiagnosis()
  ↓ spawn('python', ['run_lg_api.py'])
  ↓ stdin: JSON
Python Multi-Agent System
  ↓ Agente A → Agente B → Agente C
  ↓ stdout: JSON
pythonBridge (parse resultado)
  ↓
Response JSON
  ↓
Frontend
```

## 🛠️ Tecnologias utilizadas

### Backend (Node.js):
- **Express** 4.18.2 - Framework web
- **Joi** 17.11.0 - Validação de schemas
- **CORS** 2.8.5 - Cross-Origin Resource Sharing
- **dotenv** 16.3.1 - Variáveis de ambiente

### Python:
- **LangGraph** - Orquestração de agentes
- **Owlready2** - Ontologia OWL
- **HermiT** - Reasoner ontológico
- **ChromaDB** - RAG (Retrieval-Augmented Generation)

## 📊 Códigos de erro

| Código | Descrição |
|--------|-----------|
| `TIMEOUT` | Processamento excedeu 60 segundos |
| `EXECUTION_ERROR` | Falha ao executar Python |
| `PYTHON_ERROR` | Erro durante execução do Python |
| `PROCESSING_ERROR` | Erro no processamento do diagnóstico |
| `PARSE_ERROR` | Resposta inválida do Python |
| `STDIN_ERROR` | Erro ao enviar dados para Python |

## 🚨 Troubleshooting

### Servidor não inicia

**Erro:** `EADDRINUSE: address already in use :::3001`

**Solução:** Porta 3001 já está em uso
```bash
# Verificar processo usando a porta
netstat -ano | findstr :3001

# Matar processo (substitua PID)
taskkill /PID <PID> /F
```

### Python não encontrado

**Erro:** `ENOENT: no such file or directory, spawn python`

**Solução:** Configure o caminho correto no `.env`:
```env
PYTHON_EXECUTABLE=C:\Python310\python.exe
```

### Módulo Python não encontrado

**Erro:** `ModuleNotFoundError: No module named 'langchain'`

**Solução:** Instale as dependências Python:
```bash
pip install -r requirements.txt
```

## 🔐 Segurança (produção)

Para ambiente de produção, considere:

1. **Autenticação**: Adicionar API keys
2. **Rate limiting**: Limitar requisições por IP
3. **CORS específico**: Definir domínios permitidos
4. **HTTPS**: Usar certificado SSL
5. **Logging**: Integrar com serviço de logs
6. **Monitoring**: Adicionar métricas e alertas

## 📝 Próximos passos

### Frontend Integration:

```javascript
// Exemplo de integração no frontend
async function diagnosticarGato(formulario, pergunta) {
  try {
    const response = await fetch('http://localhost:3001/api/diagnosis', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        formulario: formulario,
        texto_livre: pergunta
      })
    });

    const data = await response.json();

    if (data.success) {
      // Processar resultado
      console.log('Estágio:', data.data.validated_result.estagio_final);
      console.log('Resposta:', data.data.final_answer);
    } else {
      // Tratar erro
      console.error('Erro:', data.error);
    }
  } catch (error) {
    console.error('Erro de conexão:', error);
  }
}
```

## 📞 Suporte

- **Documentação completa**: `api/README.md`
- **Logs do servidor**: Console do terminal
- **Logs Python**: Capturam em `data.logs` (modo debug)

---

## ✨ Recursos implementados

✅ Servidor Express na porta 3001  
✅ Validação robusta com Joi  
✅ Ponte Python otimizada (stdin/stdout)  
✅ Tratamento de erros completo  
✅ Timeout configurável (60s)  
✅ CORS habilitado  
✅ Logging detalhado  
✅ Health check endpoint  
✅ Documentação completa  
✅ Scripts de teste  
✅ Graceful shutdown  

**A API está pronta para uso! 🚀**
