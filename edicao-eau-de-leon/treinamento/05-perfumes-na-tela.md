# 05 — Perfumes na tela (fotos sem fundo)

Sempre que um perfume do catálogo é **falado**, a foto dele (sem fundo, com transparência real) aparece na tela no instante da fala. É a marca registrada dos reels da criadora ("perfumes óbvios": Sauvage, Le Male, Invictus, 1 Million surgindo em fileira) e vale também no formato `leo` quando ele cita um perfume.

## O catálogo

- `assets/perfumes/femininos/*.png`, `assets/perfumes/masculinos/*.png` — foto principal de cada perfume.
- `.../outros-angulos/*.png` — fotos alternativas (frasco com caixa, deitado, ou **close** de detalhe). Os closes encostam na borda da foto (o frasco aparece cortado de propósito): **nunca** use close na fileira; só a foto com o frasco inteiro. Abra o PNG com Read antes de usar um "outro ângulo".
- `assets/perfumes/perfumes.json` — id, nome e **apelidos** de cada um. Todas as imagens vieram da área de membros da Mentoria (pasta "Imagens Parfum") e tiveram o fundo removido de verdade (canal alfa) — não existe fundo branco/preto/xadrez "falso".

Achar o id certo:
```
python scripts/catalogo.py buscar "le male elixir"
python scripts/catalogo.py listar masculinos
```
O `transcrever.py` já gera `perfumes_citados.txt` com o que ele reconheceu. **Confira cada linha**: o reconhecimento é por nome; "o azulzinho" ou "esse aqui" não é reconhecido, e um nome parecido pode cair no perfume errado (ex.: "212 VIP" x "212 VIP Rosé" — o feminino é o Rosé; o masculino é "212 VIP Men"). Se o vídeo é de perfume masculino, prefira o id em `masculinos/`.

Perfume citado que não existe no catálogo: **não coloque nada** e avise no final. Para incluir um novo: salve a foto em qualquer pasta e rode `python scripts/remover_fundo.py foto.jpg assets/perfumes/masculinos` e depois `python scripts/catalogo.py gerar`.

## Como aparecem (padrão observado)

- **Fileira logo abaixo da legenda** (que fica no peito): frascos lado a lado, centralizados, ~300 px de altura (15% do quadro). Até 4 por fileira; com 4, ficam 10% menores. Pra forçar a altura, use `"base_y": 0.78` no grupo (fração da tela, onde fica a base dos frascos).
- Cada frasco entra **no instante em que o nome começa a ser falado**, na sua posição da fileira (da esquerda pra direita, na ordem da fala). Os anteriores ficam.
- Quando a pessoa passa pra outro grupo/assunto, a fileira inteira some e começa uma nova (novo grupo no plano).
- **Sem sombra**: nos reels o frasco entra "chapado" sobre o vídeo.
- Perfume único, protagonista do vídeo: `"tamanho": "grande"` (460 px de altura).

## Animações (campo `animacao`, por grupo ou por item)

| Valor | Como entra | Quando usar |
|---|---|---|
| `pop` (padrão) | surge em 0,10 s subindo 22 px | sempre que não houver motivo pra outra — é o mais fiel ao perfil |
| `drop` | cai de 220 px acima, freia no lugar (0,30 s) | perfume "caindo do céu" na revelação, "o melhor de todos" |
| `slide` | desliza da lateral (esquerda se o slot está à esquerda) em 0,32 s | comparação "esse x esse" |
| `fade` | aparece em 0,30 s sem mexer | perfume que fica muito tempo na tela, clima calmo |

Todos saem com fade de 0,12 s. Use **uma** animação por vídeo (consistência); `drop`/`slide` só para um momento especial.

## Tempo na tela

- Se você não puser `ate`, o grupo fica até o próximo grupo começar ou ~3,5 s depois do último item (o que vier primeiro).
- Ponha `ate` quando a pessoa continua falando daqueles perfumes por mais tempo, ou para tirar antes do CTA.
- Perfume e texto de impacto **não** dividem a tela: tire o grupo antes do texto entrar.

## Exemplo no plano
```json
"perfumes": [
  {"itens": [
     {"id": "masculinos/le-male-elixir", "take": 1, "t": 11.10},
     {"id": "masculinos/sauvage-edp",    "take": 1, "t": 12.35},
     {"id": "masculinos/bleu-de-chanel-edp", "take": 1, "t": 13.20}
   ],
   "ate": {"take": 1, "t": 16.20},
   "animacao": "pop"}
]
```
`t` = início da palavra do nome do perfume no `transcricao.txt` (take original).
