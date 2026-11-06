# 11 — Verificação: assistir e corrigir o próprio vídeo

O dono reprovou entregas por erros que dava pra ver olhando o vídeo: legenda sobreposta, pessoa saindo do centro no zoom, legenda alta demais, destaque na palavra errada. **Toda edição passa por esta verificação antes de ser entregue**, em rodadas, até sair limpa.

## 1. Medição automática (não negociável)

```
python scripts/revisar.py <trabalho>/editado.mp4
python scripts/conferir.py <trabalho>/editado.mp4 --cada 0.5
```

| Linha | Tem que dar | Se der PROBLEMA |
|---|---|---|
| SOBREPOSIÇÃO de legendas | OK | duas legendas no mesmo instante: o render já corta uma na entrada da próxima; se ainda aparecer, há texto grande/destaque com tempo cruzado no plano → ajuste `ini`/`fim` |
| CENTRALIZAÇÃO | OK (rosto a ≤ 5% do meio) | o enquadramento segue o rosto sozinho; se falhar, a pessoa sai do quadro ou o rosto não é detectado (óculos escuros, perfil) → use `"foco_x"` no trecho ou `"fixo": true` |
| POSIÇÃO da legenda | OK (peito) | legenda alta (pescoço): aumente `"legenda_y"` (0,70–0,78) |
| PAUSAS que sobraram | nenhuma | trecho com `manter_pausas` sem necessidade, ou `fim` do trecho largo demais |
| PALAVRAS | todas inteiras | aumente o trecho 0,2 s no lado da palavra cortada |

## 2. Assistir (você, com os olhos)

Abra **todas** as folhas `conferir/conferir_XX.png` (8 quadros cada, um a cada 0,5 s) e confira em cada quadro:

- [ ] **Uma** legenda só na tela; nada encavalado; nenhuma legenda repetindo um texto grande.
- [ ] Legenda no **peito**, sem cobrir a boca/queixo; mesma altura o vídeo todo.
- [ ] Pessoa **centralizada** também nos zooms (olhe os quadros com zoom de ênfase e punch).
- [ ] Destaque **só** no que vende (QUANTO / EM QUÊ / ATÉ QUANDO / FORTE). Nunca "liberamos", "ouviu", "até o".
- [ ] Destaque aparece **sozinho**, depois da palavra comum anterior.
- [ ] Grafia certa (Eau de Leon, Saiba mais, nomes de perfume, "10%").
- [ ] Nenhum texto cortado na borda da tela.
- [ ] CTA: **uma** placa só, "SAIBA MAIS", do tamanho da legenda, logo abaixo dela; vidro transparente e borrado (quase sem cor); letras rosa (feminino) / azul (masculino); não tapa o rosto, fica acima da marca d'água.
- [ ] Pontas das takes: nenhuma voz de bastidor no vídeo final. Se houve alerta, re-transcreva 2–3 s em volta do corte entre as takes e confira.
- [ ] Marca d'água no rodapé do primeiro ao último quadro; sem cartão final.
- [ ] Algo muda a cada 2–3 s (pacing), sem quadros "parados" seguidos.

## 3. Corrigir e repetir

Cada erro → corrija no plano (ou no parâmetro indicado) → `render.py --rapido` → **repita 1 e 2 inteiros**. Só faça o render final quando uma rodada inteira sair sem nenhum erro. Na entrega, diga quantas rodadas de verificação foram feitas e o que foi corrigido.
