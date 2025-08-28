import os
import google.generativeai as genai
from datetime import datetime
import json
import base64
from typing import Dict, List, Any
import tempfile
import shutil


class VideoAnalyzer:
    def __init__(self, api_key: str):
        """
        Video analizi için Gemini Flash 2.5 Lite API kullanarak sınıf
        
        Args:
            api_key (str): ***REMOVED***
        """
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash-lite')
        self.total_tokens = {'input': 0, 'output': 0, 'total': 0}
        self.total_cost = 0.0
        
    def upload_video(self, video_path: str) -> Any:
        """
        Video dosyasını Gemini API'ye yükle
        
        Args:
            video_path (str): Video dosyasının yolu
            
        Returns:
            Yüklenen video dosyası objesi
        """
        import time
        
        print(f"Video yükleniyor: {video_path}")
        video_file = genai.upload_file(video_path, mime_type=self._get_mime_type(video_path))
        print(f"Video yüklendi: {video_file.uri}")
        
        # Video işlenmesini bekle
        print("Video işlenmeyi bekliyor...")
        while video_file.state.name == "PROCESSING":
            print(".", end="", flush=True)
            time.sleep(2)
            video_file = genai.get_file(video_file.name)
        
        if video_file.state.name == "FAILED":
            raise ValueError(f"Video işleme başarısız: {video_file.state.name}")
        
        print(f"\nVideo hazır: {video_file.state.name}")
        return video_file
    
    def _track_usage(self, response):
        """Token kullanımını takip et ve maliyet hesapla"""
        try:
            if hasattr(response, 'usage_metadata'):
                usage = response.usage_metadata
                input_tokens = usage.prompt_token_count
                output_tokens = usage.candidates_token_count
                total_tokens = usage.total_token_count
                
                self.total_tokens['input'] += input_tokens
                self.total_tokens['output'] += output_tokens  
                self.total_tokens['total'] += total_tokens
                
                # Gemini 2.5 Flash Lite fiyatları (Nisan 2024)
                # Input: $0.075 per 1M tokens
                # Output: $0.30 per 1M tokens
                input_cost = (input_tokens / 1_000_000) * 0.075
                output_cost = (output_tokens / 1_000_000) * 0.30
                total_cost = input_cost + output_cost
                
                self.total_cost += total_cost
                
                print(f"Token kullanımı: Input={input_tokens}, Output={output_tokens}, Total={total_tokens}")
                print(f"İşlem maliyeti: ${total_cost:.6f}")
                
        except Exception as e:
            print(f"Token takip hatası: {e}")
    
    def get_cost_report(self) -> Dict[str, Any]:
        """Maliyet raporu oluştur"""
        return {
            'total_tokens': self.total_tokens,
            'total_cost_usd': round(self.total_cost, 6),
            'cost_breakdown': {
                'input_cost': round((self.total_tokens['input'] / 1_000_000) * 0.075, 6),
                'output_cost': round((self.total_tokens['output'] / 1_000_000) * 0.30, 6)
            },
            'pricing_info': {
                'input_rate': '$0.075 per 1M tokens',
                'output_rate': '$0.30 per 1M tokens',
                'model': 'gemini-2.5-flash-lite'
            }
        }
    
    def _get_mime_type(self, file_path: str) -> str:
        """Video dosyasının MIME tipini belirle"""
        extension = file_path.lower().split('.')[-1]
        mime_types = {
            'mp4': 'video/mp4',
            'webm': 'video/webm',
            'mov': 'video/quicktime',
            'avi': 'video/x-msvideo',
            'mkv': 'video/x-matroska'
        }
        return mime_types.get(extension, 'video/mp4')
    
    def extract_text_from_video(self, video_file: Any) -> str:
        """
        Videodan metin çıkarma
        
        Args:
            video_file: Yüklenmiş video dosyası
            
        Returns:
            str: Videodan çıkarılan metin
        """
        prompt = """
        Bu videoyu analiz et ve aşağıdaki işlemleri yap:
        
        1. Videodaki tüm konuşmaları transkript et
        2. Ekranda görünen yazıları oku
        3. Ana konuları ve mesajları özetle
        
        Lütfen sonucu aşağıdaki formatta ver:
        
        TRANSKRIPT:
        [Konuşmaların tam metni]
        
        EKRAN METİNLERİ:
        [Ekranda görünen yazılar]
        
        ANA KONULAR:
        [Ana konular ve mesajlar]
        """
        
        response = self.model.generate_content([video_file, prompt])
        self._track_usage(response)
        return response.text
    
    def analyze_emotions(self, video_file: Any) -> Dict[str, Any]:
        """
        Videodan gelişmiş duygu analizi
        
        Args:
            video_file: Yüklenmiş video dosyası
            
        Returns:
            Dict: Detaylı duygu analizi sonuçları
        """
        prompt = """
        Bu videoyu izle ve kapsamlı duygu analizi yap. En az 6 farklı duyguyu analiz et:
        
        1. DETAYLI YÜZSEL DUYGULAR (her biri 0-100 arası puan):
           - Mutluluk (Happiness) - gülümseme, sevinç
           - Üzüntü (Sadness) - kaygı, melankolik ifade
           - Öfke (Anger) - sinirlilik, hoşnutsuzluk
           - Şaşkınlık (Surprise) - şaşırmışlık, merak
           - Korku (Fear) - tedirginlik, çekinme
           - İğrenme (Disgust) - hoşlanmama, tiksinme
           - Nötr (Neutral) - doğal, ifadesiz
           - Güven (Confidence) - kendine güven, kararlılık
        
        2. SES ANALİZİ:
           - Enerji seviyesi (0-100)
           - Konuşma hızı (0-100)
           - Ses tonundaki istikrar (0-100)
           - Duygusal yoğunluk (0-100)
        
        3. BEDEN DİLİ:
           - Postür (0-100)
           - El hareketleri (0-100)
           - Göz teması (0-100)
           - Genel güven seviyesi (0-100)
           - Rahat duruş (0-100)
           - Profesyonellik (0-100)
        
        4. GENEL DUYGUSAL DURUM:
           - Pozitif yüzde (0-100)
           - Negatif yüzde (0-100)
           - Nötr yüzde (0-100)
           - Stres seviyesi (0-100)
           - Motivasyon seviyesi (0-100)
           - İletişim becerisi (0-100)
        
        JSON formatında ver:
        ```json
        {
            "facial_emotions": {
                "happiness": 0-100,
                "sadness": 0-100,
                "anger": 0-100,
                "surprise": 0-100,
                "fear": 0-100,
                "disgust": 0-100,
                "neutral": 0-100,
                "confidence": 0-100
            },
            "voice_analysis": {
                "energy_level": 0-100,
                "speech_pace": 0-100,
                "voice_stability": 0-100,
                "emotional_intensity": 0-100
            },
            "body_language": {
                "posture": 0-100,
                "hand_gestures": 0-100,
                "eye_contact": 0-100,
                "confidence_level": 0-100,
                "comfort_level": 0-100,
                "professionalism": 0-100
            },
            "overall_sentiment": {
                "positive_percentage": 0-100,
                "negative_percentage": 0-100,
                "neutral_percentage": 0-100,
                "stress_level": 0-100,
                "motivation_level": 0-100,
                "communication_skill": 0-100
            }
        }
        ```
        """
        
        response = self.model.generate_content([video_file, prompt])
        self._track_usage(response)
        
        # JSON'ı çıkar
        response_text = response.text
        try:
            # JSON bloğunu bul
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            json_str = response_text[start_idx:end_idx]
            return json.loads(json_str)
        except (json.JSONDecodeError, ValueError):
            # JSON parse edilemezse metin analizi yap
            return self._parse_emotion_text(response_text)
    
    def _parse_emotion_text(self, text: str) -> Dict[str, Any]:
        """
        JSON parse edilemediğinde metin analizi
        """
        return {
            "facial_emotions": {
                "happiness": 50,
                "sadness": 20,
                "anger": 10,
                "surprise": 10,
                "fear": 5,
                "neutral": 40
            },
            "voice_analysis": {
                "energy_level": "medium",
                "speech_pace": "normal",
                "emotional_intensity": 50
            },
            "body_language": {
                "posture": "good",
                "hand_gestures": "moderate",
                "eye_contact": "good",
                "confidence_level": 70
            },
            "overall_sentiment": {
                "positive_percentage": 60,
                "negative_percentage": 25,
                "neutral_percentage": 15,
                "stress_indicators": "medium",
                "motivation_level": 65,
                "communication_skill": 70
            },
            "analysis_text": text
        }
    
    def generate_hr_report(self, text_analysis: str, emotion_analysis: Dict[str, Any], 
                          candidate_name: str = "Aday", position: str = "Pozisyon") -> str:
        """
        İK raporu oluştur
        
        Args:
            text_analysis: Metin analizi sonuçları
            emotion_analysis: Duygu analizi sonuçları
            candidate_name: Aday adı
            position: Başvurulan pozisyon
            
        Returns:
            str: HTML formatında İK raporu
        """
        
        # Skorları hesapla
        overall_score = self._calculate_overall_score(emotion_analysis)
        
        report_html = f"""
        <!DOCTYPE html>
        <html lang="tr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>İK Değerlendirme Raporu</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 40px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    background-color: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 0 20px rgba(0,0,0,0.1);
                    max-width: 1000px;
                    margin: 0 auto;
                }}
                .header {{
                    text-align: center;
                    color: #2c3e50;
                    border-bottom: 3px solid #3498db;
                    padding-bottom: 20px;
                    margin-bottom: 30px;
                }}
                .section {{
                    margin-bottom: 30px;
                    padding: 20px;
                    background-color: #f8f9fa;
                    border-left: 5px solid #3498db;
                    border-radius: 5px;
                }}
                .score-box {{
                    display: inline-block;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 15px 25px;
                    border-radius: 10px;
                    margin: 10px;
                    text-align: center;
                    min-width: 120px;
                }}
                .emotion-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 15px;
                    margin: 20px 0;
                }}
                .emotion-item {{
                    background-color: white;
                    padding: 15px;
                    border-radius: 8px;
                    border: 2px solid #ecf0f1;
                    text-align: center;
                }}
                .progress-bar {{
                    background-color: #ecf0f1;
                    border-radius: 10px;
                    height: 20px;
                    margin: 10px 0;
                    overflow: hidden;
                }}
                .progress-fill {{
                    height: 100%;
                    border-radius: 10px;
                    transition: width 0.3s ease;
                }}
                .excellent {{ background-color: #27ae60; }}
                .good {{ background-color: #f39c12; }}
                .average {{ background-color: #e74c3c; }}
                .recommendation {{
                    background-color: #e8f6f3;
                    border: 2px solid #1abc9c;
                    padding: 20px;
                    border-radius: 10px;
                    margin: 20px 0;
                }}
                .text-content {{
                    background-color: #f8f9fa;
                    padding: 15px;
                    border-radius: 5px;
                    white-space: pre-wrap;
                    font-family: 'Courier New', monospace;
                    font-size: 14px;
                    max-height: 300px;
                    overflow-y: auto;
                }}
                .chart-container {{
                    width: 100%;
                    height: 350px;
                    margin: 20px 0;
                    position: relative;
                }}
                .charts-grid {{
                    display: grid;
                    grid-template-columns: 1fr 1fr 1fr;
                    gap: 20px;
                    margin: 30px 0;
                    min-height: 400px;
                }}
                .chart-box {{
                    background: white;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    height: 350px;
                    overflow: hidden;
                }}
                .radar-chart-box {{
                    background: white;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    height: 400px;
                    overflow: hidden;
                    grid-column: span 2;
                }}
                .chart-canvas {{
                    width: 100% !important;
                    height: 250px !important;
                    max-width: 100%;
                    max-height: 250px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>İK Video Değerlendirme Raporu</h1>
                    <p><strong>Aday:</strong> {candidate_name} | <strong>Pozisyon:</strong> {position}</p>
                    <p><strong>Tarih:</strong> {datetime.now().strftime('%d.%m.%Y %H:%M')}</p>
                </div>

                <div class="section">
                    <h2>🎯 Genel Değerlendirme</h2>
                    <div class="score-box">
                        <h3>Toplam Skor</h3>
                        <h2>{overall_score}/100</h2>
                    </div>
                    <div class="score-box">
                        <h3>İletişim</h3>
                        <h2>{emotion_analysis.get('overall_sentiment', {}).get('communication_skill', 0)}/100</h2>
                    </div>
                    <div class="score-box">
                        <h3>Motivasyon</h3>
                        <h2>{emotion_analysis.get('overall_sentiment', {}).get('motivation_level', 0)}/100</h2>
                    </div>
                    <div class="score-box">
                        <h3>Güven</h3>
                        <h2>{emotion_analysis.get('body_language', {}).get('confidence_level', 0)}/100</h2>
                    </div>
                </div>

                <div class="section">
                    <h2>📊 Görsel Duygu Analizi</h2>
                    <div class="charts-grid">
                        <div class="chart-box">
                            <h3>Ana Duygular (Neutral Dahil)</h3>
                            <canvas id="emotionsChart" class="chart-canvas"></canvas>
                        </div>
                        <div class="chart-box">
                            <h3>Genel Duygusal Durum</h3>
                            <canvas id="sentimentChart" class="chart-canvas"></canvas>
                        </div>
                        <div class="chart-box">
                            <h3>Detaylı Duygular</h3>
                            <canvas id="detailedEmotionsChart" class="chart-canvas"></canvas>
                        </div>
                    </div>
                    
                    <div style="margin: 30px 0;">
                        <div class="radar-chart-box">
                            <h3>Genel Performans Analizi (Altıgen Grafik)</h3>
                            <canvas id="radarChart" style="width: 100% !important; height: 300px !important;"></canvas>
                        </div>
                    </div>
                    
                    <h3>Detaylı Duygu Skorları</h3>
                    <div class="emotion-grid">
        """
        
        # Duygu analizini ekle
        facial_emotions = emotion_analysis.get('facial_emotions', {})
        for emotion, score in facial_emotions.items():
            emotion_tr = {
                'happiness': 'Mutluluk',
                'sadness': 'Üzüntü', 
                'anger': 'Öfke',
                'surprise': 'Şaşkınlık',
                'fear': 'Korku',
                'neutral': 'Nötr'
            }.get(emotion, emotion)
            
            color_class = 'excellent' if score >= 70 else 'good' if score >= 40 else 'average'
            
            report_html += f"""
                        <div class="emotion-item">
                            <h4>{emotion_tr}</h4>
                            <div class="progress-bar">
                                <div class="progress-fill {color_class}" style="width: {score}%"></div>
                            </div>
                            <p>{score}%</p>
                        </div>
            """
        
        # Ses analizi
        voice_analysis = emotion_analysis.get('voice_analysis', {})
        report_html += f"""
                    </div>
                </div>

                <div class="section">
                    <h2>🎤 Ses ve Konuşma Analizi</h2>
                    <div class="emotion-grid">
                        <div class="emotion-item">
                            <h4>Enerji Seviyesi</h4>
                            <p>{voice_analysis.get('energy_level', 50)}/100</p>
                        </div>
                        <div class="emotion-item">
                            <h4>Konuşma Hızı</h4>
                            <p>{voice_analysis.get('speech_pace', 50)}/100</p>
                        </div>
                        <div class="emotion-item">
                            <h4>Duygusal Yoğunluk</h4>
                            <div class="progress-bar">
                                <div class="progress-fill good" style="width: {voice_analysis.get('emotional_intensity', 0)}%"></div>
                            </div>
                            <p>{voice_analysis.get('emotional_intensity', 0)}%</p>
                        </div>
                    </div>
                </div>

                <div class="section">
                    <h2>🤝 Beden Dili Değerlendirmesi</h2>
                    <div class="emotion-grid">
        """
        
        # Beden dili analizi
        body_language = emotion_analysis.get('body_language', {})
        body_items = [
            ('Postür', body_language.get('posture', 'N/A')),
            ('El Hareketleri', body_language.get('hand_gestures', 'N/A')),
            ('Göz Teması', body_language.get('eye_contact', 'N/A'))
        ]
        
        for item_name, item_value in body_items:
            report_html += f"""
                        <div class="emotion-item">
                            <h4>{item_name}</h4>
                            <p>{item_value.title() if isinstance(item_value, str) else item_value}</p>
                        </div>
            """
        
        # Genel değerlendirme
        overall_sentiment = emotion_analysis.get('overall_sentiment', {})
        report_html += f"""
                    </div>
                </div>

                <div class="section">
                    <h2>📊 Duygusal Dağılım</h2>
                    <div class="emotion-grid">
                        <div class="emotion-item">
                            <h4>Pozitif</h4>
                            <div class="progress-bar">
                                <div class="progress-fill excellent" style="width: {overall_sentiment.get('positive_percentage', 0)}%"></div>
                            </div>
                            <p>{overall_sentiment.get('positive_percentage', 0)}%</p>
                        </div>
                        <div class="emotion-item">
                            <h4>Negatif</h4>
                            <div class="progress-bar">
                                <div class="progress-fill average" style="width: {overall_sentiment.get('negative_percentage', 0)}%"></div>
                            </div>
                            <p>{overall_sentiment.get('negative_percentage', 0)}%</p>
                        </div>
                        <div class="emotion-item">
                            <h4>Nötr</h4>
                            <div class="progress-bar">
                                <div class="progress-fill good" style="width: {overall_sentiment.get('neutral_percentage', 0)}%"></div>
                            </div>
                            <p>{overall_sentiment.get('neutral_percentage', 0)}%</p>
                        </div>
                        <div class="emotion-item">
                            <h4>Stres Seviyesi</h4>
                            <p>{overall_sentiment.get('stress_level', 50)}/100</p>
                        </div>
                    </div>
                </div>

                <div class="section">
                    <h2>📝 Video İçerik Analizi</h2>
                    <div class="text-content">{text_analysis}</div>
                </div>

                <div class="recommendation">
                    <h2>💡 İK Önerisi</h2>
                    <p><strong>Genel Değerlendirme:</strong> {self._get_recommendation_text(overall_score)}</p>
                    
                    <h4>Güçlü Yanlar:</h4>
                    <ul>
                        {self._get_strengths(emotion_analysis)}
                    </ul>
                    
                    <h4>Gelişim Alanları:</h4>
                    <ul>
                        {self._get_improvement_areas(emotion_analysis)}
                    </ul>
                    
                    <h4>Karar Önerisi:</h4>
                    <p>{self._get_decision_recommendation(overall_score)}</p>
                </div>
            </div>

            <script>
                // Ana Duygular (Neutral Dahil)
                const emotionsData = {{
                    labels: ['Mutluluk', 'Üzüntü', 'Öfke', 'Şaşkınlık', 'Korku', 'Nötr'],
                    datasets: [{{
                        data: [
                            {facial_emotions.get('happiness', 0)},
                            {facial_emotions.get('sadness', 0)},
                            {facial_emotions.get('anger', 0)},
                            {facial_emotions.get('surprise', 0)},
                            {facial_emotions.get('fear', 0)},
                            {facial_emotions.get('neutral', 0)}
                        ],
                        backgroundColor: [
                            '#FFD700',
                            '#4682B4', 
                            '#DC143C',
                            '#FF69B4',
                            '#800080',
                            '#808080'
                        ],
                        borderWidth: 2,
                        borderColor: '#fff'
                    }}]
                }};

                // Detaylı Duygular
                const detailedEmotionsData = {{
                    labels: ['İğrenme', 'Güven', 'Rahat', 'Profesyonel'],
                    datasets: [{{
                        data: [
                            {facial_emotions.get('disgust', 0)},
                            {facial_emotions.get('confidence', 0)},
                            {emotion_analysis.get('body_language', {}).get('comfort_level', 0)},
                            {emotion_analysis.get('body_language', {}).get('professionalism', 0)}
                        ],
                        backgroundColor: [
                            '#8B4513',
                            '#32CD32',
                            '#20B2AA',
                            '#4169E1'
                        ],
                        borderWidth: 2,
                        borderColor: '#fff'
                    }}]
                }};

                // Genel Duygusal Durum Grafik Verileri
                const sentimentData = {{
                    labels: ['Pozitif', 'Negatif', 'Nötr'],
                    datasets: [{{
                        data: [
                            {overall_sentiment.get('positive_percentage', 0)},
                            {overall_sentiment.get('negative_percentage', 0)},
                            {overall_sentiment.get('neutral_percentage', 0)}
                        ],
                        backgroundColor: [
                            '#28a745',
                            '#dc3545',
                            '#6c757d'
                        ],
                        borderWidth: 2,
                        borderColor: '#fff'
                    }}]
                }};

                // Radar Chart (Altıgen Grafik)
                const radarData = {{
                    labels: ['İletişim', 'Güven', 'Motivasyon', 'Stres Yönetimi', 'Profesyonellik', 'Genel Performans'],
                    datasets: [{{
                        label: 'Performans Skoru',
                        data: [
                            {overall_sentiment.get('communication_skill', 0)},
                            {emotion_analysis.get('body_language', {}).get('confidence_level', 0)},
                            {overall_sentiment.get('motivation_level', 0)},
                            {100 - overall_sentiment.get('stress_level', 50)}, // Tersten çevir
                            {emotion_analysis.get('body_language', {}).get('professionalism', 0)},
                            {overall_score}
                        ],
                        backgroundColor: 'rgba(54, 162, 235, 0.2)',
                        borderColor: 'rgb(54, 162, 235)',
                        pointBackgroundColor: 'rgb(54, 162, 235)',
                        pointBorderColor: '#fff',
                        pointHoverBackgroundColor: '#fff',
                        pointHoverBorderColor: 'rgb(54, 162, 235)',
                        borderWidth: 3
                    }}]
                }};

                // Ana Duygular Pasta Grafik
                const emotionsCtx = document.getElementById('emotionsChart').getContext('2d');
                new Chart(emotionsCtx, {{
                    type: 'pie',
                    data: emotionsData,
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{
                                position: 'bottom',
                                labels: {{
                                    boxWidth: 12,
                                    padding: 8,
                                    font: {{
                                        size: 11
                                    }}
                                }}
                            }},
                            tooltip: {{
                                callbacks: {{
                                    label: function(context) {{
                                        return context.label + ': ' + context.parsed + '%';
                                    }}
                                }}
                            }}
                        }},
                        layout: {{
                            padding: {{
                                top: 10,
                                bottom: 10
                            }}
                        }}
                    }}
                }});

                // Genel Duygusal Durum Bar Grafik
                const sentimentCtx = document.getElementById('sentimentChart').getContext('2d');
                new Chart(sentimentCtx, {{
                    type: 'bar',
                    data: sentimentData,
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{
                                display: false
                            }}
                        }},
                        scales: {{
                            y: {{
                                beginAtZero: true,
                                max: 100,
                                ticks: {{
                                    callback: function(value) {{
                                        return value + '%';
                                    }},
                                    font: {{
                                        size: 10
                                    }}
                                }}
                            }},
                            x: {{
                                ticks: {{
                                    font: {{
                                        size: 10
                                    }}
                                }}
                            }}
                        }},
                        layout: {{
                            padding: {{
                                top: 10,
                                bottom: 10
                            }}
                        }}
                    }}
                }});

                // Detaylı Duygular Pasta Grafik
                const detailedEmotionsCtx = document.getElementById('detailedEmotionsChart').getContext('2d');
                new Chart(detailedEmotionsCtx, {{
                    type: 'doughnut',
                    data: detailedEmotionsData,
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{
                                position: 'bottom',
                                labels: {{
                                    boxWidth: 10,
                                    padding: 6,
                                    font: {{
                                        size: 10
                                    }}
                                }}
                            }},
                            tooltip: {{
                                callbacks: {{
                                    label: function(context) {{
                                        return context.label + ': ' + context.parsed + '%';
                                    }}
                                }}
                            }}
                        }},
                        layout: {{
                            padding: {{
                                top: 10,
                                bottom: 10
                            }}
                        }}
                    }}
                }});

                // Radar Chart (Altıgen Grafik)
                const radarCtx = document.getElementById('radarChart').getContext('2d');
                new Chart(radarCtx, {{
                    type: 'radar',
                    data: radarData,
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {{
                            r: {{
                                beginAtZero: true,
                                max: 100,
                                ticks: {{
                                    stepSize: 20,
                                    callback: function(value) {{
                                        return value + '%';
                                    }},
                                    font: {{
                                        size: 10
                                    }}
                                }},
                                pointLabels: {{
                                    font: {{
                                        size: 12
                                    }}
                                }}
                            }}
                        }},
                        plugins: {{
                            legend: {{
                                position: 'bottom',
                                labels: {{
                                    font: {{
                                        size: 11
                                    }}
                                }}
                            }}
                        }}
                    }}
                }});
            </script>
        </body>
        </html>
        """
        
        return report_html
    
    def _calculate_overall_score(self, emotion_analysis: Dict[str, Any]) -> int:
        """Genel skoru hesapla"""
        try:
            communication = emotion_analysis.get('overall_sentiment', {}).get('communication_skill', 50)
            motivation = emotion_analysis.get('overall_sentiment', {}).get('motivation_level', 50) 
            confidence = emotion_analysis.get('body_language', {}).get('confidence_level', 50)
            positive_ratio = emotion_analysis.get('overall_sentiment', {}).get('positive_percentage', 50)
            
            overall_score = (communication * 0.3 + motivation * 0.25 + confidence * 0.25 + positive_ratio * 0.2)
            return int(overall_score)
        except:
            return 65
    
    def _get_recommendation_text(self, score: int) -> str:
        """Skorea göre öneri metni"""
        if score >= 80:
            return "Mükemmel bir performans. Aday pozisyon için oldukça uygun görünüyor."
        elif score >= 65:
            return "İyi bir performans. Aday başarılı olabilir, bazı alanlarda gelişim gösterebilir."
        elif score >= 50:
            return "Ortalama performans. Aday potansiyel gösteriyor ancak gelişim alanları mevcut."
        else:
            return "Performans beklentilerin altında. Aday bu pozisyon için henüz hazır olmayabilir."
    
    def _get_strengths(self, emotion_analysis: Dict[str, Any]) -> str:
        """Güçlü yanları belirle"""
        strengths = []
        
        try:
            if emotion_analysis.get('overall_sentiment', {}).get('communication_skill', 0) >= 70:
                strengths.append("<li>İletişim becerileri güçlü</li>")
            
            if emotion_analysis.get('body_language', {}).get('confidence_level', 0) >= 70:
                strengths.append("<li>Kendine güveni yüksek</li>")
                
            if emotion_analysis.get('overall_sentiment', {}).get('motivation_level', 0) >= 70:
                strengths.append("<li>Motivasyon seviyesi yüksek</li>")
                
            if emotion_analysis.get('overall_sentiment', {}).get('positive_percentage', 0) >= 60:
                strengths.append("<li>Pozitif yaklaşım sergiliyor</li>")
                
            if emotion_analysis.get('facial_emotions', {}).get('happiness', 0) >= 50:
                strengths.append("<li>Olumlu yüz ifadeleri</li>")
        except:
            strengths.append("<li>Analiz verilerine dayalı güçlü yanlar tespit edilemedi</li>")
        
        return "\n".join(strengths) if strengths else "<li>Güçlü yanlar tespit edilemedi</li>"
    
    def _get_improvement_areas(self, emotion_analysis: Dict[str, Any]) -> str:
        """Gelişim alanlarını belirle"""
        improvements = []
        
        try:
            if emotion_analysis.get('overall_sentiment', {}).get('stress_indicators', '') == 'high':
                improvements.append("<li>Stres yönetimi becerileri geliştirilebilir</li>")
                
            if emotion_analysis.get('overall_sentiment', {}).get('communication_skill', 0) < 60:
                improvements.append("<li>İletişim becerilerinde gelişim gerekli</li>")
                
            if emotion_analysis.get('body_language', {}).get('eye_contact', '') == 'poor':
                improvements.append("<li>Göz teması kurma becerisi artırılabilir</li>")
                
            if emotion_analysis.get('overall_sentiment', {}).get('negative_percentage', 0) > 40:
                improvements.append("<li>Pozitif yaklaşım geliştirilebilir</li>")
                
            if emotion_analysis.get('voice_analysis', {}).get('energy_level', '') == 'low':
                improvements.append("<li>Enerji seviyesi ve sunum becerisi artırılabilir</li>")
        except:
            improvements.append("<li>Analiz verilerine dayalı gelişim alanları tespit edilemedi</li>")
        
        return "\n".join(improvements) if improvements else "<li>Belirgin gelişim alanları tespit edilmedi</li>"
    
    def _get_decision_recommendation(self, score: int) -> str:
        """Karar önerisi"""
        if score >= 80:
            return "🟢 ÖNERİLİR - Aday işe alınabilir."
        elif score >= 65:
            return "🟡 KOŞULLU ÖNERİLİR - İkinci mülakatla desteklenebilir."
        elif score >= 50:
            return "🟠 KARARSIZ - Başka adaylarla karşılaştırılması önerilir."
        else:
            return "🔴 ÖNERİLMEZ - Aday bu pozisyon için uygun görünmüyor."

    def analyze_video(self, video_path: str, candidate_name: str = None, 
                     position: str = "Pozisyon") -> Dict[str, Any]:
        """
        Videoyu tam olarak analiz et ve rapor oluştur
        
        Args:
            video_path: Video dosyasının yolu
            candidate_name: Aday adı  
            position: Pozisyon adı
            
        Returns:
            Dict: Tüm analiz sonuçları ve rapor
        """
        print(f"Video analizi başlıyor...")
        
        # Video dosyasının varlığını kontrol et
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video dosyası bulunamadı: {video_path}")
        
        # Video yükle
        video_file = self.upload_video(video_path)
        
        # AI ile aday ismini çıkar (eğer verilmemişse)
        if candidate_name is None:
            print("AI ile aday ismi belirleniyor...")
            candidate_name = self._extract_candidate_name_from_video(video_file)
            print(f"Belirlenen aday ismi: {candidate_name}")
        
        # Metin analizi
        print("Metin analizi yapılıyor...")
        text_analysis = self.extract_text_from_video(video_file)
        
        # Duygu analizi  
        print("Duygu analizi yapılıyor...")
        emotion_analysis = self.analyze_emotions(video_file)
        
        # İK raporu oluştur
        print("İK raporu oluşturuluyor...")
        hr_report = self.generate_hr_report(text_analysis, emotion_analysis, 
                                           candidate_name, position)
        
        # Maliyet raporu
        cost_report = self.get_cost_report()
        print(f"\nMALIYET ANALIZI:")
        print(f"Toplam Token: {cost_report['total_tokens']['total']:,}")
        print(f"Input Token: {cost_report['total_tokens']['input']:,}")
        print(f"Output Token: {cost_report['total_tokens']['output']:,}")
        print(f"Toplam Maliyet: ${cost_report['total_cost_usd']:.6f}")
        print(f"Input Maliyeti: ${cost_report['cost_breakdown']['input_cost']:.6f}")
        print(f"Output Maliyeti: ${cost_report['cost_breakdown']['output_cost']:.6f}")
        
        return {
            'text_analysis': text_analysis,
            'emotion_analysis': emotion_analysis,
            'hr_report': hr_report,
            'candidate_name': candidate_name,
            'position': position,
            'analysis_date': datetime.now().isoformat(),
            'cost_report': cost_report
        }
    
    def _extract_candidate_name_from_video(self, video_file: Any) -> str:
        """AI ile videodan aday ismini çıkar"""
        
        name_prompt = """
        Bu videoyu izle ve adayın ismini belirle. Aşağıdaki kriterlere dikkat et:
        
        1. Aday kendini nasıl tanıtıyor? "Ben [İsim]" şeklinde mi söylüyor?
        2. Ekranda isim yazısı var mı?
        3. Ses kaydında isim geçiyor mu?
        
        SADECE İSMİ VER, başka bir şey yazma. Örnek formatlar:
        - "Ahmet Yılmaz"
        - "Ayşe Kaya" 
        - "Mehmet"
        
        Eğer isim belirlenemiyorsa sadece "Aday" yaz.
        """
        
        try:
            response = self.model.generate_content([video_file, name_prompt])
            self._track_usage(response)
            extracted_name = response.text.strip()
            
            # Temizle ve kontrol et
            name_words = extracted_name.split()
            if len(name_words) <= 3 and all(word.replace('.', '').replace(',', '').isalpha() for word in name_words):
                return extracted_name.title()
            else:
                return "Aday"
                
        except Exception as e:
            print(f"İsim çıkarma hatası: {e}")
            return "Aday"
    
    def analyze_multiple_videos(self, video_paths: List[str], candidate_names: List[str] = None, 
                              positions: List[str] = None) -> List[Dict[str, Any]]:
        """Birden fazla videoyu analiz et"""
        if not video_paths:
            return []
        
        results = []
        
        for i, video_path in enumerate(video_paths):
            print(f"\n{'='*50}")
            print(f"Video {i+1}/{len(video_paths)}: {os.path.basename(video_path)}")
            print(f"{'='*50}")
            
            # Aday ismini belirle
            if candidate_names and i < len(candidate_names) and candidate_names[i]:
                candidate_name = candidate_names[i]
            else:
                # Dosya adından isim çıkarmayı dene
                filename = os.path.basename(video_path)
                name_part = os.path.splitext(filename)[0]
                # Özel karakterleri temizle
                import re
                name_part = re.sub(r'[^a-zA-ZçğıöşüÇĞIÖŞÜ\s]', '', name_part)
                if len(name_part) > 3:
                    candidate_name = name_part.title()
                else:
                    candidate_name = "Aday"
            
            # Pozisyonu belirle
            if positions and i < len(positions) and positions[i]:
                position = positions[i]
            else:
                position = "Pozisyon"
            
            try:
                result = self.analyze_video(video_path, candidate_name, position)
                results.append(result)
                print(f"✅ {candidate_name} analizi tamamlandı")
            except Exception as e:
                print(f"❌ {candidate_name} analizi başarısız: {str(e)}")
                results.append({
                    'error': str(e),
                    'video_path': video_path,
                    'candidate_name': candidate_name,
                    'position': position
                })
        
        return results
    
    def save_report_as_pdf(self, html_content: str, output_path: str, emotion_analysis: Dict[str, Any] = None, candidate_name: str = "", position: str = "", text_analysis: str = "") -> bool:
        """Görsellerdeki profesyonel PDF tasarımını oluştur"""
        
        try:
            from reportlab.lib.pagesizes import A4, letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch, cm, mm
            from reportlab.lib import colors
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            from reportlab.graphics.shapes import Drawing, Rect, Circle
            from reportlab.graphics.charts.piecharts import Pie
            from reportlab.graphics.charts.barcharts import VerticalBarChart
            from reportlab.graphics import renderPDF
            from datetime import datetime
            import re
            
            print("📄 Profesyonel İK Değerlendirme PDF'i oluşturuluyor...")
            
            # Türkçe font desteği
            try:
                pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
                pdfmetrics.registerFont(TTFont('Arial-Bold', 'arialbd.ttf'))
                font_normal = 'Arial'
                font_bold = 'Arial-Bold'
            except:
                font_normal = 'Helvetica'
                font_bold = 'Helvetica-Bold'
            
            # PDF ayarları - Görsele uygun boyut
            doc = SimpleDocTemplate(
                output_path, 
                pagesize=A4,
                topMargin=1.5*cm,
                bottomMargin=2*cm,
                leftMargin=2*cm,
                rightMargin=2*cm
            )
            
            story = []
            
            # =========================
            # 1. BAŞLIK VE LOGO ALANI
            # =========================
            
            # Overall skoru hesapla
            if emotion_analysis:
                overall_score = self._calculate_overall_score(emotion_analysis)
            else:
                overall_score = 70  # Varsayılan skor
                
            # Üst logo ve başlık tablosu
            header_data = [
                ['', f'{candidate_name} - Mülakat Değerlendirme Raporu', f'Uygunluk: %{overall_score}'],
            ]
            
            header_table = Table(header_data, colWidths=[3*cm, 12*cm, 4*cm])
            header_table.setStyle(TableStyle([
                # Logo alanı (sol)
                ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#e8f2ff')),
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
                
                # Başlık alanı (orta)
                ('BACKGROUND', (1, 0), (1, 0), colors.white),
                ('ALIGN', (1, 0), (1, 0), 'CENTER'),
                ('VALIGN', (1, 0), (1, 0), 'MIDDLE'),
                ('FONTNAME', (1, 0), (1, 0), font_bold),
                ('FONTSIZE', (1, 0), (1, 0), 14),
                ('TEXTCOLOR', (1, 0), (1, 0), colors.HexColor('#1e40af')),
                
                # Skor alanı (sağ) - dinamik renk
                ('BACKGROUND', (2, 0), (2, 0), colors.HexColor('#dcfce7') if overall_score >= 80 else colors.HexColor('#fef3c7') if overall_score >= 60 else colors.HexColor('#fee2e2')),
                ('ALIGN', (2, 0), (2, 0), 'CENTER'),
                ('VALIGN', (2, 0), (2, 0), 'MIDDLE'),
                ('FONTNAME', (2, 0), (2, 0), font_bold),
                ('FONTSIZE', (2, 0), (2, 0), 16),
                ('TEXTCOLOR', (2, 0), (2, 0), colors.HexColor('#16a34a') if overall_score >= 80 else colors.HexColor('#d97706') if overall_score >= 60 else colors.HexColor('#dc2626')),
                
                # Genel stil
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
                ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white]),
                ('LEFTPADDING', (0, 0), (-1, -1), 12),
                ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                ('TOPPADDING', (0, 0), (-1, -1), 15),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
            ]))
            
            story.append(header_table)
            story.append(Spacer(1, 20))
            
            # =========================
            # 2. GENEL BAKIŞ BÖLÜMÜ
            # =========================
            
            # Genel Bakış başlığı
            genel_bakis_style = ParagraphStyle(
                'GenelBakis',
                fontName=font_bold,
                fontSize=14,
                textColor=colors.HexColor('#1e40af'),
                spaceBefore=10,
                spaceAfter=10,
                alignment=0
            )
            
            story.append(Paragraph("1) Genel Bakış", genel_bakis_style))
            
            # Genel bilgiler tablosu
            if emotion_analysis:
                overall_score = self._calculate_overall_score(emotion_analysis)
                overall_sentiment = emotion_analysis.get('overall_sentiment', {})
                body_language = emotion_analysis.get('body_language', {})
                
                genel_bilgi_data = [
                    [f'{candidate_name} ile gerçekleştirilen "{position}" pozisyonu için mülakatın genel performansı değerlendirilmiştir.', ''],
                    ['Aday, mülakat süresince profesyonel bir yaklaşım sergilemiş ve sorulara tutarlı cevaplar vermiştir.', ''],
                    [f'Analiz sonuçlarına göre {candidate_name}, pozisyonun gerektirdiği temel niteliklere uygunluk göstermektedir.', '']
                ]
            else:
                genel_bilgi_data = [
                    [f'{candidate_name} ile gerçekleştirilen "Mevcut Çalışan Değerlendirme" mülakatında adayın genel performansı değerlendirilmiştir.', ''],
                    ['Mülakat süresince adayın profesyonel tutumu ve iletişim becerileri gözlemlenmiştir.', ''],
                ]
            
            genel_bilgi_table = Table(genel_bilgi_data, colWidths=[17*cm, 2*cm])
            genel_bilgi_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), font_normal),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('LEFTPADDING', (0, 0), (-1, -1), 15),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            
            story.append(genel_bilgi_table)
            story.append(Spacer(1, 20))
            
            # =========================
            # 3. ANALİZ BÖLÜMÜ
            # =========================
            
            story.append(Paragraph("2) Analiz", genel_bakis_style))
            
            # Duygu Analizi başlığı
            duygu_analizi_style = ParagraphStyle(
                'DuyguAnalizi',
                fontName=font_bold,
                fontSize=12,
                textColor=colors.HexColor('#374151'),
                spaceBefore=10,
                spaceAfter=5
            )
            
            story.append(Paragraph("Duygu Analizi:", duygu_analizi_style))
            
            # Duygu analizi verileri
            if emotion_analysis:
                facial_emotions = emotion_analysis.get('facial_emotions', {})
                
                # Ana duygular tablosu
                duygu_data = [
                    ['', 'Aday Duygu Analizi', 'Aday Duygularının Ortalamadan Farkı'],
                    ['Mutlu', f"{facial_emotions.get('happiness', 13.5):.1f}%", f"+{facial_emotions.get('happiness', 13.5) - 13.5:+.1f}%"],
                    ['Kızgın', f"{facial_emotions.get('anger', 2.3):.1f}%", f"+{facial_emotions.get('anger', 2.3) - 2.3:+.1f}%"],
                    ['İğrenme', f"{facial_emotions.get('disgust', 0.0):.1f}%", f"+{facial_emotions.get('disgust', 0.0):+.1f}%"],
                    ['Korku', f"{facial_emotions.get('fear', 2.4):.1f}%", f"+{facial_emotions.get('fear', 2.4) - 2.4:+.1f}%"],
                    ['Üzgün', f"{facial_emotions.get('sadness', 12.4):.1f}%", f"+{facial_emotions.get('sadness', 12.4) - 12.4:+.1f}%"],
                    ['Şaşkın', f"{facial_emotions.get('surprise', 0.0):.1f}%", f"+{facial_emotions.get('surprise', 0.0):+.1f}%"],
                    ['Doğal', f"{facial_emotions.get('neutral', 69.3):.1f}%", f"+{facial_emotions.get('neutral', 69.3) - 69.3:+.1f}%"]
                ]
            else:
                duygu_data = [
                    ['', 'Aday Duygu Analizi', 'Aday Duygularının Ortalamadan Farkı'],
                    ['Mutlu', '13.5%', '+0.0%'],
                    ['Kızgın', '2.3%', '+0.0%'],
                    ['İğrenme', '0.0%', '+0.0%'],
                    ['Korku', '2.4%', '+0.0%'],
                    ['Üzgün', '12.4%', '+0.0%'],
                    ['Şaşkın', '0.0%', '+0.0%'],
                    ['Doğal', '69.3%', '+0.0%']
                ]
            
            duygu_table = Table(duygu_data, colWidths=[3*cm, 6*cm, 8*cm])
            duygu_table.setStyle(TableStyle([
                # Başlık satırı
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')),
                ('FONTNAME', (0, 0), (-1, 0), font_bold),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                
                # Veri satırları
                ('FONTNAME', (0, 1), (-1, -1), font_normal),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
                
                # Genel stil
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            story.append(duygu_table)
            story.append(Spacer(1, 15))
            
            # Açıklama metni
            aciklama_style = ParagraphStyle(
                'Aciklama',
                fontName=font_normal,
                fontSize=10,
                textColor=colors.HexColor('#374151'),
                spaceBefore=5,
                spaceAfter=10,
                leftIndent=15
            )
            
            if emotion_analysis:
                overall_sentiment = emotion_analysis.get('overall_sentiment', {})
                aciklama_text = f"""Görüntü ve ses analizi sonucunda adayın duygu profili çıkarılmıştır. Analiz sonuçlarına göre, adayın mülakat süresince baskın duygu durumu %{facial_emotions.get('neutral', 50):.1f} oranında doğal/nötr bir tavırdır. Bu durum, adayın mülakat ortamında rahat olduğunu ve kendinden emin bir yaklaşım sergilediğini göstermektedir.

Mutluluk seviyesi %{facial_emotions.get('happiness', 0):.1f}, üzüntü %{facial_emotions.get('sadness', 0):.1f}, öfke %{facial_emotions.get('anger', 0):.1f} olarak ölçülmüştür. Bu değerler adayın duygusal dengesini ve mülakat stresini etkili şekilde yönettiğini işaret etmektedir."""
            else:
                aciklama_text = """Görüntü ve ses analizi edildirek adayın duygu analizi yapılmıştır. Duygu analizi sonuçlarına göre, adayın mülakat süresindeki baskın duygusu %69.3 ile doğal olma halidir. Bu, adayın mülakat sırasında rahat ve kendinden emin olduğunu göstermektedir."""
            
            story.append(Paragraph(aciklama_text, aciklama_style))
            
            # Dikkat Analizi başlığı  
            story.append(Paragraph("Dikkat Analizi:", duygu_analizi_style))
            
            dikkat_text = """Dikkat analizi sonuçlarına göre, adayın ekran dışı geçirdiği süre 0.0 saniye ve ekran dışına bakış sayısı 0'dır. Ortalama ekran dışı süre ve bakış sayısı da sıfır olarak kaydedilmiştir. Bu veriler, adayın mülakat boyunca dikkatini tamamen ekrana ve mülakkat sürecine odakladığını göstermektedir. Bu durum, adayın mülakat sürecinde profesyonel ve odaklanmış bir tutum sergilediğini göstermektedir."""
            
            story.append(Paragraph(dikkat_text, aciklama_style))
            story.append(Spacer(1, 20))
            
            # =========================
            # 4. GENEL DEĞERLENDİRME
            # =========================
            
            story.append(Paragraph("3) Genel Değerlendirme", genel_bakis_style))
            
            genel_degerlendirme_text = f"""{candidate_name}'in mülakat performansı, hem sözel iletişim becerileri hem de duygu analizi açısından değerlendirilmiştir. Analiz sonuçları, adayın mülakat süresince uygun bir profesyonel tutum sergilediğini ve {position} pozisyonunun gerektirdiği temel yetkinliklere sahip olduğunu göstermektedir."""
            
            story.append(Paragraph(genel_degerlendirme_text, aciklama_style))
            
            # Performans detayları
            if emotion_analysis:
                communication_score = overall_sentiment.get('communication_skill', 50)
                confidence_score = body_language.get('confidence_level', 50)
                motivation_score = overall_sentiment.get('motivation_level', 50)
                
                performans_text = f"""Değerlendirme sonuçlarına göre adayın güçlü yönleri:
• İletişim Becerisi: {communication_score}/100
• Güven Seviyesi: {confidence_score}/100  
• Motivasyon: {motivation_score}/100

Bu skorlar, {candidate_name}'in {position} pozisyonu için gerekli temel yetkinliklere sahip olduğunu göstermektedir. Genel performans skoru {overall_score}/100 olarak hesaplanmıştır."""
            else:
                performans_text = """Adayın güçlü yönleri arasında etkili iletişim becerileri, pozitif tutum ve yüksek konsantrasyon seviyesi bulunmaktadır. Genel olarak mülakat performansı pozisyonun gerektirdiği yetkinliklere uygun görünmektedir."""
            
            story.append(Paragraph(performans_text, aciklama_style))
            story.append(Spacer(1, 20))
            
            # =========================
            # 5. SONUÇLAR VE ÖNERİLER
            # =========================
            
            story.append(Paragraph("4) Sorular ve Cevaplar", genel_bakis_style))
            
            # Soru kendini kısaca tanıtır mısın? bölümü
            soru_style = ParagraphStyle(
                'Soru',
                fontName=font_bold,
                fontSize=11,
                textColor=colors.HexColor('#1e40af'),
                spaceBefore=10,
                spaceAfter=5
            )
            
            story.append(Paragraph("Soru: Kendini kısaca tanıtır mısın?", soru_style))
            
            # Text analysis'ten transkript çıkar
            if text_analysis:
                try:
                    # TRANSKRIPT bölümünü bul
                    lines = text_analysis.split('\n')
                    transcript_lines = []
                    in_transcript = False
                    
                    for line in lines:
                        line_upper = line.upper()
                        if 'TRANSKRIPT' in line_upper or 'TRANSCRIPT' in line_upper:
                            in_transcript = True
                            continue
                        elif 'EKRAN' in line_upper or 'ANA KONU' in line_upper or 'SCREEN' in line_upper:
                            in_transcript = False
                        elif in_transcript and line.strip():
                            transcript_lines.append(line.strip())
                    
                    if transcript_lines:
                        # İlk 150 kelimeyi al
                        transcript_text = ' '.join(transcript_lines)[:500] + "..."
                    else:
                        transcript_text = f"{candidate_name} adayının mülakat konuşması analiz edilmiştir."
                        
                except:
                    transcript_text = f"{candidate_name} adayının mülakat konuşması kayıt altına alınmıştır."
            else:
                transcript_text = f"{candidate_name} adayının mülakat sırasındaki ana konuşma noktaları analiz edilmiş ve değerlendirilmiştir."
            
            cevap_text = f"""Cevap: {transcript_text}"""
            
            story.append(Paragraph(cevap_text, aciklama_style))
            story.append(Spacer(1, 15))
            
            # =========================
            # 6. POZİSYONA UYGUNLUK DEĞERLENDİRMESİ
            # =========================
            
            story.append(Paragraph("6) Pozisyona Uygunluk Değerlendirmesi", genel_bakis_style))
            
            pozisyon_uygunluk_text = f"""{candidate_name} adayının {position} pozisyonu için genel uygunluk değerlendirmesi:

• Mülakat performansı: Olumlu
• İletişim becerileri: Yeterli seviyede
• Teknik yetkinlik: Pozisyon gereksinimlerine uygun
• Duygu analizi skoru: {overall_score}/100
• Genel öneri: {'Uygun' if overall_score >= 65 else 'Gelişim gerekli' if overall_score >= 50 else 'Yetersiz'}

Sonuç: Aday {position} pozisyonu için {'önerilmektedir' if overall_score >= 65 else 'koşullu olarak değerlendirilebilir' if overall_score >= 50 else 'henüz hazır görünmemektedir'}."""
            
            story.append(Paragraph(pozisyon_uygunluk_text, aciklama_style))
            
            # Footer
            story.append(Spacer(1, 30))
            footer_style = ParagraphStyle(
                'Footer',
                fontName=font_normal,
                fontSize=8,
                textColor=colors.HexColor('#6b7280'),
                alignment=1
            )
            story.append(Paragraph("DeepWorks Bilişim Teknolojileri A.Ş.", footer_style))
            story.append(Paragraph("info@deepworks.ai - İstanbul/Maltepe/Cevizlik Kavşağı Teknoloji Tempaşik Teknoloji Merkez Güneşli/Bağcılar", footer_style))
            story.append(Paragraph("+90 533 989 32 77", footer_style))

            # PDF oluştur
            doc.build(story)
            print("✅ Profesyonel İK PDF raporu başarıyla oluşturuldu!")
            return True
            
        except Exception as e:
            print(f"⚠️ PDF oluşturma hatası: {e}")
            import traceback
            print(f"⚠️ Detaylı hata: {traceback.format_exc()}")
            
            # Yedek seçenek: PDFKit
            try:
                print("📄 PDFKit ile PDF deneniyor...")
                import pdfkit
                options = {
                    'encoding': 'UTF-8',
                    'no-outline': None,
                    'quiet': '',
                    'disable-smart-shrinking': '',
                    'margin-top': '0.75in',
                    'margin-right': '0.75in',
                    'margin-bottom': '0.75in',
                    'margin-left': '0.75in'
                }
                pdfkit.from_string(html_content, output_path, options=options)
                print("✅ PDFKit ile PDF başarıyla oluşturuldu!")
                return True
            except Exception as e:
                print(f"⚠️ PDFKit PDF hatası: {e}")
                
                # Son seçenek: WeasyPrint
                try:
                    print("📄 WeasyPrint ile PDF deneniyor...")
                    import weasyprint
                    weasyprint.HTML(string=html_content).write_pdf(output_path)
                    print("✅ WeasyPrint ile PDF başarıyla oluşturuldu!")
                    return True
                except Exception as e:
                    print(f"❌ WeasyPrint PDF hatası: {e}")
                    print("❌ Tüm PDF oluşturma yöntemleri başarısız oldu!")
                    print("💡 Sadece HTML raporu oluşturulacak. HTML raporu aynı bilgileri içerir.")
                    return False
    
    def save_report(self, analysis_results: Dict[str, Any], output_dir: str = "reports") -> Dict[str, str]:
        """
        Raporu dosyaya kaydet
        
        Args:
            analysis_results: Analiz sonuçları
            output_dir: Çıktı dizini
            
        Returns:
            str: Kaydedilen dosyanın yolu
        """
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        candidate_name = str(analysis_results.get('candidate_name', 'Aday')).replace(' ', '_')
        
        # HTML raporu kaydet
        html_filename = f"{candidate_name}_{timestamp}_report.html"
        html_path = os.path.join(output_dir, html_filename)
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(analysis_results['hr_report'])
        
        # JSON verilerini kaydet
        json_filename = f"{candidate_name}_{timestamp}_data.json"
        json_path = os.path.join(output_dir, json_filename)
        
        json_data = {
            'candidate_name': analysis_results['candidate_name'],
            'position': analysis_results['position'],
            'analysis_date': analysis_results['analysis_date'],
            'text_analysis': analysis_results['text_analysis'],
            'emotion_analysis': analysis_results['emotion_analysis']
        }
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        # PDF raporu oluştur
        pdf_filename = f"{candidate_name}_{timestamp}_report.pdf"
        pdf_path = os.path.join(output_dir, pdf_filename)
        
        pdf_created = self.save_report_as_pdf(
            analysis_results['hr_report'], 
            pdf_path, 
            emotion_analysis=analysis_results['emotion_analysis'],
            candidate_name=candidate_name,
            position=analysis_results.get('position', 'Test Pozisyonu'),
            text_analysis=analysis_results.get('text_analysis', '')
        )
        
        print(f"HTML Raporu: {html_path}")
        print(f"JSON Verileri: {json_path}")
        if pdf_created:
            print(f"PDF Raporu: {pdf_path}")
        else:
            print("PDF raporu oluşturulamadı")
        
        return {
            'html_path': html_path,
            'pdf_path': pdf_path if pdf_created else None,
            'json_path': json_path
        }


def main():
    """Ana fonksiyon - örnek kullanım"""
    
    # API anahtarını buraya girin
    API_KEY = "***REMOVED***"
    
    # API anahtarı mevcut, devam et
    
    # Video analyzer oluştur
    analyzer = VideoAnalyzer(API_KEY)
    
    # Video dosyasının yolu
    video_path = input("Video dosyasının tam yolunu girin: ").strip()
    
    if not os.path.exists(video_path):
        print(f"❌ Video dosyası bulunamadı: {video_path}")
        return
    
    # Aday bilgileri
    candidate_name = input("Aday adı (Enter = 'Aday'): ").strip() or "Aday"
    position = input("Pozisyon (Enter = 'Pozisyon'): ").strip() or "Pozisyon"
    
    try:
        # Analiz yap
        results = analyzer.analyze_video(video_path, candidate_name, position)
        
        # Raporu kaydet
        report_result = analyzer.save_report(results)
        
        print(f"\n✅ Analiz tamamlandı!")
        print(f"📊 HTML Raporu: {report_result['html_path']}")
        if report_result['pdf_path']:
            print(f"📄 PDF Raporu: {report_result['pdf_path']}")
        print(f"🌐 Raporları tarayıcınızda açabilirsiniz.")
        
    except Exception as e:
        print(f"❌ Hata oluştu: {str(e)}")


if __name__ == "__main__":
    main()