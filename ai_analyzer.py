import json
from openai import OpenAI
from typing import Dict, List, Optional
import os
from dataclasses import dataclass

@dataclass
class AIAnalysisConfig:
    api_key: Optional[str] = None
    model: str = "gpt-5"
    max_tokens: int = 1000
    temperature: float = 1

class AIWhatsAppAnalyzer:
    def __init__(self, config: AIAnalysisConfig = None):
        self.config = config or AIAnalysisConfig()
        self.client = None
        
        # Try to initialize OpenAI client
        api_key = self.config.api_key or os.getenv('OPENAI_API_KEY')
        if api_key:
            try:
                self.client = OpenAI(api_key=api_key)
                self.ai_available = True
            except Exception:
                self.ai_available = False
        else:
            self.ai_available = False
    
    def analyze_conversation_sentiment(self, messages: List[str]) -> Dict:
        """Analyze overall sentiment and emotional patterns using AI"""
        if not self.ai_available:
            return self._fallback_sentiment_analysis(messages)
        
        conversation_text = "\n".join(messages[:50])  # Limit to first 50 messages
        
        prompt = f"""
        Analise a seguinte conversa de WhatsApp e forneça insights sobre:
        1. Sentimento geral da conversa (positivo, negativo, neutro)
        2. Dinâmica emocional entre os participantes
        3. Momentos de tensão ou harmonia
        4. Padrões de comunicação observados
        
        Conversa:
        {conversation_text}
        
        Responda em formato JSON com as chaves: sentimento_geral, dinamica_emocional, momentos_chave, padroes_comunicacao.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "user", "content": prompt}],
                max_completion_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            
            ai_response = response.choices[0].message.content
            
            # Try to parse JSON response
            try:
                return json.loads(ai_response)
            except json.JSONDecodeError:
                return {"ai_analysis": ai_response, "format": "text"}
                
        except Exception as e:
            return {"error": f"AI analysis failed: {str(e)}"}
    
    def analyze_relationship_dynamics(self, participant_messages: Dict[str, List[str]]) -> Dict:
        """Analyze relationship dynamics between participants using AI"""
        if not self.ai_available:
            return self._fallback_relationship_analysis(participant_messages)
        
        # Create summary of each participant's messages
        participant_summary = {}
        for participant, messages in participant_messages.items():
            sample_messages = messages[:20]  # First 20 messages per participant
            participant_summary[participant] = "\n".join(sample_messages)
        
        prompt = f"""
        Como um psicólogo especialista em comunicação, analise a dinâmica de relacionamento desta conversa:
        
        {json.dumps(participant_summary, ensure_ascii=False, indent=2)}
        
        Forneça insights sobre:
        1. Estilo de comunicação de cada participante
        2. Nivel de intimidade/proximidade
        3. Padrões de dominância ou submissão
        4. Compatibilidade comunicativa
        5. Áreas de possível conflito ou harmonia
        6. Recomendações para melhorar a comunicação
        
        Responda em JSON com essas chaves em português.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "user", "content": prompt}],
                max_completion_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            
            ai_response = response.choices[0].message.content
            
            try:
                return json.loads(ai_response)
            except json.JSONDecodeError:
                return {"ai_analysis": ai_response, "format": "text"}
                
        except Exception as e:
            return {"error": f"Relationship analysis failed: {str(e)}"}
    
    def generate_communication_insights(self, conversation_data: Dict) -> Dict:
        """Generate deep communication insights using AI"""
        if not self.ai_available:
            return self._fallback_communication_insights(conversation_data)
        
        prompt = f"""
        Como um consultor de comunicação experiente, analise estes dados de uma conversa:
        
        {json.dumps(conversation_data, ensure_ascii=False, indent=2)}
        
        Gere insights profundos sobre:
        1. Efetividade da comunicação
        2. Pontos fortes e fracos na interação
        3. Sugestões específicas para cada participante
        4. Estratégias para melhorar o engajamento
        5. Avaliação do potencial de relacionamento (1-10)
        6. Alertas sobre possíveis problemas de comunicação
        
        Responda em JSON estruturado em português.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "user", "content": prompt}],
                max_completion_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            
            ai_response = response.choices[0].message.content
            
            try:
                return json.loads(ai_response)
            except json.JSONDecodeError:
                return {"ai_analysis": ai_response, "format": "text"}
                
        except Exception as e:
            return {"error": f"Communication insights failed: {str(e)}"}
    
    def _fallback_sentiment_analysis(self, messages: List[str]) -> Dict:
        """Fallback analysis when AI is not available"""
        positive_keywords = ['bom', 'ótimo', 'legal', 'adorei', 'obrigado', 'feliz', '😊', '❤️', '😍', '🥰']
        negative_keywords = ['ruim', 'péssimo', 'triste', 'raiva', 'problema', '😢', '😠', '😡', '💔']
        
        positive_count = sum(1 for msg in messages for keyword in positive_keywords if keyword in msg.lower())
        negative_count = sum(1 for msg in messages for keyword in negative_keywords if keyword in msg.lower())
        
        if positive_count > negative_count:
            sentiment = "positivo"
        elif negative_count > positive_count:
            sentiment = "negativo"
        else:
            sentiment = "neutro"
        
        return {
            "sentimento_geral": sentiment,
            "confianca_analise": "baixa (sem IA)",
            "indicadores_positivos": positive_count,
            "indicadores_negativos": negative_count,
            "nota": "Análise básica - para insights avançados, configure uma chave de API de IA"
        }
    
    def _fallback_relationship_analysis(self, participant_messages: Dict[str, List[str]]) -> Dict:
        """Basic relationship analysis without AI"""
        participants = list(participant_messages.keys())
        
        analysis = {
            "tipo_analise": "básica (sem IA)",
            "participantes": participants,
            "observacoes": []
        }
        
        # Simple message count analysis
        for participant, messages in participant_messages.items():
            msg_count = len(messages)
            avg_length = sum(len(msg) for msg in messages) / len(messages) if messages else 0
            
            analysis["observacoes"].append(f"{participant}: {msg_count} mensagens, média {avg_length:.1f} caracteres")
        
        analysis["recomendacao"] = "Configure uma chave de API de IA para análises mais profundas"
        
        return analysis
    
    def _fallback_communication_insights(self, conversation_data: Dict) -> Dict:
        """Basic communication insights without AI"""
        return {
            "tipo_analise": "básica (sem IA)",
            "dados_analisados": list(conversation_data.keys()),
            "insight_principal": "Dados processados com análise básica",
            "recomendacao": "Para insights avançados com IA, configure OPENAI_API_KEY",
            "pontuacao_comunicacao": 7,
            "observacao": "Pontuação baseada em métricas básicas"
        }

class EnhancedWhatsAppAnalyzer:
    """Enhanced analyzer that combines statistical analysis with AI insights"""
    
    def __init__(self, base_analyzer, ai_config: AIAnalysisConfig = None):
        self.base_analyzer = base_analyzer
        self.ai_analyzer = AIWhatsAppAnalyzer(ai_config)
    
    def generate_enhanced_report(self) -> Dict:
        """Generate comprehensive report with both statistical and AI analysis"""
        # Get base statistical analysis
        base_report = self.base_analyzer.generate_comprehensive_report()
        
        # Prepare data for AI analysis
        messages_text = [f"{msg.sender}: {msg.content}" for msg in self.base_analyzer.messages]
        participant_messages = {}
        
        for msg in self.base_analyzer.messages:
            if msg.sender not in participant_messages:
                participant_messages[msg.sender] = []
            participant_messages[msg.sender].append(msg.content)
        
        # Generate AI insights
        ai_sentiment = self.ai_analyzer.analyze_conversation_sentiment(messages_text)
        ai_relationship = self.ai_analyzer.analyze_relationship_dynamics(participant_messages)
        ai_communication = self.ai_analyzer.generate_communication_insights(base_report)
        
        # Combine reports
        enhanced_report = base_report.copy()
        enhanced_report["ai_analysis"] = {
            "sentiment_analysis": ai_sentiment,
            "relationship_dynamics": ai_relationship,
            "communication_insights": ai_communication,
            "ai_availability": self.ai_analyzer.ai_available
        }
        
        return enhanced_report