"""
Sistema de menus interativos
"""
from typing import Dict, List, Any, Tuple
from ..core.config import AttackConfig, AttackType
from ..core.validator import TargetValidator

class AttackMenu:
    """Menu de seleção de ataques"""
    
    def __init__(self):
        from .banner import BannerDisplay  # Import local para evitar circular
        self.banner = BannerDisplay()
        self.validator = TargetValidator()
        self.attack_categories = self._init_attack_categories()
    
    def _init_attack_categories(self) -> Dict[str, List[Dict]]:
        """Inicializa categorias de ataque"""
        return {
            "🔷 TCP ATTACKS": [
                {"id": 1, "name": "TCP SYN Flood", "type": AttackType.TCP_SYN_FLOOD, "desc": "Classic SYN packets"},
                {"id": 2, "name": "TCP ACK Flood", "type": AttackType.TCP_ACK_FLOOD, "desc": "ACK packet storm"},
                {"id": 3, "name": "TCP RST Flood", "type": AttackType.TCP_RST_FLOOD, "desc": "Connection reset flood"},
                {"id": 4, "name": "TCP FIN Flood", "type": AttackType.TCP_FIN_FLOOD, "desc": "FIN packet barrage"},
                {"id": 5, "name": "TCP XMAS", "type": AttackType.TCP_XMAS, "desc": "FIN/URG/PSH flags"},
                {"id": 6, "name": "TCP NULL", "type": AttackType.TCP_NULL, "desc": "No flags set"}
            ],
            "🔷 UDP ATTACKS": [
                {"id": 7, "name": "UDP Flood", "type": AttackType.UDP_FLOOD, "desc": "High-speed UDP"},
                {"id": 8, "name": "UDP Plain", "type": AttackType.UDP_PLAIN, "desc": "Simple UDP packets"}
            ],
            "🔷 AMPLIFICATION ATTACKS": [
                {"id": 9, "name": "DNS Amplification", "type": AttackType.DNS_AMPLIFICATION, "desc": "DNS reflection"},
                {"id": 10, "name": "NTP Amplification", "type": AttackType.NTP_AMPLIFICATION, "desc": "NTP monlist"},
                {"id": 11, "name": "SNMP Amplification", "type": AttackType.SNMP_AMPLIFICATION, "desc": "SNMP bulk get"},
                {"id": 12, "name": "Memcached Amplification", "type": AttackType.MEMCACHED_AMP, "desc": "Stats query"},
                {"id": 13, "name": "SSDP Amplification", "type": AttackType.SSDP_AMPLIFICATION, "desc": "UPnP discovery"},
                {"id": 14, "name": "Chargen Amplification", "type": AttackType.CHARGEN_AMP, "desc": "Character generator"},
                {"id": 15, "name": "QOTD Amplification", "type": AttackType.QOTD_AMP, "desc": "Quote of the day"},
                {"id": 16, "name": "CLDAP Amplification", "type": AttackType.CLDAP_AMPLIFICATION, "desc": "Connectionless LDAP"}
            ],
            "🔷 APPLICATION LAYER": [
                {"id": 17, "name": "HTTP Flood", "type": AttackType.HTTP_FLOOD, "desc": "Web server stress"},
                {"id": 18, "name": "HTTPS Flood", "type": AttackType.HTTPS_FLOOD, "desc": "Encrypted HTTP"},
                {"id": 19, "name": "Slowloris", "type": AttackType.SLOWLORIS, "desc": "Partial connections"},
                {"id": 20, "name": "RUDY", "type": AttackType.RUDY, "desc": "Slow POST attack"},
                {"id": 21, "name": "Slow Read", "type": AttackType.SLOW_READ, "desc": "Slow response reading"},
                {"id": 22, "name": "WebSocket Flood", "type": AttackType.WEBSOCKET_FLOOD, "desc": "WS connections"}
            ],
            "🔷 PROTOCOL SPECIFIC": [
                {"id": 23, "name": "ICMP Flood", "type": AttackType.ICMP_FLOOD, "desc": "Ping flood"},
                {"id": 24, "name": "IGMP Flood", "type": AttackType.IGMP_FLOOD, "desc": "Multicast flood"}
            ],
            "🔷 ADVANCED TECHNIQUES": [
                {"id": 25, "name": "Mixed Attack", "type": AttackType.MIXED_ATTACK, "desc": "Multiple vectors"},
                {"id": 26, "name": "Randomized Attack", "type": AttackType.RANDOMIZED, "desc": "AI-powered patterns"},
                {"id": 27, "name": "Pulse Attack", "type": AttackType.PULSE_ATTACK, "desc": "Wave-based flooding"},
                {"id": 28, "name": "IP Spoofing", "type": AttackType.IP_SPOOFING, "desc": "Source IP randomization"},
                {"id": 29, "name": "Proxy Chain", "type": AttackType.PROXY_ATTACK, "desc": "Multi-proxy routing"}
            ],
            "🔷 WEB APPLICATION": [
                {"id": 30, "name": "API Flood", "type": AttackType.API_FLOOD, "desc": "REST API stress"},
                {"id": 31, "name": "XML-RPC Flood", "type": AttackType.XML_RPC_FLOOD, "desc": "WordPress/RPC attack"}
            ]
        }
    
    def display_main_menu(self):
        """Exibe menu principal de ataques"""
        self.banner.show()
        
        print(f"\n{'='*80}")
        print(f"🎯 ELITE ATTACK SELECTION - CHOOSE YOUR WEAPON:")
        print(f"{'='*80}")
        
        for category, attacks in self.attack_categories.items():
            print(f"\n{category}:")
            for attack in attacks:
                print(f"  {attack['id']:2d}. {attack['name']:<25} - {attack['desc']}")
        
        print(f"\n{'='*80}")
    
    def get_attack_config(self) -> AttackConfig:
        """Obtém configuração completa do usuário"""
        self.display_main_menu()
        
        # Seleção do tipo de ataque
        attack_id = self._get_attack_choice()
        attack_type = self._get_attack_type(attack_id)
        
        # Informações do alvo
        target_ip = self._get_target_ip()
        target_port = self._get_target_port(attack_type)
        
        # Parâmetros do ataque
        duration = self._get_duration()
        threads = self._get_threads()
        packet_size = self._get_packet_size()
        
        # Features avançadas
        spoof_ip = self._get_boolean_setting("Use IP Spoofing")
        use_proxy, proxy_type = self._get_proxy_settings()
        randomize = self._get_boolean_setting("Randomize packets")
        
        return AttackConfig(
            target_ip=target_ip,
            target_port=target_port,
            attack_type=attack_type,
            duration=duration,
            threads=threads,
            packet_size=packet_size,
            spoof_ip=spoof_ip,
            use_proxy=use_proxy,
            randomize_packets=randomize,
            proxy_type=proxy_type  # Novo campo para tipo de proxy
        )
    
    def _safe_input(self, prompt: str) -> str:
        """Input seguro que trata Ctrl+C"""
        try:
            return input(prompt)
        except (KeyboardInterrupt, EOFError):
            print("\n⏹️  Operation cancelled.")
            raise
    
    def _get_proxy_settings(self) -> Tuple[bool, str]:
        """Obtém configurações de proxy"""
        print(f"\n🔗 CONFIGURAÇÕES DE PROXY:")
        
        try:
            use_proxy = self._get_boolean_setting("Usar Proxy Chain")
        except (KeyboardInterrupt, EOFError):
            return False, None
        
        proxy_type = None
        
        if use_proxy:
            print(f"\n🎯 Tipos de Proxy disponíveis:")
            print("  1. Aleatório (melhor disponível)")
            print("  2. HTTP/HTTPS")
            print("  3. SOCKS4")
            print("  4. SOCKS5")
            
            while True:
                try:
                    choice = self._safe_input("Selecione tipo de proxy (1-4): ").strip()
                    proxy_types = {
                        '1': 'random',    # Aleatório
                        '2': 'http',      # HTTP/HTTPS
                        '3': 'socks4',    # SOCKS4
                        '4': 'socks5'     # SOCKS5
                    }
                    if choice in proxy_types:
                        proxy_type = proxy_types[choice]
                        
                        # Mostra informações dos proxies disponíveis
                        self._show_proxy_info(proxy_type)
                        break
                    else:
                        print("❌ Escolha inválida! Digite 1, 2, 3 ou 4.")
                except (KeyboardInterrupt, EOFError):
                    print("\n⏹️  Operation cancelled.")
                    return False, None
                except ValueError:
                    print("❌ Entrada inválida!")
        
        return use_proxy, proxy_type
    
    def _show_proxy_info(self, proxy_type: str):
        """Mostra informações sobre os proxies disponíveis"""
        try:
            from ..utils.proxy_manager import proxy_manager
            
            proxy_info = proxy_manager.get_proxy_info()
            total_proxies = proxy_info['total_proxies']
            
            if total_proxies > 0:
                print(f"✅ {total_proxies} proxies disponíveis")
                
                # Mostra estatísticas por tipo
                if proxy_type == 'random':
                    print("📊 Distribuição por tipo:")
                    for p_type, count in proxy_info['by_type'].items():
                        print(f"   • {p_type.upper()}: {count} proxies")
                
                # Mostra alguns países
                countries = list(proxy_info['by_country'].items())[:5]
                if countries:
                    print("🌍 Principais países:")
                    for country, count in countries:
                        print(f"   • {country}: {count} proxies")
                
                print(f"🔄 Próxima atualização: em {self._format_time_remaining(proxy_info['next_update'])}")
            else:
                print("⚠️  Nenhum proxy disponível no momento")
                
        except Exception as e:
            print(f"⚠️  Não foi possível carregar informações dos proxies: {e}")
    
    def _format_time_remaining(self, next_update: float) -> str:
        """Formata tempo restante para próxima atualização"""
        import time
        remaining = next_update - time.time()
        
        if remaining <= 0:
            return "agora"
        elif remaining < 60:
            return f"{int(remaining)} segundos"
        elif remaining < 3600:
            return f"{int(remaining/60)} minutos"
        else:
            return f"{int(remaining/3600)} horas"
    
    def _get_attack_choice(self) -> int:
        """Obtém escolha do tipo de ataque"""
        while True:
            try:
                choice = self._safe_input(f"\n🎲 Select attack type (1-31): ").strip()
                attack_id = int(choice)
                
                if 1 <= attack_id <= 31:
                    return attack_id
                else:
                    print("❌ Please enter a number between 1 and 31")
                    
            except (KeyboardInterrupt, EOFError):
                print("\n⏹️  Operation cancelled.")
                raise
            except ValueError:
                print("❌ Please enter a valid number")
    
    def _get_attack_type(self, attack_id: int) -> AttackType:
        """Mapeia ID para tipo de ataque"""
        for category in self.attack_categories.values():
            for attack in category:
                if attack['id'] == attack_id:
                    return attack['type']
        
        return AttackType.MIXED_ATTACK
    
    def _get_target_ip(self) -> str:
        """Obtém IP/domínio do alvo"""
        while True:
            try:
                target = self._safe_input(f"\n🎯 Target IP/Domain: ").strip()
                
                if self.validator.validate_target(target):
                    return target
                else:
                    print("❌ Invalid target! Please check the IP/domain")
            except (KeyboardInterrupt, EOFError):
                print("\n⏹️  Operation cancelled.")
                raise
    
    def _get_target_port(self, attack_type: AttackType) -> int:
        """Obtém porta do alvo com base no tipo de ataque"""
        default_ports = {
            AttackType.DNS_AMPLIFICATION: 53,
            AttackType.NTP_AMPLIFICATION: 123,
            AttackType.SNMP_AMPLIFICATION: 161,
            AttackType.SSDP_AMPLIFICATION: 1900,
            AttackType.MEMCACHED_AMP: 11211,
            AttackType.CHARGEN_AMP: 19,
            AttackType.QOTD_AMP: 17,
            AttackType.CLDAP_AMPLIFICATION: 389,
            AttackType.HTTP_FLOOD: 80,
            AttackType.HTTPS_FLOOD: 443,
            AttackType.SLOWLORIS: 80,
            AttackType.WEBSOCKET_FLOOD: 80,
            AttackType.API_FLOOD: 80,
            AttackType.XML_RPC_FLOOD: 80
        }
        
        default_port = default_ports.get(attack_type, 80)
        
        while True:
            try:
                port_input = self._safe_input(f"🔌 Target port [default: {default_port}]: ").strip()
                
                if not port_input:
                    return default_port
                
                port = int(port_input)
                if 1 <= port <= 65535:
                    return port
                else:
                    print("❌ Port must be between 1-65535")
                    
            except (KeyboardInterrupt, EOFError):
                print("\n⏹️  Operation cancelled.")
                raise
            except ValueError:
                print("❌ Please enter a valid port number")
    
    def _get_duration(self) -> int:
        """Obtém duração do ataque"""
        while True:
            try:
                duration = self._safe_input(f"⏰ Duration (seconds): ").strip()
                duration_int = int(duration)
                
                if duration_int > 0:
                    return duration_int
                else:
                    print("❌ Duration must be positive")
                    
            except (KeyboardInterrupt, EOFError):
                print("\n⏹️  Operation cancelled.")
                raise
            except ValueError:
                print("❌ Please enter a valid number")
    
    def _get_threads(self) -> int:
        """Obtém número de threads"""
        while True:
            try:
                threads = self._safe_input(f"🧵 Number of threads (1-1000): ").strip()
                threads_int = int(threads)
                
                if 1 <= threads_int <= 1000:
                    return threads_int
                else:
                    print("❌ Threads must be between 1-1000")
                    
            except (KeyboardInterrupt, EOFError):
                print("\n⏹️  Operation cancelled.")
                raise
            except ValueError:
                print("❌ Please enter a valid number")
    
    def _get_packet_size(self) -> int:
        """Obtém tamanho do pacote"""
        while True:
            try:
                size = self._safe_input(f"📦 Packet size (bytes, 1-65535): ").strip()
                size_int = int(size)
                
                if 1 <= size_int <= 65535:
                    return size_int
                else:
                    print("❌ Size must be between 1-65535")
                    
            except (KeyboardInterrupt, EOFError):
                print("\n⏹️  Operation cancelled.")
                raise
            except ValueError:
                print("❌ Please enter a valid number")
    
    def _get_boolean_setting(self, setting_name: str) -> bool:
        """Obtém configuração booleana do usuário"""
        while True:
            try:
                response = self._safe_input(f"🔧 {setting_name}? (y/n): ").strip().lower()
                
                if response in ['y', 'yes', 's', 'sim']:
                    return True
                elif response in ['n', 'no', 'não']:
                    return False
                else:
                    print("❌ Please enter 'y' or 'n'")
            except (KeyboardInterrupt, EOFError):
                print("\n⏹️  Operation cancelled.")
                raise