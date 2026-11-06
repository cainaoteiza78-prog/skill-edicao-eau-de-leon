# 12 — Aprender com cada pedido de alteração (a skill melhora sozinha)

A skill aprende **na máquina de quem usa**. Todo pedido de alteração do usuário ("abaixa a música", "isso devia ter sido cortado", "o botão tá grande") é um erro que **não pode se repetir**. Por isso, além de consertar o vídeo, você grava a lição na **base de conhecimento local**: `aprendizados/aprendizados.md`.

## Quando gravar

Sempre que o usuário pedir para mudar algo numa edição que você entregou, **inclusive elogio com ressalva** ("ficou bom, mas…"). Uma lição por item pedido. Se ele pedir 3 coisas, são 3 lições.

Não grave:
- escolha que só vale para aquele vídeo e não é erro ("nesse aqui tira o destaque do preço, o cliente pediu"). Se ficar em dúvida, pergunte uma vez: "Isso vale pros próximos vídeos também?";
- conteúdo específico (o texto de uma fala, o nome de um arquivo).

## Como escrever uma boa lição

A lição tem que servir para **qualquer vídeo futuro**, não só para o atual. Transforme o pedido em regra geral:

| Pedido do usuário | Regra ruim (específica) | Regra boa (geral) |
|---|---|---|
| "depois de 'eu te apresento o Light Blue' dá pra ouvir 'pode ir, pode?'" | cortar "pode ir" no vídeo do Light Blue | voz de fora do quadro no começo/fim da take sempre sai: conferir o alertas.txt contra a copy antes de fechar os trechos |
| "abaixa a música uns 20%" | música 0,13 neste vídeo | música sempre ~15 dB abaixo da voz; nunca mais alta que isso |
| "o saiba mais tá gigante e muito colorido" | diminuir o botão | placa do SAIBA MAIS do tamanho da legenda, vidro transparente e borrado, quase sem cor |

Comando (use o Python da skill, `scripts/python.txt`):
```
python scripts/aprender.py adicionar --area cta \
  --pedido "<o que o usuário disse, com as palavras dele>" \
  --regra "<regra geral, curta, no imperativo>" \
  --como "<como aplicar e como conferir na próxima edição>" \
  --video "<qual vídeo>" \
  --mudou "<arquivo/parâmetro que você alterou na skill, se alterou>"
```
Áreas: `cortes`, `bastidor`, `legenda`, `destaques`, `textos`, `cta`, `perfumes`, `broll`, `enquadramento`, `audio`, `musica`, `cores`, `ritmo`, `entrega`, `outro`.

Se a mesma lição já existe, o script **não duplica**: ele aumenta o contador "Pedido N vezes". Lição com contador alto é erro que a skill insiste em cometer, então ela tem prioridade máxima na próxima conferência.

## Quando o erro é de PADRÃO (código), mude o padrão também

Se o pedido muda algo que o render faz sozinho em todo vídeo (volume da música, tamanho ou cor de um elemento, posição, velocidade), **só gravar a lição não basta**: ajuste o valor padrão no script certo, pra que o próximo vídeo já saia certo. Os pontos mais comuns:

| O que | Onde |
|---|---|
| volume da música | `scripts/render.py`, `ESTILO['musica_volume']` |
| tamanho, fonte, contorno e sombra da legenda/destaques | `scripts/textos.py`, `ESTILO_TEXTO` |
| botão de vidro SAIBA MAIS (tamanho, vidro, pulso) | `scripts/cta.py` |
| posição do botão | `scripts/textos.py` (`'cy'` do CTA) |
| o que vira botão | `scripts/letreiros.py`, `CTA_BOTAO` |
| palavras de bastidor | `scripts/cortes.py`, `BASTIDOR` / `FORTES` |
| marca d'água | `scripts/render.py`, `ESTILO['marca_dagua']` |

Mude o mínimo, renderize o vídeo de novo, faça a verificação completa (11) e diga no `--mudou` o que alterou.

**Atenção às atualizações:** a base `aprendizados/aprendizados.md` sobrevive quando a skill é atualizada pelo instalador, mas as **mudanças de código não**: a atualização traz o código do GitHub. Por isso a lição tem que estar sempre gravada: depois de atualizar, a skill lê a lição e refaz o ajuste se o código novo não tiver ele. Ao refazer, avise o usuário.

## Antes de cada edição

Rode `python scripts/aprender.py listar` e leia **todas** as lições, antes do treinamento. **As lições valem mais que o treinamento**: são o pedido mais recente de quem usa a skill. Na verificação (passo 5), confira cada lição como um item do checklist.

## Ao entregar

Diga em uma linha quais lições foram gravadas ("Guardei 3 aprendizados: música mais baixa, bastidor nas pontas, botão do tamanho da legenda") e se algum padrão de código mudou.

## Compartilhar com o dono da skill

`python scripts/aprender.py exportar` imprime a base inteira. O usuário pode mandar esse texto para o dono da skill, que incorpora as lições no treinamento oficial (e aí elas chegam em todas as máquinas na próxima atualização).
