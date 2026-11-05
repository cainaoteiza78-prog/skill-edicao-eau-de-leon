# 03 — Legenda padrão

A legenda é **sempre a mesma** e o render faz tudo. Seu trabalho é escolher o modo, corrigir a grafia e marcar as ênfases.

## Como ela é (igual aos reels)

- **Poppins Bold**, branca, com **sombra preta suave** deslocada pra baixo e pra direita. É uma sombra, não um contorno.
- Uma linha só. Uma frase de ~22 caracteres ocupa ~55% da largura.
- **Abaixo do pescoço, na altura do peito.** O render detecta o rosto e calcula a altura sozinho, uma vez pro vídeo todo. Se a pessoa estiver muito alta ou baixa no quadro e a legenda cair no queixo ou na barriga, force com `"legenda_y": 0.58` (fração da altura; 0,56–0,62 é o normal).
- Aparece seca, sem animação de entrada, e troca no ritmo da fala.
- Minúscula como se fala: "quer usar", "mas não faz ideia". O começo de frase também fica minúsculo; nomes próprios e marcas mantêm a maiúscula ("a Eau de Leon lançou", "o Sauvage").
- Sem ponto final e sem vírgula. Mantém **?** e **!**.

## Modos (campo `legenda`)

| Modo | Formato | Como agrupa |
|---|---|---|
| `frase` (padrão) | `leo` | 2 a 4 palavras, no máx. 24 caracteres; quebra em pausa, ponto, ? e ! |
| `palavra` | `creator` | uma palavra por vez |
| `nenhuma` | formatos sem fala | — |

## Destaque de palavra-chave (`destaques`)

A palavra que vende ganha destaque **dentro da legenda**: ela vai para uma **linha própria logo abaixo**, **maior** (1,45×), em **CAIXA ALTA**, **amarela** (#FFD23F) e entra com um **pop** no instante em que é falada. O resto da frase continua normal em cima:

```
          clica em            ← legenda normal (branca)
       SAIBA MAIS             ← destaque: maior, amarelo, pop
```

Exemplos: "clica em **SAIBA MAIS**", "simplesmente **IMPERDÍVEL**", "10% em **TODOS OS PERFUMES**", "**FRETE GRÁTIS** pra todo o Brasil", "só **HOJE**".

O que destacar:
- CTA ("saiba mais", "link na bio", "chama no direct")
- benefício ou oferta ("todos os perfumes", "frete grátis", "10%", "cupom")
- adjetivo forte do gancho ("imperdível", "o melhor", "exclusivo")
- **2 a 4 destaques por vídeo de 30 s.** Mais que isso perde a força.
- Nunca destaque o que já está num texto de impacto na tela ao mesmo tempo.

O `transcrever.py` gera `destaques_sugeridos.txt` com as candidatas e seus tempos. Escolha, confira os tempos e escreva:
```json
"destaques": [
  {"take": 1, "ini": 4.86, "fim": 5.60},
  {"take": 2, "ini": 8.80, "fim": 9.75},
  {"take": 3, "ini": 3.26, "fim": 3.80, "estilo": "grande"}
]
```
- `ini`/`fim` cobrem **só as palavras destacadas** (início da 1ª até o fim da última). Até 5 palavras.
- `estilo`: `cor` (padrão: amarelo e 1,45×) ou `grande` (branco e 1,75×, pra quando o fundo é amarelado).
- A cor é uma só pro vídeo todo (`ESTILO_TEXTO['destaque_legenda']['cor']` em `scripts/textos.py`).

## Ênfase em CAIXA ALTA (`legenda_maiusculas`)

No reel do Quiz, "DE QUAL ESCOLHER?" aparece em maiúsculas: é a pergunta do gancho. Use no máximo 1 ou 2 vezes por vídeo, sempre na pergunta do gancho ou na frase que vende.
```json
"legenda_maiusculas": [{"take": 1, "ini": 2.40, "fim": 3.10}]
```

## Correções de grafia (`correcoes`)

O Whisper erra nome de marca e de perfume. Corrija **só a grafia** do que foi falado:
- "Aude Leon", "O de Leon", "Eau de Lion" → **Eau de Leon**
- "decan" → **decant**
- "salha mais", "saia mais" → **Saiba mais**
- "10 -10" (a data falada "dez do dez") → **10.10**
- nome de perfume quebrado: "Le Male, Elixir" → **Le Male Elixir**
- "ultimora" → **última hora**

O "de" é comparado sem acento, maiúscula ou pontuação, palavra por palavra. "10 %" vira "10%" sozinho.
```json
"correcoes": [
  {"de": "Aude Leon", "para": "Eau de Leon"},
  {"de": "salha mais", "para": "Saiba mais"}
]
```
Nunca use correção pra trocar o que a pessoa disse.

## Quando a legenda some

Enquanto um texto de impacto ou destaque está na tela, a legenda some e volta logo depois que ele sai. O render faz isso sozinho.
