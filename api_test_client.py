"""
Video Analysis API Test Client
API'yi test etmek için örnek istemci
"""
import requests
import json
import time
from pathlib import Path

class VideoAnalysisAPIClient:
    """Video Analysis API istemcisi"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
    
    def check_health(self):
        """API sağlık kontrolü"""
        try:
            response = requests.get(f"{self.base_url}/health")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_status(self):
        """API durum bilgisi"""
        try:
            response = requests.get(f"{self.base_url}/")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def analyze_video_file(self, video_path: str, candidate_name: str = None, position: str = "Test Pozisyonu"):
        """Video dosyasını analiz et"""
        try:
            files = {
                'video_file': open(video_path, 'rb')
            }
            
            data = {
                'position': position
            }
            
            if candidate_name:
                data['candidate_name'] = candidate_name
            
            print(f"📤 Video gönderiliyor: {Path(video_path).name}")
            print(f"📊 Pozisyon: {position}")
            if candidate_name:
                print(f"👤 Aday: {candidate_name}")
            
            response = requests.post(
                f"{self.base_url}/analyze/upload",
                files=files,
                data=data,
                timeout=300  # 5 dakika timeout
            )
            
            files['video_file'].close()
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": f"HTTP {response.status_code}",
                    "detail": response.text
                }
                
        except Exception as e:
            return {"error": str(e)}
    
    def download_report(self, report_url: str, save_path: str = None):
        """Rapor dosyasını indir"""
        try:
            # URL'den filename çıkar
            filename = report_url.split('/')[-1]
            if not save_path:
                save_path = f"downloaded_{filename}"
            
            response = requests.get(f"{self.base_url}{report_url}")
            
            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                return {"success": True, "path": save_path}
            else:
                return {"error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    def list_analyses(self):
        """Mevcut analizleri listele"""
        try:
            response = requests.get(f"{self.base_url}/analyses")
            return response.json()
        except Exception as e:
            return {"error": str(e)}

def test_api():
    """API test fonksiyonu"""
    print("🧪 Video Analysis API Test Client")
    print("=" * 50)
    
    # API istemcisi oluştur
    client = VideoAnalysisAPIClient()
    
    # Sağlık kontrolü
    print("1️⃣ Sağlık Kontrolü...")
    health = client.check_health()
    print(f"   Sonuç: {health}")
    
    # Durum kontrolü
    print("\\n2️⃣ API Durumu...")
    status = client.get_status()
    print(f"   Sonuç: {status}")
    
    # Video listesi
    print("\\n3️⃣ Mevcut Videolar...")
    videos_dir = Path("videos")
    if videos_dir.exists():
        video_files = list(videos_dir.glob("*.webm")) + list(videos_dir.glob("*.mp4"))
        if video_files:
            for i, video in enumerate(video_files, 1):
                size_mb = video.stat().st_size / (1024 * 1024)
                print(f"   {i}. {video.name} ({size_mb:.1f} MB)")
            
            # Video seçimi
            try:
                choice = input("\\nHangi videoyu test etmek istiyorsunuz? (1-{}): ".format(len(video_files)))
                selected_video = video_files[int(choice) - 1]
                
                print(f"\\n4️⃣ Video Analizi Başlatılıyor...")
                print(f"   📹 Video: {selected_video.name}")
                
                # API'yi test et
                start_time = time.time()
                result = client.analyze_video_file(
                    video_path=str(selected_video),
                    position="API Test Pozisyonu"
                )
                end_time = time.time()
                
                print(f"\\n5️⃣ Analiz Sonuçları:")
                print(f"   ⏱️ Süre: {end_time - start_time:.2f} saniye")
                
                if "error" in result:
                    print(f"   ❌ Hata: {result['error']}")
                else:
                    print(f"   ✅ Başarılı!")
                    print(f"   👤 Aday: {result['candidate_name']}")
                    print(f"   💼 Pozisyon: {result['position']}")
                    print(f"   🆔 Analiz ID: {result['analysis_id']}")
                    print(f"   💰 Maliyet: ${result['cost_report']['total_cost_usd']:.6f}")
                    
                    print(f"\\n6️⃣ Rapor URL'leri:")
                    for report_type, url in result['report_urls'].items():
                        if url:
                            print(f"   📄 {report_type.upper()}: {client.base_url}{url}")
                    
                    # HTML raporu indirme testi
                    if result['report_urls']['html']:
                        print(f"\\n7️⃣ HTML Raporu İndirme Testi...")
                        download_result = client.download_report(
                            result['report_urls']['html'],
                            "test_report.html"
                        )
                        if "error" in download_result:
                            print(f"   ❌ İndirme hatası: {download_result['error']}")
                        else:
                            print(f"   ✅ İndirildi: {download_result['path']}")
                
            except (ValueError, IndexError, KeyboardInterrupt):
                print("   ❌ Geçersiz seçim veya işlem iptal edildi")
        else:
            print("   ❌ videos/ klasöründe video bulunamadı")
    else:
        print("   ❌ videos/ klasörü bulunamadı")
    
    print("\\n🏁 Test tamamlandı!")

if __name__ == "__main__":
    test_api()
