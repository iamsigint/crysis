#!/usr/bin/env python3
"""
CRYSIS - Advanced Network Stress Testing Tool
Version: 1.0.0001
"""

import sys
import os

# Adiciona o src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.version import version_manager
from ui.banner import BannerDisplay
from ui.menu import AttackMenu
from ui.input_handler import InputHandler
from core.validator import TargetValidator
from attacks.factory import AttackFactory
from core.stats import StatisticsManager

class Crysis:
    def __init__(self):
        self.banner = BannerDisplay()
        self.menu = AttackMenu()
        self.input_handler = InputHandler()
        self.validator = TargetValidator()
        self.stats_manager = StatisticsManager()
        self.running = False
    
    def display_welcome(self):
        """Exibe tela de boas-vindas"""
        self.banner.show()
        print(f"🚀 CRYSIS v{version_manager.get_version()} - Advanced Network Testing")
        print("⚡ FOR AUTHORIZED PENETRATION TESTING ONLY!\n")
    
    def get_user_agreement(self) -> bool:
        """Obtém aceitação dos termos"""
        print("⚠️  LEGAL WARNING: UNAUTHORIZED USE IS ILLEGAL!")
        print("   This tool is for authorized security testing only.\n")
        
        accept = input("🔐 Do you accept the terms and conditions? (y/n): ").lower()
        return accept in ['y', 'yes', 's', 'sim']
    
    def run(self):
        """Método principal de execução"""
        try:
            self.display_welcome()
            
            if not self.get_user_agreement():
                print("🚫 Access denied. Exiting.")
                return
            
            while True:
                # Mostra menu e obtém configuração
                attack_config = self.menu.get_attack_config()
                
                # Valida target
                if not self.validator.validate_target(attack_config.target_ip):
                    print("❌ Invalid target! Please check the IP/domain.")
                    continue
                
                # Executa ataque
                self.execute_attack(attack_config)
                
                # Pergunta se quer continuar
                again = input("\n🔄 Run another attack? (y/n): ").lower()
                if again not in ['y', 'yes', 's', 'sim']:
                    break
            
            print("\n🎉 Thank you for using CRYSIS!")
            
        except KeyboardInterrupt:
            print("\n\n👋 Program terminated by user.")
        except Exception as e:
            print(f"\n💥 Critical error: {e}")
            sys.exit(1)
    
    def execute_attack(self, config):
        """Executa um ataque específico"""
        try:
            print(f"\n🎯 Starting attack: {config.attack_type.name}")
            print(f"🎯 Target: {config.target_ip}:{config.target_port}")
            print(f"⏰ Duration: {config.duration}s")
            print(f"🧵 Threads: {config.threads}")
            print("=" * 50)
            
            # Cria e executa ataque
            attack = AttackFactory.create_attack(
                config.attack_type.value, 
                config, 
                self.stats_manager
            )
            
            attack.execute()
            
        except Exception as e:
            print(f"❌ Attack failed: {e}")

def main():
    """Função principal"""
    crysis = Crysis()
    crysis.run()

if __name__ == '__main__':
    main()