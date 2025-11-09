# 🚀 Quick Start Guide

Get started with AI Video Enhancer in 5 minutes!

## Prerequisites Checklist

Before you begin, ensure you have:

- [ ] Python 3.8 or higher installed
- [ ] FFmpeg installed and in system PATH
- [ ] At least 8GB RAM (16GB recommended)
- [ ] 10GB free disk space
- [ ] (Optional) NVIDIA GPU with CUDA for faster processing

## Installation Steps

### 1. Set Up Virtual Environment

```bash
# Navigate to project directory
cd "Video Enhance"

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### 2. Run Setup Script

```bash
python setup.py
```

This will:
- ✅ Check Python version
- ✅ Verify FFmpeg installation
- ✅ Check CUDA availability
- ✅ Create necessary directories
- ✅ Install dependencies
- ✅ Verify installation

### 3. Start the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## First Time Usage

### Step 1: Download AI Models

1. Look at the sidebar on the left
2. Find the "📊 Model Information" section
3. Click "Download general" for the general-purpose model
4. (Optional) Click "Download anime" for anime/cartoon content
5. Wait for downloads to complete (~64MB for general, ~17MB for anime)

### Step 2: Upload Your First Video

1. Go to the "🎬 Enhance Videos" tab
2. Click "Browse files" under "📁 Upload Videos"
3. Select one or more video files
4. Supported formats: MP4, AVI, MOV, MKV, FLV, WMV, WEBM

### Step 3: Configure Settings

**Target Resolution:**
- Start with 1080p for your first test
- Higher resolutions take longer to process

**AI Model:**
- Choose "General Purpose" for regular videos
- Choose "Anime/Cartoon Optimized" for animated content

**Output Directory:**
- Default is `output/` folder
- Change if you want files saved elsewhere

### Step 4: Start Enhancement

1. Review the processing summary
2. Click the "🎬 Start Enhancement" button
3. Switch to "📊 Processing Queue" tab to monitor progress

### Step 5: Monitor Progress

Watch real-time updates:
- Progress bar and percentage
- Current frame / Total frames
- Elapsed time
- Estimated time remaining

### Step 6: Access Your Enhanced Video

- Find your enhanced video in the output directory
- Filename format: `{original}_enhanced_{resolution}.{ext}`
- Original video remains unchanged

## Quick Tips

### 🚀 For Faster Processing
- Use a system with NVIDIA GPU
- Process smaller videos first
- Choose lower resolutions (1080p vs 8K)
- Close other applications

### 💡 Best Practices
- Test with a short video first (30 seconds)
- Use General model for live-action content
- Use Anime model for animated content
- Keep original videos as backup

### ⚠️ Common Issues

**"FFmpeg not found"**
```bash
# Windows: Download from ffmpeg.org and add to PATH
# Linux: sudo apt install ffmpeg
# macOS: brew install ffmpeg
```

**"CUDA out of memory"**
- Process smaller videos
- Use lower resolution
- Close other GPU applications

**Slow processing**
- Normal without GPU (10-30x slower)
- Consider using GPU-enabled system

## Example Workflow

### Quick Test (2 minutes)
1. Upload a 30-second video clip
2. Select 1080p resolution
3. Choose appropriate model
4. Start enhancement
5. Check output quality

### Batch Processing (10+ minutes)
1. Upload multiple videos
2. Select target resolution
3. Choose model type
4. Start enhancement
5. Monitor queue progress
6. All videos processed sequentially

## Performance Expectations

### With GPU (NVIDIA RTX 3060)
- 720p → 1080p: ~15-30 sec/min of video
- 1080p → 4K: ~30-60 sec/min of video

### Without GPU (CPU only)
- 720p → 1080p: ~2-5 min/min of video
- 1080p → 4K: ~5-10 min/min of video

*Actual times vary based on video complexity and system specs*

## Next Steps

Once you're comfortable with basic usage:

1. **Experiment with Models**: Try both models on same video
2. **Test Resolutions**: Compare different output resolutions
3. **Batch Processing**: Queue multiple videos
4. **Optimize Settings**: Adjust for your use case

## Getting Help

- **Documentation**: See `README.md` for detailed information
- **Configuration**: Check `config.py` for advanced settings
- **Troubleshooting**: Review error messages in the app

## Keyboard Shortcuts

When using Streamlit:
- `R` - Rerun the app
- `C` - Clear cache
- `?` - Show keyboard shortcuts

## Directory Structure

After setup, you'll have:
```
Video Enhance/
├── models/          # Downloaded AI models
├── uploads/         # Temporary uploaded files
├── output/          # Your enhanced videos ✨
└── temp/            # Temporary processing files
```

## Important Notes

- ✅ All processing is done locally (privacy-friendly)
- ✅ Original videos are never modified
- ✅ Audio quality is preserved
- ✅ No internet required after model download
- ⚠️ First run requires model download
- ⚠️ Processing time depends on hardware

## Ready to Go!

You're all set! Start enhancing your videos with AI-powered upscaling.

**Happy Enhancing! 🎬✨**

---

For detailed documentation, see [README.md](README.md)
