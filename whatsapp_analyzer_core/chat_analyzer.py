#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WhatsApp Chat Analyzer - Core Engine
Simplified version with essential features only
"""

import re
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from collections import Counter
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Message:
    """Represents a WhatsApp message"""
    timestamp: datetime
    sender: str
    content: str
    word_count: int = 0
    
    def __post_init__(self):
        self.word_count = len(self.content.split())

class WhatsAppAnalyzer:
    """Core WhatsApp chat analyzer with essential features"""
    
    def __init__(self):
        self.messages: List[Message] = []
        self.participants: set = set()
        self.parsing_stats = {
            'total_lines': 0,
            'parsed_messages': 0,
            'success_rate': 0.0
        }
    
    def parse_chat(self, chat_text: str) -> bool:
        """Parse WhatsApp chat text with multi-format support"""
        try:
            lines = chat_text.strip().split('\n')
            self.parsing_stats['total_lines'] = len(lines)
            
            # Common WhatsApp timestamp patterns
            patterns = [
                r'(\d{1,2}/\d{1,2}/\d{4},?\s+\d{1,2}:\d{2})\s*-\s*([^:]+):\s*(.*)',  # DD/MM/YYYY, HH:MM - Name: Message
                r'(\d{1,2}/\d{1,2}/\d{4}\s+\d{1,2}:\d{2})\s*-\s*([^:]+):\s*(.*)',     # DD/MM/YYYY HH:MM - Name: Message
                r'(\d{1,2}/\d{1,2}/\d{2},?\s+\d{1,2}:\d{2})\s*-\s*([^:]+):\s*(.*)',   # DD/MM/YY, HH:MM - Name: Message
                r'(\[\d{1,2}/\d{1,2}/\d{4},?\s+\d{1,2}:\d{2}:\d{2}\])\s+([^:]+):\s*(.*)', # [DD/MM/YYYY, HH:MM:SS] Name: Message
            ]
            
            parsed_count = 0
            current_message = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Try to match against patterns
                matched = False
                for pattern in patterns:
                    match = re.match(pattern, line)
                    if match:
                        # Save previous multiline message
                        if current_message:
                            self._add_message(current_message[0], current_message[1], current_message[2])
                            parsed_count += 1
                        
                        timestamp_str, sender, content = match.groups()
                        timestamp = self._parse_timestamp(timestamp_str)
                        
                        if timestamp:
                            current_message = (timestamp, sender.strip(), content.strip())
                            matched = True
                            break
                
                # If no pattern matched, it's likely a continuation of the previous message
                if not matched and current_message:
                    current_message = (current_message[0], current_message[1], current_message[2] + ' ' + line)
            
            # Don't forget the last message
            if current_message:
                self._add_message(current_message[0], current_message[1], current_message[2])
                parsed_count += 1
            
            self.parsing_stats['parsed_messages'] = parsed_count
            self.parsing_stats['success_rate'] = (parsed_count / len(lines)) * 100 if lines else 0
            
            logger.info(f"Parsed {parsed_count} messages from {len(self.participants)} participants")
            return len(self.messages) > 0
            
        except Exception as e:
            logger.error(f"Error parsing chat: {e}")
            return False
    
    def _parse_timestamp(self, timestamp_str: str) -> Optional[datetime]:
        """Parse timestamp with multiple format support"""
        # Clean timestamp string
        timestamp_str = timestamp_str.strip('[]')
        
        formats = [
            "%d/%m/%Y, %H:%M",
            "%d/%m/%Y %H:%M",
            "%d/%m/%y, %H:%M",
            "%d/%m/%y %H:%M",
            "%m/%d/%Y, %H:%M",
            "%m/%d/%Y %H:%M",
            "%d/%m/%Y, %H:%M:%S",
            "%d/%m/%Y %H:%M:%S",
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue
        
        logger.warning(f"Could not parse timestamp: {timestamp_str}")
        return None
    
    def _add_message(self, timestamp: datetime, sender: str, content: str):
        """Add a parsed message"""
        if timestamp and sender and content:
            message = Message(timestamp, sender, content)
            self.messages.append(message)
            self.participants.add(sender)
    
    def get_basic_stats(self) -> Dict:
        """Get basic conversation statistics"""
        if not self.messages:
            return {}
        
        # Calculate basic metrics
        total_messages = len(self.messages)
        total_words = sum(msg.word_count for msg in self.messages)
        
        # Time span
        first_message = min(self.messages, key=lambda x: x.timestamp)
        last_message = max(self.messages, key=lambda x: x.timestamp)
        duration = (last_message.timestamp - first_message.timestamp).days
        
        # Per participant stats
        participant_stats = {}
        for participant in self.participants:
            p_messages = [msg for msg in self.messages if msg.sender == participant]
            participant_stats[participant] = {
                'messages': len(p_messages),
                'words': sum(msg.word_count for msg in p_messages),
                'avg_words': sum(msg.word_count for msg in p_messages) / len(p_messages) if p_messages else 0
            }
        
        return {
            'total_messages': total_messages,
            'total_words': total_words,
            'total_participants': len(self.participants),
            'duration_days': duration,
            'messages_per_day': total_messages / max(1, duration),
            'avg_words_per_message': total_words / total_messages,
            'first_message': first_message.timestamp.strftime("%Y-%m-%d %H:%M"),
            'last_message': last_message.timestamp.strftime("%Y-%m-%d %H:%M"),
            'participants': list(self.participants),
            'participant_stats': participant_stats,
            'parsing_stats': self.parsing_stats
        }
    
    def get_activity_patterns(self) -> Dict:
        """Analyze activity patterns"""
        if not self.messages:
            return {}
        
        # Hour distribution
        hours = [msg.timestamp.hour for msg in self.messages]
        hour_counts = Counter(hours)
        
        # Day distribution
        days = [msg.timestamp.strftime('%A') for msg in self.messages]
        day_counts = Counter(days)
        
        # Most active periods
        peak_hour = max(hour_counts, key=hour_counts.get)
        peak_day = max(day_counts, key=day_counts.get)
        
        return {
            'hour_distribution': dict(hour_counts),
            'day_distribution': dict(day_counts),
            'peak_hour': peak_hour,
            'peak_day': peak_day,
            'peak_hour_messages': hour_counts[peak_hour],
            'peak_day_messages': day_counts[peak_day]
        }
    
    def get_word_analysis(self) -> Dict:
        """Basic word frequency analysis"""
        if not self.messages:
            return {}
        
        # Combine all messages
        all_text = ' '.join([msg.content for msg in self.messages])
        words = re.findall(r'\b\w+\b', all_text.lower())
        
        # Portuguese stop words
        stop_words = {
            'que', 'de', 'a', 'o', 'e', 'do', 'da', 'em', 'um', 'para', 'é', 'com', 'não', 'uma', 'os', 'no',
            'se', 'na', 'por', 'mais', 'as', 'dos', 'como', 'mas', 'foi', 'ao', 'ele', 'das', 'tem', 'à', 'seu',
            'sua', 'ou', 'ser', 'quando', 'muito', 'há', 'nos', 'já', 'está', 'eu', 'também', 'só', 'pelo',
            'pela', 'até', 'isso', 'ela', 'entre', 'era', 'depois', 'sem', 'mesmo', 'aos', 'ter', 'seus', 'suas'
        }
        
        # Filter words
        filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
        word_counts = Counter(filtered_words)
        
        return {
            'total_words': len(words),
            'unique_words': len(set(words)),
            'filtered_words': len(filtered_words),
            'top_words': word_counts.most_common(20),
            'vocabulary_richness': len(set(words)) / len(words) if words else 0
        }
    
    def generate_simple_report(self) -> Dict:
        """Generate a comprehensive but simple report"""
        return {
            'basic_stats': self.get_basic_stats(),
            'activity_patterns': self.get_activity_patterns(),
            'word_analysis': self.get_word_analysis(),
            'generated_at': datetime.now().isoformat()
        }