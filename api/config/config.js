/**
 * Configurações da API
 */

require('dotenv').config();

module.exports = {
  // Servidor
  PORT: process.env.PORT || 3001,
  NODE_ENV: process.env.NODE_ENV || 'development',
  
  // Python
  PYTHON_EXECUTABLE: process.env.PYTHON_EXECUTABLE || 'python',
  PYTHON_SCRIPT: process.env.PYTHON_SCRIPT || 'run_lg_api.py',
  PYTHON_TIMEOUT: parseInt(process.env.PYTHON_TIMEOUT || '60000'), // 60 segundos
  
  // API
  MAX_PAYLOAD_SIZE: process.env.MAX_PAYLOAD_SIZE || '1mb',
  CORS_ORIGIN: process.env.CORS_ORIGIN || '*',
  
  // Logging
  LOG_LEVEL: process.env.LOG_LEVEL || 'info',
  
  // Rate limiting (opcional, para implementação futura)
  RATE_LIMIT_WINDOW_MS: 15 * 60 * 1000, // 15 minutos
  RATE_LIMIT_MAX_REQUESTS: 100 // máximo de requisições por janela
};
