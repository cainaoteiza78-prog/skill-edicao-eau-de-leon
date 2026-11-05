# 04 — Textos de impacto e destaque

São os textos **grandes** que aparecem por cima, no lugar da legenda, por 1,5–3 s. Eles carregam a promessa do vídeo. Ficam na mesma região da legenda (centro, ~40% da altura), então a tela nunca fica poluída: ou tem legenda, ou tem texto grande.

## Dois estilos

### `impacto` — condensado, letra por letra
Visto em "ATÉ 30% DE DESCONTO / NO SITE TODO" e "30% DE DESCONTO / EM TODOS OS PERFUMES / DO SITE".
- **Oswald Bold**, branco, CAIXA ALTA, halo escuro.
- Animação: a 1ª linha é **digitada letra a letra** em 0,45 s; as linhas de baixo (menores, 78%) surgem com as letras aparecendo embaralhadas logo depois. Sai com fade de 0,12 s.
- Uso: número, oferta, dado — "ATÉ 30% DE DESCONTO", "FRETE GRÁTIS", "+600 MIL POR MÊS", "DECANT DE 5ML".

### `destaque` — arredondado e gordo, com pop
Visto em "QUIZ 100% / GRATUITO / E PERSONALIZADO".
- **Titan One** branco com sombra escura sólida; a última linha opcional (`sub`) vem em **Poppins ExtraBold** menor.
- Animação: **pop** (cresce de 60% → 108% → 100% em 0,22 s). Sai com fade 0,15 s.
- Uso: nome de produto/lançamento/benefício principal — "QUIZ 100% GRATUITO", "KIT DESCOBERTA", "CUPOM EXCLUSIVO".

### `rotulo` — texto fixo pequeno (formatos sem fala)
Poppins Bold 46, branco, posição livre (`x`, `y` em fração da tela). Ex.: "+/- 🫠", "Bom", "Melhor!", "Dia X Noite". Use só se pedirem esse formato.

## Quando usar (regra de ouro: menos é mais)

- **Formato `leo`:** 1 texto no **gancho** (primeiros 0,3–3 s) com a promessa, e 1 na **oferta/CTA**. Máximo 3 por vídeo de 30 s.
- **Formato `creator`:** normalmente nenhum.
- O texto aparece **quando a palavra-chave é falada** (o tempo `ini` é o início da palavra no `transcricao.txt`) e fica até a pessoa terminar a ideia (1,5–3 s).
- Texto **curto**: até ~20 caracteres por linha, até 3 linhas. Use `\n` pra quebrar linha. Corte artigos: "ATÉ 30% DE DESCONTO\nNO SITE TODO", não "VOCÊ TEM ATÉ 30% DE DESCONTO EM TODO O NOSSO SITE".
- O texto diz o que a pessoa está falando (ou o resumo exato). Nunca uma informação nova.

## Exemplo no plano
```json
"textos": [
  {"texto": "ATÉ 30% DE DESCONTO\nNO SITE TODO", "estilo": "impacto", "take": 2, "ini": 7.80, "fim": 10.20},
  {"texto": "QUIZ 100%\nGRATUITO", "sub": "E PERSONALIZADO", "estilo": "destaque", "take": 1, "ini": 6.90, "fim": 9.40}
]
```
