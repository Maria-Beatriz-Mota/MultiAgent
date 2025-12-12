/**
 * Serviço de geração de PDF para relatórios de diagnóstico IRIS
 */

const PDFDocument = require('pdfkit');
const fs = require('fs');
const path = require('path');

/**
 * Gera PDF com o relatório completo do diagnóstico
 * @param {Object} diagnostico - Dados do diagnóstico
 * @param {string} outputPath - Caminho para salvar o PDF
 * @returns {Promise<string>} - Caminho do arquivo gerado
 */
function gerarPDFDiagnostico(diagnostico, outputPath) {
  return new Promise((resolve, reject) => {
    try {
      const doc = new PDFDocument({
        size: 'A4',
        margins: { top: 50, bottom: 50, left: 50, right: 50 }
      });

      const stream = fs.createWriteStream(outputPath);
      doc.pipe(stream);

      // Cabeçalho
      doc.fontSize(20).fillColor('#667eea').text('Sistema de Diagnóstico IRIS', { align: 'center' });
      doc.fontSize(12).fillColor('#333').text('Doença Renal Crônica em Felinos', { align: 'center' });
      doc.moveDown(2);

      // Data e Hora
      const agora = new Date();
      doc.fontSize(10).fillColor('#666')
         .text(`Data: ${agora.toLocaleDateString('pt-BR')}`, { continued: true })
         .text(`   Hora: ${agora.toLocaleTimeString('pt-BR')}`, { align: 'left' });
      doc.moveDown(1.5);

      // Linha divisória
      doc.moveTo(50, doc.y).lineTo(550, doc.y).stroke('#667eea');
      doc.moveDown(1);

      // Dados do Paciente
      doc.fontSize(14).fillColor('#667eea').text('🐱 DADOS DO PACIENTE');
      doc.moveDown(0.5);
      
      const paciente = diagnostico.resultado?.paciente || {};
      const dados = diagnostico.formulario || {};
      
      doc.fontSize(10).fillColor('#333');
      doc.text(`Nome: ${dados.nome || 'Não informado'}`);
      doc.text(`Raça: ${dados.raca || 'SRD'}`);
      doc.text(`Sexo: ${dados.sexo === 'M' ? 'Macho' : dados.sexo === 'F' ? 'Fêmea' : 'Não informado'}`);
      doc.text(`Idade: ${dados.idade ? dados.idade + ' anos' : 'Não informada'} ${dados.idade >= 10 ? '(Idoso)' : ''}`);
      doc.text(`Peso: ${dados.peso ? dados.peso + ' kg' : 'Não informado'}`);
      doc.moveDown(1.5);

      // Sintomas e Comorbidades
      doc.fontSize(14).fillColor('#667eea').text('🩺 APRESENTAÇÃO CLÍNICA');
      doc.moveDown(0.5);
      doc.fontSize(10).fillColor('#333');
      
      const sintomas = dados.sintomas || 'Não informado';
      const comorbidades = dados.comorbidades || 'Nenhuma';
      
      doc.text(`Sintomas: ${sintomas}`);
      doc.text(`Comorbidades: ${comorbidades}`);
      doc.moveDown(1.5);

      // Biomarcadores
      doc.fontSize(14).fillColor('#667eea').text('🔬 BIOMARCADORES');
      doc.moveDown(0.5);
      doc.fontSize(10).fillColor('#333');
      
      const biomarcadores = diagnostico.resultado?.biomarcadores || {};
      doc.text(`SDMA: ${biomarcadores.sdma || dados.sdma || 'N/A'} µg/dL`);
      doc.text(`Creatinina: ${biomarcadores.creatinina || dados.creatinina || 'N/A'} mg/dL`);
      doc.text(`UPC: ${biomarcadores.upc || dados.upc || 'N/A'}`);
      doc.text(`Pressão Arterial: ${biomarcadores.pressao_arterial || dados.pressao || 'N/A'} mmHg`);
      doc.moveDown(1.5);

      // Classificação IRIS
      doc.fontSize(14).fillColor('#4caf50').text('📊 CLASSIFICAÇÃO IRIS');
      doc.moveDown(0.5);
      
      const classificacao = diagnostico.resultado?.classificacao || {};
      doc.fontSize(12).fillColor('#2e7d32');
      doc.text(`Estágio: ${classificacao.estagio || 'N/A'}`, { underline: true });
      doc.fontSize(10).fillColor('#333');
      doc.text(`Subetágio Proteinúria (AP): ${classificacao.subestagio_ap || 'N/A'}`);
      doc.text(`Subetágio Hipertensão (HT): ${classificacao.subestagio_ht || 'N/A'}`);
      doc.text(`Confiança: ${classificacao.confianca || 'N/A'}`);
      doc.moveDown(1.5);

      // Validação
      const validacao = diagnostico.resultado?.validacao || {};
      doc.fontSize(14).fillColor('#667eea').text('✅ VALIDAÇÃO');
      doc.moveDown(0.5);
      doc.fontSize(10).fillColor('#333');
      doc.text(`Ontologia (Agente B): ${validacao.estagio_ontologia || 'N/A'}`);
      doc.text(`RAG (Agente C): ${validacao.estagio_rag || 'N/A'}`);
      doc.text(`Concordância: ${validacao.concordancia ? 'Sim ✓' : 'Não ✗'}`);
      doc.moveDown(1.5);

      // Recomendações
      const recomendacoes = diagnostico.resultado?.recomendacoes || [];
      if (recomendacoes.length > 0) {
        doc.fontSize(14).fillColor('#667eea').text('💊 RECOMENDAÇÕES TERAPÊUTICAS');
        doc.moveDown(0.5);
        doc.fontSize(10).fillColor('#333');
        recomendacoes.forEach((rec, idx) => {
          doc.text(`${idx + 1}. ${rec}`);
        });
        doc.moveDown(1.5);
      }

      // Observações
      if (diagnostico.resposta_completa) {
        doc.fontSize(14).fillColor('#667eea').text('📝 OBSERVAÇÕES');
        doc.moveDown(0.5);
        doc.fontSize(9).fillColor('#666');
        
        // Adicionar resposta completa (limitada para caber na página)
        const respostaLimitada = diagnostico.resposta_completa.substring(0, 1500) + 
                                 (diagnostico.resposta_completa.length > 1500 ? '...' : '');
        doc.text(respostaLimitada, { align: 'justify' });
      }

      // Rodapé
      doc.moveDown(2);
      doc.fontSize(8).fillColor('#999')
         .text(`Gerado automaticamente pelo Sistema IRIS | ${new Date().toISOString()}`, 
               { align: 'center' });

      // Finalizar documento
      doc.end();

      stream.on('finish', () => {
        resolve(outputPath);
      });

      stream.on('error', (err) => {
        reject(err);
      });

    } catch (error) {
      reject(error);
    }
  });
}

module.exports = {
  gerarPDFDiagnostico
};
