# -*- coding: utf-8 -*-
"""
Tek Video Test - Manuel olarak bir video seçip veya yolunu girerek analiz edin
"""

from video_analyzer import VideoAnalyzer
import os

def tek_video_test():
    """Tek video için manuel test"""
    
    print("=" * 60)
    print("TEK VIDEO ANALIZI TESTI")
    print("=" * 60)
    print("Bu script ile istediğiniz bir videoyu manuel olarak test edebilirsiniz.")
    print()
    
    # API anahtarı (otomatik olarak video_analyzer.py'dan alınır)
    api_key = "***REMOVED***"
    
    # Video yolu seçenekleri
    print("VIDEO YOLU SEÇENEKLERİ:")
    print("  1. Klasördeki mevcut videolardan seç")
    print("  2. Video yolunu elle gir")
    print()
    
    while True:
        try:
            secim_turu = input("Hangi seçeneği kullanmak istiyorsunuz? (1-2): ").strip()
            
            if secim_turu == "1":
                # Mevcut videolar listesi
                print("\nMEVCUT VIDEOLAR:")
                video_files = []
                
                if os.path.exists("videos"):
                    for file in os.listdir("videos"):
                        if file.lower().endswith(('.webm', '.mp4', '.mov', '.avi', '.mkv')):
                            video_files.append(file)
                            size_mb = os.path.getsize(f"videos/{file}") / (1024 * 1024)
                            print(f"  {len(video_files)}. {file} ({size_mb:.1f} MB)")
                
                if not video_files:
                    print("  ❌ videos/ klasöründe video dosyası bulunamadı!")
                    print("  📁 Lütfen video dosyanızı videos/ klasörüne koyun veya seçenek 2'yi kullanın.")
                    continue
                    
                break
                
            elif secim_turu == "2":
                video_files = []  # Elle giriş için boş liste
                break
                
            else:
                print("❌ Geçersiz seçim! Lütfen 1 veya 2 girin.")
                
        except KeyboardInterrupt:
            print("\n❌ İşlem iptal edildi.")
            return
    
    print()
    print("MANUEL AYARLAR:")
    print("  • API Key: ✅ Hazır")
    print("  • Video Format: WebM, MP4, MOV, AVI, MKV desteklenir")
    print("  • AI İsim Çıkarma: ✅ Aktif")
    print("  • Maliyet Takibi: ✅ Aktif")
    print()
    
    # Video seçimi
    if secim_turu == "1":
        # Klasörden seçim
        while True:
            try:
                secim = input(f"Hangi videoyu analiz etmek istiyorsunuz? (1-{len(video_files)}): ").strip()
                
                if secim.isdigit() and 1 <= int(secim) <= len(video_files):
                    secilen_video = video_files[int(secim) - 1]
                    video_path = f"videos/{secilen_video}"
                    break
                else:
                    print("❌ Geçersiz seçim! Lütfen doğru numara girin.")
            except KeyboardInterrupt:
                print("\n❌ İşlem iptal edildi.")
                return
                
    else:
        # Elle video yolu girişi
        print("\nVIDEO YOLU GİRİŞİ:")
        print("Örnekler:")
        print("  • C:\\Users\\kullanici\\Desktop\\video.mp4")
        print("  • D:\\videolarim\\mülakat.webm")
        print("  • videos\\test.mp4")
        print()
        
        while True:
            try:
                video_path = input("Video dosyasının tam yolunu girin: ").strip().strip('"\'')
                
                if not video_path:
                    print("❌ Lütfen geçerli bir video yolu girin!")
                    continue
                
                # Dosyanın var olup olmadığını kontrol et
                if not os.path.exists(video_path):
                    print(f"❌ Video dosyası bulunamadı: {video_path}")
                    print("Lütfen dosya yolunu kontrol edin.")
                    continue
                
                # Video formatını kontrol et
                if not video_path.lower().endswith(('.webm', '.mp4', '.mov', '.avi', '.mkv')):
                    print("❌ Desteklenmeyen dosya formatı!")
                    print("Desteklenen formatlar: .webm, .mp4, .mov, .avi, .mkv")
                    continue
                
                # Dosya boyutunu kontrol et
                try:
                    size_mb = os.path.getsize(video_path) / (1024 * 1024)
                    if size_mb > 50:
                        print(f"⚠️  Uyarı: Video dosyası çok büyük ({size_mb:.1f} MB)")
                        print("Gemini API için 50MB'ın altında olması önerilir.")
                        
                        onay = input("Yine de devam etmek istiyor musunuz? (e/E = Evet): ").strip().lower()
                        if onay not in ['e', 'evet']:
                            continue
                    
                    secilen_video = os.path.basename(video_path)
                    print(f"✅ Video seçildi: {secilen_video} ({size_mb:.1f} MB)")
                    break
                    
                except OSError as e:
                    print(f"❌ Dosya erişim hatası: {e}")
                    continue
                    
            except KeyboardInterrupt:
                print("\n❌ İşlem iptal edildi.")
                return
    
    # Opsiyonel bilgiler
    print(f"\n📹 Seçilen video: {secilen_video}")
    print(f"📂 Video yolu: {video_path}")
    print()
    
    print("OPSIYONEL AYARLAR (Enter = otomatik):")
    aday_ismi = input("  Aday ismi (Enter = AI belirleyecek): ").strip()
    pozisyon = input("  Pozisyon (Enter = 'Test Pozisyonu'): ").strip()
    
    if not aday_ismi:
        aday_ismi = None  # AI belirleyecek
    
    if not pozisyon:
        pozisyon = "Test Pozisyonu"
    
    print(f"\n🎯 ANALIZ AYARLARI:")
    print(f"   📹 Video: {secilen_video}")
    print(f"   📂 Yol: {video_path}")
    print(f"   👤 Aday: {aday_ismi if aday_ismi else 'AI belirleyecek'}")
    print(f"   💼 Pozisyon: {pozisyon}")
    print()
    
    # Onay
    onay = input("Analizi başlatmak istiyor musunuz? (e/E = Evet, diğer = Hayır): ").strip().lower()
    
    if onay not in ['e', 'evet']:
        print("❌ Analiz iptal edildi.")
        return
    
    try:
        # Analyzer oluştur
        print(f"\n{'='*60}")
        print("ANALIZ BAŞLIYOR...")
        print(f"{'='*60}")
        
        analyzer = VideoAnalyzer(api_key)
        print("✅ Video analyzer hazır!")
        
        # Video analizi
        print(f"📊 {secilen_video} analiz ediliyor...")
        
        results = analyzer.analyze_video(
            video_path=video_path,
            candidate_name=aday_ismi,
            position=pozisyon
        )
        
        print("✅ Analiz tamamlandı!")
        
        # Raporu kaydet
        print("\n📝 Rapor kaydediliyor...")
        report_path = analyzer.save_report(results)
        
        # Sonuç özeti
        print(f"\n{'='*60}")
        print("ANALIZ SONUÇLARI")
        print(f"{'='*60}")
        
        cost_report = results['cost_report']
        candidate_name = results['candidate_name']
        
        print(f"👤 Belirlenen Aday: {candidate_name}")
        print(f"💼 Pozisyon: {results['position']}")
        print(f"📊 Token Kullanımı: {cost_report['total_tokens']['total']:,}")
        print(f"💰 Maliyet: ${cost_report['total_cost_usd']:.6f} (₺{cost_report['total_cost_usd'] * 34:.4f})")
        print(f"📄 HTML Raporu: {os.path.basename(report_path)}")
        
        # Raporu açma seçeneği
        print()
        rapor_ac = input("HTML raporunu tarayıcıda açmak ister misiniz? (e/E = Evet): ").strip().lower()
        
        if rapor_ac in ['e', 'evet']:
            os.system(f'start "" "{report_path}"')
            print("🌐 Rapor tarayıcıda açıldı!")
        
        # Reports klasörünü açma
        klasor_ac = input("Reports klasörünü açmak ister misiniz? (e/E = Evet): ").strip().lower()
        
        if klasor_ac in ['e', 'evet']:
            os.system('start "" "reports"')
            print("📂 Reports klasörü açıldı!")
        
        print(f"\n🎉 Test başarıyla tamamlandı!")
        print(f"📊 Detaylı raporu inceleyin: {os.path.basename(report_path)}")
        
    except Exception as e:
        print(f"\n❌ HATA OLUŞTU:")
        print(f"   {str(e)}")
        print(f"\n🔧 OLASI ÇÖZÜMLER:")
        print(f"   1. İnternet bağlantınızı kontrol edin")
        print(f"   2. API anahtarınızın geçerli olduğundan emin olun")  
        print(f"   3. Video dosyasının bozuk olmadığını kontrol edin")
        print(f"   4. Video boyutunun 50MB'ın altında olduğunu kontrol edin")


if __name__ == "__main__":
    try:
        tek_video_test()
    except KeyboardInterrupt:
        print("\n\n👋 Program kapatıldı. İyi günler!")
    except Exception as e:
        print(f"\n❌ Beklenmeyen hata: {e}")
        print("Lütfen programı yeniden başlatın.")
