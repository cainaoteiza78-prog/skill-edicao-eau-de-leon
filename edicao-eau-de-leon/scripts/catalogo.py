"""
Catálogo de perfumes sem fundo (assets/perfumes) + busca de citações na fala.

Uso:
  python catalogo.py buscar "le male elixir"     # acha o id certo pra usar no plano
  python catalogo.py listar [femininos|masculinos]
  python catalogo.py gerar [pasta_dos_originais]  # refaz assets/perfumes/perfumes.json

Cada perfume tem:
  id        "masculinos/le-male-elixir"  (é isso que vai no plano.json)
  nome      nome como veio da área de membros
  arquivo   caminho do PNG sem fundo (relativo a assets/perfumes)
  angulos   outras fotos do mesmo perfume (pasta outros-angulos), se houver
  apelidos  jeitos de falar o nome (o que a busca na transcrição procura)

Para ensinar um apelido novo ("o azulzinho da Lattafa"), edite "apelidos" no
perfumes.json — não precisa rodar nada.
"""
import sys as _sys
_sys.stdout.reconfigure(encoding='utf-8', errors='replace')  # console do Windows
import json
import os
import re
import sys
import unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))
PASTA = os.path.normpath(os.path.join(AQUI, '..', 'assets', 'perfumes'))
JSON = os.path.join(PASTA, 'perfumes.json')

CONCENTRACOES = {'edp', 'edt', 'edc', 'extrait', 'de', 'parfum', 'eau', 'toilette', 'perfume', 'intense'}
# Palavras comuns que não podem, sozinhas, disparar um perfume.
COMUNS = set('''
a o e de da do das dos um uma com sem para pra por mais menos muito pouco bom boa melhor
noite dia amor love sexy black white blue red gold rose rosa azul preto branco vermelho
her him men man woman women homme femme pour club good girl boy king queen one only
light dark night day fresh sport idol idole the in for my you me si yes no
'''.split())
MARCAS = ['carolina herrera', 'lancome', 'mugler', 'chanel', 'dior', 'paco rabanne', 'rabanne', 'lattafa', 'armaf',
          'givenchy', 'versace', 'prada', 'valentino', 'gucci', 'ysl', 'yves saint laurent', 'azzaro', 'montblanc',
          'jean paul gaultier', 'dolce gabbana', 'd g', 'creed', 'xerjoff', 'afnan', 'al haramain', 'rasasi',
          'orientica', 'maison alhambra', 'parfums de marly', 'tom ford', 'bvlgari', 'hugo boss', 'boss', 'calvin klein']
SIGLAS = {'ch': 'carolina herrera', 'bs': 'britney spears', 'ysl': 'yves saint laurent', 'cdn': 'club de nuit',
          'dg': 'dolce gabbana', 'jpg': 'jean paul gaultier', 'pdm': 'parfums de marly'}


def norm(s: str) -> str:
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    s = s.replace('&', ' e ').replace('°', '').replace("'", '')
    return re.sub(r'[^a-z0-9]+', ' ', s).strip()


def slug(nome: str) -> str:
    return norm(nome).replace(' ', '-')


def apelidos_de(nome: str) -> list:
    n = norm(nome)
    ap = {n}
    toks = n.split()
    sem_conc = [t for t in toks if t not in CONCENTRACOES]
    if sem_conc:
        ap.add(' '.join(sem_conc))
    if toks and toks[0] in SIGLAS:
        resto = ' '.join(toks[1:])
        ap.add(resto)
        ap.add(SIGLAS[toks[0]] + ' ' + resto)
        ap.add(' '.join(t for t in resto.split() if t not in CONCENTRACOES))
    for x in list(ap):
        for m in MARCAS:  # "good girl carolina herrera" → "good girl"
            if x.endswith(' ' + m) and len(x) > len(m) + 3:
                ap.add(x[: -len(m)].strip())
            if x.startswith(m + ' ') and len(x) > len(m) + 3:
                ap.add(x[len(m):].strip())
    for x in list(ap):
        if x.startswith('1 '):  # "1 million" também é falado "one million"
            ap.add('one ' + x[2:])
    ap = {x.strip() for x in ap if x.strip()}
    # Apelido de uma palavra só precisa ser específico.
    return sorted(x for x in ap if len(x.split()) > 1 or (len(x) >= 4 and x not in COMUNS) or x.isdigit() and len(x) >= 2)


def gerar(originais: str | None = None):
    nomes = {}
    if originais:
        for raiz, _, arqs in os.walk(originais):
            for f in arqs:
                nomes[slug(os.path.splitext(f)[0])] = os.path.splitext(f)[0]
    antigo = {}
    if os.path.exists(JSON):
        antigo = {p['id']: p for p in json.load(open(JSON, encoding='utf8'))['perfumes']}
    lista = []
    for genero in ('femininos', 'masculinos'):
        base = os.path.join(PASTA, genero)
        if not os.path.isdir(base):
            continue
        outros = os.path.join(base, 'outros-angulos')
        extras = sorted(os.listdir(outros)) if os.path.isdir(outros) else []
        for f in sorted(os.listdir(base)):
            if not f.endswith('.png'):
                continue
            s = f[:-4]
            pid = f'{genero}/{s}'
            nome = nomes.get(s) or antigo.get(pid, {}).get('nome') or s.replace('-', ' ').upper()
            ang = [f'{genero}/outros-angulos/{e}' for e in extras if e[:-4] == s or e[:-4].startswith(s + '-')]
            ap = set(apelidos_de(nome)) | set(antigo.get(pid, {}).get('apelidos', []))
            lista.append({'id': pid, 'nome': nome, 'genero': genero[:-1], 'arquivo': f'{genero}/{f}', 'angulos': ang, 'apelidos': sorted(ap)})
        # Toda foto de "outros ângulos" também é uma entrada própria (dá pra usar pelo id).
        for e in extras:
            if not e.endswith('.png'):
                continue
            s = e[:-4]
            pid = f'{genero}/outros-angulos/{s}'
            nome = nomes.get(s) or antigo.get(pid, {}).get('nome') or s.replace('-', ' ').upper()
            ap = set(apelidos_de(nome)) | set(antigo.get(pid, {}).get('apelidos', []))
            lista.append({'id': pid, 'nome': nome, 'genero': genero[:-1], 'arquivo': f'{genero}/outros-angulos/{e}', 'angulos': [], 'apelidos': sorted(ap)})
    with open(JSON, 'w', encoding='utf8') as fp:
        json.dump({'perfumes': lista}, fp, ensure_ascii=False, indent=1)
    print(f'{len(lista)} perfumes no catálogo → {JSON}')


def carregar() -> list:
    if not os.path.exists(JSON):
        return []
    return json.load(open(JSON, encoding='utf8'))['perfumes']


def por_id(cat: list, pid: str) -> dict | None:
    return next((p for p in cat if p['id'] == pid), None)


def buscar(cat: list, texto: str, n: int = 8) -> list:
    q = norm(texto)
    qt = set(q.split())
    res = []
    for p in cat:
        melhor = 0.0
        for a in p['apelidos'] + [norm(p['nome'])]:
            at = set(a.split())
            if q == a:
                sc = 100
            elif q in a or a in q:
                sc = 60 + 30 * min(len(q), len(a)) / max(len(q), len(a))
            else:
                inter = len(qt & at)
                sc = 50 * inter / max(len(qt), len(at)) if inter else 0
            melhor = max(melhor, sc)
        if melhor > 0:
            res.append((melhor, p))
    res.sort(key=lambda x: (-x[0], 'outros-angulos' in x[1]['id'], x[1]['id']))
    return [p | {'score': round(s)} for s, p in res[:n]]


def achar_citacoes(transcricao: dict, cat: list) -> list:
    """Procura os apelidos do catálogo na fala (palavra a palavra). Fica com o
    apelido mais longo em cada ponto e ignora repetição do mesmo perfume < 3 s."""
    apelidos = []
    for p in cat:
        if 'outros-angulos' in p['id']:
            continue
        for a in p['apelidos']:
            apelidos.append((a.split(), p))
    apelidos.sort(key=lambda x: -len(' '.join(x[0])))
    achados = []
    for take in transcricao['takes']:
        pal = take['palavras']
        toks = []
        for i, w in enumerate(pal):
            for t in norm(w['p']).split():
                toks.append((t, i))
        usados = set()
        for i in range(len(toks)):
            if i in usados:
                continue
            for seq, p in apelidos:
                L = len(seq)
                if [t for t, _ in toks[i:i + L]] == seq:
                    w0 = pal[toks[i][1]]
                    trecho = ' '.join(pal[j]['p'] for j in range(toks[i][1], toks[i + L - 1][1] + 1))
                    achados.append({'take': take['n'], 'ini': w0['ini'], 'id': p['id'], 'nome': p['nome'], 'trecho': trecho})
                    usados.update(range(i, i + L))
                    break
    final = []
    for c in sorted(achados, key=lambda c: (c['take'], c['ini'])):
        if final and final[-1]['id'] == c['id'] and final[-1]['take'] == c['take'] and c['ini'] - final[-1]['ini'] < 3:
            continue
        final.append(c)
    return final


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    cmd = sys.argv[1]
    if cmd == 'gerar':
        gerar(sys.argv[2] if len(sys.argv) > 2 else None)
    elif cmd == 'buscar':
        for p in buscar(carregar(), ' '.join(sys.argv[2:])):
            print(f"{p['score']:>3}  {p['id']:<55} {p['nome']}")
    elif cmd == 'listar':
        g = sys.argv[2] if len(sys.argv) > 2 else ''
        for p in carregar():
            if p['id'].startswith(g):
                print(f"{p['id']:<55} {p['nome']}")
    else:
        print(__doc__)


if __name__ == '__main__':
    main()
