"""
Clean Code Tek Video Test - SOLID prensipleri ile tam işlevsel
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from clean_video_analyzer import VideoAnalyzer

def clean_tek_video_test():
    """Gemini versiyonu ile tek video testi - tam işlevsel"""
    
    print("=" * 60)
    print("🏗️ GEMINI TEK VIDEO ANALİZİ")
    print("=" * 60)
    
    # API anahtarı
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
                    print("  📁 Lütfen video dosyanızı videos/ klasörüne koyun.")
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
    print("🏗️ CLEAN CODE ÖZELLİKLERİ:")
    print("  ✅ SOLID Prensipleri")
    print("  ✅ Modüler Architecture")
    print("  ✅ Dependency Injection")
    print("  ✅ Error Handling")
    print("  ✅ Tam İşlevsellik")
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
        print("  • videos\\test.mp4")
        print()
        
        while True:
            try:
                video_path = input("Video dosyasının tam yolunu girin: ").strip().strip('"\'')
                
                if not video_path:
                    print("❌ Lütfen geçerli bir video yolu girin!")
                    continue
                
                if not os.path.exists(video_path):
                    print(f"❌ Video dosyası bulunamadı: {video_path}")
                    continue
                
                if not video_path.lower().endswith(('.webm', '.mp4', '.mov', '.avi', '.mkv')):
                    print("❌ Desteklenmeyen dosya formatı!")
                    continue
                
                size_mb = os.path.getsize(video_path) / (1024 * 1024)
                secilen_video = os.path.basename(video_path)
                print(f"✅ Video seçildi: {secilen_video} ({size_mb:.1f} MB)")
                break
                    
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
    
    print(f"\n🎯 ANALİZ AYARLARI:")
    print(f"   📹 Video: {secilen_video}")
    print(f"   📂 Yol: {video_path}")
    print(f"   👤 Aday: {aday_ismi if aday_ismi else 'AI belirleyecek'}")
    print(f"   💼 Pozisyon: {pozisyon}")
    print()
    
    # Onay
    onay = input("Clean Code analizi başlatmak istiyor musunuz? (e/E = Evet): ").strip().lower()
    
    if onay not in ['e', 'evet']:
        print("❌ Analiz iptal edildi.")
        return
    
    try:
        # Clean Code Analyzer oluştur
        print(f"\n{'='*60}")
        print("🏗️ CLEAN CODE ANALİZ BAŞLIYOR...")
        print(f"{'='*60}")
        
        analyzer = VideoAnalyzer(api_key)
        print("✅ Clean Video Analyzer hazır! (SOLID Architecture)")
        
        # Video analizi
        print(f"📊 {secilen_video} analiz ediliyor...")
        
        result = analyzer.analyze_video(
            video_path=video_path,
            candidate_name=aday_ismi,
            position=pozisyon
        )
        
        print("✅ Analiz tamamlandı!")
        
        # Raporu kaydet (sadece HTML ve JSON gösterilecek)
        report_result = analyzer.save_report(result)
        
        # Sonuç özeti - basitleştirilmiş
        print(f"\n{'='*60}")
        print("📊 ANALİZ SONUÇLARI")
        print(f"{'='*60}")
        
        print(f"👤 Belirlenen Aday: {result.candidate_name}")
        print(f"💼 Pozisyon: {result.position}")
        print(f"📊 Token Kullanımı: {result.cost_report.total_tokens:,}")
        print(f"💰 Maliyet: ${result.cost_report.total_cost_usd:.6f} (₺{result.cost_report.total_cost_usd * 34:.4f})")
        print(f"📄 HTML Raporu: {os.path.basename(report_result['html_path'])}")
        print(f"� JSON Verileri: {os.path.basename(report_result['json_path'])}")
        print(f"\nℹ️  API için gerekli dosyalar otomatik olarak oluşturuldu.")
        
        # Rapor açma seçenekleri
        print()
        print("📊 RAPOR AÇMA SEÇENEKLERİ:")
        
        # HTML raporu açma
        html_ac = input("🌐 HTML raporunu tarayıcıda açmak ister misiniz? (e/E = Evet): ").strip().lower()
        if html_ac in ['e', 'evet']:
            import subprocess
            try:
                subprocess.run(['start', '', report_result["html_path"]], shell=True, check=True)
                print("🌐 HTML raporu tarayıcıda açıldı!")
            except Exception as e:
                print(f"⚠️ HTML raporu açılamadı: {e}")
        
        # PDF raporu açma
        if report_result['pdf_path']:
            pdf_ac = input("📄 PDF raporunu açmak ister misiniz? (e/E = Evet): ").strip().lower()
            if pdf_ac in ['e', 'evet']:
                import subprocess
                try:
                    subprocess.run(['start', '', report_result["pdf_path"]], shell=True, check=True)
                    print("📄 PDF raporu açıldı!")
                except Exception as e:
                    print(f"⚠️ PDF raporu açılamadı: {e}")
        
        # Reports klasörünü açma
        klasor_ac = input("📂 Reports klasörünü açmak ister misiniz? (e/E = Evet): ").strip().lower()
        if klasor_ac in ['e', 'evet']:
            import subprocess
            try:
                subprocess.run(['explorer', 'reports'], check=True)
                print("📂 Reports klasörü açıldı!")
            except Exception as e:
                print(f"⚠️ Klasör açılamadı: {e}")
        
        # Rapor listesi
        if report_result['pdf_path'] and report_result['api_pdf_path']:
            print(f"📊 Oluşturulan Raporlar:")
            print(f"   • HTML: {os.path.basename(report_result['html_path'])}")
            print(f"   • JSON: {os.path.basename(report_result['json_path'])}")
            print(f"   • CSV: {os.path.basename(report_result['csv_path'])}")
            print(f"   • PDF: {os.path.basename(report_result['pdf_path'])}")
            print(f"   • API PDF: {os.path.basename(report_result['api_pdf_path'])}")
        
    except Exception as e:
        print(f"\n❌HATA:")
        print(f"   {str(e)}")
        print(f"   Hata tipi: {type(e).__name__}")
        
        # Detaylı hata bilgisi
        import traceback
        print(f"\n🔍 DETAYLI HATA BİLGİSİ:")
        traceback.print_exc()


if __name__ == "__main__":
    try:
        clean_tek_video_test()
    except KeyboardInterrupt:
        print("\n\n👋 Program kapatıldı. İyi günler!")
    except Exception as e:
        print(f"\n❌ Beklenmeyen hata: {e}")
        print("Lütfen programı yeniden başlatın.")
