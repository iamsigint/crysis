"""
Medidas de segurança e verificação de permissões
"""
import os
import sys
import socket
import hashlib
import getpass
from typing import Dict, List, Optional

class SecurityManager:
    """Gerencia aspectos de segurança do sistema"""
    
    def __init__(self):
        self.allowed_targets = self._load_allowed_targets()
        self.checksum_cache = {}
    
    def _load_allowed_targets(self) -> List[str]:
        """Carrega lista de alvos permitidos (para testes autorizados)"""
        # Em ambiente real, isso viria de configuração
        return [
            "127.0.0.1",
            "localhost",
            "test.example.com",
            "192.168.1.1"
        ]
    
    def validate_environment(self) -> Dict[str, bool]:
        """Valida ambiente de execução"""
        checks = {
            'running_as_root': os.geteuid() == 0,
            'raw_sockets_available': self._check_raw_sockets(),
            'network_access': self._check_network_access(),
            'sufficient_privileges': self._check_privileges(),
            'target_authorization': True  # Será validado por alvo
        }
        
        return checks
    
    def _check_raw_sockets(self) -> bool:
        """Verifica se sockets raw estão disponíveis"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
            sock.close()
            return True
        except (PermissionError, OSError):
            return False
    
    def _check_network_access(self) -> bool:
        """Verifica acesso à rede"""
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=5)
            return True
        except:
            return False
    
    def _check_privileges(self) -> bool:
        """Verifica privilégios do sistema"""
        # Verifica se pode criar sockets raw (requer root)
        return self._check_raw_sockets()
    
    def validate_target_authorization(self, target: str) -> bool:
        """Valida se o alvo está autorizado para testes"""
        # Em ambiente real, isso verificaria uma lista de autorização
        # Por enquanto, apenas valida formato
        try:
            socket.gethostbyname(target)
            
            # Verifica se é localhost ou IP privado
            if target in ['localhost', '127.0.0.1']:
                return True
            
            # Verifica ranges privados
            if target.startswith('192.168.') or target.startswith('10.') or target.startswith('172.'):
                return True
            
            # Para IPs públicos, requer confirmação explícita
            print(f"⚠️  WARNING: Target {target} is a public IP address")
            confirmation = input("Do you have explicit authorization to test this target? (yes/no): ")
            return confirmation.lower() in ['yes', 'y', 'sim', 's']
            
        except socket.gaierror:
            return False
    
    def calculate_file_checksum(self, filepath: str) -> str:
        """Calcula checksum de arquivo para verificação de integridade"""
        if filepath in self.checksum_cache:
            return self.checksum_cache[filepath]
        
        try:
            hasher = hashlib.sha256()
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            
            checksum = hasher.hexdigest()
            self.checksum_cache[filepath] = checksum
            return checksum
            
        except Exception as e:
            raise SecurityError(f"Failed to calculate checksum: {e}")
    
    def verify_script_integrity(self) -> bool:
        """Verifica integridade dos scripts principais"""
        try:
            main_scripts = ['crysis.py', 'src/main.py']
            
            for script in main_scripts:
                if os.path.exists(script):
                    checksum = self.calculate_file_checksum(script)
                    # Em ambiente real, compararia com checksums conhecidos
                    print(f"🔒 {script}: {checksum}")
            
            return True
            
        except Exception as e:
            print(f"❌ Integrity check failed: {e}")
            return False
    
    def generate_attack_id(self, config: Dict) -> str:
        """Gera ID único para o ataque"""
        import json
        import time
        
        config_str = json.dumps(config, sort_keys=True)
        timestamp = str(int(time.time()))
        
        hasher = hashlib.md5()
        hasher.update(config_str.encode())
        hasher.update(timestamp.encode())
        hasher.update(getpass.getuser().encode())
        
        return f"attack_{hasher.hexdigest()[:12]}"
    
    def check_rate_limits(self, attack_type: str, packets_per_second: float) -> bool:
        """Verifica limites de taxa para prevenir detecção"""
        rate_limits = {
            'tcp_syn': 1000,      # pps
            'udp_flood': 5000,    # pps  
            'http_flood': 100,    # requests/segundo
            'dns_amp': 100,       # queries/segundo
            'slowloris': 10       # novas conexões/segundo
        }
        
        limit = rate_limits.get(attack_type, 1000)
        return packets_per_second <= limit
    
    def sanitize_target_input(self, input_str: str) -> str:
        """Sanitiza entrada do usuário para prevenir injection"""
        import re
        
        # Remove caracteres potencialmente perigosos
        sanitized = re.sub(r'[^\w\.\-:]', '', input_str)
        
        # Verifica formato básico de IP/domínio
        if not re.match(r'^[\w\.\-:]+$', sanitized):
            raise SecurityError("Invalid target format")
        
        return sanitized
    
    def audit_attack_parameters(self, config: Dict) -> Dict:
        """Audita parâmetros do ataque para segurança"""
        audit_result = {
            'warnings': [],
            'errors': [],
            'recommendations': []
        }
        
        # Verifica duração
        if config.get('duration', 0) > 3600:  # 1 hora
            audit_result['warnings'].append("Attack duration exceeds 1 hour")
        
        # Verifica taxa
        if config.get('rate_limit', 0) > 10000:  # 10k pps
            audit_result['warnings'].append("Packet rate very high - may trigger detection")
        
        # Verifica threads
        if config.get('threads', 0) > 500:
            audit_result['recommendations'].append("Consider reducing threads for stability")
        
        # Verifica se é IP público
        target = config.get('target_ip', '')
        if not any(target.startswith(prefix) for prefix in ['127.', '192.168.', '10.', '172.']):
            audit_result['warnings'].append("Target is a public IP address")
        
        return audit_result

class SecurityError(Exception):
    """Exceção para erros de segurança"""
    pass

# Singleton para uso global
security_manager = SecurityManager()