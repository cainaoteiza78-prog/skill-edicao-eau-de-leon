# 09 — Exemplo completo: do bruto ao plano

Duas takes de um vídeo formato `leo` (apresentador falando de perfumes + oferta). Este exemplo foi renderizado de verdade com os scripts da skill durante a criação dela.

## O que o transcrever.py devolveu (transcricao.txt, resumido)

```
── TAKE 1  (take1.mp4, 18.4s) ──
[take 1 |   0.66 →   5.12] Se você ama perfume importado mas não quer pagar caro, presta atenção.
      ↳ Se(0.66) você(1.22) ama(1.50) perfume(1.82) importado(2.26) mas(2.86) não(3.08) quer(3.24) pagar(3.44) caro,(3.72) presta(4.46) atenção.(4.70)
[take 1 |   6.20 →   9.76] A Eau de Leon tem os perfumes mais desejados do mundo em decan.
      ↳ ... em(9.30) decan.(9.44)
[take 1 |  10.58 →  16.26] Por exemplo, Le Male, Elixir, o Sauvage e o Bleu de Chanel, todos no tamanho que cabe no seu bolso.
      ↳ Por(10.58) exemplo,(10.82) Le(11.44) Male,(11.44) Elixir,(11.72) o(12.38) Sauvage(12.48) e(12.98) o(13.12) Bleu(13.12) ... bolso.(15.80)

── TAKE 2  (take2.mp4, 17.9s) ──
[take 2 |   0.94 →   3.04] Corta, corta, vou de novo.
[take 2 |   3.92 →   9.34] E pra elas, o Good Girl, o La Vie Est Belle e o Amber Rouge, que fixe o dia inteiro.
      ↳ E(3.92) pra(4.16) elas,(4.36) o(5.04) Good(5.12) Girl,(5.22) o(5.94) La(6.02) ... Amber(7.20) Rouge,(7.40) que(8.08) fixe(8.24) ...
[take 2 |  10.18 →  12.86] Até 30 % de desconto no site todo.
[take 2 |  13.72 →  15.68] Clique em Saiba mais e garante o seu.
```

`perfumes_citados.txt`:
```
[take 1 |  11.44] "Le Male, Elixir," → masculinos/le-male-elixir
[take 1 |  12.48] "Sauvage" → masculinos/sauvage-...
[take 1 |  13.12] "Bleu de Chanel," → masculinos/bleu-de-chanel
[take 2 |   5.12] "Good Girl," → femininos/good-girl-carolina-herrera
[take 2 |   6.02] "La Vie Est Belle" → femininos/la-vie-est-belle-lancome
[take 2 |   7.20] "Amber Rouge," → femininos/amber-rouge-edp
```

## Como o editor pensou

1. **Formato:** apresentador + oferta → `leo`, legenda `frase`, cartão final.
2. **Gancho:** "Se você ama perfume importado mas não quer pagar caro" → destaque "PERFUME IMPORTADO / SEM PAGAR CARO" quando ele fala "perfume" (1,82 s). "presta atenção" vira CAIXA ALTA na legenda (é o chamado).
3. **Cortes:** silêncio do começo sai (trecho começa em 0,56). "Corta, corta, vou de novo" (take 2, 0,94–3,04) **sai** — o trecho da take 2 começa em 3,82. Pausas entre frases o render tira sozinho.
4. **Whips:** na troca de assunto "o que é a Eau de Leon" (take 1, 6,10) e "e pra elas" (início da take 2). Só 2 whips em ~25 s.
5. **Perfumes:** grupo 1 masculinos (Le Male Elixir, Sauvage, Bleu de Chanel) entrando cada um no início do nome, some quando acaba a frase. Grupo 2 femininos com `drop` (momento "e pra elas"). Ids conferidos com `catalogo.py buscar`.
6. **Oferta:** "Até 30% de desconto no site todo" → impacto "ATÉ 30% DE DESCONTO / NO SITE TODO" com zoom 1,2 no trecho. Legenda some sozinha enquanto ele está na tela.
7. **Grafia:** "decan" → decant; "30 %" → 30%; "fixe" → fixa (erro do Whisper: no áudio ele fala "fixa"). "Clique em Saiba mais" fica como foi falado — correção é só grafia, nunca troca de palavra.

## O plano.json

```json
{
  "saida": "editado.mp4",
  "formato": "leo",
  "legenda": "frase",
  "trechos": [
    {"take": 1, "ini": 0.56, "fim": 5.25},
    {"take": 1, "ini": 6.10, "fim": 9.90, "transicao": "whip"},
    {"take": 1, "ini": 10.48, "fim": 16.40},
    {"take": 2, "ini": 3.82, "fim": 9.50, "transicao": "whip"},
    {"take": 2, "ini": 10.08, "fim": 13.00, "zoom": 1.2},
    {"take": 2, "ini": 13.62, "fim": 15.95}
  ],
  "correcoes": [
    {"de": "decan", "para": "decant"},
    {"de": "Le Male Elixir", "para": "Le Male Elixir"},
    {"de": "30 %", "para": "30%"},
    {"de": "fixe", "para": "fixa"}
  ],
  "legenda_maiusculas": [{"take": 1, "ini": 4.40, "fim": 5.20}],
  "textos": [
    {"texto": "ATÉ 30% DE DESCONTO\nNO SITE TODO", "estilo": "impacto", "take": 2, "ini": 10.18, "fim": 12.95},
    {"texto": "PERFUME IMPORTADO", "sub": "SEM PAGAR CARO", "estilo": "destaque", "take": 1, "ini": 1.82, "fim": 3.70}
  ],
  "perfumes": [
    {"itens": [
      {"id": "masculinos/le-male-elixir", "take": 1, "t": 11.44},
      {"id": "masculinos/bleu-de-chanel", "take": 1, "t": 13.12}
    ], "ate": {"take": 1, "t": 16.3}, "animacao": "pop"},
    {"itens": [
      {"id": "femininos/good-girl-carolina-herrera", "take": 2, "t": 5.12},
      {"id": "femininos/la-vie-est-belle-lancome", "take": 2, "t": 6.02},
      {"id": "femininos/amber-rouge-edp", "take": 2, "t": 7.20}
    ], "ate": {"take": 2, "t": 9.4}, "animacao": "drop"}
  ],
  "cartao_final": true,
  "musica": null
}
```

## Resultado

36 s de bruto → ~25,5 s editado (23,5 s de fala + 2 s de cartão), 9 pedaços (as pausas internas foram tiradas pelo render), 2 whips, 1 destaque no gancho, 5 perfumes em 2 fileiras, 1 impacto na oferta, cartão final com logo. Ao conferir os quadros: legenda na altura do peito, perfumes na fileira de baixo sem nenhum fundo, impacto digitando letra a letra, dissolve pro logo no fim.
