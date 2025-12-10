/**
 * Script de teste para a API
 * Testa o endpoint POST /api/diagnosis
 */

const testRequest = {
  formulario: {
    nome: "Mimi",
    sexo: "F",
    raca: "Siamês",
    sdma: 18.5,
    creatinina: 2.3,
    idade: 8,
    peso: 4.2,
    pressao: 145,
    upc: 0.3,
    sintomas: "poliúria, polidipsia",
    comorbidades: "hipertensão"
  },
  texto_livre: "Qual o estágio da doença renal?"
};

console.log('🧪 Testando API...\n');
console.log('Enviando requisição para: http://localhost:3001/api/diagnosis\n');

fetch('http://localhost:3001/api/diagnosis', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(testRequest)
})
  .then(response => {
    console.log(`Status: ${response.status} ${response.statusText}\n`);
    return response.json();
  })
  .then(data => {
    console.log('✅ Resposta recebida:\n');
    console.log(JSON.stringify(data, null, 2));
    
    if (data.success) {
      console.log('\n✅ Teste bem-sucedido!');
      console.log(`Estágio final: ${data.data.validated_result?.estagio_final}`);
      console.log(`Tempo de processamento: ${data.metadata.total_time_ms}ms`);
    } else {
      console.log('\n❌ Teste falhou:', data.error);
    }
  })
  .catch(error => {
    console.error('\n❌ Erro ao chamar API:', error.message);
  });
