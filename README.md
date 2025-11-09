# 🎬 AI Video Enhancer

A comprehensive video enhancement application that leverages AI-powered upscaling technology to transform videos into higher resolutions. Built with Streamlit for an intuitive user experience.

## ✨ Features

### 🚀 AI-Powered Upscaling
- **Multiple Resolution Support**: Upscale to 1080p (Full HD), 2K (1440p), 4K (2160p), and 8K (4320p)
- **Specialized AI Models**:
  - **General Purpose Model**: Optimized for standard video content (movies, vlogs, documentaries)
  - **Anime/Cartoon Model**: Specialized for animated content with enhanced detail preservation

### 🎵 Audio Preservation
- Original audio quality maintained throughout the enhancement process
- Audio stream remains untouched with original bitrate
- Automatic audio extraction and re-muxing

### 🖥️ User-Friendly Interface
- Intuitive Streamlit web interface
- Clear controls for video selection and settings
- Real-time system monitoring (CPU, Memory, GPU)
- Model management with download capabilities

### 📦 Batch Processing
- Queue multiple videos for enhancement
- Process videos sequentially
- Efficient workflow for multiple files

### 📊 Real-Time Progress Tracking
- Detailed progress information for each video
- Current frame and total frames display
- Percentage completion
- Estimated time remaining (ETA)
- Elapsed processing time
- Processing statistics and metadata

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **Video Processing**: OpenCV, FFmpeg
- **AI Models**: Real-ESRGAN (PyTorch)
- **Deep Learning**: PyTorch, BasicSR
- **System Monitoring**: psutil

## 📋 Prerequisites

### System Requirements
- **Python**: 3.8 or higher
- **FFmpeg**: Must be installed and available in system PATH
- **RAM**: Minimum 8GB (16GB recommended for 4K/8K)
- **GPU**: NVIDIA GPU with CUDA support (optional but highly recommended)
  - Without GPU: Processing will be significantly slower
  - With GPU: 10-30x faster processing

### Installing FFmpeg

#### Windows
1. Download FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to system PATH
4. Verify: `ffmpeg -version`

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install ffmpeg
```

#### macOS
```bash
brew install ffmpeg
```

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd "Video Enhance"
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Install PyTorch with CUDA (Optional but Recommended)
For GPU acceleration, install PyTorch with CUDA support:

```bash
# CUDA 11.8
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# CUDA 12.1
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# CPU only (slower)
pip install torch torchvision
```

Visit [PyTorch Get Started](https://pytorch.org/get-started/locally/) for specific installation commands.

## 🎯 Usage

### Starting the Application

1. **Activate Virtual Environment**
```bash
# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

2. **Run the Application**
```bash
streamlit run app.py
```

3. **Access the Interface**
- The application will open in your default browser
- Default URL: `http://localhost:8501`

### Using the Application

#### Step 1: Upload Videos
1. Navigate to the "🎬 Enhance Videos" tab
2. Click "Browse files" to upload video files
3. Supported formats: MP4, AVI, MOV, MKV, FLV, WMV, WEBM
4. Multiple files can be uploaded at once

#### Step 2: Configure Settings
1. **Target Resolution**: Select desired output resolution
   - 1080p (1920x1080) - Full HD
   - 2K (2560x1440) - Quad HD
   - 4K (3840x2160) - Ultra HD
   - 8K (7680x4320) - 8K UHD

2. **AI Model**: Choose appropriate model for content
   - General Purpose: Standard video content
   - Anime/Cartoon: Animated content

3. **Output Directory**: Specify where enhanced videos will be saved

#### Step 3: Download AI Models (First Time Only)
1. Check the sidebar for model status
2. If models are not downloaded, click "Download" buttons
3. Wait for models to download (may take several minutes)
4. Models are downloaded once and reused

#### Step 4: Start Enhancement
1. Review the processing summary
2. Click "🎬 Start Enhancement" button
3. Jobs are added to the processing queue

#### Step 5: Monitor Progress
1. Switch to "📊 Processing Queue" tab
2. View real-time progress for each video:
   - Current status (Pending, Processing, Completed, Failed)
   - Progress percentage
   - Current frame / Total frames
   - Elapsed time
   - Estimated time remaining
3. Page auto-refreshes during processing

#### Step 6: Access Enhanced Videos
- Enhanced videos are saved to the specified output directory
- File naming: `{original_name}_enhanced_{resolution}.{extension}`
- Original files remain unchanged

## 📁 Project Structure

```
Video Enhance/
├── app.py                  # Streamlit web interface
├── video_processor.py      # Core video processing engine
├── model_handler.py        # AI model management
├── batch_processor.py      # Batch processing system
├── requirements.txt        # Python dependencies
├── README.md              # Documentation
├── .gitignore             # Git ignore rules
├── models/                # AI model weights (auto-created)
├── uploads/               # Temporary upload storage (auto-created)
└── output/                # Enhanced videos (auto-created)
```

## 🔧 Configuration

### Model Configuration
Models are automatically downloaded on first use. Manual configuration is available in `model_handler.py`:

```python
MODEL_CONFIGS = {
    "general": {
        "name": "RealESRGAN_x4plus",
        "scale": 4,
        "url": "...",
        "description": "General purpose model"
    },
    "anime": {
        "name": "RealESRGAN_x4plus_anime_6B",
        "scale": 4,
        "url": "...",
        "description": "Anime/cartoon optimized model"
    }
}
```

### Processing Configuration
Adjust processing parameters in `video_processor.py`:

```python
# Video encoding quality
crf=18  # Lower = better quality (18-28 recommended)
preset='slow'  # Encoding speed (ultrafast, fast, medium, slow, veryslow)
```

## 🎨 Features in Detail

### AI Model Types

#### General Purpose Model (RealESRGAN_x4plus)
- **Best for**: Live-action videos, movies, documentaries, vlogs
- **Characteristics**: 
  - Natural detail enhancement
  - Noise reduction
  - Edge preservation
  - Realistic texture generation

#### Anime/Cartoon Model (RealESRGAN_x4plus_anime_6B)
- **Best for**: Anime, cartoons, animated content
- **Characteristics**:
  - Sharp line preservation
  - Vibrant color enhancement
  - Reduced blur on animated features
  - Optimized for hand-drawn aesthetics

### Resolution Scaling

The application intelligently scales videos while maintaining aspect ratio:
- Calculates optimal dimensions based on source aspect ratio
- Ensures dimensions are even (required for video encoding)
- Prevents distortion or stretching

### Audio Handling

Audio preservation process:
1. Extract audio from source video without re-encoding
2. Process video frames with AI upscaling
3. Re-encode video with high quality settings
4. Merge original audio with enhanced video
5. Output final video with pristine audio quality

### Batch Processing

Queue management features:
- Add multiple videos to processing queue
- Sequential processing to manage system resources
- Job status tracking (Pending, Processing, Completed, Failed)
- Cancel pending jobs
- Clear completed jobs from queue

### Progress Tracking

Real-time information displayed:
- **Progress Bar**: Visual representation of completion
- **Percentage**: Exact completion percentage
- **Frame Counter**: Current frame / Total frames
- **Elapsed Time**: Time spent processing
- **ETA**: Estimated time remaining
- **Statistics**: Resolution, FPS, model type

## ⚡ Performance Tips

### For Best Performance
1. **Use GPU**: NVIDIA GPU with CUDA dramatically improves speed
2. **Close Other Applications**: Free up system resources
3. **Process Smaller Batches**: Avoid queuing too many large videos
4. **Choose Appropriate Resolution**: Higher resolutions take exponentially longer
5. **SSD Storage**: Use SSD for input/output to reduce I/O bottleneck

### Processing Time Estimates (Approximate)

**With GPU (NVIDIA RTX 3060):**
- 1080p → 4K: ~30-60 seconds per minute of video
- 720p → 1080p: ~15-30 seconds per minute of video

**Without GPU (CPU only):**
- 1080p → 4K: ~5-10 minutes per minute of video
- 720p → 1080p: ~2-5 minutes per minute of video

*Times vary based on video complexity, system specifications, and resolution.*

## 🐛 Troubleshooting

### Common Issues

#### "FFmpeg not found"
- **Solution**: Install FFmpeg and add to system PATH
- **Verify**: Run `ffmpeg -version` in terminal

#### "CUDA out of memory"
- **Solution**: Process smaller videos or reduce batch size
- **Alternative**: Use CPU processing (slower but works)

#### "Model download failed"
- **Solution**: Check internet connection
- **Alternative**: Manually download models from GitHub releases

#### Slow processing without GPU
- **Expected**: CPU processing is 10-30x slower than GPU
- **Solution**: Consider using a system with NVIDIA GPU

#### Audio sync issues
- **Solution**: Ensure FFmpeg is properly installed
- **Check**: Original video audio is not corrupted

### Getting Help

If you encounter issues:
1. Check the error message in the application
2. Review the console output for detailed logs
3. Verify all prerequisites are installed
4. Check system resources (RAM, disk space)

## 🔒 Privacy & Security

- All processing is done locally on your machine
- No videos are uploaded to external servers
- No data is collected or transmitted
- Models are downloaded once from official sources

## 📝 License

This project uses the following open-source technologies:
- Real-ESRGAN: BSD 3-Clause License
- Streamlit: Apache License 2.0
- PyTorch: BSD-style License
- OpenCV: Apache License 2.0

## 🙏 Acknowledgments

- **Real-ESRGAN**: Xintao Wang et al. for the amazing AI upscaling models
- **Streamlit**: For the excellent web framework
- **PyTorch**: For the deep learning framework
- **FFmpeg**: For video processing capabilities

## 🚀 Future Enhancements

Potential features for future versions:
- [ ] Video format conversion
- [ ] Custom model training
- [ ] Frame interpolation for FPS increase
- [ ] Denoising and stabilization
- [ ] Color grading presets
- [ ] Cloud processing option
- [ ] API for programmatic access
- [ ] Video comparison viewer

## 📧 Support

For questions, issues, or feature requests, please open an issue on the project repository.

---

**Made with ❤️ using AI-powered video enhancement technology**
