/**
 * Servidor Express - API para Sistema Multi-Agente IRIS
 * 
 * Endpoints:
 * - POST /api/diagnosis - Processa diagnóstico
 * - GET /api/health - Health check
 */

const express = require('express');
const cors = require('cors');
const config = require('./config/config');
const diagnosisRoutes = require('./routes/diagnosis');
const { errorHandler, notFoundHandler } = require('./middleware/validation');

// Criar aplicação Express
const app = express();

// =====================================================================
// MIDDLEWARES
// =====================================================================

// CORS
app.use(cors({
  origin: config.CORS_ORIGIN,
  credentials: true
}));

// Body parser
app.use(express.json({ limit: config.MAX_PAYLOAD_SIZE }));
app.use(express.urlencoded({ extended: true, limit: config.MAX_PAYLOAD_SIZE }));

// Request logging
app.use((req, res, next) => {
  console.log(`[${new Date().toISOString()}] ${req.method} ${req.path}`);
  next();
});

// =====================================================================
// ROTAS
// =====================================================================

// Rota raiz
app.get('/', (req, res) => {
  res.json({
    name: 'Sistema Multi-Agente IRIS - API',
    version: '1.0.0',
    description: 'API para diagnóstico de Doença Renal Crônica em Gatos (DRC)',
    endpoints: {
      diagnosis: 'POST /api/diagnosis',
      health: 'GET /api/health'
    },
    documentation: {
      diagnosis: {
        method: 'POST',
        path: '/api/diagnosis',
        body: {
          formulario: {
            nome: 'string (opcional)',
            sexo: 'string (M/F, opcional)',
            raca: 'string (opcional)',
            sdma: 'float (µg/dL, obrigatório se não houver creatinina)',
            creatinina: 'float (mg/dL, obrigatório se não houver SDMA)',
            idade: 'integer (anos, opcional)',
            peso: 'float (kg, opcional)',
            pressao: 'float (mmHg, opcional)',
            upc: 'float (opcional)',
            sintomas: 'string (separados por vírgula, opcional)',
            comorbidades: 'string (separados por vírgula, opcional)'
          },
          texto_livre: 'string (pergunta do usuário, opcional)'
        }
      }
    }
  });
});

// Rotas da API
app.use('/api', diagnosisRoutes);

// =====================================================================
// TRATAMENTO DE ERROS
// =====================================================================

// 404 - Rota não encontrada
app.use(notFoundHandler);

// Error handler global
app.use(errorHandler);

// =====================================================================
// INICIALIZAÇÃO DO SERVIDOR
// =====================================================================

function startServer() {
  const server = app.listen(config.PORT, () => {
    console.log('='.repeat(70));
    console.log('🐱 SISTEMA MULTI-AGENTE IRIS - API');
    console.log('='.repeat(70));
    console.log(`Servidor rodando na porta: ${config.PORT}`);
    console.log(`Ambiente: ${config.NODE_ENV}`);
    console.log(`URL: http://localhost:${config.PORT}`);
    console.log(`Python: ${config.PYTHON_EXECUTABLE}`);
    console.log(`Script: ${config.PYTHON_SCRIPT}`);
    console.log(`Timeout: ${config.PYTHON_TIMEOUT}ms`);
    console.log('='.repeat(70));
  });

  // Graceful shutdown
  process.on('SIGTERM', () => {
    console.log('\n[SERVER] SIGTERM recebido, encerrando...');
    server.close(() => {
      console.log('[SERVER] Servidor encerrado');
      process.exit(0);
    });
  });

  process.on('SIGINT', () => {
    console.log('\n[SERVER] SIGINT recebido, encerrando...');
    server.close(() => {
      console.log('[SERVER] Servidor encerrado');
      process.exit(0);
    });
  });

  return server;
}

// Iniciar se executado diretamente
if (require.main === module) {
  startServer();
}

module.exports = { app, startServer };
