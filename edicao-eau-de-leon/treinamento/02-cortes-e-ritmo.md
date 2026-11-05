# 02 — Cortes, ritmo, enquadramento e transições

## A ordem das takes

O usuário manda as takes **na ordem certa** do vídeo. Isso quer dizer:
- A take 1 contém o começo, a última take contém o fim. Respeite essa ordem no plano.
- Dentro de uma take pode haver **erro + repetição** ("…presta atenção. Corta, vou de novo. Se você ama perfume…"). Fique com a **última tentativa boa** de cada fala e descarte as anteriores.
- Se duas takes repetem a mesma fala (a pessoa regravou a frase inteira na take seguinte), use a melhor (normalmente a mais recente e mais fluida) e **não repita a informação**.

## O que sai (sempre)

1. Silêncio antes da primeira palavra e depois da última.
2. Falas de bastidor: "corta", "de novo", "vou repetir", "peraí", "tá gravando?", "errei", risada de erro, contagem "3, 2, 1".
3. Frase que começou e foi abandonada no meio.
4. Gaguejo e palavra repetida por erro ("o o perfume", "que que eu").
5. Muletas longas no começo da frase ("é…", "então assim…", "tipo…") quando dá pra começar o trecho depois delas sem cortar palavra.
6. Respirações e pausas > 0,28 s **dentro** dos trechos — isso o render faz sozinho medindo o áudio; você não precisa picotar à mão.

## O que fica

- Toda informação dita de forma completa, na ordem do roteiro.
- O gancho inteiro (primeira frase) — ele é o motivo de a pessoa parar de rolar o feed.
- O CTA inteiro no fim ("clica em saiba mais", "link na bio", "me chama no direct").
- Sorriso/gesto final curto (até ~0,6 s) no formato `creator`.

## Como escolher os limites de um trecho

Use os tempos por palavra do `transcricao.txt` (o número entre parênteses é o **início** da palavra):
- `ini` do trecho = início da primeira palavra **− 0,10 s**.
- `fim` do trecho = início da última palavra + a duração dela (veja o início da palavra seguinte) **+ 0,15 s**. Na dúvida, prefira sobrar 0,2 s a cortar a sílaba final — o render apara o silêncio sobrando.
- Um trecho = uma fala inteira (uma ou mais frases seguidas). Não picote dentro da frase; o render já tira as respirações.
- Trechos de takes diferentes podem se alternar livremente, mas a ordem final é a ordem da lista `trechos`.

## Ritmo

- Meta: **zero respiro**. Entre uma frase e outra só fica a folga de 0,07 s que o render deixa.
- Vídeo `leo`: alvo 15–45 s. Se o bruto passa de 60 s de fala útil, mantenha tudo que é informação — não resuma a fala da pessoa — mas corte toda repetição.
- Vídeo `creator`: normalmente uma take quase inteira, só limpando começo, fim e erros.

## Enquadramento (o "zoom no corte")

- A cada corte seco **dentro** de uma mesma fala, o enquadramento alterna entre **1,00** (normal) e **1,12** (mais perto). É o que esconde o "pulo" do jump cut. O render faz isso sozinho.
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

Se a pessoa faz uma pausa de propósito (suspense antes do preço, gesto mostrando o frasco), marque o trecho com `"manter_pausas": true`. Sem isso, o render tira toda pausa > 0,28 s.
