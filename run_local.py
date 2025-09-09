#!/usr/bin/env python3
"""
Script para testar a aplicação Streamlit localmente
"""

import subprocess
import sys
import os

def check_dependencies():
    """Check if all required packages are installed"""
    required_packages = [
        'streamlit', 'pandas', 'plotly', 'matplotlib', 
        'seaborn', 'wordcloud', 'numpy', 'openai'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} - OK")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - FALTANDO")
    
    if missing_packages:
        print(f"\n📦 Instale os pacotes faltantes:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def test_analyzers():
    """Test if our analyzer modules work"""
    try:
        from whatsapp_analyzer import WhatsAppChatAnalyzer
        from ai_analyzer import EnhancedWhatsAppAnalyzer, AIAnalysisConfig
        print("✅ Módulos do analisador - OK")
        return True
    except Exception as e:
        print(f"❌ Erro nos módulos: {e}")
        return False

def run_streamlit():
    """Run Streamlit app"""
    print("\n🚀 Iniciando dashboard Streamlit...")
    print("📱 Acesse: http://localhost:8501")
    print("⏹️ Para parar: Ctrl+C\n")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port=8501",
            "--server.headless=false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Dashboard encerrado pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao executar Streamlit: {e}")

def main():
    print("🔍 WhatsApp Chat Analyzer - Teste Local")
    print("=" * 50)
    
    # Check dependencies
    print("\n📦 Verificando dependências...")
    if not check_dependencies():
        return
    
    # Test analyzers
    print("\n🧪 Testando módulos...")
    if not test_analyzers():
        return
    
    print("\n✅ Tudo pronto!")
    
    # Run Streamlit
    user_input = input("\n🚀 Deseja iniciar o dashboard? (s/n): ").strip().lower()
    if user_input in ['s', 'sim', 'y', 'yes']:
        run_streamlit()
    else:
        print("👋 Até logo!")

if __name__ == "__main__":
    main()