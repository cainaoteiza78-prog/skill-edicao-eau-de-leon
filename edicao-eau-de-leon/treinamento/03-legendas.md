# 03 — Legenda padrão

A legenda é **sempre a mesma** e o render faz tudo. Seu trabalho é escolher o modo, corrigir a grafia e marcar as ênfases.

## Como ela é (igual aos reels)

- **Poppins Bold**, branca, grande, com **contorno escuro** (3 px, como a Eau de Leon usa hoje) e **sombra preta suave** deslocada pra baixo.
- Uma linha só. Uma frase de ~22 caracteres ocupa ~55% da largura.
- **Na altura do PEITO, não do pescoço.** O render detecta o rosto e põe o centro da legenda ~1,5 rosto abaixo do queixo (num plano médio, y ≈ 1450–1550 de 1920), uma vez pro vídeo todo. Se cair no pescoço, force com `"legenda_y": 0.76`.
- Aparece seca, sem animação de entrada, e troca no ritmo da fala.
- Minúscula como se fala: "quer usar", "mas não faz ideia". O começo de frase também fica minúsculo; nomes próprios e marcas mantêm a maiúscula ("a Eau de Leon lançou", "o Sauvage").
- Sem ponto final e sem vírgula. Mantém **?** e **!**.

## Ritmo: palavra por palavra

A legenda passa **rápido, uma palavra por vez**, no instante em que cada uma é falada (é o que deixa o vídeo dinâmico). Só se juntam:
- **artigo + palavra seguinte:** "o perfume", "os perfumes", "uma fragrância" (o, a, os, as, um, uma);
- **as palavras de um mesmo destaque:** "10% DE DESCONTO", "TODOS OS PERFUMES", "DIA 10".

Exemplo real: `liberamos` → `10% DE DESCONTO` → `em` → `TODOS OS PERFUMES` → `até` → `o` → `DIA 10` → `desse` → `mês`.

Campo `legenda`: `palavra` (padrão; `frase` também vira palavra por palavra) ou `nenhuma` (formatos sem fala).

## Destaque de palavra-chave: a PRÓPRIA legenda aumentada (`destaques`)

É assim que a Eau de Leon faz ("QUE UM DECANT DE 2 ML / RENDE MUITO"): no instante da palavra-chave, a legenda **cresce** e vira:
- **Bebas Neue** engrossada, CAIXA ALTA, branca;
- **borda escura** (mais grossa que a da legenda comum) e **sombra maior**;
- entra com um pop curto, e a câmera chega 8% mais perto, centralizada no rosto (ver 10-pacing).

**O destaque é SEMPRE um bloco só dele.** A frase normal vem antes, em legenda comum, e só depois a palavra-chave aparece grande:
`liberamos` (comum) → `10% DE DESCONTO` (grande). Nunca "LIBERAMOS / 10% DE DESCONTO" juntos.

**Sem vidro, sem cor, sem caixa** nos destaques do corpo. O glassmorphism é só do CTA final.

### Como identificar as palavras-chave (o que destacar e o que NÃO destacar)

Destaque **só a palavra que vende**, toda vez que ela for falada. Na promoção, são 4 tipos:

| Tipo | O que destacar (exatamente) | Exemplo |
|---|---|---|
| QUANTO | o valor + o que ele é | "**10% DE DESCONTO**", "**10%**", "**FRETE GRÁTIS**", "**R$ 50 OFF**" |
| EM QUÊ | onde vale | "**TODOS OS PERFUMES**", "**SITE TODO**", "**PRIMEIRA COMPRA**" |
| ATÉ QUANDO | "dia" + número, ou a data | "até o **DIA 10**", "só **HOJE**" (o "até o" fica em legenda comum) |
| FORTE | o adjetivo que vende a promoção | "simplesmente **IMPERDÍVEL**", "**EXCLUSIVO**" |

Exemplo do dono, certinho: "a promoção 10.10 já começou e ela tá simplesmente **IMPERDÍVEL**. Liberamos **10% DE DESCONTO** em **TODOS OS PERFUMES** até o **DIA 10** desse mês. Isso mesmo que você ouviu, **10%** em **TODOS OS PERFUMES**."

**Nunca destaque:**
- verbo ou conector da frase: "liberamos", "ouviu", "isso mesmo", "até o", "em", "que";
- a palavra que vem antes ou depois da palavra-chave, só porque está colada nela;
- o que já está num texto grande na tela (redundância);
- **nome de perfume:** vai em CAIXA ALTA dentro da legenda comum (`"estilo": "caps"`), como nos anúncios da marca ("esse aqui é o CREED AVENTUS").

O `transcrever.py` gera `destaques_sugeridos.txt` com QUANTO / EM QUE / ATE QUANDO / FORTE / CTA-botao e os tempos certos de **só** essas palavras. Copie os tempos (`ini` da 1ª palavra, `fim` da última):
```json
"destaques": [
  {"take": 1, "ini": 4.86, "fim": 5.72},
  {"take": 2, "ini": 2.24, "fim": 3.54},
  {"take": 2, "ini": 3.72, "fim": 4.76},
  {"take": 2, "ini": 5.30, "fim": 5.94}
]
```

### "SAIBA MAIS" é SEMPRE uma placa de vidro 3D (o único glassmorphism)

**Só a expressão "Saiba mais" vira placa de vidro. Mais nada.** "Clica aqui", "link na bio", "compre agora", "garanta o seu" ficam na **legenda comum**. E é **UMA placa por vídeo**: se "saiba mais" for falado duas vezes, o segundo vira legenda comum. Erro real reprovado pelo dono (06/11): "CLICA AQUI" e "SAIBA MAIS" viraram duas placas, uma pulsando em cima da outra.

A placa é desenhada quadro a quadro pelo `scripts/cta.py`:
- **placa de vidro flutuando em 3D:** o vídeo atrás fica desfocado de verdade, a placa tem perspectiva (levemente inclinada), espessura lateral, borda de luz, reflexo diagonal e sombra no "chão";
- **o texto também é de vidro:** degradê da mesma cor, textura granulada, glow da própria cor, fio de luz em cima das letras e sombra que descola o texto da placa;
- **tamanho da legenda comum:** as letras têm a mesma altura da legenda (Poppins 100) e a placa só abraça o texto. Nada de botão gigante (reprovado em 06/11);
- **vidro TRANSPARENTE e borrado:** a face é quase invisível — o que se vê é o vídeo de trás **desfocado de verdade**, com um véu branco bem leve e **só um pouco** da cor da marca, só pra dar a sensação de vidro. Vidro colorido/opaco foi reprovado (06/11). A espessura é só uma aresta clara embaixo;
- **cor pelo PÚBLICO da copy** (só nas letras, com leve fade lateral): vídeo para **mulheres → rosa** (#F2A595), para **homens → azul** (#6BA9CF), **unissex → tanto faz** (o render escolhe a que mais contrasta com o fundo). Você decide o público lendo a copy/transcrição e escreve no plano `"publico": "feminino" | "masculino" | "unissex"`. Pistas: "cheirosa", "linda", "poderosa", perfume feminino, falar com "amiga" → feminino; "cheiroso", "homem", perfume masculino → masculino; nenhuma pista ou as duas → unissex. Se o plano não disser, o render conta essas pistas sozinho (linha `público:` no terminal). `"cta_cor"` força a cor e só se usa se o usuário pedir;
- aparece **logo abaixo da legenda** (sem encostar nela), acima da marca d'água, saltando da tela, quase sem inclinação, com sombra de contato e sombra no "chão", e **fica até o fim** pulsando devagar no ritmo da fala e flutuando de leve.

O render cria o CTA **sozinho** sempre que a legenda tiver "Saiba mais" (depois das correções de grafia). Garanta só a grafia: `{"de": "salha mais", "para": "Saiba mais"}`.

### Nada de legenda repetida (redundância)

**A mesma informação nunca aparece duas vezes na mesma fala.** Se um texto grande (`impacto` ou `destaque`) mostrou "PROMOÇÃO 10.10", a legenda que vem depois não pode repetir "10.10": ela continua de onde o texto grande parou ("da Eau de Leon já começou"). O render faz isso sozinho, de dois jeitos:
- some da legenda toda palavra falada enquanto o texto grande está na tela;
- some também a palavra logo depois dele que só repete o que ele já mostrou.

Seu cuidado ao planejar:
- O `fim` do texto grande deve ir até a **última palavra que ele resume** (em "a promoção do dia 10 do 10", até o fim do segundo "10").
- Não ponha texto grande e destaque com as mesmas palavras na mesma fala. Ou é texto de impacto ("10% DE DESCONTO / EM TODOS OS PERFUMES"), ou são destaques em vidro nas palavras. Na dúvida, use os destaques.
- Leia o `legenda.srt`: nenhuma palavra do texto grande pode reaparecer logo depois dele.

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
