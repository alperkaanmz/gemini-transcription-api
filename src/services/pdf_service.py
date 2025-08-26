"""
PDF generation services following SOLID principles
"""
import os
import tempfile
import requests
from typing import Dict, Any, Optional
from ..models import AnalysisResult


class PDFService:
    """
    PDF generation service following Single Responsibility Principle
    Handles both ReportLab and API-based PDF generation
    """
    
    def __init__(self, api_url: str = "https://rapor.onrender.com/generate-report"):
        self.api_url = api_url
    
    def generate_reportlab_pdf(self, result: AnalysisResult, base_filename: str, reports_dir: str, enabled: bool = False) -> Optional[str]:
        """Generate PDF using ReportLab library - disabled by default"""
        if not enabled:
            return None
            
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            from reportlab.lib.enums import TA_CENTER, TA_LEFT
            
            pdf_path = os.path.join(reports_dir, f"{base_filename}_report.pdf")
            
            # Create PDF document
            doc = SimpleDocTemplate(pdf_path, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=colors.darkblue
            )
            story.append(Paragraph("🎯 Video Analiz Raporu", title_style))
            story.append(Spacer(1, 20))
            
            # Candidate info
            story.append(Paragraph(f"<b>Aday:</b> {result.candidate_name}", styles['Normal']))
            story.append(Paragraph(f"<b>Pozisyon:</b> {result.position}", styles['Normal']))
            story.append(Paragraph(f"<b>Analiz Tarihi:</b> {result.timestamp.strftime('%d/%m/%Y %H:%M:%S')}", styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Emotion Analysis
            story.append(Paragraph("😊 Duygu Analizi", styles['Heading2']))
            emotion_data = [
                ['Duygu', 'Değer (%)'],
                ['Mutluluk', f"{result.emotion_data.happiness:.1f}%"],
                ['Üzüntü', f"{result.emotion_data.sadness:.1f}%"],
                ['Öfke', f"{result.emotion_data.anger:.1f}%"],
                ['Şaşırma', f"{result.emotion_data.surprise:.1f}%"],
                ['Korku', f"{result.emotion_data.fear:.1f}%"],
                ['Nötr', f"{result.emotion_data.neutral:.1f}%"],
                ['Güven', f"{result.emotion_data.confidence:.1f}%"]
            ]
            
            emotion_table = Table(emotion_data)
            emotion_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(emotion_table)
            story.append(Spacer(1, 20))
            
            # Sentiment Analysis
            story.append(Paragraph("📊 Genel Değerlendirme", styles['Heading2']))
            sentiment_data = [
                ['Kategori', 'Değer (%)'],
                ['Pozitif', f"{result.sentiment_data.positive_percentage:.1f}%"],
                ['Negatif', f"{result.sentiment_data.negative_percentage:.1f}%"],
                ['Nötr', f"{result.sentiment_data.neutral_percentage:.1f}%"],
                ['Stres Seviyesi', f"{result.sentiment_data.stress_level:.1f}%"],
                ['Motivasyon', f"{result.sentiment_data.motivation_level:.1f}%"],
                ['İletişim Becerisi', f"{result.sentiment_data.communication_skill:.1f}%"]
            ]
            
            sentiment_table = Table(sentiment_data)
            sentiment_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(sentiment_table)
            story.append(Spacer(1, 20))
            
            # MBTI Analysis
            story.append(Paragraph("🧠 MBTI Kişilik Analizi", styles['Heading2']))
            story.append(Paragraph(f"<b>Tahmin Edilen Tip:</b> {result.mbti_data.predicted_type}", styles['Normal']))
            story.append(Paragraph(f"<b>Güven Seviyesi:</b> {result.mbti_data.confidence_level:.1f}%", styles['Normal']))
            story.append(Spacer(1, 10))
            
            mbti_data = [
                ['MBTI Boyutu', 'Değer (%)'],
                ['Extraversion/Introversion', f"{result.mbti_data.extraversion_introversion:.1f}%"],
                ['Sensing/Intuition', f"{result.mbti_data.sensing_intuition:.1f}%"],
                ['Thinking/Feeling', f"{result.mbti_data.thinking_feeling:.1f}%"],
                ['Judging/Perceiving', f"{result.mbti_data.judging_perceiving:.1f}%"]
            ]
            
            mbti_table = Table(mbti_data)
            mbti_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(mbti_table)
            story.append(Spacer(1, 20))
            
            # Cost Analysis
            story.append(Paragraph("💰 Maliyet Analizi", styles['Heading2']))
            story.append(Paragraph(f"<b>Toplam Token:</b> {result.cost_report.total_tokens:,}", styles['Normal']))
            story.append(Paragraph(f"<b>Input Token:</b> {result.cost_report.input_tokens:,}", styles['Normal']))
            story.append(Paragraph(f"<b>Output Token:</b> {result.cost_report.output_tokens:,}", styles['Normal']))
            story.append(Paragraph(f"<b>Toplam Maliyet:</b> ${result.cost_report.total_cost_usd:.6f}", styles['Normal']))
            story.append(Paragraph(f"<b>TL Karşılığı:</b> ₺{result.cost_report.total_cost_usd * 34:.4f}", styles['Normal']))
            
            # Build PDF
            doc.build(story)
            print("✅ Profesyonel İK PDF raporu başarıyla oluşturuldu!")
            return pdf_path
            
        except ImportError:
            print("⚠️ ReportLab kütüphanesi bulunamadı - PDF oluşturulamadı")
            return None
        except Exception as e:
            print(f"⚠️ PDF oluşturma hatası: {e}")
            return None
    
    def generate_api_pdf(self, csv_path: str, candidate_name: str, position: str, base_filename: str, reports_dir: str, enabled: bool = True) -> Optional[str]:
        """Generate PDF using external API - enabled by default"""
        if not enabled or not csv_path:
            return None
            
        try:
            print("🌐 API üzerinden PDF oluşturmaya çalışılıyor...")
            print("🌐 PDF API'ye bağlanılıyor...")
            
            # Read CSV data
            with open(csv_path, 'r', encoding='utf-8') as f:
                csv_content = f.read()
            
            print(f"📋 CSV boyutu: {len(csv_content)} karakter")
            if len(csv_content) > 500:
                print(f"📋 CSV başlangıcı: {csv_content[:500]}...")
            else:
                print(f"📋 CSV içeriği: {csv_content}")
            
            # CSV dosyasını multipart/form-data ile gönder (orijinal format)
            with open(csv_path, 'rb') as f:
                files = {'file': f}
                data = {
                    'candidate_name': candidate_name,
                    'position': position,
                    'format': 'professional_hr_report'
                }
                
                print(f"🌐 API'ye gönderilen data: {data}")
                
                # Make API request with original format
                response = requests.post(
                    self.api_url,
                    files=files,
                    data=data,
                    timeout=120
                )
            
            print(f"🌐 API Response Status: {response.status_code}")
            print(f"🌐 API Response Headers: {dict(response.headers)}")
            print(f"🌐 API Response Content-Type: {response.headers.get('content-type', 'unknown')}")
            
            if response.status_code == 200:
                # Save PDF
                api_pdf_path = os.path.join(reports_dir, f"{base_filename}_api_report.pdf")
                with open(api_pdf_path, 'wb') as f:
                    f.write(response.content)
                
                print(f"✅ API üzerinden PDF oluşturuldu: {api_pdf_path} ({len(response.content)} bytes)")
                return api_pdf_path
            else:
                print(f"❌ API PDF oluşturma başarısız: {response.status_code}")
                if response.text:
                    print(f"🔍 API Error: {response.text[:200]}...")
                return None
                
        except requests.exceptions.Timeout:
            print("⚠️ API zaman aşımı - PDF oluşturulamadı")
            return None
        except requests.exceptions.ConnectionError:
            print("⚠️ API bağlantı hatası - PDF oluşturulamadı")
            return None
        except Exception as e:
            print(f"⚠️ API PDF hatası: {e}")
            return None
