# 01 — O estilo de edição da Eau de Leon

Estudo feito quadro a quadro nos reels de **@eau.de.leon** (perfil com ~136 mil seguidores, decants de perfumes importados) em 05/11/2026. Foram analisados, entre outros: o reel do Quiz (83,7 mil views), "Até 30% de desconto no site todo", "Vem ver como funciona" (bastidor do decant), "Tour na nova sede", e os reels da criadora falando de perfumes ("+/- / Bom / Melhor", "perfumes óbvios x perfumes que…"). Todas as medidas abaixo estão em px de um quadro **1080×1920** (o render usa exatamente esses números — `ESTILO` em `scripts/render.py`).

## A personalidade da edição em uma frase

**Limpa, rápida e legível**: a pessoa fala direto pra câmera, os cortes tiram todo respiro, a legenda é pequena e discreta no meio da tela, e os elementos "grandes" (texto de impacto, fotos de perfume) aparecem só no instante exato em que a fala pede. Nada de emoji animado, nada de moldura, nada de efeito sonoro de "whoosh" em todo corte, nada de cores além do branco. A identidade está no **ritmo** e na **precisão**, não em enfeite.

## Os 3 formatos que existem no perfil

### Formato `leo` — apresentador falando (fundador, time)
Plano médio, pessoa sentada ou em pé, olhando pra câmera, estante de perfumes ou escritório atrás. Ex.: Quiz, "Até 30% de desconto", tour da sede, "como funciona o decant".
- **Legenda:** frases curtas de 2 a 4 palavras, uma de cada vez (ver 03).
- **Texto de impacto** no gancho e na oferta (ver 04): "ATÉ 30% DE DESCONTO / NO SITE TODO", "QUIZ 100% GRATUITO / E PERSONALIZADO".
- **Cortes secos** nas respirações com troca de enquadramento (zoom 1,00 ↔ 1,12) a cada corte.
- **Whip** (borrão horizontal rápido) quando muda de assunto/ambiente.
- **B-roll** do produto, da tela do site, da embalagem — a legenda continua por cima.
- **Fim:** dissolve de 0,45 s para o **cartão final**: fundo preto, logo Eau de Leon branco no centro, ~2 s.
- Duração típica 15–55 s.

### Formato `creator` — criadora falando de perfumes
Uma moça sentada na frente da estante de perfumes, plano médio fixo, normalmente **uma take contínua** com poucos cortes. Ex.: "perfumes óbvios", "+/- / Bom / Melhor".
- **Legenda palavra por palavra** (uma palavra de cada vez, mesma fonte da legenda padrão).
- **Fotos sem fundo dos perfumes citados** numa fileira no terço de baixo (até 4 lado a lado), cada uma entrando no instante em que o nome é falado; quando ela muda de grupo de perfumes, a fileira inteira troca (ver 05).
- Sem texto de impacto na maioria; quando tem, é um rótulo fixo.
- **Sem cartão final** (termina no sorriso/última fala).
- Duração típica 15–30 s.

### Formatos sem fala (referência — fora do foco desta skill)
"Dia ☀️ X Noite 🌙" com linha vertical no meio, "Esse é bom mas.. / Esse é melhor!", "POV: …" com frase fixa no topo e mãos mostrando o frasco. São produções de b-roll com **rótulos fixos** (Poppins, branco, pequenos, no topo). A skill suporta rótulos fixos (`estilo: "rotulo"`) e perfumes em posição livre (`x`,`y`) caso peçam.

**Como escolher o formato:** se quem fala é o Leo/time e há oferta, CTA ou explicação → `leo`. Se é criadora apresentando/listando perfumes → `creator`. Na dúvida, `leo`.

## Medidas (1080×1920)

| Elemento | Medida observada | No render |
|---|---|---|
| Centro vertical da legenda | 40–45% da altura | y = 830 |
| Largura de uma legenda de ~24 caracteres | ~58% da largura | Poppins Bold 50 |
| Texto de impacto, 1ª linha | topo em ~40% da altura, ~72% da largura | Oswald Bold 92, topo y = 778 |
| Destaque arredondado ("QUIZ 100%") | mesmo centro, letras gordas | Titan One 96 |
| Perfumes na fileira | altura ~15% do quadro, base em ~70% | altura 300 px, base y = 1350 |
| Fileira | até 4 frascos, ~87% da largura | 940 px de largura útil |
| Logo no cartão final | ~50% da largura, centro em ~40% | 560 px, centro y = 768 |
| Cartão final | ~2 s, entra com dissolve | 2,0 s, dissolve 0,45 s |

## Cores e tipografia

- Texto **sempre branco** (#FFFFFF) com halo/sombra escura suave (preto ~55% de opacidade, desfocado). Nunca caixa colorida atrás, nunca contorno grosso colorido, nunca amarelo/verde "karaokê".
- **Poppins Bold** → legenda e rótulos. **Oswald Bold** (condensada) → texto de impacto. **Titan One** + **Poppins ExtraBold** → destaque de promessa/oferta. Todas em `assets/fontes` (licença OFL, livres).
- Cores da marca (rosa #F4A99B e azul #6BB3E0 do "E") só aparecem no logo. Não pinte texto com elas.

## O que NÃO é o estilo (erros comuns de editor)

- Legenda gigante amarela com palavra destacada em cor → **não**.
- Emoji animado, stickers, setas desenhadas, "SUBSCRIBE" → **não**.
- Zoom lento contínuo (Ken Burns) na pessoa falando → **não**; o zoom é seco, no corte.
- Transição em todo corte → **não**; corte seco é o padrão, whip só em troca de cena.
- Música alta competindo com a voz → **não**; voz sempre em primeiro plano.
- Vinheta de abertura → **não**; o vídeo começa já na fala do gancho.
