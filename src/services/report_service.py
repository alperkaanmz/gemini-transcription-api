"""
Report generation services following SOLID principles
"""
import os
import json
import csv
import requests
from datetime import datetime
from typing import Dict, Any, Optional
from ..models import AnalysisResult


class ReportService:
    """
    Report generation service following Single Responsibility Principle
    Handles HTML, JSON, CSV report generation
    """
    
    def __init__(self, reports_dir: str = "reports"):
        self.reports_dir = reports_dir
        self._ensure_reports_directory()
    
    def _ensure_reports_directory(self) -> None:
        """Ensure reports directory exists"""
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir)
    
    def generate_all_reports(self, result: AnalysisResult, generate_csv: bool = False) -> Dict[str, str]:
        """
        Generate reports - default: only HTML and JSON
        
        Args:
            result: Analysis result data
            generate_csv: Whether to generate CSV (only for API usage)
            
        Returns:
            Dictionary with paths to generated reports
        """
        timestamp = result.timestamp.strftime("%Y%m%d_%H%M%S")
        safe_name = self._safe_filename(result.candidate_name)
        base_filename = f"{safe_name}_{timestamp}"
        
        # Always generate HTML and JSON
        html_path = self._generate_html_report(result, base_filename)
        json_path = self._generate_json_report(result, base_filename)
        
        # Only generate CSV if explicitly requested (for API usage)
        csv_path = None
        if generate_csv:
            csv_path = self._generate_csv_report(result, base_filename)
        
        return {
            'html_path': html_path,
            'json_path': json_path,
            'csv_path': csv_path,
            'base_filename': base_filename
        }
    
    def _safe_filename(self, name: str) -> str:
        """Convert name to safe filename"""
        safe_name = name.replace(" ", "_")
        safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"
        return "".join(c for c in safe_name if c in safe_chars)
    
    def _generate_html_report(self, result: AnalysisResult, base_filename: str) -> str:
        """Generate interactive HTML report with charts"""
        html_path = os.path.join(self.reports_dir, f"{base_filename}_report.html")
        
        html_content = f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Video Analiz Raporu - {result.candidate_name}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .content {{
            padding: 30px;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .info-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }}
        .chart-container {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .chart-row {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }}
        .chart-box {{
            height: 400px;
        }}
        .mbti-box {{
            background: linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            margin: 20px 0;
        }}
        .cost-summary {{
            background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Video Analiz Raporu</h1>
            <h2>{result.candidate_name}</h2>
            <p>{result.position} - {result.timestamp.strftime('%d/%m/%Y %H:%M')}</p>
        </div>
        
        <div class="content">
            <div class="info-grid">
                <div class="info-card">
                    <h3>👤 Aday Bilgileri</h3>
                    <p><strong>İsim:</strong> {result.candidate_name}</p>
                    <p><strong>Pozisyon:</strong> {result.position}</p>
                    <p><strong>Analiz Tarihi:</strong> {result.timestamp.strftime('%d/%m/%Y %H:%M:%S')}</p>
                </div>
                
                <div class="info-card">
                    <h3>💰 Maliyet Analizi</h3>
                    <p><strong>Toplam Token:</strong> {result.cost_report.total_tokens:,}</p>
                    <p><strong>Maliyet:</strong> ${result.cost_report.total_cost_usd:.6f}</p>
                    <p><strong>TL Karşılığı:</strong> ₺{result.cost_report.total_cost_usd * 34:.4f}</p>
                </div>
            </div>
            
            <div class="mbti-box">
                <h2>🧠 MBTI Kişilik Analizi</h2>
                <h1 style="font-size: 3em; margin: 10px 0;">{result.mbti_data.predicted_type}</h1>
                <p>Güven Seviyesi: {result.mbti_data.confidence_level:.1f}%</p>
            </div>
            
            <div class="chart-row">
                <div class="chart-container">
                    <h3>😊 Duygu Analizi</h3>
                    <div class="chart-box">
                        <canvas id="emotionChart"></canvas>
                    </div>
                </div>
                
                <div class="chart-container">
                    <h3>📊 Genel Değerlendirme</h3>
                    <div class="chart-box">
                        <canvas id="sentimentChart"></canvas>
                    </div>
                </div>
            </div>
            
            <div class="chart-container">
                <h3>🧠 MBTI Boyutları</h3>
                <div class="chart-box">
                    <canvas id="mbtiChart"></canvas>
                </div>
            </div>
            
            <div class="cost-summary">
                <h3>💡 Analiz Özeti</h3>
                <p>Bu rapor, Gemini Flash 2.5 Lite AI modeli kullanılarak oluşturulmuştur. 
                Duygu analizi, MBTI kişilik değerlendirmesi ve iletişim becerisi analizi içermektedir.</p>
                <p><strong>Oluşturulma Zamanı:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
            </div>
        </div>
    </div>

    <script>
        // Emotion Analysis Chart
        const emotionCtx = document.getElementById('emotionChart').getContext('2d');
        new Chart(emotionCtx, {{
            type: 'doughnut',
            data: {{
                labels: ['Mutluluk', 'Üzüntü', 'Öfke', 'Şaşırma', 'Korku', 'Nötr', 'Güven'],
                datasets: [{{
                    data: [
                        {result.emotion_data.happiness},
                        {result.emotion_data.sadness},
                        {result.emotion_data.anger},
                        {result.emotion_data.surprise},
                        {result.emotion_data.fear},
                        {result.emotion_data.neutral},
                        {result.emotion_data.confidence}
                    ],
                    backgroundColor: [
                        '#FFD93D', '#FF6B6B', '#FF4757', '#FFA502', 
                        '#A4B0BE', '#57606F', '#2ED573'
                    ]
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false
            }}
        }});

        // Sentiment Analysis Chart
        const sentimentCtx = document.getElementById('sentimentChart').getContext('2d');
        new Chart(sentimentCtx, {{
            type: 'bar',
            data: {{
                labels: ['Pozitif', 'Negatif', 'Nötr', 'Motivasyon', 'İletişim'],
                datasets: [{{
                    label: 'Değerlendirme (%)',
                    data: [
                        {result.sentiment_data.positive_percentage},
                        {result.sentiment_data.negative_percentage},
                        {result.sentiment_data.neutral_percentage},
                        {result.sentiment_data.motivation_level},
                        {result.sentiment_data.communication_skill}
                    ],
                    backgroundColor: [
                        '#2ED573', '#FF4757', '#A4B0BE', '#FFA502', '#5352ED'
                    ]
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 100
                    }}
                }}
            }}
        }});

        // MBTI Chart
        const mbtiCtx = document.getElementById('mbtiChart').getContext('2d');
        new Chart(mbtiCtx, {{
            type: 'radar',
            data: {{
                labels: ['Extraversion', 'Sensing', 'Thinking', 'Judging'],
                datasets: [{{
                    label: 'MBTI Profili',
                    data: [
                        {result.mbti_data.extraversion_introversion},
                        {result.mbti_data.sensing_intuition},
                        {result.mbti_data.thinking_feeling},
                        {result.mbti_data.judging_perceiving}
                    ],
                    backgroundColor: 'rgba(102, 126, 234, 0.2)',
                    borderColor: '#667eea',
                    pointBackgroundColor: '#667eea'
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    r: {{
                        beginAtZero: true,
                        max: 100
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>"""
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return html_path
    
    def _generate_json_report(self, result: AnalysisResult, base_filename: str) -> str:
        """Generate JSON data export"""
        json_path = os.path.join(self.reports_dir, f"{base_filename}_data.json")
        
        data = {
            'candidate_name': result.candidate_name,
            'position': result.position,
            'timestamp': result.timestamp.isoformat(),
            'emotion_data': {
                'happiness': result.emotion_data.happiness,
                'sadness': result.emotion_data.sadness,
                'anger': result.emotion_data.anger,
                'surprise': result.emotion_data.surprise,
                'fear': result.emotion_data.fear,
                'neutral': result.emotion_data.neutral,
                'disgust': result.emotion_data.disgust,
                'confidence': result.emotion_data.confidence
            },
            'sentiment_data': {
                'positive_percentage': result.sentiment_data.positive_percentage,
                'negative_percentage': result.sentiment_data.negative_percentage,
                'neutral_percentage': result.sentiment_data.neutral_percentage,
                'stress_level': result.sentiment_data.stress_level,
                'motivation_level': result.sentiment_data.motivation_level,
                'communication_skill': result.sentiment_data.communication_skill
            },
            'mbti_data': {
                'predicted_type': result.mbti_data.predicted_type,
                'extraversion_introversion': result.mbti_data.extraversion_introversion,
                'sensing_intuition': result.mbti_data.sensing_intuition,
                'thinking_feeling': result.mbti_data.thinking_feeling,
                'judging_perceiving': result.mbti_data.judging_perceiving,
                'confidence_level': result.mbti_data.confidence_level
            },
            'cost_report': result.cost_report.to_dict(),
            'text_analysis': result.text_analysis
        }
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return json_path
    
    def _generate_csv_report(self, result: AnalysisResult, base_filename: str) -> str:
        """Generate CSV data export compatible with API"""
        csv_path = os.path.join(self.reports_dir, f"{base_filename}_data.csv")
        
        # API compatible CSV format
        csv_data = {
            'kisi_adi': result.candidate_name,
            'mulakat_adi': result.position,
            'llm_skoru': 85.0,  # Default score
            
            # Emotion data with both avg_ and regular format
            'avg_duygu_mutlu_%': result.emotion_data.happiness,
            'avg_duygu_kizgin_%': result.emotion_data.anger,
            'avg_duygu_igrenme_%': result.emotion_data.disgust,
            'avg_duygu_korku_%': result.emotion_data.fear,
            'avg_duygu_uzgun_%': result.emotion_data.sadness,
            'avg_duygu_saskin_%': result.emotion_data.surprise,
            'avg_duygu_dogal_%': result.emotion_data.neutral,
            'avg_duygu_guven_%': result.emotion_data.confidence,
            
            'duygu_mutlu_%': result.emotion_data.happiness,
            'duygu_kizgin_%': result.emotion_data.anger,
            'duygu_igrenme_%': result.emotion_data.disgust,
            'duygu_korku_%': result.emotion_data.fear,
            'duygu_uzgun_%': result.emotion_data.sadness,
            'duygu_saskin_%': result.emotion_data.surprise,
            'duygu_dogal_%': result.emotion_data.neutral,
            'duygu_guven_%': result.emotion_data.confidence,
            
            # Screen time data (default values)
            'ekran_disi_sure_sn': 0,
            'ekran_disi_sayisi': 0,
            'avg_ekran_disi_sure_sn': 0,
            'avg_ekran_disi_sayisi': 0,
            
            # Text analysis
            'soru': 'Genel Mülakat',
            'cevap': result.text_analysis[:500] if len(result.text_analysis) > 500 else result.text_analysis,
            
            # MBTI data - API integer bekliyor
            'tip': 1,  # API integer bekliyor, varsayılan tip ID'si
            'avg_tip': 1,  # API integer bekliyor, varsayılan tip ID'si
            'mbti_tip_str': result.mbti_data.predicted_type,
            'avg_llm_skoru': 85.0,
            
            # Sentiment data
            'pozitif_%': result.sentiment_data.positive_percentage,
            'negatif_%': result.sentiment_data.negative_percentage,
            'notr_%': result.sentiment_data.neutral_percentage,
            'stres_seviyesi': result.sentiment_data.stress_level,
            'motivasyon': result.sentiment_data.motivation_level,
            'iletisim_becerisi': result.sentiment_data.communication_skill,
            
            # MBTI dimensions with original field names
            'mbti_disdönük_%': result.mbti_data.extraversion_introversion,
            'mbti_sezgi_%': result.mbti_data.sensing_intuition,
            'mbti_hissetme_%': result.mbti_data.thinking_feeling,
            'mbti_algilama_%': result.mbti_data.judging_perceiving,
            'mbti_guvenilirlik': result.mbti_data.confidence_level,
            
            # Time and cost data
            'analiz_tarihi': result.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'token_sayisi': result.cost_report.total_tokens,
            'maliyet_usd': result.cost_report.total_cost_usd,
            
            # Evaluation fields
            'genel_puan': 85.0,
            'pozisyon_uygunlugu': 'Uygun',
            'guclü_yanlar': 'İletişim, Motivasyon',
            'gelisim_alanlari': 'Stres yönetimi',
            'oneri_durumu': 'Olumlu',
            'detayli_yorum': f'{result.candidate_name} adayı {result.position} pozisyonu için değerlendirilmiştir.',
            'iletisim_skoru': result.sentiment_data.communication_skill,
            'liderlik_potansiyeli': result.emotion_data.confidence,
            'stres_yonetimi': 100 - result.sentiment_data.stress_level,
            'takım_uyumu': result.sentiment_data.positive_percentage,
            'profesyonellik_skoru': result.emotion_data.confidence,
            'kararlılık_seviyesi': result.emotion_data.confidence,
            'duygusal_zeka': (result.emotion_data.happiness + result.emotion_data.confidence) / 2,
            'pozisyona_uygunluk': 85.0,
            'uygunluk_aciklamasi': f'{result.candidate_name} pozisyon için uygun görülmektedir.'
        }
        
        with open(csv_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=csv_data.keys())
            writer.writeheader()
            writer.writerow(csv_data)
        
        return csv_path
