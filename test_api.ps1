# Script PowerShell para testar a API
# Testa o endpoint POST /api/diagnosis

$body = @{
    formulario = @{
        nome = "Mimi"
        sexo = "F"
        raca = "Siamês"
        sdma = 18.5
        creatinina = 2.3
        idade = 8
        peso = 4.2
        pressao = 145
        upc = 0.3
        sintomas = "poliúria, polidipsia"
        comorbidades = "hipertensão"
    }
    texto_livre = "Qual o estágio da doença renal?"
} | ConvertTo-Json -Depth 10

Write-Host "🧪 Testando API..." -ForegroundColor Cyan
Write-Host ""
Write-Host "📡 Enviando requisição para: http://localhost:3001/api/diagnosis" -ForegroundColor Yellow
Write-Host ""

try {
    $response = Invoke-RestMethod -Uri "http://localhost:3001/api/diagnosis" `
        -Method POST `
        -Body $body `
        -ContentType "application/json" `
        -TimeoutSec 120

    Write-Host "✅ Resposta recebida:" -ForegroundColor Green
    Write-Host ""
    $response | ConvertTo-Json -Depth 10
    Write-Host ""
    
    if ($response.success) {
        Write-Host "✅ Teste bem-sucedido!" -ForegroundColor Green
        Write-Host "Estágio final: $($response.data.validated_result.estagio_final)" -ForegroundColor Cyan
        Write-Host "Tempo de processamento: $($response.metadata.total_time_ms)ms" -ForegroundColor Cyan
    } else {
        Write-Host "❌ Teste falhou: $($response.error)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Erro ao chamar API:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}
