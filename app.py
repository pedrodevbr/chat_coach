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

# Import our custom modules
from whatsapp_analyzer import WhatsAppChatAnalyzer, WhatsAppMessage
from ai_analyzer import EnhancedWhatsAppAnalyzer, AIAnalysisConfig

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
    
    # API Key input
    api_key = st.sidebar.text_input("🔑 Chave OpenAI (opcional)", type="password", 
                                   help="Para análises avançadas com IA")
    
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
            
            # Parse chat
            base_analyzer.parse_chat(chat_text)
            
            if not base_analyzer.messages:
                st.error("❌ Nenhuma mensagem encontrada. Verifique o formato do texto.")
                st.info("📋 Formato esperado: DD/MM/YYYY HH:MM - Nome: Mensagem")
                return
            
            # Generate analysis
            report = enhanced_analyzer.generate_enhanced_report()
            
            # Main dashboard
            st.success(f"✅ {len(base_analyzer.messages)} mensagens processadas de {len(base_analyzer.participants)} participantes!")
            
            # Metrics row
            col1, col2, col3, col4 = st.columns(4)
            
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
            
            # Tabs for different analyses
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📊 Visão Geral", "📈 Atividade", "💭 Análise Textual", 
                "🧠 Análise com IA", "📋 Relatório Completo"
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
                st.header("🧠 Análise Avançada com IA")
                
                if not api_key:
                    st.warning("🔑 Configure uma chave da OpenAI para análises avançadas!")
                    st.info("💡 Você ainda pode ver as análises básicas nas outras abas.")
                else:
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
            
            with tab5:
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