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
  assets/logo/                 ← logo Eau de Leon branco (transparente) da marca d'água
  assets/musicas/              ← (vazia) coloque aqui trilhas licenciadas, se quiser
instalar-skill.ps1             ← instala a skill no Claude Code (Windows)
instalar-skill.sh              ← idem (Mac/Linux)
```

## Instalação (uma vez) — o Claude faz tudo

Pré-requisitos: ter o **Claude Code** instalado e acesso a este repositório (o dono adiciona seu usuário do GitHub como colaborador).

Abra o Claude Code em qualquer pasta e cole:

> Instala a skill de edição da Eau de Leon: clona https://github.com/cainaoteiza78-prog/skill-edicao-eau-de-leon.git numa pasta temporária, roda o `instalar-skill.ps1` (Windows) ou `instalar-skill.sh` (Mac/Linux) que está nele e só me avisa quando aparecer "PRONTO".

O Claude copia a skill para `~/.claude/skills/edicao-eau-de-leon` e roda o **preparador** (`scripts/preparar.ps1` / `preparar.sh`). O preparador instala sozinho o que a edição precisa e que não vem no computador:

| Programa | Pra quê | Como é instalado |
|---|---|---|
| Python 3.12 | roda os scripts da skill | winget (Windows) / Homebrew (Mac) / apt (Linux) |
| ffmpeg (versão completa) | corta, junta, põe legenda e exporta o vídeo | idem |
| Runtime do Visual C++ (só Windows) | exigido pela transcrição | winget |
| Bibliotecas Python (`requirements.txt`) | transcrição, detecção de rosto, imagens | pip |
| Modelo de transcrição Whisper "small" (~500 MB) | entende a fala, no próprio PC e grátis | baixado uma vez |

Na 1ª vez leva alguns minutos e baixa ~1 GB. Tudo é grátis e roda no computador, sem nenhuma API paga. Se faltar algo depois, a própria skill percebe antes de editar e roda o preparador de novo (é o "Passo 0" do SKILL.md).

Para atualizar a skill: peça ao Claude "atualiza a skill de edição da Eau de Leon" (ele faz `git pull` e roda o instalador de novo).

Instalação manual (se preferir):
```powershell
git clone https://github.com/cainaoteiza78-prog/skill-edicao-eau-de-leon.git
cd skill-edicao-eau-de-leon
powershell -ExecutionPolicy Bypass -File .\instalar-skill.ps1
```

## Como usar

Abra o Claude Code na pasta onde estão os vídeos e peça, por exemplo:

> Edita no padrão Eau de Leon: take1.mp4, take2.mp4, take3.mp4 (nessa ordem). Tem também o print-site.png pra usar quando eu falar do site.

Ou chame direto: `/edicao-eau-de-leon take1.mp4 take2.mp4`.

O Claude vai: transcrever → decidir cortes, legenda, destaques, textos e perfumes → renderizar um rascunho → conferir os quadros → renderizar o final. Sai `edicao/editado.mp4` + `edicao/legenda.srt`.

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
