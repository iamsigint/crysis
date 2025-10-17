"""
Script de build para o Crysis
"""
import os
import sys
import subprocess
import shutil
from datetime import datetime

def run_command(cmd, cwd=None):
    """Executa comando e retorna resultado"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    print("🚀 Building Crysis...")
    
    # Verifica se estamos no diretório correto
    if not os.path.exists('src') or not os.path.exists('crysis.py'):
        print("❌ Please run this script from the project root directory")
        return 1
    
    # Cria diretório de build
    build_dir = "build"
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    os.makedirs(build_dir)
    
    # Atualiza versão
    print("📦 Updating version...")
    success, stdout, stderr = run_command("python scripts/update_version.py build")
    if not success:
        print(f"❌ Version update failed: {stderr}")
        return 1
    
    # Executa testes
    print("🧪 Running tests...")
    success, stdout, stderr = run_command("python -m pytest tests/ -v")
    if not success:
        print(f"❌ Tests failed: {stderr}")
        return 1
    
    # Cria pacote de distribuição
    print("📦 Creating distribution package...")
    success, stdout, stderr = run_command("python setup.py sdist bdist_wheel")
    if not success:
        print(f"❌ Package creation failed: {stderr}")
        return 1
    
    # Cria arquivo de instalação
    print("🔧 Creating install script...")
    create_install_script(build_dir)
    
    # Copia arquivos necessários
    print("📁 Copying files...")
    copy_essential_files(build_dir)
    
    print(f"✅ Build completed successfully! Check the '{build_dir}' directory.")
    return 0

def create_install_script(build_dir):
    """Cria script de instalação"""
    install_script = f"""#!/bin/bash
# Crysis Installation Script
# Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

echo "🚀 Installing Crysis..."

# Verifica Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Verifica versão do Python
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
if [ "$(echo '$PYTHON_VERSION < 3.8' | bc)" -eq 1 ]; then
    echo "❌ Python 3.8 or higher is required"
    exit 1
fi

# Instala dependências
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

# Configura permissões
chmod +x crysis.py

echo "✅ Installation completed!"
echo "🎉 Run Crysis with: python3 crysis.py"
"""
    
    with open(os.path.join(build_dir, "install.sh"), "w") as f:
        f.write(install_script)
    
    # Também cria versão Windows
    install_bat = f"""@echo off
REM Crysis Installation Script for Windows
REM Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

echo 🚀 Installing Crysis...

REM Verifica Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is required but not installed
    exit /b 1
)

REM Instala dependências
echo 📦 Installing dependencies...
pip install -r requirements.txt

echo ✅ Installation completed!
echo 🎉 Run Crysis with: python crysis.py
"""
    
    with open(os.path.join(build_dir, "install.bat"), "w") as f:
        f.write(install_bat)

def copy_essential_files(build_dir):
    """Copia arquivos essenciais para o build"""
    essential_files = [
        'crysis.py',
        'requirements.txt', 
        'README.md',
        'CHANGELOG.md',
        'setup.py'
    ]
    
    essential_dirs = [
        'src',
        'data',
        'docs'
    ]
    
    for file in essential_files:
        if os.path.exists(file):
            shutil.copy2(file, build_dir)
    
    for dir in essential_dirs:
        if os.path.exists(dir):
            shutil.copytree(dir, os.path.join(build_dir, dir))

if __name__ == '__main__':
    sys.exit(main())