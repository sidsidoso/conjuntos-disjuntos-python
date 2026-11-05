# Conjuntos Disjuntos (Union-Find) em Python

[![CI](https://github.com/sidsidoso/conjuntos-disjuntos-python/actions/workflows/ci.yml/badge.svg)](https://github.com/sidsidoso/conjuntos-disjuntos-python/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Licença: MIT](https://img.shields.io/badge/licen%C3%A7a-MIT-green.svg)](LICENSE)

Implementação didática e completa da estrutura de **conjuntos disjuntos** (*Union-Find* ou
*Disjoint Set Union*) em Python puro (somente biblioteca padrão), com **união por tamanho ou por
rank** e **compressão de caminho iterativa**. Inclui uma versão **genérica** para elementos
*hashable* (strings, tuplas...) e duas aplicações clássicas: o **algoritmo de Kruskal** (árvore
geradora mínima) e a **contagem de ilhas** em uma grade.

A demonstração agrupa uma rede de amizades, calcula o cabeamento de fibra óptica mais barato entre
os prédios de um campus e rotula as ilhas de um mapa em ASCII.

## Sumário

- [Conceito](#conceito)
- [Operações e complexidade](#operações-e-complexidade)
- [Decisões de implementação e otimizações](#decisões-de-implementação-e-otimizações)
- [Estrutura de pastas](#estrutura-de-pastas)
- [Como executar](#como-executar)
- [Como testar](#como-testar)
- [Exemplo de uso](#exemplo-de-uso)
- [Saída da demonstração](#saída-da-demonstração)
- [Referências](#referências)

## Conceito

A estrutura mantém uma **partição** de `n` elementos em conjuntos que não se sobrepõem, e responde
a duas perguntas: *a que conjunto `x` pertence?* (`encontrar`) e *junte os conjuntos de `a` e `b`*
(`unir`). Cada conjunto é uma **árvore** guardada num único vetor `pai`; a raiz é o
**representante** e aponta para si mesma.

```text
  pai = [0, 0, 0, 2, 4, 4, 5]          conjuntos {0, 1, 2, 3} e {4, 5, 6}

         0               4
        / \              |
       1   2             5
           |             |
           3             6
```

**União por tamanho (ou rank).** Para unir, liga-se a raiz da árvore **menor** abaixo da raiz da
**maior**. Um elemento só desce um nível quando o seu conjunto pelo menos dobra de tamanho, logo
a altura nunca passa de **log2(n)**:

```text
  unir(3, 6): tamanho(0) = 4 > tamanho(4) = 3  ->  pai[4] = 0

             0
          /  |  \
         1   2   4
             |   |
             3   5
                 |
                 6
```

(Para separar as ideias, o desenho acima mostra só a ligação das raízes; no código, os
`encontrar` que `unir` chama internamente também comprimem os caminhos de `3` e `6`.)

**Compressão de caminho.** Ao executar `encontrar(6)` na árvore acima, o caminho `6 → 5 → 4 → 0` é percorrido e,
numa segunda passada, **todos** os nós dele passam a apontar direto para a raiz:

```text
  encontrar(6)  ->  0

             0
        / / | \ \
       1 2  4  5  6
         |
         3
```

Juntas, as duas heurísticas dão custo amortizado **O(α(n))** por operação, em que α é a inversa
da função de Ackermann: α(n) ≤ 4 para qualquer `n` que caiba no universo observável. Na prática,
é tempo constante.

**Kruskal.** Ordena as arestas por peso e aceita cada uma que liga dois componentes diferentes;
o Union-Find responde "já estão conectados?" e faz a fusão.

**Ilhas.** Cada célula de terra é um elemento (`linha · colunas + coluna`). Basta unir cada
célula com as vizinhas de terra à direita e abaixo (e nas diagonais de baixo, se pedidas); o
número de ilhas é o número de conjuntos formados por células de terra.

## Operações e complexidade

`n` = número de elementos, `α` = inversa de Ackermann, `V`/`E` = vértices/arestas,
`L × C` = dimensões da grade.

| Operação | Método | Tempo (amortizado) | Pior caso de uma chamada |
|---|---|---|---|
| Criar com `n` elementos | `UnionFind(n)` | O(n) | O(n) |
| Novo elemento | `adicionar()` | O(1) | O(1) |
| Representante | `encontrar(x)` | O(α(n)) | O(log n) |
| Unir | `unir(a, b)` | O(α(n)) | O(log n) |
| Mesmo conjunto? | `conectados(a, b)` | O(α(n)) | O(log n) |
| Tamanho do conjunto | `tamanho_do_conjunto(x)` | O(α(n)) | O(log n) |
| Número de conjuntos | `numero_de_conjuntos` | O(1) | O(1) |
| Todos os grupos | `grupos()` | O(n · α(n)) | O(n log n) |
| Altura atual (estudo) | `altura_maxima()` | O(n) | O(n) |
| Versão genérica (hashable) | `UnionFindGenerico` | + O(1) médio do `dict` | |
| Kruskal | `kruskal(vertices, arestas)` | O(E log E) | |
| Ilhas | `ilhas(grade)`, `contar_ilhas(grade)` | O(L · C · α(L · C)) | |
| **Espaço** | | O(n): 3 vetores de inteiros | |

O pior caso "O(log n)" vale pela união por tamanho/rank sozinha; a compressão melhora o custo
amortizado.

## Decisões de implementação e otimizações

- **Vetores (`list`) em vez de objetos-nó**: `pai`, `tamanho` e `rank` são listas de inteiros
  indexadas pelo elemento. É compacto, tem boa localidade e evita milhões de objetos pequenos.
- **Duas estratégias de união** (`estrategia="tamanho"`, padrão, ou `"rank"`). O tamanho é
  mantido nas duas, pois `tamanho_do_conjunto` precisa dele; o rank (limite superior da altura)
  só é usado na estratégia `"rank"`. Em empate, o primeiro argumento vira a raiz.
- **Compressão de caminho iterativa em duas passadas**: a primeira acha a raiz, a segunda
  religa o caminho (`pai[x], x = raiz, pai[x]`). Sem recursão, então cadeias longas não atingem o
  limite de recursão do Python (testado com 200 000 elementos).
- **`numero_de_conjuntos` em O(1)**: um contador decrementado a cada união efetiva; `unir` devolve
  `False` quando os elementos já estavam juntos (útil no Kruskal e para detectar ciclos).
- **Índices validados**: `encontrar(-1)` lança `IndexError` em vez de "dar a volta" como faria uma
  lista do Python.
- **Versão genérica por mapeamento**: `UnionFindGenerico` associa cada elemento *hashable* a um
  índice (`dict` elemento → índice e lista índice → elemento) e delega tudo ao `UnionFind` de
  inteiros, em vez de manter dicionários de pais. Elementos desconhecidos geram `KeyError`.
- **`grupos()` determinístico**: cada grupo sai em ordem crescente e os grupos aparecem pela ordem
  do menor elemento, sem precisar ordenar no final.
- **Kruskal com parada antecipada**: termina quando já escolheu `|V| - 1` arestas; em grafo
  desconexo devolve a **floresta** geradora mínima. Laços e arestas paralelas são aceitos.
- **Ilhas sem visitar adjacências repetidas**: só os vizinhos "para frente" (direita/abaixo e as
  diagonais de baixo) são unidos, então cada adjacência é examinada uma única vez. A grade pode ser
  uma lista de strings ou de listas, com o símbolo de terra configurável (`terra="#"`, `terra=1`).
- `__slots__` nas classes e *type hints* (`UnionFindGenerico[str]`).

## Estrutura de pastas

```text
conjuntos-disjuntos-python/
├── .github/workflows/ci.yml       # testes + demo em Python 3.11, 3.12 e 3.13
├── src/conjuntos_disjuntos/
│   ├── __init__.py                # API pública
│   ├── __main__.py                # python -m conjuntos_disjuntos
│   ├── aplicacoes.py              # kruskal, ilhas, contar_ilhas
│   ├── demo.py                    # amizades, campus e mapa de ilhas
│   └── union_find.py              # UnionFind e UnionFindGenerico
├── tests/
│   └── test_union_find.py         # unittest: bordas + oráculos (BFS, Prim, força bruta)
├── main.py                        # demonstração (não exige instalação)
├── pyproject.toml
├── LICENSE
└── README.md
```

## Como executar

Requisito: **Python 3.11+**. Não há dependências externas.

**Linux / macOS**

```bash
git clone https://github.com/sidsidoso/conjuntos-disjuntos-python.git
cd conjuntos-disjuntos-python
python3 main.py
# ou, como módulo:
PYTHONPATH=src python3 -m conjuntos_disjuntos
```

**Windows (PowerShell)**

```powershell
git clone https://github.com/sidsidoso/conjuntos-disjuntos-python.git
cd conjuntos-disjuntos-python
py main.py
# ou, como módulo:
$env:PYTHONPATH = "src"; py -m conjuntos_disjuntos
```

Opcionalmente, instale o pacote em modo editável: `pip install -e .`.

## Como testar

```bash
# Linux / macOS
python3 -m unittest discover -s tests -v
```

```powershell
# Windows
py -m unittest discover -s tests -v
```

A suíte cobre casos de borda (estrutura vazia, índices inválidos ou negativos, união de um
elemento consigo mesmo, elemento genérico inexistente, grade vazia ou irregular) e compara tudo
com **oráculos independentes**:

- conectividade, tamanhos, número de conjuntos e `grupos()` contra **BFS** em 200 grafos
  aleatórios, alternando as duas estratégias;
- compressão de caminho verificada nó a nó no pior caso ("torneio" com altura exatamente log2 n)
  e altura ≤ log2(n) após 20 000 uniões aleatórias sem compressão;
- **Kruskal contra Prim** (com `heapq`) em 300 grafos aleatórios, conexos e desconexos, conferindo
  peso total, número de arestas `|V| - C` e ausência de ciclos; e contra **força bruta** (todos os
  subconjuntos de `|V| - 1` arestas) em grafos pequenos;
- contagem de ilhas contra **BFS** (*flood fill*) em 300 grades aleatórias, com 4 e 8 vizinhos.

Resultado local:

```text
Ran 23 tests in 0.690s

OK
```

## Exemplo de uso

```python
from conjuntos_disjuntos import UnionFind, UnionFindGenerico, contar_ilhas, kruskal

uf = UnionFind(6)
uf.unir(0, 1); uf.unir(2, 3); uf.unir(1, 3)
uf.conectados(0, 2)          # True
uf.tamanho_do_conjunto(0)    # 4
uf.numero_de_conjuntos       # 3
uf.grupos()                  # [[0, 1, 2, 3], [4], [5]]

rede = UnionFindGenerico(["Ana", "Bruno", "Carla"])
rede.unir("Ana", "Carla")
rede.grupos()                # [['Ana', 'Carla'], ['Bruno']]

kruskal("ABC", [("A", "B", 4), ("B", "C", 1), ("A", "C", 2)])
# (3.0, [('B', 'C', 1), ('A', 'C', 2)])

contar_ilhas(["11000", "11000", "00100", "00011"])   # 3
```

## Saída da demonstração

Saída real de `python main.py`:

```text
=== Conjuntos disjuntos (Union-Find) em Python ===

Operações básicas com inteiros 0..9
-----------------------------------
  unir(0, 1) -> True
  unir(2, 3) -> True
  unir(1, 3) -> True
  unir(4, 5) -> True
  unir(6, 7) -> True
  unir(5, 7) -> True
  unir(3, 0) -> False
  UnionFind(elementos=10, conjuntos=4, estrategia='tamanho')
  grupos: [[0, 1, 2, 3], [4, 5, 6, 7], [8], [9]]
  conectados(0, 2)? True   conectados(0, 4)? False
  tamanho_do_conjunto(6) = 4

Altura da floresta com n = 2^17 = 131072 elementos
--------------------------------------------------
  estratégia  cadeia  torneio  torneio após encontrar()
  tamanho          1       17                         1
  rank             1       17                         1
  cadeia: unir(0, 1), unir(1, 2), ...
  torneio: só une árvores de mesmo tamanho (pior caso das heurísticas)
  limite teórico: log2(n) = 17; sem heurísticas, até n - 1 = 131071

Rede de amizades (elementos genéricos)
--------------------------------------
  Ana e Bruno: novo vínculo
  Carla e Diego: novo vínculo
  Bruno e Eduarda: novo vínculo
  Fábio e Gabriela: novo vínculo
  Diego e Helena: novo vínculo
  Eduarda e Ana: já eram do mesmo grupo
  grupo 1: Ana, Bruno, Eduarda
  grupo 2: Carla, Diego, Helena
  grupo 3: Fábio, Gabriela
  grupo 4: Igor
  Ana conhece (indiretamente) Eduarda? True
  Ana conhece (indiretamente) Carla?   False

Kruskal: fibra óptica entre os prédios do campus
------------------------------------------------
  Bloco A      -- Bloco B         90 m
  Bloco B      -- Laboratórios   110 m
  Reitoria     -- Biblioteca     120 m
  Laboratórios -- Restaurante    140 m
  Biblioteca   -- Bloco A        150 m
  Total: 610 m em 5 trechos (ligar todos os pares listados custaria 1700 m)

Ilhas no mapa ('#' = terra)
---------------------------
  mapa        4 vizinhos  8 vizinhos
  ##...#....  AA...B....  AA...B....
  ##..###...  AA..BBB...  AA..BBB...
  ....#....#  ....B....C  ....B....C
  .#.......#  .D.......C  .D.......C
  ..#..##...  ..E..FF...  ..D..EE...
  ...#.##..#  ...G.FF..H  ...D.EE..F
  ilhas com 4 vizinhos: 8   com 8 vizinhos (diagonais): 6
```

## Referências

- CORMEN, T. H.; LEISERSON, C. E.; RIVEST, R. L.; STEIN, C. *Algoritmos: Teoria e Prática*.
  3. ed. Elsevier, 2012. Capítulos 21 (Estruturas de Dados para Conjuntos Disjuntos) e 23
  (Árvores Geradoras Mínimas).
- TARJAN, R. E. Efficiency of a good but not linear set union algorithm. *Journal of the ACM*,
  v. 22, n. 2, p. 215–225, 1975.
- GALLER, B. A.; FISCHER, M. J. An improved equivalence algorithm. *Communications of the ACM*,
  v. 7, n. 5, p. 301–303, 1964.
- KRUSKAL, J. B. On the shortest spanning subtree of a graph and the traveling salesman problem.
  *Proceedings of the American Mathematical Society*, v. 7, n. 1, p. 48–50, 1956.
- SEDGEWICK, R.; WAYNE, K. *Algorithms*. 4. ed. Addison-Wesley, 2011. Seções 1.5 (Union-Find) e
  4.3 (Minimum Spanning Trees).

## Licença

Distribuído sob a licença MIT. Veja [LICENSE](LICENSE).
