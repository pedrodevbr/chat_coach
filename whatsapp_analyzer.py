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
        """Parse timestamp with multiple format support"""
        # Common WhatsApp timestamp formats from different regions/versions
        formats = [
            # Brazilian/European formats
            "%d/%m/%Y %H:%M",           # 25/10/2023 09:15
            "%d/%m/%Y, %H:%M",          # 25/10/2023, 09:15
            "%d/%m/%y %H:%M",           # 25/10/23 09:15
            "%d/%m/%y, %H:%M",          # 25/10/23, 09:15
            
            # US formats
            "%m/%d/%Y %I:%M %p",        # 10/25/2023 9:15 AM
            "%m/%d/%Y, %I:%M %p",       # 10/25/2023, 9:15 AM
            "%m/%d/%y %I:%M %p",        # 10/25/23 9:15 AM
            "%m/%d/%y, %I:%M %p",       # 10/25/23, 9:15 AM
            
            # International formats
            "%Y-%m-%d %H:%M",           # 2023-10-25 09:15
            "%Y-%m-%d, %H:%M",          # 2023-10-25, 09:15
            "%Y/%m/%d %H:%M",           # 2023/10/25 09:15
            "%Y/%m/%d, %H:%M",          # 2023/10/25, 09:15
            
            # Android specific formats
            "%d.%m.%Y %H:%M",           # 25.10.2023 09:15
            "%d.%m.%Y, %H:%M",          # 25.10.2023, 09:15
            "%d.%m.%y %H:%M",           # 25.10.23 09:15
            "%d.%m.%y, %H:%M",          # 25.10.23, 09:15
            
            # Other variations
            "%d-%m-%Y %H:%M",           # 25-10-2023 09:15
            "%d-%m-%Y, %H:%M",          # 25-10-2023, 09:15
            "%d-%m-%y %H:%M",           # 25-10-23 09:15
            "%d-%m-%y, %H:%M",          # 25-10-23, 09:15
            
            # With seconds
            "%d/%m/%Y %H:%M:%S",        # 25/10/2023 09:15:30
            "%d/%m/%Y, %H:%M:%S",       # 25/10/2023, 09:15:30
            "%m/%d/%Y %I:%M:%S %p",     # 10/25/2023 9:15:30 AM
            "%m/%d/%Y, %I:%M:%S %p",    # 10/25/2023, 9:15:30 AM

            "[%Y-%m-%d %H:%M:%S]",        # [2023-10-25 09:15:30]
            "[%d/%m/%Y %H:%M:%S]",       # [25/10/2023 09:15:30]
            "[%m/%d/%Y %I:%M:%S %p]",    # [10/25/2023 9:15:30 AM]
            "[%d-%m-%Y %H:%M:%S]",       # [25-10-2023 09:15:30]
            "[%d.%m.%Y %H:%M:%S]",       # [25.10.2023 09:15:30]

        ]
        
        # Clean up common variations in timestamp string
        timestamp_clean = timestamp_str.strip()
        
        # Try each format
        for fmt in formats:
            try:
                return datetime.datetime.strptime(timestamp_clean, fmt)
            except ValueError:
                continue
        
        # If none work, try to extract numbers and make educated guess
        try:
            import re
            # Extract numbers from timestamp
            numbers = re.findall(r'\d+', timestamp_clean)
            
            if len(numbers) >= 5:  # At least day, month, year, hour, minute
                # Try to determine format based on number ranges
                nums = [int(n) for n in numbers]
                
                # Heuristic: if first number > 31 or second number > 12, likely YYYY-MM-DD
                if nums[0] > 31 or (nums[0] > 12 and nums[1] <= 12):
                    # Year first format
                    year, month, day = nums[0], nums[1], nums[2]
                elif nums[0] <= 31 and nums[1] <= 12:
                    # Day first format (European)
                    day, month, year = nums[0], nums[1], nums[2]
                elif nums[0] <= 12 and nums[1] <= 31:
                    # Month first format (US)
                    month, day, year = nums[0], nums[1], nums[2]
                else:
                    # Default to current format
                    day, month, year = nums[0], nums[1], nums[2]
                
                # Handle 2-digit years
                if year < 100:
                    year += 2000 if year < 50 else 1900
                
                hour = nums[3] if len(nums) > 3 else 0
                minute = nums[4] if len(nums) > 4 else 0
                second = nums[5] if len(nums) > 5 else 0
                
                return datetime.datetime(year, month, day, hour, minute, second)
            
        except (ValueError, IndexError):
            pass
        
        # Last resort: return current time with warning
        print(f"⚠️ Couldn't parse timestamp: {timestamp_str}, using current time")
        return datetime.datetime.now()

class WhatsAppChatAnalyzer:
    def __init__(self):
        self.messages: List[WhatsAppMessage] = []
        self.participants: set = set()
        self.detected_format: str = "Unknown"
        self.parsing_stats: Dict = {
            "total_lines": 0,
            "parsed_messages": 0,
            "skipped_lines": 0,
            "multiline_messages": 0,
            "system_messages": 0
        }
        
    def _detect_format(self, lines: List[str]) -> str:
        """Detect the most common timestamp format in the chat"""
        format_patterns = {
            "Brazilian/European (DD/MM/YYYY)": r'\d{1,2}/\d{1,2}/\d{2,4}',
            "US Format (MM/DD/YYYY AM/PM)": r'\d{1,2}/\d{1,2}/\d{2,4}.*[AP]M',
            "ISO Format (YYYY-MM-DD)": r'\d{4}-\d{1,2}-\d{1,2}',
            "Android Dot (DD.MM.YYYY)": r'\d{1,2}\.\d{1,2}\.\d{2,4}',
            "Dash Format (DD-MM-YYYY)": r'\d{1,2}-\d{1,2}-\d{2,4}(?!\s)'  # Negative lookahead to avoid YYYY-MM-DD
        }
        
        format_counts = {fmt: 0 for fmt in format_patterns.keys()}
        
        for line in lines[:50]:  # Check first 50 lines for format detection
            for format_name, pattern in format_patterns.items():
                if re.search(pattern, line):
                    format_counts[format_name] += 1
        
        # Return the most common format
        detected = max(format_counts, key=format_counts.get)
        return detected if format_counts[detected] > 0 else "Mixed/Unknown"
    
    def parse_chat(self, chat_text: str) -> None:
        """Parse WhatsApp chat with support for multiple timestamp formats"""
        lines = chat_text.strip().split('\n')
        self.parsing_stats["total_lines"] = len(lines)
        
        # Detect primary format
        self.detected_format = self._detect_format(lines)
        
        # Multiple regex patterns for different WhatsApp formats
        message_patterns = [
            # Brazilian/European formats
            r'(\d{1,2}/\d{1,2}/\d{2,4},?\s+\d{1,2}:\d{2}(?::\d{2})?)\s*-\s*([^:]+):\s*(.+)',
            
            # US formats with AM/PM
            r'(\d{1,2}/\d{1,2}/\d{2,4},?\s+\d{1,2}:\d{2}(?::\d{2})?\s*[AP]M)\s*-\s*([^:]+):\s*(.+)',
            
            # ISO formats
            r'(\d{4}-\d{1,2}-\d{1,2},?\s+\d{1,2}:\d{2}(?::\d{2})?)\s*-\s*([^:]+):\s*(.+)',
            
            # Android dot formats
            r'(\d{1,2}\.\d{1,2}\.\d{2,4},?\s+\d{1,2}:\d{2}(?::\d{2})?)\s*-\s*([^:]+):\s*(.+)',
            
            # Dash formats
            r'(\d{1,2}-\d{1,2}-\d{2,4},?\s+\d{1,2}:\d{2}(?::\d{2})?)\s*-\s*([^:]+):\s*(.+)',
            
            # Flexible format - any date-like pattern
            r'([\d\/\-\.]{6,10},?\s+[\d:APM\s]{4,11})\s*-\s*([^:]+):\s*(.+)',

            r'\[([\d\/\-\.]{6,10}\s+[\d:APM\s]{4,11})\]\s*-\s*([^:]+):\s*(.+)',  # With brackets

            r'\[([\d\/\-\.]{6,10}\s+[\d:APM\s]{4,11})\]\s*([^:]+):\s*(.+)',  # With brackets, no dash

            r'([\d\/\-\.]{6,10}\s+[\d:APM\s]{4,11})\s*([^:]+):\s*(.+)',  # No dash

        ]
        
        # Track multiline messages
        current_message = None
        multiline_count = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Try to match as new message
            message_matched = False
            
            for pattern in message_patterns:
                match = re.match(pattern, line)
                if match:
                    # Finish previous message if exists
                    if current_message:
                        if multiline_count > 0:
                            self.parsing_stats["multiline_messages"] += 1
                        self._add_message(*current_message)
                        current_message = None
                        multiline_count = 0
                    
                    timestamp, sender, content = match.groups()
                    sender = sender.strip()
                    content = content.strip()
                    
                    # Check for system messages
                    if content and (content.startswith('<') or content.startswith('‎') or 
                                   'Ligação de voz perdida' in content or 'Missed call' in content):
                        self.parsing_stats["system_messages"] += 1
                        continue
                    
                    if content:
                        current_message = (timestamp, sender, content)
                        message_matched = True
                        break
            
            # If no pattern matched, might be continuation of previous message
            if not message_matched and current_message:
                # Append to current message content
                current_message = (current_message[0], current_message[1], 
                                 current_message[2] + ' ' + line)
                multiline_count += 1
            elif not message_matched:
                self.parsing_stats["skipped_lines"] += 1
        
        # Don't forget the last message
        if current_message:
            if multiline_count > 0:
                self.parsing_stats["multiline_messages"] += 1
            self._add_message(*current_message)
        
        self.parsing_stats["parsed_messages"] = len(self.messages)
    
    def _add_message(self, timestamp: str, sender: str, content: str) -> None:
        """Helper method to add a message after validation"""
        try:
            message = WhatsAppMessage(timestamp, sender, content)
            self.messages.append(message)
            self.participants.add(sender)
        except Exception as e:
            print(f"⚠️ Skipped invalid message: {timestamp} - {sender}: {content[:50]}... (Error: {e})")
    
    def get_parsing_report(self) -> Dict:
        """Get detailed parsing statistics and format detection info"""
        success_rate = (self.parsing_stats["parsed_messages"] / 
                       max(1, self.parsing_stats["total_lines"] - self.parsing_stats["skipped_lines"])) * 100
        
        return {
            "detected_format": self.detected_format,
            "parsing_statistics": self.parsing_stats,
            "success_rate": round(success_rate, 2),
            "format_quality": "Excellent" if success_rate > 90 else 
                            "Good" if success_rate > 70 else 
                            "Fair" if success_rate > 50 else "Poor"
        }
    
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
        
        result = {
            "total_messages": total_messages,
            "participants": list(self.participants),
            "average_words_per_message": statistics.mean(word_counts),
            "average_chars_per_message": statistics.mean(char_counts),
            "sender_statistics": dict(sender_stats),
            "peak_activity_hours": peak_hours,
            "conversation_span_days": (self.messages[-1].timestamp - self.messages[0].timestamp).days if total_messages > 1 else 0
        }
        
        # Add parsing information
        result.update(self.get_parsing_report())
        
        return result
    
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