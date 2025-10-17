"""
Módulo de ataques - importa todas as classes de ataque
"""
from .tcp_attacks import (
    TCPSynFlood, TCPAckFlood, TCPFinFlood, 
    TCPXmasAttack, TCPNullAttack
)
from .udp_attacks import UDPFlood, UDPPlainAttack
from .amplification import (
    DNSAmplification, NTPAmplification, SNMPAmplification,
    SSDPAmplification, MemcachedAmplification
)
from .application import (
    HTTPFlood, HTTPSFlood, SlowlorisAttack,
    WebSocketFlood, APIFlood
)
from .advanced import MixedAttack, RandomizedAttack, PulseAttack

__all__ = [
    # TCP Attacks
    'TCPSynFlood', 'TCPAckFlood', 'TCPFinFlood', 
    'TCPXmasAttack', 'TCPNullAttack',
    
    # UDP Attacks  
    'UDPFlood', 'UDPPlainAttack',
    
    # Amplification
    'DNSAmplification', 'NTPAmplification', 'SNMPAmplification',
    'SSDPAmplification', 'MemcachedAmplification',
    
    # Application
    'HTTPFlood', 'HTTPSFlood', 'SlowlorisAttack',
    'WebSocketFlood', 'APIFlood',
    
    # Advanced
    'MixedAttack', 'RandomizedAttack', 'PulseAttack'
]