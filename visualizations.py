import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from wordcloud import WordCloud
import numpy as np
from collections import Counter
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import re
from typing import List, Dict
import os
from datetime import datetime, timedelta

# Set style for better looking plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class WhatsAppVisualizer:
    def __init__(self, analyzer):
        self.analyzer = analyzer
        self.messages = analyzer.messages
        self.participants = list(analyzer.participants)
        
    def create_message_timeline(self, save_path: str = None, show_plot: bool = True):
        """Create an interactive timeline showing messages over time"""
        if not self.messages:
            print("❌ Sem mensagens para visualizar!")
            return
            
        # Prepare data
        dates = [msg.timestamp.date() for msg in self.messages]
        df = pd.DataFrame({'date': dates})
        daily_counts = df.groupby('date').size().reset_index(name='messages')
        daily_counts['date'] = pd.to_datetime(daily_counts['date'])
        
        # Create interactive plot with Plotly
        fig = px.line(daily_counts, x='date', y='messages', 
                     title='📈 Timeline de Mensagens ao Longo do Tempo',
                     labels={'date': 'Data', 'messages': 'Número de Mensagens'},
                     line_shape='spline')
        
        fig.update_layout(
            title_font_size=16,
            xaxis_title_font_size=14,
            yaxis_title_font_size=14,
            hovermode='x unified'
        )
        
        if save_path:
            fig.write_html(save_path.replace('.png', '_timeline.html'))
            print(f"📊 Timeline salvo em: {save_path.replace('.png', '_timeline.html')}")
        
        if show_plot:
            fig.show()
        
        return fig
    
    def create_activity_heatmap(self, save_path: str = None, show_plot: bool = True):
        """Create heatmap showing activity patterns by hour and day of week"""
        if not self.messages:
            print("❌ Sem mensagens para visualizar!")
            return
            
        # Prepare data
        hours = [msg.timestamp.hour for msg in self.messages]
        days = [msg.timestamp.strftime('%A') for msg in self.messages]
        
        df = pd.DataFrame({'hour': hours, 'day': days})
        
        # Create pivot table for heatmap
        day_hour_counts = df.groupby(['day', 'hour']).size().unstack(fill_value=0)
        
        # Reorder days
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_hour_counts = day_hour_counts.reindex(day_order)
        
        # Create heatmap
        plt.figure(figsize=(15, 8))
        sns.heatmap(day_hour_counts, annot=True, fmt='d', cmap='YlOrRd', cbar_kws={'label': 'Número de Mensagens'})
        plt.title('🔥 Mapa de Calor - Atividade por Hora e Dia da Semana', fontsize=16, pad=20)
        plt.xlabel('Hora do Dia', fontsize=14)
        plt.ylabel('Dia da Semana', fontsize=14)
        plt.xticks(range(24), [f'{i}:00' for i in range(24)], rotation=45)
        plt.tight_layout()
        
        if save_path:
            heatmap_path = save_path.replace('.png', '_heatmap.png')
            plt.savefig(heatmap_path, dpi=300, bbox_inches='tight')
            print(f"🔥 Heatmap salvo em: {heatmap_path}")
        
        if show_plot:
            plt.show()
        else:
            plt.close()
    
    def create_participant_comparison(self, save_path: str = None, show_plot: bool = True):
        """Create comparison charts between participants"""
        if not self.messages or len(self.participants) < 2:
            print("❌ Necessário pelo menos 2 participantes para comparação!")
            return
            
        # Prepare data
        participant_data = {}
        for participant in self.participants:
            p_messages = [msg for msg in self.messages if msg.sender == participant]
            participant_data[participant] = {
                'messages': len(p_messages),
                'words': sum(msg.word_count for msg in p_messages),
                'avg_words': sum(msg.word_count for msg in p_messages) / len(p_messages) if p_messages else 0,
                'chars': sum(msg.char_count for msg in p_messages),
                'avg_chars': sum(msg.char_count for msg in p_messages) / len(p_messages) if p_messages else 0
            }
        
        # Create subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        participants = list(participant_data.keys())
        colors = sns.color_palette("husl", len(participants))
        
        # Messages count
        messages_counts = [participant_data[p]['messages'] for p in participants]
        ax1.bar(participants, messages_counts, color=colors)
        ax1.set_title('💬 Total de Mensagens por Participante', fontsize=14)
        ax1.set_ylabel('Número de Mensagens')
        
        # Words count
        words_counts = [participant_data[p]['words'] for p in participants]
        ax2.bar(participants, words_counts, color=colors)
        ax2.set_title('📝 Total de Palavras por Participante', fontsize=14)
        ax2.set_ylabel('Número de Palavras')
        
        # Average words per message
        avg_words = [participant_data[p]['avg_words'] for p in participants]
        ax3.bar(participants, avg_words, color=colors)
        ax3.set_title('📊 Média de Palavras por Mensagem', fontsize=14)
        ax3.set_ylabel('Palavras por Mensagem')
        
        # Average characters per message
        avg_chars = [participant_data[p]['avg_chars'] for p in participants]
        ax4.bar(participants, avg_chars, color=colors)
        ax4.set_title('📏 Média de Caracteres por Mensagem', fontsize=14)
        ax4.set_ylabel('Caracteres por Mensagem')
        
        plt.tight_layout()
        
        if save_path:
            comparison_path = save_path.replace('.png', '_comparison.png')
            plt.savefig(comparison_path, dpi=300, bbox_inches='tight')
            print(f"📊 Comparação salva em: {comparison_path}")
        
        if show_plot:
            plt.show()
        else:
            plt.close()
    
    def create_wordcloud(self, participant: str = None, save_path: str = None, show_plot: bool = True):
        """Create word cloud from messages"""
        if not self.messages:
            print("❌ Sem mensagens para criar nuvem de palavras!")
            return
            
        # Filter messages by participant if specified
        if participant and participant in self.participants:
            messages = [msg.content for msg in self.messages if msg.sender == participant]
            title = f"☁️ Nuvem de Palavras - {participant}"
            filename_suffix = f"_wordcloud_{participant.replace(' ', '_')}.png"
        else:
            messages = [msg.content for msg in self.messages]
            title = "☁️ Nuvem de Palavras - Conversa Completa"
            filename_suffix = "_wordcloud_all.png"
        
        # Combine all messages
        text = ' '.join(messages)
        
        # Clean text (remove URLs, mentions, etc.)
        text = re.sub(r'http\S+', '', text)  # Remove URLs
        text = re.sub(r'@\S+', '', text)     # Remove mentions
        text = re.sub(r'<.*?>', '', text)    # Remove media placeholders
        
        # Remove common stop words in Portuguese
        stop_words = {
            'que', 'de', 'a', 'o', 'e', 'do', 'da', 'em', 'um', 'para', 'é', 'com', 'não', 'uma', 'os', 'no',
            'se', 'na', 'por', 'mais', 'as', 'dos', 'como', 'mas', 'foi', 'ao', 'ele', 'das', 'tem', 'à', 'seu',
            'sua', 'ou', 'ser', 'quando', 'muito', 'há', 'nos', 'já', 'está', 'eu', 'também', 'só', 'pelo',
            'pela', 'até', 'isso', 'ela', 'entre', 'era', 'depois', 'sem', 'mesmo', 'aos', 'ter', 'seus', 'suas',
            'né', 'tá', 'pra', 'vc', 'você', 'aí', 'então', 'bem', 'assim', 'aqui', 'agora', 'hoje', 'ainda',
            'onde', 'depois', 'porque', 'sobre', 'antes', 'pode', 'vai', 'vou', 'fazer', 'ver', 'saber', 'dar'
        }
        
        # Create word cloud
        wordcloud = WordCloud(
            width=1200, height=600,
            background_color='white',
            stopwords=stop_words,
            max_words=100,
            colormap='viridis',
            relative_scaling=0.5,
            random_state=42
        ).generate(text)
        
        plt.figure(figsize=(15, 8))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title(title, fontsize=18, pad=20)
        plt.tight_layout(pad=0)
        
        if save_path:
            wordcloud_path = save_path.replace('.png', filename_suffix)
            plt.savefig(wordcloud_path, dpi=300, bbox_inches='tight', facecolor='white')
            print(f"☁️ Nuvem de palavras salva em: {wordcloud_path}")
        
        if show_plot:
            plt.show()
        else:
            plt.close()
    
    def create_emotion_analysis_chart(self, save_path: str = None, show_plot: bool = True):
        """Create emotional analysis visualization"""
        if not self.messages:
            print("❌ Sem mensagens para análise emocional!")
            return
            
        # Get psychological analysis data
        psych_analysis = self.analyzer.psychological_analysis()
        emotions_data = psych_analysis.get('emotional_tone_by_sender', {})
        
        if not emotions_data:
            print("❌ Dados emocionais não disponíveis!")
            return
        
        # Prepare data for plotting
        participants = list(emotions_data.keys())
        positive_counts = [emotions_data[p]['positive'] for p in participants]
        negative_counts = [emotions_data[p]['negative'] for p in participants]
        neutral_counts = [emotions_data[p]['neutral'] for p in participants]
        
        # Create stacked bar chart
        x = np.arange(len(participants))
        width = 0.6
        
        plt.figure(figsize=(12, 8))
        p1 = plt.bar(x, positive_counts, width, label='😊 Positivo', color='#2ecc71')
        p2 = plt.bar(x, neutral_counts, width, bottom=positive_counts, label='😐 Neutro', color='#95a5a6')
        p3 = plt.bar(x, negative_counts, width, 
                    bottom=np.array(positive_counts) + np.array(neutral_counts), 
                    label='😔 Negativo', color='#e74c3c')
        
        plt.xlabel('Participantes', fontsize=14)
        plt.ylabel('Número de Mensagens', fontsize=14)
        plt.title('😊😐😔 Análise Emocional por Participante', fontsize=16, pad=20)
        plt.xticks(x, participants)
        plt.legend()
        
        # Add value labels on bars
        for i, participant in enumerate(participants):
            total = positive_counts[i] + neutral_counts[i] + negative_counts[i]
            plt.text(i, total + 5, str(total), ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        
        if save_path:
            emotion_path = save_path.replace('.png', '_emotions.png')
            plt.savefig(emotion_path, dpi=300, bbox_inches='tight')
            print(f"😊 Análise emocional salva em: {emotion_path}")
        
        if show_plot:
            plt.show()
        else:
            plt.close()
    
    def create_response_time_analysis(self, save_path: str = None, show_plot: bool = True):
        """Create response time analysis visualization"""
        if not self.messages or len(self.messages) < 2:
            print("❌ Mensagens insuficientes para análise de tempo de resposta!")
            return
            
        # Calculate response times
        response_times = []
        response_participants = []
        
        for i in range(1, len(self.messages)):
            if self.messages[i].sender != self.messages[i-1].sender:
                time_diff = (self.messages[i].timestamp - self.messages[i-1].timestamp).total_seconds() / 60
                if time_diff < 1440:  # Less than 24 hours
                    response_times.append(time_diff)
                    response_participants.append(self.messages[i].sender)
        
        if not response_times:
            print("❌ Sem dados de tempo de resposta disponíveis!")
            return
        
        # Create histogram of response times
        plt.figure(figsize=(14, 10))
        
        # Overall histogram
        plt.subplot(2, 2, 1)
        plt.hist(response_times, bins=30, alpha=0.7, color='skyblue', edgecolor='black')
        plt.xlabel('Tempo de Resposta (minutos)')
        plt.ylabel('Frequência')
        plt.title('⏱️ Distribuição de Tempos de Resposta')
        plt.yscale('log')  # Log scale for better visualization
        
        # Box plot by participant
        plt.subplot(2, 2, 2)
        response_df = pd.DataFrame({
            'participant': response_participants,
            'response_time': response_times
        })
        
        sns.boxplot(data=response_df, x='participant', y='response_time')
        plt.xlabel('Participante')
        plt.ylabel('Tempo de Resposta (minutos)')
        plt.title('📦 Tempos de Resposta por Participante')
        plt.xticks(rotation=45)
        
        # Response time over time
        plt.subplot(2, 1, 2)
        response_dates = [self.messages[i].timestamp for i in range(1, len(self.messages)) 
                         if i < len(response_times) + 1]
        
        plt.scatter(response_dates[:len(response_times)], response_times, alpha=0.6, s=30)
        plt.xlabel('Data')
        plt.ylabel('Tempo de Resposta (minutos)')
        plt.title('📈 Evolução dos Tempos de Resposta ao Longo do Tempo')
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        
        if save_path:
            response_path = save_path.replace('.png', '_response_times.png')
            plt.savefig(response_path, dpi=300, bbox_inches='tight')
            print(f"⏱️ Análise de tempo de resposta salva em: {response_path}")
        
        if show_plot:
            plt.show()
        else:
            plt.close()
    
    def create_comprehensive_dashboard(self, save_path: str = None, show_individual: bool = False):
        """Create all visualizations in one comprehensive dashboard"""
        print("🎨 Criando dashboard completo de visualizações...")
        print("=" * 60)
        
        base_path = save_path or "whatsapp_analysis"
        
        # Create individual visualizations
        try:
            print("📈 1/7 - Criando timeline de mensagens...")
            self.create_message_timeline(f"{base_path}.png", show_plot=show_individual)
            
            print("🔥 2/7 - Criando mapa de calor de atividade...")
            self.create_activity_heatmap(f"{base_path}.png", show_plot=show_individual)
            
            print("📊 3/7 - Criando comparação entre participantes...")
            self.create_participant_comparison(f"{base_path}.png", show_plot=show_individual)
            
            print("☁️ 4/7 - Criando nuvem de palavras geral...")
            self.create_wordcloud(None, f"{base_path}.png", show_plot=show_individual)
            
            # Create word clouds for each participant
            for i, participant in enumerate(self.participants):
                print(f"☁️ {4+i+1}/7 - Criando nuvem de palavras para {participant}...")
                self.create_wordcloud(participant, f"{base_path}.png", show_plot=show_individual)
            
            print("😊 6/7 - Criando análise emocional...")
            self.create_emotion_analysis_chart(f"{base_path}.png", show_plot=show_individual)
            
            print("⏱️ 7/7 - Criando análise de tempo de resposta...")
            self.create_response_time_analysis(f"{base_path}.png", show_plot=show_individual)
            
            print("\n✅ Dashboard completo criado com sucesso!")
            print("🎯 Visualizações geradas:")
            print(f"   📈 Timeline: {base_path}_timeline.html")
            print(f"   🔥 Heatmap: {base_path}_heatmap.png")
            print(f"   📊 Comparação: {base_path}_comparison.png")
            print(f"   ☁️ Nuvem geral: {base_path}_wordcloud_all.png")
            for participant in self.participants:
                print(f"   ☁️ Nuvem {participant}: {base_path}_wordcloud_{participant.replace(' ', '_')}.png")
            print(f"   😊 Análise emocional: {base_path}_emotions.png")
            print(f"   ⏱️ Tempos de resposta: {base_path}_response_times.png")
            
        except Exception as e:
            print(f"❌ Erro ao criar visualizações: {e}")
            
        return True
    
    def get_visualization_summary(self):
        """Get a summary of available visualizations"""
        summary = {
            "visualizations_available": [
                "📈 Timeline de Mensagens (Interativo)",
                "🔥 Mapa de Calor de Atividade",
                "📊 Comparação entre Participantes", 
                "☁️ Nuvem de Palavras (Geral e Individual)",
                "😊 Análise Emocional por Participante",
                "⏱️ Análise de Tempos de Resposta"
            ],
            "total_messages": len(self.messages),
            "participants": list(self.participants),
            "date_range": {
                "start": min(msg.timestamp for msg in self.messages).strftime("%d/%m/%Y") if self.messages else "N/A",
                "end": max(msg.timestamp for msg in self.messages).strftime("%d/%m/%Y") if self.messages else "N/A"
            }
        }
        return summary