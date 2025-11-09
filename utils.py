"""
Utility functions for AI Video Enhancer
Common helper functions used across the application
"""

import os
import sys
import time
import psutil
import hashlib
from pathlib import Path
from typing import Union, Optional, Tuple, Dict
from datetime import datetime, timedelta


def format_bytes(bytes_size: Union[int, float]) -> str:
    """
    Format bytes to human-readable size
    
    Args:
        bytes_size: Size in bytes
        
    Returns:
        Formatted string (e.g., "1.5 GB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"


def format_time(seconds: Union[int, float]) -> str:
    """
    Format seconds to human-readable time
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted string (e.g., "1h 30m 45s")
    """
    if seconds < 0:
        return "0s"
    
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        if secs > 0:
            return f"{hours}h {minutes}m {secs}s"
        return f"{hours}h {minutes}m"


def format_duration(seconds: Union[int, float]) -> str:
    """
    Format duration in a more readable way
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted string
    """
    td = timedelta(seconds=int(seconds))
    days = td.days
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0 or not parts:
        parts.append(f"{seconds}s")
    
    return " ".join(parts)


def get_file_hash(file_path: Union[str, Path], algorithm: str = 'md5') -> str:
    """
    Calculate file hash
    
    Args:
        file_path: Path to file
        algorithm: Hash algorithm (md5, sha1, sha256)
        
    Returns:
        Hexadecimal hash string
    """
    hash_func = hashlib.new(algorithm)
    
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_func.update(chunk)
    
    return hash_func.hexdigest()


def get_file_info(file_path: Union[str, Path]) -> Dict:
    """
    Get detailed file information
    
    Args:
        file_path: Path to file
        
    Returns:
        Dictionary with file information
    """
    path = Path(file_path)
    
    if not path.exists():
        return {}
    
    stat = path.stat()
    
    return {
        'name': path.name,
        'path': str(path.absolute()),
        'size': stat.st_size,
        'size_formatted': format_bytes(stat.st_size),
        'created': datetime.fromtimestamp(stat.st_ctime),
        'modified': datetime.fromtimestamp(stat.st_mtime),
        'extension': path.suffix,
        'is_file': path.is_file(),
        'is_dir': path.is_dir()
    }


def get_system_info() -> Dict:
    """
    Get system information
    
    Returns:
        Dictionary with system information
    """
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    info = {
        'cpu': {
            'percent': cpu_percent,
            'count': psutil.cpu_count(),
            'count_physical': psutil.cpu_count(logical=False)
        },
        'memory': {
            'total': memory.total,
            'available': memory.available,
            'used': memory.used,
            'percent': memory.percent,
            'total_formatted': format_bytes(memory.total),
            'available_formatted': format_bytes(memory.available),
            'used_formatted': format_bytes(memory.used)
        },
        'disk': {
            'total': disk.total,
            'used': disk.used,
            'free': disk.free,
            'percent': disk.percent,
            'total_formatted': format_bytes(disk.total),
            'used_formatted': format_bytes(disk.used),
            'free_formatted': format_bytes(disk.free)
        },
        'platform': sys.platform,
        'python_version': sys.version
    }
    
    # GPU information
    try:
        import torch
        if torch.cuda.is_available():
            info['gpu'] = {
                'available': True,
                'name': torch.cuda.get_device_name(0),
                'count': torch.cuda.device_count(),
                'cuda_version': torch.version.cuda,
                'memory_allocated': torch.cuda.memory_allocated(0),
                'memory_reserved': torch.cuda.memory_reserved(0)
            }
        else:
            info['gpu'] = {'available': False}
    except ImportError:
        info['gpu'] = {'available': False, 'error': 'PyTorch not installed'}
    
    return info


def ensure_dir(directory: Union[str, Path]) -> Path:
    """
    Ensure directory exists, create if it doesn't
    
    Args:
        directory: Directory path
        
    Returns:
        Path object
    """
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path


def clean_directory(directory: Union[str, Path], pattern: str = "*", recursive: bool = False):
    """
    Clean files from directory
    
    Args:
        directory: Directory path
        pattern: File pattern to match
        recursive: Clean recursively
    """
    path = Path(directory)
    
    if not path.exists():
        return
    
    if recursive:
        files = path.rglob(pattern)
    else:
        files = path.glob(pattern)
    
    for file in files:
        if file.is_file():
            try:
                file.unlink()
            except Exception as e:
                print(f"Failed to delete {file}: {e}")


def get_available_space(directory: Union[str, Path]) -> int:
    """
    Get available disk space in bytes
    
    Args:
        directory: Directory path
        
    Returns:
        Available space in bytes
    """
    path = Path(directory)
    
    if not path.exists():
        path = path.parent
    
    stat = psutil.disk_usage(str(path))
    return stat.free


def check_disk_space(directory: Union[str, Path], required_bytes: int) -> bool:
    """
    Check if enough disk space is available
    
    Args:
        directory: Directory path
        required_bytes: Required space in bytes
        
    Returns:
        True if enough space available
    """
    available = get_available_space(directory)
    return available >= required_bytes


def estimate_output_size(input_size: int, scale_factor: float = 1.5) -> int:
    """
    Estimate output file size
    
    Args:
        input_size: Input file size in bytes
        scale_factor: Estimated size increase factor
        
    Returns:
        Estimated output size in bytes
    """
    return int(input_size * scale_factor)


def validate_video_file(file_path: Union[str, Path]) -> Tuple[bool, Optional[str]]:
    """
    Validate video file
    
    Args:
        file_path: Path to video file
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    path = Path(file_path)
    
    # Check if file exists
    if not path.exists():
        return False, "File does not exist"
    
    # Check if it's a file
    if not path.is_file():
        return False, "Not a file"
    
    # Check file extension
    valid_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm']
    if path.suffix.lower() not in valid_extensions:
        return False, f"Invalid file extension. Supported: {', '.join(valid_extensions)}"
    
    # Check file size
    if path.stat().st_size == 0:
        return False, "File is empty"
    
    # Try to open with OpenCV
    try:
        import cv2
        cap = cv2.VideoCapture(str(path))
        if not cap.isOpened():
            return False, "Cannot open video file"
        cap.release()
    except Exception as e:
        return False, f"Error opening video: {str(e)}"
    
    return True, None


def get_video_metadata(file_path: Union[str, Path]) -> Optional[Dict]:
    """
    Get video metadata using OpenCV
    
    Args:
        file_path: Path to video file
        
    Returns:
        Dictionary with video metadata or None
    """
    try:
        import cv2
        
        cap = cv2.VideoCapture(str(file_path))
        
        if not cap.isOpened():
            return None
        
        metadata = {
            'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'fps': cap.get(cv2.CAP_PROP_FPS),
            'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            'codec': int(cap.get(cv2.CAP_PROP_FOURCC)),
            'duration': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) / cap.get(cv2.CAP_PROP_FPS)
        }
        
        cap.release()
        
        return metadata
        
    except Exception as e:
        print(f"Error getting video metadata: {e}")
        return None


def create_progress_bar(current: int, total: int, width: int = 50) -> str:
    """
    Create a text-based progress bar
    
    Args:
        current: Current progress
        total: Total items
        width: Width of progress bar
        
    Returns:
        Progress bar string
    """
    if total == 0:
        percent = 0
    else:
        percent = current / total
    
    filled = int(width * percent)
    bar = '█' * filled + '░' * (width - filled)
    
    return f"[{bar}] {percent*100:.1f}%"


def timing_decorator(func):
    """
    Decorator to measure function execution time
    
    Args:
        func: Function to decorate
        
    Returns:
        Wrapped function
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        elapsed = end_time - start_time
        print(f"{func.__name__} took {format_time(elapsed)}")
        
        return result
    
    return wrapper


class Timer:
    """Context manager for timing code blocks"""
    
    def __init__(self, name: str = "Operation"):
        self.name = name
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, *args):
        self.end_time = time.time()
        elapsed = self.end_time - self.start_time
        print(f"{self.name} took {format_time(elapsed)}")
    
    def elapsed(self) -> float:
        """Get elapsed time"""
        if self.start_time is None:
            return 0.0
        
        end = self.end_time if self.end_time else time.time()
        return end - self.start_time


def safe_filename(filename: str) -> str:
    """
    Create a safe filename by removing invalid characters
    
    Args:
        filename: Original filename
        
    Returns:
        Safe filename
    """
    # Remove invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip('. ')
    
    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext
    
    return filename


if __name__ == "__main__":
    # Test utilities
    print("Testing utility functions...\n")
    
    print(f"Format bytes: {format_bytes(1536000000)}")
    print(f"Format time: {format_time(3665)}")
    print(f"Format duration: {format_duration(90125)}")
    
    print("\nSystem Information:")
    sys_info = get_system_info()
    print(f"CPU: {sys_info['cpu']['count']} cores, {sys_info['cpu']['percent']}% usage")
    print(f"Memory: {sys_info['memory']['used_formatted']} / {sys_info['memory']['total_formatted']}")
    print(f"GPU: {sys_info['gpu']['available']}")
    
    print("\nProgress bar:")
    for i in range(0, 101, 10):
        print(create_progress_bar(i, 100))
    
    print("\n✅ All tests passed!")
