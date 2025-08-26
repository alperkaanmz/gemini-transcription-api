"""
Data models for video analysis results
"""
from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime


@dataclass
class EmotionData:
    """Emotion analysis data model"""
    happiness: float = 0.0
    sadness: float = 0.0
    anger: float = 0.0
    surprise: float = 0.0
    fear: float = 0.0
    neutral: float = 0.0
    disgust: float = 0.0
    confidence: float = 0.0
    
    def to_dict(self) -> Dict[str, float]:
        return {
            'happiness': self.happiness,
            'sadness': self.sadness,
            'anger': self.anger,
            'surprise': self.surprise,
            'fear': self.fear,
            'neutral': self.neutral,
            'disgust': self.disgust,
            'confidence': self.confidence
        }


@dataclass
class SentimentData:
    """Overall sentiment analysis data"""
    positive_percentage: float = 0.0
    negative_percentage: float = 0.0
    neutral_percentage: float = 0.0
    stress_level: float = 0.0
    motivation_level: float = 0.0
    communication_skill: float = 0.0
    
    def to_dict(self) -> Dict[str, float]:
        return {
            'positive_percentage': self.positive_percentage,
            'negative_percentage': self.negative_percentage,
            'neutral_percentage': self.neutral_percentage,
            'stress_level': self.stress_level,
            'motivation_level': self.motivation_level,
            'communication_skill': self.communication_skill
        }


@dataclass
class MBTIData:
    """MBTI personality analysis data"""
    predicted_type: str = "ESTJ"
    extraversion_introversion: float = 0.0
    sensing_intuition: float = 0.0
    thinking_feeling: float = 0.0
    judging_perceiving: float = 0.0
    confidence_level: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'predicted_type': self.predicted_type,
            'extraversion_introversion': self.extraversion_introversion,
            'sensing_intuition': self.sensing_intuition,
            'thinking_feeling': self.thinking_feeling,
            'judging_perceiving': self.judging_perceiving,
            'confidence_level': self.confidence_level
        }


@dataclass
class CostReport:
    """API cost tracking data"""
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    input_cost_usd: float = 0.0
    output_cost_usd: float = 0.0
    total_cost_usd: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'input_tokens': self.input_tokens,
            'output_tokens': self.output_tokens,
            'total_tokens': self.total_tokens,
            'input_cost_usd': self.input_cost_usd,
            'output_cost_usd': self.output_cost_usd,
            'total_cost_usd': self.total_cost_usd
        }


@dataclass
class AnalysisResult:
    """Complete video analysis result"""
    candidate_name: str
    position: str
    emotion_data: EmotionData
    sentiment_data: SentimentData
    mbti_data: MBTIData
    text_analysis: str
    cost_report: CostReport
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'candidate_name': self.candidate_name,
            'position': self.position,
            'emotion_analysis': {
                'facial_emotions': self.emotion_data.to_dict(),
                'overall_sentiment': self.sentiment_data.to_dict(),
                'mbti_analysis': self.mbti_data.to_dict()
            },
            'text_analysis': self.text_analysis,
            'cost_report': self.cost_report.to_dict(),
            'timestamp': self.timestamp.isoformat()
        }
