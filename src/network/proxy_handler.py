"""
Manipulação de proxies para anonimização com carregamento dinâmico
"""
import socket
import random
import requests
import time
import threading
from typing import List, Optional, Dict
from urllib.parse import urlparse

class ProxyHandler:
    """Gerencia conexões através de proxies com carregamento dinâmico"""
    
    def __init__(self):
        self.proxies = []
        self.current_proxy = None
        self.last_update = 0
        self.update_interval = 1800  # 30 minutos
        self.lock = threading.Lock()
        self.proxy_timeout = 5  # Timeout para teste de proxy
        
        # Carrega proxies inicialmente
        self._load_proxies_from_api()
    
    def _load_proxies_from_api(self, limit: int = 100) -> bool:
        """Carrega lista de proxies da API GeoNode"""
        try:
            print("🔄 Carregando proxies da API...")
            
            url = f"https://proxylist.geonode.com/api/proxy-list?limit={limit}&page=1&sort_by=lastChecked&sort_type=desc"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            with self.lock:
                self.proxies.clear()
                
                for proxy_data in data.get('data', []):
                    proxy = self._parse_proxy_data(proxy_data)
                    if proxy:
                        self.proxies.append(proxy)
                
                self.last_update = time.time()
                
                print(f"✅ Carregados {len(self.proxies)} proxies da API")
                return True
                
        except Exception as e:
            print(f"❌ Erro ao carregar proxies da API: {e}")
            # Fallback para proxies estáticos
            self._load_fallback_proxies()
            return False
    
    def _parse_proxy_data(self, proxy_data: Dict) -> Optional[Dict]:
        """Parse dos dados da API para formato interno"""
        try:
            ip = proxy_data.get('ip', '')
            port = int(proxy_data.get('port', 0))
            protocols = proxy_data.get('protocols', [])
            
            if not ip or not port or not protocols:
                return None
            
            # Converte protocolos da API para nosso formato
            proxy_type = self._determine_proxy_type(protocols)
            if not proxy_type:
                return None
            
            # Filtra por qualidade
            latency = proxy_data.get('latency', 9999)
            uptime = proxy_data.get('upTime', 0)
            
            # Apenas proxies com boa qualidade
            if latency > 1000 or uptime < 90:
                return None
            
            return {
                'type': proxy_type,
                'host': ip,
                'port': port,
                'protocols': protocols,
                'latency': latency,
                'uptime': uptime,
                'country': proxy_data.get('country', 'Unknown'),
                'last_checked': proxy_data.get('lastChecked', 0)
            }
            
        except (ValueError, KeyError):
            return None
    
    def _determine_proxy_type(self, protocols: List[str]) -> str:
        """Determina o tipo de proxy baseado nos protocolos"""
        protocol_map = {
            'socks4': 'socks4',
            'socks5': 'socks5',
            'http': 'http',
            'https': 'http'  # Trata HTTPS como HTTP para simplificar
        }
        
        for protocol in protocols:
            if protocol in protocol_map:
                return protocol_map[protocol]
        
        return None
    
    def _load_fallback_proxies(self):
        """Carrega lista de fallback caso a API falhe"""
        fallback_proxies = [
            {'type': 'http', 'host': '45.77.136.191', 'port': 3128, 'country': 'US'},
            {'type': 'http', 'host': '138.197.157.60', 'port': 3128, 'country': 'US'},
            {'type': 'http', 'host': '167.71.5.83', 'port': 3128, 'country': 'US'},
            {'type': 'socks4', 'host': '51.83.116.5', 'port': 1080, 'country': 'EU'},
            {'type': 'socks5', 'host': '185.199.228.220', 'port': 1080, 'country': 'US'},
            {'type': 'socks5', 'host': '208.113.222.126', 'port': 64312, 'country': 'US'},
            {'type': 'http', 'host': '209.97.150.167', 'port': 3128, 'country': 'GB'},
            {'type': 'socks4', 'host': '66.42.60.80', 'port': 4145, 'country': 'US'},
        ]
        
        with self.lock:
            self.proxies = fallback_proxies
            print(f"✅ Usando {len(self.proxies)} proxies de fallback")
    
    def _should_update_proxies(self) -> bool:
        """Verifica se precisa atualizar a lista de proxies"""
        return time.time() - self.last_update > self.update_interval
    
    def get_random_proxy(self) -> Optional[Dict]:
        """Retorna proxy aleatório válido"""
        # Atualiza proxies se necessário
        if self._should_update_proxies():
            self._load_proxies_from_api()
        
        with self.lock:
            if not self.proxies:
                return None
            
            # Tenta encontrar um proxy válido
            for _ in range(min(10, len(self.proxies))):
                proxy = random.choice(self.proxies)
                if self._test_proxy(proxy):
                    return proxy
            
            # Se nenhum funcionar, retorna aleatório mesmo
            return random.choice(self.proxies)
    
    def get_best_proxy(self, proxy_type: str = None) -> Optional[Dict]:
        """Retorna o melhor proxy baseado em latência e uptime"""
        if self._should_update_proxies():
            self._load_proxies_from_api()
        
        with self.lock:
            if not self.proxies:
                return None
            
            # Filtra por tipo se especificado
            candidates = self.proxies
            if proxy_type:
                candidates = [p for p in self.proxies if p['type'] == proxy_type]
            
            if not candidates:
                return None
            
            # Ordena por latência e uptime
            candidates.sort(key=lambda x: (x.get('latency', 9999), -x.get('uptime', 0)))
            
            # Testa os melhores candidatos
            for proxy in candidates[:5]:
                if self._test_proxy(proxy):
                    return proxy
            
            return candidates[0]  # Retorna o melhor mesmo sem teste
    
    def _test_proxy(self, proxy: Dict, test_url: str = "http://httpbin.org/ip") -> bool:
        """Testa se o proxy está funcionando"""
        try:
            proxies = {
                'http': f"{proxy['type']}://{proxy['host']}:{proxy['port']}",
                'https': f"{proxy['type']}://{proxy['host']}:{proxy['port']}"
            }
            
            response = requests.get(
                test_url, 
                proxies=proxies, 
                timeout=self.proxy_timeout,
                headers={'User-Agent': 'Crysis-Proxy-Test/1.0'}
            )
            
            return response.status_code == 200
            
        except Exception:
            return False
    
    def set_proxy(self, proxy: Dict):
        """Define proxy atual"""
        self.current_proxy = proxy
    
    def clear_proxy(self):
        """Remove proxy atual"""
        self.current_proxy = None
    
    def get_proxy_stats(self) -> Dict:
        """Retorna estatísticas dos proxies"""
        with self.lock:
            total = len(self.proxies)
            by_type = {}
            by_country = {}
            
            for proxy in self.proxies:
                # Por tipo
                proxy_type = proxy['type']
                by_type[proxy_type] = by_type.get(proxy_type, 0) + 1
                
                # Por país
                country = proxy.get('country', 'Unknown')
                by_country[country] = by_country.get(country, 0) + 1
            
            return {
                'total_proxies': total,
                'by_type': by_type,
                'by_country': by_country,
                'last_update': self.last_update,
                'next_update': self.last_update + self.update_interval
            }
    
    def connect_through_proxy(self, target_host: str, target_port: int, timeout: float = 10.0):
        """Conecta ao alvo através do proxy"""
        if not self.current_proxy:
            # Conexão direta
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((target_host, target_port))
            return sock
        
        proxy = self.current_proxy
        
        if proxy['type'] == 'http':
            return self._connect_http_proxy(proxy, target_host, target_port, timeout)
        elif proxy['type'] in ['socks4', 'socks5']:
            return self._connect_socks_proxy(proxy, target_host, target_port, timeout)
        else:
            raise ValueError(f"Tipo de proxy não suportado: {proxy['type']}")
    
    def _connect_http_proxy(self, proxy: Dict, target_host: str, target_port: int, timeout: float):
        """Conecta através de proxy HTTP"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        
        try:
            # Conecta ao proxy
            sock.connect((proxy['host'], proxy['port']))
            
            # Envia requisição CONNECT
            connect_request = (
                f"CONNECT {target_host}:{target_port} HTTP/1.1\r\n"
                f"Host: {target_host}:{target_port}\r\n"
                f"Proxy-Connection: keep-alive\r\n"
                f"User-Agent: Crysis/1.0\r\n"
                f"\r\n"
            ).encode()
            
            sock.send(connect_request)
            
            # Lê resposta
            response = b""
            while b"\r\n\r\n" not in response:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response += chunk
            
            # Verifica se conexão foi estabelecida
            if b"200 Connection established" not in response:
                raise ConnectionError(f"Proxy connection failed: {response.decode()}")
            
            return sock
            
        except Exception as e:
            sock.close()
            raise e
    
    def _connect_socks_proxy(self, proxy: Dict, target_host: str, target_port: int, timeout: float):
        """Conecta através de proxy SOCKS"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        
        try:
            # Conecta ao proxy
            sock.connect((proxy['host'], proxy['port']))
            
            if proxy['type'] == 'socks4':
                self._socks4_handshake(sock, target_host, target_port)
            else:  # socks5
                self._socks5_handshake(sock, target_host, target_port)
            
            return sock
            
        except Exception as e:
            sock.close()
            raise e
    
    def _socks4_handshake(self, sock, target_host: str, target_port: int):
        """Handshake SOCKS4"""
        try:
            target_ip = socket.gethostbyname(target_host)
        except socket.gaierror:
            raise ConnectionError(f"Could not resolve host: {target_host}")
        
        # Pacote SOCKS4
        packet = bytearray()
        packet.append(0x04)  # SOCKS version
        packet.append(0x01)  # Command: CONNECT
        packet.extend(target_port.to_bytes(2, 'big'))  # Port
        packet.extend(socket.inet_aton(target_ip))  # IP
        packet.append(0x00)  # User ID (empty)
        
        sock.send(bytes(packet))
        
        # Lê resposta
        response = sock.recv(8)
        if len(response) < 8 or response[1] != 0x5A:
            raise ConnectionError("SOCKS4 connection failed")
    
    def _socks5_handshake(self, sock, target_host: str, target_port: int):
        """Handshake SOCKS5"""
        # Métodos de autenticação
        auth_packet = bytes([0x05, 0x01, 0x00])  # SOCKS5, 1 method, no auth
        sock.send(auth_packet)
        
        response = sock.recv(2)
        if response != b'\x05\x00':
            raise ConnectionError("SOCKS5 authentication failed")
        
        # Request de conexão
        request = bytearray()
        request.append(0x05)  # SOCKS version
        request.append(0x01)  # Command: CONNECT
        request.append(0x00)  # Reserved
        
        # Endereço de destino
        try:
            socket.inet_aton(target_host)
            request.append(0x01)  # IPv4
            request.extend(socket.inet_aton(target_host))
        except socket.error:
            request.append(0x03)  # Domain name
            request.append(len(target_host))
            request.extend(target_host.encode())
        
        request.extend(target_port.to_bytes(2, 'big'))
        
        sock.send(bytes(request))
        
        # Lê resposta
        response = sock.recv(10)
        if len(response) < 4 or response[1] != 0x00:
            raise ConnectionError("SOCKS5 connection failed")