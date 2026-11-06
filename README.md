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
  exemplos/promocao-10-10/     ← exemplo real: 3 takes brutas do Leo + plano + vídeo editado aprovado
instalar-skill.ps1             ← instala a skill no Claude Code (Windows)
instalar-skill.sh              ← idem (Mac/Linux)
```

## Instalação — um comando, instala TUDO

Só precisa ter o **Claude Code**. Não precisa ter Python, ffmpeg, git nem permissão de administrador: o instalador baixa a skill **e todas as ferramentas** para dentro da pasta da skill (`~/.claude/skills/edicao-eau-de-leon/ferramentas`), sem mexer no resto do computador.

**Windows** — abra o PowerShell e cole:
```powershell
irm https://raw.githubusercontent.com/cainaoteiza78-prog/skill-edicao-eau-de-leon/main/instalar-skill.ps1 | iex
```

**Mac / Linux** — abra o Terminal e cole:
```bash
curl -fsSL https://raw.githubusercontent.com/cainaoteiza78-prog/skill-edicao-eau-de-leon/main/instalar-skill.sh | bash
```

Ou peça ao próprio Claude Code: *"Instala a skill de edição da Eau de Leon rodando o instalador do repositório github.com/cainaoteiza78-prog/skill-edicao-eau-de-leon e me avisa quando aparecer PRONTO."*

O que é baixado (1ª vez ~1,5 GB, alguns minutos):

| Ferramenta | Pra quê | De onde |
|---|---|---|
| ffmpeg completo (com legendas) | cortar, montar, legendar e exportar o vídeo | BtbN/FFmpeg-Builds (Win/Linux), evermeet.cx (Mac) |
| uv + Python 3.12 isolado | rodar os scripts da skill | astral.sh/uv |
| Bibliotecas (`requirements.txt`) | transcrição, detecção de rosto, imagens, remoção de fundo | PyPI |
| Modelo Whisper "small" | entender a fala, no próprio PC, grátis | Hugging Face |
| Runtime Visual C++ (só Windows, se faltar) | exigido pela transcrição | Microsoft |

No fim aparece **PRONTO**. Para atualizar, rode o mesmo comando: as ferramentas já baixadas são mantidas.

> Só `git clone` não instala nada (o Git nunca executa programas, por segurança). Se alguém só clonar, a própria skill percebe na primeira edição e roda o instalador das ferramentas sozinha (Passo 0 do SKILL.md).

## Testar se ficou tudo certo

Peça ao Claude Code: *"Edita o exemplo da promoção 10.10 da skill (exemplos/promocao-10-10/takes, nessa ordem)."* O resultado tem que ficar igual ao `exemplos/promocao-10-10/editado.mp4`.

## Como usar

Abra o Claude Code na pasta onde estão os vídeos e peça, por exemplo:

> Edita no padrão Eau de Leon: take1.mp4, take2.mp4, take3.mp4 (nessa ordem). Tem também o print-site.png pra usar quando eu falar do site.

Ou chame direto: `/edicao-eau-de-leon take1.mp4 take2.mp4`.

O Claude vai: transcrever → decidir cortes, legenda, destaques, textos e perfumes → renderizar um rascunho → conferir os quadros → renderizar o final. Sai `edicao/editado.mp4` + `edicao/legenda.srt`.

## Requisitos

- Claude Code
- Windows 10/11, macOS ou Linux, 8 GB de RAM
- ~3 GB livres em disco
- internet na instalação (depois edita offline)

## Cadastrar perfume novo

```
(use o Python da skill, caminho em scripts/python.txt)
<python> ~/.claude/skills/edicao-eau-de-leon/scripts/remover_fundo.py foto-do-perfume.jpg ~/.claude/skills/edicao-eau-de-leon/assets/perfumes/masculinos
<python> ~/.claude/skills/edicao-eau-de-leon/scripts/catalogo.py gerar
```
A foto sai com transparência real (sem fundo branco/xadrez falso).
