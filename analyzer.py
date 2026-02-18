"""
Motor de Análise de Textos em Português
Corretor robusto baseado em regras, sem IA.
Usa language_tool_python (LanguageTool) para gramática
+ regras customizadas para estilo, estrutura e nota.
"""

import re
import math

# ============================================================
# Tentar importar LanguageTool (precisa de Java instalado)
# Se não tiver, usa apenas regras customizadas
# ============================================================
try:
    import language_tool_python
    _lt = language_tool_python.LanguageTool('pt-BR')
    HAS_LANGUAGE_TOOL = True
    print("[OK] LanguageTool carregado com sucesso (pt-BR)")
except Exception as e:
    _lt = None
    HAS_LANGUAGE_TOOL = False
    print(f"[AVISO] LanguageTool não disponível: {e}")
    print("[INFO] Usando apenas regras customizadas.")


# ============================================================
# DICIONÁRIO DE PALAVRAS SEM ACENTO → COM ACENTO
# ============================================================
ACCENT_FIXES = {
    "educacao": "educação", "situacao": "situação", "populacao": "população",
    "nacao": "nação", "informacao": "informação", "comunicacao": "comunicação",
    "organizacao": "organização", "preocupacao": "preocupação", "solucao": "solução",
    "açao": "ação", "relaçao": "relação", "condiçao": "condição",
    "produçao": "produção", "construçao": "construção", "destruiçao": "destruição",
    "transformacoes": "transformações", "condicoes": "condições",
    "situacoes": "situações", "informacoes": "informações",
    "politicas": "políticas", "publicas": "públicas", "publico": "público",
    "tambem": "também", "porem": "porém", "entao": "então",
    "nao": "não", "sao": "são", "estao": "estão", "serao": "serão",
    "necessario": "necessário", "necessaria": "necessária",
    "possivel": "possível", "impossivel": "impossível",
    "responsavel": "responsável", "vulneravel": "vulnerável",
    "acessivel": "acessível", "disponivel": "disponível",
    "ultimos": "últimos", "ultimo": "último", "ultima": "última",
    "indice": "índice", "indices": "índices",
    "familia": "família", "familias": "famílias",
    "saude": "saúde", "conteudo": "conteúdo", "conteudos": "conteúdos",
    "sera": "será", "tambem": "também", "voce": "você",
    "ate": "até", "alem": "além", "ja": "já",
    "alguem": "alguém", "ninguem": "ninguém",
    "historia": "história", "historico": "histórico",
    "economica": "econômica", "economico": "econômico",
    "tecnologica": "tecnológica", "tecnologico": "tecnológico",
    "psiquico": "psíquico", "fisico": "físico",
    "obrigatorio": "obrigatório", "contrario": "contrário",
    "salario": "salário", "varios": "vários", "varias": "várias",
    "frustracao": "frustração", "violencia": "violência",
    "experiencia": "experiência", "consequencia": "consequência",
    "ausencia": "ausência", "frequencia": "frequência",
    "crianca": "criança", "criancas": "crianças",
    "funçao": "função", "regiao": "região", "regioes": "regiões",
}

# ============================================================
# GÍRIAS / INTERNETÊS
# ============================================================
INFORMAL_TERMS = {
    r"\bvc\b": ('"vc"', '"você"'),
    r"\bpq\b": ('"pq"', '"porque"'),
    r"\btbm\b": ('"tbm"', '"também"'),
    r"\btb\b": ('"tb"', '"também"'),
    r"\bmt\b": ('"mt"', '"muito"'),
    r"\bblz\b": ('"blz"', '"beleza"'),
    r"\bflw\b": ('"flw"', '"falou"'),
    r"\bpfv\b|\bpfvr\b": ('"pfv"', '"por favor"'),
    r"\bobg\b|\bobgd\b": ('"obg"', '"obrigado(a)"'),
    r"\bmds\b": ('"mds"', '"meu Deus"'),
    r"\btd\b": ('"td"', '"tudo"'),
    r"\bqnd\b|\bqdo\b": ('"qnd/qdo"', '"quando"'),
    r"\bcmg\b": ('"cmg"', '"comigo"'),
    r"\bctg\b": ('"ctg"', '"contigo"'),
    r"\bdps\b": ('"dps"', '"depois"'),
    r"\bhj\b": ('"hj"', '"hoje"'),
    r"\bmsm\b": ('"msm"', '"mesmo"'),
    r"\bnd\b": ('"nd"', '"nada"'),
    r"\bngm\b": ('"ngm"', '"ninguém"'),
    r"\bslk\b": ('"slk"', '(gíria)'),
    r"\bmano\b": ('"mano"', '(coloquial)'),
    r"\bgalera\b": ('"galera"', '(coloquial)'),
    r"\bkk+\b": ('"kkk"', '(risada informal)'),
    r"\brs+\b": ('"rs"', '(risada informal)'),
    r"\bhaha+\b": ('"haha"', '(risada informal)'),
    r"\btipo assim\b": ('"tipo assim"', '(informal)'),
    r"\bne\b": ('"ne"', '"não é"'),
    r"\bent\b": ('"ent"', '"então"'),
    r"\bdai\b": ('"dai"', '"daí"'),
    r"\bpra\b": ('"pra"', '"para"'),
    r"\bpro\b": ('"pro"', '"para o"'),
}

# ============================================================
# CLICHÊS E EXPRESSÕES DESGASTADAS
# ============================================================
CLICHES = [
    (r"nos dias de hoje", '"nos dias de hoje"'),
    (r"desde os prim[oó]rdios", '"desde os primórdios"'),
    (r"desde que o mundo [eé] mundo", '"desde que o mundo é mundo"'),
    (r"muito se (discute|debate|fala)", '"muito se discute/debate"'),
    (r"nesse sentido", '"nesse sentido"'),
    (r"diante disso", '"diante disso"'),
    (r"dessa forma", '"dessa forma"'),
    (r"sendo assim", '"sendo assim"'),
    (r"conclui-se que", '"conclui-se que"'),
    (r"em pleno s[eé]culo (xxi|21)", '"em pleno século XXI"'),
    (r"ser algu[eé]m na vida", '"ser alguém na vida"'),
    (r"[eé] sabido que", '"é sabido que"'),
    (r"ao longo da hist[oó]ria", '"ao longo da história"'),
    (r"um grande desafio", '"um grande desafio"'),
    (r"cabe ressaltar que", '"cabe ressaltar que"'),
    (r"vale lembrar que", '"vale lembrar que"'),
]

# ============================================================
# EXPRESSÕES VAGAS
# ============================================================
VAGUE_EXPRESSIONS = [
    r"\balguma coisa\b",
    r"\bfazer algo\b",
    r"\bde algum modo\b",
    r"\bde alguma forma\b",
    r"\bmuita coisa\b",
    r"\bv[aá]rias coisas\b",
    r"\besse problema\b(?!.*\b(de|da|do|que)\b)",
]


# ============================================================
# ANÁLISE PRINCIPAL
# ============================================================
def analyze(text: str) -> dict:
    """Analisa um texto e retorna erros, nota e estatísticas."""

    errors = []
    lt = text.lower()
    words = text.split()
    word_count = len(words)
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    paragraphs = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]

    # ========================================================
    # 1) LANGUAGETOOL (se disponível)
    # ========================================================
    lt_error_count = 0
    if HAS_LANGUAGE_TOOL:
        try:
            matches = _lt.check(text)
            for match in matches:
                # Categorizar o tipo de erro
                category = match.category or ""
                rule_id = match.ruleId or ""

                # Ignorar regras muito genéricas ou falsos positivos comuns
                skip_rules = [
                    "WHITESPACE_RULE", "COMMA_PARENTHESIS_WHITESPACE",
                    "UNPAIRED_BRACKETS"
                ]
                if rule_id in skip_rules:
                    continue

                # Determinar tipo
                if any(k in category.upper() for k in ["GRAMM", "AGREEMENT", "SYNTAX", "TYPO", "SPELL"]):
                    err_type = "grammar"
                elif any(k in category.upper() for k in ["STYLE", "REDUNDANCY", "TYPOGRAPHY"]):
                    err_type = "style"
                else:
                    err_type = "grammar"

                # Trecho do erro
                ctx = match.context or ""
                offset = match.offsetInContext or 0
                length = match.errorLength or 0
                highlighted = ctx[offset:offset+length] if offset + length <= len(ctx) else ""

                suggestion_text = ""
                if match.replacements:
                    top = match.replacements[:3]
                    suggestion_text = f'Sugestão: {", ".join(top)}'

                error_msg = match.message or "Erro detectado"
                if highlighted:
                    error_msg = f'"{highlighted}" — {error_msg}'

                errors.append({
                    "type": err_type,
                    "text": error_msg,
                    "suggestion": suggestion_text if suggestion_text else "Revise este trecho.",
                    "source": "languagetool",
                    "offset": match.offset,
                    "length": match.errorLength,
                })
                lt_error_count += 1

                # Limitar para não poluir
                if lt_error_count >= 20:
                    break

        except Exception as e:
            print(f"[ERRO LanguageTool] {e}")

    # ========================================================
    # 2) REGRAS CUSTOMIZADAS - ACENTUAÇÃO
    # ========================================================
    missing_accents = []
    words_lower = [w.lower().strip(".,;:!?()\"'") for w in words]

    for word_clean in set(words_lower):
        if word_clean in ACCENT_FIXES:
            correct = ACCENT_FIXES[word_clean]
            # Verificar se a versão correta já existe no texto
            if correct.lower() not in lt:
                missing_accents.append(f'"{word_clean}" → "{correct}"')

    if missing_accents:
        # Agrupar em chunks de 5 para não ficar gigante
        for i in range(0, len(missing_accents), 5):
            chunk = missing_accents[i:i+5]
            errors.append({
                "type": "grammar",
                "text": f"Palavras sem acentuação: {', '.join(chunk)}",
                "suggestion": "Essas palavras exigem acentuação gráfica conforme as regras do português.",
                "source": "custom",
            })

    # ========================================================
    # 3) REGRAS CUSTOMIZADAS - CONCORDÂNCIA VERBAL
    # ========================================================
    # Sujeito plural + verbo singular
    concordance_patterns = [
        (r"\b(os|as|esses?|essas?|muitos|muitas|diversos|diversas|vários|várias|alguns|algumas|todos|todas|professores|alunos|estudantes|jovens|crianças|criancas|pessoas|escolas|cidades|políticas|politicas|mudanças|mudancas|problemas|tecnologias)\b[^.!?]{0,30}\b(precisa|conta|recebe|apresenta|encontra|sofre|ganha|tem|vem|afeta|representa|contribui|gera|causa|existe|faz|alerta|desempenha|funciona)\b",
         "Possível erro de concordância: verbo no singular com sujeito no plural",
         "Quando o sujeito está no plural, o verbo deve concordar. Ex: 'Os alunos precisam' (não 'precisa'), 'As escolas contam' (não 'conta')."),
    ]

    for pattern, msg, suggestion in concordance_patterns:
        if re.search(pattern, lt):
            # Evitar duplicatas com LanguageTool
            if not any(e.get("source") == "languagetool" and "concord" in e["text"].lower() for e in errors):
                errors.append({
                    "type": "grammar",
                    "text": msg,
                    "suggestion": suggestion,
                    "source": "custom",
                })

    # ========================================================
    # 4) REGRAS CUSTOMIZADAS - LINGUAGEM INFORMAL
    # ========================================================
    found_informal = []
    for pattern, (term, replacement) in INFORMAL_TERMS.items():
        if re.search(pattern, lt):
            found_informal.append(f'{term} → {replacement}')

    if found_informal:
        errors.append({
            "type": "grammar",
            "text": f"Linguagem informal / internetês detectada ({len(found_informal)} ocorrências)",
            "suggestion": f"Em textos formais, evite: {', '.join(found_informal[:8])}{'...' if len(found_informal) > 8 else ''}.",
            "source": "custom",
        })

    # ========================================================
    # 5) REGRAS CUSTOMIZADAS - CLICHÊS
    # ========================================================
    found_cliches = []
    for pattern, label in CLICHES:
        if re.search(pattern, lt):
            found_cliches.append(label)

    if found_cliches:
        errors.append({
            "type": "style",
            "text": f"Expressões clichê encontradas: {', '.join(found_cliches)}",
            "suggestion": "Clichês enfraquecem a argumentação. Substitua por conectivos e expressões mais originais e específicas.",
            "source": "custom",
        })

    # ========================================================
    # 6) REGRAS CUSTOMIZADAS - EXPRESSÕES VAGAS
    # ========================================================
    found_vague = []
    for pattern in VAGUE_EXPRESSIONS:
        match = re.search(pattern, lt)
        if match:
            found_vague.append(f'"{match.group()}"')

    if found_vague:
        errors.append({
            "type": "style",
            "text": f"Expressões vagas detectadas: {', '.join(found_vague)}",
            "suggestion": "Seja mais específico. Ao invés de 'alguma coisa', descreva exatamente o que propõe.",
            "source": "custom",
        })

    # ========================================================
    # 7) REGRAS CUSTOMIZADAS - ESTRUTURA
    # ========================================================

    # Pontuação final ausente
    if text.strip() and not re.search(r'[.!?]\s*$', text.strip()):
        errors.append({
            "type": "style",
            "text": "Texto não termina com pontuação final",
            "suggestion": "Finalize com ponto final, interrogação ou exclamação.",
            "source": "custom",
        })

    # Ausência de vírgulas em texto longo
    if word_count > 40 and text.count(',') < 2:
        errors.append({
            "type": "style",
            "text": "Poucas vírgulas para o tamanho do texto",
            "suggestion": "Use vírgulas para separar orações, adjuntos deslocados e enumerações. Isso melhora a leitura.",
            "source": "custom",
        })

    # Texto sem parágrafos
    if paragraphs and len(paragraphs) == 1 and word_count > 80:
        errors.append({
            "type": "style",
            "text": "Texto sem divisão em parágrafos",
            "suggestion": "Divida em parágrafos: introdução, desenvolvimento (2-3 parágrafos) e conclusão. Cada parágrafo deve ter uma ideia central.",
            "source": "custom",
        })

    # Frases muito longas
    long_sentences = [s for s in sentences if len(s.split()) > 45]
    if long_sentences:
        errors.append({
            "type": "style",
            "text": f"{len(long_sentences)} frase(s) com mais de 45 palavras",
            "suggestion": "Frases longas demais dificultam a compreensão. Divida em períodos menores.",
            "source": "custom",
        })

    # Frases iniciando com minúscula
    lower_starts = 0
    for i, s in enumerate(sentences):
        if i > 0 and s and re.match(r'^[a-záàâãéèêíïóôõúüç]', s):
            lower_starts += 1
    if lower_starts > 0:
        errors.append({
            "type": "grammar",
            "text": f"{lower_starts} frase(s) iniciando com letra minúscula",
            "suggestion": "Toda frase deve começar com letra maiúscula após pontuação final.",
            "source": "custom",
        })

    # Repetição excessiva de palavras
    stop_words = {
        'a', 'o', 'e', 'é', 'de', 'do', 'da', 'em', 'no', 'na', 'os', 'as',
        'dos', 'das', 'um', 'uma', 'que', 'se', 'por', 'com', 'para', 'não',
        'ao', 'aos', 'pelo', 'pela', 'mais', 'muito', 'como', 'mas', 'ou',
        'nos', 'nas', 'seu', 'sua', 'esse', 'essa', 'este', 'esta', 'isso',
        'isto', 'são', 'foi', 'ser', 'ter', 'há', 'já', 'das', 'dos', 'nem',
        'uns', 'umas', 'seus', 'suas', 'num', 'numa', 'nesse', 'nessa',
        'desse', 'dessa', 'deste', 'desta', 'neste', 'nesta', 'entre',
        'sobre', 'sob', 'até', 'sem', 'pois', 'após', 'quando', 'onde',
        'ainda', 'mesmo', 'também', 'cada', 'toda', 'todo', 'à', 'às',
    }
    word_freq = {}
    for w in words:
        clean = re.sub(r'[^a-záàâãéèêíïóôõúüç]', '', w.lower())
        if len(clean) > 3 and clean not in stop_words:
            word_freq[clean] = word_freq.get(clean, 0) + 1

    repeated = [f'"{w}" ({c}x)' for w, c in word_freq.items() if c >= 4]
    if repeated:
        errors.append({
            "type": "style",
            "text": f"Repetição excessiva: {', '.join(repeated[:5])}",
            "suggestion": "Use sinônimos ou reformule frases para evitar repetição e enriquecer o vocabulário.",
            "source": "custom",
        })

    # ========================================================
    # 8) MÉTRICAS DE LEGIBILIDADE
    # ========================================================
    avg_word_len = sum(len(w) for w in words) / max(word_count, 1)
    avg_sentence_len = word_count / max(len(sentences), 1)
    vocabulary_richness = len(set(w.lower() for w in words)) / max(word_count, 1)

    # ========================================================
    # 9) DICAS POSITIVAS
    # ========================================================
    grammar_count = len([e for e in errors if e["type"] == "grammar"])
    style_count = len([e for e in errors if e["type"] == "style"])

    if word_count < 30:
        errors.append({
            "type": "tip",
            "text": f"Texto muito curto ({word_count} palavras)",
            "suggestion": "Uma redação deve ter no mínimo 7 linhas (~100 palavras). Desenvolva argumentos com exemplos e dados.",
            "source": "custom",
        })
    elif word_count < 100:
        errors.append({
            "type": "tip",
            "text": f"Texto curto ({word_count} palavras)",
            "suggestion": "Tente expandir para 200+ palavras. Adicione argumentos, exemplos concretos e dados para fortalecer o texto.",
            "source": "custom",
        })
    elif word_count >= 200:
        errors.append({
            "type": "tip",
            "text": f"Bom volume de texto ({word_count} palavras)",
            "suggestion": "O tamanho está adequado. Verifique se todos os argumentos estão bem desenvolvidos.",
            "source": "custom",
        })

    if len(paragraphs) >= 4:
        errors.append({
            "type": "tip",
            "text": f"Boa estrutura de parágrafos ({len(paragraphs)} parágrafos)",
            "suggestion": "A divisão em parágrafos demonstra organização e facilita a leitura.",
            "source": "custom",
        })

    if vocabulary_richness > 0.7 and word_count > 50:
        errors.append({
            "type": "tip",
            "text": f"Vocabulário diversificado ({vocabulary_richness:.0%} de palavras únicas)",
            "suggestion": "Bom uso de vocabulário variado, o que enriquece o texto.",
            "source": "custom",
        })

    if grammar_count == 0 and style_count == 0:
        errors.append({
            "type": "tip",
            "text": "Nenhum erro significativo encontrado",
            "suggestion": "Texto muito bem escrito! Continue praticando para manter esse nível de qualidade.",
            "source": "custom",
        })
    else:
        errors.append({
            "type": "tip",
            "text": "Continue praticando!",
            "suggestion": "Cada erro corrigido é um aprendizado. Revise seus textos anteriores e observe sua evolução.",
            "source": "custom",
        })

    # ========================================================
    # 10) CALCULAR NOTA
    # ========================================================
    grade = 10.0

    # Penalidades
    grade -= grammar_count * 0.8
    grade -= style_count * 0.4

    # Bônus por tamanho
    if word_count > 100:
        grade += 0.3
    if word_count > 200:
        grade += 0.3
    if word_count > 300:
        grade += 0.2

    # Bônus por estrutura
    if len(paragraphs) >= 3:
        grade += 0.3
    if len(paragraphs) >= 4:
        grade += 0.2

    # Bônus por vocabulário
    if vocabulary_richness > 0.6:
        grade += 0.2

    # Penalidade extra por linguagem informal
    has_informal = any("informal" in e["text"].lower() or "internetês" in e["text"].lower() for e in errors)
    if has_informal:
        grade -= 1.5

    grade = round(max(0.5, min(10.0, grade)), 1)

    # Classificação
    if grade >= 7:
        grade_label = "Bom trabalho! Texto com boa qualidade."
        grade_class = "high"
    elif grade >= 5:
        grade_label = "Razoável. Corrija os erros apontados."
        grade_class = "medium"
    else:
        grade_label = "Precisa de revisão. Analise cada erro com atenção."
        grade_class = "low"

    # ========================================================
    # RESULTADO
    # ========================================================
    return {
        "errors": errors,
        "grade": grade,
        "grade_label": grade_label,
        "grade_class": grade_class,
        "stats": {
            "word_count": word_count,
            "char_count": len(text),
            "sentence_count": len(sentences),
            "paragraph_count": len(paragraphs),
            "avg_word_length": round(avg_word_len, 1),
            "avg_sentence_length": round(avg_sentence_len, 1),
            "vocabulary_richness": round(vocabulary_richness * 100, 1),
            "grammar_errors": grammar_count,
            "style_errors": style_count,
            "has_language_tool": HAS_LANGUAGE_TOOL,
        },
    }
