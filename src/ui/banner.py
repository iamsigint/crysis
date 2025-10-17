"""
Display de banners e interfaces visuais
"""
import os
import sys
import time
from typing import Dict, List, Any  # Adicionado import

class BannerDisplay:
    """Gerencia exibição de banners e interfaces"""
    
    def __init__(self):
        self.version = "1.0.0001"  # Temporário até corrigir o version_manager
        self.colors = self._init_colors()
    
    def _init_colors(self) -> Dict[str, str]:
        """Inicializa cores para terminal"""
        colors = {
            'RED': '\033[91m',
            'GREEN': '\033[92m',
            'YELLOW': '\033[93m',
            'BLUE': '\033[94m',
            'MAGENTA': '\033[95m',
            'CYAN': '\033[96m',
            'WHITE': '\033[97m',
            'BOLD': '\033[1m',
            'UNDERLINE': '\033[4m',
            'END': '\033[0m'
        }
        return colors
    
    def show(self):
        """Exibe banner principal"""
        self._clear_screen()
        
        banner = f"""
{self.colors['CYAN']}╔════════════════════════════════════════════════════════════════╗
║                {self.colors['BOLD']}🚀 CRYSIS TEST SUITE 🚀{self.colors['END']}{self.colors['CYAN']}                 ║
║                       ELITE EDITION v{self.version}                      ║
╠════════════════════════════════════════════════════════════════╣
║   ██████╗██╗   ██╗██████╗ ███████╗██████╗     ██████╗██████╗  ║
║  ██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗   ██╔════╝██╔══██╗ ║
║  ██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝   ██║     ██████╔╝ ║
║  ██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗   ██║     ██╔══██╗ ║
║  ╚██████╗   ██║   ██████╔╝███████╗██║  ██║██╗╚██████╗██║  ██║ ║
║   ╚═════╝   ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝ ╚═════╝╚═╝  ╚═╝ ║
╚════════════════════════════════════════════════════════════════╝{self.colors['END']}
        """
        
        print(banner)
        self._show_warning()
    
    def _show_warning(self):
        """Exibe avisos legais"""
        warning = f"""
{self.colors['RED']}{self.colors['BOLD']}⚠️  LEGAL WARNING: UNAUTHORIZED USE IS ILLEGAL!{self.colors['END']}
{self.colors['YELLOW']}This tool is for authorized security testing only.
Use only on systems you own or have explicit permission to test.
The developers are not responsible for misuse.{self.colors['END']}
        """
        print(warning)
    
    def show_attack_start(self, attack_name: str, target: str, duration: int):
        """Exibe informações de início de ataque"""
        print(f"\n{self.colors['GREEN']}{self.colors['BOLD']}🎯 STARTING ATTACK{self.colors['END']}")
        print(f"{self.colors['CYAN']}Attack Type:{self.colors['END']} {attack_name}")
        print(f"{self.colors['CYAN']}Target:{self.colors['END']} {target}")
        print(f"{self.colors['CYAN']}Duration:{self.colors['END']} {duration}s")
        print(f"{self.colors['CYAN']}Time:{self.colors['END']} {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{self.colors['YELLOW']}Press Ctrl+C to stop the attack{self.colors['END']}")
        print("=" * 60)
    
    def show_attack_progress(self, stats: Dict):
        """Exibe progresso do ataque em tempo real"""
        elapsed = time.time() - stats['start_time']
        packets_per_sec = stats['packets_sent'] / max(elapsed, 1)
        mbps = (stats['bytes_sent'] * 8) / (max(elapsed, 1) * 1000000)
        success_rate = 100 - (stats['errors'] / max(stats['packets_sent'], 1) * 100)
        
        progress_line = (
            f"{self.colors['GREEN']}📊 PACOTES: {stats['packets_sent']:,} | "
            f"{self.colors['YELLOW']}ERROS: {stats['errors']} | "
            f"{self.colors['BLUE']}VELOCIDADE: {packets_per_sec:.1f} pps | "
            f"{self.colors['MAGENTA']}LARGURA: {mbps:.2f} Mbps | "
            f"{self.colors['CYAN']}SUCESSO: {success_rate:.1f}%{self.colors['END']}"
        )
        
        print(f"\r{progress_line}", end="", flush=True)
    
    def show_attack_summary(self, stats: Dict):
        """Exibe resumo final do ataque"""
        duration = time.time() - stats['start_time']
        
        summary = f"""
{self.colors['GREEN']}{self.colors['BOLD']}📈 ATTACK SUMMARY{self.colors['END']}
{self.colors['CYAN']}╔══════════════════════════════════════════════════════════════╗
║                         RESULTS                          ║
╠══════════════════════════════════════════════════════════════╣
║ 📦 Total Packets: {stats['packets_sent']:>15,}           ║
║ 💾 Total Bytes: {stats['bytes_sent']:>17,}           ║
║ ❌ Errors: {stats['errors']:>24}           ║
║ ⏱️  Duration: {duration:>19.2f}s           ║
║ ⚡ Avg Speed: {stats['packets_sent']/max(duration,1):>16.1f} pps    ║
║ 🌊 Bandwidth: {(stats['bytes_sent']*8)/(max(duration,1)*1000000):>16.2f} Mbps    ║
║ 🎯 Success Rate: {100 - (stats['errors']/max(stats['packets_sent'],1)*100):>15.1f}%     ║
╚══════════════════════════════════════════════════════════════╝{self.colors['END']}
        """
        
        print(summary)
    
    def show_error(self, message: str):
        """Exibe mensagem de erro"""
        print(f"\n{self.colors['RED']}❌ ERROR: {message}{self.colors['END']}")
    
    def show_success(self, message: str):
        """Exibe mensagem de sucesso"""
        print(f"\n{self.colors['GREEN']}✅ SUCCESS: {message}{self.colors['END']}")
    
    def show_warning_message(self, message: str):
        """Exibe mensagem de aviso"""
        print(f"\n{self.colors['YELLOW']}⚠️  WARNING: {message}{self.colors['END']}")
    
    def _clear_screen(self):
        """Limpa a tela do terminal"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def animate_loading(self, message: str, duration: float = 2.0):
        """Exibe animação de carregamento"""
        animation = "⣾⣽⣻⢿⡿⣟⣯⣷"
        start_time = time.time()
        i = 0
        
        while time.time() - start_time < duration:
            print(f"\r{self.colors['CYAN']}{animation[i % len(animation)]} {message}{self.colors['END']}", end="")
            i += 1
            time.sleep(0.1)
        
        print("\r" + " " * (len(message) + 2) + "\r", end="")