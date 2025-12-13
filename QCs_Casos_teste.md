# Competency Questions (CQs) – Ontologia DRC Felina

As CQs abaixo foram formuladas para validar a capacidade de inferência e consulta da ontologia. Cada CQ apresenta: número, pergunta, nota de implementação e consulta SPARQL.

---

**CQ1: Gatos em Estágio Avançado (3 ou 4)**
- Pergunta: Quais gatos estão em estágios 3 ou 4?
- Implementação na ontologia: Sim (EstagioIRIS3 e EstagioIRIS4 definidos)
- SPARQL:
```sparql
SELECT ?gato WHERE {
  ?gato a :Gato .
  { ?gato :estaNoEstagio :Estagio3 }
  UNION
  { ?gato :estaNoEstagio :Estagio4 }
}
```

**CQ2: Gatos Idosos (≥ 7 anos)**
- Pergunta: Quais gatos têm 7 anos ou mais?
- Implementação na ontologia: Sim (propriedade idade presente)
- SPARQL:
```sparql
SELECT ?gato ?idade WHERE {
  ?gato a :Gato .
  ?gato :idade ?idade .
  FILTER(?idade >= 7)
}
```

**CQ3: Gatos com Raça Predisposta**
- Pergunta: Quais gatos pertencem a raças predispostas à DRC?
- Implementação na ontologia: Sim (classes para raças e RacaComMaiorPredisposicao)
- SPARQL:
```sparql
SELECT ?gato ?raca WHERE {
  ?gato a :Gato .
  ?gato :hasRaca ?raca .
  ?raca a :RacaComMaiorPredisposicao .
}
```

**CQ4: Gatos com Comorbidades**
- Pergunta: Quais gatos possuem comorbidades associadas à DRC?
- Implementação na ontologia: Sim (propriedades e classes para comorbidades)
- SPARQL:
```sparql
SELECT ?gato ?comorbidade WHERE {
  ?gato a :Gato .
  ?gato :hasComorbidade ?comorbidade .
}
```

**CQ5: Gatos com Proteinúria Borderline (AP1)**
- Pergunta: Quais gatos apresentam subestágio AP1?
- Implementação na ontologia: Sim (classe BordelineProteinurico definida por restrição de razaoProteina)
- SPARQL:
```sparql
SELECT ?gato WHERE {
  ?gato a :Gato .
  ?gato :subestagioAP :AP1 .
}
```

**CQ6: Gatos sem Proteinúria (AP0)**
- Pergunta: Quais gatos apresentam subestágio AP0?
- Implementação na ontologia: Sim (classe NaoProteinurico definida)
- SPARQL:
```sparql
SELECT ?gato WHERE {
  ?gato a :Gato .
  ?gato :subestagioAP :AP0 .
}
```

**CQ7: Gatos com Pressão Arterial ≥ 180 mmHg**
- Pergunta: Quais gatos têm pressão arterial sistólica maior ou igual a 180 mmHg?
- Implementação na ontologia: Sim (propriedade pressaoArterial presente)
- SPARQL:
```sparql
SELECT ?gato ?pressao WHERE {
  ?gato a :Gato .
  ?gato :pressaoArterial ?pressao .
  FILTER(?pressao >= 180)
}
```

**CQ8: Gatos com Diagnóstico Confirmado de DRC**
- Pergunta: Quais gatos possuem diagnóstico confirmado de DRC?
- Implementação na ontologia: Sim (classe GatoComIRC e propriedade diagnostico presentes)
- SPARQL:
```sparql
SELECT ?gato WHERE {
  ?gato a :Gato .
  ?gato :diagnostico true .
}
```

## Casos de Teste

Os casos de teste foram realizados para validar o sistema multiagente. Cenários:
1. Ontologia infere corretamente e RAG concorda.
2. Ontologia recebe dados incorretos com diferença de 1.
3. Ontologia recebe dados incorretos com diferença de 2.
4. Ontologia recebe dados, mas não há perguntas.
5. Pergunta fora do escopo, mas a ontologia recebe dados corretamente.