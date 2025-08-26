"""
Gemini API service for video processing
"""
import time
from typing import Any, Dict, Tuple
import google.generativeai as genai
from ..utils import FileUtils, CostCalculator
from ..models import CostReport


class GeminiService:
    """Service for interacting with Gemini API"""
    
    def __init__(self, api_key: str, model_name: str = 'gemini-2.5-flash-lite'):
        """Initialize Gemini service
        
        Args:
            api_key: Google AI API key
            model_name: Gemini model to use
        """
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.cost_calculator = CostCalculator()
    
    def upload_video(self, video_path: str) -> Any:
        """Upload video to Gemini API
        
        Args:
            video_path: Path to video file
            
        Returns:
            Uploaded video file object
            
        Raises:
            ValueError: If video processing fails
        """
        if not FileUtils.validate_video_file(video_path):
            raise ValueError(f"Invalid video file: {video_path}")
        
        print(f"Video yükleniyor: {video_path}")
        mime_type = FileUtils.get_mime_type(video_path)
        video_file = genai.upload_file(path=video_path, mime_type=mime_type)
        print(f"Video yüklendi: {video_file.uri}")
        
        # Wait for video processing
        print("Video işlenmeyi bekliyor...")
        while video_file.state.name == "PROCESSING":
            print(".", end="", flush=True)
            time.sleep(2)
            video_file = genai.get_file(video_file.name)
        
        print()  # New line after dots
        
        if video_file.state.name == "FAILED":
            raise ValueError(f"Video işleme başarısız: {video_file.state.name}")
        
        print(f"Video hazır: {video_file.state.name}")
        return video_file
    
    def generate_content(self, prompt: str, video_file: Any = None) -> Tuple[str, Dict[str, int]]:
        """Generate content using Gemini model
        
        Args:
            prompt: Text prompt for generation
            video_file: Optional video file object
            
        Returns:
            Tuple of (generated_text, token_usage)
        """
        try:
            if video_file:
                response = self.model.generate_content([prompt, video_file])
            else:
                response = self.model.generate_content(prompt)
            
            # Extract token usage
            token_usage = {
                'input': response.usage_metadata.prompt_token_count,
                'output': response.usage_metadata.candidates_token_count,
                'total': response.usage_metadata.total_token_count
            }
            
            # Track costs
            self.cost_calculator.add_token_usage(
                token_usage['input'], 
                token_usage['output']
            )
            
            # Print token usage
            cost = CostCalculator.calculate_single_operation_cost(
                token_usage['input'], 
                token_usage['output']
            )
            print(f"Token kullanımı: Input={token_usage['input']}, "
                  f"Output={token_usage['output']}, Total={token_usage['total']}")
            print(f"İşlem maliyeti: ${cost:.6f}")
            
            return response.text, token_usage
            
        except Exception as e:
            print(f"❌ Content generation error: {e}")
            raise
    
    def get_cost_report(self) -> CostReport:
        """Get comprehensive cost report"""
        return self.cost_calculator.get_cost_report()
    
    def print_cost_summary(self) -> None:
        """Print cost summary"""
        self.cost_calculator.print_cost_summary()
