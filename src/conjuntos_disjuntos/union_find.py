"""Conjuntos disjuntos (Union-Find) com união por tamanho/rank e compressão de caminho."""

from __future__ import annotations

from collections.abc import Hashable, Iterable, Iterator
from typing import Generic, Literal, TypeVar

T = TypeVar("T", bound=Hashable)
Estrategia = Literal["tamanho", "rank"]

__all__ = ["Estrategia", "UnionFind", "UnionFindGenerico"]


class UnionFind:
    """Floresta de conjuntos disjuntos sobre os inteiros ``0 .. n-1``.

    Cada conjunto é uma árvore representada pelo vetor ``_pai``; a raiz é o
    representante. Duas otimizações mantêm as árvores rasas:

    - **união por tamanho** (padrão) ou **por rank**: a raiz da árvore menor
      (ou de menor rank) passa a apontar para a da maior;
    - **compressão de caminho** (iterativa): depois de achar a raiz, todos os
      nós do caminho passam a apontar diretamente para ela.

    Com as duas, uma sequência de m operações custa O(m · α(n)), em que α é a
    inversa da função de Ackermann (α(n) <= 4 para qualquer n prático).
    """

    __slots__ = ("_estrategia", "_numero_de_conjuntos", "_pai", "_rank", "_tamanho")

    def __init__(self, n: int = 0, estrategia: Estrategia = "tamanho") -> None:
        if n < 0:
            raise ValueError("n não pode ser negativo")
        if estrategia not in ("tamanho", "rank"):
            raise ValueError("estrategia deve ser 'tamanho' ou 'rank'")
        self._estrategia: Estrategia = estrategia
        self._pai = list(range(n))
        self._tamanho = [1] * n  # válido apenas nas raízes
        self._rank = [0] * n  # limite superior da altura; só usado na estratégia "rank"
        self._numero_de_conjuntos = n

    # ------------------------------------------------------------ básicos

    def __len__(self) -> int:
        """Número de elementos (não de conjuntos)."""
        return len(self._pai)

    def __repr__(self) -> str:
        return (
            f"UnionFind(elementos={len(self)}, conjuntos={self._numero_de_conjuntos}, "
            f"estrategia={self._estrategia!r})"
        )

    @property
    def estrategia(self) -> Estrategia:
        return self._estrategia

    @property
    def numero_de_conjuntos(self) -> int:
        """Quantidade de conjuntos disjuntos. O(1)."""
        return self._numero_de_conjuntos

    def adicionar(self) -> int:
        """Cria um novo conjunto unitário e devolve o índice do novo elemento."""
        indice = len(self._pai)
        self._pai.append(indice)
        self._tamanho.append(1)
        self._rank.append(0)
        self._numero_de_conjuntos += 1
        return indice

    # ------------------------------------------------------------ operações

    def encontrar(self, x: int) -> int:
        """Representante (raiz) do conjunto de ``x``, com compressão de caminho.

        Duas passadas, sem recursão: a primeira sobe até a raiz; a segunda
        refaz o caminho apontando cada nó direto para ela.
        """
        self._verificar(x)
        pai = self._pai
        raiz = x
        while pai[raiz] != raiz:
            raiz = pai[raiz]
        while pai[x] != raiz:
            pai[x], x = raiz, pai[x]
        return raiz

    def unir(self, a: int, b: int) -> bool:
        """Une os conjuntos de ``a`` e ``b``. Devolve ``False`` se já eram o mesmo."""
        ra, rb = self.encontrar(a), self.encontrar(b)
        if ra == rb:
            return False
        if self._estrategia == "tamanho":
            if self._tamanho[ra] < self._tamanho[rb]:
                ra, rb = rb, ra
        else:
            if self._rank[ra] < self._rank[rb]:
                ra, rb = rb, ra
            elif self._rank[ra] == self._rank[rb]:
                self._rank[ra] += 1
        # ra é a nova raiz.
        self._pai[rb] = ra
        self._tamanho[ra] += self._tamanho[rb]
        self._numero_de_conjuntos -= 1
        return True

    def conectados(self, a: int, b: int) -> bool:
        """``True`` se ``a`` e ``b`` estão no mesmo conjunto."""
        return self.encontrar(a) == self.encontrar(b)

    def tamanho_do_conjunto(self, x: int) -> int:
        """Quantidade de elementos no conjunto de ``x``."""
        return self._tamanho[self.encontrar(x)]

    def grupos(self) -> list[list[int]]:
        """Todos os conjuntos, cada um em ordem crescente, ordenados pelo menor elemento."""
        por_raiz: dict[int, list[int]] = {}
        for x in range(len(self._pai)):
            por_raiz.setdefault(self.encontrar(x), []).append(x)
        # x cresce no laço: cada lista já sai ordenada e os grupos aparecem
        # na ordem do seu menor elemento (ordem de inserção do dict).
        return list(por_raiz.values())

    def altura_maxima(self) -> int:
        """Maior profundidade atual da floresta (para estudo; não comprime). O(n)."""
        profundidade = [-1] * len(self._pai)
        maior = 0
        for x in range(len(self._pai)):
            caminho = []
            while profundidade[x] < 0 and self._pai[x] != x:
                caminho.append(x)
                x = self._pai[x]
            if profundidade[x] < 0:
                profundidade[x] = 0
            d = profundidade[x]
            for y in reversed(caminho):
                d += 1
                profundidade[y] = d
            maior = max(maior, d)
        return maior

    # ------------------------------------------------------------ auxiliares

    def _verificar(self, x: int) -> None:
        if not 0 <= x < len(self._pai):
            raise IndexError(f"elemento {x} fora do intervalo 0..{len(self._pai) - 1}")


class UnionFindGenerico(Generic[T]):
    """Union-Find sobre elementos *hashable* quaisquer (strings, tuplas, ...).

    Cada elemento novo recebe o próximo índice inteiro (``dict`` elemento ->
    índice e lista índice -> elemento) e todas as operações são delegadas a um
    :class:`UnionFind` de inteiros, que é mais rápido que ter dicionários de
    pais e tamanhos.
    """

    __slots__ = ("_elementos", "_indice", "_uf")

    def __init__(self, elementos: Iterable[T] = (), estrategia: Estrategia = "tamanho") -> None:
        self._uf = UnionFind(0, estrategia)
        self._indice: dict[T, int] = {}
        self._elementos: list[T] = []
        for e in elementos:
            self.adicionar(e)

    def __len__(self) -> int:
        return len(self._elementos)

    def __contains__(self, elemento: object) -> bool:
        return elemento in self._indice

    def __iter__(self) -> Iterator[T]:
        return iter(self._elementos)

    def __repr__(self) -> str:
        return f"UnionFindGenerico(elementos={len(self)}, conjuntos={self.numero_de_conjuntos})"

    @property
    def numero_de_conjuntos(self) -> int:
        return self._uf.numero_de_conjuntos

    def adicionar(self, elemento: T) -> bool:
        """Cria o conjunto ``{elemento}``. Devolve ``False`` se ele já existia."""
        if elemento in self._indice:
            return False
        self._indice[elemento] = self._uf.adicionar()
        self._elementos.append(elemento)
        return True

    def encontrar(self, elemento: T) -> T:
        """Representante do conjunto de ``elemento``."""
        return self._elementos[self._uf.encontrar(self._i(elemento))]

    def unir(self, a: T, b: T) -> bool:
        return self._uf.unir(self._i(a), self._i(b))

    def conectados(self, a: T, b: T) -> bool:
        return self._uf.conectados(self._i(a), self._i(b))

    def tamanho_do_conjunto(self, elemento: T) -> int:
        return self._uf.tamanho_do_conjunto(self._i(elemento))

    def grupos(self) -> list[list[T]]:
        """Conjuntos com os elementos na ordem em que foram adicionados."""
        return [[self._elementos[i] for i in g] for g in self._uf.grupos()]

    def _i(self, elemento: T) -> int:
        try:
            return self._indice[elemento]
        except KeyError:
            raise KeyError(f"elemento inexistente: {elemento!r}") from None
