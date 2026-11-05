# 07 — O plano.json (o que o render lê)

Você escreve `<trabalho>/plano.json`. **Todo tempo é da take original**: `take` (1, 2, 3… na ordem que o usuário mandou) + segundos daquela take, copiados do `transcricao.txt`. O render converte pra linha do tempo final sozinho (inclusive quando um tempo cai num pedaço que foi cortado: vai pro próximo pedaço que ficou).

## Esquema completo

```jsonc
{
  "saida": "editado.mp4",            // nome do arquivo final (na pasta de trabalho)
  "formato": "leo",                  // "leo" | "creator"  (ver 01)
  "legenda": "frase",                // "frase" (leo) | "palavra" (creator) | "nenhuma"

  "trechos": [                       // ORDEM = ordem do vídeo final
    {"take": 1, "ini": 0.55, "fim": 5.30},
    {"take": 1, "ini": 6.10, "fim": 9.95, "transicao": "whip"},
    {"take": 2, "ini": 2.80, "fim": 8.40, "zoom": 1.25, "foco_x": 0.45, "manter_pausas": false}
  ],
  //  transicao: "corte" (padrão) | "whip" | "fade" | "flash"   — entra no começo do trecho
  //  zoom: força o enquadramento do trecho (padrão: alterna 1,00/1,12 a cada corte)
  //  foco_x / foco_y: 0..1, onde centralizar o recorte 9:16 (padrão 0,5)
  //  manter_pausas: true = não tira silêncios desse trecho

  "correcoes": [ {"de": "decan", "para": "decant"} ],
  "legenda_maiusculas": [ {"take": 1, "ini": 2.40, "fim": 3.10} ],

  "textos": [
    {"texto": "ATÉ 30% DE DESCONTO\nNO SITE TODO", "estilo": "impacto", "take": 2, "ini": 7.8, "fim": 10.2},
    {"texto": "QUIZ 100%\nGRATUITO", "sub": "E PERSONALIZADO", "estilo": "destaque", "take": 1, "ini": 6.9, "fim": 9.4},
    {"texto": "Melhor! 🤌", "estilo": "rotulo", "x": 0.18, "y": 0.62, "tamanho": 58, "take": 1, "ini": 0.0, "fim": 30.0}
  ],

  "perfumes": [
    {"itens": [ {"id": "masculinos/sauvage-edp", "take": 1, "t": 12.3} ],
     "ate": {"take": 1, "t": 16.0},    // opcional
     "animacao": "pop",                // pop | drop | slide | fade
     "tamanho": "normal",              // normal | grande
     "base_y": 0.78}                   // opcional: onde fica a base dos frascos (fração da tela)
  ],
  //  item pode ter "x"/"y" (0..1, centro do frasco) pra posição livre

  "broll": [
    {"arquivo": "../site.png", "take": 1, "ini": 9.1, "fim": 12.0, "transicao": "whip", "inicio_arquivo": 0}
  ],

  "divisorias": [ {"take": 1, "ini": 0, "fim": 12, "y0": 0.23, "y1": 0.62} ],   // linha branca do "Dia X Noite"
  "legenda_y": 0.58,                 // opcional: força a altura da legenda (padrão = automático pelo rosto)

  "cartao_final": true,              // padrão: true no leo, false no creator
  "musica": null                     // null | "auto" | "caminho/da/trilha.mp3"
}
```

(Os comentários `//` são só explicação — o arquivo real é JSON puro, sem comentários.)

## Regras de ouro

1. `trechos` nunca se sobrepõem na mesma take e nunca repetem fala.
2. `ini` < `fim` sempre; tempos dentro da duração da take.
3. Todo `id` de perfume existe (`catalogo.py buscar`). O render para com erro se não existir.
4. Tempos de texto/perfume/b-roll apontam para fala que **ficou** no vídeo. Se apontar pra um pedaço cortado, o elemento pula pro próximo pedaço — confira no `linha_do_tempo.json`.
5. Depois do render, `linha_do_tempo.json` mostra onde cada elemento caiu no vídeo final, e `legenda.srt` traz a legenda pronta.
