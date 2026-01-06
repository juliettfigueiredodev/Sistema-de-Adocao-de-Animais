import heapq
import time
from src.models.adotante import Adotante # Assumindo que já existe
from src.validators.exceptions import FilaVaziaError

class FilaEspera:
    def __init__(self):
        # A lista interna armazenará tuplas.
        # Ordena tuplas item por item.
        self._interessados = []

    def adicionar(self, adotante: Adotante, pontuacao: int):
        """
        Adiciona um interessado na fila.
        Prioridade 1: Maior pontuação (usando negativo pois o heapq é min-heap)
        Prioridade 2: Menor tempo (quem chega antes)
        """
        timestamp = time.time()
        # (-pontuacao) garante que a maior pontuação fique no topo do heap
        entry = (-pontuacao, timestamp, adotante)
        heapq.heappush(self._interessados, entry)
        print(f"[{adotante.nome}] entrou na fila com pontuação {pontuacao}.")

    def proximo(self) -> Adotante:
        """Retorna e remove o próximo adotante prioritário da fila."""
        if not self._interessados:
            raise FilaVaziaError("A fila de espera está vazia.")
        
        _, _, adotante = heapq.heappop(self._interessados)
        return adotante

    def espiar_proximo(self) -> Adotante:
        """Vê quem é o próximo sem remover."""
        if not self._interessados:
            return None
        return self._interessados[0][2]

    def __len__(self):
        """Requisito técnico do PDF """
        return len(self._interessados)
    
    def __str__(self):
        return f"Fila com {len(self)} interessados."