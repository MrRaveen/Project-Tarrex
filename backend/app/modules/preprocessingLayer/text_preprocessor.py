import re
import logging
from typing import List, Dict, Any, Optional
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
import nltk

logger = logging.getLogger(__name__)

class TextPreprocessor:
    def __init__(self):
        # Download required NLTK data
        self._download_nltk_data()
        
        self.stemmer = PorterStemmer()
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
        # Sri Lankan specific stop words and terms
        self.sri_lankan_stop_words = {
            'sri', 'lanka', 'lankan', 'colombo', 'kandy', 'galle', 'jaffna',
            'government', 'minister', 'president', 'official', 'said', 'says'
        }
        
        # Common Sinhala/Tamil terms that might appear in English text
        self.common_local_terms = {
            'ayubowan': 'greeting',
            'vanakkam': 'greeting', 
            'dhanyavaad': 'thank you',
            'nandri': 'thank you',
            'kade': 'shop',
            'weda': 'work',
            'pola': 'market',
            'gedara': 'home',
            'pansala': 'temple',
            'kovil': 'temple'
        }
        
        # Economic and political terms specific to Sri Lanka
        self.special_terms = {
            'lkr': 'sri lankan rupees',
            'rs': 'rupees',
            'ird': 'inland revenue department',
            'cb': 'central bank',
            'cbsl': 'central bank of sri lanka',
            'gdp': 'gross domestic product',
            'vat': 'value added tax',
            'nbt': 'nation building tax',
            'esc': 'economic service charge',
            'ceb': 'ceylon electricity board',
            'lwc': 'lanka electricity company',
            'slpa': 'sri lanka ports authority',
            'sltb': 'sri lanka transport board'
        }
    
    def _download_nltk_data(self):
        """Download required NLTK data"""
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
            
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
            
        try:
            nltk.data.find('corpora/wordnet')
        except LookupError:
            nltk.download('wordnet')
    
    def preprocess_text(self, text: str, language: str = 'english') -> str:
        """Preprocess text for NLP tasks"""
        if not text or not isinstance(text, str):
            return ""
        
        try:
            # Convert to lowercase
            text = text.lower()
            
            # Remove special characters and numbers
            text = re.sub(r'[^a-zA-Z\s]', ' ', text)
            
            # Tokenize
            tokens = word_tokenize(text)
            
            # Remove stop words
            tokens = [token for token in tokens if token not in self.stop_words]
            
            # Remove Sri Lankan specific stop words
            tokens = [token for token in tokens if token not in self.sri_lankan_stop_words]
            
            # Stemming
            tokens = [self.stemmer.stem(token) for token in tokens]
            
            # Lemmatization
            tokens = [self.lemmatizer.lemmatize(token) for token in tokens]
            
            # Remove short words
            tokens = [token for token in tokens if len(token) > 2]
            
            # Join back to text
            processed_text = ' '.join(tokens)
            
            return processed_text.strip()
            
        except Exception as e:
            logger.error(f"Error preprocessing text: {e}")
            return text
    
    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """Extract keywords from text"""
        processed_text = self.preprocess_text(text)
        
        if not processed_text:
            return []
        
        # Tokenize and count frequencies
        tokens = word_tokenize(processed_text)
        word_freq = {}
        
        for token in tokens:
            if token in word_freq:
                word_freq[token] += 1
            else:
                word_freq[token] = 1
        
        # Sort by frequency
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        # Get top keywords
        keywords = [word for word, freq in sorted_words[:max_keywords]]
        
        return keywords
    
    def detect_sentiment(self, text: str) -> Dict[str, Any]:
        """Simple sentiment analysis for Sri Lankan context"""
        if not text:
            return {'sentiment': 'neutral', 'score': 0.0}
        
        # Positive words relevant to Sri Lankan context
        positive_words = {
            'growth', 'develop', 'progress', 'improve', 'benefit', 'success',
            'positive', 'good', 'great', 'excellent', 'better', 'strong',
            'stable', 'recover', 'boost', 'increase', 'profit', 'gain',
            'opportunity', 'hope', 'optimistic', 'peace', 'unity', 'harmony'
        }
        
        # Negative words relevant to Sri Lankan context
        negative_words = {
            'crisis', 'problem', 'issue', 'challenge', 'difficult', 'hard',
            'bad', 'poor', 'weak', 'negative', 'worse', 'decline', 'drop',
            'loss', 'debt', 'inflation', 'unemployment', 'poverty', 'strike',
            'protest', 'conflict', 'violence', 'corruption', 'scandal', 'fraud'
        }
        
        processed_text = self.preprocess_text(text)
        tokens = word_tokenize(processed_text)
        
        positive_count = sum(1 for token in tokens if token in positive_words)
        negative_count = sum(1 for token in tokens if token in negative_words)
        
        total_words = len(tokens)
        
        if total_words == 0:
            return {'sentiment': 'neutral', 'score': 0.0}
        
        positive_score = positive_count / total_words
        negative_score = negative_count / total_words
        
        sentiment_score = positive_score - negative_score
        
        if sentiment_score > 0.1:
            sentiment = 'positive'
        elif sentiment_score < -0.1:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'sentiment': sentiment,
            'score': round(sentiment_score, 3),
            'positive_words': positive_count,
            'negative_words': negative_count,
            'total_words': total_words
        }
    
    def extract_named_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities from text (simplified version)"""
        entities = {
            'persons': [],
            'organizations': [],
            'locations': [],
            'dates': [],
            'currencies': []
        }
        
        # Simple pattern matching for Sri Lankan context
        
        # Person names (common Sri Lankan names)
        person_patterns = [
            r'\b(?:Mr\.|Ms\.|Mrs\.|Dr\.)\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b'
        ]
        
        # Organizations (Sri Lankan government and companies)
        org_patterns = [
            r'\b(?:Government|Ministry|Department|Board|Authority|Corporation)\s+of\s+[A-Z][a-z]+',
            r'\b[A-Z][a-z]+\s+(?:Limited|Ltd|Pvt|Private|Company|Corp)\.?',
            r'\b(?:CEB|LECO|SLTB|SLPA|IRD|CBSL|SEC)\b'
        ]
        
        # Locations (Sri Lankan cities and regions)
        location_patterns = [
            r'\b(?:Colombo|Kandy|Galle|Jaffna|Trincomalee|Anuradhapura|Badulla|Matara|Ratnapura)',
            r'\b(?:Northern|Eastern|Western|Southern|Central|North Western|North Central|Uva|Sabaragamuwa)\s+Province',
            r'\b(?:Sri\s+Lanka|Ceylon)\b'
        ]
        
        # Dates
        date_patterns = [
            r'\b\d{1,2}/\d{1,2}/\d{4}\b',
            r'\b\d{4}-\d{2}-\d{2}\b',
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4}\b'
        ]
        
        # Currencies
        currency_patterns = [
            r'\bRs\.?\s*\d+(?:,\d{3})*(?:\.\d{2})?\b',
            r'\bLKR\s*\d+(?:,\d{3})*(?:\.\d{2})?\b',
            r'\b\$\s*\d+(?:,\d{3})*(?:\.\d{2})?\b'
        ]
        
        # Extract entities using patterns
        for pattern in person_patterns:
            entities['persons'].extend(re.findall(pattern, text))
        
        for pattern in org_patterns:
            entities['organizations'].extend(re.findall(pattern, text))
        
        for pattern in location_patterns:
            entities['locations'].extend(re.findall(pattern, text))
        
        for pattern in date_patterns:
            entities['dates'].extend(re.findall(pattern, text))
        
        for pattern in currency_patterns:
            entities['currencies'].extend(re.findall(pattern, text))
        
        # Remove duplicates
        for key in entities:
            entities[key] = list(set(entities[key]))
        
        return entities
    
    def calculate_readability_score(self, text: str) -> float:
        """Calculate simple readability score"""
        if not text:
            return 0.0
        
        try:
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            words = re.findall(r'\b\w+\b', text.lower())
            
            if not sentences or not words:
                return 0.0
            
            avg_sentence_length = len(words) / len(sentences)
            avg_word_length = sum(len(word) for word in words) / len(words)
            
            # Simple readability formula (higher = more complex)
            readability = (avg_sentence_length * 0.4) + (avg_word_length * 0.6)
            
            return round(readability, 2)
            
        except Exception as e:
            logger.error(f"Error calculating readability: {e}")
            return 0.0
    
    def detect_language(self, text: str) -> str:
        """Simple language detection (English vs Sinhala/Tamil)"""
        if not text:
            return 'unknown'
        
        # Common Sinhala characters (Unicode range)
        sinhala_chars = re.findall(r'[\u0D80-\u0DFF]', text)
        
        # Common Tamil characters (Unicode range)
        tamil_chars = re.findall(r'[\u0B80-\u0BFF]', text)
        
        if sinhala_chars:
            return 'sinhala'
        elif tamil_chars:
            return 'tamil'
        else:
            # Assume English if no Sinhala/Tamil characters found
            return 'english'
    
    def summarize_text(self, text: str, max_sentences: int = 3) -> str:
        """Simple text summarization"""
        if not text:
            return ""
        
        try:
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            if not sentences:
                return ""
            
            # Simple heuristic: take first few sentences
            summary = ' '.join(sentences[:max_sentences])
            
            return summary
            
        except Exception as e:
            logger.error(f"Error summarizing text: {e}")
            return text[:500] + '...' if len(text) > 500 else text