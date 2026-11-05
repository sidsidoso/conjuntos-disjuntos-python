"""Demonstração: amizades, cabeamento de um campus (Kruskal) e ilhas em um mapa."""

from __future__ import annotations

import string

from .aplicacoes import ilhas, kruskal
from .union_find import Estrategia, UnionFind, UnionFindGenerico

AMIZADES: list[tuple[str, str]] = [
    ("Ana", "Bruno"),
    ("Carla", "Diego"),
    ("Bruno", "Eduarda"),
    ("Fábio", "Gabriela"),
    ("Diego", "Helena"),
    ("Eduarda", "Ana"),  # já estavam no mesmo grupo
]
PESSOAS = ["Ana", "Bruno", "Carla", "Diego", "Eduarda", "Fábio", "Gabriela", "Helena", "Igor"]

# Prédios de um campus e o custo (metros de fibra óptica) de ligar cada par.
PREDIOS = ["Reitoria", "Biblioteca", "Bloco A", "Bloco B", "Laboratórios", "Restaurante"]
LIGACOES: list[tuple[str, str, float]] = [
    ("Reitoria", "Biblioteca", 120),
    ("Reitoria", "Bloco A", 300),
    ("Reitoria", "Restaurante", 250),
    ("Biblioteca", "Bloco A", 150),
    ("Biblioteca", "Bloco B", 200),
    ("Bloco A", "Bloco B", 90),
    ("Bloco A", "Laboratórios", 180),
    ("Bloco B", "Laboratórios", 110),
    ("Bloco B", "Restaurante", 160),
    ("Laboratórios", "Restaurante", 140),
]

MAPA = [
    "##...#....",
    "##..###...",
    "....#....#",
    ".#.......#",
    "..#..##...",
    "...#.##..#",
]


ESTRATEGIAS: tuple[Estrategia, ...] = ("tamanho", "rank")


def montar_torneio(n: int, estrategia: Estrategia) -> UnionFind:
    """Une sempre árvores de mesmo tamanho (0-1, 2-3, ..., depois 0-2, 4-6, ...).

    É o pior caso da união por tamanho/rank: a altura cresce 1 por rodada e
    termina em log2(n). Como só raízes são unidas, não há compressão.
    """
    uf = UnionFind(n, estrategia)
    passo = 1
    while passo < n:
        for i in range(0, n - passo, 2 * passo):
            uf.unir(i, i + passo)
        passo *= 2
    return uf


def _titulo(texto: str) -> None:
    print()
    print(texto)
    print("-" * len(texto))


def _desenhar_ilhas(mapa: list[str], diagonais: bool) -> list[str]:
    """Mapa com cada ilha marcada por uma letra (A, B, C, ...)."""
    linhas = [list(linha.replace("#", "?")) for linha in mapa]
    for letra, ilha in zip(string.ascii_uppercase, ilhas(mapa, terra="#", diagonais=diagonais)):
        for i, j in ilha:
            linhas[i][j] = letra
    return ["".join(linha) for linha in linhas]


def executar() -> None:
    """Executa a demonstração completa no terminal."""
    print("=== Conjuntos disjuntos (Union-Find) em Python ===")

    _titulo("Operações básicas com inteiros 0..9")
    uf = UnionFind(10)
    for a, b in [(0, 1), (2, 3), (1, 3), (4, 5), (6, 7), (5, 7), (3, 0)]:
        print(f"  unir({a}, {b}) -> {uf.unir(a, b)}")
    print(f"  {uf}")
    print(f"  grupos: {uf.grupos()}")
    print(f"  conectados(0, 2)? {uf.conectados(0, 2)}   conectados(0, 4)? {uf.conectados(0, 4)}")
    print(f"  tamanho_do_conjunto(6) = {uf.tamanho_do_conjunto(6)}")

    n = 1 << 17
    _titulo(f"Altura da floresta com n = 2^17 = {n} elementos")
    print(f"  {'estratégia':<11}{'cadeia':>7}{'torneio':>9}{'torneio após encontrar()':>26}")
    for estrategia in ESTRATEGIAS:
        cadeia = UnionFind(n, estrategia)
        for i in range(n - 1):
            cadeia.unir(i, i + 1)  # a árvore grande sempre absorve um elemento novo
        torneio = montar_torneio(n, estrategia)
        altura_torneio = torneio.altura_maxima()
        for x in range(n):
            torneio.encontrar(x)
        print(
            f"  {estrategia:<11}{cadeia.altura_maxima():>7}{altura_torneio:>9}"
            f"{torneio.altura_maxima():>26}"
        )
    print("  cadeia: unir(0, 1), unir(1, 2), ...")
    print("  torneio: só une árvores de mesmo tamanho (pior caso das heurísticas)")
    print(f"  limite teórico: log2(n) = 17; sem heurísticas, até n - 1 = {n - 1}")

    _titulo("Rede de amizades (elementos genéricos)")
    rede = UnionFindGenerico(PESSOAS)
    for a, b in AMIZADES:
        print(f"  {a} e {b}: {'novo vínculo' if rede.unir(a, b) else 'já eram do mesmo grupo'}")
    for i, grupo in enumerate(rede.grupos(), start=1):
        print(f"  grupo {i}: {', '.join(grupo)}")
    print(f"  Ana conhece (indiretamente) Eduarda? {rede.conectados('Ana', 'Eduarda')}")
    print(f"  Ana conhece (indiretamente) Carla?   {rede.conectados('Ana', 'Carla')}")

    _titulo("Kruskal: fibra óptica entre os prédios do campus")
    total, escolhidas = kruskal(PREDIOS, LIGACOES)
    for u, v, metros in escolhidas:
        print(f"  {u:<12} -- {v:<12} {metros:>5.0f} m")
    todas = sum(p for _, _, p in LIGACOES)
    print(f"  Total: {total:.0f} m em {len(escolhidas)} trechos", end="")
    print(f" (ligar todos os pares listados custaria {todas:.0f} m)")

    _titulo("Ilhas no mapa ('#' = terra)")
    vizinhanca4 = _desenhar_ilhas(MAPA, diagonais=False)
    vizinhanca8 = _desenhar_ilhas(MAPA, diagonais=True)
    print(f"  {'mapa':<12}{'4 vizinhos':<12}8 vizinhos")
    for original, v4, v8 in zip(MAPA, vizinhanca4, vizinhanca8):
        print(f"  {original:<12}{v4:<12}{v8}")
    n4 = len(ilhas(MAPA, terra="#"))
    n8 = len(ilhas(MAPA, terra="#", diagonais=True))
    print(f"  ilhas com 4 vizinhos: {n4}   com 8 vizinhos (diagonais): {n8}")
