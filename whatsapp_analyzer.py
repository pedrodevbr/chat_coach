import re
import datetime
from typing import List, Dict, Tuple
from collections import Counter, defaultdict
import statistics

class WhatsAppMessage:
    def __init__(self, timestamp: str, sender: str, content: str):
        self.timestamp = self._parse_timestamp(timestamp)
        self.sender = sender
        self.content = content
        self.word_count = len(content.split())
        self.char_count = len(content)
        
    def _parse_timestamp(self, timestamp_str: str) -> datetime.datetime:
        try:
            return datetime.datetime.strptime(timestamp_str, "%d/%m/%Y %H:%M")
        except ValueError:
            try:
                return datetime.datetime.strptime(timestamp_str, "%m/%d/%y, %I:%M %p")
            except ValueError:
                return datetime.datetime.now()

class WhatsAppChatAnalyzer:
    def __init__(self):
        self.messages: List[WhatsAppMessage] = []
        self.participants: set = set()
        
    def parse_chat(self, chat_text: str) -> None:
        lines = chat_text.strip().split('\n')
        
        message_pattern = r'(\d{1,2}/\d{1,2}/\d{2,4} \d{1,2}:\d{2}(?:\s?[AP]M)?) - ([^:]+): (.+)'
        
        for line in lines:
            match = re.match(message_pattern, line)
            if match:
                timestamp, sender, content = match.groups()
                sender = sender.strip()
                content = content.strip()
                
                if content and not content.startswith('<'):  # Skip system messages
                    message = WhatsAppMessage(timestamp, sender, content)
                    self.messages.append(message)
                    self.participants.add(sender)
    
    def linguistic_analysis(self) -> Dict:
        total_messages = len(self.messages)
        if total_messages == 0:
            return {"error": "No messages to analyze"}
            
        word_counts = [msg.word_count for msg in self.messages]
        char_counts = [msg.char_count for msg in self.messages]
        
        sender_stats = defaultdict(lambda: {"messages": 0, "words": 0, "chars": 0})
        
        for msg in self.messages:
            sender_stats[msg.sender]["messages"] += 1
            sender_stats[msg.sender]["words"] += msg.word_count
            sender_stats[msg.sender]["chars"] += msg.char_count
        
        # Analyze message timing patterns
        hours = [msg.timestamp.hour for msg in self.messages]
        hour_distribution = Counter(hours)
        
        # Most active hours
        peak_hours = sorted(hour_distribution.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            "total_messages": total_messages,
            "participants": list(self.participants),
            "average_words_per_message": statistics.mean(word_counts),
            "average_chars_per_message": statistics.mean(char_counts),
            "sender_statistics": dict(sender_stats),
            "peak_activity_hours": peak_hours,
            "conversation_span_days": (self.messages[-1].timestamp - self.messages[0].timestamp).days if total_messages > 1 else 0
        }
    
    def psychological_analysis(self) -> Dict:
        if not self.messages:
            return {"error": "No messages to analyze"}
            
        # Analyze emotional indicators
        positive_words = ['ótimo', 'bom', 'legal', 'adorei', 'perfeito', 'obrigado', 'obrigada', 
                         'feliz', 'alegre', 'amor', 'querido', 'querida', '😊', '❤️', '😍', '🥰']
        negative_words = ['ruim', 'péssimo', 'triste', 'chato', 'irritado', 'bravo', 'raiva',
                         'problema', 'difícil', '😢', '😠', '😡', '😤', '💔']
        
        sender_emotions = defaultdict(lambda: {"positive": 0, "negative": 0, "neutral": 0})
        
        response_times = []
        for i in range(1, len(self.messages)):
            if self.messages[i].sender != self.messages[i-1].sender:
                time_diff = (self.messages[i].timestamp - self.messages[i-1].timestamp).total_seconds() / 60
                if time_diff < 1440:  # Less than 24 hours
                    response_times.append(time_diff)
        
        for msg in self.messages:
            content_lower = msg.content.lower()
            positive_count = sum(1 for word in positive_words if word in content_lower)
            negative_count = sum(1 for word in negative_words if word in content_lower)
            
            if positive_count > negative_count:
                sender_emotions[msg.sender]["positive"] += 1
            elif negative_count > positive_count:
                sender_emotions[msg.sender]["negative"] += 1
            else:
                sender_emotions[msg.sender]["neutral"] += 1
        
        return {
            "emotional_tone_by_sender": dict(sender_emotions),
            "average_response_time_minutes": statistics.mean(response_times) if response_times else 0,
            "median_response_time_minutes": statistics.median(response_times) if response_times else 0,
            "total_response_interactions": len(response_times)
        }
    
    def communication_analysis(self) -> Dict:
        if not self.messages:
            return {"error": "No messages to analyze"}
            
        # Analyze question patterns
        question_count = sum(1 for msg in self.messages if '?' in msg.content)
        exclamation_count = sum(1 for msg in self.messages if '!' in msg.content)
        
        # Analyze conversation starters vs responses
        conversation_patterns = defaultdict(lambda: {"initiated": 0, "responded": 0})
        
        for i, msg in enumerate(self.messages):
            if i == 0 or (msg.timestamp - self.messages[i-1].timestamp).total_seconds() > 3600:  # 1 hour gap
                conversation_patterns[msg.sender]["initiated"] += 1
            else:
                conversation_patterns[msg.sender]["responded"] += 1
        
        # Analyze politeness indicators
        polite_words = ['por favor', 'obrigado', 'obrigada', 'desculpa', 'perdão', 'com licença']
        politeness_by_sender = defaultdict(int)
        
        for msg in self.messages:
            content_lower = msg.content.lower()
            politeness_count = sum(1 for word in polite_words if word in content_lower)
            politeness_by_sender[msg.sender] += politeness_count
        
        return {
            "question_percentage": (question_count / len(self.messages)) * 100,
            "exclamation_percentage": (exclamation_count / len(self.messages)) * 100,
            "conversation_patterns": dict(conversation_patterns),
            "politeness_indicators": dict(politeness_by_sender),
            "communication_balance": self._calculate_balance()
        }
    
    def relationship_coaching_insights(self) -> Dict:
        if not self.messages:
            return {"error": "No messages to analyze"}
            
        # Analyze engagement levels
        sender_msg_count = Counter(msg.sender for msg in self.messages)
        total_msgs = len(self.messages)
        
        engagement_balance = {}
        for sender, count in sender_msg_count.items():
            engagement_balance[sender] = (count / total_msgs) * 100
        
        # Analyze conversation flow
        consecutive_messages = defaultdict(list)
        current_sender = None
        count = 0
        
        for msg in self.messages:
            if msg.sender == current_sender:
                count += 1
            else:
                if current_sender and count > 1:
                    consecutive_messages[current_sender].append(count)
                current_sender = msg.sender
                count = 1
        
        if current_sender and count > 1:
            consecutive_messages[current_sender].append(count)
        
        # Calculate average consecutive messages
        avg_consecutive = {}
        for sender, counts in consecutive_messages.items():
            avg_consecutive[sender] = statistics.mean(counts) if counts else 1
        
        return {
            "engagement_balance_percentage": engagement_balance,
            "average_consecutive_messages": avg_consecutive,
            "relationship_health_score": self._calculate_relationship_health(),
            "communication_recommendations": self._generate_recommendations()
        }
    
    def _calculate_balance(self) -> Dict:
        if len(self.participants) != 2:
            return {"type": "group_chat", "balance": "N/A"}
        
        sender_counts = Counter(msg.sender for msg in self.messages)
        participants = list(sender_counts.keys())
        
        if len(participants) == 2:
            count1, count2 = sender_counts[participants[0]], sender_counts[participants[1]]
            balance_ratio = min(count1, count2) / max(count1, count2) * 100
            
            return {
                "type": "bilateral",
                "balance_percentage": round(balance_ratio, 2),
                "dominant_sender": participants[0] if count1 > count2 else participants[1]
            }
        
        return {"type": "unknown", "balance": "N/A"}
    
    def _calculate_relationship_health(self) -> int:
        if not self.messages:
            return 0
            
        # Simple scoring based on various factors
        score = 50  # Base score
        
        # Response time factor
        psych_analysis = self.psychological_analysis()
        if psych_analysis.get("average_response_time_minutes", 0) < 60:
            score += 10
        
        # Emotional balance
        emotions = psych_analysis.get("emotional_tone_by_sender", {})
        positive_total = sum(data.get("positive", 0) for data in emotions.values())
        negative_total = sum(data.get("negative", 0) for data in emotions.values())
        
        if positive_total > negative_total:
            score += 15
        elif negative_total > positive_total * 2:
            score -= 10
        
        # Communication balance
        comm_analysis = self.communication_analysis()
        balance_info = comm_analysis.get("communication_balance", {})
        if balance_info.get("type") == "bilateral" and balance_info.get("balance_percentage", 0) > 70:
            score += 15
        
        return max(0, min(100, score))
    
    def _generate_recommendations(self) -> List[str]:
        recommendations = []
        
        # Analyze current state
        linguistic = self.linguistic_analysis()
        psychological = self.psychological_analysis()
        communication = self.communication_analysis()
        
        # Generate recommendations based on analysis
        if communication.get("communication_balance", {}).get("balance_percentage", 100) < 60:
            recommendations.append("Considere equilibrar mais a participação na conversa")
        
        if psychological.get("average_response_time_minutes", 0) > 120:
            recommendations.append("Tempos de resposta mais rápidos podem melhorar a conexão")
        
        if communication.get("question_percentage", 0) < 10:
            recommendations.append("Fazer mais perguntas pode demonstrar maior interesse")
        
        politeness_total = sum(communication.get("politeness_indicators", {}).values())
        if politeness_total < len(self.messages) * 0.1:
            recommendations.append("Incluir mais expressões de cortesia pode melhorar o tom")
        
        return recommendations if recommendations else ["A comunicação parece estar fluindo bem!"]
    
    def generate_comprehensive_report(self) -> Dict:
        return {
            "linguistic_analysis": self.linguistic_analysis(),
            "psychological_analysis": self.psychological_analysis(),
            "communication_analysis": self.communication_analysis(),
            "relationship_insights": self.relationship_coaching_insights()
        }