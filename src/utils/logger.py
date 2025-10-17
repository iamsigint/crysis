"""
Sistema de logging avançado
"""
import logging
import sys
import os
import time
from datetime import datetime
from typing import Dict, Any
from enum import Enum

class LogLevel(Enum):
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50

class AttackLogger:
    """Sistema de logging para ataques e métricas"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir
        self.setup_logging()
        self.attack_logs: Dict[str, Any] = {}
    
    def setup_logging(self):
        """Configura sistema de logging"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        
        # Configura formato
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        date_format = '%Y-%m-%d %H:%M:%S'
        
        # Configura root logger
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            datefmt=date_format,
            handlers=[
                logging.FileHandler(os.path.join(self.log_dir, f"crysis_{datetime.now().strftime('%Y%m%d')}.log")),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger('crysis')
    
    def start_attack_log(self, attack_id: str, config: Dict):
        """Inicia log para um ataque específico"""
        self.attack_logs[attack_id] = {
            'start_time': time.time(),
            'config': config,
            'stats': {
                'packets_sent': 0,
                'bytes_sent': 0,
                'errors': 0,
                'success_rate': 100.0
            },
            'events': []
        }
        
        self.logger.info(f"Attack started: {attack_id}")
        self.logger.info(f"Attack config: {config}")
    
    def log_attack_event(self, attack_id: str, event_type: str, message: str, data: Dict = None):
        """Registra evento durante o ataque"""
        if attack_id not in self.attack_logs:
            return
        
        event = {
            'timestamp': time.time(),
            'type': event_type,
            'message': message,
            'data': data or {}
        }
        
        self.attack_logs[attack_id]['events'].append(event)
        
        # Também loga no sistema principal
        log_message = f"[{attack_id}] {message}"
        if event_type == 'ERROR':
            self.logger.error(log_message)
        elif event_type == 'WARNING':
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)
    
    def update_attack_stats(self, attack_id: str, stats: Dict):
        """Atualiza estatísticas do ataque"""
        if attack_id in self.attack_logs:
            self.attack_logs[attack_id]['stats'].update(stats)
    
    def end_attack_log(self, attack_id: str, reason: str = "Completed"):
        """Finaliza log do ataque e salva relatório"""
        if attack_id not in self.attack_logs:
            return
        
        attack_log = self.attack_logs[attack_id]
        duration = time.time() - attack_log['start_time']
        
        # Calcula métricas finais
        stats = attack_log['stats']
        if stats['packets_sent'] > 0:
            stats['success_rate'] = 100 - (stats['errors'] / stats['packets_sent'] * 100)
            stats['packets_per_second'] = stats['packets_sent'] / duration
            stats['bytes_per_second'] = stats['bytes_sent'] / duration
            stats['mbps'] = (stats['bytes_sent'] * 8) / (duration * 1000000)
        
        # Salva relatório
        report = {
            'attack_id': attack_id,
            'start_time': attack_log['start_time'],
            'end_time': time.time(),
            'duration': duration,
            'completion_reason': reason,
            'config': attack_log['config'],
            'final_stats': stats,
            'events_count': len(attack_log['events']),
            'significant_events': [e for e in attack_log['events'] if e['type'] in ['ERROR', 'WARNING']]
        }
        
        # Salva em arquivo JSON
        import json
        report_file = os.path.join(self.log_dir, f"attack_{attack_id}_{int(time.time())}.json")
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        self.logger.info(f"Attack completed: {attack_id} - Duration: {duration:.2f}s")
        self.logger.info(f"Final stats: {stats}")
        self.logger.info(f"Report saved: {report_file}")
        
        # Remove da memória
        del self.attack_logs[attack_id]
        
        return report
    
    def log_performance_metrics(self, metrics: Dict):
        """Registra métricas de performance"""
        self.logger.info(f"Performance metrics: {metrics}")
    
    def log_security_event(self, event: str, details: Dict = None):
        """Registra eventos de segurança"""
        self.logger.warning(f"Security event: {event} - Details: {details}")
    
    def get_attack_history(self, limit: int = 10) -> list:
        """Retorna histórico de ataques recentes"""
        # Em implementação real, buscaria do banco de dados
        # Por enquanto retorna da memória
        return list(self.attack_logs.keys())[-limit:]
    
    def cleanup_old_logs(self, days: int = 7):
        """Remove logs antigos"""
        try:
            current_time = time.time()
            for filename in os.listdir(self.log_dir):
                filepath = os.path.join(self.log_dir, filename)
                if os.path.isfile(filepath):
                    # Verifica se o arquivo é mais antigo que 'days'
                    if current_time - os.path.getmtime(filepath) > (days * 24 * 60 * 60):
                        os.remove(filepath)
                        self.logger.info(f"Removed old log file: {filename}")
        except Exception as e:
            self.logger.error(f"Error cleaning up old logs: {e}")

# Singleton para uso global
attack_logger = AttackLogger()