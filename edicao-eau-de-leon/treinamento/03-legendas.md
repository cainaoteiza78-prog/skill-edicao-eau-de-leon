# 03 — Legenda padrão

A legenda da Eau de Leon é **sempre a mesma** e o render já faz tudo; seu trabalho é escolher o modo, corrigir grafia e marcar ênfases.

## Como ela é

- Fonte **Poppins Bold**, branca, halo escuro suave (sem caixa, sem contorno colorido).
- Tamanho discreto: uma frase de ~24 caracteres ocupa ~58% da largura.
- **Centro da tela, um pouco acima do meio** (centro em y = 830 de 1920, ~43%) — na altura do peito/queixo de quem fala, não embaixo.
- Uma linha só. Aparece **seca** (sem animação de entrada), troca no ritmo da fala.
- Minúscula como se fala: "quer usar", "perfume importado", "mas não faz ideia". O começo de frase também fica minúsculo; nomes próprios e marcas mantêm maiúscula ("a Eau de Leon lançou", "o Sauvage").
- Sem ponto final e sem vírgula. Mantém **?** e **!**.

## Modos (campo `legenda` no plano)

| Modo | Formato | Como agrupa |
|---|---|---|
| `frase` (padrão) | `leo` | 2 a 4 palavras, no máx. 24 caracteres; quebra em pausa > 0,35 s, ponto, ? e ! |
| `palavra` | `creator` | uma palavra por vez, no instante em que é falada |
| `nenhuma` | só se o usuário pedir (ex.: vídeo sem fala) | — |

## Ênfase em CAIXA ALTA (`legenda_maiusculas`)

O reel do Quiz mostra "DE QUAL ESCOLHER?" em maiúsculas — é a pergunta-chave do gancho. Use isso **com parcimônia**: no máximo 1 ou 2 por vídeo, sempre a pergunta do gancho ou a frase que vende (preço, desconto). Marque a janela de tempo (take original):
```json
"legenda_maiusculas": [{"take": 1, "ini": 2.40, "fim": 3.10}]
```

## Correções de grafia (`correcoes`)

O Whisper erra nome de perfume e de marca. Leia a transcrição procurando:
- "O de Leon", "Ô de Leon", "Eau de Lion" → **Eau de Leon**
- "decan", "de can" → **decant**
- nomes de perfume quebrados: "Le Male, Elixir" → **Le Male Elixir**, "Sovage" → **Sauvage**, "Bleu de Chanel" ok
- "saiba mais" → **Saiba mais** (CTA do anúncio)
- valores: "trinta por cento" → **30%**

Formato: `{"de": "como está na transcrição (1 ou mais palavras)", "para": "como deve aparecer"}`. O "de" é comparado sem acento/maiúscula/pontuação, palavra por palavra, e as palavras viram uma só na legenda.
```json
"correcoes": [
  {"de": "decan", "para": "decant"},
  {"de": "Le Male Elixir", "para": "Le Male Elixir"},
  {"de": "o de Leon", "para": "Eau de Leon"}
]
```
Nunca use correção pra mudar o que a pessoa falou — só a grafia do que ela falou.

## Quando a legenda some

Enquanto um **texto de impacto ou destaque** está na tela, a legenda some (é assim nos reels). O render faz isso sozinho. Por isso, não ponha texto de impacto por cima de fala importante que não esteja no próprio texto.
