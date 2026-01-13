"""
Repositório para persistência de adotantes em JSON.
Arquivo: src/infrastructure/adotante_repository.py
"""

import json
from pathlib import Path
from typing import List, Optional, Iterator

from ..models.adotante import Adotante


class AdotanteRepository:
    """
    Repositório para gerenciar persistência de adotantes.
    
    Attributes:
        filepath: Caminho do arquivo JSON
        _adotantes: Dicionário de adotantes indexados por nome
    """
    
    def __init__(self, filepath: str = "data/adotantes.json"):
        """
        Inicializa o repositório.
        
        Args:
            filepath: Caminho do arquivo JSON de persistência
        """
        self.filepath = Path(filepath)
        self._adotantes: dict[str, Adotante] = {}
        
        # Garante que o diretório existe
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
    
    def add(self, adotante: Adotante) -> None:
        """
        Adiciona um adotante ao repositório.
        
        Args:
            adotante: Adotante a ser adicionado
        """
        self._adotantes[adotante.nome] = adotante
    
    def get(self, nome: str) -> Optional[Adotante]:
        """
        Busca um adotante por nome.
        
        Args:
            nome: Nome do adotante
            
        Returns:
            Adotante encontrado ou None
        """
        return self._adotantes.get(nome)
    
    def update(self, adotante: Adotante) -> None:
        """
        Atualiza os dados de um adotante.
        
        Args:
            adotante: Adotante com dados atualizados
        """
        self._adotantes[adotante.nome] = adotante
    
    def delete(self, nome: str) -> bool:
        """
        Remove um adotante do repositório.
        
        Args:
            nome: Nome do adotante a ser removido
            
        Returns:
            True se removido, False se não encontrado
        """
        if nome in self._adotantes:
            del self._adotantes[nome]
            return True
        return False
    
    def list(self) -> List[Adotante]:
        """
        Lista todos os adotantes.
        
        Returns:
            Lista de adotantes
        """
        return list(self._adotantes.values())
    
    def save(self) -> None:
        """Persiste os adotantes no arquivo JSON."""
        data = {
            nome: {
                "nome": adotante.nome,
                "idade": adotante.idade,
                "moradia": adotante.moradia,
                "area_util": adotante.area_util,
                "experiencia": adotante.experiencia,
                "criancas": adotante.criancas,
                "outros_animais": adotante.outros_animais,
            }
            for nome, adotante in self._adotantes.items()
        }
        
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load(self) -> None:
        """Carrega os adotantes do arquivo JSON."""
        if not self.filepath.exists():
            return
        
        with open(self.filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        self._adotantes = {}
        for nome, dados in data.items():
            adotante = Adotante(
                nome=dados["nome"],
                idade=dados["idade"],
                moradia=dados["moradia"],
                area_util=dados["area_util"],
                experiencia=dados["experiencia"],
                criancas=dados["criancas"],
                outros_animais=dados["outros_animais"],
            )
            self._adotantes[nome] = adotante
    
    def __len__(self) -> int:
        """Retorna quantidade de adotantes."""
        return len(self._adotantes)
    
    def __iter__(self) -> Iterator[Adotante]:
        """Permite iteração sobre os adotantes."""
        return iter(self._adotantes.values())
    
    def __contains__(self, nome: str) -> bool:
        """Verifica se um adotante existe."""
        return nome in self._adotantes