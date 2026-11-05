# Skill de edição — padrão Eau de Leon (Claude Code)

Skill para o **Claude Code** editar Reels/TikTok no estilo da [@eau.de.leon](https://www.instagram.com/eau.de.leon/): você passa as takes na ordem, ele entrega o MP4 1080×1920 pronto — cortes sem respiro, legenda padrão, textos de impacto, **fotos sem fundo dos perfumes citados** entrando na hora da fala, b-roll, whip/fade/slide/drop/pop e o cartão final com o logo.

Tudo roda **local e grátis** (ffmpeg + Whisper local). Nenhuma API paga.

## O que vem no repositório

```
edicao-eau-de-leon/            ← a skill (é essa pasta que vai pro Claude)
  SKILL.md                     ← o que o Claude lê primeiro (fluxo)
  treinamento/                 ← o treinamento completo do estilo (01 a 09)
  scripts/                     ← transcrever, render, conferir, catálogo, remover fundo
  assets/perfumes/             ← 445 fotos de perfume SEM FUNDO (PNG transparente) + perfumes.json
  assets/fontes/               ← as fontes do perfil: Poppins, Bebas Neue, Bungee, TikTok Sans + emoji Noto (OFL)
  assets/logo/                 ← logo Eau de Leon branco (transparente) do cartão final
  assets/musicas/              ← (vazia) coloque aqui trilhas licenciadas, se quiser
instalar-skill.ps1             ← instala a skill no Claude Code (Windows)
instalar-skill.sh              ← idem (Mac/Linux)
```

## Instalação (uma vez)

**Windows (PowerShell):**
```powershell
git clone https://github.com/cainaoteiza78-prog/skill-edicao-eau-de-leon.git
cd skill-edicao-eau-de-leon
powershell -ExecutionPolicy Bypass -File .\instalar-skill.ps1
```

**Mac/Linux:**
```bash
git clone https://github.com/cainaoteiza78-prog/skill-edicao-eau-de-leon.git
cd skill-edicao-eau-de-leon && bash instalar-skill.sh
```

O instalador copia a skill para `~/.claude/skills/edicao-eau-de-leon`, instala ffmpeg/Python se faltarem, as bibliotecas (`requirements.txt`), baixa o modelo de transcrição e roda um teste (`scripts/verificar.py`). No fim tem que aparecer **"Tudo pronto."**

Para atualizar depois: `git pull` e rode o instalador de novo.

## Como usar

Abra o Claude Code na pasta onde estão os vídeos e peça, por exemplo:

> Edita no padrão Eau de Leon: take1.mp4, take2.mp4, take3.mp4 (nessa ordem). Tem também o print-site.png pra usar quando eu falar do site.

Ou chame direto: `/edicao-eau-de-leon take1.mp4 take2.mp4`.

O Claude vai: transcrever → decidir cortes, legenda, textos e perfumes → renderizar um rascunho → conferir os quadros → renderizar o final. Sai `edicao/editado.mp4` + `edicao/legenda.srt`.

## Requisitos

- Claude Code
- Windows 10/11, macOS ou Linux, 8 GB de RAM
- ~3 GB livres (ffmpeg, Python, modelo de transcrição)
- ffmpeg **com libass** (o instalador baixa a build certa no Windows)

## Cadastrar perfume novo

```
python edicao-eau-de-leon/scripts/remover_fundo.py foto-do-perfume.jpg edicao-eau-de-leon/assets/perfumes/masculinos
python edicao-eau-de-leon/scripts/catalogo.py gerar
```
A foto sai com transparência real (sem fundo branco/xadrez falso).
