# 06 — B-roll, marca d'água e áudio

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

## Marca d'água (sempre) e NADA de cartão final

- **Proibido terminar com cartão final** (logo no fundo preto). O dono não gostou e pediu para nunca mais usar. O render não tem mais essa opção.
- O logo da Eau de Leon aparece como **marca d'água o vídeo inteiro**: pequeno (180 px de largura), centralizado, 70 px acima da borda de baixo, 90% de opacidade. O render coloca sozinho, não precisa pôr no plano.
- O vídeo termina na última palavra do CTA + 0,35 s parado (o anúncio do Meta come os últimos quadros).
- O logo está em `assets/logo/eau-de-leon-branco.png` (transparente). Não troque.

## Áudio

- **Voz:** o render limpa graves (< 80 Hz) e nivela em **-14 LUFS** (padrão Instagram/TikTok). Micro-fade de 20–30 ms em cada corte pra não estalar.
- **Música de fundo: sempre, animada e sempre diferente** (padrão `"musica": "auto"`). Tem que passar uma sensação **divertida** e dinâmica, sem roubar a cena da fala.
  - Se houver faixas **licenciadas** em `assets/musicas/` (mp3/wav/m4a), o render usa uma delas em **rodízio** e não repete a do vídeo anterior. Coloque lá só músicas alegres (pop, funk leve, house, tropical).
  - Se a pasta estiver vazia, o render **compõe uma trilha nova** (`scripts/trilha.py`): tom maior, 104–124 bpm, bumbo + palma + chimbal, baixo sincopado, acordes no contratempo e arpejo brilhante (marimba/pluck), com partes que mudam a cada 4 compassos. O clima (`pop`, `funk`, `house`, `tropical`), o tom, o andamento e os acordes são sorteados a cada vídeo. É feita na hora: sem direito autoral e sem custo.
  - Volume: **~15 dB abaixo da voz** (`musica_volume` 0,13 no render; era 0,171 e o dono pediu pra abaixar pelo menos 20% em 06/11). Dá pra perceber a música, mas ela nunca disputa com a voz; abaixa um pouco quando alguém fala (sem sumir). Não suba esse volume. Entra com fade de 0,8 s e sai com fade de 1 s no fim.
  - `"musica": "caminho/trilha.mp3"` usa uma faixa específica; `"musica": null` tira a música (só se o usuário pedir).
  - O terminal mostra qual foi usada (`música: gerada: funk, 110 bpm (semente …)`). Para repetir uma trilha gerada: `python scripts/trilha.py trilha.wav --duracao 30 --semente <número> --clima funk` e use o caminho em `"musica"`.
- Não adicione efeito sonoro (whoosh, pop, ding). O estilo não usa.
