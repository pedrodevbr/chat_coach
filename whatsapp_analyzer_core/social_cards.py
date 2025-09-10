#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Social Media Cards Generator - Core version
Simple, clean cards for sharing
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import numpy as np
import io
import base64
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class SocialCardGenerator:
    """Generate simple, clean social media cards"""
    
    def __init__(self):
        self.card_size = (10, 10)  # Square format for Instagram
        self.dpi = 108  # Will result in 1080x1080 pixels
        
        # Color schemes
        self.colors = {
            'primary': '#667eea',
            'secondary': '#764ba2',
            'accent': '#f093fb',
            'text_dark': '#2d3748',
            'text_light': '#ffffff',
            'background': '#ffffff',
            'light_bg': '#f7fafc'
        }
    
    def create_relationship_score_card(self, score_data: Dict) -> str:
        """Create a relationship score card"""
        try:
            fig, ax = plt.subplots(figsize=self.card_size, dpi=self.dpi)
            fig.patch.set_facecolor(self.colors['background'])
            ax.set_xlim(0, 10)
            ax.set_ylim(0, 10)
            ax.axis('off')
            
            # Background gradient
            gradient = np.linspace(0, 1, 256).reshape(256, -1)
            gradient = np.vstack((gradient, gradient))
            extent = [0, 10, 0, 10]
            ax.imshow(gradient, aspect='auto', cmap='plasma', alpha=0.1, extent=extent)
            
            # Title
            ax.text(5, 8.5, "💕 Compatibility Score", 
                   fontsize=24, fontweight='bold', ha='center', va='center',
                   color=self.colors['text_dark'])
            
            # Main score circle
            circle = plt.Circle((5, 5.5), 1.5, color=self.colors['primary'], alpha=0.2)
            ax.add_patch(circle)
            
            # Score text
            score = score_data.get('total_score', 0)
            grade = score_data.get('grade', 'C')
            ax.text(5, 5.5, f"{score:.0f}/100", 
                   fontsize=48, fontweight='bold', ha='center', va='center',
                   color=self.colors['primary'])
            
            # Grade
            ax.text(5, 4.5, f"Grade: {grade}", 
                   fontsize=20, fontweight='bold', ha='center', va='center',
                   color=self.colors['text_dark'])
            
            # Percentile
            percentile = score_data.get('percentile', 50)
            ax.text(5, 3.5, f"Better than {percentile}% of couples!", 
                   fontsize=16, ha='center', va='center',
                   color=self.colors['secondary'])
            
            # Description
            description = score_data.get('description', 'Great Connection!')
            ax.text(5, 2.5, description, 
                   fontsize=18, ha='center', va='center', style='italic',
                   color=self.colors['text_dark'])
            
            # Footer
            ax.text(5, 1, "WhatsApp Chat Analyzer", 
                   fontsize=12, ha='center', va='center',
                   color=self.colors['secondary'], alpha=0.7)
            
            return self._save_card_to_base64(fig)
            
        except Exception as e:
            logger.error(f"Error creating relationship score card: {e}")
            return ""
    
    def create_personality_card(self, personality_data: Dict) -> str:
        """Create a chat personality card"""
        try:
            fig, ax = plt.subplots(figsize=self.card_size, dpi=self.dpi)
            fig.patch.set_facecolor(self.colors['background'])
            ax.set_xlim(0, 10)
            ax.set_ylim(0, 10)
            ax.axis('off')
            
            # Background
            rect = FancyBboxPatch((0.5, 0.5), 9, 9, boxstyle="round,pad=0.1", 
                                 facecolor=self.colors['light_bg'], 
                                 edgecolor=self.colors['primary'], linewidth=2)
            ax.add_patch(rect)
            
            # Title
            ax.text(5, 8.5, "Chat Personality", 
                   fontsize=24, fontweight='bold', ha='center', va='center',
                   color=self.colors['text_dark'])
            
            # Archetype
            archetype = personality_data.get('archetype', '😊 Os Comunicadores')
            ax.text(5, 7, archetype, 
                   fontsize=20, fontweight='bold', ha='center', va='center',
                   color=self.colors['primary'])
            
            # Traits
            traits = personality_data.get('traits', ['Sociáveis'])
            traits_text = ' • '.join(traits[:3])
            ax.text(5, 5.5, traits_text, 
                   fontsize=16, ha='center', va='center',
                   color=self.colors['secondary'])
            
            # Description
            description = personality_data.get('description', 'Great communicators!')
            # Wrap long descriptions
            if len(description) > 60:
                words = description.split()
                line1 = ' '.join(words[:len(words)//2])
                line2 = ' '.join(words[len(words)//2:])
                ax.text(5, 4, line1, fontsize=14, ha='center', va='center',
                       color=self.colors['text_dark'])
                ax.text(5, 3.3, line2, fontsize=14, ha='center', va='center',
                       color=self.colors['text_dark'])
            else:
                ax.text(5, 3.5, description, fontsize=14, ha='center', va='center',
                       color=self.colors['text_dark'])
            
            # Footer
            ax.text(5, 1.5, "Discover your chat style!", 
                   fontsize=12, ha='center', va='center', style='italic',
                   color=self.colors['secondary'])
            
            ax.text(5, 1, "WhatsApp Chat Analyzer", 
                   fontsize=10, ha='center', va='center',
                   color=self.colors['secondary'], alpha=0.7)
            
            return self._save_card_to_base64(fig)
            
        except Exception as e:
            logger.error(f"Error creating personality card: {e}")
            return ""
    
    def create_stats_card(self, stats_data: Dict) -> str:
        """Create a statistics card"""
        try:
            fig, ax = plt.subplots(figsize=self.card_size, dpi=self.dpi)
            fig.patch.set_facecolor(self.colors['background'])
            ax.set_xlim(0, 10)
            ax.set_ylim(0, 10)
            ax.axis('off')
            
            # Title
            ax.text(5, 9, "📊 Chat Statistics", 
                   fontsize=24, fontweight='bold', ha='center', va='center',
                   color=self.colors['text_dark'])
            
            # Stats boxes
            stats = [
                (f"📱 {stats_data.get('total_messages', 0)}", "Messages"),
                (f"📝 {stats_data.get('total_words', 0)}", "Words"),
                (f"👥 {stats_data.get('total_participants', 0)}", "Participants"),
                (f"📅 {stats_data.get('duration_days', 0)}", "Days")
            ]
            
            positions = [(2.5, 7), (7.5, 7), (2.5, 4.5), (7.5, 4.5)]
            
            for i, ((value, label), (x, y)) in enumerate(zip(stats, positions)):
                # Box
                rect = FancyBboxPatch((x-1.2, y-0.8), 2.4, 1.6, boxstyle="round,pad=0.1", 
                                     facecolor=self.colors['primary'], alpha=0.1,
                                     edgecolor=self.colors['primary'])
                ax.add_patch(rect)
                
                # Value
                ax.text(x, y+0.2, value, fontsize=18, fontweight='bold', 
                       ha='center', va='center', color=self.colors['primary'])
                
                # Label
                ax.text(x, y-0.3, label, fontsize=12, 
                       ha='center', va='center', color=self.colors['text_dark'])
            
            # Fun fact
            messages_per_day = stats_data.get('messages_per_day', 0)
            if messages_per_day > 0:
                ax.text(5, 2.5, f"🎯 {messages_per_day:.1f} messages per day!", 
                       fontsize=16, ha='center', va='center',
                       color=self.colors['secondary'])
            
            # Footer
            ax.text(5, 1, "WhatsApp Chat Analyzer", 
                   fontsize=12, ha='center', va='center',
                   color=self.colors['secondary'], alpha=0.7)
            
            return self._save_card_to_base64(fig)
            
        except Exception as e:
            logger.error(f"Error creating stats card: {e}")
            return ""
    
    def create_fun_facts_card(self, facts: list) -> str:
        """Create a fun facts card"""
        try:
            fig, ax = plt.subplots(figsize=self.card_size, dpi=self.dpi)
            fig.patch.set_facecolor(self.colors['background'])
            ax.set_xlim(0, 10)
            ax.set_ylim(0, 10)
            ax.axis('off')
            
            # Background decoration
            for i in range(5):
                circle = plt.Circle((1 + i * 2, 9.2), 0.1, 
                                  color=self.colors['accent'], alpha=0.5)
                ax.add_patch(circle)
            
            # Title
            ax.text(5, 8.5, "🎉 Fun Facts", 
                   fontsize=26, fontweight='bold', ha='center', va='center',
                   color=self.colors['text_dark'])
            
            # Facts
            y_positions = [7.5, 6.5, 5.5, 4.5, 3.5]
            for i, fact in enumerate(facts[:5]):
                if i < len(y_positions):
                    ax.text(5, y_positions[i], fact, 
                           fontsize=14, ha='center', va='center',
                           color=self.colors['text_dark'],
                           bbox=dict(boxstyle="round,pad=0.3", 
                                   facecolor=self.colors['light_bg'],
                                   alpha=0.7))
            
            # Footer
            ax.text(5, 2, "Share your chat insights!", 
                   fontsize=14, ha='center', va='center', style='italic',
                   color=self.colors['secondary'])
            
            ax.text(5, 1, "WhatsApp Chat Analyzer", 
                   fontsize=12, ha='center', va='center',
                   color=self.colors['secondary'], alpha=0.7)
            
            return self._save_card_to_base64(fig)
            
        except Exception as e:
            logger.error(f"Error creating fun facts card: {e}")
            return ""
    
    def _save_card_to_base64(self, fig) -> str:
        """Save matplotlib figure to base64 string"""
        try:
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=self.dpi, bbox_inches='tight',
                       facecolor='white', edgecolor='none', pad_inches=0.1)
            buffer.seek(0)
            
            # Convert to base64
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close(fig)  # Clean up
            
            return f"data:image/png;base64,{image_base64}"
            
        except Exception as e:
            logger.error(f"Error saving card to base64: {e}")
            plt.close(fig)
            return ""