"""Testes do Union-Find e das aplicações, com oráculos de BFS, força bruta e Prim."""

import heapq
import io
import itertools
import math
import random
import sys
import unittest
from collections import deque
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from conjuntos_disjuntos import (  # noqa: E402
    UnionFind,
    UnionFindGenerico,
    contar_ilhas,
    ilhas,
    kruskal,
)
from conjuntos_disjuntos.demo import (  # noqa: E402
    LIGACOES,
    MAPA,
    PREDIOS,
    executar,
    montar_torneio,
)

ESTRATEGIAS = ("tamanho", "rank")

# ----------------------------------------------------------------- oráculos


def componentes_bfs(n: int, arestas: list[tuple[int, int]]) -> list[int]:
    """Rótulo do componente de cada vértice (BFS em lista de adjacência)."""
    adj: list[list[int]] = [[] for _ in range(n)]
    for u, v in arestas:
        adj[u].append(v)
        adj[v].append(u)
    rotulo = [-1] * n
    atual = 0
    for s in range(n):
        if rotulo[s] != -1:
            continue
        rotulo[s] = atual
        fila = deque([s])
        while fila:
            u = fila.popleft()
            for w in adj[u]:
                if rotulo[w] == -1:
                    rotulo[w] = atual
                    fila.append(w)
        atual += 1
    return rotulo


def prim(n: int, arestas: list[tuple[int, int, float]]) -> float:
    """Peso da floresta geradora mínima por Prim (heap), recomeçando em cada componente."""
    adj: list[list[tuple[float, int]]] = [[] for _ in range(n)]
    for u, v, p in arestas:
        adj[u].append((p, v))
        adj[v].append((p, u))
    na_arvore = [False] * n
    total = 0.0
    for inicio in range(n):
        if na_arvore[inicio]:
            continue
        heap: list[tuple[float, int]] = [(0.0, inicio)]
        while heap:
            p, u = heapq.heappop(heap)
            if na_arvore[u]:
                continue
            na_arvore[u] = True
            total += p
            for q, w in adj[u]:
                if not na_arvore[w]:
                    heapq.heappush(heap, (q, w))
    return total


def mst_forca_bruta(n: int, arestas: list[tuple[int, int, float]]) -> float:
    """Menor peso entre todos os subconjuntos de n-1 arestas que formam árvore."""
    melhor = math.inf
    for escolha in itertools.combinations(arestas, n - 1):
        if len(set(componentes_bfs(n, [(u, v) for u, v, _ in escolha]))) == 1:
            melhor = min(melhor, sum(p for _, _, p in escolha))
    return melhor


def ilhas_bfs(grade: list[str], diagonais: bool) -> int:
    linhas, colunas = len(grade), len(grade[0]) if grade else 0
    passos = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    if diagonais:
        passos += [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    visto = [[False] * colunas for _ in range(linhas)]
    total = 0
    for i in range(linhas):
        for j in range(colunas):
            if grade[i][j] != "1" or visto[i][j]:
                continue
            total += 1
            visto[i][j] = True
            fila = deque([(i, j)])
            while fila:
                a, b = fila.popleft()
                for da, db in passos:
                    x, y = a + da, b + db
                    if 0 <= x < linhas and 0 <= y < colunas and grade[x][y] == "1":
                        if not visto[x][y]:
                            visto[x][y] = True
                            fila.append((x, y))
    return total


def grafo_aleatorio(
    rng: random.Random, n: int, m: int, conexo: bool
) -> list[tuple[int, int, float]]:
    arestas: list[tuple[int, int, float]] = []
    if conexo:  # árvore aleatória garante conexidade
        for v in range(1, n):
            arestas.append((rng.randrange(v), v, float(rng.randint(1, 50))))
    for _ in range(m):
        u, v = rng.randrange(n), rng.randrange(n)
        arestas.append((u, v, float(rng.randint(1, 50))))  # laços e paralelas inclusos
    return arestas


# -------------------------------------------------------------------- testes


class TestUnionFind(unittest.TestCase):
    def test_vazio(self) -> None:
        uf = UnionFind()
        self.assertEqual(len(uf), 0)
        self.assertEqual(uf.numero_de_conjuntos, 0)
        self.assertEqual(uf.grupos(), [])
        self.assertEqual(uf.altura_maxima(), 0)
        with self.assertRaises(IndexError):
            uf.encontrar(0)

    def test_parametros_invalidos(self) -> None:
        with self.assertRaises(ValueError):
            UnionFind(-1)
        with self.assertRaises(ValueError):
            UnionFind(3, "altura")  # type: ignore[arg-type]
        uf = UnionFind(3)
        for indice in (-1, 3, 100):
            with self.assertRaises(IndexError):
                uf.encontrar(indice)  # índice negativo não "dá a volta" como em listas
        with self.assertRaises(IndexError):
            uf.unir(0, 5)

    def test_operacoes_basicas(self) -> None:
        for estrategia in ESTRATEGIAS:
            with self.subTest(estrategia=estrategia):
                uf = UnionFind(6, estrategia)
                self.assertEqual(uf.numero_de_conjuntos, 6)
                self.assertTrue(uf.unir(0, 1))
                self.assertTrue(uf.unir(2, 3))
                self.assertFalse(uf.unir(1, 0))
                self.assertTrue(uf.unir(1, 3))
                self.assertFalse(uf.unir(0, 0))
                self.assertEqual(uf.numero_de_conjuntos, 3)
                self.assertTrue(uf.conectados(0, 2))
                self.assertFalse(uf.conectados(0, 4))
                self.assertEqual(uf.tamanho_do_conjunto(3), 4)
                self.assertEqual(uf.tamanho_do_conjunto(5), 1)
                self.assertEqual(uf.grupos(), [[0, 1, 2, 3], [4], [5]])
                self.assertEqual(uf.encontrar(0), uf.encontrar(3))

    def test_adicionar(self) -> None:
        uf = UnionFind(2)
        self.assertEqual(uf.adicionar(), 2)
        self.assertEqual(len(uf), 3)
        self.assertEqual(uf.numero_de_conjuntos, 3)
        uf.unir(2, 0)
        self.assertEqual(uf.grupos(), [[0, 2], [1]])

    def test_uniao_por_tamanho_menor_vai_para_maior(self) -> None:
        uf = UnionFind(5)
        uf.unir(0, 1)
        uf.unir(0, 2)  # conjunto {0,1,2}
        uf.unir(4, 0)  # 4 sozinho deve ir para baixo da raiz do conjunto grande
        self.assertEqual(uf.encontrar(4), uf.encontrar(1))
        self.assertEqual(uf._pai[4], uf.encontrar(0))

    def test_compressao_de_caminho(self) -> None:
        for estrategia in ESTRATEGIAS:
            with self.subTest(estrategia=estrategia):
                n = 1 << 10
                uf = montar_torneio(n, estrategia)  # type: ignore[arg-type]
                self.assertEqual(uf.altura_maxima(), 10)  # exatamente log2(n)
                raiz = uf.encontrar(0)
                # Elemento mais profundo: o último (n-1 = 1111111111 em binário).
                caminho = []
                x = n - 1
                while uf._pai[x] != x:
                    caminho.append(x)
                    x = uf._pai[x]
                self.assertEqual(len(caminho), 10)
                self.assertEqual(uf.encontrar(n - 1), raiz)
                for y in caminho:  # todos agora apontam direto para a raiz
                    self.assertEqual(uf._pai[y], raiz)
                for y in range(n):
                    uf.encontrar(y)
                self.assertEqual(uf.altura_maxima(), 1)

    def test_altura_limitada_por_log(self) -> None:
        rng = random.Random(3)
        for estrategia in ESTRATEGIAS:
            n = 5000
            uf = UnionFind(n, estrategia)  # type: ignore[arg-type]
            for passo in range(4 * n):
                # Une só raízes (sem compressão) para testar a heurística de união pura.
                ra, rb = rng.randrange(n), rng.randrange(n)
                while uf._pai[ra] != ra:
                    ra = uf._pai[ra]
                while uf._pai[rb] != rb:
                    rb = uf._pai[rb]
                uf.unir(ra, rb)
                if passo % 2000 == 0:
                    self.assertLessEqual(uf.altura_maxima(), math.log2(n))
            self.assertLessEqual(uf.altura_maxima(), math.log2(n))

    def test_cadeia_longa_sem_recursao(self) -> None:
        n = 200_000
        uf = UnionFind(n)
        for i in range(n - 1):
            uf.unir(i, i + 1)
        self.assertEqual(uf.numero_de_conjuntos, 1)
        self.assertEqual(uf.tamanho_do_conjunto(n // 2), n)
        self.assertTrue(uf.conectados(0, n - 1))

    def test_aleatorio_contra_bfs(self) -> None:
        rng = random.Random(2026)
        for rodada in range(200):
            estrategia = ESTRATEGIAS[rodada % 2]
            n = rng.randint(1, 60)
            arestas = [(rng.randrange(n), rng.randrange(n)) for _ in range(rng.randint(0, n))]
            uf = UnionFind(n, estrategia)  # type: ignore[arg-type]
            novas = sum(uf.unir(u, v) for u, v in arestas)
            rotulo = componentes_bfs(n, arestas)
            num_componentes = len(set(rotulo))
            self.assertEqual(uf.numero_de_conjuntos, num_componentes)
            self.assertEqual(novas, n - num_componentes)  # cada união útil reduz 1
            for _ in range(50):
                a, b = rng.randrange(n), rng.randrange(n)
                self.assertEqual(uf.conectados(a, b), rotulo[a] == rotulo[b])
                self.assertEqual(uf.tamanho_do_conjunto(a), rotulo.count(rotulo[a]))
            esperado = sorted(
                (sorted(v for v in range(n) if rotulo[v] == c) for c in set(rotulo)),
                key=lambda g: g[0],
            )
            self.assertEqual(uf.grupos(), esperado)


class TestUnionFindGenerico(unittest.TestCase):
    def test_strings_e_tuplas(self) -> None:
        uf = UnionFindGenerico(["a", "b", "c"])
        self.assertTrue(uf.adicionar((1, 2)))
        self.assertFalse(uf.adicionar("a"))
        self.assertEqual(len(uf), 4)
        self.assertIn((1, 2), uf)
        self.assertTrue(uf.unir("a", (1, 2)))
        self.assertTrue(uf.conectados((1, 2), "a"))
        self.assertIn(uf.encontrar("a"), ("a", (1, 2)))
        self.assertEqual(uf.tamanho_do_conjunto("a"), 2)
        self.assertEqual(uf.numero_de_conjuntos, 3)
        self.assertEqual(uf.grupos(), [["a", (1, 2)], ["b"], ["c"]])
        self.assertEqual(list(uf), ["a", "b", "c", (1, 2)])

    def test_elemento_inexistente(self) -> None:
        uf = UnionFindGenerico(["x"])
        with self.assertRaises(KeyError):
            uf.encontrar("y")
        with self.assertRaises(KeyError):
            uf.unir("x", "y")
        self.assertNotIn("y", uf)

    def test_aleatorio_contra_inteiros(self) -> None:
        rng = random.Random(11)
        nomes = [f"v{i}" for i in range(80)]
        uf_g = UnionFindGenerico(nomes, estrategia="rank")
        uf_i = UnionFind(80, "rank")
        for _ in range(60):
            a, b = rng.randrange(80), rng.randrange(80)
            self.assertEqual(uf_g.unir(nomes[a], nomes[b]), uf_i.unir(a, b))
        self.assertEqual(uf_g.grupos(), [[nomes[i] for i in g] for g in uf_i.grupos()])


class TestKruskal(unittest.TestCase):
    def test_exemplo_campus(self) -> None:
        total, escolhidas = kruskal(PREDIOS, LIGACOES)
        self.assertEqual(total, 610)
        self.assertEqual(len(escolhidas), len(PREDIOS) - 1)

    def test_grafo_vazio_e_unitario(self) -> None:
        self.assertEqual(kruskal([], []), (0.0, []))
        self.assertEqual(kruskal(["A"], [("A", "A", 5)]), (0.0, []))

    def test_vertice_inexistente(self) -> None:
        with self.assertRaises(KeyError):
            kruskal(["A", "B"], [("A", "C", 1)])

    def test_contra_prim(self) -> None:
        rng = random.Random(42)
        for rodada in range(300):
            n = rng.randint(1, 40)
            conexo = rodada % 3 != 0
            arestas = grafo_aleatorio(rng, n, rng.randint(0, 3 * n), conexo)
            total, escolhidas = kruskal(range(n), arestas)
            self.assertEqual(total, prim(n, arestas))
            # Floresta geradora: |V| - C arestas, sem ciclos, mesmos componentes.
            rotulo = componentes_bfs(n, [(u, v) for u, v, _ in arestas])
            c = len(set(rotulo))
            self.assertEqual(len(escolhidas), n - c)
            rotulo_mst = componentes_bfs(n, [(u, v) for u, v, _ in escolhidas])
            self.assertEqual(len(set(rotulo_mst)), c)
            self.assertEqual(total, sum(p for _, _, p in escolhidas))

    def test_contra_forca_bruta(self) -> None:
        rng = random.Random(5)
        for _ in range(60):
            n = rng.randint(2, 6)
            arestas = grafo_aleatorio(rng, n, rng.randint(0, 6), conexo=True)
            total, _ = kruskal(range(n), arestas)
            self.assertEqual(total, mst_forca_bruta(n, arestas))


class TestIlhas(unittest.TestCase):
    def test_exemplo_classico(self) -> None:
        grade = ["11000", "11000", "00100", "00011"]
        self.assertEqual(contar_ilhas(grade), 3)
        self.assertEqual(ilhas(grade)[0], [(0, 0), (0, 1), (1, 0), (1, 1)])

    def test_diagonais(self) -> None:
        grade = ["101", "010", "101"]
        self.assertEqual(contar_ilhas(grade), 5)
        self.assertEqual(contar_ilhas(grade, diagonais=True), 1)

    def test_bordas(self) -> None:
        self.assertEqual(contar_ilhas([]), 0)
        self.assertEqual(contar_ilhas(["000", "000"]), 0)
        self.assertEqual(contar_ilhas(["111", "111"]), 1)
        self.assertEqual(contar_ilhas([[1, 0, 1]], terra=1), 2)  # listas de inteiros
        with self.assertRaises(ValueError):
            contar_ilhas(["10", "1"])

    def test_demo(self) -> None:
        self.assertEqual(len(ilhas(MAPA, terra="#")), 8)
        self.assertEqual(len(ilhas(MAPA, terra="#", diagonais=True)), 6)

    def test_contra_bfs(self) -> None:
        rng = random.Random(9)
        for _ in range(300):
            linhas, colunas = rng.randint(1, 12), rng.randint(1, 12)
            p = rng.random()
            grade = [
                "".join("1" if rng.random() < p else "0" for _ in range(colunas))
                for _ in range(linhas)
            ]
            for diagonais in (False, True):
                esperado = ilhas_bfs(grade, diagonais)
                self.assertEqual(contar_ilhas(grade, diagonais=diagonais), esperado)
                celulas = sum(len(i) for i in ilhas(grade, diagonais=diagonais))
                self.assertEqual(celulas, sum(linha.count("1") for linha in grade))


class TestDemo(unittest.TestCase):
    def test_demo_executa(self) -> None:
        saida = io.StringIO()
        with redirect_stdout(saida):
            executar()
        texto = saida.getvalue()
        self.assertIn("Total: 610 m em 5 trechos", texto)
        self.assertIn("ilhas com 4 vizinhos: 8", texto)


if __name__ == "__main__":
    unittest.main()
