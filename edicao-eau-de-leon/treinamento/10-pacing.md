# 10 — Pacing: o ritmo que deixa o vídeo gostoso de assistir

**Pacing** é a cadência dos acontecimentos na tela. O olho perde o interesse quando nada muda; cansa quando tudo muda junto. Um vídeo da Eau de Leon tem que parecer rápido e leve, sem ficar poluído.

## As 7 regras

1. **Gancho em até 1,5 s.** A primeira palavra entra no quadro 0 (sem silêncio). O texto grande do gancho aparece na palavra-chave dele, nunca depois de 1,5 s.
2. **Algo muda a cada 2–3 s, no máximo.** Conta como mudança: corte, troca de enquadramento (punch), palavra-chave aumentada, texto grande, perfume entrando, b-roll, whip. O render cuida disso sozinho:
   - nos cortes de respiração, o enquadramento alterna 1,00 ↔ 1,12;
   - num pedaço que passa de 2,6 s sem corte, ele faz um **punch** a cada ~2,4 s (troca o enquadramento num respiro entre palavras, sem cortar nada da fala).
3. **A palavra-chave bate junto com a fala.** A legenda aumentada entra no instante da palavra e a câmera "chega perto" 8% (zoom de ênfase) e volta. Imagem, texto e voz no mesmo tempo: é isso que dá a sensação de "pancada".
4. **Um evento grande de cada vez.** Nunca dois textos grandes juntos, nem destaque em cima de texto de impacto, nem perfume em cima de destaque. Depois de um momento cheio, deixe ~1 s só de legenda normal pra respirar. O render já evita punch colado numa ênfase.
5. **Zero tempo morto.** Sem pausa > 0,15 s, sem "é…", sem silêncio no fim. O `conferir.py` mede.
6. **O CTA pulsa no ritmo da fala.** O botão "SAIBA MAIS" pulsa uma vez a cada ~2–3 palavras faladas (calculado pela velocidade da fala do vídeo, entre 0,8 e 1,3 s por pulso). Lento e constante, como se pedisse o clique.
7. **A música empurra, a voz manda.** Música animada (104–124 bpm) dá energia, mas fica ~15 dB abaixo da voz (baixinha, ver 06).

## Curva do vídeo (formato `leo`, 15–30 s)

| Trecho | Duração | Densidade | O que acontece |
|---|---|---|---|
| Gancho | 0–3 s | **alta** | texto grande na palavra-chave + zoom de ênfase |
| Corpo / oferta | 3–12 s | **média-alta** | legenda aumentada em QUANTO / EM QUÊ / ATÉ QUANDO, punches, perfumes |
| Reforço | 12–15 s | média | repetição da oferta (legenda aumentada de novo) |
| CTA | últimos 2–4 s | **foco** | só a legenda + o botão pulsando até o fim |

## Como conferir o pacing

- O render imprime `pacing: N punch(es) de enquadramento, M zoom(s) de ênfase`. Num vídeo de 15–20 s, espere de 2 a 6 punches e de 3 a 6 ênfases.
- Nas folhas do `conferir.py` (um quadro por segundo), quadros vizinhos não podem parecer idênticos por mais de 3 seguidos.
- Se estiver monótono: ponha mais 1 destaque (oferta, escopo ou prazo) ou um b-roll. Se estiver poluído: tire o destaque mais fraco (ex.: "imperdível").
- Pra travar o enquadramento de um trecho (pessoa mostrando um produto, sem punch), use `"fixo": true` no trecho do plano.
