---
name: edicao-eau-de-leon
description: Edita vídeos (Reels/TikTok 9:16) no padrão visual da Eau de Leon a partir das takes brutas na ordem certa — corta erros e respirações, põe legenda padrão, textos de impacto, fotos sem fundo dos perfumes citados, b-roll, transições (whip, fade, slide, drop, pop) e o cartão final com o logo. Use quando pedirem "edita esse vídeo", "edição Eau de Leon", "monta o reels com essas takes", "editar no estilo da Eau de Leon", "/edicao-eau-de-leon", ou quando receber arquivos de vídeo (.mp4/.mov) de gravação para virar post. Roda tudo local e grátis (ffmpeg + Whisper local), sem API paga.
---

# Edição de vídeo no padrão Eau de Leon

Você recebe **as takes na ordem certa** e entrega **um MP4 1080×1920 pronto pra postar**, idêntico em estilo aos reels da @eau.de.leon. Você é o editor: decide cortes, legenda, textos e perfumes; os scripts só executam.

> Antes da 1ª edição na máquina, rode `scripts/instalar.ps1` (Windows) ou `scripts/instalar.sh` (Mac/Linux). Ver `README.md`.

## Leia primeiro (obrigatório, nesta ordem)

1. `treinamento/01-estilo-eau-de-leon.md` — o que é o estilo, os 3 formatos e as medidas
2. `treinamento/02-cortes-e-ritmo.md` — o que cortar, ritmo, enquadramento, transições
3. `treinamento/03-legendas.md` — legenda padrão (fonte, tamanho, posição, quebra, caixa)
4. `treinamento/04-textos-de-impacto.md` — quando e como pôr texto grande na tela
5. `treinamento/05-perfumes-na-tela.md` — fotos sem fundo dos perfumes citados
6. `treinamento/06-broll-cartao-final-audio.md` — b-roll, cartão final, música, volume
7. `treinamento/07-plano-json.md` — o formato exato do plano que o render lê
8. `treinamento/08-checklist-qualidade.md` — a conferência antes de entregar
9. `treinamento/09-exemplo-completo.md` — uma edição inteira, do bruto ao plano

## Fluxo (siga sem pular etapas)

**1. Organize.** Crie uma pasta de trabalho ao lado das takes: `<pasta das takes>/edicao/`. Anote a ordem das takes como o usuário passou (take 1, 2, 3…). Se ele mandou b-roll (prints, vídeos do produto), anote também.

**2. Transcreva** (local, grátis):
```
python <skill>/scripts/transcrever.py <trabalho> take1.mp4 take2.mp4 ...
```
Gera `transcricao.txt` (frases com tempo de cada palavra), `transcricao.json` e `perfumes_citados.txt`.
Se o áudio tiver muito ruído ou nome errado demais, rode de novo com `--modelo medium`.

**3. Entenda o vídeo.** Leia `transcricao.txt` inteiro e `perfumes_citados.txt`. Responda pra você mesmo:
- Qual o formato? (`leo` = apresentador falando com legenda em frase / `creator` = criadora falando de perfumes com legenda palavra a palavra). Ver treinamento/01.
- Qual o gancho (primeira frase forte)? Qual a oferta/CTA no fim?
- Quais falas são erro, repetição, "corta", "de novo", gaguejo → **saem**.
- Quais perfumes são citados → **entram na tela** no instante exato da fala. Confirme cada id com `python <skill>/scripts/catalogo.py buscar "nome"`.

**4. Escreva o plano** em `<trabalho>/plano.json` seguindo `treinamento/07-plano-json.md`. Tempos sempre na **take original** (take N + segundo), copiados do `transcricao.txt`.

**5. Rascunho e conferência:**
```
python <skill>/scripts/render.py <trabalho>/plano.json --rapido
python <skill>/scripts/conferir.py <trabalho>/editado.mp4
```
Abra **cada** `conferir/conferir_XX.png` com a ferramenta Read e passe o `treinamento/08-checklist-qualidade.md` item por item. Errou algo → corrija o plano e renderize de novo. Não entregue sem olhar os quadros.

**6. Render final** (sem `--rapido`) e entregue: caminho do MP4, duração, o que foi cortado (em linguagem simples), perfumes que entraram, e `legenda.srt` (pra colar como legenda do post se quiserem).

## Regras que não mudam

- **Nunca** chame API paga (OpenAI, ElevenLabs, etc.). Transcrição é o Whisper local do `transcrever.py`.
- **Nunca** invente fala nem mude o sentido do que a pessoa disse. Correção de legenda é só grafia (nome de perfume, marca, "Eau de Leon").
- Perfume na tela **só** se ele foi falado (ou o usuário pediu) e **só** com a foto do catálogo `assets/perfumes` — nunca baixe imagem da internet, nunca use foto com fundo.
- Perfume que não está no catálogo: não invente; avise no fim ("o X foi citado mas não tem foto no catálogo") e siga sem ele.
- Saída sempre 1080×1920, 30 fps, H.264 + AAC, voz em -14 LUFS.
- Se faltar algo que só o usuário sabe (ex.: qual take é a boa quando as duas estão perfeitas e dizem coisas diferentes), pergunte **uma vez**, objetivo. O resto, decida pelo treinamento.
