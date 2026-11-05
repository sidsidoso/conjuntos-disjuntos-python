"""Pacote ``conjuntos_disjuntos``: Union-Find com aplicações (Kruskal e ilhas)."""

from .aplicacoes import contar_ilhas, ilhas, kruskal
from .union_find import Estrategia, UnionFind, UnionFindGenerico

__all__ = [
    "Estrategia",
    "UnionFind",
    "UnionFindGenerico",
    "contar_ilhas",
    "ilhas",
    "kruskal",
]
__version__ = "1.0.0"
