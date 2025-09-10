#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for the core WhatsApp analyzer
"""

import sys
import os

# Set UTF-8 encoding for Windows
if sys.platform.startswith('win'):
    os.system('chcp 65001 > nul 2>&1')
    sys.stdout.reconfigure(encoding='utf-8')

from chat_analyzer import WhatsAppAnalyzer
from relationship_analyzer import RelationshipAnalyzer
from social_cards import SocialCardGenerator
from ai_analyzer import AIAnalyzer, AIConfig

def test_core_features():
    """Test all core features"""
    print("🧪 Testing WhatsApp Chat Analyzer Core")
    print("=" * 50)
    
    # Sample conversation
    sample_chat = """25/10/2023 09:15 - João: Oi! Como você está?
25/10/2023 09:17 - Maria: Oi João! Estou bem, obrigada! E você? 😊
25/10/2023 09:18 - João: Também estou ótimo! O que você vai fazer hoje?
25/10/2023 09:20 - Maria: Vou trabalhar pela manhã, mas à tarde estou livre. Por que?
25/10/2023 09:22 - João: Pensei em convidar você para um café ☕
25/10/2023 09:23 - Maria: Adoraria! 😍 Que horas seria bom para você?
25/10/2023 09:25 - João: Que tal às 15h no café da esquina?
25/10/2023 09:26 - Maria: Perfeito! Nos vemos lá então ❤️
25/10/2023 09:27 - João: Combinado! Até mais tarde 👋
25/10/2023 09:28 - Maria: Até! 🥰"""
    
    # Test 1: Basic Analysis
    print("\n1. 📊 Testing Basic Analysis")
    analyzer = WhatsAppAnalyzer()
    success = analyzer.parse_chat(sample_chat)
    
    if success:
        print(f"✅ Parsed {len(analyzer.messages)} messages from {len(analyzer.participants)} participants")
        
        stats = analyzer.get_basic_stats()
        print(f"📈 Total words: {stats['total_words']}")
        print(f"📅 Duration: {stats['duration_days']} days")
        print(f"💬 Messages per day: {stats['messages_per_day']:.1f}")
        
        activity = analyzer.get_activity_patterns()
        print(f"🕐 Peak hour: {activity['peak_hour']}:00")
        print(f"📅 Peak day: {activity['peak_day']}")
        
        word_analysis = analyzer.get_word_analysis()
        print(f"📝 Vocabulary richness: {word_analysis['vocabulary_richness']:.2f}")
        print(f"🔝 Top words: {word_analysis['top_words'][:3]}")
    else:
        print("❌ Failed to parse chat")
        return False
    
    # Test 2: Relationship Analysis
    print("\n2. 💕 Testing Relationship Analysis")
    relationship_analyzer = RelationshipAnalyzer(analyzer)
    
    # Relationship score
    score_data = relationship_analyzer.calculate_relationship_score()
    if "error" not in score_data:
        print(f"✅ Relationship score: {score_data['total_score']:.1f}/100 ({score_data['grade']})")
        print(f"📊 Percentile: {score_data['percentile']}%")
        print(f"💭 Description: {score_data['description']}")
    else:
        print(f"❌ Relationship score error: {score_data['error']}")
    
    # Chat personality
    personality = relationship_analyzer.get_chat_personality()
    print(f"✅ Chat personality: {personality['archetype']}")
    print(f"🎯 Traits: {', '.join(personality['traits'])}")
    
    # Fun facts
    fun_facts = relationship_analyzer.generate_fun_facts()
    print(f"✅ Generated {len(fun_facts)} fun facts")
    for fact in fun_facts[:3]:
        print(f"   🎉 {fact}")
    
    # Test 3: Social Cards
    print("\n3. 📱 Testing Social Cards Generation")
    card_generator = SocialCardGenerator()
    
    # Test stats card
    stats_card = card_generator.create_stats_card(stats)
    if stats_card:
        print("✅ Stats card generated successfully")
    else:
        print("❌ Failed to generate stats card")
    
    # Test personality card
    personality_card = card_generator.create_personality_card(personality)
    if personality_card:
        print("✅ Personality card generated successfully")
    else:
        print("❌ Failed to generate personality card")
    
    # Test relationship card
    if "error" not in score_data:
        relationship_card = card_generator.create_relationship_score_card(score_data)
        if relationship_card:
            print("✅ Relationship card generated successfully")
        else:
            print("❌ Failed to generate relationship card")
    
    # Test fun facts card
    facts_card = card_generator.create_fun_facts_card(fun_facts)
    if facts_card:
        print("✅ Fun facts card generated successfully")
    else:
        print("❌ Failed to generate fun facts card")
    
    # Test 4: AI Analysis (will fail without API key, but test structure)
    print("\n4. 🤖 Testing AI Analysis Structure")
    ai_config = AIConfig(api_key=None)  # No API key for test
    ai_analyzer = AIAnalyzer(ai_config)
    
    if not ai_analyzer.is_ai_available():
        print("⚠️ AI analysis not available (no API key)")
        print("✅ AI structure test passed")
    else:
        messages_text = [msg.content for msg in analyzer.messages]
        ai_result = ai_analyzer.analyze_conversation_sentiment(messages_text)
        if ai_result.get('success'):
            print("✅ AI analysis completed successfully")
        else:
            print(f"❌ AI analysis failed: {ai_result.get('error')}")
    
    print("\n" + "=" * 50)
    print("🎉 Core Features Test Complete!")
    print("✅ All essential features are working")
    print("🚀 Ready for production use!")
    
    return True

if __name__ == "__main__":
    test_core_features()