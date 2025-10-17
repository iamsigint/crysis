"""
Configurações e modelos de dados
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any

class AttackType(Enum):
    # TCP Attacks
    TCP_SYN_FLOOD = "tcp_syn"
    TCP_ACK_FLOOD = "tcp_ack"
    TCP_RST_FLOOD = "tcp_rst"
    TCP_FIN_FLOOD = "tcp_fin"
    TCP_XMAS = "tcp_xmas"
    TCP_NULL = "tcp_null"
    
    # UDP Attacks
    UDP_FLOOD = "udp_flood"
    UDP_PLAIN = "udp_plain"
    
    # Amplification Attacks
    DNS_AMPLIFICATION = "dns_amp"
    NTP_AMPLIFICATION = "ntp_amp"
    SNMP_AMPLIFICATION = "snmp_amp"
    SSDP_AMPLIFICATION = "ssdp_amp"
    MEMCACHED_AMP = "memcached_amp"
    CHARGEN_AMP = "chargen_amp"
    QOTD_AMP = "qotd_amp"
    CLDAP_AMPLIFICATION = "cldap_amp"
    
    # Application Layer
    HTTP_FLOOD = "http_flood"
    HTTPS_FLOOD = "https_flood"
    SLOWLORIS = "slowloris"
    RUDY = "rudy"
    SLOW_READ = "slow_read"
    
    # Protocol Specific
    ICMP_FLOOD = "icmp_flood"
    IGMP_FLOOD = "igmp_flood"
    
    # Advanced Techniques
    MIXED_ATTACK = "mixed"
    RANDOMIZED = "randomized"
    PULSE_ATTACK = "pulse"
    IP_SPOOFING = "ip_spoof"
    PROXY_ATTACK = "proxy_chain"
    
    # Web Application
    WEBSOCKET_FLOOD = "websocket"
    API_FLOOD = "api_flood"
    XML_RPC_FLOOD = "xml_rpc"

@dataclass
class AttackConfig:
    target_ip: str
    target_port: int
    attack_type: AttackType
    duration: int
    threads: int
    packet_size: int
    rate_limit: Optional[int] = None
    use_proxy: bool = False
    spoof_ip: bool = False
    randomize_packets: bool = False
    proxy_type: Optional[str] = None  # Novo campo: 'random', 'http', 'socks4', 'socks5'

@dataclass
class AttackStats:
    packets_sent: int = 0
    bytes_sent: int = 0
    errors: int = 0
    start_time: Optional[float] = None
    amplification_factor: float = 0.0
    success_rate: float = 100.0
    