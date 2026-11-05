# 02 — Cortes, ritmo, enquadramento e transições

## A ordem das takes

O usuário manda as takes **na ordem certa** do vídeo. Isso quer dizer:
- A take 1 contém o começo, a última take contém o fim. Respeite essa ordem no plano.
- Dentro de uma take pode haver **erro + repetição** ("…presta atenção. Corta, vou de novo. Se você ama perfume…"). Fique com a **última tentativa boa** de cada fala e descarte as anteriores.
- Se duas takes repetem a mesma fala (a pessoa regravou a frase inteira na take seguinte), use a melhor (normalmente a mais recente e mais fluida) e **não repita a informação**.

## O que sai (sempre)

O render tira sozinho (`scripts/cortes.py`):
- **respirações, pausas e estalos ENTRE palavras.** Regra de ouro: **o corte nunca cai dentro de uma palavra.** O tempo de cada palavra é protegido; dele só sai silêncio de verdade (no nível do ruído da sala, por mais de 0,16 s). O "t" de "todos" (um silêncio de ~80 ms dentro da palavra) fica. As bordas ainda crescem pra pegar consoante que o Whisper deixou de fora, e uma trava final garante que a parte com som de cada palavra cabe inteira num pedaço. Na conferência, não pode sobrar pausa maior que ~0,15 s;
- **falas de bastidor isoladas**: "corta", "vai", "parou", "pera", "de novo", "vou de novo", "repete", "errei", "valendo", "ok", "bora", "mais uma vez", "3, 2, 1"… Saem quando estão soltas (com pausa antes ou depois, ou na ponta da take). "Isso **vai** ficar lindo" fica, porque faz parte da frase. O render lista no terminal o que removeu (`fala de bastidor removida: …`).

Você decide e tira pelo plano:
1. A **tentativa errada** inteira quando a pessoa repete a frase: fique com a última tentativa boa.
2. Frase começada e abandonada no meio.
3. Gaguejo ou palavra repetida por erro ("o o perfume").
4. Muleta longa no começo ("então assim…"), quando dá pra começar o trecho depois dela sem cortar palavra.
5. Bastidor que não está isolado ("corta isso aí que eu errei o nome"): o filtro automático não pega, então tire pelo plano.

## O que fica

- Toda informação dita de forma completa, na ordem do roteiro.
- O gancho inteiro (primeira frase) — ele é o motivo de a pessoa parar de rolar o feed.
- O CTA inteiro no fim ("clica em saiba mais", "link na bio", "me chama no direct").
- Sorriso/gesto final curto (até ~0,6 s) no formato `creator`.

## Como escolher os limites de um trecho

Use os tempos por palavra do `transcricao.txt` (o número entre parênteses é o **início** da palavra):
- `ini` do trecho = início da primeira palavra **− 0,10 s**.
- `fim` do trecho = início da última palavra + a duração dela (veja o início da palavra seguinte) **+ 0,15 s**. Na dúvida, prefira sobrar 0,2 s a cortar a sílaba final — o render apara o silêncio sobrando.
- Um trecho = uma fala inteira (uma ou mais frases seguidas). Não picote dentro da frase; o render já tira as respirações e as pausas.
- Os cortes do render seguem a VOZ, então o vídeo pula junto com a fala. Se a imagem de um pedaço estiver ruim (pessoa saindo do quadro, mão na frente da câmera), tire o trecho pelo plano.
- Trechos de takes diferentes podem se alternar livremente, mas a ordem final é a ordem da lista `trechos`.

## Ritmo

- Meta: **zero respiro**. Entre uma frase e outra só fica a folga de ~0,08 s que o render deixa.
- Vídeo `leo`: alvo 15–45 s. Se o bruto passa de 60 s de fala útil, mantenha tudo que é informação — não resuma a fala da pessoa — mas corte toda repetição.
- Vídeo `creator`: normalmente uma take quase inteira, só limpando começo, fim e erros.

## Enquadramento (o "zoom no corte")

- A cada corte seco **dentro** de uma mesma fala, o enquadramento alterna entre **1,00** (normal) e **1,12** (mais perto). É o que esconde o "pulo" do jump cut. O render faz isso sozinho.
- **Todo zoom (punch e ênfase) é centralizado no ROSTO** da pessoa (detectado em cada pedaço), nunca no centro da tela: o rosto é acompanhado a cada 0,25 s e o enquadramento o segue suavemente (e, se a pessoa está fora do meio, a câmera aproxima o mínimo necessário pra centralizar). A pessoa não pode "escorregar" pro lado. O `revisar.py` mede isso.
- Ênfase forte (a frase do preço, "olha isso"): pode forçar `"zoom": 1.25` naquele trecho.
- Gravação horizontal ou pessoa fora do centro: use `"foco_x"` (0 = esquerda, 0,5 = centro, 1 = direita) pra não cortar o rosto no 9:16.

## Transições (campo `transicao` do trecho — vale pro começo dele)

| Valor | Quando usar | Como fica |
|---|---|---|
| `corte` (padrão) | quase sempre | corte seco + troca de enquadramento |
| `whip` | troca de **cena/assunto/ambiente**: do gancho pra explicação, de uma sala pra outra, da pessoa pro produto | borrão horizontal de 0,10 s na saída e na entrada (o "chicote" que aparece no reel do Quiz aos 3,2 s) |
| `fade` | só depois de pausa dramática ou passagem de tempo | entra do preto em 0,25 s |
| `flash` | raríssimo, revelação ("e o preço é…") | entra do branco em 0,18 s |

Regra: **no máximo 1 whip a cada ~6 s**. Um vídeo de 30 s tem tipicamente 2 a 4 whips; o resto é corte seco.

## Pausas que devem ficar

Se a pessoa faz uma pausa de propósito (suspense antes do preço, gesto mostrando o frasco), marque o trecho com `"manter_pausas": true`. Sem isso, o render tira toda pausa. A pausa de propósito é rara: na dúvida, corte.
