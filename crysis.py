#!/usr/bin/env python3
"""
CRYSIS - Advanced Network Stress Testing Tool
Main Entry Point - Version 1.0.0001
"""

import sys
import os
import time
import threading
import signal
from datetime import datetime

# Adiciona o src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

class AttackStats:
    """Estatísticas do ataque em tempo real"""
    def __init__(self):
        self.packets_sent = 0
        self.bytes_sent = 0
        self.errors = 0
        self.start_time = None
        self.lock = threading.Lock()
    
    def update(self, bytes_sent: int, packets: int = 1):
        """Atualiza estatísticas de forma thread-safe"""
        with self.lock:
            self.packets_sent += packets
            self.bytes_sent += bytes_sent
    
    def increment_errors(self, count: int = 1):
        """Incrementa contador de erros"""
        with self.lock:
            self.errors += count
    
    def get_stats(self):
        """Retorna cópia das estatísticas atuais"""
        with self.lock:
            return {
                'packets_sent': self.packets_sent,
                'bytes_sent': self.bytes_sent,
                'errors': self.errors,
                'start_time': self.start_time
            }

class Crysis:
    def __init__(self):
        from src.ui.banner import BannerDisplay
        from src.ui.menu import AttackMenu
        from src.core.validator import TargetValidator
        from src.attacks.factory import AttackFactory
        
        self.banner = BannerDisplay()
        self.menu = AttackMenu()
        self.validator = TargetValidator()
        self.attack_factory = AttackFactory
        self.stats = AttackStats()
        self.stop_event = threading.Event()
        self.running = False
        self.interrupted = False
        
        # Configura handler de sinal de forma segura
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self):
        """Configura handlers de sinal de forma segura"""
        try:
            self.original_sigint = signal.getsignal(signal.SIGINT)
            signal.signal(signal.SIGINT, self._signal_handler)
        except Exception as e:
            print(f"⚠️  Aviso de signal: {e}")
            self.original_sigint = None
    
    def _signal_handler(self, signum, frame):
        """Handler para Ctrl+C de forma segura"""
        if self.interrupted:
            # Segundo Ctrl+C - saída forçada
            print("\n\n🛑 Saindo forçadamente...")
            os._exit(1)
        
        self.interrupted = True
        print("\n\n🛑 Recebido sinal de interrupção...")
        self.stop_attack()
        
        # Restaura handler original de forma segura
        self._safe_restore_signal_handler()
    
    def _safe_restore_signal_handler(self):
        """Restaura o handler de sinal original de forma segura"""
        try:
            if self.original_sigint is not None:
                signal.signal(signal.SIGINT, self.original_sigint)
            self.interrupted = False
        except Exception as e:
            # Ignora erros de signal em threads não principais
            pass
    
    def _safe_input(self, prompt: str) -> str:
        """Input seguro que trata Ctrl+C"""
        try:
            return input(prompt)
        except (KeyboardInterrupt, EOFError):
            print("\n⏹️  Operação cancelada.")
            self.stop_attack()
            raise SystemExit()
        except Exception as e:
            print(f"\n❌ Erro no input: {e}")
            raise
    
    def display_welcome(self):
        """Exibe tela de boas-vindas"""
        self.banner.show()
        print(f"🚀 CRYSIS v1.0.0001 - Advanced Network Testing")
        print("⚡ FOR AUTHORIZED PENETRATION TESTING ONLY!\n")
    
    def get_user_agreement(self) -> bool:
        """Obtém aceitação dos termos"""
        print("⚠️  LEGAL WARNING: UNAUTHORIZED USE IS ILLEGAL!")
        print("   This tool is for authorized security testing only.\n")
        
        try:
            accept = self._safe_input("🔐 Do you accept the terms and conditions? (y/n): ").lower()
            return accept in ['y', 'yes', 's', 'sim']
        except (KeyboardInterrupt, EOFError):
            return False
        except SystemExit:
            raise
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False
    
    def run(self):
        """Método principal de execução"""
        try:
            self.display_welcome()
            
            if not self.get_user_agreement():
                print("🚫 Access denied. Exiting.")
                return
            
            # Loop principal
            while True:
                try:
                    config = self.menu.get_attack_config()
                    
                    # Validação adicional do alvo
                    if not self.validator.validate_target(config.target_ip):
                        print("❌ Invalid target! Please check the IP/domain.")
                        continue
                    
                    # Executa ataque REAL
                    self.execute_real_attack(config)
                    
                    # Pergunta se quer continuar
                    try:
                        again = self._safe_input("\n🔄 Run another attack? (y/n): ").lower()
                        if again not in ['y', 'yes', 's', 'sim']:
                            break
                    except SystemExit:
                        break
                        
                except (KeyboardInterrupt, EOFError):
                    print("\n\n⏹️  Operation cancelled.")
                    break
                except SystemExit:
                    break
                except Exception as e:
                    print(f"\n❌ Error: {e}")
                    import traceback
                    traceback.print_exc()
                    continue
        
            print("\n🎉 Thank you for using CRYSIS!")
            
        except Exception as e:
            print(f"\n💥 Critical error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self._safe_restore_signal_handler()
    
    def execute_real_attack(self, config):
        """Executa um ataque REAL com otimizações de performance"""
        
        # OTIMIZAÇÃO: Aumenta limites do sistema para mais performance
        try:
            import resource
            # Aumenta limite de arquivos abertos
            resource.setrlimit(resource.RLIMIT_NOFILE, (10000, 10000))
            print("🔧 Limites de sistema otimizados")
        except:
            print("⚠️  Não foi possível otimizar limites do sistema")
            pass
        
        # Configuração de socket para melhor performance
        import socket
        socket.setdefaulttimeout(2)  # Timeout global reduzido
        
        # Prepara estatísticas
        self.stats = AttackStats()
        self.stats.start_time = time.time()
        self.stop_event.clear()
        self.running = True
        
        try:
            # Cria o ataque usando a factory
            attack = self.attack_factory.create_attack(
                config.attack_type.value, 
                config, 
                self.stats
            )
            
            # Configura o stop_event no ataque
            attack.stop_event = self.stop_event
            
            # Mostra informações do ataque
            self._show_attack_info(config)
            
            # Inicia monitor de progresso em thread separada
            monitor_thread = threading.Thread(
                target=self._progress_monitor, 
                args=(config.duration,),
                name="ProgressMonitor"
            )
            monitor_thread.daemon = True
            monitor_thread.start()
            
            # Executa o ataque
            print("⚡ Iniciando ataque...")
            attack.execute()
            
        except KeyboardInterrupt:
            print(f"\n🛑 Attack interrupted by user")
        except Exception as e:
            print(f"\n❌ Attack error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Para o ataque
            self.stop_attack()
            
            # Aguarda um pouco para estatísticas finais
            time.sleep(1)
            
            # Mostra resumo final
            self._show_final_summary()
    
    def _show_attack_info(self, config):
        """Exibe informações do ataque"""
        print(f"\n🎯 STARTING REAL ATTACK: {config.attack_type.name}")
        print(f"🎯 Target: {config.target_ip}:{config.target_port}")
        print(f"⏰ Duration: {config.duration}s")
        print(f"🧵 Threads: {config.threads}")
        print(f"📦 Packet Size: {config.packet_size} bytes")
        print(f"🎭 IP Spoofing: {config.spoof_ip}")
        print(f"🔗 Proxy Chain: {config.use_proxy}")
        if config.use_proxy and config.proxy_type:
            print(f"🔧 Proxy Type: {config.proxy_type}")
        print(f"🎲 Randomize: {config.randomize_packets}")
        print("=" * 60)
        print("⚡ Press Ctrl+C to stop the attack")
        print("=" * 60)
    
    def _progress_monitor(self, duration: int):
        """Monitora progresso do ataque em tempo real"""
        start_time = time.time()
        last_update = start_time
        
        while self.running and (time.time() - start_time) < duration:
            try:
                current_stats = self.stats.get_stats()
                current_time = time.time()
                elapsed = current_time - current_stats['start_time']
                
                if elapsed > 0 and (current_time - last_update) >= 0.5:
                    packets_per_sec = current_stats['packets_sent'] / elapsed
                    mbps = (current_stats['bytes_sent'] * 8) / (elapsed * 1000000)
                    success_rate = 100 - (current_stats['errors'] / max(current_stats['packets_sent'], 1) * 100) if current_stats['packets_sent'] > 0 else 100
                    
                    progress_line = (
                        f"📊 Packets: {current_stats['packets_sent']:,} | "
                        f"Errors: {current_stats['errors']} | "
                        f"Speed: {packets_per_sec:.1f} pps | "
                        f"Bandwidth: {mbps:.2f} Mbps | "
                        f"Success: {success_rate:.1f}%"
                    )
                    
                    print(f"\r{progress_line}", end="", flush=True)
                    last_update = current_time
                
                time.sleep(0.1)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                # Ignora erros no monitor para não travar o ataque
                continue
        
        print()  # Nova linha após o progresso
    
    def _show_final_summary(self):
        """Exibe resumo final do ataque"""
        # Aguarda um momento para estatísticas finais se estabilizarem
        time.sleep(0.5)
        
        final_stats = self.stats.get_stats()
        duration = time.time() - final_stats['start_time']
        
        print(f"\n{'='*70}")
        print("📈 FINAL ATTACK REPORT")
        print(f"{'='*70}")
        print(f"📦 Total Packets: {final_stats['packets_sent']:,}")
        print(f"💾 Total Bytes: {final_stats['bytes_sent']:,}")
        print(f"❌ Errors: {final_stats['errors']}")
        print(f"⏱️  Duration: {duration:.2f}s")
        
        if duration > 0:
            avg_speed = final_stats['packets_sent'] / duration
            bandwidth = (final_stats['bytes_sent'] * 8) / (duration * 1000000)
            print(f"⚡ Average Speed: {avg_speed:.1f} pps")
            print(f"🌊 Bandwidth: {bandwidth:.2f} Mbps")
            
            if final_stats['packets_sent'] > 0:
                success_rate = 100 - (final_stats['errors'] / final_stats['packets_sent'] * 100)
                print(f"🎯 Success Rate: {success_rate:.1f}%")
        
        print(f"{'='*70}")
    
    def stop_attack(self):
        """Para o ataque atual de forma segura"""
        self.running = False
        self.stop_event.set()
        
        # Pequena pausa para threads terminarem
        time.sleep(0.5)

def main():
    """Função principal"""
    try:
        crysis = Crysis()
        crysis.run()
    except KeyboardInterrupt:
        print("\n\n👋 Programa encerrado pelo usuário")
    except Exception as e:
        print(f"\n💥 Erro fatal: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
