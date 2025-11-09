"""
Video Enhancement Application - Streamlit Web Interface
AI-powered video upscaling with intuitive user interface
"""

import streamlit as st
import os
from pathlib import Path
import time
from datetime import datetime
import psutil
import torch

from model_handler import ModelHandler
from video_processor import VideoProcessor
from batch_processor import BatchProcessor, JobStatus

# Page configuration
st.set_page_config(
    page_title="AI Video Enhancer",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    .stat-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)


# Initialize session state
def init_session_state():
    """Initialize session state variables"""
    if 'model_handler' not in st.session_state:
        st.session_state.model_handler = ModelHandler()
    
    if 'video_processor' not in st.session_state:
        st.session_state.video_processor = VideoProcessor(st.session_state.model_handler)
    
    if 'batch_processor' not in st.session_state:
        st.session_state.batch_processor = BatchProcessor(st.session_state.video_processor)
    
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []
    
    if 'output_dir' not in st.session_state:
        st.session_state.output_dir = "output"


def format_time(seconds: float) -> str:
    """Format seconds to human-readable time"""
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


def format_bytes(bytes_size: float) -> str:
    """Format bytes to human-readable size"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} TB"


def get_system_info() -> dict:
    """Get system information"""
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "gpu_available": torch.cuda.is_available(),
        "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "N/A"
    }


def render_header():
    """Render application header"""
    st.markdown('<h1 class="main-header">🎬 AI Video Enhancer</h1>', unsafe_allow_html=True)
    st.markdown("""
        <p style='text-align: center; font-size: 1.2rem; color: #666;'>
        Transform your videos with AI-powered upscaling technology
        </p>
    """, unsafe_allow_html=True)
    st.markdown("---")


def render_sidebar():
    """Render sidebar with system info and settings"""
    with st.sidebar:
        st.header("⚙️ System Information")
        
        sys_info = get_system_info()
        
        st.metric("CPU Usage", f"{sys_info['cpu_percent']}%")
        st.metric("Memory Usage", f"{sys_info['memory_percent']}%")
        
        if sys_info['gpu_available']:
            st.success(f"✅ GPU: {sys_info['gpu_name']}")
        else:
            st.warning("⚠️ No GPU detected - Processing will be slower")
        
        st.markdown("---")
        
        st.header("📊 Model Information")
        
        models = st.session_state.model_handler.list_available_models()
        
        for model_type, info in models.items():
            with st.expander(f"🤖 {model_type.capitalize()} Model"):
                st.write(f"**Name:** {info['name']}")
                st.write(f"**Description:** {info['description']}")
                st.write(f"**Scale:** {info['scale']}x")
                
                if info['downloaded']:
                    st.success(f"✅ Downloaded ({info['size_mb']:.1f} MB)")
                else:
                    st.warning("⚠️ Not downloaded")
                    if st.button(f"Download {model_type}", key=f"download_{model_type}"):
                        with st.spinner(f"Downloading {model_type} model..."):
                            success = st.session_state.model_handler.download_model(model_type)
                            if success:
                                st.success("Download complete!")
                                st.rerun()
                            else:
                                st.error("Download failed!")
        
        st.markdown("---")
        
        st.header("🗑️ Cleanup")
        if st.button("Clear Completed Jobs"):
            st.session_state.batch_processor.clear_completed_jobs()
            st.success("Cleared!")
            st.rerun()


def render_upload_section():
    """Render video upload section"""
    st.header("📁 Upload Videos")
    
    uploaded_files = st.file_uploader(
        "Choose video files",
        type=['mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv', 'webm'],
        accept_multiple_files=True,
        help="Upload one or more video files for enhancement"
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} file(s) uploaded")
        
        # Save uploaded files
        upload_dir = Path("uploads")
        upload_dir.mkdir(exist_ok=True)
        
        saved_files = []
        for uploaded_file in uploaded_files:
            file_path = upload_dir / uploaded_file.name
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            saved_files.append(str(file_path))
        
        st.session_state.uploaded_files = saved_files
        
        # Display file information
        with st.expander("📋 File Details"):
            for i, file_path in enumerate(saved_files, 1):
                try:
                    video_info = st.session_state.video_processor.get_video_info(file_path)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**{i}. {Path(file_path).name}**")
                    with col2:
                        st.write(f"Resolution: {video_info['width']}x{video_info['height']}")
                    with col3:
                        st.write(f"Duration: {format_time(video_info['duration'])}")
                except Exception as e:
                    st.error(f"Error reading {Path(file_path).name}: {str(e)}")


def render_settings_section():
    """Render enhancement settings section"""
    st.header("⚙️ Enhancement Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        target_resolution = st.selectbox(
            "Target Resolution",
            options=["1080p", "2K", "4K", "8K"],
            help="Select the target resolution for enhanced videos"
        )
        
        st.info(f"""
        **Resolution Details:**
        - **1080p (Full HD):** 1920x1080
        - **2K (QHD):** 2560x1440
        - **4K (UHD):** 3840x2160
        - **8K:** 7680x4320
        """)
    
    with col2:
        model_type = st.selectbox(
            "AI Model",
            options=["general", "anime"],
            format_func=lambda x: "General Purpose" if x == "general" else "Anime/Cartoon Optimized",
            help="Select the AI model optimized for your content type"
        )
        
        st.info(f"""
        **Model Information:**
        - **General Purpose:** Best for standard video content (movies, vlogs, etc.)
        - **Anime/Cartoon:** Optimized for animated content with sharp lines and colors
        """)
    
    output_dir = st.text_input(
        "Output Directory",
        value=st.session_state.output_dir,
        help="Directory where enhanced videos will be saved"
    )
    st.session_state.output_dir = output_dir
    
    return target_resolution, model_type, output_dir


def render_process_section(target_resolution, model_type, output_dir):
    """Render processing control section"""
    st.header("🚀 Start Enhancement")
    
    if not st.session_state.uploaded_files:
        st.warning("⚠️ Please upload video files first")
        return
    
    # Check if models are downloaded
    model_info = st.session_state.model_handler.get_model_info(model_type)
    if not model_info['downloaded']:
        st.error(f"⚠️ {model_type.capitalize()} model not downloaded. Please download it from the sidebar.")
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Files to Process", len(st.session_state.uploaded_files))
    
    with col2:
        total_duration = 0
        for file_path in st.session_state.uploaded_files:
            try:
                info = st.session_state.video_processor.get_video_info(file_path)
                total_duration += info['duration']
            except:
                pass
        st.metric("Total Duration", format_time(total_duration))
    
    with col3:
        estimated_time = 0
        for file_path in st.session_state.uploaded_files:
            try:
                est = st.session_state.video_processor.estimate_processing_time(
                    file_path,
                    target_resolution
                )
                estimated_time += est
            except:
                pass
        st.metric("Estimated Time", format_time(estimated_time))
    
    if st.button("🎬 Start Enhancement", type="primary", use_container_width=True):
        # Add jobs to batch processor
        job_ids = st.session_state.batch_processor.add_batch_jobs(
            st.session_state.uploaded_files,
            output_dir,
            target_resolution,
            model_type
        )
        
        st.success(f"✅ Added {len(job_ids)} job(s) to queue!")
        time.sleep(1)
        st.rerun()


def render_progress_section():
    """Render progress tracking section"""
    st.header("📊 Processing Status")
    
    queue_status = st.session_state.batch_processor.get_queue_status()
    
    # Overall statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Jobs", queue_status['total'])
    with col2:
        st.metric("Pending", queue_status['pending'], delta=None)
    with col3:
        st.metric("Processing", queue_status['processing'], delta=None)
    with col4:
        st.metric("Completed", queue_status['completed'], delta=None)
    
    if queue_status['failed'] > 0:
        st.error(f"⚠️ {queue_status['failed']} job(s) failed")
    
    # Job list
    jobs = st.session_state.batch_processor.get_all_jobs()
    
    if not jobs:
        st.info("No jobs in queue. Upload videos and start enhancement to begin.")
        return
    
    st.markdown("---")
    
    # Display each job
    for job in sorted(jobs, key=lambda x: x.start_time or datetime.now(), reverse=True):
        job_dict = job.to_dict()
        
        with st.container():
            # Job header
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                status_emoji = {
                    "pending": "⏳",
                    "processing": "🔄",
                    "completed": "✅",
                    "failed": "❌",
                    "cancelled": "🚫"
                }
                st.write(f"{status_emoji.get(job_dict['status'], '❓')} **{Path(job_dict['input_path']).name}**")
            
            with col2:
                st.write(f"**{job_dict['target_resolution']}** | {job_dict['model_type']}")
            
            with col3:
                st.write(f"**{job_dict['status'].upper()}**")
            
            # Progress bar for active jobs
            if job_dict['status'] == 'processing':
                progress = job_dict['progress'] / 100
                st.progress(progress)
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.write(f"Progress: {job_dict['progress']:.1f}%")
                with col2:
                    st.write(f"Frame: {job_dict['current_frame']}/{job_dict['total_frames']}")
                with col3:
                    st.write(f"Elapsed: {format_time(job_dict['elapsed_time'])}")
                with col4:
                    st.write(f"ETA: {format_time(job_dict['eta'])}")
            
            # Completed job info
            elif job_dict['status'] == 'completed':
                col1, col2 = st.columns(2)
                with col1:
                    st.success(f"✅ Completed in {format_time(job_dict['elapsed_time'])}")
                with col2:
                    if Path(job_dict['output_path']).exists():
                        file_size = Path(job_dict['output_path']).stat().st_size
                        st.write(f"Output: {format_bytes(file_size)}")
            
            # Failed job info
            elif job_dict['status'] == 'failed':
                st.error(f"❌ Failed: {job_dict.get('error_message', 'Unknown error')}")
            
            # Pending job info
            elif job_dict['status'] == 'pending':
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"Estimated time: {format_time(job_dict['eta'])}")
                with col2:
                    if st.button("Cancel", key=f"cancel_{job_dict['job_id']}"):
                        st.session_state.batch_processor.cancel_job(job_dict['job_id'])
                        st.rerun()
            
            st.markdown("---")
    
    # Auto-refresh for active jobs
    if queue_status['processing'] > 0 or queue_status['pending'] > 0:
        time.sleep(2)
        st.rerun()


def main():
    """Main application function"""
    init_session_state()
    
    render_header()
    render_sidebar()
    
    # Main content tabs
    tab1, tab2 = st.tabs(["🎬 Enhance Videos", "📊 Processing Queue"])
    
    with tab1:
        render_upload_section()
        st.markdown("---")
        target_resolution, model_type, output_dir = render_settings_section()
        st.markdown("---")
        render_process_section(target_resolution, model_type, output_dir)
    
    with tab2:
        render_progress_section()
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #666; padding: 2rem;'>
            <p>🎬 AI Video Enhancer | Powered by Real-ESRGAN</p>
            <p>Transform your videos with state-of-the-art AI upscaling technology</p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
