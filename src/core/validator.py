"""
Validação de entradas e configurações
"""
import ipaddress
import socket
import re
from typing import Union, Optional
from urllib.parse import urlparse

class TargetValidator:
    """Valida alvos e configurações de ataque"""
    
    def validate_target(self, target: str) -> bool:
        """Valida se o alvo é um IP ou domínio válido"""
        try:
            # Tenta como IP primeiro
            ipaddress.ip_address(target)
            return True
        except ValueError:
            # Tenta como domínio
            try:
                socket.gethostbyname(target)
                return True
            except socket.gaierror:
                return False
    
    def validate_port(self, port: Union[int, str]) -> bool:
        """Valida número da porta"""
        try:
            port_num = int(port)
            return 1 <= port_num <= 65535
        except (ValueError, TypeError):
            return False
    
    def validate_duration(self, duration: Union[int, str]) -> bool:
        """Valida duração do ataque"""
        try:
            duration_num = int(duration)
            return 1 <= duration_num <= 86400  # Máximo 24 horas
        except (ValueError, TypeError):
            return False
    
    def validate_threads(self, threads: Union[int, str]) -> bool:
        """Valida número de threads"""
        try:
            threads_num = int(threads)
            return 1 <= threads_num <= 1000
        except (ValueError, TypeError):
            return False
    
    def validate_packet_size(self, size: Union[int, str]) -> bool:
        """Valida tamanho do pacote"""
        try:
            size_num = int(size)
            return 1 <= size_num <= 65535
        except (ValueError, TypeError):
            return False
    
    def validate_rate_limit(self, rate: Union[int, str]) -> bool:
        """Valida limite de taxa"""
        try:
            rate_num = int(rate)
            return 1 <= rate_num <= 1000000  # Máximo 1M pps
        except (ValueError, TypeError):
            return False
    
    def validate_protocol(self, protocol: str) -> bool:
        """Valida protocolo"""
        valid_protocols = ['tcp', 'udp', 'icmp', 'http', 'https', 'dns', 'ntp']
        return protocol.lower() in valid_protocols
    
    def validate_url(self, url: str) -> bool:
        """Valida URL"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def sanitize_input(self, input_str: str, input_type: str = 'general') -> str:
        """Sanitiza entrada do usuário"""
        sanitized = input_str.strip()
        
        if input_type == 'ip':
            # Remove caracteres não IP
            sanitized = re.sub(r'[^\d\.]', '', sanitized)
        elif input_type == 'port':
            # Remove caracteres não numéricos
            sanitized = re.sub(r'[^\d]', '', sanitized)
        elif input_type == 'domain':
            # Remove caracteres inválidos para domínio
            sanitized = re.sub(r'[^a-zA-Z0-9\.\-]', '', sanitized)
        
        return sanitized
    
    def comprehensive_validation(self, config: dict) -> dict:
        """Validação abrangente de configuração"""
        errors = []
        warnings = []
        
        # Valida target
        if not self.validate_target(config.get('target_ip', '')):
            errors.append("Invalid target IP or domain")
        
        # Valida porta
        if not self.validate_port(config.get('target_port', 0)):
            errors.append("Invalid target port")
        
        # Valida duração
        duration = config.get('duration', 0)
        if not self.validate_duration(duration):
            errors.append("Invalid duration")
        elif duration > 3600:  # 1 hora
            warnings.append("Long attack duration may trigger monitoring systems")
        
        # Valida threads
        threads = config.get('threads', 0)
        if not self.validate_threads(threads):
            errors.append("Invalid thread count")
        elif threads > 100:
            warnings.append("High thread count may impact system performance")
        
        # Valida tamanho do pacote
        packet_size = config.get('packet_size', 0)
        if not self.validate_packet_size(packet_size):
            errors.append("Invalid packet size")
        elif packet_size > 1500:
            warnings.append("Large packet size may cause fragmentation")
        
        # Validações específicas por tipo de ataque
        attack_type = config.get('attack_type', '')
        if 'amplification' in attack_type:
            if packet_size < 100:
                warnings.append("Small packet size may reduce amplification effect")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def check_target_availability(self, target: str, port: int, timeout: float = 3.0) -> bool:
        """Verifica se o alvo está acessível"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout)
                result = sock.connect_ex((target, port))
                return result == 0
        except:
            return False
    
    def get_target_info(self, target: str) -> dict:
        """Obtém informações sobre o alvo"""
        try:
            # Resolve IP
            ip_address = socket.gethostbyname(target)
            
            # Tenta obter nome reverso
            try:
                hostname = socket.gethostbyaddr(ip_address)[0]
            except socket.herror:
                hostname = ip_address
            
            # Verifica se é IP privado
            is_private = ipaddress.ip_address(ip_address).is_private
            
            return {
                'ip_address': ip_address,
                'hostname': hostname,
                'is_private': is_private,
                'resolved_successfully': True
            }
        except socket.gaierror:
            return {
                'ip_address': None,
                'hostname': None,
                'is_private': None,
                'resolved_successfully': False
            }

class ConfigurationValidator:
    """Valida configurações do sistema"""
    
    def __init__(self):
        self.required_directories = ['logs', 'data', 'reports']
        self.required_permissions = ['network', 'file_write']
    
    def validate_environment(self) -> dict:
        """Valida ambiente de execução"""
        checks = {}
        
        # Verifica diretórios
        for directory in self.required_directories:
            checks[f'directory_{directory}'] = self._check_directory(directory)
        
        # Verifica permissões
        for permission in self.required_permissions:
            checks[f'permission_{permission}'] = self._check_permission(permission)
        
        # Verifica dependências
        checks['python_version'] = self._check_python_version()
        checks['required_modules'] = self._check_required_modules()
        
        return checks
    
    def _check_directory(self, directory: str) -> bool:
        """Verifica se diretório existe e é gravável"""
        import os
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
                return True
            except:
                return False
        return os.access(directory, os.W_OK)
    
    def _check_permission(self, permission: str) -> bool:
        """Verifica permissões específicas"""
        import socket
        import os
        
        if permission == 'network':
            try:
                socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                return True
            except:
                return False
        elif permission == 'file_write':
            try:
                test_file = 'test_write.permission'
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
                return True
            except:
                return False
        
        return False
    
    def _check_python_version(self) -> bool:
        """Verifica versão do Python"""
        import sys
        return sys.version_info >= (3, 8)
    
    def _check_required_modules(self) -> bool:
        """Verifica módulos necessários"""
        required_modules = ['socket', 'threading', 'time', 'random', 'struct', 'ssl']
        
        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                return False
        
        return True