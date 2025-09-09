#!/usr/bin/env python3

import json
from whatsapp_analyzer import WhatsAppChatAnalyzer
from ai_analyzer import EnhancedWhatsAppAnalyzer, AIAnalysisConfig

def print_section(title: str, data: dict):
    print(f"\n{'='*50}")
    print(f" {title.upper()}")
    print('='*50)
    
    for key, value in data.items():
        if isinstance(value, dict):
            print(f"\n{key.replace('_', ' ').title()}:")
            for sub_key, sub_value in value.items():
                print(f"  {sub_key}: {sub_value}")
        elif isinstance(value, list):
            print(f"\n{key.replace('_', ' ').title()}:")
            for item in value:
                print(f"  • {item}")
        else:
            print(f"{key.replace('_', ' ').title()}: {value}")

def test_analyzer():
    print("WhatsApp Chat Analyzer - Test Run")
    print("=" * 50)
    
    # Test without AI (no API key)
    ai_config = AIAnalysisConfig(api_key=None)
    
    base_analyzer = WhatsAppChatAnalyzer()
    analyzer = EnhancedWhatsAppAnalyzer(base_analyzer, ai_config)
    
    # Try to load conversa1.txt
    try:
        print("\nTentando carregar conversa1.txt...")
        with open("conversa1.txt", 'r', encoding='utf-8') as file:
            # Read only first 1000 lines to avoid memory issues
            lines = file.readlines()[:1000]
            chat_text = ''.join(lines)
        
        print(f"Carregadas {len(lines)} linhas da conversa1.txt")
        
    except FileNotFoundError:
        print("Arquivo conversa1.txt não encontrado, usando dados de exemplo...")
        
        # Sample WhatsApp conversation data
        chat_text = """25/10/2023 09:15 - João: Oi! Como você está?
25/10/2023 09:17 - Maria: Oi João! Estou bem, obrigada! E você?
25/10/2023 09:18 - João: Também estou ótimo! O que você vai fazer hoje?
25/10/2023 09:20 - Maria: Vou trabalhar pela manhã, mas à tarde estou livre. Por que?
25/10/2023 09:22 - João: Pensei em convidar você para um café ☕
25/10/2023 09:23 - Maria: Adoraria! 😊 Que horas seria bom para você?
25/10/2023 09:25 - João: Que tal às 15h no café da esquina?
25/10/2023 09:26 - Maria: Perfeito! Nos vemos lá então
25/10/2023 09:27 - João: Combinado! Até mais tarde 👋
25/10/2023 09:28 - Maria: Até! ❤️
25/10/2023 15:45 - João: Já estou chegando no café!
25/10/2023 15:46 - Maria: Eu também! Te vejo em 2 minutos
25/10/2023 18:30 - Maria: Muito obrigada pelo café! Foi muito legal conversar
25/10/2023 18:32 - João: Eu que agradeço! Foi ótimo te conhecer melhor
25/10/2023 18:33 - Maria: Com certeza! Vamos repetir em breve?
25/10/2023 18:35 - João: Claro! Que tal no fim de semana?
25/10/2023 18:36 - Maria: Adorei a ideia! Me manda uma mensagem na sexta?
25/10/2023 18:37 - João: Pode deixar! Tenha uma ótima noite
25/10/2023 18:38 - Maria: Você também! Até sexta 🥰"""
    
    except Exception as e:
        print(f"Erro ao ler arquivo: {e}")
        return
    
    # Parse and analyze the chat
    print("\nProcessando conversa...")
    base_analyzer.parse_chat(chat_text)
    
    if not base_analyzer.messages:
        print("Nenhuma mensagem foi encontrada. Verifique o formato do texto.")
        return
    
    print(f"Encontradas {len(base_analyzer.messages)} mensagens de {len(base_analyzer.participants)} participantes")
    
    # Generate comprehensive report with AI
    print("Gerando análise completa...")
    report = analyzer.generate_enhanced_report()
    
    # Display results
    print_section("ANÁLISE LINGUÍSTICA", report["linguistic_analysis"])
    print_section("ANÁLISE PSICOLÓGICA", report["psychological_analysis"])
    print_section("ANÁLISE DE COMUNICAÇÃO", report["communication_analysis"])
    print_section("INSIGHTS DE RELACIONAMENTO", report["relationship_insights"])
    
    # Display AI analysis
    if "ai_analysis" in report:
        ai_data = report["ai_analysis"]
        if ai_data.get("ai_availability", False):
            print_section("ANÁLISE COM IA - SENTIMENTO", ai_data["sentiment_analysis"])
            print_section("ANÁLISE COM IA - DINÂMICA DE RELACIONAMENTO", ai_data["relationship_dynamics"])
            print_section("ANÁLISE COM IA - INSIGHTS DE COMUNICAÇÃO", ai_data["communication_insights"])
        else:
            print_section("ANÁLISE BÁSICA (SEM IA)", ai_data.get("sentiment_analysis", {}))
    
    # Save report
    filename = "test_analysis_report.json"
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\nRelatório salvo em: {filename}")
    except Exception as e:
        print(f"Erro ao salvar arquivo: {e}")
    
    print("\nAnálise concluída!")

if __name__ == "__main__":
    test_analyzer()