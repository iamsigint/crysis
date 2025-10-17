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
import concurrent.futures

class ProxyHandler:
    """Gerencia conexões através de proxies com carregamento dinâmico"""

    def __init__(self):
        self.proxies = []
        self.current_proxy = None
        self.last_update = 0
        self.update_interval = 1800  # 30 minutos
        self.lock = threading.Lock()
        self.proxy_timeout = 2  # Timeout reduzido
        self.max_proxies = 20   # Limite máximo de proxies

        # Carrega proxies inicialmente de forma assíncrona
        self._load_proxies_async()

    def _load_proxies_async(self):
        """Carrega proxies em thread separada"""
        def load():
            try:
                self._load_proxies_from_api()
            except Exception as e:
                print(f"❌ Erro ao carregar proxies: {e}")
                self._load_fallback_proxies()
        
        thread = threading.Thread(target=load, daemon=True)
        thread.start()

    def _load_proxies_from_api(self, limit: int = 100) -> bool:
        """Carrega lista de proxies da API GeoNode de forma otimizada"""
        try:
            print("🔄 Carregando proxies da API...")

            url = f"https://proxylist.geonode.com/api/proxy-list?limit={limit}&page=1&sort_by=lastChecked&sort_type=desc&speed=fast"

            response = requests.get(url, timeout=15)
            response.raise_for_status()

            data = response.json()

            all_proxies = []
            for proxy_data in data.get('data', []):
                proxy = self._parse_proxy_data(proxy_data)
                if proxy:
                    all_proxies.append(proxy)

            print(f"📥 {len(all_proxies)} proxies encontrados, testando...")

            # Teste em paralelo - MUITO MAIS RÁPIDO
            valid_proxies = self._test_proxies_parallel(all_proxies[:30])  # Testa apenas os 30 primeiros

            with self.lock:
                self.proxies = valid_proxies
                self.last_update = time.time()

            print(f"✅ {len(valid_proxies)} proxies válidos carregados")
            return len(valid_proxies) > 0

        except Exception as e:
            print(f"❌ Erro API: {e}")
            self._load_fallback_proxies()
            return False

    def _test_proxies_parallel(self, proxies: List[Dict]) -> List[Dict]:
        """Testa múltiplos proxies em paralelo"""
        def test_proxy(proxy):
            if self._test_proxy_fast(proxy):
                return proxy
            return None

        valid_proxies = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(test_proxy, proxy) for proxy in proxies]
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    valid_proxies.append(result)

        return valid_proxies

    def _test_proxy_fast(self, proxy: Dict) -> bool:
        """Teste RÁPIDO de proxy usando socket direto"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1.5)  # Timeout MUITO curto
            sock.connect((proxy['host'], proxy['port']))
            sock.close()
            return True
        except:
            return False

    def _parse_proxy_data(self, proxy_data: Dict) -> Optional[Dict]:
        """Parse rápido dos dados da API"""
        try:
            ip = proxy_data.get('ip', '').strip()
            port = int(proxy_data.get('port', 0))
            protocols = proxy_data.get('protocols', [])

            if not ip or port <= 0 or port > 65535 or not protocols:
                return None

            # Filtra apenas proxies rápidos
            latency = proxy_data.get('latency', 9999)
            uptime = proxy_data.get('upTime', 0)

            if latency > 2000 or uptime < 80:  # Critérios mais rigorosos
                return None

            proxy_type = self._determine_proxy_type(protocols)
            if not proxy_type:
                return None

            return {
                'type': proxy_type,
                'host': ip,
                'port': port,
                'latency': latency,
                'uptime': uptime,
                'country': proxy_data.get('country', 'Unknown')
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
        ]

        with self.lock:
            # Testa cada proxy de fallback
            self.proxies = [p for p in fallback_proxies if self._test_proxy_fast(p)]
            print(f"✅ Usando {len(self.proxies)} proxies de fallback")

    def _should_update_proxies(self) -> bool:
        """Verifica se precisa atualizar a lista de proxies"""
        return time.time() - self.last_update > self.update_interval

    def get_random_proxy(self) -> Optional[Dict]:
        """Retorna proxy aleatório válido"""
        # Atualiza proxies se necessário
        if self._should_update_proxies():
            self._load_proxies_async()

        with self.lock:
            if not self.proxies:
                return None

            # Tenta encontrar um proxy válido
            for _ in range(min(5, len(self.proxies))):
                proxy = random.choice(self.proxies)
                if self._test_proxy_fast(proxy):
                    return proxy

            # Se nenhum funcionar, retorna aleatório mesmo
            return random.choice(self.proxies)

    def get_best_proxy(self, proxy_type: str = None) -> Optional[Dict]:
        """Retorna o melhor proxy baseado em latência e uptime"""
        if self._should_update_proxies():
            self._load_proxies_async()

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
            for proxy in candidates[:3]:
                if self._test_proxy_fast(proxy):
                    return proxy

            return candidates[0]  # Retorna o melhor mesmo sem teste

    def _test_proxy(self, proxy: Dict, test_url: str = "http://httpbin.org/ip") -> bool:
        """Testa se o proxy está funcionando com requests"""
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
