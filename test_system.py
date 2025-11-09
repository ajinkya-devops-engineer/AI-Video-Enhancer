"""
System Test Script for AI Video Enhancer
Tests all components and verifies installation
"""

import sys
import os
from pathlib import Path


def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)


def print_test(name, status, message=""):
    """Print test result"""
    symbol = "✅" if status else "❌"
    print(f"{symbol} {name}")
    if message:
        print(f"   {message}")


def test_python_version():
    """Test Python version"""
    print_header("Python Version")
    
    version = sys.version_info
    required = (3, 8)
    
    current = f"{version.major}.{version.minor}.{version.micro}"
    print(f"Current version: {current}")
    
    is_valid = version >= required
    print_test(
        "Python Version Check",
        is_valid,
        f"Required: {required[0]}.{required[1]}+"
    )
    
    return is_valid


def test_imports():
    """Test required imports"""
    print_header("Package Imports")
    
    packages = {
        'streamlit': 'Streamlit',
        'cv2': 'OpenCV',
        'torch': 'PyTorch',
        'numpy': 'NumPy',
        'PIL': 'Pillow',
        'ffmpeg': 'FFmpeg-Python',
        'psutil': 'psutil'
    }
    
    all_ok = True
    
    for module, name in packages.items():
        try:
            __import__(module)
            print_test(f"{name}", True)
        except ImportError as e:
            print_test(f"{name}", False, str(e))
            all_ok = False
    
    return all_ok


def test_ffmpeg():
    """Test FFmpeg installation"""
    print_header("FFmpeg")
    
    import subprocess
    
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print_test("FFmpeg Installation", True, version_line)
            return True
        else:
            print_test("FFmpeg Installation", False, "FFmpeg not working")
            return False
            
    except FileNotFoundError:
        print_test("FFmpeg Installation", False, "FFmpeg not found in PATH")
        return False
    except Exception as e:
        print_test("FFmpeg Installation", False, str(e))
        return False


def test_cuda():
    """Test CUDA availability"""
    print_header("CUDA Support")
    
    try:
        import torch
        
        cuda_available = torch.cuda.is_available()
        
        if cuda_available:
            device_name = torch.cuda.get_device_name(0)
            cuda_version = torch.version.cuda
            device_count = torch.cuda.device_count()
            
            print_test("CUDA Available", True)
            print(f"   GPU: {device_name}")
            print(f"   CUDA Version: {cuda_version}")
            print(f"   Device Count: {device_count}")
        else:
            print_test("CUDA Available", False, "No CUDA-capable GPU detected")
            print("   Note: Processing will use CPU (slower)")
        
        return True  # Not a critical failure
        
    except Exception as e:
        print_test("CUDA Check", False, str(e))
        return True


def test_directories():
    """Test directory structure"""
    print_header("Directory Structure")
    
    required_dirs = ['models', 'uploads', 'output', 'temp']
    all_ok = True
    
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        
        if dir_path.exists():
            print_test(f"{dir_name}/", True, "Exists")
        else:
            try:
                dir_path.mkdir(exist_ok=True)
                print_test(f"{dir_name}/", True, "Created")
            except Exception as e:
                print_test(f"{dir_name}/", False, str(e))
                all_ok = False
    
    return all_ok


def test_modules():
    """Test custom modules"""
    print_header("Custom Modules")
    
    modules = [
        'model_handler',
        'video_processor',
        'batch_processor',
        'utils',
        'config'
    ]
    
    all_ok = True
    
    for module_name in modules:
        try:
            __import__(module_name)
            print_test(f"{module_name}.py", True)
        except Exception as e:
            print_test(f"{module_name}.py", False, str(e))
            all_ok = False
    
    return all_ok


def test_model_handler():
    """Test model handler functionality"""
    print_header("Model Handler")
    
    try:
        from model_handler import ModelHandler
        
        handler = ModelHandler()
        print_test("ModelHandler Initialization", True)
        
        models = handler.list_available_models()
        print_test("List Models", True, f"{len(models)} models available")
        
        for model_type, info in models.items():
            status = "Downloaded" if info['downloaded'] else "Not downloaded"
            print(f"   {model_type}: {status}")
        
        return True
        
    except Exception as e:
        print_test("Model Handler", False, str(e))
        return False


def test_video_processor():
    """Test video processor functionality"""
    print_header("Video Processor")
    
    try:
        from model_handler import ModelHandler
        from video_processor import VideoProcessor
        
        handler = ModelHandler()
        processor = VideoProcessor(handler)
        
        print_test("VideoProcessor Initialization", True)
        
        # Test resolution presets
        presets = processor.RESOLUTION_PRESETS
        print_test("Resolution Presets", True, f"{len(presets)} presets available")
        
        for preset, (width, height) in presets.items():
            print(f"   {preset}: {width}x{height}")
        
        return True
        
    except Exception as e:
        print_test("Video Processor", False, str(e))
        return False


def test_batch_processor():
    """Test batch processor functionality"""
    print_header("Batch Processor")
    
    try:
        from model_handler import ModelHandler
        from video_processor import VideoProcessor
        from batch_processor import BatchProcessor
        
        handler = ModelHandler()
        video_proc = VideoProcessor(handler)
        batch_proc = BatchProcessor(video_proc)
        
        print_test("BatchProcessor Initialization", True)
        
        status = batch_proc.get_queue_status()
        print_test("Queue Status", True, f"{status['total']} jobs")
        
        return True
        
    except Exception as e:
        print_test("Batch Processor", False, str(e))
        return False


def test_system_resources():
    """Test system resources"""
    print_header("System Resources")
    
    try:
        from utils import get_system_info, format_bytes
        
        info = get_system_info()
        
        print(f"CPU: {info['cpu']['count']} cores")
        print(f"     Usage: {info['cpu']['percent']}%")
        
        print(f"\nMemory: {info['memory']['total_formatted']}")
        print(f"        Available: {info['memory']['available_formatted']}")
        print(f"        Usage: {info['memory']['percent']}%")
        
        print(f"\nDisk: {info['disk']['total_formatted']}")
        print(f"      Free: {info['disk']['free_formatted']}")
        print(f"      Usage: {info['disk']['percent']}%")
        
        # Check minimum requirements
        min_ram_gb = 8
        min_disk_gb = 10
        
        ram_gb = info['memory']['total'] / (1024**3)
        disk_gb = info['disk']['free'] / (1024**3)
        
        ram_ok = ram_gb >= min_ram_gb
        disk_ok = disk_gb >= min_disk_gb
        
        print_test(
            "RAM Check",
            ram_ok,
            f"{ram_gb:.1f}GB available (minimum: {min_ram_gb}GB)"
        )
        
        print_test(
            "Disk Space Check",
            disk_ok,
            f"{disk_gb:.1f}GB free (minimum: {min_disk_gb}GB)"
        )
        
        return ram_ok and disk_ok
        
    except Exception as e:
        print_test("System Resources", False, str(e))
        return False


def test_config():
    """Test configuration"""
    print_header("Configuration")
    
    try:
        from config import validate_config, APP_NAME, APP_VERSION
        
        print(f"Application: {APP_NAME}")
        print(f"Version: {APP_VERSION}")
        
        issues = validate_config()
        
        if issues:
            print_test("Configuration Validation", False)
            for issue in issues:
                print(f"   - {issue}")
            return False
        else:
            print_test("Configuration Validation", True)
            return True
            
    except Exception as e:
        print_test("Configuration", False, str(e))
        return False


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("  AI Video Enhancer - System Test")
    print("="*60)
    
    tests = [
        ("Python Version", test_python_version),
        ("Package Imports", test_imports),
        ("FFmpeg", test_ffmpeg),
        ("CUDA Support", test_cuda),
        ("Directories", test_directories),
        ("Custom Modules", test_modules),
        ("Model Handler", test_model_handler),
        ("Video Processor", test_video_processor),
        ("Batch Processor", test_batch_processor),
        ("System Resources", test_system_resources),
        ("Configuration", test_config)
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {str(e)}")
            results.append((name, False))
    
    # Summary
    print_header("Test Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        symbol = "✅" if result else "❌"
        print(f"{symbol} {name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready.")
        print("\nNext steps:")
        print("1. Run: streamlit run app.py")
        print("2. Download AI models from the sidebar")
        print("3. Start enhancing videos!")
        return True
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
