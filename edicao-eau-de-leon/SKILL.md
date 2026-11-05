---
name: edicao-eau-de-leon
description: Edita vídeos (Reels/TikTok 9:16) no padrão visual da Eau de Leon a partir das takes brutas na ordem certa — corta erros e respirações, põe legenda padrão com destaque nas palavras-chave, textos de impacto, música suave de fundo (sempre diferente), fotos sem fundo dos perfumes citados, b-roll, transições (whip, fade, slide, drop, pop) e o cartão final com o logo. Use quando pedirem "edita esse vídeo", "edição Eau de Leon", "monta o reels com essas takes", "editar no estilo da Eau de Leon", "/edicao-eau-de-leon", ou quando receber arquivos de vídeo (.mp4/.mov) de gravação para virar post. Roda tudo local e grátis (ffmpeg + Whisper local), sem API paga.
---

# Edição de vídeo no padrão Eau de Leon

Você recebe **as takes na ordem certa** e entrega **um MP4 1080×1920 pronto pra postar**, idêntico em estilo aos reels da @eau.de.leon. Você é o editor: decide cortes, legenda, textos e perfumes; os scripts só executam.

## Passo 0 — preparar a máquina (automático, sempre antes de editar)

A skill precisa de programas que não vêm no Windows/Mac: **Python**, **ffmpeg** (corta e monta o vídeo), bibliotecas Python e o modelo de transcrição. **Você instala tudo sozinho**, sem pedir nada ao usuário:

1. Se existir `<skill>/scripts/python.txt`, rode `"<conteúdo do python.txt>" <skill>/scripts/verificar.py`. Se terminar em **"Tudo pronto."**, pule pro fluxo.
2. Senão (ou se algo deu FALTA), rode o preparador e espere terminar (a 1ª vez leva alguns minutos e baixa ~1 GB):
   - Windows: `powershell -ExecutionPolicy Bypass -File "<skill>\scripts\preparar.ps1"`
   - Mac/Linux: `bash "<skill>/scripts/preparar.sh"`
3. Ele termina com `PYTHON=<caminho>`. **Use esse caminho no lugar de `python`** em todos os comandos abaixo (também fica salvo em `scripts/python.txt`). Não use o `python` solto: no Windows ele pode ser o atalho falso da Microsoft Store.
4. Se o preparador falhar, leia a mensagem: normalmente basta rodar de novo (o Windows às vezes só enxerga o programa recém-instalado na 2ª vez). Se pedir algo que só a pessoa pode fazer (senha de administrador, instalar o "Instalador de Aplicativo" da Microsoft Store), diga exatamente o que fazer em uma frase.

`<skill>` = a pasta desta skill (onde está este SKILL.md), normalmente `~/.claude/skills/edicao-eau-de-leon`.

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
Gera `transcricao.txt` (frases com tempo de cada palavra), `transcricao.json`, `perfumes_citados.txt` e `destaques_sugeridos.txt` (palavras-chave candidatas a destaque).
Se o áudio tiver muito ruído ou nome errado demais, rode de novo com `--modelo medium`.

**3. Entenda o vídeo.** Leia `transcricao.txt` inteiro e `perfumes_citados.txt`. Responda pra você mesmo:
- Qual o formato? (`leo` = apresentador falando com legenda em frase / `creator` = criadora falando de perfumes com legenda palavra a palavra). Ver treinamento/01.
- Qual o gancho (primeira frase forte)? Qual a oferta/CTA no fim?
- Quais falas são erro, repetição, "corta", "de novo", gaguejo → **saem**.
- Quais perfumes são citados → **entram na tela** no instante exato da fala. Confirme cada id com `python <skill>/scripts/catalogo.py buscar "nome"`.
- Quais são as **palavras-chave** (o que vende: "SAIBA MAIS", "IMPERDÍVEL", "TODOS OS PERFUMES", "FRETE GRÁTIS", o número do desconto) → viram **destaque** na legenda. Comece pelo `destaques_sugeridos.txt` e escolha 2 a 4 por vídeo (ver treinamento/03).

**4. Escreva o plano** em `<trabalho>/plano.json` seguindo `treinamento/07-plano-json.md`. Tempos sempre na **take original** (take N + segundo), copiados do `transcricao.txt`.

**5. Rascunho e conferência:**
```
python <skill>/scripts/render.py <trabalho>/plano.json --rapido
python <skill>/scripts/conferir.py <trabalho>/editado.mp4
```
Abra **cada** `conferir/conferir_XX.png` com a ferramenta Read e passe o `treinamento/08-checklist-qualidade.md` item por item. Errou algo → corrija o plano e renderize de novo. Não entregue sem olhar os quadros.

**6. Render final** (sem `--rapido`) e entregue: caminho do MP4, duração, o que foi cortado (em linguagem simples), perfumes e destaques que entraram, a música usada, e `legenda.srt` (pra colar como legenda do post se quiserem).

## Regras que não mudam

- **A única voz do vídeo é a das takes.** Nunca gere, adicione ou troque voz (nada de TTS, locução ou narração).
- **Nunca** chame API paga (OpenAI, ElevenLabs, etc.). Transcrição é o Whisper local do `transcrever.py`.
- **Fontes só as do perfil** (Poppins, Bebas Neue, Bungee, TikTok Sans). Nunca invente ou troque fonte.
- **Nunca** invente fala nem mude o sentido do que a pessoa disse. Correção de legenda é só grafia (nome de perfume, marca, "Eau de Leon").
- Perfume na tela **só** se ele foi falado (ou o usuário pediu) e **só** com a foto do catálogo `assets/perfumes` — nunca baixe imagem da internet, nunca use foto com fundo.
- Perfume que não está no catálogo: não invente; avise no fim ("o X foi citado mas não tem foto no catálogo") e siga sem ele.
- Saída sempre 1080×1920, 30 fps, H.264 + AAC, voz em -14 LUFS, **com música suave de fundo** (padrão; só tire se o usuário pedir).
- Se faltar algo que só o usuário sabe (ex.: qual take é a boa quando as duas estão perfeitas e dizem coisas diferentes), pergunte **uma vez**, objetivo. O resto, decida pelo treinamento.
