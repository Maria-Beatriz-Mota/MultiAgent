/**
 * Serviço de registro de diagnósticos em CSV
 */

const createCsvWriter = require('csv-writer').createObjectCsvWriter;
const fs = require('fs');
const path = require('path');

const CSV_PATH = path.join(__dirname, '../../historico_diagnosticos.csv');

// Definir colunas do CSV
const CSV_HEADERS = [
  { id: 'data_hora', title: 'Data/Hora' },
  { id: 'nome', title: 'Nome' },
  { id: 'raca', title: 'Raça' },
  { id: 'estagio', title: 'Estágio' },
  { id: 'sintomas', title: 'Sintomas' },
  { id: 'comorbidade', title: 'Comorbidade' },
  { id: 'idoso', title: 'Idoso' },
  { id: 'subestagio_proteinuria', title: 'Subetágio Proteinúria' },
  { id: 'subestagio_hipertensao', title: 'Subetágio Hipertensão' },
  { id: 'tratamento', title: 'Tratamento' },
  { id: 'observacoes', title: 'Observações' }
];

/**
 * Inicializa o arquivo CSV se não existir
 */
function inicializarCSV() {
  if (!fs.existsSync(CSV_PATH)) {
    const csvWriter = createCsvWriter({
      path: CSV_PATH,
      header: CSV_HEADERS,
      encoding: 'utf8',
      append: false
    });
    
    // Criar arquivo vazio com cabeçalhos
    csvWriter.writeRecords([]).catch(err => {
      console.error('[CSV] Erro ao criar arquivo:', err);
    });
  }
}

/**
 * Adiciona registro de diagnóstico ao CSV
 * @param {Object} diagnostico - Dados completos do diagnóstico
 * @returns {Promise<void>}
 */
async function salvarDiagnosticoCSV(diagnostico) {
  try {
    inicializarCSV();

    const dados = diagnostico.formulario || {};
    const resultado = diagnostico.resultado || {};
    const classificacao = resultado.classificacao || {};
    const recomendacoes = resultado.recomendacoes || [];

    // Formatar data/hora
    const agora = new Date();
    const dataHora = `${agora.toLocaleDateString('pt-BR')} ${agora.toLocaleTimeString('pt-BR')}`;

    // Preparar registro
    const registro = {
      data_hora: dataHora,
      nome: dados.nome || 'Não informado',
      raca: dados.raca || 'SRD',
      estagio: classificacao.estagio || 'N/A',
      sintomas: dados.sintomas || 'Não informado',
      comorbidade: dados.comorbidades || 'Nenhuma',
      idoso: dados.idade >= 10 ? 'Sim' : 'Não',
      subestagio_proteinuria: classificacao.subestagio_ap || 'N/A',
      subestagio_hipertensao: classificacao.subestagio_ht || 'N/A',
      tratamento: recomendacoes.length > 0 ? recomendacoes.join('; ') : 'Sem recomendações',
      observacoes: `Confiança: ${classificacao.confianca || 'N/A'}, SDMA: ${dados.sdma || 'N/A'}, Creatinina: ${dados.creatinina || 'N/A'}`
    };

    // Escrever no CSV
    const csvWriter = createCsvWriter({
      path: CSV_PATH,
      header: CSV_HEADERS,
      encoding: 'utf8',
      append: true
    });

    await csvWriter.writeRecords([registro]);
    
    console.log('[CSV] Diagnóstico salvo com sucesso:', {
      data_hora: dataHora,
      nome: registro.nome,
      estagio: registro.estagio
    });

    return CSV_PATH;

  } catch (error) {
    console.error('[CSV] Erro ao salvar diagnóstico:', error);
    throw error;
  }
}

/**
 * Retorna o caminho do arquivo CSV
 * @returns {string}
 */
function getCSVPath() {
  return CSV_PATH;
}

module.exports = {
  salvarDiagnosticoCSV,
  getCSVPath,
  inicializarCSV
};
