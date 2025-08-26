"""
Clean, SOLID-compliant Video Analyzer
"""
import os
from datetime import datetime
from typing import Dict, Any, Optional

from src.models import AnalysisResult, EmotionData, SentimentData, MBTIData
from src.services import GeminiService, ReportService, PDFService
from src.utils import FileUtils


class VideoAnalyzer:
    """
    Main orchestrator for video analysis following SOLID principles
    
    Single Responsibility: Coordinates the analysis process
    Open/Closed: Extensible through dependency injection
    Liskov Substitution: Uses abstract interfaces
    Interface Segregation: Small, focused interfaces
    Dependency Inversion: Depends on abstractions, not concretions
    """
    
    def __init__(self, api_key: str):
        """Initialize video analyzer with required services
        
        Args:
            api_key: Google AI API key for Gemini service
        """
        self.gemini_service = GeminiService(api_key)
        self.report_service = ReportService()
        self.pdf_service = PDFService()
        self.file_utils = FileUtils()
    
    def analyze_video(
        self, 
        video_path: str, 
        candidate_name: Optional[str] = None, 
        position: str = "Test Pozisyonu"
    ) -> AnalysisResult:
        """
        Analyze video and return comprehensive results
        
        Args:
            video_path: Path to video file
            candidate_name: Candidate name (auto-detected if None)
            position: Position being interviewed for
            
        Returns:
            Complete analysis result
            
        Raises:
            ValueError: If video file is invalid
            RuntimeError: If analysis fails
        """
        print("Video analizi başlıyor...")
        
        # Validate input
        if not FileUtils.validate_video_file(video_path):
            raise ValueError(f"Geçersiz video dosyası: {video_path}")
        
        try:
            # Upload video
            video_file = self.gemini_service.upload_video(video_path)
            
            # Auto-detect candidate name if not provided
            if not candidate_name:
                candidate_name = self._extract_candidate_name(video_file)
            
            # Perform analyses
            text_analysis = self._analyze_text(video_file)
            emotion_data, sentiment_data, mbti_data = self._analyze_emotions(video_file)
            
            # Create result object
            result = AnalysisResult(
                candidate_name=candidate_name,
                position=position,
                emotion_data=emotion_data,
                sentiment_data=sentiment_data,
                mbti_data=mbti_data,
                text_analysis=text_analysis,
                cost_report=self.gemini_service.get_cost_report(),
                timestamp=datetime.now()
            )
            
            print("✅ Analiz tamamlandı!")
            self.gemini_service.print_cost_summary()
            
            return result
            
        except Exception as e:
            print(f"❌ Video analizi hatası: {e}")
            raise RuntimeError(f"Video analizi başarısız: {e}")
    
    def _extract_candidate_name(self, video_file: Any) -> str:
        """Extract candidate name from video using AI"""
        prompt = """
        Bu videodaki kişinin adını belirle. Sadece adı söyle, başka bir şey yazma.
        Örnek: Ahmet Yılmaz
        """
        
        print("AI ile aday ismi belirleniyor...")
        name, _ = self.gemini_service.generate_content(prompt, video_file)
        
        # Clean the response
        cleaned_name = name.strip().replace('"', '').replace("'", "")
        print(f"Belirlenen aday ismi: {cleaned_name}")
        
        return cleaned_name
    
    def _analyze_text(self, video_file: Any) -> str:
        """Analyze speech and communication from video"""
        prompt = """
        Bu videodaki konuşmayı analiz et ve aşağıdaki formatta rapor ver:

        TRANSKRIPT:
        [Videodaki konuşmaların tam metni]

        İLETİŞİM ANALİZİ:
        - Konuşma hızı ve akıcılığı
        - Kelime seçimi ve terminoloji kullanımı
        - Cümle yapısı ve gramer
        - Ana mesajlar ve önemli noktalar

        ÖNERİLER:
        - İletişim becerileri için öneriler
        - Gelişim alanları
        """
        
        print("Metin analizi yapılıyor...")
        analysis, _ = self.gemini_service.generate_content(prompt, video_file)
        
        return analysis.strip()
    
    def _analyze_emotions(self, video_file: Any) -> tuple[EmotionData, SentimentData, MBTIData]:
        """Analyze emotions, sentiment and personality from video"""
        prompt = """
        Bu videoyu analiz ederek aşağıdaki JSON formatında sonuç ver:

        {
            "facial_emotions": {
                "happiness": 0-100 arası değer,
                "sadness": 0-100 arası değer,
                "anger": 0-100 arası değer,
                "surprise": 0-100 arası değer,
                "fear": 0-100 arası değer,
                "neutral": 0-100 arası değer,
                "disgust": 0-100 arası değer,
                "confidence": 0-100 arası değer
            },
            "overall_sentiment": {
                "positive_percentage": 0-100 arası değer,
                "negative_percentage": 0-100 arası değer,
                "neutral_percentage": 0-100 arası değer,
                "stress_level": 0-100 arası değer,
                "motivation_level": 0-100 arası değer,
                "communication_skill": 0-100 arası değer
            },
            "mbti_analysis": {
                "predicted_type": "MBTI tipi (örn: ESTJ)",
                "extraversion_introversion": 0-100 arası değer,
                "sensing_intuition": 0-100 arası değer,
                "thinking_feeling": 0-100 arası değer,
                "judging_perceiving": 0-100 arası değer,
                "confidence_level": 0-100 arası değer
            }
        }

        Sadece JSON formatında yanıt ver, başka açıklama ekleme.
        """
        
        print("Duygu analizi yapılıyor...")
        analysis_text, _ = self.gemini_service.generate_content(prompt, video_file)
        
        print(f"🔍 AI Response: {analysis_text[:200]}...")  # Debug için ilk 200 karakter
        
        try:
            import json
            # Clean markdown formatting
            cleaned_text = analysis_text.strip()
            if cleaned_text.startswith('```json'):
                cleaned_text = cleaned_text[7:]  # Remove ```json
            if cleaned_text.endswith('```'):
                cleaned_text = cleaned_text[:-3]  # Remove ```
            cleaned_text = cleaned_text.strip()
            
            analysis_data = json.loads(cleaned_text)
            
            # Create data objects
            emotion_data = EmotionData(**analysis_data['facial_emotions'])
            sentiment_data = SentimentData(**analysis_data['overall_sentiment'])
            mbti_data = MBTIData(**analysis_data['mbti_analysis'])
            
            return emotion_data, sentiment_data, mbti_data
            
        except (json.JSONDecodeError, KeyError) as e:
            print(f"⚠️ JSON parsing error: {e}")
            print(f"🔍 Raw response: {repr(analysis_text)}")  # Raw response'u göster
            # Return default values if parsing fails
            return EmotionData(), SentimentData(), MBTIData()
    
    def save_report(self, result: AnalysisResult, generate_csv: bool = False, generate_pdf: bool = False, generate_api_pdf: bool = True) -> Dict[str, Any]:
        """
        Generate and save report formats
        
        Args:
            result: Analysis result to save
            generate_csv: Generate CSV file (default: False, only for API usage)
            generate_pdf: Generate ReportLab PDF (default: False)
            generate_api_pdf: Generate API PDF (default: True, requires CSV)
            
        Returns:
            Dictionary with paths to generated reports
        """
        print("\n📝 Rapor kaydediliyor...")
        
        # Generate core reports (HTML, JSON) and optionally CSV
        report_paths = self.report_service.generate_all_reports(result, generate_csv=generate_csv or generate_api_pdf)
        
        # Generate ReportLab PDF if requested
        reportlab_pdf = None
        if generate_pdf:
            print("📄 ReportLab ile profesyonel PDF oluşturuluyor...")
            reportlab_pdf = self.pdf_service.generate_reportlab_pdf(
                result, 
                report_paths['base_filename'], 
                self.report_service.reports_dir,
                enabled=True
            )
        
        # Generate API PDF if requested and CSV is available
        api_pdf = None
        if generate_api_pdf and report_paths['csv_path']:
            api_pdf = self.pdf_service.generate_api_pdf(
                report_paths['csv_path'],
                result.candidate_name,
                result.position,
                report_paths['base_filename'],
                self.report_service.reports_dir,
                enabled=True
            )
        
        # Print simplified report summary (only show HTML and JSON)
        print(f"✅ HTML Raporu: {os.path.basename(report_paths['html_path'])}")
        print(f"✅ JSON Verileri: {os.path.basename(report_paths['json_path'])}")
        
        # Only show CSV and PDFs if explicitly generated
        if generate_csv and report_paths['csv_path']:
            print(f"✅ CSV Verileri: {os.path.basename(report_paths['csv_path'])}")
        
        if reportlab_pdf:
            print(f"✅ PDF Raporu: {os.path.basename(reportlab_pdf)}")
        
        if api_pdf:
            print(f"✅ API PDF Raporu: {os.path.basename(api_pdf)}")
        
        return {
            'html_path': report_paths['html_path'],
            'json_path': report_paths['json_path'],
            'csv_path': report_paths['csv_path'],
            'pdf_path': reportlab_pdf,
            'api_pdf_path': api_pdf,
            'base_filename': report_paths['base_filename']
        }
