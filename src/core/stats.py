"""
Gerenciamento de estatísticas e métricas
"""
import time
import threading
from typing import Dict, List, Any
from dataclasses import dataclass
from .config import AttackStats

class StatisticsManager:
    """Gerencia coleta e análise de estatísticas"""
    
    def __init__(self):
        self.stats = AttackStats()
        self.lock = threading.Lock()
        self.history: List[Dict] = []
        self.start_time = time.time()
    
    def update_stats(self, bytes_sent: int, packets: int = 1):
        """Atualiza estatísticas de forma thread-safe"""
        with self.lock:
            self.stats.packets_sent += packets
            self.stats.bytes_sent += bytes_sent
            
            # Calcula taxa de sucesso
            if self.stats.packets_sent > 0:
                self.stats.success_rate = 100 - (self.stats.errors / self.stats.packets_sent * 100)
    
    def increment_errors(self, count: int = 1):
        """Incrementa contador de erros"""
        with self.lock:
            self.stats.errors += count
    
    def get_current_stats(self) -> AttackStats:
        """Retorna cópia das estatísticas atuais"""
        with self.lock:
            return AttackStats(
                packets_sent=self.stats.packets_sent,
                bytes_sent=self.stats.bytes_sent,
                errors=self.stats.errors,
                start_time=self.stats.start_time or self.start_time,
                amplification_factor=self.stats.amplification_factor,
                success_rate=self.stats.success_rate
            )
    
    def calculate_metrics(self) -> Dict[str, Any]:
        """Calcula métricas derivadas"""
        current_stats = self.get_current_stats()
        elapsed = time.time() - current_stats.start_time
        
        metrics = {
            'duration': elapsed,
            'packets_per_second': current_stats.packets_sent / max(elapsed, 1),
            'bytes_per_second': current_stats.bytes_sent / max(elapsed, 1),
            'megabits_per_second': (current_stats.bytes_sent * 8) / (max(elapsed, 1) * 1000000),
            'error_rate': current_stats.errors / max(current_stats.packets_sent, 1),
            'success_rate': current_stats.success_rate,
            'efficiency': current_stats.packets_sent / max(elapsed, 1)  # pps por thread
        }
        
        return metrics
    
    def record_snapshot(self):
        """Registra snapshot atual no histórico"""
        snapshot = {
            'timestamp': time.time(),
            'stats': self.get_current_stats(),
            'metrics': self.calculate_metrics()
        }
        self.history.append(snapshot)
    
    def get_performance_trend(self) -> Dict[str, List]:
        """Retorna tendência de performance ao longo do tempo"""
        if len(self.history) < 2:
            return {}
        
        trends = {
            'timestamps': [s['timestamp'] for s in self.history],
            'packets_per_second': [s['metrics']['packets_per_second'] for s in self.history],
            'success_rates': [s['metrics']['success_rate'] for s in self.history],
            'error_rates': [s['metrics']['error_rate'] for s in self.history]
        }
        
        return trends
    
    def reset_stats(self):
        """Reinicia todas as estatísticas"""
        with self.lock:
            self.stats = AttackStats()
            self.start_time = time.time()
            self.stats.start_time = self.start_time
            self.history.clear()
    
    def generate_report(self) -> Dict[str, Any]:
        """Gera relatório completo"""
        metrics = self.calculate_metrics()
        trends = self.get_performance_trend()
        current_stats = self.get_current_stats()
        
        report = {
            'summary': {
                'total_packets': current_stats.packets_sent,
                'total_bytes': current_stats.bytes_sent,
                'total_errors': current_stats.errors,
                'total_duration': metrics['duration'],
                'average_throughput': metrics['megabits_per_second'],
                'final_success_rate': metrics['success_rate']
            },
            'performance_metrics': metrics,
            'efficiency_analysis': self._analyze_efficiency(),
            'recommendations': self._generate_recommendations(),
            'trend_data': trends
        }
        
        return report
    
    def _analyze_efficiency(self) -> Dict[str, Any]:
        """Analisa eficiência do ataque"""
        metrics = self.calculate_metrics()
        
        efficiency = {
            'packet_efficiency': metrics['packets_per_second'] / max(metrics['megabits_per_second'], 0.001),
            'bandwidth_utilization': min(100, metrics['megabits_per_second'] / 100 * 100),  # Assume 100Mbps como referência
            'error_impact': metrics['error_rate'] * 100,
            'overall_score': max(0, 100 - (metrics['error_rate'] * 1000))  # Score 0-100
        }
        
        return efficiency
    
    def _generate_recommendations(self) -> List[str]:
        """Gera recomendações baseadas nas estatísticas"""
        metrics = self.calculate_metrics()
        recommendations = []
        
        if metrics['error_rate'] > 0.1:  # 10% de erro
            recommendations.append("High error rate detected - consider reducing packet rate or checking target availability")
        
        if metrics['success_rate'] < 80:
            recommendations.append("Low success rate - target may be implementing protection measures")
        
        if metrics['packets_per_second'] < 10:
            recommendations.append("Very low packet rate - check network connectivity and thread count")
        
        if metrics['megabits_per_second'] < 1.0:
            recommendations.append("Low bandwidth utilization - consider increasing packet size or thread count")
        
        if not recommendations:
            recommendations.append("Attack parameters appear optimal - consider increasing scale for higher impact")
        
        return recommendations
    
    def export_to_json(self, filename: str = None):
        """Exporta estatísticas para JSON"""
        import json
        from datetime import datetime
        
        if not filename:
            filename = f"attack_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = self.generate_report()
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        return filename