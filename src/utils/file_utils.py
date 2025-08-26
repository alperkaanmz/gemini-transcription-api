"""
File operation utilities
"""
import os
import mimetypes
from typing import Optional


class FileUtils:
    """Utility functions for file operations"""
    
    @staticmethod
    def get_mime_type(file_path: str) -> str:
        """Get MIME type for a file"""
        mime_type, _ = mimetypes.guess_type(file_path)
        
        if mime_type:
            return mime_type
        
        # Fallback for common video formats
        ext = os.path.splitext(file_path)[1].lower()
        video_types = {
            '.mp4': 'video/mp4',
            '.webm': 'video/webm',
            '.mov': 'video/quicktime',
            '.avi': 'video/x-msvideo',
            '.mkv': 'video/x-matroska'
        }
        
        return video_types.get(ext, 'video/mp4')
    
    @staticmethod
    def ensure_directory_exists(directory_path: str) -> None:
        """Create directory if it doesn't exist"""
        os.makedirs(directory_path, exist_ok=True)
    
    @staticmethod
    def clean_filename(filename: str) -> str:
        """Clean filename by removing special characters"""
        # Replace Turkish characters and special chars
        replacements = {
            'ü': 'u', 'ğ': 'g', 'ş': 's', 'ç': 'c', 
            'ı': 'i', 'ö': 'o', ' ': '_'
        }
        
        cleaned = filename
        for old, new in replacements.items():
            cleaned = cleaned.replace(old, new)
        
        # Remove any remaining special characters except underscore and dash
        cleaned = ''.join(c for c in cleaned if c.isalnum() or c in '_-')
        
        return cleaned
    
    @staticmethod
    def get_file_size_mb(file_path: str) -> float:
        """Get file size in MB"""
        if not os.path.exists(file_path):
            return 0.0
        
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024)
    
    @staticmethod
    def validate_video_file(file_path: str) -> bool:
        """Validate if file is a supported video format"""
        if not os.path.exists(file_path):
            return False
        
        supported_extensions = {'.mp4', '.webm', '.mov', '.avi', '.mkv'}
        file_extension = os.path.splitext(file_path)[1].lower()
        
        return file_extension in supported_extensions
