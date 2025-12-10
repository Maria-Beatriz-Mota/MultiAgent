/**
 * Controller para diagnóstico IRIS
 */

const { executePythonDiagnosis, PythonBridgeError } = require('../services/pythonBridge');

/**
 * POST /api/diagnosis
 * Processa requisição de diagnóstico
 */
async function processDiagnosis(req, res, next) {
  const startTime = Date.now();
  
  try {
    const { formulario, texto_livre } = req.body;

    console.log('[DIAGNOSIS] Nova requisição:', {
      timestamp: new Date().toISOString(),
      hasFormulario: !!formulario,
      hasTextoLivre: !!texto_livre,
      sdma: formulario?.sdma,
      creatinina: formulario?.creatinina
    });

    // Executar sistema Python
    const result = await executePythonDiagnosis({
      formulario,
      texto_livre: texto_livre || ''
    });

    // Resposta bem-sucedida formatada
    const response = {
      success: true,
      resultado: result.resultado,
      resposta_completa: result.resposta_completa,
      metadata: {
        ...result.metadata,
        total_time_ms: Date.now() - startTime,
        timestamp: new Date().toISOString()
      }
    };

    // Incluir dados completos apenas em modo desenvolvimento
    if (process.env.NODE_ENV === 'development') {
      response.dados_completos = result.dados_completos;
    }

    res.json(response);

    console.log('[DIAGNOSIS] Sucesso:', {
      totalTime: `${Date.now() - startTime}ms`,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('[DIAGNOSIS] Erro:', {
      message: error.message,
      code: error.code,
      timestamp: new Date().toISOString()
    });

    // Erro específico do Python Bridge
    if (error instanceof PythonBridgeError) {
      const statusCode = error.code === 'TIMEOUT' ? 504 : 500;
      
      return res.status(statusCode).json({
        success: false,
        error: error.message,
        code: error.code,
        ...(process.env.NODE_ENV === 'development' && { details: error.details })
      });
    }

    // Erro genérico
    next(error);
  }
}

/**
 * GET /api/health
 * Health check da API
 */
function healthCheck(req, res) {
  res.json({
    success: true,
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    environment: process.env.NODE_ENV || 'development'
  });
}

module.exports = {
  processDiagnosis,
  healthCheck
};
