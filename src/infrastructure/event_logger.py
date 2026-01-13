"""
Sistema de Log de Eventos usando Observer Pattern.
Arquivo: src/infrastructure/event_logger.py
"""

from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import List, Optional


class Observer(ABC):
    """Interface do Observer - quem vai receber notificações de eventos."""
    
    @abstractmethod
    def update(self, evento: str, dados: dict) -> None:
        """Método chamado quando um evento ocorre."""
        pass


class EventSubject:
    """
    Subject do padrão Observer.
    Notifica todos os observers registrados quando eventos ocorrem.
    """
    
    def __init__(self):
        self._observers: List[Observer] = []
    
    def attach(self, observer: Observer) -> None:
        """Registra um observer para receber notificações."""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer: Observer) -> None:
        """Remove um observer."""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify(self, evento: str, dados: dict) -> None:
        """Notifica todos os observers sobre um evento."""
        for observer in self._observers:
            observer.update(evento, dados)


class FileLogger(Observer):
    """
    Observer concreto que salva logs em arquivo.
    """
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "sistema.log"
    
    def update(self, evento: str, dados: dict) -> None:
        """Salva evento no arquivo de log."""
        timestamp = datetime.now().isoformat()
        
        # Salva em formato legível
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {evento}\n")
            for key, value in dados.items():
                f.write(f"  {key}: {value}\n")
            f.write("-" * 80 + "\n")


class ConsoleLogger(Observer):
    """
    Observer concreto que exibe logs no console (opcional).
    """
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
    
    def update(self, evento: str, dados: dict) -> None:
        """Exibe evento no console se verbose=True."""
        if self.verbose:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[LOG {timestamp}] {evento}: {dados}")


class EventLogger:
    """
    Singleton que gerencia o sistema de logs.
    Fornece interface simples para registrar eventos.
    """
    
    _instance: Optional['EventLogger'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.subject = EventSubject()
        
        # Adiciona logger de arquivo por padrão
        self.file_logger = FileLogger()
        self.subject.attach(self.file_logger)
        
        # Console logger desabilitado por padrão (não polui terminal)
        self.console_logger = ConsoleLogger(verbose=False)
        self.subject.attach(self.console_logger)
        
        self._initialized = True
    
    def log(self, evento: str, **kwargs) -> None:
        """
        Registra um evento com dados adicionais.
        
        Args:
            evento: Nome/tipo do evento
            **kwargs: Dados adicionais sobre o evento
        """
        self.subject.notify(evento, kwargs)
    
    def enable_console(self) -> None:
        """Ativa logs no console."""
        self.console_logger.verbose = True
    
    def disable_console(self) -> None:
        """Desativa logs no console."""
        self.console_logger.verbose = False


# Instância global do logger (Singleton)
logger = EventLogger()