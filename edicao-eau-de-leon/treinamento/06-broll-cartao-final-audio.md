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
- **Música:** os reels usam "áudio original" — a voz manda. Trilha é opcional:
  - `"musica": null` (padrão) → sem trilha.
  - `"musica": "auto"` → usa a primeira faixa em `assets/musicas/` (coloque lá trilhas **licenciadas/sem direitos**).
  - `"musica": "C:/caminho/trilha.mp3"` → essa faixa.
  - A trilha fica bem baixa (volume 0,12) e **abaixa sozinha** quando alguém fala (sidechain); entra com fade de 0,8 s e sai com fade de 1,5 s.
- Não adicione efeito sonoro (whoosh, pop, ding). O estilo não usa.
