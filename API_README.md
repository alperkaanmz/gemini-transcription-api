# Video Analysis API

Clean Code & SOLID prensipleri ile yazılmış video analiz API'si.

## 🚀 Özellikler

- ✅ **RESTful API** - Modern FastAPI ile
- ✅ **Clean Code** - SOLID prensipleri
- ✅ **Video Upload** - Dosya yükleme desteği
- ✅ **AI Analizi** - Google Gemini ile duygu, davranış ve MBTI analizi
- ✅ **Çoklu Format** - HTML, JSON, CSV, PDF raporları
- ✅ **Async** - Asenkron işlem desteği
- ✅ **CORS** - Cross-origin desteği
- ✅ **Swagger** - Otomatik API dokümantasyonu

## 📋 Gereksinimler

```bash
pip install -r requirements.txt
```

## 🎯 Hızlı Başlangıç

### 1. API Sunucusunu Başlat

```bash
python api_server.py
```

API şu adreste çalışacak: `http://localhost:8000`

### 2. API Dokümantasyonu

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 3. Test İstemcisi

```bash
python api_test_client.py
```

## 🔗 API Endpoints

### Durum Kontrolü

```http
GET /
GET /health
```

### Video Analizi

```http
POST /analyze/upload
Content-Type: multipart/form-data

Parameters:
- video_file: Video dosyası (mp4, webm, mov, avi, mkv)
- candidate_name: Aday ismi (opsiyonel)
- position: Pozisyon adı (varsayılan: "Test Pozisyonu")
```

### Rapor İndirme

```http
GET /reports/{filename}
```

### Analiz Listesi

```http
GET /analyses
```

### Temizlik

```http
DELETE /cleanup
```

## 💻 Kullanım Örnekleri

### Python ile API Kullanımı

```python
import requests

# Video analizi
files = {'video_file': open('video.mp4', 'rb')}
data = {'position': 'Software Developer', 'candidate_name': 'John Doe'}

response = requests.post(
    'http://localhost:8000/analyze/upload',
    files=files,
    data=data
)

result = response.json()
print(f"Analiz ID: {result['analysis_id']}")
print(f"Aday: {result['candidate_name']}")
```

### cURL ile API Kullanımı

```bash
curl -X POST "http://localhost:8000/analyze/upload" \\
     -H "accept: application/json" \\
     -H "Content-Type: multipart/form-data" \\
     -F "video_file=@video.mp4" \\
     -F "position=Software Developer" \\
     -F "candidate_name=John Doe"
```

### JavaScript/Fetch ile API Kullanımı

```javascript
const formData = new FormData();
formData.append('video_file', videoFile);
formData.append('position', 'Software Developer');
formData.append('candidate_name', 'John Doe');

fetch('http://localhost:8000/analyze/upload', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => {
    console.log('Analiz ID:', data.analysis_id);
    console.log('Aday:', data.candidate_name);
});
```

## 📊 Yanıt Formatı

```json
{
    "success": true,
    "message": "Video analizi başarıyla tamamlandı",
    "analysis_id": "John_Doe_20250826_123456",
    "candidate_name": "John Doe",
    "position": "Software Developer",
    "emotion_data": {
        "facial_emotions": { ... },
        "emotion_timeline": [ ... ]
    },
    "sentiment_data": {
        "positive_percentage": 75,
        "negative_percentage": 15,
        "neutral_percentage": 10
    },
    "mbti_data": {
        "personality_type": "ENFJ",
        "traits": { ... }
    },
    "text_analysis": "Detaylı metin analizi...",
    "cost_report": {
        "total_tokens": 50000,
        "total_cost_usd": 0.025
    },
    "report_urls": {
        "html": "/reports/John_Doe_20250826_123456_report.html",
        "json": "/reports/John_Doe_20250826_123456_data.json",
        "csv": "/reports/John_Doe_20250826_123456_data.csv",
        "pdf": "/reports/John_Doe_20250826_123456_api_report.pdf"
    },
    "timestamp": "2025-08-26T12:34:56"
}
```

## 🔧 Konfigürasyon

### API Ayarları

```python
# api_server.py içinde
API_KEY = "your_gemini_api_key"
HOST = "0.0.0.0"
PORT = 8000
```

### CORS Ayarları

```python
# Güvenlik için production'da specific domainler kullanın
allow_origins = ["https://yourdomain.com"]
```

## 🚀 Production Deployment

### Docker ile

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Nginx ile Reverse Proxy

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📝 Hata Kodları

- `400` - Bad Request (Geçersiz video formatı, eksik parametreler)
- `404` - Not Found (Rapor dosyası bulunamadı)
- `500` - Internal Server Error (Analiz hatası, sistem hatası)
- `501` - Not Implemented (URL analizi henüz desteklenmez)

## 🔒 Güvenlik

- API anahtarını güvenli şekilde saklayın
- Production'da HTTPS kullanın
- CORS ayarlarını dikkatli yapılandırın
- Rate limiting ekleyin
- Input validation uygulayın

## 🤝 Katkıda Bulunma

1. Fork the project
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 Lisans

MIT License - Detaylar için LICENSE dosyasına bakın.
