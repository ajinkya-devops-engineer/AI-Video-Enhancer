"""
Video Processing Engine with AI-powered upscaling
Handles video enhancement, audio preservation, and frame processing
"""

import cv2
import numpy as np
import ffmpeg
import torch
from pathlib import Path
from typing import Optional, Callable, Dict, Tuple
import tempfile
import shutil
import subprocess
import json


class VideoProcessor:
    """Core video processing engine with AI upscaling capabilities"""
    
    RESOLUTION_PRESETS = {
        "1080p": (1920, 1080),
        "2K": (2560, 1440),
        "4K": (3840, 2160),
        "8K": (7680, 4320)
    }
    
    def __init__(self, model_handler):
        """
        Initialize video processor
        
        Args:
            model_handler: AI model handler for upscaling
        """
        self.model_handler = model_handler
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
    def get_video_info(self, video_path: str) -> Dict:
        """
        Extract video metadata
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary containing video information
        """
        try:
            probe = ffmpeg.probe(video_path)
            video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
            audio_info = next((s for s in probe['streams'] if s['codec_type'] == 'audio'), None)
            
            return {
                'width': int(video_info['width']),
                'height': int(video_info['height']),
                'fps': eval(video_info['r_frame_rate']),
                'total_frames': int(video_info.get('nb_frames', 0)),
                'duration': float(probe['format']['duration']),
                'codec': video_info['codec_name'],
                'has_audio': audio_info is not None,
                'audio_codec': audio_info['codec_name'] if audio_info else None,
                'audio_bitrate': audio_info.get('bit_rate', 'N/A') if audio_info else None
            }
        except Exception as e:
            raise Exception(f"Failed to get video info: {str(e)}")
    
    def calculate_target_resolution(
        self, 
        source_width: int, 
        source_height: int, 
        target_preset: str
    ) -> Tuple[int, int]:
        """
        Calculate target resolution maintaining aspect ratio
        
        Args:
            source_width: Original video width
            source_height: Original video height
            target_preset: Target resolution preset (1080p, 2K, 4K, 8K)
            
        Returns:
            Tuple of (target_width, target_height)
        """
        if target_preset not in self.RESOLUTION_PRESETS:
            raise ValueError(f"Invalid resolution preset: {target_preset}")
        
        target_width, target_height = self.RESOLUTION_PRESETS[target_preset]
        
        # Calculate aspect ratio
        source_aspect = source_width / source_height
        target_aspect = target_width / target_height
        
        # Adjust to maintain aspect ratio
        if source_aspect > target_aspect:
            # Width is the limiting factor
            final_width = target_width
            final_height = int(target_width / source_aspect)
        else:
            # Height is the limiting factor
            final_height = target_height
            final_width = int(target_height * source_aspect)
        
        # Ensure dimensions are even (required for video encoding)
        final_width = final_width if final_width % 2 == 0 else final_width - 1
        final_height = final_height if final_height % 2 == 0 else final_height - 1
        
        return final_width, final_height
    
    def extract_audio(self, video_path: str, audio_path: str) -> bool:
        """
        Extract audio from video preserving original quality
        
        Args:
            video_path: Input video path
            audio_path: Output audio path
            
        Returns:
            True if audio extracted successfully
        """
        try:
            # Extract audio without re-encoding to preserve quality
            stream = ffmpeg.input(video_path)
            stream = ffmpeg.output(stream.audio, audio_path, acodec='copy')
            ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)
            return True
        except ffmpeg.Error as e:
            print(f"Audio extraction failed: {e.stderr.decode()}")
            return False
    
    def merge_audio_video(
        self, 
        video_path: str, 
        audio_path: str, 
        output_path: str
    ) -> bool:
        """
        Merge video and audio streams
        
        Args:
            video_path: Enhanced video path (no audio)
            audio_path: Original audio path
            output_path: Final output path
            
        Returns:
            True if merge successful
        """
        try:
            video = ffmpeg.input(video_path)
            audio = ffmpeg.input(audio_path)
            
            stream = ffmpeg.output(
                video, 
                audio, 
                output_path,
                vcodec='copy',
                acodec='copy',
                strict='experimental'
            )
            
            ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)
            return True
        except ffmpeg.Error as e:
            print(f"Audio/Video merge failed: {e.stderr.decode()}")
            return False
    
    def process_video(
        self,
        input_path: str,
        output_path: str,
        target_resolution: str,
        model_type: str = "general",
        progress_callback: Optional[Callable[[int, int, Dict], None]] = None
    ) -> bool:
        """
        Process video with AI upscaling
        
        Args:
            input_path: Input video path
            output_path: Output video path
            target_resolution: Target resolution preset
            model_type: AI model type (general or anime)
            progress_callback: Callback function for progress updates
            
        Returns:
            True if processing successful
        """
        temp_dir = None
        
        try:
            # Get video information
            video_info = self.get_video_info(input_path)
            
            # Calculate target resolution
            target_width, target_height = self.calculate_target_resolution(
                video_info['width'],
                video_info['height'],
                target_resolution
            )
            
            # Create temporary directory
            temp_dir = tempfile.mkdtemp()
            temp_audio = Path(temp_dir) / "audio.aac"
            temp_video = Path(temp_dir) / "video_no_audio.mp4"
            
            # Extract audio if present
            has_audio = False
            if video_info['has_audio']:
                has_audio = self.extract_audio(input_path, str(temp_audio))
            
            # Open video capture
            cap = cv2.VideoCapture(input_path)
            
            # Get total frames
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            if total_frames == 0:
                total_frames = int(video_info['fps'] * video_info['duration'])
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            # Setup video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(
                str(temp_video),
                fourcc,
                fps,
                (target_width, target_height)
            )
            
            frame_count = 0
            
            # Process frames
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Upscale frame using AI model
                enhanced_frame = self.model_handler.upscale_frame(
                    frame,
                    target_width,
                    target_height,
                    model_type
                )
                
                # Write enhanced frame
                out.write(enhanced_frame)
                
                frame_count += 1
                
                # Progress callback
                if progress_callback:
                    progress_info = {
                        'current_frame': frame_count,
                        'total_frames': total_frames,
                        'fps': fps,
                        'resolution': f"{target_width}x{target_height}",
                        'model': model_type
                    }
                    progress_callback(frame_count, total_frames, progress_info)
            
            # Release resources
            cap.release()
            out.release()
            
            # Re-encode with better quality using ffmpeg
            temp_video_hq = Path(temp_dir) / "video_hq.mp4"
            
            stream = ffmpeg.input(str(temp_video))
            stream = ffmpeg.output(
                stream,
                str(temp_video_hq),
                vcodec='libx264',
                crf=18,
                preset='slow',
                pix_fmt='yuv420p'
            )
            ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)
            
            # Merge audio if present
            if has_audio and temp_audio.exists():
                success = self.merge_audio_video(
                    str(temp_video_hq),
                    str(temp_audio),
                    output_path
                )
            else:
                # Just copy the video
                shutil.copy(str(temp_video_hq), output_path)
                success = True
            
            return success
            
        except Exception as e:
            print(f"Video processing failed: {str(e)}")
            return False
            
        finally:
            # Cleanup temporary directory
            if temp_dir and Path(temp_dir).exists():
                shutil.rmtree(temp_dir, ignore_errors=True)
    
    def estimate_processing_time(
        self,
        video_path: str,
        target_resolution: str
    ) -> float:
        """
        Estimate processing time in seconds
        
        Args:
            video_path: Input video path
            target_resolution: Target resolution preset
            
        Returns:
            Estimated time in seconds
        """
        try:
            video_info = self.get_video_info(video_path)
            total_frames = video_info['total_frames']
            
            if total_frames == 0:
                total_frames = int(video_info['fps'] * video_info['duration'])
            
            # Rough estimation: ~0.5-2 seconds per frame depending on resolution
            scale_factor = {
                "1080p": 0.5,
                "2K": 1.0,
                "4K": 1.5,
                "8K": 2.0
            }.get(target_resolution, 1.0)
            
            # Adjust for GPU availability
            if torch.cuda.is_available():
                scale_factor *= 0.3  # GPU is much faster
            
            return total_frames * scale_factor
            
        except Exception:
            return 0.0
