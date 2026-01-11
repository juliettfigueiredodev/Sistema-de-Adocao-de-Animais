"""
Módulo responsável pela gestão da fila de espera de adotantes.
"""

import heapq
import time
from typing import List, Optional, Tuple

from src.models.adotante import Adotante
from src.validators.exceptions import FilaVaziaError

class FilaEspera:
    """
    Implementa uma fila de prioridade para interessados na adoção.

    A prioridade é determinada por dois fatores:
    1. Pontuação (Score): Quanto maior, maior a prioridade.
    2. Tempo de chegada: Em caso de empate na pontuação, quem chegou antes
       tem prioridade (FIFO para pontuações iguais).

    Internamente, utiliza um heap (min-heap) do módulo `heapq`. Para simular
    prioridade máxima para maiores pontuações, o valor do score é armazenado
    como negativo.

    Attributes:
        _interessados: Lista interna usada como heap, armazenando tuplas no
            formato (score_negativo, timestamp, objeto_adotante).
    
    Example:
        >>> fila = FilaEspera()
        >>> fila.adicionar(adotante1, 90)
        >>> fila.adicionar(adotante2, 95)
        >>> proximo = fila.proximo()
        >>> print(proximo.nome)  # Retorna adotante2 (95 pontos)
    """

    def __init__(self)-> None:
        """Inicializa uma nova fila de espera vazia."""
        # A lista interna armazenará tuplas: (int, float, Adotante)
        self._interessados: List[Tuple[int, float, Adotante]] = []

    def adicionar(self, adotante: Adotante, pontuacao: int) -> None:
        """
        Adiciona um interessado na fila com base em sua pontuação.

        A ordem de prioridade é garantida inserindo a pontuação negativada
        no min-heap, fazendo com que o "menor" número (ex: -90 vs -80)
        fique no topo. O timestamp serve como critério de desempate.

        Args:
            adotante: O objeto Adotante a ser inserido na fila.
            pontuacao: O score de compatibilidade do adotante (0-100).
        """
        timestamp = time.time()
        # (-pontuacao) garante que a maior pontuação fique no topo do heap
        entry = (-pontuacao, timestamp, adotante)
        heapq.heappush(self._interessados, entry)
        print(f"[{adotante.nome}] entrou na fila com pontuação {pontuacao}.")

    def proximo(self) -> Adotante:
        """
        Retorna e remove o próximo adotante prioritário da fila.

        Returns:
            O objeto Adotante com a maior prioridade atual.

        Raises:
            FilaVaziaError: Se a fila estiver vazia no momento da chamada.
        """
        if not self._interessados:
            raise FilaVaziaError("A fila de espera está vazia.")
        
        # O heap remove o item com menor valor na primeira posição da tupla
        _, _, adotante = heapq.heappop(self._interessados)
        return adotante

    def espiar_proximo(self) -> Adotante:
        """
        Vê quem é o próximo adotante sem removê-lo da fila (peek).

        Returns:
            O próximo Adotante se a fila não estiver vazia, caso contrário None.
        """
        if not self._interessados:
            return None
        # O elemento no índice 0 é sempre o de maior prioridade no heap
        return self._interessados[0][2]

    def __len__(self) -> int:
        """
        Retorna o número de interessados atualmente na fila.
        
        Returns:
            Inteiro representando o tamanho da fila.
        """
        return len(self._interessados)
    
    def __str__(self)-> str:
        """
        Retorna uma representação textual amigável da fila.
        
        Returns:
            String formatada com a contagem de interessados.
        """
        return f"Fila com {len(self)} interessados."