"""
AI Model Handler for Video Upscaling
Manages multiple AI models optimized for different content types
"""

import cv2
import numpy as np
import torch
from pathlib import Path
from typing import Optional, Dict
import urllib.request
import os


class ModelHandler:
    """Handles AI models for video upscaling"""
    
    MODEL_CONFIGS = {
        "general": {
            "name": "RealESRGAN_x4plus",
            "scale": 4,
            "url": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth",
            "description": "General purpose model for standard video content"
        },
        "anime": {
            "name": "RealESRGAN_x4plus_anime_6B",
            "scale": 4,
            "url": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.2.4/RealESRGAN_x4plus_anime_6B.pth",
            "description": "Optimized model for anime and cartoon content"
        }
    }
    
    def __init__(self, models_dir: str = "models"):
        """
        Initialize model handler
        
        Args:
            models_dir: Directory to store model weights
        """
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.loaded_models: Dict[str, any] = {}
        
        print(f"Using device: {self.device}")
        
    def download_model(self, model_type: str, progress_callback: Optional[callable] = None) -> bool:
        """
        Download model weights if not present
        
        Args:
            model_type: Type of model (general or anime)
            progress_callback: Optional callback for download progress
            
        Returns:
            True if model is available
        """
        if model_type not in self.MODEL_CONFIGS:
            raise ValueError(f"Unknown model type: {model_type}")
        
        config = self.MODEL_CONFIGS[model_type]
        model_path = self.models_dir / f"{config['name']}.pth"
        
        if model_path.exists():
            return True
        
        try:
            print(f"Downloading {config['name']} model...")
            
            def report_progress(block_num, block_size, total_size):
                if progress_callback and total_size > 0:
                    progress = (block_num * block_size / total_size) * 100
                    progress_callback(min(progress, 100))
            
            urllib.request.urlretrieve(
                config['url'],
                str(model_path),
                reporthook=report_progress
            )
            
            print(f"Model downloaded successfully: {model_path}")
            return True
            
        except Exception as e:
            print(f"Failed to download model: {str(e)}")
            return False
    
    def load_model(self, model_type: str) -> bool:
        """
        Load AI model into memory
        
        Args:
            model_type: Type of model (general or anime)
            
        Returns:
            True if model loaded successfully
        """
        if model_type in self.loaded_models:
            return True
        
        try:
            # Import RealESRGAN here to avoid issues if not installed
            from basicsr.archs.rrdbnet_arch import RRDBNet
            from realesrgan import RealESRGANer
            
            config = self.MODEL_CONFIGS[model_type]
            model_path = self.models_dir / f"{config['name']}.pth"
            
            if not model_path.exists():
                print(f"Model not found. Downloading...")
                if not self.download_model(model_type):
                    return False
            
            # Determine model architecture based on type
            if model_type == "anime":
                model = RRDBNet(
                    num_in_ch=3,
                    num_out_ch=3,
                    num_feat=64,
                    num_block=6,
                    num_grow_ch=32,
                    scale=4
                )
            else:
                model = RRDBNet(
                    num_in_ch=3,
                    num_out_ch=3,
                    num_feat=64,
                    num_block=23,
                    num_grow_ch=32,
                    scale=4
                )
            
            # Initialize upsampler
            upsampler = RealESRGANer(
                scale=config['scale'],
                model_path=str(model_path),
                model=model,
                tile=0,
                tile_pad=10,
                pre_pad=0,
                half=torch.cuda.is_available(),
                device=self.device
            )
            
            self.loaded_models[model_type] = upsampler
            print(f"Model {model_type} loaded successfully")
            return True
            
        except Exception as e:
            print(f"Failed to load model: {str(e)}")
            return False
    
    def upscale_frame(
        self,
        frame: np.ndarray,
        target_width: int,
        target_height: int,
        model_type: str = "general"
    ) -> np.ndarray:
        """
        Upscale a single frame using AI model
        
        Args:
            frame: Input frame (BGR format)
            target_width: Target width
            target_height: Target height
            model_type: Model type to use
            
        Returns:
            Enhanced frame
        """
        try:
            # Load model if not already loaded
            if model_type not in self.loaded_models:
                if not self.load_model(model_type):
                    # Fallback to traditional upscaling
                    return cv2.resize(
                        frame,
                        (target_width, target_height),
                        interpolation=cv2.INTER_LANCZOS4
                    )
            
            upsampler = self.loaded_models[model_type]
            
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Upscale using AI model
            output, _ = upsampler.enhance(frame_rgb, outscale=4)
            
            # Convert back to BGR
            output_bgr = cv2.cvtColor(output, cv2.COLOR_RGB2BGR)
            
            # Resize to exact target dimensions if needed
            if output_bgr.shape[1] != target_width or output_bgr.shape[0] != target_height:
                output_bgr = cv2.resize(
                    output_bgr,
                    (target_width, target_height),
                    interpolation=cv2.INTER_LANCZOS4
                )
            
            return output_bgr
            
        except Exception as e:
            print(f"AI upscaling failed, using fallback: {str(e)}")
            # Fallback to traditional upscaling
            return cv2.resize(
                frame,
                (target_width, target_height),
                interpolation=cv2.INTER_LANCZOS4
            )
    
    def get_model_info(self, model_type: str) -> Dict:
        """
        Get information about a model
        
        Args:
            model_type: Model type
            
        Returns:
            Dictionary with model information
        """
        if model_type not in self.MODEL_CONFIGS:
            return {}
        
        config = self.MODEL_CONFIGS[model_type]
        model_path = self.models_dir / f"{config['name']}.pth"
        
        return {
            "name": config["name"],
            "description": config["description"],
            "scale": config["scale"],
            "downloaded": model_path.exists(),
            "loaded": model_type in self.loaded_models,
            "size_mb": model_path.stat().st_size / (1024 * 1024) if model_path.exists() else 0
        }
    
    def list_available_models(self) -> Dict[str, Dict]:
        """
        List all available models
        
        Returns:
            Dictionary of model information
        """
        return {
            model_type: self.get_model_info(model_type)
            for model_type in self.MODEL_CONFIGS.keys()
        }
    
    def unload_model(self, model_type: str):
        """
        Unload model from memory
        
        Args:
            model_type: Model type to unload
        """
        if model_type in self.loaded_models:
            del self.loaded_models[model_type]
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            print(f"Model {model_type} unloaded")
    
    def unload_all_models(self):
        """Unload all models from memory"""
        self.loaded_models.clear()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        print("All models unloaded")
