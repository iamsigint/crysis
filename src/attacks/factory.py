"""
Factory para criação de ataques dinâmicos
"""
from typing import Dict, Type
from .base import BaseAttack

# Importa todos os ataques
from .tcp_attacks import (
    TCPSynFlood, TCPAckFlood, TCPFinFlood, TCPXmasAttack, TCPNullAttack
)
from .udp_attacks import UDPFlood, UDPPlainAttack
from .amplification import (
    DNSAmplification, NTPAmplification, SNMPAmplification,
    SSDPAmplification, MemcachedAmplification
)
from .application import (
    HTTPFlood, HTTPSFlood, SlowlorisAttack, WebSocketFlood, APIFlood
)
from .advanced import MixedAttack, RandomizedAttack, PulseAttack

class AttackFactory:
    _attack_registry: Dict[str, Type[BaseAttack]] = {}
    
    @classmethod
    def register_attack(cls, attack_type: str, attack_class: Type[BaseAttack]):
        """Registra uma classe de ataque"""
        cls._attack_registry[attack_type] = attack_class
    
    @classmethod
    def create_attack(cls, attack_type: str, config, stats_manager):
        """Cria uma instância de ataque"""
        if attack_type not in cls._attack_registry:
            raise ValueError(f"Tipo de ataque não suportado: {attack_type}")
        
        return cls._attack_registry[attack_type](config, stats_manager)
    
    @classmethod
    def get_available_attacks(cls):
        """Retorna lista de ataques disponíveis"""
        return list(cls._attack_registry.keys())

def register_default_attacks():
    """Registra todos os ataques padrão"""
    # TCP Attacks
    AttackFactory.register_attack("tcp_syn", TCPSynFlood)
    AttackFactory.register_attack("tcp_ack", TCPAckFlood)
    AttackFactory.register_attack("tcp_fin", TCPFinFlood)
    AttackFactory.register_attack("tcp_xmas", TCPXmasAttack)
    AttackFactory.register_attack("tcp_null", TCPNullAttack)
    
    # UDP Attacks
    AttackFactory.register_attack("udp_flood", UDPFlood)
    AttackFactory.register_attack("udp_plain", UDPPlainAttack)
    
    # Amplification Attacks
    AttackFactory.register_attack("dns_amp", DNSAmplification)
    AttackFactory.register_attack("ntp_amp", NTPAmplification)
    AttackFactory.register_attack("snmp_amp", SNMPAmplification)
    AttackFactory.register_attack("ssdp_amp", SSDPAmplification)
    AttackFactory.register_attack("memcached_amp", MemcachedAmplification)
    
    # Application Attacks
    AttackFactory.register_attack("http_flood", HTTPFlood)
    AttackFactory.register_attack("https_flood", HTTPSFlood)
    AttackFactory.register_attack("slowloris", SlowlorisAttack)
    AttackFactory.register_attack("websocket", WebSocketFlood)
    AttackFactory.register_attack("api_flood", APIFlood)
    
    # Advanced Attacks
    AttackFactory.register_attack("mixed", MixedAttack)
    AttackFactory.register_attack("randomized", RandomizedAttack)
    AttackFactory.register_attack("pulse", PulseAttack)

# Inicializa o registro
register_default_attacks()