"""
Script para atualização automática de versão
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.version import version_manager

def main():
    if len(sys.argv) > 1:
        action = sys.argv[1]
        if action == "build":
            version_manager.increment_build()
            print(f"✅ Build incremented to: {version_manager.get_version()}")
        elif action == "revision":
            version_manager.increment_revision()
            print(f"✅ Revision incremented to: {version_manager.get_full_version()}")
        elif action == "set" and len(sys.argv) == 5:
            major = int(sys.argv[2])
            minor = int(sys.argv[3])
            build = int(sys.argv[4])
            version_manager.set_version(major, minor, build)
            print(f"✅ Version set to: {version_manager.get_version()}")
        else:
            print("Usage: python update_version.py [build|revision|set major minor build]")
    else:
        print(f"Current version: {version_manager.get_full_version()}")

if __name__ == '__main__':
    main()