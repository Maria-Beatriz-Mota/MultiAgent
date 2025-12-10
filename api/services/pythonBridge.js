/**
 * Serviço de ponte para o sistema Python
 * Executa o script Python e gerencia a comunicação via stdin/stdout
 */

const { spawn } = require('child_process');
const path = require('path');
const config = require('../config/config');

// Configurar encoding UTF-8 para Windows
const isWindows = process.platform === 'win32';

class PythonBridgeError extends Error {
  constructor(message, code, details) {
    super(message);
    this.name = 'PythonBridgeError';
    this.code = code;
    this.details = details;
  }
}

/**
 * Executa o sistema Python multi-agente
 * @param {Object} data - Dados para enviar ao Python (formulario + texto_livre)
 * @returns {Promise<Object>} - Resultado do processamento
 */
async function executePythonDiagnosis(data) {
  return new Promise((resolve, reject) => {
    const startTime = Date.now();
    
    // Caminho do script Python (relativo à raiz do projeto)
    const projectRoot = path.resolve(__dirname, '../..');
    const scriptPath = path.join(projectRoot, config.PYTHON_SCRIPT);
    
    console.log('[PYTHON] Iniciando processo:', {
      script: scriptPath,
      python: config.PYTHON_EXECUTABLE,
      timestamp: new Date().toISOString()
    });

    // Spawn do processo Python com encoding UTF-8
    // Nota: NÃO usar shell: true, pois quebra caminhos com espaços
    const pythonProcess = spawn(config.PYTHON_EXECUTABLE, [scriptPath], {
      cwd: projectRoot,
      env: { 
        ...process.env,
        PYTHONIOENCODING: 'utf-8',  // Força UTF-8 no Python
        PYTHONUTF8: '1'              // Python 3.7+ UTF-8 mode
      }
    });

    let stdout = '';
    let stderr = '';
    let timedOut = false;

    // Timeout
    const timeout = setTimeout(() => {
      timedOut = true;
      pythonProcess.kill('SIGTERM');
      
      reject(new PythonBridgeError(
        'Timeout: O processamento excedeu o tempo limite',
        'TIMEOUT',
        { 
          timeout: config.PYTHON_TIMEOUT,
          elapsedTime: Date.now() - startTime
        }
      ));
    }, config.PYTHON_TIMEOUT);

    // Capturar stdout
    pythonProcess.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    // Capturar stderr (para logs/debug)
    pythonProcess.stderr.on('data', (data) => {
      stderr += data.toString();
      if (config.LOG_LEVEL === 'debug') {
        console.log('[PYTHON STDERR]', data.toString());
      }
    });

    // Tratamento de erros do processo
    pythonProcess.on('error', (error) => {
      clearTimeout(timeout);
      
      console.error('[PYTHON] Erro ao executar:', error);
      
      reject(new PythonBridgeError(
        'Falha ao executar o script Python',
        'EXECUTION_ERROR',
        { 
          originalError: error.message,
          pythonExecutable: config.PYTHON_EXECUTABLE,
          scriptPath: scriptPath
        }
      ));
    });

    // Processo finalizado
    pythonProcess.on('close', (code) => {
      clearTimeout(timeout);
      
      if (timedOut) return; // Já rejeitado pelo timeout
      
      const processingTime = Date.now() - startTime;
      
      console.log('[PYTHON] Processo finalizado:', {
        exitCode: code,
        processingTime: `${processingTime}ms`,
        stdoutLength: stdout.length,
        stderrLength: stderr.length
      });

      // Erro no processo Python
      if (code !== 0) {
        let errorMessage = 'Erro no processamento do diagnóstico';
        let errorDetails = { exitCode: code, stderr, stdout };

        // Tentar extrair mensagem de erro do stdout (JSON)
        try {
          const result = JSON.parse(stdout);
          if (result.error) {
            errorMessage = result.error;
            errorDetails = { ...errorDetails, ...result };
          }
        } catch (e) {
          // Se não for JSON, usar stderr como mensagem
          if (stderr) {
            errorMessage = stderr.trim().split('\n').pop() || errorMessage;
          }
        }

        return reject(new PythonBridgeError(
          errorMessage,
          'PYTHON_ERROR',
          errorDetails
        ));
      }

      // Sucesso - parsear resultado JSON
      try {
        const result = JSON.parse(stdout);
        
        if (!result.success) {
          return reject(new PythonBridgeError(
            result.error || 'Erro desconhecido no processamento',
            'PROCESSING_ERROR',
            { result, stderr }
          ));
        }

        // Adicionar metadata
        result.metadata = {
          processing_time_ms: processingTime,
          timestamp: new Date().toISOString()
        };

        resolve(result);
        
      } catch (error) {
        console.error('[PYTHON] Erro ao parsear JSON:', error);
        console.error('[PYTHON] stdout:', stdout);
        
        reject(new PythonBridgeError(
          'Resposta inválida do sistema Python',
          'PARSE_ERROR',
          { 
            parseError: error.message,
            stdout: stdout.substring(0, 500), // Primeiros 500 chars
            stderr
          }
        ));
      }
    });

    // Enviar dados via stdin
    try {
      const inputJson = JSON.stringify(data);
      pythonProcess.stdin.write(inputJson);
      pythonProcess.stdin.end();
      
      if (config.LOG_LEVEL === 'debug') {
        console.log('[PYTHON] Dados enviados:', inputJson);
      }
    } catch (error) {
      clearTimeout(timeout);
      pythonProcess.kill();
      
      reject(new PythonBridgeError(
        'Erro ao enviar dados para o processo Python',
        'STDIN_ERROR',
        { originalError: error.message }
      ));
    }
  });
}

module.exports = {
  executePythonDiagnosis,
  PythonBridgeError
};
