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
        self.initialization_lock = threading.Lock()
        
        # Inicialização síncrona para evitar problemas
        self._initialize_sync()
    
    def _initialize_sync(self):
        """Inicializa o pool de proxies de forma síncrona"""
        try:
            print("⏳ Inicializando proxy manager...")
            # Aguarda o proxy_handler carregar
            time.sleep(3)
            self._refresh_proxy_pool()
            self.initialized = True
            print(f"✅ Proxy manager inicializado com {len(self.proxy_pool)} proxies")
        except Exception as e:
            print(f"❌ Erro ao inicializar proxy manager: {e}")
            self.initialized = False
    
    def _refresh_proxy_pool(self, size: int = 15):
        """Atualiza o pool de proxies ativos"""
        with self.lock:
            self.proxy_pool.clear()
            
            # Coleta proxies diretamente do handler
            if hasattr(self.proxy_handler, 'proxies') and self.proxy_handler.proxies:
                valid_proxies = self.proxy_handler.proxies[:size]
                self.proxy_pool.extend(valid_proxies)
            
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
            
        with self.lock:
            for proxy in self.proxy_pool:
                if proxy.get('type') == proxy_type:
                    return proxy
            return None
    
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
        
        with self.lock:
            total = len(self.proxy_pool)
            by_type = {}
            by_country = {}

            for proxy in self.proxy_pool:
                # Por tipo
                proxy_type = proxy.get('type', 'unknown')
                by_type[proxy_type] = by_type.get(proxy_type, 0) + 1

                # Por país
                country = proxy.get('country', 'Unknown')
                by_country[country] = by_country.get(country, 0) + 1

            return {
                'total_proxies': total,
                'by_type': by_type,
                'by_country': by_country,
                'pool_size': total,
                'current_index': self.current_index,
                'pool_proxies': [
                    f"{p.get('host', '')}:{p.get('port', '')} ({p.get('type', '')})" 
                    for p in self.proxy_pool[:5]  # Mostra apenas os primeiros 5
                ],
                'status': 'ready'
            }

# Singleton para uso global
proxy_manager = ProxyManager()
