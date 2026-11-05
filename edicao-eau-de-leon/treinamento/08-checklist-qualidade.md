# 08 — Checklist antes de entregar

Rode `python scripts/conferir.py <trabalho>/editado.mp4`, abra **todas** as folhas `conferir/conferir_XX.png` com a ferramenta Read e marque cada item. Item reprovado → ajuste o plano → render de novo → confira de novo.

## Corte e ritmo
- [ ] O vídeo começa **na primeira palavra do gancho** (sem silêncio, sem "oi gente" se não fizer parte do gancho).
- [ ] Nenhuma fala de bastidor ("corta", "de novo", "errei") — leia o `legenda.srt` inteiro procurando.
- [ ] Nenhuma frase repetida (mesma informação duas vezes).
- [ ] Nenhuma palavra cortada no meio (ouça o fim de cada trecho: se o `legenda.srt` mostra a palavra mas ela parece engolida, aumente `fim` em 0,15 s).
- [ ] O CTA final está inteiro.
- [ ] Whips só em troca de assunto/cena, no máximo 1 a cada ~6 s.

## Legenda
- [ ] Mesma posição (altura do peito/queixo) o vídeo todo, uma linha, branca, sem caixa.
- [ ] Nomes certos: Eau de Leon, decant, nomes de perfume com a grafia oficial.
- [ ] Sem ponto/vírgula; ? e ! preservados; começo de frase minúsculo; marcas com maiúscula.
- [ ] Modo certo: `frase` (leo) ou `palavra` (creator).
- [ ] Legenda não aparece junto com texto de impacto.

## Textos de impacto
- [ ] No máximo 3 em 30 s; o do gancho aparece nos primeiros 3 s (formato leo com promessa clara).
- [ ] Curtos (≤ 20 caracteres por linha), CAIXA ALTA, dizem o que a pessoa fala.
- [ ] Não cobrem o rosto (ficam na altura do peito; se a pessoa está muito baixa no quadro, use `foco_y` maior no trecho pra subir o enquadramento).

## Perfumes
- [ ] Cada perfume aparece **no momento em que é falado** (não antes).
- [ ] É o perfume certo (confira o rótulo do frasco na folha de conferência contra o nome falado).
- [ ] Sem fundo nenhum em volta do frasco (nem branco, nem cinza, nem quadrado).
- [ ] Fileira centralizada, não corta frasco na borda, não fica em cima do texto de impacto.
- [ ] Grupo some quando o assunto muda.

## Cartão final e áudio
- [ ] Formato leo: dissolve para o fundo preto com logo Eau de Leon centralizado, ~2 s. Creator: sem cartão.
- [ ] Voz clara, sem estalo nos cortes, volume constante.
- [ ] Música (se houver) não compete com a voz.

## Técnico
- [ ] `ffprobe` mostra 1080×1920, 30 fps, h264 + aac.
- [ ] Duração coerente com a fala útil (sem buracos pretos, sem quadro congelado fora do cartão).

Ao entregar, diga: arquivo final, duração, o que foi cortado (frases, em linguagem simples), perfumes que entraram (e os citados que não têm foto), e onde está o `legenda.srt`.
