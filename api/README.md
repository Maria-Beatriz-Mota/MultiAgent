# API Express - Sistema Multi-Agente IRIS

API REST para comunicação entre frontend e sistema Python de diagnóstico de Doença Renal Crônica (DRC) em gatos segundo diretrizes IRIS.

## 🚀 Início Rápido

### Instalação

```bash
# Instalar dependências Node.js
npm install

# Copiar arquivo de configuração
copy .env.example .env

# Iniciar servidor
npm start
```

### Desenvolvimento

```bash
# Modo desenvolvimento com hot-reload
npm run dev
```

## 📡 Endpoints

### `POST /api/diagnosis`

Processa diagnóstico IRIS para gatos.

**Request Body:**
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
  "texto_livre": "O gato está comendo bem?"
}
```

**Response (Success):**
```json
{
  "success": true,
  "data": {
    "final_answer": "...",
    "clinical_data": {...},
    "inference_result": {...},
    "validated_result": {...}
  },
  "metadata": {
    "processing_time_ms": 2345,
    "timestamp": "2025-12-10T15:30:45.123Z",
    "total_time_ms": 2350
  }
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "Mensagem de erro",
  "code": "ERROR_CODE",
  "details": {...}
}
```

**Validação:**
- `sdma` OU `creatinina` são **obrigatórios** (pelo menos um)
- `sexo`: Apenas "M" ou "F"
- Valores numéricos devem ser positivos
- Strings têm limites de tamanho

---

### `GET /api/health`

Health check da API.

**Response:**
```json
{
  "success": true,
  "status": "healthy",
  "timestamp": "2025-12-10T15:30:45.123Z",
  "uptime": 3600.5,
  "environment": "development"
}
```

---

### `GET /`

Documentação básica da API.

## ⚙️ Configuração

Edite o arquivo `.env`:

```env
# Porta do servidor
PORT=3001

# Ambiente (development/production)
NODE_ENV=development

# Executável Python
PYTHON_EXECUTABLE=python

# Script Python a ser executado
PYTHON_SCRIPT=run_lg_api.py

# Timeout em milissegundos (60 segundos)
PYTHON_TIMEOUT=60000

# CORS (permite todos por padrão)
CORS_ORIGIN=*

# Log level (debug/info/warn/error)
LOG_LEVEL=info
```

## 🏗️ Arquitetura

```
api/
├── server.js              # Servidor Express principal
├── config/
│   └── config.js          # Configurações centralizadas
├── routes/
│   └── diagnosis.js       # Rotas da API
├── controllers/
│   └── diagnosisController.js  # Lógica de negócio
├── services/
│   └── pythonBridge.js    # Comunicação com Python
└── middleware/
    └── validation.js      # Validação de dados
```

### Fluxo de Dados

```
Frontend → POST /api/diagnosis
              ↓
    Validação (Joi Schema)
              ↓
    diagnosisController
              ↓
    pythonBridge.executePythonDiagnosis()
              ↓
    spawn('python', ['run_lg_api.py'])
              ↓
    stdin: JSON → Python → stdout: JSON
              ↓
    Parse resultado
              ↓
    Response → Frontend
```

## 🔧 Desenvolvimento

### Estrutura de Erros

A API retorna códigos de erro específicos:

- `TIMEOUT`: Processamento excedeu tempo limite
- `EXECUTION_ERROR`: Falha ao executar script Python
- `PYTHON_ERROR`: Erro durante execução do Python
- `PROCESSING_ERROR`: Erro no processamento do diagnóstico
- `PARSE_ERROR`: Resposta inválida do Python
- `STDIN_ERROR`: Erro ao enviar dados para Python

### Logging

Configure `LOG_LEVEL` no `.env`:

- `debug`: Logs detalhados (inclui stdout/stderr do Python)
- `info`: Logs informativos (padrão)
- `warn`: Apenas avisos
- `error`: Apenas erros

### Timeout

O timeout padrão é 60 segundos. Ajuste via `PYTHON_TIMEOUT` em `.env` se necessário.

## 📝 Exemplo de Uso (cURL)

```bash
curl -X POST http://localhost:3001/api/diagnosis \
  -H "Content-Type: application/json" \
  -d '{
    "formulario": {
      "sdma": 18.5,
      "creatinina": 2.3,
      "idade": 8
    },
    "texto_livre": "Qual o estágio da doença renal?"
  }'
```

## 🐛 Troubleshooting

### Erro: "Python não encontrado"

Configure o caminho correto no `.env`:
```env
PYTHON_EXECUTABLE=C:\Python310\python.exe
```

### Erro: "Módulo não encontrado"

Instale as dependências Python:
```bash
pip install -r requirements.txt
```

### API não inicia

Verifique se a porta 3001 está livre:
```bash
netstat -ano | findstr :3001
```

## 📦 Deploy

Para produção:

1. Configure `.env` para produção:
```env
NODE_ENV=production
LOG_LEVEL=warn
CORS_ORIGIN=https://seu-frontend.com
```

2. Use um process manager como PM2:
```bash
npm install -g pm2
pm2 start api/server.js --name iris-api
```

## 📄 Licença

MIT
