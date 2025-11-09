"""
Batch Processing System for Video Enhancement
Handles multiple video processing tasks with queue management
"""

import threading
import queue
from pathlib import Path
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import time
from enum import Enum


class JobStatus(Enum):
    """Status of a processing job"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ProcessingJob:
    """Represents a single video processing job"""
    job_id: str
    input_path: str
    output_path: str
    target_resolution: str
    model_type: str
    status: JobStatus = JobStatus.PENDING
    progress: float = 0.0
    current_frame: int = 0
    total_frames: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None
    estimated_time: float = 0.0
    metadata: Dict = field(default_factory=dict)
    
    def get_elapsed_time(self) -> float:
        """Get elapsed processing time in seconds"""
        if self.start_time is None:
            return 0.0
        
        end = self.end_time if self.end_time else datetime.now()
        return (end - self.start_time).total_seconds()
    
    def get_eta(self) -> float:
        """Get estimated time remaining in seconds"""
        if self.progress <= 0 or self.start_time is None:
            return self.estimated_time
        
        elapsed = self.get_elapsed_time()
        estimated_total = elapsed / (self.progress / 100)
        return max(0, estimated_total - elapsed)
    
    def to_dict(self) -> Dict:
        """Convert job to dictionary"""
        return {
            "job_id": self.job_id,
            "input_path": self.input_path,
            "output_path": self.output_path,
            "target_resolution": self.target_resolution,
            "model_type": self.model_type,
            "status": self.status.value,
            "progress": self.progress,
            "current_frame": self.current_frame,
            "total_frames": self.total_frames,
            "elapsed_time": self.get_elapsed_time(),
            "eta": self.get_eta(),
            "error_message": self.error_message,
            "metadata": self.metadata
        }


class BatchProcessor:
    """Manages batch processing of multiple videos"""
    
    def __init__(self, video_processor, max_workers: int = 1):
        """
        Initialize batch processor
        
        Args:
            video_processor: VideoProcessor instance
            max_workers: Maximum number of concurrent processing jobs
        """
        self.video_processor = video_processor
        self.max_workers = max_workers
        
        self.job_queue: queue.Queue = queue.Queue()
        self.jobs: Dict[str, ProcessingJob] = {}
        self.active_jobs: List[str] = []
        
        self.is_running = False
        self.worker_thread: Optional[threading.Thread] = None
        
        self._lock = threading.Lock()
        self._job_counter = 0
    
    def add_job(
        self,
        input_path: str,
        output_path: str,
        target_resolution: str,
        model_type: str = "general"
    ) -> str:
        """
        Add a new job to the queue
        
        Args:
            input_path: Input video path
            output_path: Output video path
            target_resolution: Target resolution preset
            model_type: AI model type
            
        Returns:
            Job ID
        """
        with self._lock:
            self._job_counter += 1
            job_id = f"job_{self._job_counter}_{int(time.time())}"
        
        # Estimate processing time
        estimated_time = self.video_processor.estimate_processing_time(
            input_path,
            target_resolution
        )
        
        job = ProcessingJob(
            job_id=job_id,
            input_path=input_path,
            output_path=output_path,
            target_resolution=target_resolution,
            model_type=model_type,
            estimated_time=estimated_time
        )
        
        with self._lock:
            self.jobs[job_id] = job
        
        self.job_queue.put(job_id)
        
        # Start worker if not running
        if not self.is_running:
            self.start()
        
        return job_id
    
    def add_batch_jobs(
        self,
        video_files: List[str],
        output_dir: str,
        target_resolution: str,
        model_type: str = "general"
    ) -> List[str]:
        """
        Add multiple jobs at once
        
        Args:
            video_files: List of input video paths
            output_dir: Output directory
            target_resolution: Target resolution preset
            model_type: AI model type
            
        Returns:
            List of job IDs
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        job_ids = []
        
        for video_file in video_files:
            input_path = Path(video_file)
            output_file = output_path / f"{input_path.stem}_enhanced_{target_resolution}{input_path.suffix}"
            
            job_id = self.add_job(
                str(input_path),
                str(output_file),
                target_resolution,
                model_type
            )
            job_ids.append(job_id)
        
        return job_ids
    
    def get_job(self, job_id: str) -> Optional[ProcessingJob]:
        """Get job by ID"""
        with self._lock:
            return self.jobs.get(job_id)
    
    def get_all_jobs(self) -> List[ProcessingJob]:
        """Get all jobs"""
        with self._lock:
            return list(self.jobs.values())
    
    def get_queue_status(self) -> Dict:
        """Get overall queue status"""
        with self._lock:
            total = len(self.jobs)
            pending = sum(1 for j in self.jobs.values() if j.status == JobStatus.PENDING)
            processing = sum(1 for j in self.jobs.values() if j.status == JobStatus.PROCESSING)
            completed = sum(1 for j in self.jobs.values() if j.status == JobStatus.COMPLETED)
            failed = sum(1 for j in self.jobs.values() if j.status == JobStatus.FAILED)
            
            return {
                "total": total,
                "pending": pending,
                "processing": processing,
                "completed": completed,
                "failed": failed,
                "is_running": self.is_running
            }
    
    def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a pending job
        
        Args:
            job_id: Job ID to cancel
            
        Returns:
            True if cancelled successfully
        """
        with self._lock:
            job = self.jobs.get(job_id)
            if job and job.status == JobStatus.PENDING:
                job.status = JobStatus.CANCELLED
                return True
        return False
    
    def clear_completed_jobs(self):
        """Remove completed and failed jobs from the list"""
        with self._lock:
            self.jobs = {
                jid: job for jid, job in self.jobs.items()
                if job.status not in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]
            }
    
    def _process_job(self, job_id: str):
        """Process a single job"""
        job = self.get_job(job_id)
        if not job or job.status == JobStatus.CANCELLED:
            return
        
        # Update job status
        with self._lock:
            job.status = JobStatus.PROCESSING
            job.start_time = datetime.now()
            self.active_jobs.append(job_id)
        
        def progress_callback(current_frame: int, total_frames: int, info: Dict):
            """Update job progress"""
            with self._lock:
                job.current_frame = current_frame
                job.total_frames = total_frames
                job.progress = (current_frame / total_frames * 100) if total_frames > 0 else 0
                job.metadata.update(info)
        
        try:
            # Process video
            success = self.video_processor.process_video(
                job.input_path,
                job.output_path,
                job.target_resolution,
                job.model_type,
                progress_callback
            )
            
            # Update job status
            with self._lock:
                if success:
                    job.status = JobStatus.COMPLETED
                    job.progress = 100.0
                else:
                    job.status = JobStatus.FAILED
                    job.error_message = "Processing failed"
                
                job.end_time = datetime.now()
                
        except Exception as e:
            with self._lock:
                job.status = JobStatus.FAILED
                job.error_message = str(e)
                job.end_time = datetime.now()
        
        finally:
            with self._lock:
                if job_id in self.active_jobs:
                    self.active_jobs.remove(job_id)
    
    def _worker(self):
        """Worker thread that processes jobs from the queue"""
        while self.is_running:
            try:
                # Get next job from queue (with timeout)
                job_id = self.job_queue.get(timeout=1)
                
                # Process the job
                self._process_job(job_id)
                
                self.job_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Worker error: {str(e)}")
    
    def start(self):
        """Start the batch processor"""
        if not self.is_running:
            self.is_running = True
            self.worker_thread = threading.Thread(target=self._worker, daemon=True)
            self.worker_thread.start()
    
    def stop(self, wait: bool = True):
        """
        Stop the batch processor
        
        Args:
            wait: Wait for current jobs to complete
        """
        self.is_running = False
        
        if wait and self.worker_thread:
            self.worker_thread.join(timeout=5)
    
    def wait_for_completion(self):
        """Wait for all jobs to complete"""
        self.job_queue.join()
