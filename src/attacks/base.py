"""
Classe base para todos os ataques
"""
import threading
from abc import ABC, abstractmethod
from typing import Any
from ..core.config import AttackConfig

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
    
    def _update_stats(self, bytes_sent: int, packets: int = 1):
        """Atualiza estatísticas de forma ROBUSTA"""
        try:
            # Tenta método update() primeiro
            if hasattr(self.stats_manager, 'update') and callable(self.stats_manager.update):
                self.stats_manager.update(bytes_sent, packets)
            else:
                # Fallback direto para atributos
                if hasattr(self.stats_manager, 'packets_sent'):
                    self.stats_manager.packets_sent += packets
                if hasattr(self.stats_manager, 'bytes_sent'):
                    self.stats_manager.bytes_sent += bytes_sent
        except Exception as e:
            # Em caso de erro, apenas ignora - não quebra o ataque
            pass
    
    def _handle_error(self, count: int = 1):
        """Trata erros de forma ROBUSTA"""
        try:
            if hasattr(self.stats_manager, 'increment_errors') and callable(self.stats_manager.increment_errors):
                self.stats_manager.increment_errors(count)
            elif hasattr(self.stats_manager, 'errors'):
                self.stats_manager.errors += count
        except Exception:
            # Ignora erros de estatísticas
            pass
