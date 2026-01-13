"""
Repositório para persistência de filas de espera em JSON.
Arquivo: src/infrastructure/fila_repository.py
"""

import json
from pathlib import Path
from typing import Optional, Dict

from ..models.fila_espera import FilaEspera
from ..models.adotante import Adotante


class FilaRepository:
    """
    Repositório para gerenciar persistência de filas de espera.
    
    Attributes:
        filepath: Caminho do arquivo JSON
        _filas: Dicionário de filas indexadas por animal_id
    """
    
    def __init__(self, filepath: str = "data/filas.json"):
        """
        Inicializa o repositório.
        
        Args:
            filepath: Caminho do arquivo JSON de persistência
        """
        self.filepath = Path(filepath)
        self._filas: Dict[str, FilaEspera] = {}
        
        # Garante que o diretório existe
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
    
    def get(self, animal_id: str) -> Optional[FilaEspera]:
        """
        Busca a fila de um animal.
        
        Args:
            animal_id: ID do animal
            
        Returns:
            Fila do animal ou None
        """
        return self._filas.get(animal_id)
    
    def get_or_create(self, animal_id: str) -> FilaEspera:
        """
        Busca ou cria uma fila para um animal.
        
        Args:
            animal_id: ID do animal
            
        Returns:
            Fila do animal (existente ou nova)
        """
        if animal_id not in self._filas:
            self._filas[animal_id] = FilaEspera()
        return self._filas[animal_id]
    
    def update(self, animal_id: str, fila: FilaEspera) -> None:
        """
        Atualiza a fila de um animal.
        
        Args:
            animal_id: ID do animal
            fila: Fila atualizada
        """
        self._filas[animal_id] = fila
    
    def delete(self, animal_id: str) -> bool:
        """
        Remove a fila de um animal.
        
        Args:
            animal_id: ID do animal
            
        Returns:
            True se removida, False se não encontrada
        """
        if animal_id in self._filas:
            del self._filas[animal_id]
            return True
        return False
    
    def list_all(self) -> Dict[str, FilaEspera]:
        """
        Lista todas as filas.
        
        Returns:
            Dicionário de filas por animal_id
        """
        return self._filas.copy()
    
    def save(self) -> None:
        """Persiste as filas no arquivo JSON."""
        data = {}
        
        for animal_id, fila in self._filas.items():
            # Serializa cada adotante na fila
            fila_data = []
            for score_negativo, timestamp, adotante in fila._interessados:  # CORRIGIDO: _interessados em vez de _fila
                fila_data.append({
                    "adotante": {
                        "nome": adotante.nome,
                        "idade": adotante.idade,
                        "moradia": adotante.moradia,
                        "area_util": adotante.area_util,
                        "experiencia": adotante.experiencia,
                        "criancas": adotante.criancas,
                        "outros_animais": adotante.outros_animais,
                    },
                    "score": -score_negativo,  # Converte de volta para positivo
                    "timestamp": timestamp
                })
            
            data[animal_id] = fila_data
        
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load(self) -> None:
        """Carrega as filas do arquivo JSON."""
        if not self.filepath.exists():
            return
        
        with open(self.filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        self._filas = {}
        for animal_id, fila_data in data.items():
            fila = FilaEspera()
            
            # Reconstrói cada adotante e adiciona na fila preservando timestamp
            for item in fila_data:
                dados_adotante = item["adotante"]
                score = item["score"]
                timestamp = item.get("timestamp", 0)  # Pega timestamp se existir
                
                adotante = Adotante(
                    nome=dados_adotante["nome"],
                    idade=dados_adotante["idade"],
                    moradia=dados_adotante["moradia"],
                    area_util=dados_adotante["area_util"],
                    experiencia=dados_adotante["experiencia"],
                    criancas=dados_adotante["criancas"],
                    outros_animais=dados_adotante["outros_animais"],
                )
                
                # Adiciona diretamente no heap preservando a ordem
                import heapq
                entry = (-score, timestamp, adotante)
                heapq.heappush(fila._interessados, entry)
            
            self._filas[animal_id] = fila
    
    def __len__(self) -> int:
        """Retorna quantidade de filas."""
        return len(self._filas)
    
    def __contains__(self, animal_id: str) -> bool:
        """Verifica se existe fila para um animal."""
        return animal_id in self._filas