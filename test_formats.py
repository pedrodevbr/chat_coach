#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for different WhatsApp timestamp formats
"""
import sys
import os

# Set UTF-8 encoding for Windows
if sys.platform.startswith('win'):
    os.system('chcp 65001 > nul 2>&1')
    sys.stdout.reconfigure(encoding='utf-8')

from whatsapp_analyzer import WhatsAppChatAnalyzer
import datetime

def test_date_formats():
    """Test various WhatsApp date/time formats"""
    
    # Sample conversations in different formats
    test_conversations = {
        "Brazilian Format (DD/MM/YYYY)": """
25/10/2023 09:15 - João: Oi! Como você está?
25/10/2023, 09:17 - Maria: Oi João! Estou bem, obrigada!
25/10/2023 09:18 - João: Também estou ótimo!
""",

        "US Format (MM/DD/YYYY with AM/PM)": """
10/25/2023 9:15 AM - John: Hi! How are you?
10/25/2023, 9:17 AM - Mary: Hi John! I'm doing well, thank you!
10/25/2023 9:18 AM - John: I'm great too!
""",

        "ISO Format (YYYY-MM-DD)": """
2023-10-25 09:15 - João: Oi! Como você está?
2023-10-25, 09:17 - Maria: Oi João! Estou bem, obrigada!
2023-10-25 09:18 - João: Também estou ótimo!
""",

        "Android Dot Format (DD.MM.YYYY)": """
25.10.2023 09:15 - Hans: Hallo! Wie geht es dir?
25.10.2023, 09:17 - Lisa: Hallo Hans! Mir geht es gut, danke!
25.10.2023 09:18 - Hans: Mir geht es auch gut!
""",

        "Dash Format (DD-MM-YYYY)": """
25-10-2023 09:15 - Pierre: Salut! Comment ça va?
25-10-2023, 09:17 - Sophie: Salut Pierre! Ça va bien, merci!
25-10-2023 09:18 - Pierre: Moi aussi ça va bien!
""",

        "Short Year Format (DD/MM/YY)": """
25/10/23 09:15 - Alex: Hey! What's up?
25/10/23, 09:17 - Sam: Hey Alex! Not much, you?
25/10/23 09:18 - Alex: Same here!
""",

        "With Seconds": """
25/10/2023 09:15:30 - Carlos: ¡Hola! ¿Cómo estás?
25/10/2023, 09:17:45 - Ana: ¡Hola Carlos! Estoy bien, ¡gracias!
25/10/2023 09:18:12 - Carlos: ¡Yo también estoy bien!
""",

        "Mixed Format (Real world scenario)": """
25/10/2023 09:15 - João: Oi! Tudo bem?
This is a continuation
of the previous message
25/10/2023, 09:17 - Maria: Oi João! 
Estou bem sim!
E você?
10/25/2023 9:18 AM - John: I'm switching to English
2023-10-25 09:19 - Mixed: Different formats in same chat
25.10.2023, 09:20 - Android: From Android device
""",

        "Complex Real Conversation": """
19/11/2021 15:54 - Pedro: Vai o q?
19/11/2021 15:56 - Anapaula: <Mídia oculta>
19/11/2021 15:56 - Anapaula: <Mídia oculta>
19/11/2021 20:21 - Pedro: Cheguei😀
19/11/2021 20:23 - Anapaula: Indo
22/11/2021 07:24 - Anapaula: Ligação de voz perdida
22/11/2021 07:38 - Anapaula: Ligação de voz perdida
23/11/2021 13:17 - Anapaula: <Mídia oculta>
25/11/2021, 16:55 - Pedro: <Mídia oculta>
25/11/2021 16:55 - Pedro: <Mídia oculta>
04/12/2021 20:29 - Anapaula: Oi meu lindo, querido e amado filho!!!
04/12/2021 21:01 - Pedro: Oie
04/12/2021 21:01 - Pedro: So consegui entrar agira
04/12/2021 21:01 - Pedro: Cheguei da trilha
04/12/2021 21:01 - Pedro: Foi intenso
"""
    }
    
    print("🧪 Testando diferentes formatos de data/hora do WhatsApp")
    print("=" * 80)
    
    total_success = 0
    total_tests = 0
    
    for format_name, conversation in test_conversations.items():
        print(f"\n📅 Testando: {format_name}")
        print("-" * 50)
        
        analyzer = WhatsAppChatAnalyzer()
        analyzer.parse_chat(conversation)
        
        total_tests += 1
        
        if analyzer.messages:
            total_success += 1
            print(f"✅ Sucesso: {len(analyzer.messages)} mensagens encontradas")
            print(f"👥 Participantes: {list(analyzer.participants)}")
            
            # Show first and last timestamps
            first_msg = analyzer.messages[0]
            last_msg = analyzer.messages[-1]
            
            print(f"⏰ Primeira mensagem: {first_msg.timestamp} - {first_msg.sender}: {first_msg.content[:30]}...")
            if len(analyzer.messages) > 1:
                print(f"⏰ Última mensagem: {last_msg.timestamp} - {last_msg.sender}: {last_msg.content[:30]}...")
            
            # Test linguistic analysis
            try:
                analysis = analyzer.linguistic_analysis()
                print(f"📊 Análise: {analysis['total_messages']} mensagens, período de {analysis['conversation_span_days']} dias")
            except Exception as e:
                print(f"⚠️ Erro na análise: {e}")
        else:
            print(f"❌ Falhou: Nenhuma mensagem encontrada")
            # Show raw lines for debugging
            lines = conversation.strip().split('\n')[:3]
            print(f"🔍 Primeiras linhas:")
            for i, line in enumerate(lines, 1):
                print(f"   {i}: {line.strip()}")
    
    print("\n" + "=" * 80)
    print(f"📈 Resultado Final: {total_success}/{total_tests} formatos testados com sucesso")
    print(f"🎯 Taxa de sucesso: {(total_success/total_tests)*100:.1f}%")
    
    if total_success == total_tests:
        print("🎉 Todos os formatos funcionaram perfeitamente!")
    else:
        print("⚠️ Alguns formatos precisam de ajustes.")
    
    return total_success == total_tests

def test_edge_cases():
    """Test edge cases and problematic scenarios"""
    
    print("\n🔬 Testando casos extremos...")
    print("=" * 50)
    
    edge_cases = {
        "Empty lines and spaces": """
        
25/10/2023 09:15 - João: Mensagem com linhas vazias

25/10/2023 09:17 - Maria: Segunda mensagem
        
        """,
        
        "Multiline messages": """
25/10/2023 09:15 - João: Esta é uma mensagem
que continua na próxima linha
e ainda continua aqui
25/10/2023 09:17 - Maria: Mensagem normal
""",
        
        "Special characters": """
25/10/2023 09:15 - João🎉: Mensagem com emoji no nome
25/10/2023 09:17 - Maria: Mensagem com: dois pontos no meio
25/10/2023 09:18 - Pedro-Silva: Nome com traço
""",
        
        "System messages": """
25/10/2023 09:15 - João: Mensagem normal
25/10/2023 09:16 - System: <Mídia oculta>
25/10/2023 09:17 - System: ‎image omitted
25/10/2023 09:18 - Maria: Outra mensagem normal
""",
        
        "Very long names": """
25/10/2023 09:15 - João Pedro Silva Santos da Costa: Nome muito longo aqui
25/10/2023 09:17 - +55 11 99999-9999: Número de telefone
25/10/2023 09:18 - Maria: Resposta normal
"""
    }
    
    for test_name, conversation in edge_cases.items():
        print(f"\n🧪 Teste: {test_name}")
        
        analyzer = WhatsAppChatAnalyzer()
        analyzer.parse_chat(conversation)
        
        print(f"📝 Mensagens encontradas: {len(analyzer.messages)}")
        if analyzer.messages:
            for msg in analyzer.messages:
                print(f"   • {msg.sender}: {msg.content[:50]}{'...' if len(msg.content) > 50 else ''}")

if __name__ == "__main__":
    print("🚀 WhatsApp Format Testing Suite")
    print("=" * 80)
    
    # Test main formats
    success = test_date_formats()
    
    # Test edge cases
    test_edge_cases()
    
    print(f"\n{'🎉 TODOS OS TESTES PASSARAM!' if success else '⚠️ ALGUNS TESTES FALHARAM'}")
    print("=" * 80)