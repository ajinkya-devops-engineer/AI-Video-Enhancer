"""
Configuration file for AI Video Enhancer
Centralized settings and constants
"""

from pathlib import Path

# Application Settings
APP_NAME = "AI Video Enhancer"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Transform videos with AI-powered upscaling technology"

# Directory Settings
BASE_DIR = Path(__file__).parent
MODELS_DIR = BASE_DIR / "models"
UPLOADS_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "output"
TEMP_DIR = BASE_DIR / "temp"

# Ensure directories exist
MODELS_DIR.mkdir(exist_ok=True)
UPLOADS_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)

# Video Processing Settings
VIDEO_EXTENSIONS = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm']
MAX_UPLOAD_SIZE_MB = 2000  # Maximum upload size in MB

# Resolution Presets
RESOLUTION_PRESETS = {
    "1080p": {
        "width": 1920,
        "height": 1080,
        "name": "Full HD",
        "description": "1920x1080 pixels"
    },
    "2K": {
        "width": 2560,
        "height": 1440,
        "name": "Quad HD",
        "description": "2560x1440 pixels"
    },
    "4K": {
        "width": 3840,
        "height": 2160,
        "name": "Ultra HD",
        "description": "3840x2160 pixels"
    },
    "8K": {
        "width": 7680,
        "height": 4320,
        "name": "8K UHD",
        "description": "7680x4320 pixels"
    }
}

# Video Encoding Settings
VIDEO_ENCODING = {
    "codec": "libx264",
    "crf": 18,  # Constant Rate Factor (0-51, lower is better quality)
    "preset": "slow",  # Encoding speed preset
    "pix_fmt": "yuv420p",  # Pixel format for compatibility
    "audio_codec": "copy"  # Copy audio without re-encoding
}

# Model Settings
MODEL_CONFIGS = {
    "general": {
        "name": "RealESRGAN_x4plus",
        "display_name": "General Purpose",
        "scale": 4,
        "description": "Optimized for standard video content (movies, vlogs, documentaries)",
        "url": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth",
        "file_size_mb": 64,
        "architecture": {
            "num_in_ch": 3,
            "num_out_ch": 3,
            "num_feat": 64,
            "num_block": 23,
            "num_grow_ch": 32
        }
    },
    "anime": {
        "name": "RealESRGAN_x4plus_anime_6B",
        "display_name": "Anime/Cartoon Optimized",
        "scale": 4,
        "description": "Specialized for animated content with enhanced detail preservation",
        "url": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.2.4/RealESRGAN_x4plus_anime_6B.pth",
        "file_size_mb": 17,
        "architecture": {
            "num_in_ch": 3,
            "num_out_ch": 3,
            "num_feat": 64,
            "num_block": 6,
            "num_grow_ch": 32
        }
    }
}

# Processing Settings
PROCESSING = {
    "max_workers": 1,  # Number of concurrent processing jobs
    "tile_size": 0,  # Tile size for processing (0 = auto)
    "tile_pad": 10,  # Padding for tiles
    "pre_pad": 0,  # Pre-padding
    "use_half_precision": True,  # Use FP16 for GPU (faster, less memory)
    "progress_update_interval": 1  # Seconds between progress updates
}

# Performance Settings
PERFORMANCE = {
    "gpu_memory_fraction": 0.9,  # Fraction of GPU memory to use
    "cpu_threads": 4,  # Number of CPU threads for processing
    "batch_size": 1,  # Batch size for frame processing
    "cache_size_mb": 512  # Cache size in MB
}

# UI Settings
UI_CONFIG = {
    "theme": "light",
    "page_icon": "🎬",
    "layout": "wide",
    "sidebar_state": "expanded",
    "auto_refresh_interval": 2,  # Seconds between auto-refresh
    "max_jobs_display": 20  # Maximum number of jobs to display
}

# Logging Settings
LOGGING = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "video_enhancer.log",
    "max_size_mb": 10,
    "backup_count": 3
}

# Error Messages
ERROR_MESSAGES = {
    "ffmpeg_not_found": "FFmpeg not found. Please install FFmpeg and add it to your system PATH.",
    "model_not_found": "AI model not found. Please download the model from the sidebar.",
    "invalid_video": "Invalid video file. Please upload a valid video file.",
    "processing_failed": "Video processing failed. Please check the error log.",
    "insufficient_memory": "Insufficient memory. Try processing a smaller video or lower resolution.",
    "cuda_error": "CUDA error. Try using CPU mode or updating your GPU drivers."
}

# Success Messages
SUCCESS_MESSAGES = {
    "upload_complete": "Video uploaded successfully!",
    "processing_complete": "Video enhancement completed!",
    "model_downloaded": "Model downloaded successfully!",
    "job_added": "Job added to queue successfully!"
}

# System Requirements
SYSTEM_REQUIREMENTS = {
    "python_min_version": "3.8",
    "ram_min_gb": 8,
    "ram_recommended_gb": 16,
    "disk_space_min_gb": 10,
    "ffmpeg_required": True,
    "cuda_optional": True
}

# Feature Flags
FEATURES = {
    "batch_processing": True,
    "real_time_preview": False,  # Future feature
    "video_comparison": False,  # Future feature
    "custom_models": False,  # Future feature
    "cloud_processing": False,  # Future feature
    "api_access": False  # Future feature
}

# API Settings (for future use)
API_CONFIG = {
    "enabled": False,
    "host": "0.0.0.0",
    "port": 8000,
    "cors_enabled": True,
    "rate_limit": 100  # Requests per hour
}

# Telemetry Settings
TELEMETRY = {
    "enabled": False,  # No telemetry by default
    "anonymous": True,
    "collect_errors": False,
    "collect_usage": False
}

# Development Settings
DEBUG = {
    "enabled": False,
    "verbose_logging": False,
    "save_intermediate_frames": False,
    "profile_performance": False
}


def get_config(section: str, key: str = None):
    """
    Get configuration value
    
    Args:
        section: Configuration section name
        key: Optional key within section
        
    Returns:
        Configuration value or section
    """
    sections = {
        "app": {
            "name": APP_NAME,
            "version": APP_VERSION,
            "description": APP_DESCRIPTION
        },
        "dirs": {
            "base": BASE_DIR,
            "models": MODELS_DIR,
            "uploads": UPLOADS_DIR,
            "output": OUTPUT_DIR,
            "temp": TEMP_DIR
        },
        "video": VIDEO_ENCODING,
        "models": MODEL_CONFIGS,
        "processing": PROCESSING,
        "performance": PERFORMANCE,
        "ui": UI_CONFIG,
        "features": FEATURES
    }
    
    if section not in sections:
        return None
    
    if key is None:
        return sections[section]
    
    return sections[section].get(key)


def validate_config():
    """Validate configuration settings"""
    issues = []
    
    # Check directories
    for dir_path in [MODELS_DIR, UPLOADS_DIR, OUTPUT_DIR, TEMP_DIR]:
        if not dir_path.exists():
            issues.append(f"Directory does not exist: {dir_path}")
    
    # Check video encoding settings
    if VIDEO_ENCODING["crf"] < 0 or VIDEO_ENCODING["crf"] > 51:
        issues.append("Invalid CRF value (must be 0-51)")
    
    # Check processing settings
    if PROCESSING["max_workers"] < 1:
        issues.append("max_workers must be at least 1")
    
    return issues


if __name__ == "__main__":
    # Validate configuration
    issues = validate_config()
    
    if issues:
        print("Configuration issues found:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✅ Configuration validated successfully")
        print(f"\nApplication: {APP_NAME} v{APP_VERSION}")
        print(f"Models directory: {MODELS_DIR}")
        print(f"Output directory: {OUTPUT_DIR}")
