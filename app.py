import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
import re
import json
import io
import base64
from collections import Counter
import logging

# Configure logging for Streamlit app
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('streamlit_app_debug.log'),
        logging.StreamHandler()
    ]
)
app_logger = logging.getLogger(__name__)

# Import our custom modules
from whatsapp_analyzer import WhatsAppChatAnalyzer, WhatsAppMessage
from ai_analyzer import EnhancedWhatsAppAnalyzer, AIAnalysisConfig
from multi_ai_analyzer import MultiAIWhatsAppAnalyzer, BaseAIProvider
from viral_metrics import ViralMetrics
from shareable_cards import ShareableCardGenerator
from word_blacklist import WordBlacklist

# Page config
st.set_page_config(
    page_title="WhatsApp Chat Analyzer 💬",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
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
    .insight-box {
        background: #f8f9fa;
        border-left: 4px solid #007bff;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 10px 10px 0;
    }
    .stAlert > div {
        padding: 1rem;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

def create_plotly_wordcloud(text, title):
    """Create a word cloud using plotly (Streamlit friendly)"""
    # Clean text
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'@\S+', '', text)
    text = re.sub(r'<.*?>', '', text)
    
    # Portuguese stop words
    stop_words = {
        'que', 'de', 'a', 'o', 'e', 'do', 'da', 'em', 'um', 'para', 'é', 'com', 'não', 'uma', 'os', 'no',
        'se', 'na', 'por', 'mais', 'as', 'dos', 'como', 'mas', 'foi', 'ao', 'ele', 'das', 'tem', 'à', 'seu',
        'sua', 'ou', 'ser', 'quando', 'muito', 'há', 'nos', 'já', 'está', 'eu', 'também', 'só', 'pelo',
        'pela', 'até', 'isso', 'ela', 'entre', 'era', 'depois', 'sem', 'mesmo', 'aos', 'ter', 'seus', 'suas',
        'né', 'tá', 'pra', 'vc', 'você', 'aí', 'então', 'bem', 'assim', 'aqui', 'agora', 'hoje', 'ainda'
    }
    
    # Get word frequencies
    words = [word.lower() for word in text.split() if len(word) > 2 and word.lower() not in stop_words]
    word_freq = Counter(words)
    
    if not word_freq:
        return None
    
    # Create word cloud with matplotlib (then convert to image for Streamlit)
    try:
        wordcloud = WordCloud(
            width=800, height=400,
            background_color='white',
            max_words=50,
            colormap='viridis'
        ).generate_from_frequencies(word_freq)
        
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        ax.set_title(title, fontsize=16, pad=20)
        
        return fig
    except:
        return None

def process_uploaded_file(uploaded_file):
    """Process uploaded WhatsApp chat file"""
    try:
        # Read file content
        content = uploaded_file.read()
        
        # Try different encodings
        for encoding in ['utf-8', 'latin-1', 'cp1252']:
            try:
                chat_text = content.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        else:
            st.error("❌ Não foi possível decodificar o arquivo. Tente salvar como UTF-8.")
            return None
        
        return chat_text
    except Exception as e:
        st.error(f"❌ Erro ao processar arquivo: {e}")
        return None

def create_timeline_chart(messages):
    """Create timeline chart using Plotly"""
    dates = [msg.timestamp.date() for msg in messages]
    df = pd.DataFrame({'date': dates})
    daily_counts = df.groupby('date').size().reset_index(name='messages')
    daily_counts['date'] = pd.to_datetime(daily_counts['date'])
    
    fig = px.line(daily_counts, x='date', y='messages', 
                 title='📈 Timeline de Mensagens',
                 labels={'date': 'Data', 'messages': 'Mensagens'})
    fig.update_layout(height=400)
    return fig

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

def create_participant_charts(analyzer):
    """Create participant comparison charts"""
    participants = list(analyzer.participants)
    
    # Prepare data
    participant_data = {}
    for participant in participants:
        p_messages = [msg for msg in analyzer.messages if msg.sender == participant]
        participant_data[participant] = {
            'messages': len(p_messages),
            'words': sum(msg.word_count for msg in p_messages),
            'avg_words': sum(msg.word_count for msg in p_messages) / len(p_messages) if p_messages else 0,
        }
    
    # Create comparison chart
    df = pd.DataFrame(participant_data).T
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'Participante'}, inplace=True)
    
    fig = make_subplots(rows=1, cols=2, 
                       subplot_titles=['💬 Total de Mensagens', '📝 Média de Palavras'])
    
    fig.add_trace(go.Bar(x=df['Participante'], y=df['messages'], name='Mensagens'), row=1, col=1)
    fig.add_trace(go.Bar(x=df['Participante'], y=df['avg_words'], name='Palavras'), row=1, col=2)
    
    fig.update_layout(height=400, showlegend=False)
    return fig

def create_emotion_chart(emotions_data):
    """Create emotional analysis chart"""
    if not emotions_data:
        return None
    
    participants = list(emotions_data.keys())
    positive = [emotions_data[p]['positive'] for p in participants]
    negative = [emotions_data[p]['negative'] for p in participants]
    neutral = [emotions_data[p]['neutral'] for p in participants]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(name='😊 Positivo', x=participants, y=positive))
    fig.add_trace(go.Bar(name='😔 Negativo', x=participants, y=negative))
    fig.add_trace(go.Bar(name='😐 Neutro', x=participants, y=neutral))
    
    fig.update_layout(
        title='😊😐😔 Análise Emocional por Participante',
        barmode='stack',
        height=400
    )
    return fig

def main():
    """Main Streamlit app"""
    
    # Header
    st.markdown('<h1 class="main-header">WhatsApp Chat Analyzer 💬✨</h1>', unsafe_allow_html=True)
    st.markdown("### 🔍 Analise suas conversas como um expert: linguista + psicólogo + coach de relacionamentos!")
    
    # Sidebar
    st.sidebar.title("⚙️ Configurações")
    
    # AI Model Selection
    st.sidebar.subheader("🤖 Modelos de IA")
    
    # Model selection
    available_models = ["OpenAI", "Gemini", "Claude", "Grok"]
    selected_models = st.sidebar.multiselect(
        "Escolha os modelos de IA:",
        available_models,
        default=["OpenAI"],
        help="Selecione um ou mais modelos para análise comparativa"
    )
    
    # API Keys for different providers
    api_keys = {}
    
    if "OpenAI" in selected_models:
        api_keys['openai'] = st.sidebar.text_input("🔑 Chave OpenAI", type="password", 
                                                   help="Para análises com OpenAI/ChatGPT")
    
    if "Gemini" in selected_models:
        api_keys['gemini'] = st.sidebar.text_input("🔑 Chave Google Gemini", type="password",
                                                   help="Para análises com Google Gemini")
    
    if "Claude" in selected_models:
        api_keys['anthropic'] = st.sidebar.text_input("🔑 Chave Anthropic Claude", type="password",
                                                      help="Para análises com Claude")
    
    if "Grok" in selected_models:
        api_keys['grok'] = st.sidebar.text_input("🔑 Chave X.AI Grok", type="password",
                                                 help="Para análises com Grok")
    
    # Legacy OpenAI support
    api_key = api_keys.get('openai')
    
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
25/10/2023 09:28 - Maria: Até! 🥰
25/10/2023 15:45 - João: Já estou chegando no café!
25/10/2023 15:46 - Maria: Eu também! Te vejo em 2 minutos
25/10/2023 18:30 - Maria: Muito obrigada pelo café! Foi muito legal conversar
25/10/2023 18:32 - João: Eu que agradeço! Foi ótimo te conhecer melhor
25/10/2023 18:33 - Maria: Com certeza! Vamos repetir em breve?
25/10/2023 18:35 - João: Claro! Que tal no fim de semana?
25/10/2023 18:36 - Maria: Adorei a ideia! Me manda uma mensagem na sexta?
25/10/2023 18:37 - João: Pode deixar! Tenha uma ótima noite
25/10/2023 18:38 - Maria: Você também! Até sexta 🌟"""
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
            # Initialize analyzers
            base_analyzer = WhatsAppChatAnalyzer()
            ai_config = AIAnalysisConfig(api_key=api_key if api_key else None)
            enhanced_analyzer = EnhancedWhatsAppAnalyzer(base_analyzer, ai_config)
            
            # Initialize multi-AI analyzer if models are selected
            multi_ai_analyzer = None
            if selected_models and any(api_keys.values()):
                app_logger.info(f"🔧 Initializing multi-AI analyzer with models: {selected_models}")
                try:
                    multi_ai_analyzer = MultiAIWhatsAppAnalyzer()
                    
                    # Configure providers
                    from multi_ai_analyzer import AIModelConfig
                    for model in selected_models:
                        if model == "OpenAI" and api_keys.get('openai'):
                            app_logger.info(f"⚙️ Configuring OpenAI provider")
                            config = AIModelConfig(model_type="openai", api_key=api_keys['openai'])
                            success = multi_ai_analyzer.add_model("openai", config)
                            app_logger.info(f"OpenAI configuration result: {success}")
                            
                        elif model == "Gemini" and api_keys.get('gemini'):
                            app_logger.info(f"⚙️ Configuring Gemini provider")
                            config = AIModelConfig(model_type="gemini", api_key=api_keys['gemini'])
                            success = multi_ai_analyzer.add_model("gemini", config)
                            app_logger.info(f"Gemini configuration result: {success}")
                            
                        elif model == "Claude" and api_keys.get('anthropic'):
                            app_logger.info(f"⚙️ Configuring Claude provider")
                            config = AIModelConfig(model_type="claude", api_key=api_keys['anthropic'])
                            success = multi_ai_analyzer.add_model("claude", config)
                            app_logger.info(f"Claude configuration result: {success}")
                            
                        elif model == "Grok" and api_keys.get('grok'):
                            app_logger.info(f"⚙️ Configuring Grok provider")
                            config = AIModelConfig(model_type="grok", api_key=api_keys['grok'])
                            success = multi_ai_analyzer.add_model("grok", config)
                            app_logger.info(f"Grok configuration result: {success}")
                    
                    app_logger.info(f"✅ Multi-AI analyzer initialized successfully")
                    
                except Exception as e:
                    app_logger.error(f"❌ Error initializing multi-AI analyzer: {e}")
                    st.error(f"Erro ao inicializar análise multi-IA: {e}")
            else:
                app_logger.info("ℹ️ No models selected or no API keys provided")
            
            # Parse chat
            base_analyzer.parse_chat(chat_text)
            
            if not base_analyzer.messages:
                st.error("❌ Nenhuma mensagem encontrada. Verifique o formato do texto.")
                st.info("📋 Formato esperado: DD/MM/YYYY HH:MM - Nome: Mensagem")
                return
            
            # Generate analysis
            report = enhanced_analyzer.generate_enhanced_report()
            
            # Main dashboard
            parsing_info = report['linguistic_analysis']
            detected_format = parsing_info.get('detected_format', 'Unknown')
            format_quality = parsing_info.get('format_quality', 'Unknown')
            success_rate = parsing_info.get('success_rate', 0)
            
            # Success message with format detection
            col1, col2 = st.columns([3, 1])
            with col1:
                st.success(f"✅ {len(base_analyzer.messages)} mensagens processadas de {len(base_analyzer.participants)} participantes!")
            with col2:
                color = "🟢" if format_quality == "Excellent" else "🟡" if format_quality == "Good" else "🟠" if format_quality == "Fair" else "🔴"
                st.info(f"{color} Formato: {detected_format}")
            
            # Metrics row
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("💬 Total de Mensagens", len(base_analyzer.messages))
            
            with col2:
                st.metric("👥 Participantes", len(base_analyzer.participants))
            
            with col3:
                avg_words = report['linguistic_analysis']['average_words_per_message']
                st.metric("📝 Média Palavras/Msg", f"{avg_words:.1f}")
            
            with col4:
                span_days = report['linguistic_analysis']['conversation_span_days']
                st.metric("📅 Período (dias)", span_days)
                
            with col5:
                st.metric("🎯 Taxa de Sucesso", f"{success_rate:.1f}%")
            
            # Tabs for different analyses
            tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
                "📊 Visão Geral", "🎯 Score & Viral", "📈 Atividade", "💭 Análise Textual", 
                "🧠 Análise com IA", "🔍 Detalhes do Parse", "📋 Relatório Completo"
            ])
            
            with tab1:
                st.header("📊 Análise Geral")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Timeline chart
                    timeline_fig = create_timeline_chart(base_analyzer.messages)
                    st.plotly_chart(timeline_fig, use_container_width=True)
                    
                    # Participant comparison
                    participant_fig = create_participant_charts(base_analyzer)
                    st.plotly_chart(participant_fig, use_container_width=True)
                
                with col2:
                    # Activity heatmap
                    heatmap_fig = create_activity_heatmap(base_analyzer.messages)
                    st.plotly_chart(heatmap_fig, use_container_width=True)
                    
                    # Emotional analysis
                    emotions_data = report['psychological_analysis'].get('emotional_tone_by_sender', {})
                    if emotions_data:
                        emotion_fig = create_emotion_chart(emotions_data)
                        st.plotly_chart(emotion_fig, use_container_width=True)
            
            with tab2:
                st.header("🎯 Score de Relacionamento & Conteúdo Viral")
                
                # Initialize viral metrics
                viral_metrics = ViralMetrics(base_analyzer)
                card_generator = ShareableCardGenerator()
                
                # Relationship Score (only for 2-person chats)
                if len(base_analyzer.participants) == 2:
                    st.subheader("💕 Compatibilidade do Relacionamento")
                    
                    with st.spinner("Calculando seu score de relacionamento..."):
                        relationship_data = viral_metrics.generate_relationship_score()
                    
                    if "error" not in relationship_data:
                        # Main score display
                        col1, col2, col3 = st.columns([1, 2, 1])
                        
                        with col2:
                            score = relationship_data['total_score']
                            grade = relationship_data['grade']
                            percentile = relationship_data['percentile']
                            
                            # Big score display
                            st.markdown(f"""
                            <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 20px; color: white;">
                                <h1 style="font-size: 3em; margin: 0;">{score}/100</h1>
                                <h2 style="margin: 10px 0;">Nota: {grade}</h2>
                                <p style="font-size: 1.2em;">Melhor que {percentile}% dos casais!</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Personality type
                        personality = relationship_data['personality']
                        st.success(f"🎭 **Tipo de Relacionamento:** {personality['type']}")
                        st.info(f"💭 {personality['description']}")
                        
                        # Detailed scores
                        st.subheader("📊 Pontuação Detalhada")
                        detailed = relationship_data['detailed_scores']
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("⚖️ Equilíbrio", f"{detailed.get('balance', 0):.1f}/20")
                            st.metric("⚡ Velocidade", f"{detailed.get('speed', 0):.1f}/15")
                        with col2:
                            st.metric("💝 Sincronia Emocional", f"{detailed.get('emotion', 0):.1f}/25")
                            st.metric("🎭 Variedade", f"{detailed.get('variety', 0):.1f}/20")
                        with col3:
                            st.metric("📈 Consistência", f"{detailed.get('consistency', 0):.1f}/20")
                        
                        # Improvements
                        if relationship_data.get('improvements'):
                            st.subheader("💡 Dicas de Melhoria")
                            for improvement in relationship_data['improvements']:
                                st.write(f"• {improvement}")
                        
                        # Fun facts
                        if relationship_data.get('fun_facts'):
                            st.subheader("🎉 Fatos Divertidos")
                            for fact in relationship_data['fun_facts']:
                                st.write(f"🎯 {fact}")
                
                # Chat Personality (for all chats)
                st.subheader("🎭 Personalidade do Chat")
                
                with st.spinner("Analisando personalidade do chat..."):
                    personality_data = viral_metrics.generate_chat_personality()
                
                # Display archetype with visual flair
                archetype = personality_data['archetype']
                st.markdown(f"""
                <div style="text-align: center; padding: 15px; background: linear-gradient(45deg, #FF6B6B, #4ECDC4); border-radius: 15px; color: white; margin: 10px 0;">
                    <h2 style="margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);">{archetype}</h2>
                </div>
                """, unsafe_allow_html=True)
                
                # Traits
                st.write("**Suas características:**")
                trait_cols = st.columns(2)
                for i, trait in enumerate(personality_data['traits']):
                    with trait_cols[i % 2]:
                        st.success(trait)
                
                # Fun description
                st.info(f"📝 **Descrição:** {personality_data['fun_description']}")
                
                # Conversation Highlights
                st.subheader("🌟 Destaques da Conversa")
                
                highlights = viral_metrics.generate_conversation_highlights()
                
                if 'timeline' in highlights:
                    timeline = highlights['timeline']
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("📅 Primeiro chat", timeline['first_message_date'])
                        st.metric("⏱️ Duração", f"{timeline['duration_days']} dias")
                    
                    with col2:
                        st.metric("💬 Msgs/dia", f"{timeline['messages_per_day']:.1f}")
                        st.metric("📊 Total de meses", f"{timeline['duration_months']:.1f}")
                    
                    with col3:
                        peak = highlights.get('peak_activity', {})
                        if peak:
                            st.metric("🕐 Hora pico", peak['peak_hour'])
                            st.metric("📅 Dia pico", peak['peak_day'])
                
                # Social Media Cards
                st.subheader("📱 Cards para Redes Sociais")
                st.write("Imagens prontas para compartilhar no Instagram, Twitter, TikTok!")
                
                # Generate cards
                try:
                    cards_data = {
                        'messages': base_analyzer.messages,
                        'conversation_span_days': report['linguistic_analysis'].get('conversation_span_days', 0),
                        'messages_per_day': len(base_analyzer.messages) / max(1, report['linguistic_analysis'].get('conversation_span_days', 1))
                    }
                    
                    cards = card_generator.generate_all_cards(cards_data)
                    
                    if cards:
                        card_cols = st.columns(2)
                        card_names = list(cards.keys())
                        
                        for i, (card_name, card_data) in enumerate(cards.items()):
                            with card_cols[i % 2]:
                                st.image(card_data, caption=f"Card: {card_name.title()}")
                                
                                # Download button for each card
                                st.download_button(
                                    label=f"📥 Baixar {card_name.title()}",
                                    data=base64.b64decode(card_data.split(',')[1]),
                                    file_name=f"chat_card_{card_name}.png",
                                    mime="image/png"
                                )
                    
                except Exception as e:
                    st.error(f"Erro ao gerar cards: {e}")
                
                # Premium Features Preview
                st.subheader("✨ Funcionalidades Premium")
                
                premium_preview = viral_metrics.generate_premium_preview()
                
                # Create attractive premium section
                st.markdown("""
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 15px; color: white; text-align: center;">
                    <h3>🚀 Desbloqueie Insights Ainda Mais Profundos!</h3>
                    <p>Descubra o que suas mensagens realmente revelam sobre seu relacionamento com análise de IA!</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Preview features
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**🧠 Análises com IA:**")
                    for feature in premium_preview['premium_features']['ai_insights']['preview'][:3]:
                        st.write(f"• {feature}")
                
                with col2:
                    st.write("**📊 Métricas Avançadas:**")
                    for feature in premium_preview['premium_features']['advanced_metrics']['features'][:3]:
                        st.write(f"• {feature}")
                
                # Call to action
                st.warning("💎 **Upgrade para Premium** por apenas $4.99/mês e desbloqueie análises de IA avançadas, gráficos personalizados e insights preditivos!")
                
                # Mock upgrade button
                if st.button("🔓 Fazer Upgrade Agora", type="primary"):
                    st.balloons()
                    st.success("🎉 Funcionalidade de upgrade será implementada em breve! Por enquanto, aproveite a análise gratuita!")

            with tab3:
                st.header("📈 Análise de Atividade")
                
                # Peak hours
                peak_hours = report['linguistic_analysis']['peak_activity_hours']
                st.subheader("⏰ Horários Mais Ativos")
                
                for hour, count in peak_hours:
                    st.write(f"🕐 **{hour}:00h** - {count} mensagens")
                
                # Response time analysis
                if 'average_response_time_minutes' in report['psychological_analysis']:
                    avg_response = report['psychological_analysis']['average_response_time_minutes']
                    median_response = report['psychological_analysis']['median_response_time_minutes']
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("⏱️ Tempo Médio de Resposta", f"{avg_response:.1f} min")
                    with col2:
                        st.metric("📊 Tempo Mediano de Resposta", f"{median_response:.1f} min")
            
            with tab3:
                st.header("💭 Análise Textual e Nuvens de Palavras")
                
                # Overall word cloud
                all_text = ' '.join([msg.content for msg in base_analyzer.messages])
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("☁️ Nuvem de Palavras - Geral")
                    wordcloud_fig = create_plotly_wordcloud(all_text, "Palavras Mais Usadas")
                    if wordcloud_fig:
                        st.pyplot(wordcloud_fig)
                
                with col2:
                    # Word clouds by participant
                    if len(base_analyzer.participants) > 1:
                        selected_participant = st.selectbox(
                            "Escolha um participante:", 
                            list(base_analyzer.participants)
                        )
                        
                        participant_messages = [
                            msg.content for msg in base_analyzer.messages 
                            if msg.sender == selected_participant
                        ]
                        participant_text = ' '.join(participant_messages)
                        
                        st.subheader(f"☁️ Nuvem - {selected_participant}")
                        participant_wordcloud = create_plotly_wordcloud(
                            participant_text, 
                            f"Palavras de {selected_participant}"
                        )
                        if participant_wordcloud:
                            st.pyplot(participant_wordcloud)
            
            with tab4:
                st.header("💭 Análise Textual e Nuvens de Palavras")
                
                # Initialize word blacklist
                blacklist = WordBlacklist()
                
                # Blacklist customization
                with st.expander("🎛️ Personalizar Filtros de Palavras"):
                    st.write("**Filtros Ativos:**")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        # Show blacklist info
                        blacklist_info = blacklist.get_blacklist_info()
                        st.metric("Total de palavras filtradas", blacklist_info['total_blacklisted'])
                        
                        st.write("**Categorias filtradas:**")
                        for category, count in blacklist_info['categories'].items():
                            st.write(f"• {category}: {count} palavras")
                    
                    with col2:
                        # Custom blacklist
                        st.write("**Adicionar palavras personalizadas:**")
                        custom_words = st.text_area("Digite palavras separadas por vírgula:", 
                                                   placeholder="exemplo: teste, palavra, filtrar")
                        
                        if st.button("Adicionar à lista"):
                            if custom_words:
                                words_to_add = [w.strip() for w in custom_words.split(',') if w.strip()]
                                blacklist.add_custom_words(words_to_add)
                                st.success(f"Adicionadas {len(words_to_add)} palavras ao filtro!")
                
                # Overall word cloud with blacklist
                all_text = ' '.join([msg.content for msg in base_analyzer.messages])
                
                # Analyze text with blacklist
                text_analysis = blacklist.analyze_text(all_text)
                
                # Show filtering stats
                st.subheader("📊 Estatísticas de Filtragem")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Palavras originais", text_analysis['original_words'])
                with col2:
                    st.metric("Palavras filtradas", text_analysis['filtered_words'])
                with col3:
                    st.metric("Palavras removidas", text_analysis['removed_words'])
                with col4:
                    st.metric("% removido", f"{text_analysis['removal_percentage']:.1f}%")
                
                # Word clouds
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("☁️ Nuvem - Original")
                    # Create word cloud without filtering
                    words_original = all_text.split()
                    if words_original:
                        original_text_clean = ' '.join([blacklist._clean_word(w) for w in words_original if blacklist._clean_word(w)])
                        wordcloud_fig = create_plotly_wordcloud(original_text_clean, "Palavras Mais Usadas (Original)")
                        if wordcloud_fig:
                            st.pyplot(wordcloud_fig)
                    
                    # Top original words
                    st.write("**Top 10 palavras originais:**")
                    for word, count in text_analysis['top_original'][:10]:
                        st.write(f"• {word}: {count}")

                with col2:
                    st.subheader("☁️ Nuvem - Filtrada")
                    # Create word cloud with filtering
                    words_filtered = all_text.split()
                    filtered_words = blacklist.remove_blacklisted_words(words_filtered)
                    if filtered_words:
                        filtered_text = ' '.join(filtered_words)
                        filtered_wordcloud = create_plotly_wordcloud(filtered_text, "Palavras Relevantes (Filtrada)")
                        if filtered_wordcloud:
                            st.pyplot(filtered_wordcloud)
                    
                    # Top filtered words
                    st.write("**Top 10 palavras filtradas:**")
                    for word, count in text_analysis['top_filtered'][:10]:
                        st.write(f"• {word}: {count}")
                
                # Participant-specific word clouds
                if len(base_analyzer.participants) <= 5:  # Limit to avoid too many columns
                    st.subheader("☁️ Nuvens por Participante (Filtradas)")
                    
                    participant_cols = st.columns(min(len(base_analyzer.participants), 3))
                    
                    for i, participant in enumerate(list(base_analyzer.participants)[:3]):
                        with participant_cols[i]:
                            st.write(f"**{participant}**")
                            
                            participant_messages = [
                                msg.content for msg in base_analyzer.messages 
                                if msg.sender == participant
                            ]
                            
                            if participant_messages:
                                participant_text = ' '.join(participant_messages)
                                participant_words = participant_text.split()
                                participant_filtered = blacklist.remove_blacklisted_words(participant_words)
                                
                                if participant_filtered:
                                    participant_clean_text = ' '.join(participant_filtered)
                                    participant_wordcloud = create_plotly_wordcloud(
                                        participant_clean_text, 
                                        f"Palavras de {participant}"
                                    )
                                    if participant_wordcloud:
                                        st.pyplot(participant_wordcloud)
                                else:
                                    st.info("Todas as palavras foram filtradas para este participante")
                            else:
                                st.info("Nenhuma mensagem encontrada")
                
                # Suggestions for custom blacklist
                if st.checkbox("🔍 Mostrar sugestões de palavras para filtrar"):
                    suggestions = blacklist.suggest_custom_blacklist(all_text, min_frequency=3)
                    
                    if suggestions:
                        st.subheader("💡 Sugestões de Palavras para Filtrar")
                        st.write("Palavras frequentes que você pode querer filtrar:")
                        
                        suggestion_cols = st.columns(3)
                        for i, (word, count) in enumerate(suggestions[:15]):
                            with suggestion_cols[i % 3]:
                                if st.button(f"Filtrar '{word}' ({count}x)", key=f"suggest_{word}"):
                                    blacklist.add_custom_words([word])
                                    st.success(f"'{word}' adicionada ao filtro!")
                                    st.experimental_rerun()
                    else:
                        st.info("Nenhuma sugestão encontrada. Seu texto já está bem limpo!")

            with tab5:
                st.header("🧠 Análise Avançada com IA")
                
                if not selected_models or not any(api_keys.values()):
                    st.warning("🔑 Configure pelo menos um modelo de IA para análises avançadas!")
                    st.info("💡 Selecione os modelos de IA na barra lateral e configure as respectivas chaves API.")
                    
                    # Show available models
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**🤖 Modelos Disponíveis:**")
                        st.write("• **OpenAI GPT** - Análise conversacional avançada")
                        st.write("• **Google Gemini** - Insights multimodais")
                    with col2:
                        st.write("• **Anthropic Claude** - Análise psicológica profunda")
                        st.write("• **X.AI Grok** - Perspectivas humorísticas e criativas")
                
                else:
                    # Show selected models
                    st.success(f"🎯 Analisando com: {', '.join(selected_models)}")
                    
                    # Multi-AI Analysis
                    if multi_ai_analyzer and len(selected_models) > 1:
                        st.subheader("🔄 Análise Comparativa Multi-IA")
                        
                        with st.spinner("Executando análise com múltiplos modelos de IA..."):
                            try:
                                # Get all messages as text for analysis
                                messages_text = [msg.content for msg in base_analyzer.messages]
                                
                                # Run sentiment analysis across models
                                if st.button("🚀 Executar Análise Multi-IA", type="primary"):
                                    import asyncio
                                    
                                    # Create async wrapper for Streamlit
                                    async def run_multi_analysis():
                                        sentiment_results = await multi_ai_analyzer.analyze_sentiment_multi_model(
                                            messages_text[:20],  # Limit for demo
                                            models=[model.lower() for model in selected_models]
                                        )
                                        return sentiment_results
                                    
                                    # Run analysis
                                    try:
                                        loop = asyncio.new_event_loop()
                                        asyncio.set_event_loop(loop)
                                        results = loop.run_until_complete(run_multi_analysis())
                                        
                                        # Display results
                                        if results and results.get('individual_results'):
                                            st.subheader("📊 Resultados por Modelo")
                                            
                                            # Create columns for each model
                                            model_cols = st.columns(len(selected_models))
                                            
                                            for i, model in enumerate(selected_models):
                                                model_key = model.lower()
                                                with model_cols[i]:
                                                    st.write(f"**{model}**")
                                                    
                                                    if model_key in results['individual_results']:
                                                        model_result = results['individual_results'][model_key]
                                                        
                                                        if 'sentiment' in model_result:
                                                            sentiment = model_result['sentiment']
                                                            st.metric("Sentimento", sentiment.get('overall', 'N/A'))
                                                        
                                                        if 'insights' in model_result:
                                                            st.write("**Insights:**")
                                                            insights = model_result['insights'][:2]  # Show first 2
                                                            for insight in insights:
                                                                st.write(f"• {insight}")
                                                    else:
                                                        st.error(f"Erro na análise com {model}")
                                            
                                            # Consensus results
                                            if 'consensus' in results:
                                                st.subheader("🎯 Consenso dos Modelos")
                                                consensus = results['consensus']
                                                
                                                if 'overall_sentiment' in consensus:
                                                    st.success(f"**Sentimento Geral:** {consensus['overall_sentiment']}")
                                                
                                                if 'key_insights' in consensus:
                                                    st.write("**Insights Principais:**")
                                                    for insight in consensus['key_insights']:
                                                        st.write(f"✨ {insight}")
                                        
                                    except Exception as e:
                                        st.error(f"Erro durante análise multi-IA: {e}")
                                        st.info("Tente com um modelo individual primeiro.")
                            
                            except Exception as e:
                                st.error(f"Erro ao configurar análise multi-IA: {e}")
                    
                    # Individual model analysis (legacy support)
                    if api_key:
                        ai_data = report.get('ai_analysis', {})
                        
                        if ai_data.get('ai_availability', False):
                            # Sentiment analysis
                            st.subheader("😊 Análise de Sentimentos")
                            sentiment = ai_data.get('sentiment_analysis', {})
                            
                            if 'sentimento_geral' in sentiment:
                                st.write(f"**Sentimento Geral:** {sentiment['sentimento_geral']}")
                            
                            if 'dinamica_emocional' in sentiment:
                                st.markdown(f"**Dinâmica Emocional:** {sentiment['dinamica_emocional']}")
                            
                            if 'momentos_chave' in sentiment:
                                st.subheader("🎯 Momentos Chave")
                                for momento in sentiment['momentos_chave']:
                                    st.write(f"• {momento}")
                            
                            # Relationship dynamics
                            st.subheader("💫 Dinâmica de Relacionamento")
                            relationship = ai_data.get('relationship_dynamics', {})
                            
                            for key, value in relationship.items():
                                if isinstance(value, dict):
                                    st.write(f"**{key.title()}:**")
                                    for subkey, subvalue in value.items():
                                        st.write(f"  • {subkey}: {subvalue}")
                                else:
                                    st.write(f"**{key.title()}:** {value}")
                            
                            # Communication insights
                            st.subheader("💡 Insights de Comunicação")
                            comm_insights = ai_data.get('communication_insights', {})
                            
                            if 'avaliacao_potencial_relacionamento' in comm_insights:
                                score = comm_insights['avaliacao_potencial_relacionamento']
                                st.metric("🎯 Score do Relacionamento", f"{score}/10")
                            
                            if 'alertas_problemas_comunicacao' in comm_insights:
                                st.subheader("⚠️ Alertas")
                                for alerta in comm_insights['alertas_problemas_comunicacao']:
                                    st.warning(f"⚠️ {alerta}")
                        
                        else:
                            st.error("❌ Análise com IA não disponível. Verifique sua chave da API.")
            
            with tab6:
                st.header("🔍 Detalhes do Parsing")
                
                # Format detection info
                st.subheader("📅 Detecção de Formato")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("🎯 Formato Detectado", detected_format)
                    st.metric("📊 Qualidade do Parse", format_quality)
                    
                with col2:
                    st.metric("✅ Taxa de Sucesso", f"{success_rate:.1f}%")
                    parsing_stats = parsing_info.get('parsing_statistics', {})
                    if parsing_stats:
                        st.metric("📝 Linhas Processadas", parsing_stats.get('total_lines', 0))
                
                # Parsing statistics
                if parsing_stats:
                    st.subheader("📈 Estatísticas de Processamento")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("✅ Mensagens Extraídas", parsing_stats.get('parsed_messages', 0))
                        st.metric("📜 Mensagens Multilinhas", parsing_stats.get('multiline_messages', 0))
                    
                    with col2:
                        st.metric("🚫 Linhas Ignoradas", parsing_stats.get('skipped_lines', 0))
                        st.metric("🔧 Mensagens do Sistema", parsing_stats.get('system_messages', 0))
                        
                    with col3:
                        if parsing_stats.get('total_lines', 0) > 0:
                            msg_ratio = (parsing_stats.get('parsed_messages', 0) / parsing_stats.get('total_lines', 1)) * 100
                            st.metric("📋 Proporção Msg/Linhas", f"{msg_ratio:.1f}%")
                
                # Format compatibility guide
                st.subheader("📱 Formatos Suportados")
                
                formats_info = {
                    "🇧🇷 Brasileiro/Europeu": "DD/MM/YYYY HH:MM",
                    "🇺🇸 Americano": "MM/DD/YYYY H:MM AM/PM",
                    "🌍 ISO Internacional": "YYYY-MM-DD HH:MM",
                    "🤖 Android": "DD.MM.YYYY HH:MM",
                    "📱 Alternativo": "DD-MM-YYYY HH:MM"
                }
                
                for format_name, format_example in formats_info.items():
                    emoji = "✅" if format_name.split()[1].lower() in detected_format.lower() else "📋"
                    st.write(f"{emoji} **{format_name}**: `{format_example}`")
                
                # Tips for better parsing
                st.subheader("💡 Dicas para Melhor Análise")
                
                tips = [
                    "🎯 **Taxa de sucesso baixa?** Verifique se o formato está correto",
                    "📱 **Exportação**: Use 'Sem mídia' ao exportar do WhatsApp",
                    "🔤 **Encoding**: Salve o arquivo como UTF-8 para caracteres especiais",
                    "🚫 **Mensagens perdidas?** Algumas mensagens do sistema são filtradas automaticamente",
                    "📜 **Multilinhas**: Mensagens longas são automaticamente concatenadas"
                ]
                
                for tip in tips:
                    st.markdown(f"- {tip}")
            
            with tab7:
                st.header("📋 Relatório Completo")
                
                # Download button for full report
                report_json = json.dumps(report, ensure_ascii=False, indent=2)
                
                st.download_button(
                    label="📥 Baixar Relatório JSON",
                    data=report_json,
                    file_name=f"whatsapp_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
                
                # Show expandable sections
                with st.expander("📊 Análise Linguística"):
                    st.json(report['linguistic_analysis'])
                
                with st.expander("🧠 Análise Psicológica"):
                    st.json(report['psychological_analysis'])
                
                with st.expander("💬 Análise de Comunicação"):
                    st.json(report['communication_analysis'])
                
                with st.expander("❤️ Insights de Relacionamento"):
                    st.json(report['relationship_insights'])
                
                if 'ai_analysis' in report:
                    with st.expander("🤖 Análise com IA"):
                        st.json(report['ai_analysis'])
    
    else:
        # Welcome screen
        st.markdown("""
        ## 👋 Bem-vindo ao WhatsApp Chat Analyzer!
        
        ### 🚀 Como usar:
        1. **📤 Faça upload** do arquivo .txt da sua conversa do WhatsApp
        2. **🔑 Opcionalmente**, adicione sua chave da OpenAI para análises avançadas
        3. **🔍 Explore** os insights e visualizações geradas
        
        ### 📱 Como exportar do WhatsApp:
        1. Abra a conversa no WhatsApp
        2. Toque nos 3 pontos (⋮) → **Mais** → **Exportar conversa**
        3. Escolha **"Sem mídia"**
        4. Salve como arquivo .txt
        
        ### 🧠 O que você vai descobrir:
        - 📊 **Padrões de atividade** e horários mais ativos
        - 💭 **Análise emocional** das mensagens
        - ⏱️ **Tempos de resposta** e engajamento
        - ☁️ **Nuvens de palavras** personalizadas
        - 🤖 **Insights com IA** (opcional)
        - 💫 **Score de relacionamento** e recomendações
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