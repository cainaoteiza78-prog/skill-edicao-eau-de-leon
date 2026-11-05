# 06 — B-roll, cartão final e áudio

## B-roll (imagens/vídeos de apoio)

Nos reels do Leo, quando ele fala do site, do produto, da embalagem ou da operação, a tela corta para a imagem disso **e a legenda continua por cima**. O áudio é sempre a fala original.

- Só use b-roll que o usuário mandou (prints do site, vídeo do frasco, embalagem) ou outra take dele mesmo mostrando o produto. Não busque imagem na internet.
- Tela cheia (cobre o quadro todo, recortado em 9:16 a partir do centro; ajuste com `foco_x`).
- Dura o tempo da fala que ele ilustra (normalmente 1,5–4 s). Nunca no gancho (os primeiros 2 s são o rosto).
- Entrada: `whip` (padrão), `corte` ou `slide` (desliza da esquerda).
- Para vídeo, `inicio_arquivo` diz de que segundo do arquivo começar.

```json
"broll": [
  {"arquivo": "../print-quiz.png", "take": 1, "ini": 9.10, "fim": 12.00, "transicao": "whip"},
  {"arquivo": "../embalagem.mp4", "take": 2, "ini": 3.00, "fim": 6.20, "inicio_arquivo": 1.5, "transicao": "corte"}
]
```
Caminho relativo é a partir da pasta de trabalho.

## Cartão final

- Formato `leo`: **sempre** (padrão `true`). O último quadro dissolve em 0,45 s para o fundo preto com o **logo Eau de Leon branco** (o "E" rosa/azul + "EAU DE LEON") no centro, e fica 2 s.
- Formato `creator`: **não** tem (padrão `false`).
- O logo está em `assets/logo/eau-de-leon-branco.png` (transparente). Não troque.
- Para desligar/ligar à força: `"cartao_final": false/true`.

## Áudio

- **Voz:** o render limpa graves (< 80 Hz) e nivela em **-14 LUFS** (padrão Instagram/TikTok). Micro-fade de 20–30 ms em cada corte pra não estalar.
- **Música suave de fundo: sempre, e sempre diferente** (padrão `"musica": "auto"`).
  - Se houver faixas **licenciadas** em `assets/musicas/` (mp3/wav/m4a), o render usa uma delas em **rodízio**: não repete a do vídeo anterior.
  - Se a pasta estiver vazia, o render **gera uma trilha nova** (`scripts/trilha.py`): lofi/ambiente calmo com piano elétrico, pad, baixo e batida leve. Tom, andamento (68–88 bpm), acordes e instrumentos são sorteados a cada vídeo. É feita na hora, então não tem direito autoral nem custo.
  - Fica bem baixa (~20 dB abaixo da voz) e **abaixa sozinha** quando alguém fala. Entra com fade de 0,8 s e sai com fade de 1,5 s junto com o cartão final.
  - `"musica": "caminho/trilha.mp3"` usa uma faixa específica; `"musica": null` tira a música (só se o usuário pedir).
  - O terminal mostra qual foi usada (`música: gerada (semente …)` ou `música: licenciada: …`). Para repetir exatamente uma trilha gerada: `python scripts/trilha.py trilha.wav --duracao 30 --semente <número>` e use o caminho em `"musica"`.
- Não adicione efeito sonoro (whoosh, pop, ding). O estilo não usa.
