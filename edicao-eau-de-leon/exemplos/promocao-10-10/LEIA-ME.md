# Exemplo completo — Promoção 10.10 (takes reais do Leo)

```
takes/take1.MOV   gancho   ("A promoção do dia 10 do 10 da Eau de Leon já começou...")
takes/take2.MOV   oferta   ("Liberamos 10% de desconto em todos os perfumes...")
takes/take3.MOV   CTA      ("Não deixe pra última hora, clica em Saiba mais...")
plano.json        o plano de edição que gerou o vídeo (explicado em treinamento/09)
editado.mp4       o resultado aprovado: é a REFERÊNCIA de como a edição deve ficar
```

## Pra que serve
- **Referência visual:** antes de editar um vídeo novo, o Claude pode tirar quadros do
  `editado.mp4` (`scripts/conferir.py exemplos/promocao-10-10/editado.mp4 --cada 1`) e
  comparar com o próprio rascunho.
- **Teste da instalação:** pra conferir se a máquina está pronta, peça ao Claude:
  *"Edita o exemplo da promoção 10.10 da skill (exemplos/promocao-10-10/takes, nessa ordem)."*
  O resultado tem que ficar igual ao `editado.mp4` (a música muda a cada edição, é normal).

Rodar à mão (troque PYTHON pelo caminho em `scripts/python.txt`):
```
PYTHON scripts/transcrever.py exemplos/promocao-10-10/trabalho exemplos/promocao-10-10/takes/take1.MOV exemplos/promocao-10-10/takes/take2.MOV exemplos/promocao-10-10/takes/take3.MOV
copie plano.json para exemplos/promocao-10-10/trabalho/
PYTHON scripts/render.py exemplos/promocao-10-10/trabalho/plano.json
PYTHON scripts/revisar.py exemplos/promocao-10-10/trabalho/editado.mp4
```
