#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-Model AI Analyzer for WhatsApp Chat Analysis
Supports OpenAI GPT, Google Gemini, Grok, and Claude models
"""

import json
import os
import asyncio
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from abc import ABC, abstractmethod
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('multi_ai_debug.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# AI Model imports with logging
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
    logger.info("✅ OpenAI library imported successfully")
except ImportError as e:
    OPENAI_AVAILABLE = False
    logger.warning(f"❌ OpenAI library not available: {e}")

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
    logger.info("✅ Google Generative AI library imported successfully")
except ImportError as e:
    GEMINI_AVAILABLE = False
    logger.warning(f"❌ Gemini library not available: {e}")

try:
    import anthropic
    CLAUDE_AVAILABLE = True
    logger.info("✅ Anthropic library imported successfully")
except ImportError as e:
    CLAUDE_AVAILABLE = False
    logger.warning(f"❌ Claude library not available: {e}")

# For Grok - using OpenAI-compatible API
try:
    import requests
    GROK_AVAILABLE = True
    logger.info("✅ Requests library imported successfully (for Grok)")
except ImportError as e:
    GROK_AVAILABLE = False
    logger.warning(f"❌ Requests library not available for Grok: {e}")

@dataclass
class AIModelConfig:
    """Configuration for AI models"""
    model_type: str  # 'openai', 'gemini', 'claude', 'grok'
    api_key: Optional[str] = None
    model_name: Optional[str] = None
    max_tokens: int = 1000
    temperature: float = 1
    timeout: int = 30
    
    def __post_init__(self):
        # Set default model names
        if not self.model_name:
            defaults = {
                'openai': 'gpt-4o-mini',
                'gemini': 'gemini-2.5-flash',
                'claude': 'claude-3-sonnet-20240229',
                'grok': 'grok-beta'
            }
            self.model_name = defaults.get(self.model_type, 'gpt-4o-mini')

class BaseAIProvider(ABC):
    """Base class for AI providers"""
    
    def __init__(self, config: AIModelConfig):
        self.config = config
        self.client = None
        self.is_available = False
        self.last_request_time = 0
        logger.info(f"🔧 Initializing {config.model_type} provider with model: {config.model_name}")
        self.rate_limit_delay = 1  # seconds between requests
    
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the AI provider"""
        pass
    
    @abstractmethod
    async def analyze_async(self, prompt: str) -> Dict:
        """Perform async analysis"""
        pass
    
    def analyze(self, prompt: str) -> Dict:
        """Synchronous wrapper for analysis"""
        try:
            logger.debug(f"🔍 Starting synchronous analysis with {self.config.model_type}")
            result = asyncio.run(self.analyze_async(prompt))
            logger.debug(f"✅ Synchronous analysis completed for {self.config.model_type}")
            return result
        except Exception as e:
            error_msg = f"Analysis failed: {str(e)}"
            logger.error(f"❌ Analysis error for {self.config.model_type}: {error_msg}")
            return {"error": error_msg}
    
    def _rate_limit_check(self):
        """Check rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)
        
        self.last_request_time = time.time()
    
    def _clean_response(self, response_text: str) -> Dict:
        """Try to extract JSON from response"""
        try:
            # Try to parse as JSON first
            return json.loads(response_text)
        except json.JSONDecodeError:
            # If not JSON, try to extract JSON from text
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except:
                    pass
            
            # Fallback: return as text analysis
            return {"ai_analysis": response_text, "format": "text"}

class OpenAIProvider(BaseAIProvider):
    """OpenAI GPT provider"""
    
    def initialize(self) -> bool:
        if not OPENAI_AVAILABLE:
            logger.warning("❌ OpenAI library not available for initialization")
            return False
        
        api_key = self.config.api_key or os.getenv('OPENAI_API_KEY')
        if not api_key:
            logger.warning("❌ No OpenAI API key provided")
            return False
        
        try:
            logger.info(f"🔧 Initializing OpenAI client with model: {self.config.model_name}")
            self.client = OpenAI(api_key=api_key)
            self.is_available = True
            logger.info("✅ OpenAI client initialized successfully")
            return True
        except Exception as e:
            logger.error(f"❌ OpenAI initialization failed: {e}")
            return False
    
    async def analyze_async(self, prompt: str) -> Dict:
        if not self.is_available:
            logger.warning("❌ OpenAI provider not available for analysis")
            return {"error": "OpenAI not available"}
        
        logger.debug(f"🔍 Starting OpenAI analysis with {self.config.model_name}")
        self._rate_limit_check()
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_completion_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            
            response_text = response.choices[0].message.content
            logger.info(f"✅ OpenAI analysis completed successfully")
            return self._clean_response(response_text)
            
        except Exception as e:
            error_msg = f"OpenAI analysis failed: {str(e)}"
            logger.error(f"❌ OpenAI analysis error: {error_msg}")
            return {"error": error_msg}

class GeminiProvider(BaseAIProvider):
    """Google Gemini provider"""
    
    def initialize(self) -> bool:
        if not GEMINI_AVAILABLE:
            logger.warning("❌ Gemini library not available for initialization")
            return False
        
        api_key = self.config.api_key or os.getenv('GEMINI_API_KEY')
        if not api_key:
            logger.warning("❌ No Gemini API key provided")
            return False
        
        try:
            logger.info(f"🔧 Initializing Gemini client with model: {self.config.model_name}")
            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel(self.config.model_name)
            self.is_available = True
            logger.info("✅ Gemini client initialized successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Gemini initialization failed: {e}")
            return False
    
    async def analyze_async(self, prompt: str) -> Dict:
        if not self.is_available:
            logger.warning("❌ Gemini provider not available for analysis")
            return {"error": "Gemini not available"}
        
        logger.debug(f"🔍 Starting Gemini analysis with {self.config.model_name}")
        self._rate_limit_check()
        
        try:
            # Configure generation parameters
            generation_config = genai.types.GenerationConfig(
                max_output_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            
            response = self.client.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            response_text = response.text
            logger.info(f"✅ Gemini analysis completed successfully")
            return self._clean_response(response_text)
            
        except Exception as e:
            error_msg = f"Gemini analysis failed: {str(e)}"
            logger.error(f"❌ Gemini analysis error: {error_msg}")
            return {"error": error_msg}

class ClaudeProvider(BaseAIProvider):
    """Anthropic Claude provider"""
    
    def initialize(self) -> bool:
        if not CLAUDE_AVAILABLE:
            logger.warning("❌ Claude library not available for initialization")
            return False
        
        api_key = self.config.api_key or os.getenv('CLAUDE_API_KEY')
        if not api_key:
            logger.warning("❌ No Claude API key provided")
            return False
        
        try:
            logger.info(f"🔧 Initializing Claude client with model: {self.config.model_name}")
            self.client = anthropic.Anthropic(api_key=api_key)
            self.is_available = True
            logger.info("✅ Claude client initialized successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Claude initialization failed: {e}")
            return False
    
    async def analyze_async(self, prompt: str) -> Dict:
        if not self.is_available:
            logger.warning("❌ Claude provider not available for analysis")
            return {"error": "Claude not available"}
        
        logger.debug(f"🔍 Starting Claude analysis with {self.config.model_name}")
        self._rate_limit_check()
        
        try:
            message = self.client.messages.create(
                model=self.config.model_name,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text
            logger.info(f"✅ Claude analysis completed successfully")
            return self._clean_response(response_text)
            
        except Exception as e:
            error_msg = f"Claude analysis failed: {str(e)}"
            logger.error(f"❌ Claude analysis error: {error_msg}")
            return {"error": error_msg}

class GrokProvider(BaseAIProvider):
    """X.AI Grok provider"""
    
    def initialize(self) -> bool:
        if not GROK_AVAILABLE:
            logger.warning("❌ Grok dependencies not available for initialization")
            return False
        
        api_key = self.config.api_key or os.getenv('GROK_API_KEY')
        if not api_key:
            logger.warning("❌ No Grok API key provided")
            return False
        
        try:
            logger.info(f"🔧 Initializing Grok client with model: {self.config.model_name}")
            # Grok uses OpenAI-compatible API
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://api.x.ai/v1"
            )
            self.is_available = True
            logger.info("✅ Grok client initialized successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Grok initialization failed: {e}")
            return False
    
    async def analyze_async(self, prompt: str) -> Dict:
        if not self.is_available:
            logger.warning("❌ Grok provider not available for analysis")
            return {"error": "Grok not available"}
        
        logger.debug(f"🔍 Starting Grok analysis with {self.config.model_name}")
        self._rate_limit_check()
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            
            response_text = response.choices[0].message.content
            logger.info(f"✅ Grok analysis completed successfully")
            return self._clean_response(response_text)
            
        except Exception as e:
            error_msg = f"Grok analysis failed: {str(e)}"
            logger.error(f"❌ Grok analysis error: {error_msg}")
            return {"error": error_msg}

class MultiAIWhatsAppAnalyzer:
    """Multi-model AI analyzer for WhatsApp chats"""
    
    def __init__(self):
        self.providers: Dict[str, BaseAIProvider] = {}
        self.active_models: List[str] = []
        logger.info("🚀 MultiAIWhatsAppAnalyzer initialized")
        logger.info(f"📊 Available libraries - OpenAI: {OPENAI_AVAILABLE}, Gemini: {GEMINI_AVAILABLE}, Claude: {CLAUDE_AVAILABLE}, Grok: {GROK_AVAILABLE}")
        
    def add_model(self, model_type: str, config: AIModelConfig) -> bool:
        """Add an AI model to the analyzer"""
        logger.info(f"🔧 Adding {model_type} model to analyzer")
        
        provider_classes = {
            'openai': OpenAIProvider,
            'gemini': GeminiProvider,
            'claude': ClaudeProvider,
            'grok': GrokProvider
        }
        
        if model_type not in provider_classes:
            logger.error(f"❌ Unknown model type: {model_type}")
            return False
        
        provider = provider_classes[model_type](config)
        
        if provider.initialize():
            self.providers[model_type] = provider
            if model_type not in self.active_models:
                self.active_models.append(model_type)
            logger.info(f"✅ {model_type} model added successfully")
            return True
        
        logger.warning(f"❌ Failed to initialize {model_type} model")
        return False
    
    def get_available_models(self) -> List[Dict]:
        """Get list of available models with their capabilities"""
        models = []
        
        model_info = {
            'openai': {
                'name': 'OpenAI GPT',
                'models': ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'gpt-3.5-turbo'],
                'strengths': ['General analysis', 'Conversation patterns', 'Relationship insights'],
                'icon': '🤖',
                'speed': 'Fast',
                'cost': 'Low'
            },
            'gemini': {
                'name': 'Google Gemini',
                'models': ['gemini-pro', 'gemini-pro-vision'],
                'strengths': ['Multilingual analysis', 'Cultural insights', 'Complex reasoning'],
                'icon': '💎',
                'speed': 'Medium',
                'cost': 'Low'
            },
            'claude': {
                'name': 'Anthropic Claude',
                'models': ['claude-3-opus-20240229', 'claude-3-sonnet-20240229', 'claude-3-haiku-20240307'],
                'strengths': ['Deep psychological analysis', 'Nuanced communication', 'Safety-focused'],
                'icon': '🧠',
                'speed': 'Medium',
                'cost': 'Medium'
            },
            'grok': {
                'name': 'X.AI Grok',
                'models': ['grok-beta'],
                'strengths': ['Witty analysis', 'Social media insights', 'Humor detection'],
                'icon': '🚀',
                'speed': 'Fast',
                'cost': 'Medium'
            }
        }
        
        for model_type, provider in self.providers.items():
            if provider.is_available:
                info = model_info.get(model_type, {})
                info.update({
                    'type': model_type,
                    'available': True,
                    'current_model': provider.config.model_name
                })
                models.append(info)
        
        # Add unavailable models for reference
        for model_type, info in model_info.items():
            if model_type not in self.providers:
                info.update({
                    'type': model_type,
                    'available': False,
                    'reason': 'API key not configured'
                })
                models.append(info)
        
        return models
    
    async def analyze_sentiment_multi_model(self, messages: List[str], models: List[str] = None) -> Dict:
        """Analyze sentiment using multiple AI models"""
        logger.info(f"🔍 Starting multi-model sentiment analysis")
        
        if not models:
            models = self.active_models
        
        logger.info(f"📊 Using models: {models}")
        logger.info(f"💬 Analyzing {len(messages)} messages")
        
        conversation_text = "\n".join(messages[:30])  # Limit for API costs
        
        prompt = f"""
        Analise a seguinte conversa de WhatsApp e forneça insights sobre:
        1. Sentimento geral da conversa (positivo, negativo, neutro)
        2. Dinâmica emocional entre os participantes
        3. Momentos de tensão ou harmonia
        4. Padrões de comunicação observados
        5. Recomendações para melhorar a comunicação
        
        Conversa:
        {conversation_text}
        
        Responda em formato JSON com as chaves: sentimento_geral, dinamica_emocional, momentos_chave, padroes_comunicacao, recomendacoes.
        """
        
        results = {}
        
        # Analyze with each model concurrently
        tasks = []
        for model_type in models:
            if model_type in self.providers:
                task = self._analyze_with_model(model_type, prompt)
                tasks.append((model_type, task))
        
        # Wait for all analyses to complete
        for model_type, task in tasks:
            try:
                result = await task
                results[model_type] = result
            except Exception as e:
                results[model_type] = {"error": f"Analysis failed: {str(e)}"}
        
        return results
    
    async def _analyze_with_model(self, model_type: str, prompt: str) -> Dict:
        """Analyze with a specific model"""
        provider = self.providers.get(model_type)
        if not provider:
            return {"error": f"Provider {model_type} not available"}
        
        return await provider.analyze_async(prompt)
    
    def analyze_relationship_dynamics_multi(self, participant_messages: Dict[str, List[str]], 
                                          models: List[str] = None) -> Dict:
        """Analyze relationship dynamics using multiple models"""
        
        if not models:
            models = self.active_models[:2]  # Limit to 2 models for cost
        
        # Create summary of each participant
        participant_summary = {}
        for participant, messages in participant_messages.items():
            sample_messages = messages[:15]  # Limit for API costs
            participant_summary[participant] = "\n".join(sample_messages)
        
        prompt = f"""
        Como um psicólogo especialista em comunicação, analise a dinâmica de relacionamento desta conversa:
        
        {json.dumps(participant_summary, ensure_ascii=False, indent=2)}
        
        Forneça insights sobre:
        1. Estilo de comunicação de cada participante
        2. Nível de intimidade/proximidade
        3. Padrões de dominância ou submissão
        4. Compatibilidade comunicativa
        5. Áreas de possível conflito ou harmonia
        6. Recomendações específicas para cada participante
        7. Score de compatibilidade (0-10)
        
        Responda em JSON estruturado em português.
        """
        
        results = {}
        
        for model_type in models:
            if model_type in self.providers:
                try:
                    result = self.providers[model_type].analyze(prompt)
                    results[model_type] = result
                except Exception as e:
                    results[model_type] = {"error": f"Analysis failed: {str(e)}"}
        
        return results
    
    def get_consensus_analysis(self, multi_model_results: Dict) -> Dict:
        """Generate consensus analysis from multiple model results"""
        
        if not multi_model_results:
            return {"error": "No results to analyze"}
        
        # Extract successful analyses
        successful_analyses = {}
        for model, result in multi_model_results.items():
            if "error" not in result:
                successful_analyses[model] = result
        
        if not successful_analyses:
            return {"error": "All models failed to provide analysis"}
        
        # Generate consensus
        consensus = {
            "models_used": list(successful_analyses.keys()),
            "consensus_available": len(successful_analyses) > 1,
            "primary_analysis": None,
            "supporting_analyses": [],
            "conflicting_opinions": [],
            "confidence_score": 0
        }
        
        # Use the first successful analysis as primary
        primary_model = list(successful_analyses.keys())[0]
        consensus["primary_analysis"] = {
            "model": primary_model,
            "result": successful_analyses[primary_model]
        }
        
        # Add supporting analyses
        for model, result in successful_analyses.items():
            if model != primary_model:
                consensus["supporting_analyses"].append({
                    "model": model,
                    "result": result
                })
        
        # Calculate confidence score
        consensus["confidence_score"] = min(len(successful_analyses) * 25, 100)
        
        # Add model comparison
        consensus["model_comparison"] = self._compare_model_results(successful_analyses)
        
        return consensus
    
    def _compare_model_results(self, results: Dict) -> Dict:
        """Compare results from different models"""
        comparison = {
            "sentiment_agreement": True,
            "key_insights": [],
            "model_strengths": {},
            "recommendation_overlap": 0
        }
        
        # Extract key insights from each model
        for model, result in results.items():
            if isinstance(result, dict):
                # Extract sentiment if available
                sentiment = result.get('sentimento_geral', result.get('sentiment', 'unknown'))
                
                # Store model-specific insights
                comparison["model_strengths"][model] = {
                    "sentiment": sentiment,
                    "analysis_depth": len(str(result)),
                    "structured_response": isinstance(result, dict) and len(result) > 3
                }
                
                # Collect key insights
                if 'momentos_chave' in result:
                    comparison["key_insights"].extend(result['momentos_chave'][:2])
                elif 'key_moments' in result:
                    comparison["key_insights"].extend(result['key_moments'][:2])
        
        return comparison
    
    def generate_enhanced_report_multi_ai(self, base_report: Dict, 
                                        messages: List[str],
                                        participant_messages: Dict[str, List[str]]) -> Dict:
        """Generate enhanced report using multiple AI models"""
        
        enhanced_report = base_report.copy()
        
        if not self.active_models:
            enhanced_report["multi_ai_analysis"] = {
                "available": False,
                "reason": "No AI models configured"
            }
            return enhanced_report
        
        try:
            # Sentiment analysis with multiple models
            sentiment_results = asyncio.run(
                self.analyze_sentiment_multi_model(messages, self.active_models[:3])
            )
            
            # Relationship dynamics with selected models
            relationship_results = self.analyze_relationship_dynamics_multi(
                participant_messages, self.active_models[:2]
            )
            
            # Generate consensus
            sentiment_consensus = self.get_consensus_analysis(sentiment_results)
            relationship_consensus = self.get_consensus_analysis(relationship_results)
            
            enhanced_report["multi_ai_analysis"] = {
                "available": True,
                "models_used": self.active_models,
                "sentiment_analysis": {
                    "individual_results": sentiment_results,
                    "consensus": sentiment_consensus
                },
                "relationship_analysis": {
                    "individual_results": relationship_results,
                    "consensus": relationship_consensus
                },
                "model_comparison": self._generate_model_comparison(),
                "recommendation": self._get_best_model_recommendation()
            }
            
        except Exception as e:
            enhanced_report["multi_ai_analysis"] = {
                "available": True,
                "error": f"Multi-AI analysis failed: {str(e)}"
            }
        
        return enhanced_report
    
    def _generate_model_comparison(self) -> Dict:
        """Generate comparison of available models"""
        comparison = {
            "speed_ranking": [],
            "accuracy_estimation": {},
            "cost_ranking": [],
            "specialty_recommendations": {}
        }
        
        # Speed ranking (estimated)
        speed_order = ['openai', 'grok', 'gemini', 'claude']
        comparison["speed_ranking"] = [model for model in speed_order if model in self.active_models]
        
        # Cost ranking (estimated - low to high)
        cost_order = ['openai', 'gemini', 'grok', 'claude']
        comparison["cost_ranking"] = [model for model in cost_order if model in self.active_models]
        
        # Specialty recommendations
        specialties = {
            'openai': ['General analysis', 'Conversation patterns', 'Quick insights'],
            'gemini': ['Multilingual chats', 'Cultural analysis', 'Complex reasoning'],
            'claude': ['Psychological depth', 'Safety analysis', 'Nuanced communication'],
            'grok': ['Humor analysis', 'Social trends', 'Witty insights']
        }
        
        for model in self.active_models:
            if model in specialties:
                comparison["specialty_recommendations"][model] = specialties[model]
        
        return comparison
    
    def _get_best_model_recommendation(self) -> Dict:
        """Recommend best model for different use cases"""
        
        recommendations = {
            "best_overall": "openai",
            "best_for_relationships": "claude", 
            "best_for_humor": "grok",
            "best_for_multilingual": "gemini",
            "most_cost_effective": "openai"
        }
        
        # Filter recommendations to only available models
        available_recommendations = {}
        for use_case, model in recommendations.items():
            if model in self.active_models:
                available_recommendations[use_case] = model
            else:
                # Fallback to first available model
                if self.active_models:
                    available_recommendations[use_case] = self.active_models[0]
        
        return available_recommendations

# Global instance
multi_ai_analyzer = MultiAIWhatsAppAnalyzer()