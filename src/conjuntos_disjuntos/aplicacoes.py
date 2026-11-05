"""Aplicações clássicas do Union-Find: Kruskal e contagem de ilhas em grade."""

from __future__ import annotations

from collections.abc import Hashable, Iterable, Sequence
from typing import TypeVar

from .union_find import UnionFind, UnionFindGenerico

V = TypeVar("V", bound=Hashable)

__all__ = ["contar_ilhas", "ilhas", "kruskal"]


def kruskal(
    vertices: Iterable[V], arestas: Iterable[tuple[V, V, float]]
) -> tuple[float, list[tuple[V, V, float]]]:
    """Árvore geradora mínima pelo algoritmo de Kruskal.

    Ordena as arestas por peso e aceita cada uma que liga dois componentes
    diferentes (o Union-Find responde isso em tempo quase constante).

    Devolve ``(peso_total, arestas_escolhidas)``. Se o grafo for desconexo, o
    resultado é a **floresta** geradora mínima (uma árvore por componente),
    com ``|V| - componentes`` arestas.

    Complexidade: O(E log E) para ordenar + O(E · α(V)) para as uniões.
    """
    uf: UnionFindGenerico[V] = UnionFindGenerico(vertices)
    # sorted é estável: arestas de mesmo peso mantêm a ordem de entrada.
    ordenadas = sorted(arestas, key=lambda aresta: aresta[2])
    escolhidas: list[tuple[V, V, float]] = []
    total = 0.0
    limite = len(uf) - 1
    for u, v, peso in ordenadas:
        if u not in uf or v not in uf:
            raise KeyError(f"aresta ({u!r}, {v!r}) usa vértice inexistente")
        if uf.unir(u, v):
            escolhidas.append((u, v, peso))
            total += peso
            if len(escolhidas) == limite:  # árvore completa: pode parar
                break
    return total, escolhidas


def ilhas(
    grade: Sequence[Sequence[object]], terra: object = "1", diagonais: bool = False
) -> list[list[tuple[int, int]]]:
    """Ilhas (componentes de células ``terra``) de uma grade retangular.

    Cada célula ``(linha, coluna)`` vira o índice ``linha * colunas + coluna``.
    Basta unir cada célula de terra com as vizinhas de terra **à direita e
    abaixo** (e nas duas diagonais de baixo, se ``diagonais``): cada adjacência
    é examinada uma única vez.

    Devolve as ilhas como listas de coordenadas, em ordem de leitura.
    Complexidade: O(L · C · α(L · C)).
    """
    linhas = len(grade)
    colunas = len(grade[0]) if linhas else 0
    if any(len(linha) != colunas for linha in grade):
        raise ValueError("a grade precisa ser retangular")

    vizinhos = [(0, 1), (1, 0)]
    if diagonais:
        vizinhos += [(1, 1), (1, -1)]

    uf = UnionFind(linhas * colunas)
    for i in range(linhas):
        for j in range(colunas):
            if grade[i][j] != terra:
                continue
            for di, dj in vizinhos:
                ni, nj = i + di, j + dj
                if 0 <= ni < linhas and 0 <= nj < colunas and grade[ni][nj] == terra:
                    uf.unir(i * colunas + j, ni * colunas + nj)

    por_raiz: dict[int, list[tuple[int, int]]] = {}
    for i in range(linhas):
        for j in range(colunas):
            if grade[i][j] == terra:
                por_raiz.setdefault(uf.encontrar(i * colunas + j), []).append((i, j))
    return list(por_raiz.values())


def contar_ilhas(
    grade: Sequence[Sequence[object]], terra: object = "1", diagonais: bool = False
) -> int:
    """Número de ilhas da grade (ver :func:`ilhas`)."""
    return len(ilhas(grade, terra, diagonais))
