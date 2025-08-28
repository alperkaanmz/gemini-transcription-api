import requests
import json

# API URL'si
API_BASE_URL = "http://localhost:5000"

def test_health():
    """Sağlık kontrolü testi"""
    print("=== Sağlık Kontrolü ===")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"Hata: {e}")
    print()

def test_docs():
    """API dokümantasyonu testi"""
    print("=== API Dokümantasyonu ===")
    try:
        response = requests.get(f"{API_BASE_URL}/docs")
        print(f"Status Code: {response.status_code}")
        result = response.json()
        print(f"Title: {result.get('title')}")
        print(f"Version: {result.get('version')}")
        print(f"Endpoints: {list(result.get('endpoints', {}).keys())}")
        print(f"Supported Formats: {result.get('supported_formats')}")
    except Exception as e:
        print(f"Hata: {e}")
    print()

def test_transcribe_file(video_path):
    """Dosya yükleme ile transkripsiyon testi"""
    print("=== Dosya ile Transkripsiyon ===")
    try:
        with open(video_path, 'rb') as video_file:
            files = {'video': video_file}
            response = requests.post(f"{API_BASE_URL}/transcribe", files=files)
            
        print(f"Status Code: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if result.get('success'):
            print(f"\nTranskripsiyon: {result.get('transcription')}")
        
    except Exception as e:
        print(f"Hata: {e}")
    print()

def test_transcribe_url(video_url):
    """URL ile transkripsiyon testi"""
    print("=== URL ile Transkripsiyon ===")
    try:
        data = {"url": video_url}
        response = requests.post(
            f"{API_BASE_URL}/transcribe-url", 
            json=data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status Code: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if result.get('success'):
            print(f"\nTranskripsiyon: {result.get('transcription')}")
        
    except Exception as e:
        print(f"Hata: {e}")
    print()

if __name__ == "__main__":
    print("Transkripsiyon API Test Scripti")
    print("================================")
    
    # Sağlık kontrolü
    test_health()
    
    # API dokümantasyonu
    test_docs()
    
    # Dosya ile test (mevcut video dosyalarından birini kullan)
    video_file_path = "videos/deneme.webm"  # Bu dosyanın var olduğunu varsayıyoruz
    try:
        test_transcribe_file(video_file_path)
    except FileNotFoundError:
        print(f"Video dosyası bulunamadı: {video_file_path}")
        print("Lütfen mevcut bir video dosyası yolu verin.\n")
    
    # URL ile test (örnek)
    # test_transcribe_url("https://example.com/video.mp4")
    
    print("Test tamamlandı!")
