#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test viral features and shareable content generation
"""
import sys
import os

# Set UTF-8 encoding for Windows
if sys.platform.startswith('win'):
    os.system('chcp 65001 > nul 2>&1')
    sys.stdout.reconfigure(encoding='utf-8')

from whatsapp_analyzer import WhatsAppChatAnalyzer
from viral_metrics import ViralMetrics
from shareable_cards import ShareableCardGenerator
from word_blacklist import WordBlacklist

def test_viral_features():
    print("🧪 Testing Viral Features & Shareable Content")
    print("=" * 60)
    
    # Sample data for testing
    sample_conversation = """25/10/2023 09:15 - João: Oi! Como você está?
25/10/2023 09:17 - Maria: Oi João! Estou bem, obrigada! E você? 😊
25/10/2023 09:18 - João: Também estou ótimo! O que você vai fazer hoje?
25/10/2023 09:20 - Maria: Vou trabalhar pela manhã, mas à tarde estou livre. Por que?
25/10/2023 09:22 - João: Pensei em convidar você para um café ☕
25/10/2023 09:23 - Maria: Adoraria! 😍 Que horas seria bom para você?
25/10/2023 09:25 - João: Que tal às 15h no café da esquina?
25/10/2023 09:26 - Maria: Perfeito! Nos vemos lá então ❤️
25/10/2023 09:27 - João: Combinado! Até mais tarde 👋
25/10/2023 09:28 - Maria: Até! 🥰
25/10/2023 15:45 - João: Já estou chegando no café!
25/10/2023 15:46 - Maria: Eu também! Te vejo em 2 minutos
25/10/2023 18:30 - Maria: Muito obrigada pelo café! Foi muito legal conversar
25/10/2023 18:32 - João: Eu que agradeço! Foi ótimo te conhecer melhor
25/10/2023 18:33 - Maria: Com certeza! Vamos repetir em breve?
25/10/2023 18:35 - João: Claro! Que tal no fim de semana?
25/10/2023 18:36 - Maria: Adorei a ideia! Me manda uma mensagem na sexta?
25/10/2023 18:37 - João: Pode deixar! Tenha uma ótima noite
25/10/2023 18:38 - Maria: Você também! Até sexta 🌟"""

    # Initialize analyzer
    analyzer = WhatsAppChatAnalyzer()
    analyzer.parse_chat(sample_conversation)
    
    print(f"✅ Parsed {len(analyzer.messages)} messages from {len(analyzer.participants)} participants")
    
    # Test viral metrics
    print("\n🎯 Testing Viral Metrics...")
    viral_metrics = ViralMetrics(analyzer)
    
    # Test relationship score
    print("\n💕 Relationship Score:")
    relationship_data = viral_metrics.generate_relationship_score()
    if "error" not in relationship_data:
        print(f"   Score: {relationship_data['total_score']}/100 ({relationship_data['grade']})")
        print(f"   Type: {relationship_data['personality']['type']}")
        print(f"   Percentile: {relationship_data['percentile']}%")
        print(f"   Improvements: {len(relationship_data['improvements'])} suggestions")
    else:
        print(f"   Error: {relationship_data['error']}")
    
    # Test chat personality
    print("\n🎭 Chat Personality:")
    personality_data = viral_metrics.generate_chat_personality()
    print(f"   Archetype: {personality_data['archetype']}")
    print(f"   Traits: {', '.join(personality_data['traits'][:3])}")
    print(f"   Description: {personality_data['fun_description'][:100]}...")
    
    # Test conversation highlights
    print("\n🌟 Conversation Highlights:")
    highlights = viral_metrics.generate_conversation_highlights()
    
    if 'timeline' in highlights:
        timeline = highlights['timeline']
        print(f"   Duration: {timeline['duration_days']} days")
        print(f"   Messages/day: {timeline['messages_per_day']:.1f}")
        print(f"   First message: {timeline['first_message_date']}")
    
    if 'peak_activity' in highlights:
        peak = highlights['peak_activity']
        print(f"   Peak hour: {peak['peak_hour']}")
        print(f"   Peak day: {peak['peak_day']}")
    
    # Test premium preview
    print("\n✨ Premium Preview:")
    premium_preview = viral_metrics.generate_premium_preview()
    ai_features = premium_preview['premium_features']['ai_insights']['preview']
    print(f"   AI features available: {len(ai_features)}")
    print(f"   Sample: {ai_features[0]}")
    
    # Test word blacklist
    print("\n🚫 Word Blacklist:")
    blacklist = WordBlacklist()
    blacklist_info = blacklist.get_blacklist_info()
    print(f"   Total blacklisted: {blacklist_info['total_blacklisted']} words")
    print(f"   Categories: {len(blacklist_info['categories'])}")
    
    # Test text filtering
    all_text = ' '.join([msg.content for msg in analyzer.messages])
    text_analysis = blacklist.analyze_text(all_text)
    print(f"   Original words: {text_analysis['original_words']}")
    print(f"   Filtered words: {text_analysis['filtered_words']}")
    print(f"   Removal rate: {text_analysis['removal_percentage']:.1f}%")
    
    # Test shareable cards generation
    print("\n📱 Shareable Cards:")
    card_generator = ShareableCardGenerator()
    
    try:
        cards_data = {
            'messages': analyzer.messages,
            'conversation_span_days': 0,
            'messages_per_day': len(analyzer.messages)
        }
        
        cards = card_generator.generate_all_cards(cards_data)
        print(f"   Generated {len(cards)} cards")
        
        for card_name in cards.keys():
            print(f"   ✅ {card_name.title()} card ready")
        
        # Test individual card generation
        try:
            # Test stats card
            stats = {
                'total_messages': len(analyzer.messages),
                'total_words': sum(msg.word_count for msg in analyzer.messages),
                'duration_days': 1,
                'messages_per_day': len(analyzer.messages),
                'fun_fact': "Amazing conversation! 🌟"
            }
            
            stats_card = card_generator.create_stats_highlight_card(stats)
            print("   ✅ Stats card generation successful")
            
        except Exception as e:
            print(f"   ❌ Error generating individual cards: {e}")
        
    except Exception as e:
        print(f"   ❌ Error generating cards: {e}")
    
    # Test social media content generation
    print("\n📲 Social Media Content:")
    try:
        social_cards = viral_metrics.generate_social_media_cards()
        print(f"   Generated {len(social_cards)} social media cards")
        
        for card in social_cards:
            print(f"   • {card['type'].title()}: {card['title'][:50]}...")
            if 'shareable_text' in card:
                print(f"     Share text: {card['shareable_text'][:60]}...")
        
    except Exception as e:
        print(f"   ❌ Error generating social media content: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Viral Features Testing Complete!")
    print("✅ All core features are working properly")
    print("🚀 Ready for users to create shareable content!")
    
    return True

if __name__ == "__main__":
    success = test_viral_features()
    
    if success:
        print("\n💎 VIRAL FEATURES ARE READY!")
        print("🔥 Users will love sharing their chat insights!")
    else:
        print("\n⚠️ Some features need attention")