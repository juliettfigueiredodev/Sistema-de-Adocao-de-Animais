"""
Módulo responsável por carregar configurações do sistema.
"""

import json
from pathlib import Path
from typing import Dict, Optional, ClassVar


class SettingsLoader:
    """
    Carrega e gerencia as configurações do sistema a partir de settings.json.
    
    Implementa o padrão Singleton para garantir uma única instância
    e evitar múltiplas leituras do arquivo.
    
    Attributes:
        _instance: Instância única da classe (Singleton).
        _settings: Configurações carregadas em cache.
    
    Example:
        >>> settings = SettingsLoader.carregar()
        >>> idade_min = settings["politicas"]["idade_minima"]
    """
    
    _instance: ClassVar[Optional['SettingsLoader']] = None
    _settings: ClassVar[Optional[Dict]] = None
    
    def __new__(cls) -> 'SettingsLoader':
        """
        Garante que apenas uma instância da classe exista (Singleton).
        
        Returns:
            A instância única de SettingsLoader.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def carregar(cls, caminho: str = "settings.json") -> Dict:
        """
        Carrega as configurações do arquivo JSON.
        
        O arquivo é lido apenas uma vez e mantido em cache.
        Para forçar recarga, use o método recarregar().
        
        Args:
            caminho: Caminho relativo ou absoluto para o arquivo de configurações.
        
        Returns:
            Dicionário contendo todas as configurações do sistema.
        
        Raises:
            FileNotFoundError: Se o arquivo não for encontrado.
            json.JSONDecodeError: Se o arquivo contiver JSON inválido.
        
        Example:
            >>> config = SettingsLoader.carregar()
            >>> print(config["politicas"]["idade_minima"])
            18
        """
        # Cache: carrega apenas uma vez
        if cls._settings is None:
            arquivo_path = Path(caminho)
            
            if not arquivo_path.exists():
                raise FileNotFoundError(
                    f"Arquivo de configurações não encontrado: {caminho}"
                )
            
            try:
                with open(arquivo_path, "r", encoding="utf-8") as arquivo:
                    cls._settings = json.load(arquivo)
            except json.JSONDecodeError as e:
                raise json.JSONDecodeError(
                    f"Erro ao decodificar JSON em {caminho}: {e.msg}",
                    e.doc,
                    e.pos
                )
        
        return cls._settings
    
    @classmethod
    def recarregar(cls, caminho: str = "settings.json") -> Dict:
        """
        Força a recarga das configurações do arquivo.
        
        Útil para testes ou quando o arquivo é modificado em runtime.
        
        Args:
            caminho: Caminho para o arquivo de configurações.
        
        Returns:
            Dicionário com as configurações recarregadas.
        """
        cls._settings = None
        return cls.carregar(caminho)
    
    def __repr__(self) -> str:
        """Representação técnica do loader."""
        carregado = "carregado" if self._settings else "não carregado"
        return f"SettingsLoader(status={carregado})"