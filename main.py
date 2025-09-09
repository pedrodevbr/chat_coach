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

def main():
    print("WhatsApp Chat Analyzer - MVP com IA")
    print("=" * 50)
    
    # Check for AI configuration
    ai_key = input("Chave da API OpenAI (opcional, Enter para pular): ").strip()
    ai_config = AIAnalysisConfig(api_key=ai_key if ai_key else None)
    
    # Option 1: Read from file
    print("\nOpções:")
    print("1. Carregar conversa de arquivo")
    print("2. Usar dados de exemplo")
    print("3. Inserir texto manualmente")
    print("4. Testar com conversa1.txt")
    print("5. Testar com conversa2.txt")
    
    choice = input("\nEscolha uma opção (1-5): ").strip()
    
    base_analyzer = WhatsAppChatAnalyzer()
    analyzer = EnhancedWhatsAppAnalyzer(base_analyzer, ai_config)
    
    if choice == "1":
        file_path = input("Digite o caminho do arquivo: ").strip()
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                chat_text = file.read()
        except FileNotFoundError:
            print(f"Arquivo não encontrado: {file_path}")
            return
        except Exception as e:
            print(f"Erro ao ler arquivo: {e}")
            return
    
    elif choice == "2":
        # Sample WhatsApp conversation data
        chat_text = """25/10/2023, 09:15 - João: Oi! Como você está?
25/10/2023, 09:17 - Maria: Oi João! Estou bem, obrigada! E você?
25/10/2023, 09:18 - João: Também estou ótimo! O que você vai fazer hoje?
25/10/2023, 09:20 - Maria: Vou trabalhar pela manhã, mas à tarde estou livre. Por que?
25/10/2023, 09:22 - João: Pensei em convidar você para um café ☕
25/10/2023, 09:23 - Maria: Adoraria! 😊 Que horas seria bom para você?
25/10/2023, 09:25 - João: Que tal às 15h no café da esquina?
25/10/2023, 09:26 - Maria: Perfeito! Nos vemos lá então
25/10/2023, 09:27 - João: Combinado! Até mais tarde 👋
25/10/2023, 09:28 - Maria: Até! ❤️
25/10/2023, 15:45 - João: Já estou chegando no café!
25/10/2023, 15:46 - Maria: Eu também! Te vejo em 2 minutos
25/10/2023, 18:30 - Maria: Muito obrigada pelo café! Foi muito legal conversar
25/10/2023, 18:32 - João: Eu que agradeço! Foi ótimo te conhecer melhor
25/10/2023, 18:33 - Maria: Com certeza! Vamos repetir em breve?
25/10/2023, 18:35 - João: Claro! Que tal no fim de semana?
25/10/2023, 18:36 - Maria: Adorei a ideia! Me manda uma mensagem na sexta?
25/10/2023, 18:37 - João: Pode deixar! Tenha uma ótima noite
25/10/2023, 18:38 - Maria: Você também! Até sexta 🥰"""
        
        print("\nUsando conversa de exemplo...")
    
    elif choice == "3":
        print("\nCole o texto da conversa do WhatsApp (pressione Enter duas vezes para finalizar):")
        lines = []
        empty_line_count = 0
        
        while True:
            line = input()
            if line == "":
                empty_line_count += 1
                if empty_line_count >= 2:
                    break
            else:
                empty_line_count = 0
                lines.append(line)
        
        chat_text = "\n".join(lines)
    
    elif choice == "4":
        try:
            with open("conversa1.txt", 'r', encoding='utf-8') as file:
                chat_text = file.read()
            print("Carregando conversa1.txt...")
        except FileNotFoundError:
            print("Arquivo conversa1.txt não encontrado!")
            return
        except Exception as e:
            print(f"Erro ao ler conversa1.txt: {e}")
            return
    
    elif choice == "5":
        try:
            with open("conversa2.txt", 'r', encoding='utf-8') as file:
                chat_text = file.read()
            print("Carregando conversa2.txt...")
        except FileNotFoundError:
            print("Arquivo conversa2.txt não encontrado!")
            return
        except Exception as e:
            print(f"Erro ao ler conversa2.txt: {e}")
            return
    
    else:
        print("Opção inválida!")
        return
    
    # Parse and analyze the chat
    print("\nProcessando conversa...")
    base_analyzer.parse_chat(chat_text)
    
    if not base_analyzer.messages:
        print("Nenhuma mensagem foi encontrada. Verifique o formato do texto.")
        return
    
    # Generate comprehensive report with AI
    print("Gerando análise completa (incluindo IA se disponível)...")
    report = analyzer.generate_enhanced_report()
    
    # Display results
    print_section("ANÁLISE LINGUÍSTICA", report["linguistic_analysis"])
    print_section("ANÁLISE PSICOLÓGICA", report["psychological_analysis"])
    print_section("ANÁLISE DE COMUNICAÇÃO", report["communication_analysis"])
    print_section("INSIGHTS DE RELACIONAMENTO", report["relationship_insights"])
    
    # Display AI analysis if available
    if "ai_analysis" in report:
        ai_data = report["ai_analysis"]
        if ai_data.get("ai_availability", False):
            print_section("ANÁLISE COM IA - SENTIMENTO", ai_data["sentiment_analysis"])
            print_section("ANÁLISE COM IA - DINÂMICA DE RELACIONAMENTO", ai_data["relationship_dynamics"])
            print_section("ANÁLISE COM IA - INSIGHTS DE COMUNICAÇÃO", ai_data["communication_insights"])
        else:
            print_section("ANÁLISE BÁSICA (SEM IA)", ai_data.get("sentiment_analysis", {}))
    
    # Option to save report
    save_report = input("\n\nDeseja salvar o relatório em um arquivo JSON? (s/n): ").strip().lower()
    
    if save_report in ['s', 'sim', 'y', 'yes']:
        filename = input("Nome do arquivo (sem extensão): ").strip()
        if not filename:
            filename = "chat_analysis_report"
        
        filename += ".json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"Relatório salvo em: {filename}")
        except Exception as e:
            print(f"Erro ao salvar arquivo: {e}")
    
    print("\nAnálise concluída!")

if __name__ == "__main__":
    main()