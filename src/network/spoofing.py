"""
Técnicas de IP spoofing
"""
import random
import socket
import struct
from typing import List

class IPSpoofer:
    """Gerencia spoofing de endereços IP"""
    
    def __init__(self):
        self.public_ranges = self._load_public_ranges()
    
    def _load_public_ranges(self) -> List[str]:
        """Carrega ranges de IP públicos para spoofing"""
        return [
            "1.0.0.0/8", "2.0.0.0/8", "3.0.0.0/8", "4.0.0.0/6",
            "8.0.0.0/7", "11.0.0.0/8", "12.0.0.0/6", "16.0.0.0/4",
            "32.0.0.0/3", "64.0.0.0/2", "128.0.0.0/3", "160.0.0.0/5",
            "168.0.0.0/6", "172.0.0.0/12", "173.0.0.0/8", "174.0.0.0/7",
            "176.0.0.0/5", "184.0.0.0/6", "188.0.0.0/8", "189.0.0.0/9",
            "190.0.0.0/7", "192.0.0.0/9", "192.128.0.0/11", "192.160.0.0/13",
            "192.169.0.0/16", "192.170.0.0/15", "192.172.0.0/14", "192.176.0.0/12",
            "192.192.0.0/10", "193.0.0.0/8", "194.0.0.0/7", "196.0.0.0/6",
            "200.0.0.0/7", "202.0.0.0/7", "204.0.0.0/6", "208.0.0.0/4"
        ]
    
    def generate_spoofed_ip(self) -> str:
        """Gera IP aleatório para spoofing"""
        range_str = random.choice(self.public_ranges)
        network, prefix = range_str.split('/')
        prefix_len = int(prefix)
        
        # Converte network para inteiro
        network_int = self._ip_to_int(network)
        
        # Calcula máscara
        mask = (1 << 32) - (1 << (32 - prefix_len))
        
        # Gera IP aleatório dentro do range
        random_ip_int = network_int + random.randint(1, (1 << (32 - prefix_len)) - 2)
        random_ip_int &= mask
        random_ip_int |= network_int
        
        return self._int_to_ip(random_ip_int)
    
    def _ip_to_int(self, ip: str) -> int:
        """Converte IP string para inteiro"""
        return struct.unpack("!I", socket.inet_aton(ip))[0]
    
    def _int_to_ip(self, ip_int: int) -> str:
        """Converte inteiro para IP string"""
        return socket.inet_ntoa(struct.pack("!I", ip_int))
    
    def create_spoofed_packet(self, source_ip: str, dest_ip: str, dest_port: int, 
                            protocol: str = 'tcp', payload: bytes = b'') -> bytes:
        """Cria pacote com IP spoofed (simplificado)"""
        # Em uma implementação real, isso criaria pacotes IP raw
        # Esta é uma versão simplificada para demonstração
        
        if protocol.lower() == 'tcp':
            return self._create_spoofed_tcp_packet(source_ip, dest_ip, dest_port, payload)
        elif protocol.lower() == 'udp':
            return self._create_spoofed_udp_packet(source_ip, dest_ip, dest_port, payload)
        else:
            raise ValueError(f"Protocolo não suportado: {protocol}")
    
    def _create_spoofed_tcp_packet(self, source_ip: str, dest_ip: str, dest_port: int, payload: bytes) -> bytes:
        """Cria pacote TCP spoofed"""
        source_port = random.randint(1024, 65535)
        
        # Cabeçalho TCP simplificado
        tcp_header = struct.pack(
            '!HHIIBBHHH',
            source_port, dest_port,  # Portas
            random.randint(0, 4294967295),  # Seq number
            0,  # Ack number
            5 << 4,  # Data offset
            0x02,  # SYN flag
            8192,  # Window
            0,  # Checksum
            0   # Urgent pointer
        )
        
        return tcp_header + payload
    
    def _create_spoofed_udp_packet(self, source_ip: str, dest_ip: str, dest_port: int, payload: bytes) -> bytes:
        """Cria pacote UDP spoofed"""
        source_port = random.randint(1024, 65535)
        length = 8 + len(payload)
        
        # Cabeçalho UDP
        udp_header = struct.pack('!HHHH', source_port, dest_port, length, 0)
        
        return udp_header + payload
    
    def validate_spoofing_capability(self) -> bool:
        """Valida se o sistema suporta IP spoofing"""
        try:
            # Tenta criar socket raw (requer privilégios)
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
            sock.close()
            return True
        except (PermissionError, OSError):
            return False