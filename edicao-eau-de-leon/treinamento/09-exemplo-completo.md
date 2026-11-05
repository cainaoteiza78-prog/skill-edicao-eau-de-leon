# 09 — Exemplo completo (takes reais do Leo, promoção 10.10)

Três takes brutas gravadas no iPhone (1920×1080 deitado, rotacionado pelo celular → o render enquadra em 9:16). A voz é só a do Leo.

Ordem passada pelo usuário: `IMG_1586.MOV` (gancho) → `IMG_1598.MOV` (oferta) → `IMG_1591.MOV` (CTA).

## transcricao.txt (resumido)

```
── TAKE 1 (IMG_1586.MOV, 6.8s) ──
      ↳ A(0.00) promoção(1.00) do(1.44) dia(1.56) 10(1.78) -10(2.14) da(2.46) Aude(2.70) Leon(2.88) já(3.12) começou(3.40) e(3.94) ela(4.18) tá(4.28) simplesmente(4.42) imperdível.(4.86)
── TAKE 2 (IMG_1598.MOV, 10.6s) ──
      ↳ Liberamos(1.70) 10(2.24) %(2.56) do(3.04) desconto(3.22) em(3.54) todos(3.72) os(4.02) perfumes(4.30) até(4.76) o(5.12) dia(5.30) 10(5.50) de(5.94) mês.(6.12)
      ↳ Isso(6.74) o(6.94) mês(7.04) que(7.14) você(7.30) ouviu.(7.42)
      ↳ 10(7.92) %(8.18) em(8.56) todos(8.88) os(9.06) perfumes.(9.26)
── TAKE 3 (IMG_1591.MOV, 6.5s) ──
      ↳ Não(1.60) deixe(2.00) pra(2.32) ultimora,(2.42) clica(2.98) em(3.18) salha(3.26) mais(3.54) e(3.74) faça(3.94) já(4.12) o(4.38) seu(4.46) pedido.(4.56)
```

## Como o editor pensou

1. **Formato** `leo`, legenda `frase`, marca d'água automática, sem cartão final.
2. **Trechos:** um por take, da primeira à última palavra. O render tira as pausas e respirações sozinho, sem cortar palavra.
3. **Whip** só na troca do gancho para a oferta (muda o cenário).
4. **Gancho:** destaque Bungee "PROMOÇÃO / 10.10" de "promoção" até o fim do segundo "10" (2,75). Sem redundância: a legenda continua em "Eau de Leon já começou", sem repetir "10.10".
5. **Palavras-chave** (regra da oferta, vindas do `destaques_sugeridos.txt`): "liberamos **10% DE DESCONTO** em **TODOS OS PERFUMES** até o dia **10** desse mês. Isso mesmo que você ouviu, **10%** em **TODOS OS PERFUMES**." Em cada uma, a legenda cresceu para Bebas (frase em cima, palavra-chave grande embaixo), com zoom de ênfase.
6. **CTA:** "clica em Saiba mais" virou a **placa de vidro 3D** sozinha, azul (o fundo era a caixa rosa), pulsando até o fim.
7. **Grafia:** "Aude Leon" → Eau de Leon; "10 -10" → 10.10; "ultimora" → última hora; "salha mais" → Saiba mais; "do desconto" → de desconto; "de mês" → desse mês; "isso o mês" → isso mesmo.
8. **Música:** `auto`, trilha animada nova.
9. **Pacing:** o render fez 4 punches de enquadramento e 6 zooms de ênfase.

## plano.json

```json
{
  "saida": "editado-v4.mp4",
  "formato": "leo",
  "legenda": "frase",
  "trechos": [
    {"take": 1, "ini": 0.0, "fim": 6.0},
    {"take": 2, "ini": 1.55, "fim": 9.90, "transicao": "whip"},
    {"take": 3, "ini": 1.50, "fim": 5.10}
  ],
  "correcoes": [
    {"de": "Aude Leon", "para": "Eau de Leon"},
    {"de": "10 -10", "para": "10.10"},
    {"de": "ultimora", "para": "última hora"},
    {"de": "salha mais", "para": "Saiba mais"},
    {"de": "do desconto", "para": "de desconto"},
    {"de": "de mês", "para": "desse mês"},
    {"de": "isso o mês", "para": "isso mesmo"}
  ],
  "textos": [
    {"texto": "PROMOÇÃO
10.10", "estilo": "destaque", "take": 1, "ini": 1.00, "fim": 2.75}
  ],
  "destaques": [
    {"take": 2, "ini": 2.24, "fim": 3.54},
    {"take": 2, "ini": 3.72, "fim": 4.76},
    {"take": 2, "ini": 5.50, "fim": 5.94},
    {"take": 2, "ini": 7.92, "fim": 8.56},
    {"take": 2, "ini": 8.88, "fim": 9.68}
  ],
  "musica": "auto"
}
```

## Resultado

23,9 s de bruto → 16,5 s. `conferir.py`: **PAUSAS: nenhuma**, **PALAVRAS: todas inteiras**, voz em -14,6 LUFS. Legenda no peito, 5 palavras-chave com a legenda aumentada, CTA SAIBA MAIS em vidro 3D azul pulsando, marca d'água do início ao fim.
