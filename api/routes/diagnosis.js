/**
 * Rotas de diagnóstico
 */

const express = require('express');
const router = express.Router();
const { processDiagnosis, healthCheck } = require('../controllers/diagnosisController');
const { validateDiagnosisRequest } = require('../middleware/validation');

/**
 * POST /api/diagnosis
 * Processa diagnóstico IRIS para gatos
 */
router.post('/diagnosis', validateDiagnosisRequest, processDiagnosis);

/**
 * GET /api/health
 * Health check da API
 */
router.get('/health', healthCheck);

module.exports = router;
