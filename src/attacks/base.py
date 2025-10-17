"""
Classe base para todos os ataques - CORREÇÃO URGENTE
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
        """Atualiza estatísticas de forma precisa - CORRIGIDO"""
        if hasattr(self.stats_manager, 'update'):
            self.stats_manager.update(bytes_sent, packets)
        else:
            # Fallback para compatibilidade
            print(f"⚠️  AVISO: stats_manager não tem método update()")
    
    def _handle_error(self, count: int = 1):
        """Trata erros de forma mais eficiente - CORRIGIDO"""
        if hasattr(self.stats_manager, 'increment_errors'):
            self.stats_manager.increment_errors(count)
