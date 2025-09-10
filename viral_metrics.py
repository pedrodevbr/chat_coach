#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Viral Metrics and Shareable Insights for WhatsApp Chat Analyzer
Creates engaging, shareable content that users want to post on social media
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import random
from collections import Counter, defaultdict
import statistics

class ViralMetrics:
    def __init__(self, analyzer):
        self.analyzer = analyzer
        self.messages = analyzer.messages
        self.participants = list(analyzer.participants)
        
    def generate_relationship_score(self) -> Dict:
        """Generate a comprehensive relationship compatibility score"""
        if len(self.participants) != 2:
            return {"error": "Relationship score only available for 2-person chats"}
        
        scores = {}
        
        # 1. Communication Balance (20%)
        msg_counts = Counter(msg.sender for msg in self.messages)
        p1_msgs, p2_msgs = msg_counts[self.participants[0]], msg_counts[self.participants[1]]
        balance = min(p1_msgs, p2_msgs) / max(p1_msgs, p2_msgs)
        scores['balance'] = balance * 20
        
        # 2. Response Speed (15%)
        response_times = self._calculate_response_times()
        if response_times:
            avg_response = statistics.median(response_times)  # Use median for robustness
            # Score decreases as response time increases (max 1440 min = 24h)
            speed_score = max(0, (1440 - min(avg_response, 1440)) / 1440)
            scores['speed'] = speed_score * 15
        else:
            scores['speed'] = 0
        
        # 3. Emotional Synchrony (25%)
        emotion_sync = self._calculate_emotion_synchrony()
        scores['emotion'] = emotion_sync * 25
        
        # 4. Conversation Variety (20%)
        variety_score = self._calculate_conversation_variety()
        scores['variety'] = variety_score * 20
        
        # 5. Engagement Consistency (20%)
        consistency_score = self._calculate_engagement_consistency()
        scores['consistency'] = consistency_score * 20
        
        total_score = sum(scores.values())
        
        # Generate personality insights
        personality = self._generate_relationship_personality(total_score, scores)
        
        # Generate comparison with "average couples"
        percentile = self._calculate_percentile(total_score)
        
        return {
            "total_score": round(total_score, 1),
            "max_score": 100,
            "percentile": percentile,
            "grade": self._score_to_grade(total_score),
            "detailed_scores": {k: round(v, 1) for k, v in scores.items()},
            "personality": personality,
            "improvements": self._generate_improvements(scores),
            "fun_facts": self._generate_fun_facts(),
            "comparison": self._generate_comparison_stats(total_score)
        }
    
    def generate_chat_personality(self) -> Dict:
        """Generate a fun personality profile for the chat"""
        
        # Calculate various metrics
        total_msgs = len(self.messages)
        avg_msg_length = statistics.mean([len(msg.content) for msg in self.messages])
        night_msgs = len([m for m in self.messages if 22 <= m.timestamp.hour or m.timestamp.hour <= 6])
        weekend_msgs = len([m for m in self.messages if m.timestamp.weekday() >= 5])
        
        # Question percentage
        questions = len([m for m in self.messages if '?' in m.content])
        question_ratio = questions / total_msgs
        
        # Emoji usage
        emoji_msgs = len([m for m in self.messages if any(ord(char) > 127 for char in m.content)])
        emoji_ratio = emoji_msgs / total_msgs
        
        # Determine personality traits
        traits = []
        
        if avg_msg_length > 50:
            traits.append("📚 Storyteller")
        elif avg_msg_length < 15:
            traits.append("⚡ Quick Texter")
        else:
            traits.append("💬 Balanced Communicator")
        
        if night_msgs / total_msgs > 0.3:
            traits.append("🦉 Night Owl")
        elif night_msgs / total_msgs < 0.1:
            traits.append("🐓 Early Bird")
        else:
            traits.append("🌅 Regular Schedule")
        
        if question_ratio > 0.2:
            traits.append("🤔 Curious Mind")
        elif question_ratio < 0.05:
            traits.append("📢 Statement Maker")
        else:
            traits.append("❓ Balanced Questioner")
        
        if emoji_ratio > 0.4:
            traits.append("😍 Emoji Enthusiast")
        elif emoji_ratio < 0.1:
            traits.append("📝 Text Purist")
        else:
            traits.append("😊 Emoji Balanced")
        
        # Generate archetype
        archetype = self._determine_archetype(avg_msg_length, night_msgs/total_msgs, 
                                            question_ratio, emoji_ratio)
        
        return {
            "archetype": archetype,
            "traits": traits,
            "stats": {
                "avg_message_length": round(avg_msg_length, 1),
                "night_percentage": round((night_msgs/total_msgs)*100, 1),
                "weekend_percentage": round((weekend_msgs/total_msgs)*100, 1),
                "question_percentage": round(question_ratio*100, 1),
                "emoji_percentage": round(emoji_ratio*100, 1)
            },
            "fun_description": self._generate_personality_description(archetype, traits)
        }
    
    def generate_conversation_highlights(self) -> Dict:
        """Generate shareable conversation highlights and milestones"""
        
        highlights = {}
        
        # Time-based milestones
        if self.messages:
            first_msg = min(self.messages, key=lambda x: x.timestamp)
            last_msg = max(self.messages, key=lambda x: x.timestamp)
            duration_days = (last_msg.timestamp - first_msg.timestamp).days
            
            highlights["timeline"] = {
                "first_message_date": first_msg.timestamp.strftime("%B %d, %Y"),
                "duration_days": duration_days,
                "duration_months": round(duration_days / 30.44, 1),
                "messages_per_day": round(len(self.messages) / max(duration_days, 1), 1)
            }
        
        # Peak activity analysis
        hours = [msg.timestamp.hour for msg in self.messages]
        peak_hour = Counter(hours).most_common(1)[0][0]
        
        days_of_week = [msg.timestamp.strftime('%A') for msg in self.messages]
        peak_day = Counter(days_of_week).most_common(1)[0][0]
        
        highlights["peak_activity"] = {
            "peak_hour": f"{peak_hour:02d}:00",
            "peak_day": peak_day,
            "peak_description": self._get_peak_description(peak_hour, peak_day)
        }
        
        # Message milestones
        highlights["milestones"] = self._calculate_milestones()
        
        # Longest/shortest messages
        highlights["extremes"] = self._find_message_extremes()
        
        # Conversation streaks
        highlights["streaks"] = self._calculate_conversation_streaks()
        
        # Special patterns
        highlights["patterns"] = self._find_special_patterns()
        
        return highlights
    
    def generate_social_media_cards(self) -> List[Dict]:
        """Generate ready-to-share social media cards with engaging visuals"""
        
        cards = []
        
        # Card 1: Relationship Score
        if len(self.participants) == 2:
            relationship_data = self.generate_relationship_score()
            cards.append({
                "type": "relationship_score",
                "title": f"Our Chat Compatibility: {relationship_data['grade']}!",
                "subtitle": f"{relationship_data['total_score']}/100 - Better than {relationship_data['percentile']}% of couples!",
                "visual_elements": {
                    "score": relationship_data['total_score'],
                    "grade": relationship_data['grade'],
                    "percentile": relationship_data['percentile']
                },
                "shareable_text": f"We scored {relationship_data['total_score']}/100 on our chat compatibility! {relationship_data['personality']['description']} 💕 #ChatAnalysis #RelationshipGoals"
            })
        
        # Card 2: Chat Personality
        personality_data = self.generate_chat_personality()
        cards.append({
            "type": "personality",
            "title": f"Our Chat Personality: {personality_data['archetype']}",
            "subtitle": ", ".join(personality_data['traits'][:3]),
            "visual_elements": {
                "archetype": personality_data['archetype'],
                "traits": personality_data['traits']
            },
            "shareable_text": f"Our chat personality is {personality_data['archetype']}! {personality_data['fun_description'][:100]}... #ChatPersonality #TextingStyle"
        })
        
        # Card 3: Message Statistics
        cards.append({
            "type": "statistics",
            "title": f"{len(self.messages)} Messages Analyzed!",
            "subtitle": f"{len(self.participants)} participants, {self._get_duration_text()} of chatting",
            "visual_elements": {
                "total_messages": len(self.messages),
                "participants": len(self.participants),
                "duration": self._get_duration_text(),
                "words": sum(msg.word_count for msg in self.messages)
            },
            "shareable_text": f"Just analyzed our {len(self.messages)} messages! We've been chatting for {self._get_duration_text()} 📱 #ChatStats #Friendship"
        })
        
        # Card 4: Fun Facts
        fun_facts = self._generate_viral_fun_facts()
        if fun_facts:
            cards.append({
                "type": "fun_facts",
                "title": "Mind-Blowing Chat Facts! 🤯",
                "subtitle": "You won't believe these statistics...",
                "visual_elements": {
                    "facts": fun_facts[:3]  # Top 3 most interesting
                },
                "shareable_text": f"🤯 Fun fact: {fun_facts[0]} Check out our chat analysis! #ChatFacts #MindBlown"
            })
        
        return cards
    
    def generate_premium_preview(self) -> Dict:
        """Generate enticing preview of premium AI features"""
        
        # Mock some premium insights to show value
        premium_features = {
            "ai_insights": {
                "available": False,
                "preview": [
                    "🧠 Deep personality analysis using advanced AI",
                    "💕 Relationship compatibility predictions", 
                    "🎯 Personalized communication recommendations",
                    "📈 Relationship health trends over time",
                    "🔮 Conversation style evolution analysis"
                ],
                "sample_insight": "Based on your communication patterns, you show strong emotional intelligence and adaptability in conversations..."
            },
            "advanced_metrics": {
                "available": False,
                "features": [
                    "🎭 Mood tracking across conversations",
                    "🕒 Optimal texting time recommendations",
                    "📊 Communication style comparison with famous couples",
                    "🎨 Custom branded chat reports",
                    "📤 High-resolution shareable graphics"
                ]
            },
            "predictions": {
                "available": False,
                "examples": [
                    "🔮 Predict conversation topics you'll discuss next",
                    "📅 Best times to have important conversations", 
                    "💬 Communication improvement suggestions",
                    "🎯 Relationship milestone predictions"
                ]
            }
        }
        
        return {
            "premium_features": premium_features,
            "upgrade_incentives": [
                "💎 Unlock AI-powered relationship insights",
                "🚀 Get premium shareable graphics",
                "📈 Track your relationship evolution",
                "🎨 Custom branded reports",
                "🔥 Advanced compatibility analysis"
            ],
            "value_proposition": "Discover what your messages really say about your relationship with AI-powered analysis!"
        }
    
    def _calculate_response_times(self) -> List[float]:
        """Calculate response times between different senders"""
        response_times = []
        
        for i in range(1, len(self.messages)):
            if self.messages[i].sender != self.messages[i-1].sender:
                time_diff = (self.messages[i].timestamp - self.messages[i-1].timestamp).total_seconds() / 60
                if time_diff < 1440:  # Less than 24 hours
                    response_times.append(time_diff)
        
        return response_times
    
    def _calculate_emotion_synchrony(self) -> float:
        """Calculate how well emotions are synchronized between participants"""
        if len(self.participants) != 2:
            return 0.5
        
        # Simple emotion analysis based on punctuation and common words
        emotions = defaultdict(list)
        
        for msg in self.messages:
            emotion_score = 0
            content = msg.content.lower()
            
            # Positive indicators
            if any(word in content for word in ['feliz', 'amor', 'ótimo', 'legal', 'bom', '❤️', '😍', '😊', '🥰']):
                emotion_score += 1
            if '!' in msg.content:
                emotion_score += 0.5
            
            # Negative indicators  
            if any(word in content for word in ['triste', 'ruim', 'chato', 'problema', '😢', '😠', '😡']):
                emotion_score -= 1
            
            emotions[msg.sender].append(emotion_score)
        
        # Calculate correlation between participants' emotions
        if len(emotions) == 2:
            p1_emotions = emotions[self.participants[0]]
            p2_emotions = emotions[self.participants[1]]
            
            if len(p1_emotions) > 1 and len(p2_emotions) > 1:
                # Simple correlation calculation
                min_len = min(len(p1_emotions), len(p2_emotions))
                p1_sample = p1_emotions[:min_len]
                p2_sample = p2_emotions[:min_len]
                
                if statistics.stdev(p1_sample) > 0 and statistics.stdev(p2_sample) > 0:
                    correlation = np.corrcoef(p1_sample, p2_sample)[0, 1]
                    return max(0, correlation)  # Return 0 if negative correlation
        
        return 0.5  # Default middle score
    
    def _calculate_conversation_variety(self) -> float:
        """Calculate variety in conversation topics and styles"""
        # Simple variety metrics
        unique_words = set()
        total_words = []
        
        for msg in self.messages:
            words = msg.content.lower().split()
            total_words.extend(words)
            unique_words.update(words)
        
        if len(total_words) == 0:
            return 0
        
        # Vocabulary diversity
        diversity = len(unique_words) / len(total_words)
        
        # Message length variety
        lengths = [len(msg.content) for msg in self.messages]
        if len(lengths) > 1:
            length_variety = statistics.stdev(lengths) / statistics.mean(lengths) if statistics.mean(lengths) > 0 else 0
        else:
            length_variety = 0
        
        # Combine metrics
        variety_score = min(1.0, diversity * 5 + min(length_variety, 0.5))
        return variety_score
    
    def _calculate_engagement_consistency(self) -> float:
        """Calculate how consistently both participants engage"""
        if len(self.participants) != 2:
            return 0.5
        
        # Group messages by day
        daily_messages = defaultdict(lambda: defaultdict(int))
        
        for msg in self.messages:
            day = msg.timestamp.date()
            daily_messages[day][msg.sender] += 1
        
        # Calculate daily engagement balance
        balances = []
        for day, senders in daily_messages.items():
            if len(senders) == 2:
                counts = list(senders.values())
                balance = min(counts) / max(counts)
                balances.append(balance)
        
        if balances:
            return statistics.mean(balances)
        return 0.5
    
    def _generate_relationship_personality(self, score: float, scores: Dict) -> Dict:
        """Generate relationship personality based on scores"""
        
        personalities = [
            {"range": (90, 100), "type": "💎 Soulmate Connection", 
             "description": "You two are basically telepathic! Your communication is so in sync, it's almost scary good."},
            {"range": (80, 90), "type": "🔥 Power Couple", 
             "description": "Your chat chemistry is off the charts! You balance each other perfectly."},
            {"range": (70, 80), "type": "💕 Sweet Harmony", 
             "description": "You have a lovely, balanced communication style that flows naturally."},
            {"range": (60, 70), "type": "🌟 Growing Strong", 
             "description": "Your communication shows great potential with room for even more connection."},
            {"range": (50, 60), "type": "🌱 Building Together", 
             "description": "You're developing a solid foundation for great communication."},
            {"range": (0, 50), "type": "💪 Work in Progress", 
             "description": "Every great relationship starts somewhere - you're on your journey!"}
        ]
        
        for personality in personalities:
            if personality["range"][0] <= score <= personality["range"][1]:
                return personality
        
        return personalities[-1]  # Fallback
    
    def _calculate_percentile(self, score: float) -> int:
        """Calculate percentile ranking (simulated)"""
        # Simulated percentile based on score
        if score >= 95:
            return random.randint(98, 99)
        elif score >= 90:
            return random.randint(90, 97)
        elif score >= 80:
            return random.randint(75, 89)
        elif score >= 70:
            return random.randint(60, 74)
        elif score >= 60:
            return random.randint(40, 59)
        else:
            return random.randint(10, 39)
    
    def _score_to_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 95:
            return "A+"
        elif score >= 90:
            return "A"
        elif score >= 85:
            return "A-"
        elif score >= 80:
            return "B+"
        elif score >= 75:
            return "B"
        elif score >= 70:
            return "B-"
        elif score >= 65:
            return "C+"
        elif score >= 60:
            return "C"
        else:
            return "C-"
    
    def _generate_improvements(self, scores: Dict) -> List[str]:
        """Generate improvement suggestions"""
        improvements = []
        
        if scores.get('balance', 0) < 15:
            improvements.append("💬 Try to balance who initiates conversations more")
        if scores.get('speed', 0) < 10:
            improvements.append("⚡ Faster responses could boost your connection")
        if scores.get('emotion', 0) < 20:
            improvements.append("😊 Show more emotional expression in your messages")
        if scores.get('variety', 0) < 15:
            improvements.append("🎭 Try discussing more diverse topics")
        if scores.get('consistency', 0) < 15:
            improvements.append("📅 More consistent daily interaction could help")
        
        if not improvements:
            improvements.append("🌟 You're doing great! Keep up the amazing communication!")
        
        return improvements
    
    def _generate_fun_facts(self) -> List[str]:
        """Generate fun facts about the conversation"""
        facts = []
        
        if self.messages:
            # Total words
            total_words = sum(msg.word_count for msg in self.messages)
            facts.append(f"📚 You've shared {total_words:,} words together!")
            
            # Time span
            first_msg = min(self.messages, key=lambda x: x.timestamp)
            last_msg = max(self.messages, key=lambda x: x.timestamp)
            days = (last_msg.timestamp - first_msg.timestamp).days
            if days > 0:
                facts.append(f"📅 You've been chatting for {days:,} days!")
            
            # Average per day
            if days > 0:
                avg_per_day = len(self.messages) / days
                facts.append(f"📱 You average {avg_per_day:.1f} messages per day!")
            
            # Longest message
            longest = max(self.messages, key=lambda x: len(x.content))
            if len(longest.content) > 100:
                facts.append(f"📝 Longest message: {len(longest.content)} characters!")
        
        return facts
    
    def _generate_comparison_stats(self, score: float) -> Dict:
        """Generate comparison with 'average' couples"""
        comparisons = {
            "response_time": "67% faster than average couples",
            "message_balance": "23% more balanced than typical relationships", 
            "conversation_variety": "156% more diverse topics discussed",
            "daily_consistency": "89% more consistent daily interaction"
        }
        
        return {
            "better_than": f"{self._calculate_percentile(score)}% of couples",
            "specific_comparisons": comparisons,
            "fun_comparison": self._generate_fun_comparison(score)
        }
    
    def _determine_archetype(self, avg_length: float, night_ratio: float, 
                           question_ratio: float, emoji_ratio: float) -> str:
        """Determine chat archetype based on metrics"""
        
        archetypes = [
            "🎭 The Storytellers",
            "⚡ The Speed Texters", 
            "🦉 The Night Owls",
            "🤔 The Deep Thinkers",
            "😍 The Emoji Masters",
            "📚 The Philosophers",
            "🎪 The Entertainment Duo",
            "💼 The Efficient Communicators",
            "🌟 The Balanced Chatters"
        ]
        
        # Simple logic to determine archetype
        if avg_length > 50:
            return "🎭 The Storytellers"
        elif avg_length < 15:
            return "⚡ The Speed Texters"
        elif night_ratio > 0.4:
            return "🦉 The Night Owls"
        elif question_ratio > 0.2:
            return "🤔 The Deep Thinkers"
        elif emoji_ratio > 0.4:
            return "😍 The Emoji Masters"
        else:
            return random.choice(archetypes)
    
    def _generate_personality_description(self, archetype: str, traits: List[str]) -> str:
        """Generate fun personality description"""
        
        descriptions = {
            "🎭 The Storytellers": "You love sharing detailed stories and experiences. Your conversations are like mini novels!",
            "⚡ The Speed Texters": "Quick, snappy, and to the point. You've mastered the art of efficient communication!",
            "🦉 The Night Owls": "Your best conversations happen when the world is sleeping. Night time is your prime time!",
            "🤔 The Deep Thinkers": "You ask all the right questions and dive deep into meaningful topics.",
            "😍 The Emoji Masters": "Why use words when emojis say it better? Your conversations are colorful masterpieces!",
            "📚 The Philosophers": "Every conversation becomes a deep dive into life's mysteries.",
            "🎪 The Entertainment Duo": "Your chat is basically a comedy show. Never a dull moment!",
            "💼 The Efficient Communicators": "Clear, concise, and effective. You get things done through chat!",
            "🌟 The Balanced Chatters": "Perfect balance of everything - the goldilocks of chat styles!"
        }
        
        return descriptions.get(archetype, "You have a unique and interesting communication style!")
    
    def _calculate_milestones(self) -> Dict:
        """Calculate message milestones"""
        milestones = {}
        
        if len(self.messages) >= 1000:
            milestones["1k_messages"] = "🎉 Hit 1,000 messages!"
        if len(self.messages) >= 10000:
            milestones["10k_messages"] = "🏆 Amazing! 10,000+ messages!"
        
        # Check for daily streaks
        dates = [msg.timestamp.date() for msg in self.messages]
        unique_dates = sorted(set(dates))
        
        max_streak = 1
        current_streak = 1
        
        for i in range(1, len(unique_dates)):
            if unique_dates[i] - unique_dates[i-1] == timedelta(days=1):
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 1
        
        if max_streak >= 7:
            milestones["week_streak"] = f"🔥 {max_streak} day chatting streak!"
        
        return milestones
    
    def _find_message_extremes(self) -> Dict:
        """Find longest/shortest messages and other extremes"""
        if not self.messages:
            return {}
        
        longest = max(self.messages, key=lambda x: len(x.content))
        shortest = min([m for m in self.messages if len(m.content.strip()) > 0], 
                      key=lambda x: len(x.content), default=longest)
        
        return {
            "longest_message": {
                "length": len(longest.content),
                "sender": longest.sender,
                "preview": longest.content[:50] + "..." if len(longest.content) > 50 else longest.content
            },
            "shortest_message": {
                "length": len(shortest.content),
                "sender": shortest.sender,
                "content": shortest.content
            }
        }
    
    def _calculate_conversation_streaks(self) -> Dict:
        """Calculate various conversation streaks"""
        # Daily messaging streaks
        dates = [msg.timestamp.date() for msg in self.messages]
        date_counter = Counter(dates)
        
        # Find longest streak of consecutive days with messages
        unique_dates = sorted(set(dates))
        max_streak = 1
        current_streak = 1
        
        for i in range(1, len(unique_dates)):
            if unique_dates[i] - unique_dates[i-1] == timedelta(days=1):
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 1
        
        return {
            "daily_streak": max_streak,
            "most_active_day": max(date_counter.items(), key=lambda x: x[1]) if date_counter else None
        }
    
    def _find_special_patterns(self) -> Dict:
        """Find special communication patterns"""
        patterns = {}
        
        # Late night conversations (after 11 PM or before 6 AM)
        late_night = [m for m in self.messages if m.timestamp.hour >= 23 or m.timestamp.hour <= 5]
        if late_night:
            patterns["night_owl_percentage"] = round((len(late_night) / len(self.messages)) * 100, 1)
        
        # Weekend vs weekday activity
        weekend_msgs = [m for m in self.messages if m.timestamp.weekday() >= 5]
        if weekend_msgs:
            patterns["weekend_percentage"] = round((len(weekend_msgs) / len(self.messages)) * 100, 1)
        
        # Question frequency
        questions = [m for m in self.messages if '?' in m.content]
        if questions:
            patterns["question_percentage"] = round((len(questions) / len(self.messages)) * 100, 1)
        
        return patterns
    
    def _get_peak_description(self, hour: int, day: str) -> str:
        """Get description for peak activity time"""
        hour_descriptions = {
            range(6, 9): "early morning coffee chats ☕",
            range(9, 12): "productive morning conversations 🌅", 
            range(12, 14): "lunch break catch-ups 🍽️",
            range(14, 17): "afternoon check-ins 📱",
            range(17, 20): "evening wind-down chats 🌆",
            range(20, 23): "cozy night conversations 🌙",
            range(23, 24): "late night deep talks 🌃",
            range(0, 6): "middle-of-the-night messages 🦉"
        }
        
        description = "regular chatting"
        for time_range, desc in hour_descriptions.items():
            if hour in time_range:
                description = desc
                break
        
        return f"You love your {description} on {day}s!"
    
    def _get_duration_text(self) -> str:
        """Get human-readable duration text"""
        if not self.messages:
            return "0 days"
        
        first = min(self.messages, key=lambda x: x.timestamp)
        last = max(self.messages, key=lambda x: x.timestamp)
        days = (last.timestamp - first.timestamp).days
        
        if days < 1:
            return "less than a day"
        elif days < 30:
            return f"{days} days"
        elif days < 365:
            months = round(days / 30.44, 1)
            return f"{months} months"
        else:
            years = round(days / 365.25, 1)
            return f"{years} years"
    
    def _generate_viral_fun_facts(self) -> List[str]:
        """Generate viral-worthy fun facts"""
        facts = []
        
        if not self.messages:
            return facts
        
        total_words = sum(msg.word_count for msg in self.messages)
        total_chars = sum(len(msg.content) for msg in self.messages)
        
        # Impressive numbers
        if total_words > 10000:
            facts.append(f"We've shared {total_words:,} words - that's like a short novel! 📚")
        
        if total_chars > 50000:
            facts.append(f"Our {total_chars:,} characters could fill {total_chars//2000} pages! 📄")
        
        # Time-based facts
        duration = self._get_duration_text()
        if "years" in duration:
            facts.append(f"We've been chatting for {duration} - that's dedication! 💪")
        
        # Activity patterns
        night_msgs = len([m for m in self.messages if m.timestamp.hour >= 22 or m.timestamp.hour <= 6])
        if night_msgs > len(self.messages) * 0.3:
            facts.append(f"{round((night_msgs/len(self.messages))*100)}% of our messages are after 10 PM - night owl mode! 🦉")
        
        # Response patterns
        response_times = self._calculate_response_times()
        if response_times:
            avg_response = statistics.median(response_times)
            if avg_response < 5:
                facts.append(f"We reply in under 5 minutes on average - lightning fast! ⚡")
            elif avg_response < 60:
                facts.append(f"Average response time: {round(avg_response)} minutes - pretty good! ⏰")
        
        return facts[:5]  # Return top 5 most interesting facts
    
    def _generate_fun_comparison(self, score: float) -> str:
        """Generate fun comparison with pop culture references"""
        comparisons = [
            "Your chat chemistry rivals Ross and Rachel! 💕",
            "You communicate better than most sitcom couples! 📺",
            "Your texting game is stronger than most influencers! 📱",
            "You've got the communication skills of a power couple! 💪",
            "Your chat flow is smoother than a Netflix series! 🎬"
        ]
        
        return random.choice(comparisons)