"""
Setup script for AI Video Enhancer
Helps with initial setup and verification
"""

import sys
import subprocess
import os
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required. Current version: {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True


def check_ffmpeg():
    """Check if FFmpeg is installed"""
    print("\nChecking FFmpeg installation...")
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✅ {version_line}")
            return True
        else:
            print("❌ FFmpeg not found or not working properly")
            return False
    except FileNotFoundError:
        print("❌ FFmpeg not found in system PATH")
        print("\nTo install FFmpeg:")
        print("  Windows: Download from https://ffmpeg.org/download.html")
        print("  Linux: sudo apt install ffmpeg")
        print("  macOS: brew install ffmpeg")
        return False
    except Exception as e:
        print(f"❌ Error checking FFmpeg: {str(e)}")
        return False


def check_cuda():
    """Check if CUDA is available"""
    print("\nChecking CUDA availability...")
    try:
        import torch
        if torch.cuda.is_available():
            print(f"✅ CUDA available: {torch.cuda.get_device_name(0)}")
            print(f"   CUDA Version: {torch.version.cuda}")
            return True
        else:
            print("⚠️  CUDA not available - will use CPU (slower)")
            print("   For GPU acceleration, install CUDA-enabled PyTorch:")
            print("   Visit: https://pytorch.org/get-started/locally/")
            return False
    except ImportError:
        print("⚠️  PyTorch not installed yet")
        return False


def create_directories():
    """Create necessary directories"""
    print("\nCreating directories...")
    directories = ['models', 'uploads', 'output', 'temp']
    
    for dir_name in directories:
        dir_path = Path(dir_name)
        dir_path.mkdir(exist_ok=True)
        print(f"✅ Created/verified: {dir_name}/")
    
    return True


def install_dependencies():
    """Install Python dependencies"""
    print("\nInstalling Python dependencies...")
    print("This may take several minutes...\n")
    
    try:
        subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'],
            check=True
        )
        
        subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'],
            check=True
        )
        
        print("\n✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Failed to install dependencies: {str(e)}")
        return False


def verify_installation():
    """Verify that all components are working"""
    print("\nVerifying installation...")
    
    try:
        # Test imports
        print("Testing imports...")
        import streamlit
        import cv2
        import torch
        import numpy
        import ffmpeg
        
        print("✅ All required packages imported successfully")
        
        # Test model handler
        print("\nTesting model handler...")
        from model_handler import ModelHandler
        model_handler = ModelHandler()
        models = model_handler.list_available_models()
        print(f"✅ Model handler initialized ({len(models)} models available)")
        
        # Test video processor
        print("\nTesting video processor...")
        from video_processor import VideoProcessor
        video_processor = VideoProcessor(model_handler)
        print("✅ Video processor initialized")
        
        # Test batch processor
        print("\nTesting batch processor...")
        from batch_processor import BatchProcessor
        batch_processor = BatchProcessor(video_processor)
        print("✅ Batch processor initialized")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Verification failed: {str(e)}")
        return False


def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "="*60)
    print("🎉 Setup Complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Activate virtual environment (if not already active)")
    print("   Windows: venv\\Scripts\\activate")
    print("   Linux/macOS: source venv/bin/activate")
    print("\n2. Start the application:")
    print("   streamlit run app.py")
    print("\n3. Access the web interface:")
    print("   http://localhost:8501")
    print("\n4. Download AI models from the sidebar (first time only)")
    print("\n5. Upload videos and start enhancing!")
    print("\n" + "="*60)
    print("\nFor help and documentation, see README.md")
    print("="*60 + "\n")


def main():
    """Main setup function"""
    print("="*60)
    print("AI Video Enhancer - Setup Script")
    print("="*60 + "\n")
    
    # Check prerequisites
    if not check_python_version():
        sys.exit(1)
    
    ffmpeg_ok = check_ffmpeg()
    cuda_ok = check_cuda()
    
    if not ffmpeg_ok:
        print("\n⚠️  FFmpeg is required. Please install it and run setup again.")
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Ask user if they want to install dependencies
    print("\n" + "="*60)
    response = input("Install Python dependencies? (y/n): ").lower().strip()
    
    if response == 'y':
        if not install_dependencies():
            print("\n⚠️  Dependency installation failed.")
            print("Try running manually: pip install -r requirements.txt")
            sys.exit(1)
        
        # Verify installation
        if not verify_installation():
            print("\n⚠️  Installation verification failed.")
            print("Some components may not be working correctly.")
            sys.exit(1)
    else:
        print("\nSkipping dependency installation.")
        print("Run manually: pip install -r requirements.txt")
    
    # Print next steps
    print_next_steps()


if __name__ == "__main__":
    main()
