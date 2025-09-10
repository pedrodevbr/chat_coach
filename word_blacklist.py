#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Word blacklist system for WhatsApp chat analysis
Filters out common words, system messages, and noise that don't add value to analysis
"""

import re
from typing import Set, List, Dict
from collections import Counter

class WordBlacklist:
    def __init__(self):
        self.blacklist = self._create_default_blacklist()
        self.custom_blacklist: Set[str] = set()
        self.whitelist: Set[str] = set()  # Words to always keep even if blacklisted
        
    def _create_default_blacklist(self) -> Set[str]:
        """Create comprehensive default blacklist"""
        
        # Portuguese stop words and common words
        portuguese_stop_words = {
            # Articles
            'a', 'o', 'as', 'os', 'um', 'uma', 'uns', 'umas',
            
            # Prepositions
            'de', 'da', 'do', 'das', 'dos', 'em', 'na', 'no', 'nas', 'nos',
            'por', 'para', 'com', 'sem', 'sobre', 'sob', 'entre', 'contra',
            'até', 'desde', 'perante', 'após', 'ante', 'durante', 'mediante',
            'segundo', 'conforme', 'consoante',
            
            # Conjunctions
            'e', 'ou', 'mas', 'porém', 'contudo', 'todavia', 'entretanto',
            'no entanto', 'logo', 'portanto', 'assim', 'então', 'pois',
            'porque', 'como', 'quando', 'onde', 'se', 'que', 'embora',
            'ainda que', 'mesmo que', 'caso', 'desde que', 'a fim de que',
            
            # Pronouns
            'eu', 'tu', 'ele', 'ela', 'nós', 'vós', 'eles', 'elas',
            'me', 'te', 'se', 'nos', 'vos', 'lhe', 'lhes', 'mim', 'ti',
            'si', 'comigo', 'contigo', 'consigo', 'conosco', 'convosco',
            'meu', 'teu', 'seu', 'nosso', 'vosso', 'minha', 'tua', 'sua',
            'nossa', 'vossa', 'meus', 'teus', 'seus', 'nossos', 'vossos',
            'minhas', 'tuas', 'suas', 'nossas', 'vossas',
            
            # Adverbs
            'não', 'sim', 'talvez', 'quiçá', 'acaso', 'porventura', 'decerto',
            'certamente', 'realmente', 'verdadeiramente', 'efetivamente',
            'muito', 'pouco', 'mais', 'menos', 'tão', 'tanto', 'quanto',
            'bem', 'mal', 'melhor', 'pior', 'assim', 'já', 'ainda', 'sempre',
            'nunca', 'jamais', 'hoje', 'ontem', 'amanhã', 'agora', 'depois',
            'antes', 'cedo', 'tarde', 'logo', 'breve', 'aqui', 'aí', 'ali',
            'lá', 'cá', 'acolá', 'algures', 'nenhures', 'alhures', 'dentro',
            'fora', 'perto', 'longe', 'acima', 'abaixo', 'adiante', 'atrás',
            
            # Verbs (common auxiliary and linking verbs)
            'ser', 'estar', 'ter', 'haver', 'ir', 'vir', 'fazer', 'dar',
            'ver', 'saber', 'poder', 'querer', 'dever', 'dizer', 'falar',
            'é', 'está', 'tem', 'há', 'vai', 'vem', 'faz', 'dá', 'vê',
            'sabe', 'pode', 'quer', 'deve', 'diz', 'fala', 'foi', 'era',
            'será', 'seria', 'teve', 'tinha', 'terá', 'teria', 'sendo',
            'estando', 'tendo', 'havendo', 'indo', 'vindo', 'fazendo',
            'dando', 'vendo', 'sabendo', 'podendo', 'querendo', 'devendo',
            'dizendo', 'falando', 'sido', 'estado', 'tido', 'ido', 'vindo',
            'feito', 'dado', 'visto', 'sabido', 'podido', 'querido',
            'devido', 'dito', 'falado',
            
            # Numbers and quantifiers
            'um', 'dois', 'três', 'quatro', 'cinco', 'seis', 'sete', 'oito',
            'nove', 'dez', 'onze', 'doze', 'treze', 'catorze', 'quinze',
            'dezesseis', 'dezessete', 'dezoito', 'dezenove', 'vinte',
            'primeiro', 'segundo', 'terceiro', 'quarto', 'quinto',
            'alguns', 'algumas', 'vários', 'várias', 'muitos', 'muitas',
            'poucos', 'poucas', 'todos', 'todas', 'nenhum', 'nenhuma',
            'qualquer', 'quaisquer', 'certo', 'certa', 'certos', 'certas',
            'outro', 'outra', 'outros', 'outras', 'mesmo', 'mesma',
            'mesmos', 'mesmas', 'próprio', 'própria', 'próprios', 'próprias'
        }
        
        # English stop words (for international chats)
        english_stop_words = {
            'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you',
            'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his',
            'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself',
            'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which',
            'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are',
            'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having',
            'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if',
            'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for',
            'with', 'about', 'against', 'between', 'into', 'through', 'during',
            'before', 'after', 'above', 'below', 'up', 'down', 'in', 'out',
            'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once',
            'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any',
            'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such',
            'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too',
            'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now'
        }
        
        # Spanish common words (for international chats)
        spanish_stop_words = {
            'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no',
            'te', 'lo', 'le', 'da', 'su', 'por', 'son', 'con', 'para', 'al',
            'del', 'los', 'las', 'una', 'sus', 'nos', 'les', 'está', 'está',
            'pero', 'son', 'todo', 'más', 'muy', 'ya', 'hay', 'fue', 'ser',
            'como', 'si', 'sobre', 'me', 'yo', 'mi', 'tu', 'él', 'ella',
            'ese', 'eso', 'esta', 'este', 'esto', 'bien', 'sí', 'qué', 'cómo'
        }
        
        # Internet slang and WhatsApp specific
        internet_slang = {
            # Common abbreviations
            'vc', 'você', 'tb', 'também', 'hj', 'hoje', 'td', 'tudo', 'pq',
            'porque', 'q', 'que', 'n', 'não', 'bj', 'beijo', 'bjs', 'beijos',
            'abs', 'abraços', 'vlw', 'valeu', 'flw', 'falou', 'blz', 'beleza',
            'tmj', 'estamos juntos', 'rs', 'rsrs', 'rsrsrs', 'kkk', 'kkkk',
            'kkkkk', 'haha', 'hahaha', 'hehe', 'hihi', 'huehue', 'lol',
            'kek', 'top', 'show', 'massa', 'dahora', 'maneiro', 'legal',
            'foda', 'irado', 'bacana', 'demais', 'né', 'né?', 'tá', 'ta',
            'tah', 'tô', 'to', 'tou', 'tava', 'tava', 'tô', 'to', 'vou',
            'vo', 'vô', 'pra', 'pro', 'pros', 'pras', 'numa', 'nuns',
            'umas', 'duma', 'duns', 'dumas',
            
            # English internet slang
            'lol', 'lmao', 'lmfao', 'rofl', 'omg', 'wtf', 'btw', 'imo', 'imho',
            'fyi', 'asap', 'ttyl', 'brb', 'afk', 'gg', 'gj', 'wp', 'np',
            'ty', 'thx', 'thanks', 'ur', 'u', 'ur', 'r', 'pls', 'plz',
            'idk', 'dunno', 'nvm', 'nvmd', 'jk', 'jkjk', 'irl', 'tbh',
            'ngl', 'fr', 'no cap', 'cap', 'sus', 'salty', 'toxic', 'noob',
            'rekt', 'pwned', 'fail', 'epic', 'nice', 'cool', 'awesome',
            'amazing', 'wow', 'whoa', 'damn', 'shit', 'fuck', 'hell',
            'god', 'jesus', 'christ', 'ok', 'okay', 'okey', 'k', 'kk',
            
            # Greetings and farewells
            'oi', 'olá', 'eai', 'e ai', 'eae', 'e ae', 'salve', 'fala',
            'oie', 'oii', 'oiii', 'hi', 'hello', 'hey', 'sup', 'whats up',
            'wassup', 'yo', 'hola', 'buenos', 'buenas', 'bye', 'tchau',
            'tchao', 'xau', 'xao', 'fui', 'foi', 'ate', 'até', 'cya',
            'see ya', 'later', 'farewell', 'adios', 'hasta', 'luego',
            
            # Common expressions and interjections
            'ah', 'oh', 'eh', 'hm', 'hmm', 'hmmm', 'uhm', 'uhh', 'err',
            'ahem', 'wow', 'uau', 'nossa', 'caramba', 'putz', 'puxa',
            'eita', 'opa', 'ops', 'oops', 'uff', 'ufa', 'afe', 'xi',
            'aff', 'bah', 'meh', 'duh', 'tsk', 'pfft', 'mhmm', 'aha',
            'uh-huh', 'nah', 'yep', 'yup', 'yeah', 'yea', 'si', 'claro',
            'claro que si', 'por supuesto',
            
            # Time expressions
            'ontem', 'hoje', 'amanhã', 'depois', 'antes', 'agora', 'já',
            'ainda', 'sempre', 'nunca', 'às vezes', 'sometimes', 'never',
            'always', 'often', 'usually', 'rarely', 'seldom', 'yesterday',
            'today', 'tomorrow', 'now', 'then', 'later', 'soon', 'early',
            'late', 'morning', 'afternoon', 'evening', 'night', 'manhã',
            'tarde', 'noite', 'madrugada', 'ayer', 'mañana', 'temprano',
            'noche', 'dia', 'semana', 'mês', 'ano', 'hora', 'minuto',
            'segundo', 'week', 'month', 'year', 'hour', 'minute', 'second',
            'day', 'time', 'tempo',
        }
        
        # System messages and media indicators
        system_messages = {
            '<mídia', 'mídia', 'oculta>', '<media', 'omitted>', 'image',
            'video', 'audio', 'document', 'contact', 'location', 'sticker',
            'gif', 'voice', 'message', 'deleted', 'this', 'was', 'removed',
            'ligação', 'chamada', 'call', 'missed', 'perdida', 'voz', 'video',
            'videochamada', 'videocall', 'grupo', 'group', 'added', 'removed',
            'left', 'joined', 'created', 'changed', 'settings', 'subject',
            'description', 'picture', 'admin', 'administrator', 'member',
            'participant', 'encryption', 'criptografia', 'security', 'code',
            'changed', 'mudou', 'alterou', 'modified', 'updated', 'backup',
            'restored', 'messages', 'mensagens', 'end-to-end', 'encrypted',
            'criptografadas', 'https', 'http', 'www', 'com', 'br', 'org',
            'net', 'info', 'link', 'url', 'site', 'website', 'página',
            'page', 'click', 'clique', 'access', 'acesse', 'visit', 'visite','null','perdida','mensagem'
        }
        
        # Combine all blacklists
        blacklist = set()
        blacklist.update(portuguese_stop_words)
        blacklist.update(english_stop_words)
        blacklist.update(spanish_stop_words)
        blacklist.update(internet_slang)
        blacklist.update(system_messages)
        
        return blacklist
    
    def add_custom_words(self, words: List[str]) -> None:
        """Add custom words to blacklist"""
        for word in words:
            self.custom_blacklist.add(word.lower().strip())
    
    def add_whitelist_words(self, words: List[str]) -> None:
        """Add words to whitelist (never filtered)"""
        for word in words:
            self.whitelist.add(word.lower().strip())
    
    def remove_blacklisted_words(self, words: List[str]) -> List[str]:
        """Remove blacklisted words but keep whitelisted ones"""
        filtered_words = []
        
        for word in words:
            word_clean = self._clean_word(word)
            
            if not word_clean:  # Skip empty words
                continue
            
            word_lower = word_clean.lower()
            
            # Always keep whitelisted words
            if word_lower in self.whitelist:
                filtered_words.append(word_clean)
                continue
            
            # Skip blacklisted words
            if word_lower in self.blacklist or word_lower in self.custom_blacklist:
                continue
            
            # Skip very short words (unless whitelisted)
            if len(word_clean) < 3:
                continue
            
            # Skip words that are mostly numbers
            if self._is_mostly_numeric(word_clean):
                continue
            
            filtered_words.append(word_clean)
        
        return filtered_words
    
    def _clean_word(self, word: str) -> str:
        """Clean individual word"""
        # Remove punctuation and special characters
        cleaned = re.sub(r'[^\w\s]', '', word)
        
        # Remove extra whitespace
        cleaned = cleaned.strip()
        
        # Remove URLs
        if 'http' in cleaned.lower() or 'www' in cleaned.lower():
            return ''
        
        # Remove phone numbers (simple pattern)
        if re.match(r'^\+?\d+$', cleaned):
            return ''
        
        return cleaned
    
    def _is_mostly_numeric(self, word: str) -> bool:
        """Check if word is mostly numbers"""
        if len(word) == 0:
            return True
        
        numeric_chars = sum(1 for char in word if char.isdigit())
        return (numeric_chars / len(word)) > 0.5
    
    def analyze_text(self, text: str) -> Dict:
        """Analyze text and return filtered vs unfiltered statistics"""
        words = text.lower().split()
        
        # Original word count
        original_words = [self._clean_word(word) for word in words]
        original_words = [w for w in original_words if w]
        
        # Filtered words
        filtered_words = self.remove_blacklisted_words(original_words)
        
        # Calculate statistics
        original_count = Counter(original_words)
        filtered_count = Counter(filtered_words)
        
        removed_words = set(original_words) - set(filtered_words)
        removed_count = sum(original_count[word] for word in removed_words)
        
        return {
            "original_words": len(original_words),
            "filtered_words": len(filtered_words),
            "removed_words": removed_count,
            "removal_percentage": (removed_count / max(1, len(original_words))) * 100,
            "top_original": original_count.most_common(10),
            "top_filtered": filtered_count.most_common(10),
            "top_removed": [(word, original_count[word]) for word in 
                           sorted(removed_words, key=lambda x: original_count[x], reverse=True)[:10]]
        }
    
    def get_blacklist_info(self) -> Dict:
        """Get information about current blacklist"""
        return {
            "total_blacklisted": len(self.blacklist) + len(self.custom_blacklist),
            "default_blacklisted": len(self.blacklist),
            "custom_blacklisted": len(self.custom_blacklist),
            "whitelisted": len(self.whitelist),
            "categories": {
                "Portuguese stop words": 200,  # Approximate counts
                "English stop words": 100,
                "Spanish stop words": 50,
                "Internet slang": 150,
                "System messages": 50,
                "Custom words": len(self.custom_blacklist)
            }
        }
    
    def suggest_custom_blacklist(self, text: str, min_frequency: int = 5) -> List[str]:
        """Suggest words that appear frequently and might be worth blacklisting"""
        words = text.lower().split()
        cleaned_words = [self._clean_word(word) for word in words]
        cleaned_words = [w for w in cleaned_words if w and len(w) >= 3]
        
        word_count = Counter(cleaned_words)
        
        # Find frequent words not already blacklisted
        suggestions = []
        for word, count in word_count.most_common(50):
            if (count >= min_frequency and 
                word.lower() not in self.blacklist and 
                word.lower() not in self.custom_blacklist and
                word.lower() not in self.whitelist):
                suggestions.append((word, count))
        
        return suggestions[:20]  # Return top 20 suggestions

# Global instance
default_blacklist = WordBlacklist()