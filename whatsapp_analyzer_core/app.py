#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WhatsApp Chat Analyzer - Core Streamlit App
Simplified version with essential features only
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import base64
from datetime import datetime
from collections import Counter

# Import our core modules
from chat_analyzer import WhatsAppAnalyzer
from relationship_analyzer import RelationshipAnalyzer
from social_cards import SocialCardGenerator
from ai_analyzer import AIAnalyzer, AIConfig

# Page config
st.set_page_config(
    page_title="WhatsApp Chat Analyzer 💬",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .stAlert > div {
        padding: 1rem;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

def create_activity_heatmap(messages):
    """Create activity heatmap"""
    hours = [msg.timestamp.hour for msg in messages]
    days = [msg.timestamp.strftime('%A') for msg in messages]
    
    df = pd.DataFrame({'hour': hours, 'day': days})
    heatmap_data = df.groupby(['day', 'hour']).size().unstack(fill_value=0)
    
    # Reorder days
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_names = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
    heatmap_data = heatmap_data.reindex(day_order)
    heatmap_data.index = day_names
    
    fig = px.imshow(heatmap_data, 
                   title='🔥 Mapa de Calor - Atividade por Hora e Dia',
                   labels={'x': 'Hora', 'y': 'Dia da Semana', 'color': 'Mensagens'},
                   aspect='auto')
    fig.update_layout(height=400)
    return fig

def create_timeline_chart(messages):
    """Create timeline chart"""
    dates = [msg.timestamp.date() for msg in messages]
    df = pd.DataFrame({'date': dates})
    daily_counts = df.groupby('date').size().reset_index(name='messages')
    daily_counts['date'] = pd.to_datetime(daily_counts['date'])
    
    fig = px.line(daily_counts, x='date', y='messages', 
                 title='📈 Timeline de Mensagens',
                 labels={'date': 'Data', 'messages': 'Mensagens'})
    fig.update_layout(height=400)
    return fig

def create_participant_chart(stats):
    """Create participant comparison chart"""
    participant_stats = stats.get('participant_stats', {})
    if not participant_stats:
        return None
    
    participants = list(participant_stats.keys())
    messages = [participant_stats[p]['messages'] for p in participants]
    words = [participant_stats[p]['words'] for p in participants]
    
    fig = make_subplots(rows=1, cols=2, 
                       subplot_titles=['💬 Mensagens por Participante', '📝 Palavras por Participante'])
    
    fig.add_trace(go.Bar(x=participants, y=messages, name='Mensagens', marker_color='#667eea'), row=1, col=1)
    fig.add_trace(go.Bar(x=participants, y=words, name='Palavras', marker_color='#764ba2'), row=1, col=2)
    
    fig.update_layout(height=400, showlegend=False)
    return fig

def process_uploaded_file(uploaded_file):
    """Process uploaded WhatsApp chat file"""
    try:
        content = uploaded_file.read()
        
        # Try different encodings
        for encoding in ['utf-8', 'latin-1', 'cp1252']:
            try:
                chat_text = content.decode(encoding)
                return chat_text
            except UnicodeDecodeError:
                continue
        
        st.error("❌ Não foi possível decodificar o arquivo. Tente salvar como UTF-8.")
        return None
        
    except Exception as e:
        st.error(f"❌ Erro ao processar arquivo: {e}")
        return None

def main():
    """Main Streamlit app"""
    
    # Header
    st.markdown('<h1 class="main-header">WhatsApp Chat Analyzer 💬✨</h1>', unsafe_allow_html=True)
    st.markdown("### 🔍 Analise suas conversas com insights inteligentes!")
    
    # Sidebar
    st.sidebar.title("⚙️ Configurações")
    
    # API Key input
    api_key = st.sidebar.text_input(
        "🔑 OpenAI API Key (Premium)", 
        type="password",
        help="Para análises avançadas com IA. Deixe vazio para análise básica."
    )
    
    # File upload or example data
    st.sidebar.subheader("📁 Dados de Entrada")
    
    input_option = st.sidebar.radio(
        "Escolha uma opção:",
        ["📤 Upload de arquivo", "🎭 Dados de exemplo", "✍️ Colar texto"]
    )
    
    chat_text = None
    
    if input_option == "📤 Upload de arquivo":
        uploaded_file = st.sidebar.file_uploader(
            "Escolha o arquivo da conversa",
            type=['txt'],
            help="Exporte sua conversa do WhatsApp como arquivo .txt"
        )
        
        if uploaded_file:
            chat_text = process_uploaded_file(uploaded_file)
            
    elif input_option == "🎭 Dados de exemplo":
        chat_text = """25/10/2023 09:15 - João: Oi! Como você está?
25/10/2023 09:17 - Maria: Oi João! Estou bem, obrigada! E você? 😊
25/10/2023 09:18 - João: Também estou ótimo! O que você vai fazer hoje?
25/10/2023 09:20 - Maria: Vou trabalhar pela manhã, mas à tarde estou livre. Por que?
25/10/2023 09:22 - João: Pensei em convidar você para um café ☕
25/10/2023 09:23 - Maria: Adoraria! 😍 Que horas seria bom para você?
25/10/2023 09:25 - João: Que tal às 15h no café da esquina?
25/10/2023 09:26 - Maria: Perfeito! Nos vemos lá então ❤️
25/10/2023 09:27 - João: Combinado! Até mais tarde 👋
25/10/2023 09:28 - Maria: Até! 🥰"""
        st.sidebar.success("✅ Usando dados de exemplo")
        
    elif input_option == "✍️ Colar texto":
        chat_text = st.sidebar.text_area(
            "Cole o texto da conversa aqui:",
            height=200,
            help="Cole o texto exportado do WhatsApp"
        )
    
    # Process the data
    if chat_text:
        with st.spinner('🔄 Analisando conversa...'):
            # Initialize analyzer
            analyzer = WhatsAppAnalyzer()
            
            # Parse chat
            success = analyzer.parse_chat(chat_text)
            
            if not success or not analyzer.messages:
                st.error("❌ Nenhuma mensagem encontrada. Verifique o formato do texto.")
                st.info("📋 Formato esperado: DD/MM/YYYY HH:MM - Nome: Mensagem")
                return
            
            # Generate basic analysis
            stats = analyzer.get_basic_stats()
            activity = analyzer.get_activity_patterns()
            word_analysis = analyzer.get_word_analysis()
            
            # Initialize relationship analyzer
            relationship_analyzer = RelationshipAnalyzer(analyzer)
            
            # Initialize AI analyzer if API key provided
            ai_analyzer = None
            ai_insights = {}
            if api_key:
                ai_config = AIConfig(api_key=api_key)
                ai_analyzer = AIAnalyzer(ai_config)
                
                if ai_analyzer.is_ai_available():
                    messages_text = [msg.content for msg in analyzer.messages]
                    ai_insights = ai_analyzer.analyze_conversation_sentiment(messages_text)
            
            # Success message
            col1, col2 = st.columns([3, 1])
            with col1:
                st.success(f"✅ {stats['total_messages']} mensagens processadas de {stats['total_participants']} participantes!")
            with col2:
                success_rate = stats['parsing_stats']['success_rate']
                if success_rate > 80:
                    st.info(f"🟢 Parse: {success_rate:.1f}%")
                else:
                    st.warning(f"🟡 Parse: {success_rate:.1f}%")
            
            # Metrics row
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("💬 Mensagens", stats['total_messages'])
            with col2:
                st.metric("👥 Participantes", stats['total_participants'])
            with col3:
                st.metric("📝 Palavras", stats['total_words'])
            with col4:
                st.metric("📅 Período (dias)", stats['duration_days'])
            with col5:
                st.metric("💨 Msgs/dia", f"{stats['messages_per_day']:.1f}")
            
            # Main tabs
            tab1, tab2, tab3, tab4 = st.tabs(["📊 Visão Geral", "💕 Relacionamento", "🤖 IA Premium", "📱 Cards Sociais"])
            
            with tab1:
                st.header("📊 Análise Geral")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Timeline
                    timeline_fig = create_timeline_chart(analyzer.messages)
                    st.plotly_chart(timeline_fig, use_container_width=True)
                    
                    # Participant comparison
                    participant_fig = create_participant_chart(stats)
                    if participant_fig:
                        st.plotly_chart(participant_fig, use_container_width=True)
                
                with col2:
                    # Activity heatmap
                    heatmap_fig = create_activity_heatmap(analyzer.messages)
                    st.plotly_chart(heatmap_fig, use_container_width=True)
                    
                    # Word analysis
                    st.subheader("📝 Análise de Palavras")
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("Total de palavras", word_analysis['total_words'])
                        st.metric("Vocabulário único", word_analysis['unique_words'])
                    with col_b:
                        st.metric("Riqueza vocabular", f"{word_analysis['vocabulary_richness']:.2f}")
                        st.metric("Palavras relevantes", word_analysis['filtered_words'])
                    
                    # Top words
                    if word_analysis['top_words']:
                        st.write("**🔝 Palavras mais usadas:**")
                        for word, count in word_analysis['top_words'][:10]:
                            st.write(f"• {word}: {count}")
            
            with tab2:
                st.header("💕 Análise de Relacionamento")
                
                # Relationship score for 2-person chats
                if len(analyzer.participants) == 2:
                    st.subheader("🎯 Score de Compatibilidade")
                    
                    score_data = relationship_analyzer.calculate_relationship_score()
                    
                    if "error" not in score_data:
                        # Display score
                        col1, col2, col3 = st.columns([1, 2, 1])
                        
                        with col2:
                            score = score_data['total_score']
                            grade = score_data['grade']
                            percentile = score_data['percentile']
                            description = score_data['description']
                            
                            st.markdown(f"""
                            <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 20px; color: white;">
                                <h1 style="font-size: 3em; margin: 0;">{score:.0f}/100</h1>
                                <h2 style="margin: 10px 0;">Nota: {grade}</h2>
                                <p style="font-size: 1.2em;">Melhor que {percentile}% dos casais!</p>
                                <p style="font-style: italic;">{description}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Detailed scores
                        st.subheader("📊 Pontuação Detalhada")
                        detailed = score_data['detailed_scores']
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("⚖️ Equilíbrio", f"{detailed.get('balance', 0):.1f}/20")
                            st.metric("📈 Consistência", f"{detailed.get('consistency', 0):.1f}/20")
                        with col2:
                            st.metric("💬 Engajamento", f"{detailed.get('engagement', 0):.1f}/30")
                            st.metric("🎯 Variedade", f"{detailed.get('variety', 0):.1f}/10")
                        with col3:
                            st.metric("⚡ Frequência", f"{detailed.get('frequency', 0):.1f}/20")
                        
                        # Tips
                        if score_data.get('improvement_tips'):
                            st.subheader("💡 Dicas de Melhoria")
                            for tip in score_data['improvement_tips']:
                                st.info(tip)
                    else:
                        st.error(score_data['error'])
                
                # Chat personality
                st.subheader("🎭 Personalidade do Chat")
                
                personality_data = relationship_analyzer.get_chat_personality()
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown(f"""
                    <div style="text-align: center; padding: 15px; background: linear-gradient(45deg, #FF6B6B, #4ECDC4); border-radius: 15px; color: white; margin: 10px 0;">
                        <h2 style="margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);">{personality_data['archetype']}</h2>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.write("**Características:**")
                    for trait in personality_data['traits']:
                        st.success(f"✨ {trait}")
                    
                    st.info(f"📝 **Descrição:** {personality_data['description']}")
                
                with col2:
                    # Fun facts
                    st.subheader("🎉 Curiosidades")
                    fun_facts = relationship_analyzer.generate_fun_facts()
                    for fact in fun_facts[:5]:
                        st.write(f"• {fact}")
            
            with tab3:
                st.header("🤖 Análise Premium com IA")
                
                if not api_key:
                    st.warning("🔑 Configure uma chave da OpenAI para análises avançadas!")
                    st.info("💡 A análise com IA oferece insights psicológicos e de relacionamento mais profundos.")
                    
                    # Show what premium offers
                    st.subheader("✨ O que você ganha com Premium:")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**🧠 Análise de Sentimentos:**")
                        st.write("• Detecta emoções na conversa")
                        st.write("• Identifica dinâmica do relacionamento")
                        st.write("• Analisa estilo de comunicação")
                    
                    with col2:
                        st.write("**💡 Insights Personalizados:**")
                        st.write("• Sugestões de melhoria")
                        st.write("• Análise comportamental")
                        st.write("• Recomendações específicas")
                    
                    st.markdown("""
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 15px; color: white; text-align: center; margin: 20px 0;">
                        <h3>🚀 Desbloqueie o Poder da IA!</h3>
                        <p>Obtenha uma chave da OpenAI e descubra insights únicos sobre suas conversas.</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                elif ai_analyzer and ai_analyzer.is_ai_available():
                    if ai_insights.get('success'):
                        analysis = ai_insights['ai_analysis']
                        
                        st.subheader("🎯 Análise de Sentimentos")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if 'sentimento' in analysis:
                                sentiment = analysis['sentimento']
                                sentiment_emoji = {"positivo": "😊", "negativo": "😔", "neutro": "😐"}.get(sentiment.lower(), "🤔")
                                st.metric("Sentimento Geral", f"{sentiment_emoji} {sentiment.title()}")
                            
                            if 'dinamica' in analysis:
                                st.metric("Dinâmica", analysis['dinamica'])
                        
                        with col2:
                            if 'estilo' in analysis:
                                st.metric("Estilo", analysis['estilo'])
                            
                            if 'intimidade' in analysis:
                                st.metric("Intimidade", analysis['intimidade'])
                        
                        if 'observacao' in analysis:
                            st.subheader("🔍 Observação da IA")
                            st.success(analysis['observacao'])
                        
                        # Additional insights for relationships
                        if len(analyzer.participants) == 2:
                            relationship_insights = ai_analyzer.generate_relationship_insights(
                                stats, list(analyzer.participants)
                            )
                            
                            if relationship_insights.get('success'):
                                insights = relationship_insights['relationship_insights']
                                
                                st.subheader("💝 Insights do Relacionamento")
                                
                                if 'frequencia' in insights:
                                    st.info(f"⏰ **Frequência:** {insights['frequencia']}")
                                
                                if 'estilo' in insights:
                                    st.info(f"💬 **Estilo:** {insights['estilo']}")
                                
                                if 'sugestao' in insights:
                                    st.success(f"💡 **Sugestão:** {insights['sugestao']}")
                    
                    else:
                        st.error(f"❌ Erro na análise de IA: {ai_insights.get('error', 'Erro desconhecido')}")
                
                else:
                    st.error("❌ Não foi possível conectar com a IA. Verifique sua chave da API.")
            
            with tab4:
                st.header("📱 Cards para Redes Sociais")
                st.write("Crie imagens prontas para compartilhar no Instagram, Facebook, Twitter!")
                
                card_generator = SocialCardGenerator()
                
                # Generate different types of cards
                col1, col2 = st.columns(2)
                
                with col1:
                    # Stats card
                    st.subheader("📊 Card de Estatísticas")
                    if st.button("🎨 Gerar Card de Stats", key="stats_card"):
                        with st.spinner("Criando card..."):
                            stats_card = card_generator.create_stats_card(stats)
                            if stats_card:
                                st.image(stats_card, caption="Card de Estatísticas")
                                
                                # Download button
                                st.download_button(
                                    label="📥 Baixar Card de Stats",
                                    data=base64.b64decode(stats_card.split(',')[1]),
                                    file_name=f"whatsapp_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                                    mime="image/png"
                                )
                            else:
                                st.error("Erro ao gerar card de estatísticas")
                    
                    # Personality card
                    st.subheader("🎭 Card de Personalidade")
                    if st.button("🎨 Gerar Card de Personalidade", key="personality_card"):
                        with st.spinner("Criando card..."):
                            personality_data = relationship_analyzer.get_chat_personality()
                            personality_card = card_generator.create_personality_card(personality_data)
                            if personality_card:
                                st.image(personality_card, caption="Card de Personalidade")
                                
                                st.download_button(
                                    label="📥 Baixar Card de Personalidade",
                                    data=base64.b64decode(personality_card.split(',')[1]),
                                    file_name=f"whatsapp_personality_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                                    mime="image/png"
                                )
                            else:
                                st.error("Erro ao gerar card de personalidade")
                
                with col2:
                    # Relationship score card (only for 2-person chats)
                    if len(analyzer.participants) == 2:
                        st.subheader("💕 Card de Relacionamento")
                        if st.button("🎨 Gerar Card de Score", key="relationship_card"):
                            with st.spinner("Criando card..."):
                                score_data = relationship_analyzer.calculate_relationship_score()
                                if "error" not in score_data:
                                    relationship_card = card_generator.create_relationship_score_card(score_data)
                                    if relationship_card:
                                        st.image(relationship_card, caption="Card de Relacionamento")
                                        
                                        st.download_button(
                                            label="📥 Baixar Card de Relacionamento",
                                            data=base64.b64decode(relationship_card.split(',')[1]),
                                            file_name=f"whatsapp_relationship_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                                            mime="image/png"
                                        )
                                    else:
                                        st.error("Erro ao gerar card de relacionamento")
                                else:
                                    st.error("Não foi possível calcular o score de relacionamento")
                    
                    # Fun facts card
                    st.subheader("🎉 Card de Curiosidades")
                    if st.button("🎨 Gerar Card de Fun Facts", key="facts_card"):
                        with st.spinner("Criando card..."):
                            fun_facts = relationship_analyzer.generate_fun_facts()
                            facts_card = card_generator.create_fun_facts_card(fun_facts)
                            if facts_card:
                                st.image(facts_card, caption="Card de Curiosidades")
                                
                                st.download_button(
                                    label="📥 Baixar Card de Fun Facts",
                                    data=base64.b64decode(facts_card.split(',')[1]),
                                    file_name=f"whatsapp_facts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                                    mime="image/png"
                                )
                            else:
                                st.error("Erro ao gerar card de curiosidades")
                
                st.info("💡 **Dica:** Os cards são otimizados para Instagram (1080x1080) e funcionam bem em todas as redes sociais!")
    
    else:
        # Welcome screen
        st.markdown("""
        ## 👋 Bem-vindo ao WhatsApp Chat Analyzer!
        
        ### 🚀 Como usar:
        1. **📤 Faça upload** do arquivo .txt da sua conversa do WhatsApp
        2. **🔑 Opcionalmente**, adicione sua chave da OpenAI para análises com IA
        3. **🔍 Explore** os insights e crie cards para redes sociais
        
        ### 📱 Como exportar do WhatsApp:
        1. Abra a conversa no WhatsApp
        2. Toque nos 3 pontos (⋮) → **Mais** → **Exportar conversa**
        3. Escolha **"Sem mídia"**
        4. Salve como arquivo .txt
        
        ### 🎯 O que você vai descobrir:
        - 📊 **Estatísticas completas** da conversa
        - 💕 **Score de relacionamento** (para conversas de 2 pessoas)
        - 🎭 **Personalidade do chat** com arquétipos únicos
        - 🤖 **Análise com IA** (com OpenAI API)
        - 📱 **Cards para redes sociais** prontos para compartilhar
        """)
        
        # Show sample format
        st.subheader("📋 Formato de Entrada Esperado:")
        st.code("""
25/10/2023 09:15 - João: Oi! Como você está?
25/10/2023 09:17 - Maria: Oi João! Estou bem, obrigada!
25/10/2023 09:18 - João: Também estou ótimo!
        """)

if __name__ == "__main__":
    main()