import os
import google.generativeai as genai
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import tempfile
import time
import json
from datetime import datetime
import re
from dotenv import load_dotenv

# .env dosyasını yükle (local development için)
load_dotenv()

app = FastAPI(
    title="Video Transkripsiyon API",
    description="Gemini 2.5 Flash Lite kullanarak video dosyalarından sadece konuşma metni çıkarma",
    version="1.0.0"
)

# Konfigürasyon
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'webm', 'mov', 'avi', 'mkv'}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

# Upload klasörünü oluştur
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Pydantic modeller
class URLRequest(BaseModel):
    url: str

class TranscriptionService:
    def __init__(self, api_key: str):
        """
        Sadece transkripsiyon için Gemini 2.5 Flash Lite kullanarak servis
        
        Args:
            api_key (str): Google Gemini API anahtarı
        """
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash-lite')
        
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
    
    def upload_video(self, video_path: str):
        """
        Video dosyasını Gemini API'ye yükle
        
        Args:
            video_path (str): Video dosyasının yolu
            
        Returns:
            Yüklenen video dosyası objesi
        """
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
    
    def transcribe_video(self, video_file) -> str:
        """
        Videodan sadece transkripsiyon çıkar
        
        Args:
            video_file: Yüklenmiş video dosyası
            
        Returns:
            str: Videodan çıkarılan konuşma metni
        """
        prompt = """
        Bu videoyu analiz et ve SADECE aşağıdaki işlemi yap:
        
        Videodaki tüm konuşmaları tam olarak transkript et. 
        
        Lütfen:
        - Sadece konuşulan sözleri yaz.
        - Hiçbir analiz, yorum veya ek bilgi, zaman vs. ekleme
        - Eğer konuşma yoksa "Videoda konuşma tespit edilmedi" yaz
        
        TRANSKRIPT:
        """
        
        response = self.model.generate_content([video_file, prompt])
        return response.text

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def secure_filename(filename):
    """Dosya adını güvenli hale getir"""
    filename = re.sub(r'[^a-zA-Z0-9._-]', '', filename)
    return filename

# API anahtarını çevre değişkeninden al
API_KEY = os.getenv('GEMINI_API_KEY')
if not API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is required")

transcription_service = TranscriptionService(API_KEY)

@app.get('/health')
def health_check():
    """Sağlık kontrol endpoint'i"""
    return {
        'status': 'healthy',
        'service': 'transcription-api',
        'timestamp': datetime.now().isoformat()
    }

@app.get('/docs')
def docs():
    """API dokümantasyonu endpoint'i"""
    base_url = "http://localhost:8000"  # FastAPI için güncellenen port
    documentation = {
        'title': 'Video Transkripsiyon API',
        'description': 'Gemini 2.5 Flash Lite kullanarak video dosyalarından sadece konuşma metni çıkarma',
        'version': '1.0.0',
        'base_url': base_url,
        'endpoints': {
            'health': {
                'method': 'GET',
                'path': '/health',
                'description': 'API sağlık durumu kontrolü',
                'response': {
                    'status': 'healthy',
                    'service': 'transcription-api',
                    'timestamp': 'ISO format zaman damgası'
                }
            },
            'docs': {
                'method': 'GET',
                'path': '/docs',
                'description': 'API dokümantasyonu (bu sayfa)',
                'response': 'JSON format API dokümantasyonu'
            },
            'transcribe': {
                'method': 'POST',
                'path': '/transcribe',
                'description': 'Video dosyası yükleyerek transkripsiyon',
                'content_type': 'multipart/form-data',
                'parameters': {
                    'video': 'Video dosyası (mp4, webm, mov, avi, mkv)'
                },
                'max_file_size': '100MB',
                'response': {
                    'success': 'boolean',
                    'transcription': 'string - konuşma metni',
                    'message': 'string - durum mesajı',
                    'timestamp': 'string - ISO format'
                }
            },
            'transcribe_url': {
                'method': 'POST',
                'path': '/transcribe-url',
                'description': 'URL\'den video indirip transkripsiyon',
                'content_type': 'application/json',
                'body': {
                    'url': 'string - video URL\'si'
                },
                'response': {
                    'success': 'boolean',
                    'transcription': 'string - konuşma metni',
                    'message': 'string - durum mesajı',
                    'timestamp': 'string - ISO format'
                }
            }
        },
        'supported_formats': list(ALLOWED_EXTENSIONS),
        'max_file_size_mb': MAX_FILE_SIZE // (1024 * 1024),
        'examples': {
            'curl_file_upload': f"curl -X POST -F \"video=@video.mp4\" {base_url}/transcribe",
            'curl_url': f"curl -X POST -H \"Content-Type: application/json\" -d '{{\"url\": \"https://example.com/video.mp4\"}}' {base_url}/transcribe-url",
            'python_file': f'''
import requests

with open("video.mp4", "rb") as f:
    files = {{"video": f}}
    response = requests.post("{base_url}/transcribe", files=files)
    result = response.json()
    print(result["transcription"])
            '''.strip(),
            'python_url': f'''
import requests

data = {{"url": "https://example.com/video.mp4"}}
response = requests.post("{base_url}/transcribe-url", json=data)
result = response.json()
print(result["transcription"])
            '''.strip()
        },
        'error_codes': {
            '400': 'Geçersiz istek (dosya yok, desteklenmeyen format, büyük dosya)',
            '500': 'Sunucu hatası (video işleme hatası, API hatası)'
        },
        'notes': [
            'API sadece transkripsiyon yapar, duygu analizi yapmaz',
            'Konuşmacı ayrımı [Konuşmacı 1], [Konuşmacı 2] şeklinde yapılır',
            'Geçici dosyalar otomatik olarak silinir',
            'Gemini 2.5 Flash Lite modeli kullanılır'
        ]
    }
    return documentation

@app.post('/transcribe')
async def transcribe(video: UploadFile = File(...)):
    """
    Video dosyasından transkripsiyon çıkarma endpoint'i
    
    Args:
        video: UploadFile - video dosyası (mp4, webm, mov, avi, mkv)
    
    Returns:
        JSON: {
            "success": true/false,
            "transcription": "metin",
            "message": "durum mesajı",
            "timestamp": "zaman damgası"
        }
    """
    try:
        # Dosya kontrolü
        if not video.filename:
            raise HTTPException(
                status_code=400,
                detail={
                    'success': False,
                    'message': 'Dosya seçilmedi',
                    'timestamp': datetime.now().isoformat()
                }
            )
        
        if not allowed_file(video.filename):
            raise HTTPException(
                status_code=400,
                detail={
                    'success': False,
                    'message': f'Desteklenen formatlar: {", ".join(ALLOWED_EXTENSIONS)}',
                    'timestamp': datetime.now().isoformat()
                }
            )
        
        # Dosya boyutu kontrolü
        content = await video.read()
        file_size = len(content)
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail={
                    'success': False,
                    'message': f'Dosya boyutu çok büyük (max: {MAX_FILE_SIZE // (1024*1024)}MB)',
                    'timestamp': datetime.now().isoformat()
                }
            )
        
        # Geçici dosya kaydet
        filename = secure_filename(video.filename)
        temp_path = os.path.join(UPLOAD_FOLDER, f"temp_{int(time.time())}_{filename}")
        
        with open(temp_path, 'wb') as f:
            f.write(content)
        
        try:
            # Video yükle ve transkript et
            video_file = transcription_service.upload_video(temp_path)
            transcription = transcription_service.transcribe_video(video_file)
            
            # Geçici dosyayı sil
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            # Gemini'den dosyayı sil
            try:
                genai.delete_file(video_file.name)
            except:
                pass  # Silme hatası önemli değil
            
            return {
                'success': True,
                'transcription': transcription.strip(),
                'message': 'Transkripsiyon başarıyla tamamlandı',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            # Geçici dosyayı sil
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            raise HTTPException(
                status_code=500,
                detail={
                    'success': False,
                    'message': f'Transkripsiyon hatası: {str(e)}',
                    'timestamp': datetime.now().isoformat()
                }
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                'success': False,
                'message': f'Sunucu hatası: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
        )

if __name__ == '__main__':
    import uvicorn
    
    # Development server
    print("Transkripsiyon API'si başlatılıyor...")
    print(f"Desteklenen formatlar: {', '.join(ALLOWED_EXTENSIONS)}")
    print(f"Maksimum dosya boyutu: {MAX_FILE_SIZE // (1024*1024)}MB")
    print("\nEndpoint'ler:")
    print("GET  /health - Sağlık kontrolü")
    print("GET  /docs - API dokümantasyonu")
    print("POST /transcribe - Dosya yükleme ile transkripsiyon")
    print("Otomatik Swagger UI: http://localhost:8000/docs")
    
    uvicorn.run(app, host='0.0.0.0', port=8000)
