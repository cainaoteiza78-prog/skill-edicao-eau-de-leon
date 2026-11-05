# 04 — Textos grandes: impacto, destaque e rótulo

Os textos grandes ficam **no lugar da legenda** (no peito) por 1,5–3 s e carregam a promessa do vídeo. A tela nunca tem legenda e texto grande ao mesmo tempo.

## `impacto`: Bebas Neue, letra por letra
Visto em "ATÉ 30% DE DESCONTO / NO SITE TODO" e "30% DE DESCONTO / EM TODOS OS PERFUMES".
- Bebas Neue engrossada, branca, CAIXA ALTA, sombra suave.
- A 1ª linha é **digitada letra a letra** em 0,45 s. As linhas de baixo (78% do tamanho) surgem com as letras aparecendo embaralhadas logo depois.
- Uso: número, oferta, dado ("10% DE DESCONTO", "FRETE GRÁTIS", "+600 MIL POR MÊS").

## `destaque`: Bungee, com pop
Visto em "QUIZ 100% / GRATUITO / E PERSONALIZADO".
- Bungee branca, sombra mais escura, linhas quase encostando. Entra com **pop** (60% → 108% → 100% em 0,22 s).
- `sub` é a última linha, menor (82%), na mesma fonte.
- Uso: nome do produto, da ação ou do benefício ("PROMOÇÃO 10.10", "QUIZ 100% GRATUITO", "KIT DESCOBERTA").

## `rotulo`: texto nativo do TikTok/Instagram, com emoji
Visto em "POV: Você encontrou o perfume perfeito para balada!", "Sexy e muitooo impressionante! 👏😲🔥", "+/- 🫠", "Bom 🤗", "Melhor! 🤌", "Dia ☀️ X Noite 🌙".
- TikTok Sans SemiBold, branca, contorno preto fino. Frase normal (não caixa alta), emoji colorido junto.
- Posição livre: `x`, `y` em fração da tela (padrão no topo, `y` 0,14). Quebre linha com `\n`.
- `tamanho` opcional (padrão 62). Em rótulo de tier list use ~58.
- Fica parado; entra e sai com fade curto.
- Uso: formatos sem fala, ou rótulo fixo de comparação na fala da criadora.

## Quando usar

- **`leo`:** 1 destaque ou impacto no **gancho** (primeiros 0,3–3 s) e 1 na **oferta**. No máximo 3 em 30 s.
- **`creator`:** normalmente nenhum, ou um rótulo fixo.
- **Sem fala:** rótulo no topo (POV) e, se quiser, outro no rodapé com emoji.
- **Sem redundância:** o `fim` do texto vai até a última palavra que ele resume, e as palavras dele não podem reaparecer na legenda logo depois. Não use texto de impacto e destaques 3D com as mesmas palavras na mesma fala (ver 03).
- O texto entra **na palavra-chave** (`ini` = início da palavra no `transcricao.txt`) e fica até a ideia acabar.
- Curto: até ~20 caracteres por linha, até 3 linhas. Ele repete ou resume o que a pessoa fala; nunca traz informação nova.

```json
"textos": [
  {"texto": "PROMOÇÃO\n10.10", "estilo": "destaque", "take": 1, "ini": 1.00, "fim": 3.10},
  {"texto": "10% DE DESCONTO\nEM TODOS OS PERFUMES", "estilo": "impacto", "take": 2, "ini": 2.24, "fim": 4.70},
  {"texto": "POV: Você encontrou o\nperfume perfeito para balada!", "estilo": "rotulo", "y": 0.13, "take": 1, "ini": 0, "fim": 12}
],
"divisorias": [ {"take": 1, "ini": 0, "fim": 12, "y0": 0.23, "y1": 0.62} ]
```
`divisorias` desenha a linha branca vertical do meio (formato "Dia X Noite").
