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

## Destaque de palavra-chave: GLASSMORPHISM (`destaques`)

A palavra que vende sai da legenda e aparece num **painel de vidro fosco**, logo abaixo da frase (que continua normal em cima). O visual é realista e premium, nada de cara de desenho:
- o **vídeo atrás do painel fica desfocado de verdade** (o render recorta, desfoca e devolve aquele pedaço);
- película translúcida por cima, borda fina de luz, reflexo suave no topo e sombra difusa embaixo (o painel "flutua");
- texto **Poppins Bold** em CAIXA ALTA, espaçado, branco, com sombra sutil;
- entrada discreta: aparece em 0,22 s subindo 24 px. **Nada** de giro, quique ou cor saturada: é isso que deixa o visual infantil.
- a câmera chega 8% mais perto junto (zoom de ênfase, ver 10-pacing).

```
         liberamos              ← legenda normal (Poppins branca)
   ╭──────────────────────╮
   │   10% DE DESCONTO    │     ← vidro fosco (fundo desfocado)
   ╰──────────────────────╯
```

A película varia sozinha, em rodízio: clara, azulada (azul da marca), rosada (rosa da marca). Sempre bem sutil, porque o vidro é quase transparente.

### Como identificar as palavras-chave (a regra da oferta)

Em fala de promoção, destaque **sempre** estas 3 coisas, toda vez que forem faladas:

1. **QUANTO**: o valor da vantagem, junto com o que ele é: "**10% DE DESCONTO**", "**10%**", "**R$ 50 OFF**", "**FRETE GRÁTIS**".
2. **EM QUÊ**: onde vale: "**TODOS OS PERFUMES**", "**SITE TODO**", "**PRIMEIRA COMPRA**".
3. **ATÉ QUANDO**: o prazo (só o número ou a data): "até o dia **10**", "só **HOJE**".

Exemplo do dono: "liberamos **10% DE DESCONTO** em **TODOS OS PERFUMES** até o dia **10** desse mês. Isso mesmo que você ouviu, **10%** em **TODOS OS PERFUMES**."

Também podem ganhar vidro: um adjetivo muito forte ("imperdível", "exclusivo"), mas só se o vídeo estiver com poucos destaques. **Nome de perfume** não vira 3D: vai em CAIXA ALTA dentro da legenda (`"estilo": "caps"`), como nos anúncios da marca ("esse aqui é o CREED AVENTUS").

O `transcrever.py` gera `destaques_sugeridos.txt` já marcando QUANTO / EM QUE / ATE QUANDO / CTA-botao / FORTE com os tempos. Confira e copie:
```json
"destaques": [
  {"take": 2, "ini": 2.24, "fim": 3.54},
  {"take": 2, "ini": 3.72, "fim": 4.76},
  {"take": 2, "ini": 5.50, "fim": 5.94},
  {"take": 1, "ini": 1.20, "fim": 2.10, "estilo": "caps"}
]
```
`ini`/`fim` cobrem **só as palavras destacadas**, até 4 palavras.

### "SAIBA MAIS" é SEMPRE um botão

O CTA de clique ("saiba mais", "link na bio", "clica aqui", "compre agora") é desenhado como um **botão de vidro**:
- pílula de **vidro escuro** fosco (contraste em qualquer fundo), texto branco Poppins Bold, maior que todos os outros textos;
- borda de luz, reflexo no topo, sombra difusa e um halo bem leve;
- aparece no peito, logo abaixo da legenda, saltando da tela;
- **fica até o fim do vídeo pulsando devagar** (cresce 7% e volta), no ritmo da fala, uma vez a cada ~2–3 palavras;
- é só visual, mas induz a pessoa a clicar no botão real do anúncio.

O render cria o botão **sozinho** sempre que a legenda tiver "Saiba mais" (depois das correções de grafia). Garanta só que a grafia está certa: o Whisper costuma ouvir "saia mais" ou "salha mais", então corrija com `{"de": "salha mais", "para": "Saiba mais"}`.

### Nada de legenda repetida (redundância)

**A mesma informação nunca aparece duas vezes na mesma fala.** Se um texto grande (`impacto` ou `destaque`) mostrou "PROMOÇÃO 10.10", a legenda que vem depois não pode repetir "10.10": ela continua de onde o texto grande parou ("da Eau de Leon já começou"). O render faz isso sozinho, de dois jeitos:
- some da legenda toda palavra falada enquanto o texto grande está na tela;
- some também a palavra logo depois dele que só repete o que ele já mostrou.

Seu cuidado ao planejar:
- O `fim` do texto grande deve ir até a **última palavra que ele resume** (em "a promoção do dia 10 do 10", até o fim do segundo "10").
- Não ponha texto grande e vidro com as mesmas palavras na mesma fala. Ou é texto de impacto ("10% DE DESCONTO / EM TODOS OS PERFUMES"), ou são destaques em vidro nas palavras. Na dúvida, use os destaques em vidro.
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
