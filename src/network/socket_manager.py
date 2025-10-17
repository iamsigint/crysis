"""
Gerenciamento inteligente de sockets
"""
import socket
import random
import time
from typing import Optional, Dict, Any
from contextlib import contextmanager

class SocketManager:
    """Gerencia criação e reutilização de sockets"""
    
    # Cache de sockets para reutilização
    _socket_cache: Dict[str, socket.socket] = {}
    
    @staticmethod
    @contextmanager
    def create_tcp_socket(timeout: float = 5.0, keepalive: bool = True):
        """Cria socket TCP com configurações otimizadas"""
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            
            if keepalive:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            
            # Otimizações para performance
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            
            yield sock
            
        except Exception as e:
            raise e
        finally:
            if sock:
                try:
                    sock.close()
                except:
                    pass
    
    @staticmethod
    @contextmanager
    def create_udp_socket(timeout: float = 2.0, buffer_size: int = 8192):
        """Cria socket UDP com configurações otimizadas"""
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(timeout)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, buffer_size)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, buffer_size)
            
            yield sock
            
        except Exception as e:
            raise e
        finally:
            if sock:
                try:
                    sock.close()
                except:
                    pass
    
    @staticmethod
    @contextmanager
    def create_ssl_socket(host: str, port: int, timeout: float = 5.0):
        """Cria socket SSL/TLS"""
        import ssl
        
        sock = None
        ssl_sock = None
        try:
            # Cria contexto SSL
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            # Cria socket TCP
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            
            # Conecta e encapsula com SSL
            sock.connect((host, port))
            ssl_sock = context.wrap_socket(sock, server_hostname=host)
            
            yield ssl_sock
            
        except Exception as e:
            raise e
        finally:
            if ssl_sock:
                try:
                    ssl_sock.close()
                except:
                    pass
            elif sock:
                try:
                    sock.close()
                except:
                    pass
    
    @staticmethod
    def create_raw_socket(protocol: int = socket.IPPROTO_TCP):
        """Cria socket raw (requer privilégios de root)"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, protocol)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
            return sock
        except PermissionError:
            raise PermissionError("Raw sockets require root privileges")
    
    @staticmethod
    def get_source_ip(target: str = "8.8.8.8", port: int = 80) -> str:
        """Obtém IP de origem do sistema"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.settimeout(2)
                sock.connect((target, port))
                return sock.getsockname()[0]
        except:
            return "127.0.0.1"
    
    @staticmethod
    def validate_connection(target: str, port: int, timeout: float = 3.0) -> bool:
        """Valida se é possível conectar ao alvo"""
        try:
            with SocketManager.create_tcp_socket(timeout) as sock:
                sock.connect((target, port))
                return True
        except:
            return False
    
    @staticmethod
    def calculate_mtu(target: str, max_mtu: int = 1500) -> int:
        """Estima MTU para o caminho até o alvo (simplificado)"""
        # Em uma implementação real, usaria ping com DF flag
        # Esta é uma versão simplificada
        common_mtus = [576, 1280, 1492, 1500, 9000]
        return min(max_mtu, random.choice(common_mtus))