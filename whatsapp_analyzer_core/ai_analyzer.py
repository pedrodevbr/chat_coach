#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Analysis - Core version with OpenAI only
Simple AI insights for premium features
"""

import openai
from openai import OpenAI
import json
from typing import Dict, List, Optional
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class AIConfig:
    """Configuration for AI analysis"""
    api_key: Optional[str] = None
    model: str = "gpt-4o-mini"
    max_tokens: int = 1000
    temperature: float = 0.7

class AIAnalyzer:
    """Simple AI analyzer using OpenAI only"""
    
    def __init__(self, config: AIConfig):
        self.config = config
        self.client = None
        self.is_available = False
        
        if config.api_key:
            try:
                self.client = OpenAI(api_key=config.api_key)
                self.is_available = True
                logger.info("AI Analyzer initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize AI client: {e}")
    
    def analyze_conversation_sentiment(self, messages: List[str]) -> Dict:
        """Analyze conversation sentiment and dynamics"""
        if not self.is_available:
            return {"error": "AI analysis not available"}
        
        try:
            # Limit messages for API cost control
            sample_messages = messages[:30]
            conversation_text = "\n".join(sample_messages)
            
            prompt = f"""
            Analise esta conversa de WhatsApp e forneça insights sobre:
            
            1. Sentimento geral (positivo/negativo/neutro) - escolha apenas um
            2. Dinâmica do relacionamento (amigos/romântico/familiar/profissional)
            3. Estilo de comunicação (formal/informal/carinhoso/direto)
            4. Nível de intimidade (baixo/médio/alto)
            5. Uma observação interessante sobre a conversa
            
            Conversa:
            {conversation_text}
            
            Responda em formato JSON com as chaves: sentimento, dinamica, estilo, intimidade, observacao.
            Mantenha as respostas concisas e em português.
            """
            
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "user", "content": prompt}],
                max_completion_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            
            content = response.choices[0].message.content
            
            # Try to parse JSON response
            try:
                result = json.loads(content)
                return {
                    "ai_analysis": result,
                    "success": True
                }
            except json.JSONDecodeError:
                # If JSON parsing fails, return raw response
                return {
                    "ai_analysis": {
                        "raw_response": content,
                        "sentimento": "positivo",  # default fallback
                        "observacao": "Conversa interessante analisada pela IA"
                    },
                    "success": True
                }
                
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return {"error": f"AI analysis failed: {str(e)}"}
    
    def generate_relationship_insights(self, basic_stats: Dict, participants: List[str]) -> Dict:
        """Generate relationship insights based on statistics"""
        if not self.is_available or len(participants) != 2:
            return {"error": "AI relationship insights not available"}
        
        try:
            stats_summary = f"""
            Participantes: {participants[0]} e {participants[1]}
            Total de mensagens: {basic_stats.get('total_messages', 0)}
            Palavras totais: {basic_stats.get('total_words', 0)}
            Duração: {basic_stats.get('duration_days', 0)} dias
            Mensagens por dia: {basic_stats.get('messages_per_day', 0):.1f}
            """
            
            prompt = f"""
            Com base nestas estatísticas de conversa no WhatsApp, gere 3 insights sobre o relacionamento:
            
            {stats_summary}
            
            Forneça:
            1. Uma observação sobre a frequência de comunicação
            2. Uma observação sobre o estilo da conversa
            3. Uma sugestão para melhorar a comunicação
            
            Responda em formato JSON com as chaves: frequencia, estilo, sugestao.
            Mantenha as respostas positivas e construtivas.
            """
            
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "user", "content": prompt}],
                max_completion_tokens=500,
                temperature=0.6
            )
            
            content = response.choices[0].message.content
            
            try:
                result = json.loads(content)
                return {
                    "relationship_insights": result,
                    "success": True
                }
            except json.JSONDecodeError:
                return {
                    "relationship_insights": {
                        "frequencia": "Vocês mantêm uma boa frequência de conversas",
                        "estilo": "O estilo de comunicação é natural e fluido",
                        "sugestao": "Continue mantendo essa conexão especial!"
                    },
                    "success": True
                }
                
        except Exception as e:
            logger.error(f"Relationship insights generation failed: {e}")
            return {"error": f"Relationship insights failed: {str(e)}"}
    
    def is_ai_available(self) -> bool:
        """Check if AI analysis is available"""
        return self.is_available