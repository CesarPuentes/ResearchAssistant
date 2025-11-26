"""Scheduled monitoring with APScheduler."""

import logging
from typing import Callable, Optional
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import pytz

logger = logging.getLogger(__name__)


class NewsScheduler:
    """Manages scheduled news monitoring tasks."""
    
    def __init__(self, timezone: str = "America/New_York"):
        """
        Initialize the scheduler.
        
        Args:
            timezone: Timezone for scheduling
        """
        self.timezone = pytz.timezone(timezone)
        self.scheduler = BackgroundScheduler(timezone=self.timezone)
        self.jobs = {}
        
        logger.info(f"NewsScheduler initialized with timezone: {timezone}")
    
    def start(self):
        """Start the scheduler."""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Scheduler started")
    
    def stop(self):
        """Stop the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler stopped")
    
    def schedule_monitoring(
        self,
        session_id: int,
        interval_hours: int,
        callback: Callable,
        **callback_kwargs
    ) -> str:
        """
        Schedule a monitoring task.
        
        Args:
            session_id: Monitoring session ID
            interval_hours: Run every N hours
            callback: Function to call on each run
            **callback_kwargs: Arguments to pass to callback
            
        Returns:
            Job ID
        """
        job_id = f"monitoring_{session_id}"
        
        # Remove existing job if any
        if job_id in self.jobs:
            self.remove_job(job_id)
        
        # Add new job
        job = self.scheduler.add_job(
            callback,
            trigger=IntervalTrigger(hours=interval_hours),
            id=job_id,
            kwargs=callback_kwargs,
            next_run_time=datetime.now(self.timezone)  # Run immediately
        )
        
        self.jobs[job_id] = job
        logger.info(f"Scheduled monitoring job {job_id} to run every {interval_hours} hours")
        
        return job_id
    
    def remove_job(self, job_id: str):
        """
        Remove a scheduled job.
        
        Args:
            job_id: Job ID to remove
        """
        if job_id in self.jobs:
            self.scheduler.remove_job(job_id)
            del self.jobs[job_id]
            logger.info(f"Removed job {job_id}")
    
    def get_job_status(self, job_id: str) -> Optional[dict]:
        """
        Get status of a scheduled job.
        
        Args:
            job_id: Job ID
            
        Returns:
            Job status dict or None
        """
        if job_id in self.jobs:
            job = self.jobs[job_id]
            return {
                'id': job.id,
                'next_run_time': job.next_run_time,
                'trigger': str(job.trigger)
            }
        return None
    
    def list_jobs(self) -> list:
        """List all scheduled jobs."""
        return [
            {
                'id': job.id,
                'next_run_time': job.next_run_time,
                'trigger': str(job.trigger)
            }
            for job in self.scheduler.get_jobs()
        ]
