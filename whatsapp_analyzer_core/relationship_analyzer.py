#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Relationship Analysis - Core viral features
Simple relationship scoring and personality analysis
"""

import random
from typing import Dict, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class RelationshipAnalyzer:
    """Simple relationship analysis for viral features"""
    
    def __init__(self, analyzer):
        self.analyzer = analyzer
        self.messages = analyzer.messages
        self.participants = analyzer.participants
    
    def calculate_relationship_score(self) -> Dict:
        """Calculate a simple relationship compatibility score"""
        if len(self.participants) != 2:
            return {"error": "Relationship score only works for 2-person chats"}
        
        try:
            basic_stats = self.analyzer.get_basic_stats()
            
            # Simple scoring based on various factors
            scores = {}
            
            # Balance score (0-20): How balanced is the conversation
            participant_stats = basic_stats['participant_stats']
            participants = list(self.participants)
            p1_messages = participant_stats[participants[0]]['messages']
            p2_messages = participant_stats[participants[1]]['messages']
            
            total_messages = p1_messages + p2_messages
            if total_messages > 0:
                balance_ratio = min(p1_messages, p2_messages) / max(p1_messages, p2_messages)
                scores['balance'] = balance_ratio * 20
            else:
                scores['balance'] = 0
            
            # Consistency score (0-20): Regular communication
            duration = basic_stats['duration_days']
            if duration > 0:
                consistency = min(basic_stats['messages_per_day'] / 10, 1) * 20
                scores['consistency'] = consistency
            else:
                scores['consistency'] = 20  # Single day gets full points
            
            # Engagement score (0-30): Word count and interaction
            avg_words = basic_stats['avg_words_per_message']
            engagement = min(avg_words / 10, 1) * 30
            scores['engagement'] = engagement
            
            # Response frequency (0-20): How much they talk to each other
            if total_messages > 10:
                frequency_score = min(total_messages / 50, 1) * 20
            else:
                frequency_score = total_messages * 2  # Bonus for starting conversations
            scores['frequency'] = frequency_score
            
            # Variety score (0-10): Different times and patterns
            activity = self.analyzer.get_activity_patterns()
            unique_hours = len(activity.get('hour_distribution', {}))
            variety = (unique_hours / 24) * 10
            scores['variety'] = variety
            
            # Calculate total score
            total_score = sum(scores.values())
            
            # Assign grade
            if total_score >= 85:
                grade = "A+"
                description = "💕 Relacionamento Perfeito"
            elif total_score >= 75:
                grade = "A"
                description = "❤️ Muito Compatíveis"
            elif total_score >= 65:
                grade = "B+"
                description = "😊 Boa Sintonia"
            elif total_score >= 55:
                grade = "B"
                description = "👫 Amigos Próximos"
            elif total_score >= 45:
                grade = "C+"
                description = "🤝 Conhecidos"
            else:
                grade = "C"
                description = "👋 Início da Amizade"
            
            # Calculate percentile (mock calculation for viral effect)
            percentile = min(int(total_score * 1.2), 99)
            
            return {
                'total_score': round(total_score, 1),
                'grade': grade,
                'description': description,
                'percentile': percentile,
                'detailed_scores': {k: round(v, 1) for k, v in scores.items()},
                'improvement_tips': self._get_improvement_tips(scores, total_score)
            }
            
        except Exception as e:
            logger.error(f"Error calculating relationship score: {e}")
            return {"error": "Could not calculate relationship score"}
    
    def _get_improvement_tips(self, scores: Dict, total_score: float) -> List[str]:
        """Generate improvement suggestions based on scores"""
        tips = []
        
        if scores['balance'] < 10:
            tips.append("💬 Tente equilibrar mais a conversa - ambos devem participar igualmente")
        
        if scores['engagement'] < 15:
            tips.append("📝 Escreva mensagens mais elaboradas para aprofundar a conexão")
        
        if scores['frequency'] < 10:
            tips.append("🕐 Conversem com mais frequência para fortalecer o relacionamento")
        
        if scores['consistency'] < 10:
            tips.append("⏰ Mantenham um ritmo mais regular de conversas")
        
        if scores['variety'] < 5:
            tips.append("🌅 Conversem em diferentes momentos do dia para descobrir mais um sobre o outro")
        
        if not tips and total_score < 80:
            tips.append("🌟 Vocês já têm uma ótima conexão! Continue assim!")
        
        return tips[:3]  # Maximum 3 tips
    
    def get_chat_personality(self) -> Dict:
        """Determine chat personality archetype"""
        try:
            basic_stats = self.analyzer.get_basic_stats()
            activity = self.analyzer.get_activity_patterns()
            
            # Analyze patterns to determine personality
            avg_words = basic_stats['avg_words_per_message']
            messages_per_day = basic_stats['messages_per_day']
            peak_hour = activity.get('peak_hour', 12)
            total_messages = basic_stats['total_messages']
            
            # Determine archetype based on communication patterns
            if avg_words > 15 and messages_per_day < 10:
                archetype = "🎭 Os Pensadores Profundos"
                traits = ["Reflexivos", "Detalhistas", "Filosóficos"]
                description = "Vocês preferem conversas longas e significativas, explorando temas com profundidade."
                
            elif messages_per_day > 50:
                archetype = "⚡ Os Tagarelas"
                traits = ["Comunicativos", "Energéticos", "Próximos"]
                description = "Vocês conversam muito e frequentemente, mantendo contato constante."
                
            elif peak_hour < 6 or peak_hour > 22:
                archetype = "🦉 Os Corujas da Madrugada"
                traits = ["Noturnos", "Íntimos", "Criativos"]
                description = "Vocês se conectam melhor nas altas horas, quando o mundo está quieto."
                
            elif 6 <= peak_hour <= 8:
                archetype = "🌅 Os Matutinos"
                traits = ["Organizados", "Disciplinados", "Otimistas"]
                description = "Começam o dia conversando, trazendo energia positiva um para o outro."
                
            elif avg_words < 5:
                archetype = "💨 Os Diretos ao Ponto"
                traits = ["Objetivos", "Eficientes", "Práticos"]
                description = "Vocês comunicam de forma clara e direta, sem rodeios."
                
            elif total_messages < 50:
                archetype = "🌱 Os Iniciantes"
                traits = ["Cautelosos", "Descobrindo", "Potencial"]
                description = "Estão começando a se conhecer melhor através das mensagens."
                
            else:
                archetype = "😊 Os Equilibrados"
                traits = ["Balanceados", "Harmoniosos", "Estáveis"]
                description = "Mantêm um padrão de comunicação saudável e consistente."
            
            return {
                'archetype': archetype,
                'traits': traits,
                'description': description,
                'based_on': {
                    'avg_words': avg_words,
                    'messages_per_day': round(messages_per_day, 1),
                    'peak_hour': peak_hour,
                    'total_messages': total_messages
                }
            }
            
        except Exception as e:
            logger.error(f"Error determining chat personality: {e}")
            return {
                'archetype': '🤝 Os Comunicadores',
                'traits': ['Sociáveis', 'Amigáveis', 'Conectados'],
                'description': 'Vocês sabem se comunicar bem e manter uma boa conversa.',
                'based_on': {}
            }
    
    def generate_fun_facts(self) -> List[str]:
        """Generate interesting fun facts about the conversation"""
        try:
            basic_stats = self.analyzer.get_basic_stats()
            activity = self.analyzer.get_activity_patterns()
            word_analysis = self.analyzer.get_word_analysis()
            
            facts = []
            
            # Message facts
            total_messages = basic_stats['total_messages']
            facts.append(f"📱 Vocês trocaram {total_messages} mensagens!")
            
            # Word facts
            total_words = basic_stats['total_words']
            facts.append(f"📝 Escreveram juntos {total_words} palavras!")
            
            # Time facts
            duration = basic_stats['duration_days']
            if duration > 0:
                facts.append(f"📅 Conversando há {duration} dias!")
            
            # Activity facts
            peak_hour = activity.get('peak_hour')
            if peak_hour:
                if peak_hour < 6:
                    facts.append("🌙 Vocês são mais ativos de madrugada!")
                elif peak_hour < 12:
                    facts.append("🌅 Vocês adoram conversar de manhã!")
                elif peak_hour < 18:
                    facts.append("☀️ A tarde é o momento preferido para conversar!")
                else:
                    facts.append("🌆 Vocês se conectam melhor à noite!")
            
            # Vocabulary facts
            vocab_richness = word_analysis.get('vocabulary_richness', 0)
            if vocab_richness > 0.3:
                facts.append("🎓 Vocês têm um vocabulário muito rico!")
            
            # Participation facts
            if len(self.participants) == 2:
                participant_stats = basic_stats['participant_stats']
                participants = list(self.participants)
                p1_msgs = participant_stats[participants[0]]['messages']
                p2_msgs = participant_stats[participants[1]]['messages']
                
                if abs(p1_msgs - p2_msgs) < 5:
                    facts.append("⚖️ Vocês participam igualmente da conversa!")
                
                total_words_p1 = participant_stats[participants[0]]['words']
                total_words_p2 = participant_stats[participants[1]]['words']
                
                if total_words_p1 > total_words_p2 * 1.5:
                    facts.append(f"📖 {participants[0]} é mais falante!")
                elif total_words_p2 > total_words_p1 * 1.5:
                    facts.append(f"📖 {participants[1]} é mais falante!")
            
            return facts[:5]  # Return top 5 facts
            
        except Exception as e:
            logger.error(f"Error generating fun facts: {e}")
            return ["🎉 Vocês têm uma conversa interessante!"]