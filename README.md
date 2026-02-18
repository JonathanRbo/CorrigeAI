# CorrigeAI - Corretor Inteligente de Textos

Plataforma educacional para professores e alunos corrigirem textos, redações e trabalhos escolares. Analisa gramática, estilo, estrutura e atribui nota automaticamente.

![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=flat&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat&logo=javascript&logoColor=black)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=flat&logo=flask&logoColor=white)

---

## Sobre

O CorrigeAI oferece correção automática de textos em português com foco em:

- **Gramática** — acentuação, concordância verbal, ortografia
- **Estilo** — clichês, repetições, expressões vagas, pontuação
- **Estrutura** — parágrafos, tamanho do texto, legibilidade
- **Linguagem** — detecção de internetês e gírias em textos formais
- **Nota** — avaliação de 0 a 10 com resumo detalhado

## Funcionalidades

- Landing page completa com demo interativa
- 5 textos de exemplo prontos para teste (péssimo, mediano, bom, ENEM, informal)
- Análise local via JavaScript (funciona sem servidor)
- API Python com Flask para análise avançada
- Suporte opcional ao LanguageTool (5000+ regras gramaticais)
- Fallback automático: se a API estiver offline, usa o motor JS

## Estrutura do Projeto

```
corretor-educacional/
├── index.html          # Landing page + demo interativa
├── app.py              # Servidor Flask (API)
├── analyzer.py         # Motor de análise em Python
├── requirements.txt    # Dependências Python
├── .gitignore
└── README.md
```

## Como Usar

### Modo 1 — Apenas Frontend (sem Python)

Abra o `index.html` diretamente no navegador. A demo funciona com o motor JavaScript local (20+ regras).

### Modo 2 — Com Backend Python (recomendado)

```bash
# Instalar dependências
pip install -r requirements.txt

# Rodar o servidor
python app.py
```

Acesse `http://localhost:5000`. O frontend detecta automaticamente a API e exibe um badge verde **"Python API"**.

### Modo 3 — Com LanguageTool (máxima precisão)

Requer [Java 8+](https://java.com) instalado na máquina.

```bash
pip install -r requirements.txt
python app.py
```

Se o Java estiver disponível, o LanguageTool será carregado automaticamente com 5000+ regras para pt-BR.

## O que é Analisado

### Gramática (Python: 80+ regras / JS: 20+ regras)
| Regra | Exemplo |
|-------|---------|
| Acentuação ausente | "educacao" → "educação" |
| Concordância verbal | "os alunos precisa" → "precisam" |
| Verbo "é" sem acento | "e importante" → "é importante" |
| Til ausente | "nao" → "não" |
| Linguagem informal | "vc", "pq", "tbm", "kkk" |

### Estilo
| Regra | Exemplo |
|-------|---------|
| Clichês | "nesse sentido", "nos dias de hoje" |
| Expressões vagas | "alguma coisa", "fazer algo" |
| Repetição excessiva | mesma palavra 4+ vezes |
| Pontuação ausente | texto sem ponto final |
| Estrutura fraca | texto sem parágrafos |

### Nota (0 a 10)
```
Base: 10.0
 − erros gramaticais × 0.8~1.2
 − erros de estilo × 0.4~0.6
 + bônus por tamanho (>100, >200, >300 palavras)
 + bônus por parágrafos (≥3, ≥4)
 + bônus por vocabulário diversificado
 − penalidade por linguagem informal
```

| Nota | Cor | Classificação |
|------|-----|---------------|
| 7-10 | Verde | Bom trabalho |
| 5-6.9 | Amarelo | Razoável |
| 0-4.9 | Vermelho | Precisa de revisão |

## API

### `POST /api/analisar`

```json
// Request
{ "texto": "A educacao no Brasil e importante..." }

// Response
{
  "errors": [
    { "type": "grammar", "text": "...", "suggestion": "..." }
  ],
  "grade": 6.5,
  "grade_label": "Razoável. Corrija os erros apontados.",
  "grade_class": "medium",
  "stats": {
    "word_count": 42,
    "sentence_count": 3,
    "paragraph_count": 1,
    "grammar_errors": 2,
    "style_errors": 1,
    "vocabulary_richness": 78.5,
    "has_language_tool": false
  }
}
```

### `GET /api/status`

Retorna o estado do servidor e se o LanguageTool está ativo.

## Tecnologias

- **Frontend:** HTML5, CSS3 (Squeleton Framework), JavaScript
- **Backend:** Python 3, Flask, Flask-CORS
- **Gramática:** LanguageTool (opcional, requer Java)
- **Animações:** WOW.js, Animated.css
- **Ícones:** Iccon (via Squeleton)

## Licença

MIT
