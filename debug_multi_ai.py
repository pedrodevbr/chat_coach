#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive debug script for multi-AI integration
"""
import sys
import os
import logging

# Set UTF-8 encoding for Windows
if sys.platform.startswith('win'):
    os.system('chcp 65001 > nul 2>&1')
    sys.stdout.reconfigure(encoding='utf-8')

# Configure debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug_comprehensive.log'),
        logging.StreamHandler()
    ]
)

def test_imports():
    """Test all critical imports"""
    print("=" * 60)
    print("🧪 TESTING IMPORTS")
    print("=" * 60)
    
    try:
        from multi_ai_analyzer import MultiAIWhatsAppAnalyzer, BaseAIProvider, AIModelConfig
        print("✅ Multi-AI analyzer imports successful")
    except Exception as e:
        print(f"❌ Multi-AI imports failed: {e}")
        return False
    
    try:
        from whatsapp_analyzer import WhatsAppChatAnalyzer, WhatsAppMessage
        print("✅ WhatsApp analyzer imports successful")
    except Exception as e:
        print(f"❌ WhatsApp analyzer imports failed: {e}")
    
    try:
        from viral_metrics import ViralMetrics
        print("✅ Viral metrics imports successful")
    except Exception as e:
        print(f"❌ Viral metrics imports failed: {e}")
    
    return True

def test_ai_libraries():
    """Test AI library availability"""
    print("\n" + "=" * 60)
    print("🔍 TESTING AI LIBRARY AVAILABILITY")
    print("=" * 60)
    
    libraries = {
        'OpenAI': 'openai',
        'Gemini': 'google.generativeai',
        'Claude': 'anthropic',
        'Requests (for Grok)': 'requests'
    }
    
    for name, lib in libraries.items():
        try:
            __import__(lib)
            print(f"✅ {name} library available")
        except ImportError as e:
            print(f"❌ {name} library not available: {e}")

def test_multi_ai_configuration():
    """Test multi-AI analyzer configuration"""
    print("\n" + "=" * 60)
    print("🔧 TESTING MULTI-AI CONFIGURATION")
    print("=" * 60)
    
    try:
        from multi_ai_analyzer import MultiAIWhatsAppAnalyzer, AIModelConfig
        
        # Initialize analyzer
        analyzer = MultiAIWhatsAppAnalyzer()
        print("✅ MultiAIWhatsAppAnalyzer initialized")
        
        # Test model configurations (without real API keys)
        models_to_test = ['openai', 'gemini', 'claude', 'grok']
        
        for model_type in models_to_test:
            try:
                config = AIModelConfig(model_type=model_type, api_key="test_key")
                success = analyzer.add_model(model_type, config)
                print(f"{'✅' if success else '⚠️'} {model_type.title()} configuration: {success}")
            except Exception as e:
                print(f"❌ {model_type.title()} configuration error: {e}")
        
        # Test available models
        try:
            available = analyzer.get_available_models()
            print(f"📊 Available models: {len(available)}")
            for model in available:
                status = "✅ Available" if model.get('available', False) else "❌ Not available"
                print(f"   • {model.get('name', 'Unknown')}: {status}")
        except Exception as e:
            print(f"❌ Error getting available models: {e}")
        
        return analyzer
    except Exception as e:
        print(f"❌ Multi-AI configuration error: {e}")
        return None

def test_whatsapp_analysis():
    """Test WhatsApp analysis functionality"""
    print("\n" + "=" * 60)
    print("💬 TESTING WHATSAPP ANALYSIS")
    print("=" * 60)
    
    try:
        from whatsapp_analyzer import WhatsAppChatAnalyzer
        
        # Sample conversation
        sample_chat = """25/10/2023 09:15 - João: Oi! Como você está?
25/10/2023 09:17 - Maria: Oi João! Estou bem, obrigada! E você? 😊
25/10/2023 09:18 - João: Também estou ótimo! O que você vai fazer hoje?
25/10/2023 09:20 - Maria: Vou trabalhar pela manhã, mas à tarde estou livre. Por que?
25/10/2023 09:22 - João: Pensei em convidar você para um café ☕"""
        
        analyzer = WhatsAppChatAnalyzer()
        analyzer.parse_chat(sample_chat)
        
        print(f"✅ Parsed {len(analyzer.messages)} messages from {len(analyzer.participants)} participants")
        return analyzer
        
    except Exception as e:
        print(f"❌ WhatsApp analysis error: {e}")
        return None

def test_viral_features():
    """Test viral features"""
    print("\n" + "=" * 60)
    print("🎯 TESTING VIRAL FEATURES")
    print("=" * 60)
    
    try:
        # Use WhatsApp analyzer from previous test
        whatsapp_analyzer = test_whatsapp_analysis()
        if not whatsapp_analyzer:
            return False
        
        from viral_metrics import ViralMetrics
        viral_metrics = ViralMetrics(whatsapp_analyzer)
        
        # Test relationship score
        relationship_data = viral_metrics.generate_relationship_score()
        if "error" not in relationship_data:
            print(f"✅ Relationship score: {relationship_data['total_score']}/100")
        else:
            print(f"⚠️ Relationship score error: {relationship_data['error']}")
        
        # Test chat personality
        personality_data = viral_metrics.generate_chat_personality()
        print(f"✅ Chat personality: {personality_data['archetype']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Viral features error: {e}")
        return False

def test_logging_system():
    """Test the logging system"""
    print("\n" + "=" * 60)
    print("📝 TESTING LOGGING SYSTEM")
    print("=" * 60)
    
    try:
        # Test if log files can be created
        test_logger = logging.getLogger('debug_test')
        test_logger.info("Testing logging system")
        
        # Check if log files exist
        log_files = ['multi_ai_debug.log', 'debug_comprehensive.log']
        for log_file in log_files:
            if os.path.exists(log_file):
                print(f"✅ Log file created: {log_file}")
            else:
                print(f"ℹ️ Log file not yet created: {log_file}")
        
        return True
    except Exception as e:
        print(f"❌ Logging system error: {e}")
        return False

def main():
    """Main debug function"""
    print("🚀 COMPREHENSIVE MULTI-AI DEBUG TEST")
    print("This will test all components and generate detailed logs")
    
    results = {
        'imports': test_imports(),
        'ai_libraries': test_ai_libraries(),
        'multi_ai_config': test_multi_ai_configuration(),
        'whatsapp_analysis': test_whatsapp_analysis(),
        'viral_features': test_viral_features(),
        'logging_system': test_logging_system()
    }
    
    print("\n" + "=" * 60)
    print("📊 DEBUG RESULTS SUMMARY")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    passed_tests = sum(1 for r in results.values() if r)
    total_tests = len(results)
    
    print(f"\n🎯 Overall Result: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL SYSTEMS READY!")
        print("✅ Multi-AI WhatsApp analyzer is fully functional")
    else:
        print("⚠️ Some components need attention")
        print("📝 Check the log files for detailed error information")
    
    print("\n📁 Log files generated:")
    print("• debug_comprehensive.log - Complete debug log")
    print("• multi_ai_debug.log - Multi-AI specific logs")
    print("• streamlit_app_debug.log - Streamlit app logs")

if __name__ == "__main__":
    main()