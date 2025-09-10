#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Shareable Visual Cards Generator for WhatsApp Chat Analyzer
Creates Instagram/Twitter/TikTok-ready visual content that users want to share
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import matplotlib.patheffects
import seaborn as sns
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io
import base64
from typing import Dict, List, Tuple
import textwrap

# Set up modern, trendy color palettes
PALETTES = {
    "sunset": ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7"],
    "neon": ["#FF0080", "#00FFFF", "#FFFF00", "#FF8000", "#8000FF"],
    "pastel": ["#FFB3BA", "#FFDFBA", "#FFFFBA", "#BAFFC9", "#BAE1FF"],
    "dark": ["#2C3E50", "#E74C3C", "#3498DB", "#F39C12", "#9B59B6"],
    "gradient": ["#667eea", "#764ba2", "#f093fb", "#f5576c", "#4facfe"]
}

class ShareableCardGenerator:
    def __init__(self):
        self.fig_size = (10, 10)  # Square format for social media
        self.dpi = 300  # High resolution for sharing
        
    def create_relationship_score_card(self, score_data: Dict) -> str:
        """Create viral-worthy relationship score card"""
        
        fig, ax = plt.subplots(figsize=self.fig_size, dpi=self.dpi)
        fig.patch.set_facecolor('#1a1a1a')  # Dark background
        ax.set_facecolor('#1a1a1a')
        
        # Remove axes
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis('off')
        
        # Title
        title_text = "💕 RELATIONSHIP COMPATIBILITY"
        ax.text(5, 9.2, title_text, fontsize=24, fontweight='bold', 
                ha='center', va='center', color='white')
        
        # Main score circle
        circle = plt.Circle((5, 6), 1.5, color=PALETTES["neon"][0], alpha=0.8)
        ax.add_patch(circle)
        
        # Score text
        score = score_data.get('total_score', 0)
        grade = score_data.get('grade', 'C')
        ax.text(5, 6, f"{score}/100", fontsize=36, fontweight='bold', 
                ha='center', va='center', color='white')
        ax.text(5, 5.2, f"Grade: {grade}", fontsize=20, fontweight='bold',
                ha='center', va='center', color='white')
        
        # Percentile
        percentile = score_data.get('percentile', 50)
        ax.text(5, 4.2, f"Better than {percentile}% of couples!", 
                fontsize=16, ha='center', va='center', color=PALETTES["sunset"][3])
        
        # Personality type
        personality = score_data.get('personality', {}).get('type', 'Great Connection')
        ax.text(5, 3.5, personality, fontsize=18, fontweight='bold',
                ha='center', va='center', color=PALETTES["sunset"][1])
        
        # Fun facts
        facts = score_data.get('fun_facts', [])[:2]
        for i, fact in enumerate(facts):
            ax.text(5, 2.5 - i*0.4, fact, fontsize=12, 
                   ha='center', va='center', color='white', alpha=0.8)
        
        # Watermark
        ax.text(5, 0.5, "Created with ChatCoach AI", fontsize=10, 
                ha='center', va='center', color='white', alpha=0.5)
        
        return self._save_figure_as_base64(fig)
    
    def create_personality_card(self, personality_data: Dict) -> str:
        """Create shareable personality archetype card"""
        
        fig, ax = plt.subplots(figsize=self.fig_size, dpi=self.dpi)
        
        # Gradient background
        gradient = np.linspace(0, 1, 256).reshape(256, -1)
        gradient = np.vstack((gradient, gradient))
        ax.imshow(gradient, aspect='auto', cmap='viridis', extent=[0, 10, 0, 10])
        
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis('off')
        
        # Title
        ax.text(5, 9, "YOUR CHAT PERSONALITY", fontsize=24, fontweight='bold',
                ha='center', va='center', color='white')
        
        # Archetype
        archetype = personality_data.get('archetype', 'The Chatters')
        ax.text(5, 7.5, archetype, fontsize=28, fontweight='bold',
                ha='center', va='center', color='white',
                bbox=dict(boxstyle="round,pad=0.3", facecolor='black', alpha=0.7))
        
        # Traits
        traits = personality_data.get('traits', [])[:4]
        for i, trait in enumerate(traits):
            y_pos = 6 - i * 0.8
            ax.text(5, y_pos, trait, fontsize=14, 
                   ha='center', va='center', color='white',
                   bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.2))
        
        # Fun description (truncated)
        description = personality_data.get('fun_description', '')[:100] + "..."
        wrapped_text = textwrap.fill(description, width=40)
        ax.text(5, 2, wrapped_text, fontsize=11, ha='center', va='center', 
                color='white', alpha=0.9)
        
        # Watermark
        ax.text(5, 0.3, "Discover your chat style • ChatCoach AI", 
                fontsize=10, ha='center', va='center', color='white', alpha=0.6)
        
        return self._save_figure_as_base64(fig)
    
    def create_stats_highlight_card(self, stats: Dict) -> str:
        """Create eye-catching stats card"""
        
        fig, ax = plt.subplots(figsize=self.fig_size, dpi=self.dpi)
        fig.patch.set_facecolor('#000014')  # Deep space background
        ax.set_facecolor('#000014')
        
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis('off')
        
        # Title with glow effect
        ax.text(5, 9, "📊 CHAT STATISTICS", fontsize=26, fontweight='bold',
                ha='center', va='center', color='#00FFFF',
                path_effects=[matplotlib.patheffects.withStroke(linewidth=3, foreground='#000033')])
        
        # Main stats in boxes
        stats_to_show = [
            ("Messages", stats.get('total_messages', 0), "💬"),
            ("Words", stats.get('total_words', 0), "📝"),
            ("Days", stats.get('duration_days', 0), "📅"),
            ("Avg/Day", f"{stats.get('messages_per_day', 0):.1f}", "📱")
        ]
        
        colors = PALETTES["neon"]
        positions = [(2.5, 6.5), (7.5, 6.5), (2.5, 4), (7.5, 4)]
        
        for i, (label, value, emoji) in enumerate(stats_to_show):
            x, y = positions[i]
            color = colors[i % len(colors)]
            
            # Background box
            box = FancyBboxPatch((x-1, y-0.8), 2, 1.6, 
                               boxstyle="round,pad=0.1", 
                               facecolor=color, alpha=0.3,
                               edgecolor=color, linewidth=2)
            ax.add_patch(box)
            
            # Emoji
            ax.text(x, y+0.3, emoji, fontsize=24, ha='center', va='center')
            
            # Value
            ax.text(x, y-0.1, str(value), fontsize=20, fontweight='bold',
                   ha='center', va='center', color='white')
            
            # Label
            ax.text(x, y-0.5, label, fontsize=12, 
                   ha='center', va='center', color='white', alpha=0.8)
        
        # Fun fact at bottom
        fun_fact = stats.get('fun_fact', 'Amazing conversation!')
        ax.text(5, 2, fun_fact, fontsize=14, ha='center', va='center',
                color='#00FFFF', fontweight='bold')
        
        # Watermark
        ax.text(5, 0.5, "Get your chat analysis • ChatCoach", 
                fontsize=10, ha='center', va='center', color='white', alpha=0.5)
        
        return self._save_figure_as_base64(fig)
    
    def create_fun_facts_card(self, facts: List[str]) -> str:
        """Create mind-blowing fun facts card"""
        
        fig, ax = plt.subplots(figsize=self.fig_size, dpi=self.dpi)
        
        # Explosive gradient background
        theta = np.linspace(0, 2*np.pi, 100)
        r = np.linspace(0, 1, 50)
        T, R = np.meshgrid(theta, r)
        z = np.sin(5*T) * R
        
        ax.contourf(T, R, z, levels=20, cmap='plasma', alpha=0.8)
        ax.set_xlim(0, 2*np.pi)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        # Convert to square coordinates for text
        ax2 = fig.add_subplot(111)
        ax2.set_xlim(0, 10)
        ax2.set_ylim(0, 10)
        ax2.axis('off')
        ax2.patch.set_alpha(0)
        
        # Explosive title
        ax2.text(5, 9, "🤯 MIND-BLOWING", fontsize=24, fontweight='bold',
                ha='center', va='center', color='white',
                path_effects=[matplotlib.patheffects.withStroke(linewidth=4, foreground='black')])
        ax2.text(5, 8.3, "CHAT FACTS!", fontsize=24, fontweight='bold',
                ha='center', va='center', color='#FFFF00',
                path_effects=[matplotlib.patheffects.withStroke(linewidth=4, foreground='black')])
        
        # Facts
        selected_facts = facts[:3]  # Top 3 most viral facts
        emojis = ["🔥", "⚡", "🌟"]
        
        for i, fact in enumerate(selected_facts):
            y_pos = 6.5 - i * 1.5
            emoji = emojis[i % len(emojis)]
            
            # Background bubble
            bubble = plt.Circle((5, y_pos), 1.8, color='white', alpha=0.9)
            ax2.add_patch(bubble)
            
            # Emoji
            ax2.text(5, y_pos + 0.5, emoji, fontsize=20, ha='center', va='center')
            
            # Fact text (wrapped)
            wrapped_fact = textwrap.fill(fact, width=25)
            ax2.text(5, y_pos - 0.2, wrapped_fact, fontsize=11, fontweight='bold',
                    ha='center', va='center', color='black')
        
        # Call to action
        ax2.text(5, 1.5, "What secrets do YOUR chats reveal?", 
                fontsize=14, fontweight='bold', ha='center', va='center', 
                color='white', style='italic')
        
        # Watermark
        ax2.text(5, 0.3, "Analyze your chats • ChatCoach AI", 
                fontsize=10, ha='center', va='center', color='white', alpha=0.7)
        
        return self._save_figure_as_base64(fig)
    
    def create_comparison_card(self, comparison_data: Dict) -> str:
        """Create 'vs average couples' comparison card"""
        
        fig, ax = plt.subplots(figsize=self.fig_size, dpi=self.dpi)
        
        # Split screen design
        ax.axvline(x=5, color='white', linewidth=3, alpha=0.8)
        
        # Left side (YOU) - vibrant
        left_rect = patches.Rectangle((0, 0), 5, 10, linewidth=0, 
                                    facecolor=PALETTES["gradient"][0], alpha=0.8)
        ax.add_patch(left_rect)
        
        # Right side (AVERAGE) - muted
        right_rect = patches.Rectangle((5, 0), 5, 10, linewidth=0, 
                                     facecolor='#666666', alpha=0.6)
        ax.add_patch(right_rect)
        
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis('off')
        
        # Headers
        ax.text(2.5, 9, "YOU TWO", fontsize=20, fontweight='bold',
                ha='center', va='center', color='white')
        ax.text(7.5, 9, "AVERAGE COUPLES", fontsize=16, fontweight='bold',
                ha='center', va='center', color='white')
        
        # Crown for winners
        ax.text(2.5, 8.5, "👑", fontsize=30, ha='center', va='center')
        
        # Comparison metrics
        metrics = [
            ("Response Time", "67% faster", "slower"),
            ("Daily Messages", "2.3x more", "fewer"),
            ("Topic Variety", "156% more diverse", "repetitive"),
            ("Night Chats", "89% more", "basic hours")
        ]
        
        for i, (metric, your_stat, their_stat) in enumerate(metrics):
            y_pos = 7.5 - i * 1.5
            
            # Your side (left)
            ax.text(2.5, y_pos, metric, fontsize=12, fontweight='bold',
                   ha='center', va='center', color='white')
            ax.text(2.5, y_pos - 0.4, your_stat, fontsize=14, fontweight='bold',
                   ha='center', va='center', color='#00FFFF')
            
            # Their side (right)
            ax.text(7.5, y_pos - 0.4, their_stat, fontsize=12,
                   ha='center', va='center', color='white', alpha=0.7)
        
        # Bottom message
        percentile = comparison_data.get('percentile', 85)
        ax.text(5, 1, f"YOU'RE BETTER THAN {percentile}% OF COUPLES!", 
                fontsize=16, fontweight='bold', ha='center', va='center', 
                color='#FFFF00',
                bbox=dict(boxstyle="round,pad=0.3", facecolor='black', alpha=0.8))
        
        # Watermark
        ax.text(5, 0.3, "Compare your relationship • ChatCoach", 
                fontsize=9, ha='center', va='center', color='white', alpha=0.6)
        
        return self._save_figure_as_base64(fig)
    
    def create_premium_teaser_card(self) -> str:
        """Create premium features teaser card"""
        
        fig, ax = plt.subplots(figsize=self.fig_size, dpi=self.dpi)
        
        # Premium gradient background (gold/black)
        gradient = np.linspace(0, 1, 256).reshape(1, -1)
        gradient = np.vstack([gradient] * 256)
        ax.imshow(gradient, aspect='auto', cmap='YlOrBr', extent=[0, 10, 0, 10], alpha=0.8)
        
        # Dark overlay for text readability
        overlay = patches.Rectangle((0, 0), 10, 10, linewidth=0, 
                                  facecolor='black', alpha=0.6)
        ax.add_patch(overlay)
        
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis('off')
        
        # Premium badge
        ax.text(5, 9.2, "✨ PREMIUM FEATURES ✨", fontsize=22, fontweight='bold',
                ha='center', va='center', color='gold')
        
        # Lock icon
        ax.text(5, 8.3, "🔒", fontsize=40, ha='center', va='center')
        
        # Teaser features
        features = [
            "🧠 AI Relationship Counseling",
            "💝 Compatibility Predictions", 
            "📈 Relationship Trend Analysis",
            "🎨 Custom Branded Reports",
            "🔮 Future Conversation Topics"
        ]
        
        for i, feature in enumerate(features):
            y_pos = 6.8 - i * 0.8
            ax.text(5, y_pos, feature, fontsize=13, fontweight='bold',
                   ha='center', va='center', color='white',
                   bbox=dict(boxstyle="round,pad=0.2", facecolor='gold', alpha=0.3))
        
        # Call to action
        ax.text(5, 2.2, "UNLOCK PREMIUM", fontsize=20, fontweight='bold',
                ha='center', va='center', color='gold',
                bbox=dict(boxstyle="round,pad=0.3", facecolor='black', alpha=0.8))
        
        ax.text(5, 1.6, "Get deeper insights into your relationship!", 
                fontsize=12, ha='center', va='center', color='white', style='italic')
        
        # Pricing hint
        ax.text(5, 1, "Starting at $4.99/month", fontsize=14, fontweight='bold',
                ha='center', va='center', color='#90EE90')
        
        # Watermark
        ax.text(5, 0.3, "ChatCoach AI Premium", 
                fontsize=10, ha='center', va='center', color='white', alpha=0.7)
        
        return self._save_figure_as_base64(fig)
    
    def create_streak_achievement_card(self, streak_days: int) -> str:
        """Create achievement/streak card"""
        
        fig, ax = plt.subplots(figsize=self.fig_size, dpi=self.dpi)
        
        # Fire gradient background
        ax.imshow(np.random.rand(10, 10), cmap='hot', extent=[0, 10, 0, 10], alpha=0.7)
        
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis('off')
        
        # Achievement banner
        banner = FancyBboxPatch((1, 8), 8, 1.5, boxstyle="round,pad=0.1",
                              facecolor='gold', edgecolor='orange', linewidth=3)
        ax.add_patch(banner)
        
        ax.text(5, 8.75, "🏆 ACHIEVEMENT UNLOCKED! 🏆", 
                fontsize=18, fontweight='bold', ha='center', va='center', color='black')
        
        # Fire emojis
        fire_positions = [(2, 7), (8, 7), (1, 4), (9, 4), (3, 2), (7, 2)]
        for x, y in fire_positions:
            ax.text(x, y, "🔥", fontsize=24, ha='center', va='center')
        
        # Main achievement
        ax.text(5, 6, f"{streak_days} DAY", fontsize=32, fontweight='bold',
                ha='center', va='center', color='white',
                path_effects=[matplotlib.patheffects.withStroke(linewidth=4, foreground='black')])
        
        ax.text(5, 5.2, "CHAT STREAK!", fontsize=28, fontweight='bold',
                ha='center', va='center', color='#FFFF00',
                path_effects=[matplotlib.patheffects.withStroke(linewidth=4, foreground='black')])
        
        # Congratulations
        ax.text(5, 4, "You two are unstoppable!", fontsize=16, fontweight='bold',
                ha='center', va='center', color='white', style='italic')
        
        # Stats
        ax.text(5, 3, f"🎯 Consistency Level: LEGENDARY", fontsize=14,
                ha='center', va='center', color='white',
                bbox=dict(boxstyle="round,pad=0.2", facecolor='red', alpha=0.7))
        
        # Motivational quote
        quotes = [
            "Communication is the fuel of relationships! 💕",
            "Daily chats = daily connection! 🌟", 
            "You're relationship goals! 👑",
            "Consistency is the key to connection! 🗝️"
        ]
        quote = quotes[streak_days % len(quotes)]
        ax.text(5, 1.5, quote, fontsize=12, ha='center', va='center', 
                color='white', fontweight='bold')
        
        # Watermark
        ax.text(5, 0.3, "Keep the streak alive • ChatCoach", 
                fontsize=10, ha='center', va='center', color='white', alpha=0.7)
        
        return self._save_figure_as_base64(fig)
    
    def _save_figure_as_base64(self, fig) -> str:
        """Save matplotlib figure as base64 string for embedding"""
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', bbox_inches='tight', 
                   facecolor=fig.get_facecolor(), dpi=self.dpi)
        buffer.seek(0)
        
        # Convert to base64
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close(fig)  # Free memory
        
        return f"data:image/png;base64,{image_base64}"
    
    def generate_all_cards(self, analyzer_data: Dict) -> Dict[str, str]:
        """Generate all shareable cards and return as base64 images"""
        
        cards = {}
        
        # Only generate cards if we have data
        messages = analyzer_data.get('messages', [])
        if not messages:
            return cards
        
        try:
            # Basic stats card
            stats = {
                'total_messages': len(messages),
                'total_words': sum(getattr(msg, 'word_count', 0) if hasattr(msg, 'word_count') else 0 for msg in messages),
                'duration_days': analyzer_data.get('conversation_span_days', 0),
                'messages_per_day': analyzer_data.get('messages_per_day', 0),
                'fun_fact': "Your chat is amazing! 🌟"
            }
            cards['stats'] = self.create_stats_highlight_card(stats)
            
            # Premium teaser (always available)
            cards['premium'] = self.create_premium_teaser_card()
            
        except Exception as e:
            print(f"Error generating cards: {e}")
        
        return cards

# Global instance
card_generator = ShareableCardGenerator()