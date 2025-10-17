"""
Classe base para todos os ataques
"""
import threading
from abc import ABC, abstractmethod
from typing import Any
from ..core.config import AttackConfig, AttackStats

class BaseAttack(ABC):
    def __init__(self, config: AttackConfig, stats_manager):
        self.config = config
        self.stats_manager = stats_manager
        self.stop_event = threading.Event()
        self.running = False
    
    @abstractmethod
    def execute(self):
        """Método principal de execução do ataque"""
        pass
    
    def stop(self):
        """Para o ataque graciosamente"""
        self.stop_event.set()
        self.running = False
    
    def _update_stats(self, bytes_sent: int):
        """Atualiza estatísticas"""
        self.stats_manager.update_stats(bytes_sent)
    
    def _handle_error(self):
        """Trata erros"""
        self.stats_manager.increment_errors()