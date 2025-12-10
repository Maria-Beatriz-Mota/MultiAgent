/**
 * Middleware de validação de dados
 */

const Joi = require('joi');

// Schema de validação do formulário
const formularioSchema = Joi.object({
  nome: Joi.string().trim().max(100).optional().allow(''),
  sexo: Joi.string().valid('M', 'F', 'm', 'f', '').optional().allow(''),
  raca: Joi.string().trim().max(100).optional().allow(''),
  sdma: Joi.number().positive().precision(2).optional(),
  creatinina: Joi.number().positive().precision(2).optional(),
  idade: Joi.number().integer().min(0).max(30).optional(),
  peso: Joi.number().positive().max(50).precision(2).optional(),
  pressao: Joi.number().positive().max(300).precision(1).optional(),
  upc: Joi.number().min(0).max(50).precision(2).optional(),
  sintomas: Joi.string().trim().max(500).optional().allow(''),
  comorbidades: Joi.string().trim().max(500).optional().allow('')
}).or('sdma', 'creatinina'); // Pelo menos um dos dois é obrigatório

// Schema completo da requisição
const requestSchema = Joi.object({
  formulario: formularioSchema.required(),
  texto_livre: Joi.string().trim().max(1000).optional().allow('')
});

/**
 * Middleware de validação
 */
const validateDiagnosisRequest = (req, res, next) => {
  const { error, value } = requestSchema.validate(req.body, {
    abortEarly: false,
    stripUnknown: true
  });

  if (error) {
    const errors = error.details.map(detail => ({
      field: detail.path.join('.'),
      message: detail.message
    }));

    return res.status(400).json({
      success: false,
      error: 'Dados inválidos',
      details: errors
    });
  }

  // Normalizar sexo para maiúsculo
  if (value.formulario.sexo) {
    value.formulario.sexo = value.formulario.sexo.toUpperCase();
  }

  // Substituir o body pelo valor validado e normalizado
  req.body = value;
  next();
};

/**
 * Middleware de tratamento de erros
 */
const errorHandler = (err, req, res, next) => {
  console.error('[ERROR]', {
    message: err.message,
    stack: err.stack,
    timestamp: new Date().toISOString()
  });

  // Erro de JSON inválido
  if (err instanceof SyntaxError && err.status === 400 && 'body' in err) {
    return res.status(400).json({
      success: false,
      error: 'JSON inválido',
      message: err.message
    });
  }

  // Erro genérico
  res.status(err.status || 500).json({
    success: false,
    error: err.message || 'Erro interno do servidor',
    ...(process.env.NODE_ENV === 'development' && { stack: err.stack })
  });
};

/**
 * Middleware para rotas não encontradas
 */
const notFoundHandler = (req, res) => {
  res.status(404).json({
    success: false,
    error: 'Rota não encontrada',
    path: req.path
  });
};

module.exports = {
  validateDiagnosisRequest,
  errorHandler,
  notFoundHandler
};
