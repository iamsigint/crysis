"""
Gerador de padrões de ataque baseados em IA
"""
import random
import time
from typing import Dict, List, Any
from enum import Enum

class AttackPattern(Enum):
    STEADY_FLOW = "steady"
    PULSE_WAVE = "pulse" 
    RANDOM_BURST = "random_burst"
    SLOW_RISE = "slow_rise"
    TSUNAMI = "tsunami"
    STAIRCASE = "staircase"
    SINUSOIDAL = "sinusoidal"

class AttackPatternGenerator:
    """Gera padrões inteligentes de ataque"""
    
    def __init__(self):
        self.patterns = self._initialize_patterns()
        self.current_pattern = None
    
    def _initialize_patterns(self) -> Dict[AttackPattern, Dict]:
        """Inicializa biblioteca de padrões"""
        return {
            AttackPattern.STEADY_FLOW: {
                'name': 'Steady Flow',
                'description': 'Fluxo constante e previsível',
                'intensity': 0.3,
                'variation': 0.1,
                'burst_size': 1,
                'sleep_time': 0.01
            },
            AttackPattern.PULSE_WAVE: {
                'name': 'Pulse Wave', 
                'description': 'Rajadas rápidas seguidas de pausas',
                'intensity': 0.7,
                'variation': 0.4,
                'burst_size': 50,
                'sleep_time': 0.5
            },
            AttackPattern.RANDOM_BURST: {
                'name': 'Random Burst',
                'description': 'Explosões aleatórias de tráfego',
                'intensity': 0.8,
                'variation': 0.9,
                'burst_size': (10, 100),
                'sleep_time': (0.1, 1.0)
            },
            AttackPattern.SLOW_RISE: {
                'name': 'Slow Rise',
                'description': 'Aumento gradual da intensidade',
                'intensity': 0.5,
                'variation': 0.2,
                'phases': 10,
                'increment': 5
            },
            AttackPattern.TSUNAMI: {
                'name': 'Tsunami',
                'description': 'Ataque massivo seguido de pausa longa',
                'intensity': 0.9,
                'variation': 0.3,
                'burst_size': 200,
                'sleep_time': 2.0
            },
            AttackPattern.STAIRCASE: {
                'name': 'Staircase',
                'description': 'Aumento em degraus com platôs',
                'intensity': 0.6,
                'variation': 0.2,
                'steps': 5,
                'step_duration': 3
            },
            AttackPattern.SINUSOIDAL: {
                'name': 'Sinusoidal',
                'description': 'Padrão de onda senoidal',
                'intensity': 0.5,
                'variation': 0.3,
                'period': 10,
                'amplitude': 0.4
            }
        }
    
    def get_random_pattern(self) -> Dict[str, Any]:
        """Retorna padrão aleatório"""
        pattern_type = random.choice(list(self.patterns.keys()))
        self.current_pattern = pattern_type
        return {
            'pattern': pattern_type.value,
            'name': self.patterns[pattern_type]['name'],
            'config': self.patterns[pattern_type]
        }
    
    def get_pattern_by_name(self, pattern_name: str) -> Dict[str, Any]:
        """Retorna padrão específico pelo nome"""
        for pattern_type, config in self.patterns.items():
            if config['name'].lower() == pattern_name.lower():
                self.current_pattern = pattern_type
                return {
                    'pattern': pattern_type.value,
                    'name': config['name'],
                    'config': config
                }
        return self.get_random_pattern()
    
    def generate_attack_sequence(self, pattern: Dict, duration: int) -> List[Dict]:
        """Gera sequência de ataque baseada no padrão"""
        pattern_type = AttackPattern(pattern['pattern'])
        config = pattern['config']
        
        if pattern_type == AttackPattern.STEADY_FLOW:
            return self._generate_steady_sequence(config, duration)
        elif pattern_type == AttackPattern.PULSE_WAVE:
            return self._generate_pulse_sequence(config, duration)
        elif pattern_type == AttackPattern.RANDOM_BURST:
            return self._generate_random_burst_sequence(config, duration)
        elif pattern_type == AttackPattern.SLOW_RISE:
            return self._generate_slow_rise_sequence(config, duration)
        elif pattern_type == AttackPattern.TSUNAMI:
            return self._generate_tsunami_sequence(config, duration)
        elif pattern_type == AttackPattern.STAIRCASE:
            return self._generate_staircase_sequence(config, duration)
        elif pattern_type == AttackPattern.SINUSOIDAL:
            return self._generate_sinusoidal_sequence(config, duration)
        else:
            return self._generate_steady_sequence(config, duration)
    
    def _generate_steady_sequence(self, config: Dict, duration: int) -> List[Dict]:
        """Gera sequência de fluxo constante"""
        sequence = []
        for i in range(duration * 10):  # 10 ações por segundo
            sequence.append({
                'action': 'send_packets',
                'count': 1,
                'intensity': config['intensity'],
                'sleep': config['sleep_time']
            })
        return sequence
    
    def _generate_pulse_sequence(self, config: Dict, duration: int) -> List[Dict]:
        """Gera sequência de pulsos"""
        sequence = []
        pulses = duration // 2  # Pulso a cada 2 segundos
        
        for pulse in range(pulses):
            # Fase ativa
            sequence.append({
                'action': 'send_burst',
                'count': config['burst_size'],
                'intensity': config['intensity'],
                'sleep': 0.01
            })
            # Fase de pausa
            sequence.append({
                'action': 'sleep',
                'duration': config['sleep_time']
            })
        
        return sequence
    
    def _generate_random_burst_sequence(self, config: Dict, duration: int) -> List[Dict]:
        """Gera sequência de rajadas aleatórias"""
        sequence = []
        time_elapsed = 0
        
        while time_elapsed < duration:
            burst_size = random.randint(config['burst_size'][0], config['burst_size'][1])
            sleep_time = random.uniform(config['sleep_time'][0], config['sleep_time'][1])
            
            sequence.append({
                'action': 'send_burst',
                'count': burst_size,
                'intensity': config['intensity'],
                'sleep': 0.01
            })
            
            sequence.append({
                'action': 'sleep', 
                'duration': sleep_time
            })
            
            time_elapsed += sleep_time + (burst_size * 0.01)
        
        return sequence[:int(duration * 10)]  # Limita pela duração
    
    def _generate_slow_rise_sequence(self, config: Dict, duration: int) -> List[Dict]:
        """Gera sequência de aumento gradual"""
        sequence = []
        phase_duration = duration / config['phases']
        
        for phase in range(config['phases']):
            packets_per_phase = (phase + 1) * config['increment']
            
            for i in range(int(packets_per_phase)):
                sequence.append({
                    'action': 'send_packets',
                    'count': 1,
                    'intensity': config['intensity'] * (phase + 1) / config['phases'],
                    'sleep': 0.1
                })
            
            # Pequena pausa entre fases
            sequence.append({
                'action': 'sleep',
                'duration': 0.5
            })
        
        return sequence
    
    def _generate_tsunami_sequence(self, config: Dict, duration: int) -> List[Dict]:
        """Gera sequência tsunami"""
        sequence = []
        waves = max(1, duration // 5)  # Onda a cada 5 segundos
        
        for wave in range(waves):
            # Onda massiva
            sequence.append({
                'action': 'send_burst',
                'count': config['burst_size'],
                'intensity': config['intensity'],
                'sleep': 0.001  # Muito rápido
            })
            
            # Pausa longa
            sequence.append({
                'action': 'sleep',
                'duration': config['sleep_time']
            })
        
        return sequence
    
    def _generate_staircase_sequence(self, config: Dict, duration: int) -> List[Dict]:
        """Gera sequência em escada"""
        sequence = []
        step_duration = config['step_duration']
        steps = config['steps']
        
        for step in range(steps):
            intensity = (step + 1) / steps
            packets_per_second = 10 + (step * 20)  # Aumenta a cada degrau
            
            for second in range(step_duration):
                for i in range(packets_per_second):
                    sequence.append({
                        'action': 'send_packets',
                        'count': 1,
                        'intensity': intensity,
                        'sleep': 1.0 / packets_per_second
                    })
        
        return sequence
    
    def _generate_sinusoidal_sequence(self, config: Dict, duration: int) -> List[Dict]:
        """Gera sequência sinusoidal"""
        sequence = []
        period = config['period']
        amplitude = config['amplitude']
        base_intensity = config['intensity']
        
        for t in range(duration * 10):  # 10 pontos por segundo
            time_ratio = t / (duration * 10)
            sine_value = math.sin(2 * math.pi * time_ratio * (10 / period))
            intensity = base_intensity + (amplitude * sine_value)
            
            sequence.append({
                'action': 'send_packets',
                'count': max(1, int(5 * (intensity + 0.5))),  # 1-10 pacotes
                'intensity': max(0.1, min(1.0, intensity)),
                'sleep': 0.1
            })
        
        return sequence
    
    def adapt_pattern(self, current_pattern: Dict, success_rate: float, response_time: float) -> Dict:
        """Adapta padrão baseado em métricas de performance"""
        pattern_type = AttackPattern(current_pattern['pattern'])
        config = current_pattern['config'].copy()
        
        # Ajusta baseado na taxa de sucesso
        if success_rate < 50:
            # Reduz intensidade se muitos erros
            config['intensity'] *= 0.8
            if 'burst_size' in config:
                if isinstance(config['burst_size'], tuple):
                    config['burst_size'] = (
                        max(1, int(config['burst_size'][0] * 0.7)),
                        max(5, int(config['burst_size'][1] * 0.7))
                    )
                else:
                    config['burst_size'] = max(5, int(config['burst_size'] * 0.7))
        elif success_rate > 90:
            # Aumenta intensidade se performance boa
            config['intensity'] = min(1.0, config['intensity'] * 1.2)
            if 'burst_size' in config:
                if isinstance(config['burst_size'], tuple):
                    config['burst_size'] = (
                        int(config['burst_size'][0] * 1.3),
                        int(config['burst_size'][1] * 1.3)
                    )
                else:
                    config['burst_size'] = int(config['burst_size'] * 1.3)
        
        # Ajusta baseado no tempo de resposta
        if response_time > 2.0:  # Resposta lenta
            if 'sleep_time' in config:
                if isinstance(config['sleep_time'], tuple):
                    config['sleep_time'] = (
                        config['sleep_time'][0] * 1.5,
                        config['sleep_time'][1] * 1.5
                    )
                else:
                    config['sleep_time'] *= 1.5
        
        return {
            'pattern': current_pattern['pattern'],
            'name': current_pattern['name'],
            'config': config
        }

# Para a sequência sinusoidal
import math