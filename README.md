# 🎥 AI Video Analizi ve İK Raporu Sistemi

Google **Gemini Flash 2.5 Lite API** ile otomatik video mülakat analizi ve İK değerlendirme sistemi.

## 🌟 Özellikler

### 🤖 AI Destekli Analiz
- ✅ **Otomatik İsim Çıkarma**: AI videodan aday ismini tespit eder
- ✅ **8 Duygu Analizi**: Mutluluk, üzüntü, öfke, şaşkınlık, korku, iğrenme, güven, nötr
- ✅ **Tam Transkript**: Konuşma + ekran metinleri
- ✅ **Beden Dili**: Postür, göz teması, güven seviyesi

### 📊 Görsel Raporlama  
- 🍰 **Pasta Grafik**: Ana duygu dağılımı (neutral dahil)
- 📊 **Bar Grafik**: Pozitif/negatif/nötr durum
- 🍩 **Donut Grafik**: Detaylı duygular (iğrenme, güven, rahatlık)
- 🕷️ **Radar Grafik**: 6 boyutlu performans analizi

### 💰 Maliyet Kontrolü
- 📊 **Gerçek Zamanlı**: Token + USD/TL takibi
- 💵 **Uygun Fiyat**: ~14 kuruş/video
- 📈 **Detaylı Rapor**: İşlem bazında maliyet

### 📁 Çoklu Format Çıktı
- 🌐 **HTML**: Grafikli interaktif rapor
- 📋 **JSON**: Ham veriler (API entegrasyonu)
- 📄 **PDF**: Yazdırma dostu rapor (opsiyonel)

## 🚀 Hızlı Başlangıç

### 1. Kurulum
```bash
git clone <repo>
cd gemini-api
pip install -r requirements.txt
```

### 2. API Anahtarı
1. [Google AI Studio](https://makersuite.google.com/app/apikey)'dan API anahtarı alın
2. `video_analyzer.py` dosyasındaki `API_KEY` değişkenini güncelleyin

### 3. Video Ekleme
```bash
# Videolarınızı videos/ klasörüne kopyalayın
cp your_video.webm videos/
```

### 4. Analiz Başlatma
```bash
# Otomatik analiz (tüm videos/ klasörü)
python video_analyzer.py
```

## 📊 Örnek Çıktı

```
MALIYET ANALIZI:
Toplam Token: 51,351
Input Token: 50,676  
Output Token: 675
Toplam Maliyet: $0.004003 (₺0.136)

AI ile belirlenen isim: "Kerem Deniz"
HTML Raporu: reports/Kerem_Deniz_20250825_004913_report.html
JSON Verileri: reports/Kerem_Deniz_20250825_004913_data.json
```

## 💻 Programlı Kullanım

### Basit Örnek
```python
from video_analyzer import VideoAnalyzer

analyzer = VideoAnalyzer("YOUR-API-KEY")

# AI isim çıkarma ile
results = analyzer.analyze_video("videos/mulakat.webm")
report_path = analyzer.save_report(results)

# Maliyet bilgisi
cost = results['cost_report']['total_cost_usd']
print(f"Maliyet: ${cost:.6f}")
```

### Toplu Analiz
```python
import os

for video_file in os.listdir("videos"):
    if video_file.endswith(('.webm', '.mp4')):
        results = analyzer.analyze_video(f"videos/{video_file}")
        analyzer.save_report(results)
```

## 🎯 Desteklenen Formatlar

- **Video**: WebM, MP4, MOV, AVI, MKV
- **Çıktı**: HTML (grafikli), JSON (ham veri), PDF (opsiyonel)
- **Diller**: Türkçe + çoklu dil desteği

## 📊 Analiz Detayları

### 🤖 AI Özellikleri
- **İsim Tanıma**: "Ben Ahmet Yılmaz" → "Ahmet Yılmaz"
- **Konuşma Tanıma**: Tam transkript + ekran yazıları
- **Duygu Tespiti**: 8 farklı duygu kategorisi
- **Beden Dili**: 6 boyutlu analiz

### 📈 Grafik Türleri
1. **Ana Duygular (Pasta)**: Neutral dahil 6 duygu dağılımı
2. **Duygusal Durum (Bar)**: Pozitif/negatif/nötr yüzdeler  
3. **Detaylı Duygular (Donut)**: İğrenme, güven, rahatlık, profesyonellik
4. **Performans Radarı (Altıgen)**: İletişim, güven, motivasyon, stres yönetimi, profesyonellik, genel performans

## 💰 Maliyet Bilgileri

| **Metrik** | **Değer** |
|------------|-----------|
| **Model** | Gemini 2.5 Flash Lite |
| **Input** | $0.075 / 1M token |
| **Output** | $0.30 / 1M token |
| **Ortalama Video** | ~$0.004 (~₺0.14) |
| **Token/Video** | ~50K token |

### Maliyet Örnekleri
- **1 video (5dk)**: ~₺0.14
- **10 video**: ~₺1.40  
- **100 video**: ~₺14.00

## 🔧 Teknik Özellikler

### Sistem Gereksinimleri
- **Python**: 3.8+
- **RAM**: 2GB+
- **Disk**: 500MB+ (raporlar için)
- **İnternet**: API erişimi

### Performans
- **Analiz Süresi**: 30-60 saniye/video
- **Video Boyutu**: 5-50MB optimal
- **Eş Zamanlı**: 1 video (sıralı işlem)

## 📋 Proje Yapısı

```
gemini-api/
├── 🔧 video_analyzer.py     # Ana motor
├── 📋 requirements.txt      # Kütüphaneler
├── 📖 README.md            # Bu dosya
├── 📚 KULLANIM_REHBERI.md  # Detaylı kılavuz
├── 🎥 videos/              # Video klasörü
│   ├── deneme.webm
│   ├── deneme2.webm  
│   └── deneme3.webm
└── 📊 reports/             # Çıktı raporları
    ├── Kerem_Deniz_report.html
    └── Kerem_Deniz_data.json
```

## 🚀 Gelişmiş Özellikler

### Otomatik İsim Çıkarma
```python
# AI kendisi belirler
results = analyzer.analyze_video("mulakat.webm", candidate_name=None)
# Çıktı: "Kerem Deniz" (videodan)
```

### Maliyet Takibi
```python
# Gerçek zamanlı maliyet
cost_report = results['cost_report']
print(f"Maliyet: ${cost_report['total_cost_usd']:.6f}")
print(f"Token: {cost_report['total_tokens']['total']:,}")
```

### Batch Processing
```python
# Tüm videos/ klasörünü işle
import os
for video in os.listdir("videos"):
    if video.endswith('.webm'):
        analyzer.analyze_video(f"videos/{video}")
```

## 🎯 Kullanım Alanları

- 🏢 **İK Departmanları**: Mülakat değerlendirme
- 🎓 **Eğitim Kurumları**: Öğrenci performans analizi
- 💼 **Danışmanlık**: Kişilik değerlendirme
- 🔬 **Araştırma**: Duygu analizi çalışmaları
- 📊 **Veri Bilimi**: Video analitik projeleri

## ⚠️ Önemli Bilgiler

### Veri Gizliliği
- ✅ Videolar Google sunucularına geçici yüklenir
- ✅ İşlem sonrası otomatik silinir
- ✅ Kişisel veriler local olarak saklanır

### Sınırlamalar  
- ❌ 100MB+ video dosyaları
- ❌ Eşzamanlı çoklu işlem
- ❌ Offline kullanım (API gerekli)

---

## 📚 Daha Fazla Bilgi

Detaylı kullanım için: **[KULLANIM_REHBERI.md](KULLANIM_REHBERI.md)**

**🎥 Hemen başlayın:** `python video_analyzer.py` 🚀