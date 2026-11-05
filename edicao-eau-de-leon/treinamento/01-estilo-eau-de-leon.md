# 01 — O estilo de edição da Eau de Leon

Estudo feito quadro a quadro, com recorte em resolução nativa, nos reels da **@eau.de.leon** (05/11/2026). Entre os analisados: Quiz (83,7 mil views), "Até 30% de desconto no site todo", "Vem ver como funciona" (decant), tour da sede, reels da criadora ("perfumes óbvios", "+/- / Bom / Melhor"), "Dia X Noite", "POV: …". As fontes foram identificadas letra a letra comparando lado a lado com as candidatas. **Não troque nenhuma fonte.** Todas estão em `assets/fontes` (licença OFL).

## A personalidade da edição

**Limpa, rápida e legível.** A pessoa fala direto pra câmera e os cortes tiram todo respiro. A legenda é branca, discreta e fica no peito. Os elementos grandes (texto de impacto, perfumes) só aparecem no instante em que a fala pede. A única voz do vídeo é a de quem gravou as takes: **nunca** se põe narração, locução ou voz gerada.

## Os elementos (fonte, cor e onde ficam)

| Elemento | Fonte | Aparência | Exemplo do perfil |
|---|---|---|---|
| Legenda | **Poppins Bold** | branca, minúscula como se fala, sombra preta suave deslocada pra baixo e pra direita (sem contorno), 1 linha | "já começou", "DE QUAL ESCOLHER?" |
| Destaque de palavra-chave | Poppins Bold, 1,45× | CAIXA ALTA, **amarela**, linha própria logo abaixo da frase, pop | "clica em **SAIBA MAIS**", "simplesmente **IMPERDÍVEL**" |
| Texto de impacto | **Bebas Neue** engrossada (o negrito do CapCut) | branca, CAIXA ALTA, sombra suave; a 1ª linha é digitada letra a letra e as de baixo vêm menores | "30% DE DESCONTO / EM TODOS OS PERFUMES" |
| Destaque | **Bungee** | branca, CAIXA ALTA, sombra mais escura, entra com pop; linhas quase encostando | "QUIZ 100% / GRATUITO / E PERSONALIZADO" |
| Rótulo / POV | **TikTok Sans SemiBold** (texto nativo do TikTok/Instagram) | branca, contorno preto fino, frase normal (não caixa alta) + emoji colorido | "POV: Você encontrou o perfume perfeito para balada!", "Bom 🤗", "Dia ☀️ X Noite 🌙" |
| Perfumes | foto sem fundo | **sem sombra**, "chapada" no vídeo, em fileira | criadora listando perfumes |
| Divisória | linha branca vertical fina no meio | só nas comparações "isso X aquilo" | "Dia X Noite" |
| Cartão final | logo Eau de Leon branco no preto | dissolve 0,45 s e fica ~2 s | fim dos reels do Leo |

Os emojis saem no desenho do Google (Noto). Os do perfil são os da Apple, que não podem ser distribuídos; o formato e o tamanho são os mesmos.

## Onde as coisas ficam no quadro (1080×1920)

- **Legenda: abaixo do pescoço, na altura do peito** de quem fala. O render acha o rosto sozinho (`enquadramento.py`) e põe o centro da legenda ~0,6 rosto abaixo do queixo. Num plano médio isso dá y ≈ 1080–1160. A altura é a mesma no vídeo todo.
- **Texto de impacto e destaque:** no mesmo lugar da legenda (a legenda some enquanto eles estão na tela).
- **Fileira de perfumes:** logo abaixo da legenda, centralizada, até 4 frascos.
- **Rótulos/POV:** no topo (y ≈ 12–15%), ou onde o formato pedir (ex.: tier list à esquerda).
- **Logo no cartão final:** 560 px de largura, centro em y = 768.

## Os 3 formatos do perfil

### `leo`: apresentador falando (fundador, time)
Plano médio, olhando pra câmera, estante de perfumes ou escritório atrás.
- Legenda em frases de 2 a 4 palavras.
- **Destaque** (Bungee) ou **impacto** (Bebas) no gancho e na oferta.
- **Cortes secos** nas respirações, alternando o enquadramento (zoom 1,00 ↔ 1,12) a cada corte.
- **Whip** (borrão horizontal de ~0,1 s) quando muda o assunto ou o ambiente.
- **B-roll** do produto, do site ou da embalagem, com a legenda continuando por cima.
- Fim: **cartão final** com o logo.

### `creator`: criadora falando de perfumes
Sentada na frente da estante, uma take quase contínua.
- Legenda **palavra por palavra**.
- **Perfumes citados** entrando em fileira na hora em que são falados.
- Às vezes um **rótulo** fixo no topo ("+/- 🫠 / Bom 🤗 / Melhor! 🤌").
- Sem cartão final.

### Formatos sem fala (produto na mão)
"POV: …" no topo e frase no rodapé com emoji, "Dia ☀️ X Noite 🌙" com a divisória, "Esse é bom mas.. / Esse é melhor!". Tudo com **rótulo** (TikTok Sans) e sem legenda de fala.

## O que NÃO é o estilo

- Fonte inventada ou "parecida": use só as 5 da tabela.
- Legenda inteira amarela ou colorida, caixa atrás do texto, contorno grosso. A cor vai **só** na palavra-chave destacada (2 a 4 por vídeo).
- Legenda no queixo ou na barriga: é **no peito**.
- Sombra em perfume, moldura, sticker animado, seta desenhada.
- Zoom lento contínuo (Ken Burns) na pessoa falando.
- Transição em todo corte (corte seco é o padrão).
- Narração, locução ou qualquer voz que não seja a das takes.
- Sem música, ou música alta competindo com a voz. O padrão é trilha suave, baixa e diferente a cada vídeo.
- Vinheta de abertura.
