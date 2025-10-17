"""
Gerenciador avançado de proxies
"""
import time
import threading
from typing import List, Dict, Optional
from ..network.proxy_handler import ProxyHandler

class ProxyManager:
    """Gerencia múltiplos proxies com balanceamento de carga"""
    
    def __init__(self):
        self.proxy_handler = ProxyHandler()
        self.proxy_pool = []
        self.current_index = 0
        self.lock = threading.Lock()
        self.initialized = False
        
        # Inicializa o pool em thread separada para não travar
        self._initialize_async()
    
    def _initialize_async(self):
        """Inicializa o pool de proxies de forma assíncrona"""
        def init_thread():
            try:
                self._refresh_proxy_pool()
                self.initialized = True
                print("✅ Proxy manager inicializado")
            except Exception as e:
                print(f"❌ Erro ao inicializar proxy manager: {e}")
                self.initialized = False
        
        thread = threading.Thread(target=init_thread, daemon=True)
        thread.start()
    
    def _refresh_proxy_pool(self, size: int = 20):
        """Atualiza o pool de proxies ativos"""
        with self.lock:
            self.proxy_pool.clear()
            
            # Coleta os melhores proxies
            collected = 0
            max_attempts = size * 2  # Limite de tentativas
            
            for _ in range(max_attempts):
                if collected >= size:
                    break
                    
                proxy = self.proxy_handler.get_best_proxy()
                if proxy and proxy not in self.proxy_pool:
                    self.proxy_pool.append(proxy)
                    collected += 1
            
            print(f"🔄 Pool de proxies atualizado: {len(self.proxy_pool)} proxies ativos")
    
    def get_next_proxy(self) -> Optional[Dict]:
        """Retorna próximo proxy no pool (round-robin)"""
        if not self.initialized:
            return None
            
        with self.lock:
            if not self.proxy_pool:
                return None
            
            proxy = self.proxy_pool[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.proxy_pool)
            return proxy
    
    def get_proxy_by_type(self, proxy_type: str) -> Optional[Dict]:
        """Retorna proxy específico por tipo"""
        if not self.initialized:
            return None
        return self.proxy_handler.get_best_proxy(proxy_type)
    
    def mark_proxy_failed(self, proxy: Dict):
        """Marca um proxy como falho e remove do pool"""
        with self.lock:
            if proxy in self.proxy_pool:
                self.proxy_pool.remove(proxy)
                print(f"🗑️ Proxy {proxy['host']}:{proxy['port']} removido do pool")
    
    def get_proxy_info(self) -> Dict:
        """Retorna informações detalhadas sobre os proxies"""
        if not self.initialized:
            return {
                'total_proxies': 0,
                'by_type': {},
                'by_country': {},
                'pool_size': 0,
                'current_index': 0,
                'pool_proxies': [],
                'status': 'initializing'
            }
        
        stats = self.proxy_handler.get_proxy_stats()
        
        with self.lock:
            stats['pool_size'] = len(self.proxy_pool)
            stats['current_index'] = self.current_index
            stats['pool_proxies'] = [
                f"{p['host']}:{p['port']} ({p['type']})" 
                for p in self.proxy_pool[:10]  # Mostra apenas os primeiros 10
            ]
            stats['status'] = 'ready'
        
        return stats

# Singleton para uso global
proxy_manager = ProxyManager()