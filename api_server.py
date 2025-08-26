"""
Video Analysis API Server
Clean Code & SOLID prensipleri ile yazılmış API sistemi
"""
import os
import sys
import asyncio
import tempfile
import shutil
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path

# FastAPI imports
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Local imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from clean_video_analyzer import VideoAnalyzer

# API Models
class AnalysisRequest(BaseModel):
    """Video analizi istek modeli"""
    video_url: Optional[str] = None
    candidate_name: Optional[str] = None
    position: str = "Test Pozisyonu"

class AnalysisResponse(BaseModel):
    """Video analizi yanıt modeli"""
    success: bool
    message: str
    analysis_id: str
    candidate_name: str
    position: str
    emotion_data: Dict[str, Any]
    sentiment_data: Dict[str, Any]
    mbti_data: Dict[str, Any]
    text_analysis: str
    cost_report: Dict[str, Any]
    report_urls: Dict[str, str]
    timestamp: str

class StatusResponse(BaseModel):
    """Durum yanıt modeli"""
    status: str
    message: str
    version: str = "1.0.0"

# FastAPI App
app = FastAPI(
    title="Video Analysis API",
    description="Clean Code & SOLID prensipleri ile yazılmış video analiz API'si",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production'da specific domainler kullanın
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global değişkenler
API_KEY = "***REMOVED***"
TEMP_DIR = Path("temp_uploads")
REPORTS_DIR = Path("reports")

# Klasörleri oluştur
TEMP_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)

# Video Analyzer instance
analyzer = VideoAnalyzer(API_KEY)

@app.get("/", response_model=StatusResponse)
async def root():
    """API durumu"""
    return StatusResponse(
        status="active",
        message="Video Analysis API is running with Clean Code & SOLID principles"
    )

@app.get("/health")
async def health_check():
    """Sağlık kontrolü"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/analyze/upload", response_model=AnalysisResponse)
async def analyze_uploaded_video(
    background_tasks: BackgroundTasks,
    video_file: UploadFile = File(...),
    candidate_name: Optional[str] = Form(None),
    position: str = Form("Test Pozisyonu")
):
    """
    Yüklenen video dosyasını analiz et
    
    Args:
        video_file: Yüklenen video dosyası
        candidate_name: Aday ismi (opsiyonel, AI belirleyebilir)
        position: Pozisyon adı
    
    Returns:
        Analiz sonuçları
    """
    try:
        # Dosya validasyonu
        if not video_file.filename:
            raise HTTPException(status_code=400, detail="Video dosyası gerekli")
        
        # Desteklenen formatları kontrol et
        supported_formats = ['.mp4', '.webm', '.mov', '.avi', '.mkv']
        file_ext = Path(video_file.filename).suffix.lower()
        if file_ext not in supported_formats:
            raise HTTPException(
                status_code=400, 
                detail=f"Desteklenmeyen format: {file_ext}. Desteklenen: {supported_formats}"
            )
        
        # Geçici dosya oluştur
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_filename = f"upload_{timestamp}_{video_file.filename}"
        temp_path = TEMP_DIR / temp_filename
        
        # Dosyayı kaydet
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(video_file.file, buffer)
        
        print(f"📁 Video yüklendi: {temp_path}")
        
        # Analizi başlat
        result = analyzer.analyze_video(
            video_path=str(temp_path),
            candidate_name=candidate_name,
            position=position
        )
        
        # Raporları kaydet
        report_paths = analyzer.save_report(result, generate_csv=True, generate_api_pdf=True)
        
        # Analysis ID oluştur
        analysis_id = f"{result.candidate_name}_{timestamp}"
        
        # Yanıt hazırla
        response = AnalysisResponse(
            success=True,
            message="Video analizi başarıyla tamamlandı",
            analysis_id=analysis_id,
            candidate_name=result.candidate_name,
            position=result.position,
            emotion_data=result.emotion_data,
            sentiment_data=result.sentiment_data,
            mbti_data=result.mbti_data,
            text_analysis=result.text_analysis,
            cost_report=result.cost_report.__dict__,
            report_urls={
                "html": f"/reports/{Path(report_paths['html_path']).name}",
                "json": f"/reports/{Path(report_paths['json_path']).name}",
                "csv": f"/reports/{Path(report_paths['csv_path']).name}",
                "pdf": f"/reports/{Path(report_paths['api_pdf_path']).name}" if report_paths['api_pdf_path'] else None
            },
            timestamp=result.timestamp.isoformat()
        )
        
        # Geçici dosyayı temizle (arka planda)
        background_tasks.add_task(cleanup_temp_file, temp_path)
        
        return response
        
    except Exception as e:
        print(f"❌ API Hatası: {e}")
        raise HTTPException(status_code=500, detail=f"Analiz hatası: {str(e)}")

@app.post("/analyze/url")
async def analyze_video_url(request: AnalysisRequest):
    """
    URL'den video analizi (Google Drive, YouTube vb.)
    
    Args:
        request: Video URL'i ve analiz parametreleri
    
    Returns:
        Analiz sonuçları
    """
    try:
        if not request.video_url:
            raise HTTPException(status_code=400, detail="Video URL'i gerekli")
        
        # TODO: URL'den video indirme implementasyonu
        # Google Drive, YouTube vb. için özel işleme
        
        raise HTTPException(
            status_code=501, 
            detail="URL'den video analizi henüz implement edilmedi. Upload kullanın."
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"URL analizi hatası: {str(e)}")

@app.get("/reports/{filename}")
async def get_report(filename: str):
    """Rapor dosyasını indir"""
    file_path = REPORTS_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Rapor dosyası bulunamadı")
    
    # MIME type belirleme
    if filename.endswith('.html'):
        media_type = 'text/html'
    elif filename.endswith('.json'):
        media_type = 'application/json'
    elif filename.endswith('.csv'):
        media_type = 'text/csv'
    elif filename.endswith('.pdf'):
        media_type = 'application/pdf'
    else:
        media_type = 'application/octet-stream'
    
    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=filename
    )

@app.get("/analyses")
async def list_analyses():
    """Mevcut analizleri listele"""
    try:
        reports = []
        
        # Reports klasöründeki dosyaları tara
        for file_path in REPORTS_DIR.glob("*.json"):
            reports.append({
                "filename": file_path.name,
                "size": file_path.stat().st_size,
                "created": datetime.fromtimestamp(file_path.stat().st_ctime).isoformat()
            })
        
        return {
            "success": True,
            "count": len(reports),
            "reports": reports
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Liste hatası: {str(e)}")

@app.delete("/cleanup")
async def cleanup_old_files():
    """Eski geçici dosyaları temizle"""
    try:
        cleaned_count = 0
        
        # Temp klasörünü temizle
        for file_path in TEMP_DIR.glob("*"):
            if file_path.is_file():
                file_path.unlink()
                cleaned_count += 1
        
        return {
            "success": True,
            "message": f"{cleaned_count} geçici dosya temizlendi"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Temizleme hatası: {str(e)}")

async def cleanup_temp_file(file_path: Path):
    """Geçici dosyayı temizle"""
    try:
        if file_path.exists():
            file_path.unlink()
            print(f"🧹 Geçici dosya temizlendi: {file_path}")
    except Exception as e:
        print(f"⚠️ Geçici dosya temizleme hatası: {e}")

# Development server
if __name__ == "__main__":
    print("🚀 Video Analysis API başlatılıyor...")
    print("📊 Clean Code & SOLID prensipleri ile")
    print("🌐 API Dokümantasyonu: http://localhost:8000/docs")
    
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
