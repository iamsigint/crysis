"""
Sistema de versionamento para Crysis
"""
import os
import json
from typing import Dict, Tuple

class VersionManager:
    def __init__(self):
        self.version_file = "version.json"
        self.major = 1
        self.minor = 0
        self.build = 1  # Começa com 1
        self.revision = 0
        self.load_version()
    
    def load_version(self):
        """Carrega a versão atual do arquivo"""
        if os.path.exists(self.version_file):
            try:
                with open(self.version_file, 'r') as f:
                    data = json.load(f)
                    self.major = data.get('major', 1)
                    self.minor = data.get('minor', 0)
                    self.build = data.get('build', 1)
                    self.revision = data.get('revision', 0)
            except:
                # Se houver erro no arquivo, usa padrão
                self.save_version()
        else:
            self.save_version()
    
    def save_version(self):
        """Salva a versão atual no arquivo"""
        data = {
            'major': self.major,
            'minor': self.minor,
            'build': self.build,
            'revision': self.revision
        }
        with open(self.version_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_version(self) -> str:
        """Retorna a versão formatada"""
        return f"{self.major}.{self.minor}.{self.build:04d}"
    
    def get_full_version(self) -> str:
        """Retorna a versão completa"""
        return f"{self.major}.{self.minor}.{self.build:04d}.{self.revision:04d}"
    
    def increment_build(self):
        """Incrementa o número do build"""
        self.build += 1
        self.revision = 0
        self.save_version()
    
    def increment_revision(self):
        """Incrementa o número da revisão"""
        self.revision += 1
        self.save_version()
    
    def set_version(self, major: int, minor: int, build: int, revision: int = 0):
        """Define uma versão específica"""
        self.major = major
        self.minor = minor
        self.build = build
        self.revision = revision
        self.save_version()

# Instância global
version_manager = VersionManager()