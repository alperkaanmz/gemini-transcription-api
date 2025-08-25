# 🎥 Video Analizi ve İK Raporu - Kullanım Rehberi

## 🚀 Hızlı Başlangıç

### 1. Kurulum
```bash
# Gerekli kütüphaneleri yükleyin
pip install -r requirements.txt
```

### 2. API Anahtarı
- [Google AI Studio](https://makersuite.google.com/app/apikey) adresinden API anahtarınızı alın
- `video_analyzer.py` dosyasındaki `API_KEY` değişkenini güncelleyin

### 3. Video Hazırlığı
- Videolarınızı `videos/` klasörüne koyun
- Desteklenen formatlar: **WebM, MP4, MOV, AVI, MKV**

## 📋 Kullanım Yöntemleri

### Yöntem 1: Otomatik Analiz (Önerilen)
```bash
python video_analyzer.py
```
Bu komut:
- Videos klasöründeki tüm dosyaları bulur
- AI ile aday isimlerini otomatik çıkarır
- Her video için tam analiz yapar
- HTML + JSON raporları oluşturur

### Yöntem 2: Programlı Kullanım
```python
from video_analyzer import VideoAnalyzer

# Analyzer oluştur
analyzer = VideoAnalyzer("YOUR-API-KEY")

# Video analiz et
results = analyzer.analyze_video(
    video_path="videos/mulakat.webm",
    candidate_name=None,  # AI otomatik belirler
    position="Yazılım Geliştirici"
)

# Raporu kaydet
report_path = analyzer.save_report(results)
print(f"Rapor: {report_path}")
```

### Yöntem 3: Toplu Analiz
```python
# Birden fazla video
videos = ["video1.webm", "video2.webm", "video3.webm"]

for video in videos:
    results = analyzer.analyze_video(video)
    analyzer.save_report(results)
```

## 📊 Çıktılar

Her analiz sonucunda şunlar oluşturulur:

### 1. HTML Raporu
- **Konum**: `reports/Aday_Ismi_YYYYMMDD_HHMMSS_report.html`
- **İçerik**: Grafikli İK raporu
- **Grafikler**: 4 adet (pasta, bar, donut, radar)

### 2. JSON Verileri  
- **Konum**: `reports/Aday_Ismi_YYYYMMDD_HHMMSS_data.json`
- **İçerik**: Ham analiz verileri
- **Kullanım**: API entegrasyonları için

### 3. PDF Raporu (İsteğe bağlı)
- **Durum**: Windows'ta sorunlu (kütüphane eksikliği)
- **Alternatif**: HTML raporunu tarayıcıdan PDF'e dönüştürün

## 🎯 Özellikler

### Otomatik AI Analizi
- ✅ **İsim Çıkarma**: "Ben Ahmet" → "Ahmet" 
- ✅ **Metin Tanıma**: Konuşma + ekran yazıları
- ✅ **8 Duygu Analizi**: Mutluluk, üzüntü, öfke, şaşkınlık, korku, iğrenme, güven, nötr

### Görsel Raporlama
- 🍰 **Ana Duygular (Pasta)**: Neutral dahil 6 duygu
- 📊 **Duygusal Durum (Bar)**: Pozitif/Negatif/Nötr
- 🍩 **Detaylı Duygular (Donut)**: İğrenme, güven, rahatlık, profesyonellik  
- 🕷️ **Performans Radarı (Altıgen)**: 6 ana kriter

### Maliyet Takibi
- 💰 **Gerçek Zamanlı**: Her işlem maliyeti görüntülenir
- 📊 **Detaylı Rapor**: Token kullanımı + USD/TL maliyeti
- ⚡ **Verimli**: Tek analiz ~14 kuruş

## 💡 Kullanım Örnekleri

### Örnek 1: Tek Aday Analizi
```bash
# videos/ahmet_mulakat.webm dosyası için
python video_analyzer.py

# Sonuç: reports/Ahmet_20250825_120000_report.html
```

### Örnek 2: Toplu İK Değerlendirme
```python
import os
from video_analyzer import VideoAnalyzer

analyzer = VideoAnalyzer("API-KEY")

# Tüm mülakatları analiz et
for video_file in os.listdir("videos"):
    if video_file.endswith(('.webm', '.mp4', '.mov')):
        video_path = f"videos/{video_file}"
        results = analyzer.analyze_video(video_path)
        analyzer.save_report(results)
        
        # Maliyet bilgisi
        cost = results['cost_report']['total_cost_usd']
        print(f"{video_file}: ${cost:.6f}")
```

### Örnek 3: Sonuçları Karşılaştırma
```python
import json

# İki adayın sonuçlarını karşılaştır
with open("reports/Ahmet_data.json") as f:
    ahmet_data = json.load(f)

with open("reports/Ayse_data.json") as f:
    ayse_data = json.load(f)

# Skorları karşılaştır
ahmet_score = ahmet_data['emotion_analysis']['overall_sentiment']['communication_skill']
ayse_score = ayse_data['emotion_analysis']['overall_sentiment']['communication_skill']

print(f"İletişim Skoru - Ahmet: {ahmet_score}, Ayşe: {ayse_score}")
```

## 🔧 Sorun Giderme

### Video Yüklenemedi
```
❌ Video dosyası bulunamadı: video.mp4
```
**Çözüm**: Video dosyasının `videos/` klasöründe olduğundan emin olun.

### API Hatası
```
❌ 403 API key not valid
```
**Çözüm**: Google AI Studio'dan geçerli API anahtarı alın ve güncelleyin.

### İsim Çıkaramadı
```
AI ile aday ismi belirleniyor... → "Aday"
```
**Çözüm**: Video başında aday kendini tanıtmıyorsa "Aday" olarak kaydedilir, normal davranış.

### PDF Oluşturulamadı
```
❌ PDF oluşturulamadı: library not found
```
**Çözüm**: HTML raporunu tarayıcıda açıp PDF olarak kaydedin.

## 📈 Performans İpuçları

### Video Boyutu
- ✅ **Optimal**: 5-20 MB WebM
- ⚠️ **Büyük**: 50+ MB (yavaş yükleme)
- ❌ **Çok büyük**: 100+ MB (timeout riski)

### Toplu İşlem
- 🔄 **Sıralı**: Aynı anda 1 video işleyin
- ⏱️ **Bekleme**: Video başına 30-60 saniye 
- 💾 **Depolama**: Her rapor ~500KB

### Maliyet Optimizasyonu
- 📹 **Kısa videolar**: 2-5 dakika ideal
- 🎯 **Odaklı içerik**: Net konuşma + yüz görüntüsü
- 💰 **Bütçe**: 100 video ~14 TL

## 🎯 Sonuç

Bu sistem ile:
- ⚡ Hızlı video analizi (30-60 saniye)
- 🎯 Otomatik İK değerlendirmesi
- 📊 Profesyonel raporlar  
- 💰 Uygun maliyetli işlem (~14 kuruş/video)

**Başlamak için**: `python video_analyzer.py` komutunu çalıştırın!