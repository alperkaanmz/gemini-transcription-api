# ⚡ Hızlı Başlangıç Kılavuzu

## 🚀 3 Adımda Başlayın

### 1️⃣ API Anahtarı Ayarlayın
```bash
# video_analyzer.py dosyasını açın
# Satır 23: API_KEY = "YOUR-API-KEY-HERE"
# Kendi API anahtarınızı yazın
```
**API Anahtarı:** [Google AI Studio](https://makersuite.google.com/app/apikey)

### 2️⃣ Video Ekleyin
```bash
# Videolarınızı videos/ klasörüne kopyalayın
cp your_interview.webm videos/
```

### 3️⃣ Analiz Başlatın
```bash
python video_analyzer.py
```

## ✅ Kontrol Listesi

- [ ] Python 3.8+ yüklü mü?
- [ ] `pip install -r requirements.txt` çalıştırdınız mı?
- [ ] API anahtarınızı `video_analyzer.py` dosyasına yazdınız mı?
- [ ] Video dosyanızı `videos/` klasörüne koydunuz mu?

## 🎯 İlk Çalışma Örneği

```bash
# Terminal/CMD açın
cd C:\Users\mazin\Desktop\Stella\gemini-api

# Analizi başlatın  
python video_analyzer.py

# Beklenen çıktı:
# Video analizi başlıyor...
# AI ile aday ismi belirleniyor...
# Belirlenen aday ismi: [İsim]
# MALIYET ANALİZİ:
# Toplam Maliyet: $0.004003
# HTML Raporu: reports/[İsim]_report.html
```

## 📊 Sonuçları Görüntüleme

Analiz bitince:
1. `reports/` klasörü açılacak
2. HTML dosyasını tarayıcıda açın
3. Grafikli raporu inceleyin

## 🆘 Hata Durumunda

### API Hatası
```
❌ 403 API key not valid
```
**Çözüm**: API anahtarınızı kontrol edin

### Video Bulunamadı
```
❌ Video dosyası bulunamadı
```
**Çözüm**: Dosya yolunu kontrol edin

### Kütüphane Hatası
```
❌ No module named 'google.generativeai'
```
**Çözüm**: `pip install -r requirements.txt`

## 💡 İpuçları

- ✅ **Video Format**: WebM en iyi sonucu verir
- ✅ **Video Süresi**: 2-5 dakika ideal
- ✅ **Kalite**: Net ses + yüz görüntüsü
- ✅ **İsim**: Videoda "Ben [İsim]" desin

**🎥 Hemen deneyin ve ilk raporunuzu alın!** 🚀