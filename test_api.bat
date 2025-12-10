@echo off
echo Testing API...
echo.

curl -X POST http://localhost:3001/api/diagnosis ^
  -H "Content-Type: application/json" ^
  -d "{\"formulario\":{\"nome\":\"Mimi\",\"sexo\":\"F\",\"raca\":\"Siames\",\"sdma\":18.5,\"creatinina\":2.3,\"idade\":8,\"peso\":4.2,\"pressao\":145,\"upc\":0.3,\"sintomas\":\"poliuria, polidipsia\",\"comorbidades\":\"hipertensao\"},\"texto_livre\":\"Qual o estagio da doenca renal?\"}"

echo.
echo.
pause
