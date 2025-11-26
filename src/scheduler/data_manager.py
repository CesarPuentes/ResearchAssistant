"""Data manager for storing and retrieving monitoring data."""

import logging
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

Base = declarative_base()


class MonitoringSession(Base):
    """Database model for monitoring sessions."""
    __tablename__ = 'monitoring_sessions'
    
    id = Column(Integer, primary_key=True)
    prompt = Column(String(500), nullable=False)
    interval_hours = Column(Integer, nullable=False)
    started_at = Column(DateTime, nullable=False)
    last_run_at = Column(DateTime)
    is_active = Column(Integer, default=1)  # SQLite doesn't have boolean
    email_to = Column(String(200))
    

class NewsArticle(Base):
    """Database model for news articles."""
    __tablename__ = 'news_articles'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, nullable=False)
    title = Column(String(500))
    url = Column(Text)
    source = Column(String(200))
    snippet = Column(Text)
    found_at = Column(DateTime, nullable=False)
    

class MonitoringReport(Base):
    """Database model for monitoring reports."""
    __tablename__ = 'monitoring_reports'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, nullable=False)
    analysis = Column(Text)
    created_at = Column(DateTime, nullable=False)
    article_count = Column(Integer, default=0)


class DataManager:
    """Manages persistent storage for monitoring data."""
    
    def __init__(self, database_path: Path):
        """
        Initialize data manager.
        
        Args:
            database_path: Path to SQLite database file
        """
        self.database_path = database_path
        database_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create engine and tables
        self.engine = create_engine(f'sqlite:///{database_path}')
        Base.metadata.create_all(self.engine)
        
        # Create session maker
        self.Session = sessionmaker(bind=self.engine)
        
        logger.info(f"DataManager initialized with database: {database_path}")
    
    def create_session(
        self,
        prompt: str,
        interval_hours: int,
        email_to: str
    ) -> int:
        """
        Create a new monitoring session.
        
        Args:
            prompt: Search prompt
            interval_hours: Monitoring interval
            email_to: Recipient email
            
        Returns:
            Session ID
        """
        session = self.Session()
        try:
            monitoring_session = MonitoringSession(
                prompt=prompt,
                interval_hours=interval_hours,
                started_at=datetime.now(),
                email_to=email_to
            )
            session.add(monitoring_session)
            session.commit()
            session_id = monitoring_session.id
            logger.info(f"Created monitoring session {session_id}")
            return session_id
        finally:
            session.close()
    
    def update_session_run(self, session_id: int):
        """Update the last run time for a session."""
        session = self.Session()
        try:
            monitoring_session = session.query(MonitoringSession).filter_by(id=session_id).first()
            if monitoring_session:
                monitoring_session.last_run_at = datetime.now()
                session.commit()
        finally:
            session.close()
    
    def stop_session(self, session_id: int):
        """Mark a session as inactive."""
        session = self.Session()
        try:
            monitoring_session = session.query(MonitoringSession).filter_by(id=session_id).first()
            if monitoring_session:
                monitoring_session.is_active = 0
                session.commit()
                logger.info(f"Stopped monitoring session {session_id}")
        finally:
            session.close()
    
    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """Get all active monitoring sessions."""
        session = self.Session()
        try:
            sessions = session.query(MonitoringSession).filter_by(is_active=1).all()
            return [{
                'id': s.id,
                'prompt': s.prompt,
                'interval_hours': s.interval_hours,
                'started_at': s.started_at,
                'last_run_at': s.last_run_at,
                'email_to': s.email_to
            } for s in sessions]
        finally:
            session.close()
    
    def get_session(self, session_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific monitoring session."""
        session = self.Session()
        try:
            s = session.query(MonitoringSession).filter_by(id=session_id).first()
            if s:
                return {
                    'id': s.id,
                    'prompt': s.prompt,
                    'interval_hours': s.interval_hours,
                    'started_at': s.started_at,
                    'last_run_at': s.last_run_at,
                    'email_to': s.email_to,
                    'is_active': bool(s.is_active)
                }
            return None
        finally:
            session.close()
    
    def store_articles(
        self,
        session_id: int,
        articles: List[Dict[str, Any]]
    ):
        """
        Store found articles for a session.
        
        Args:
            session_id: Monitoring session ID
            articles: List of article dictionaries
        """
        session = self.Session()
        try:
            for article in articles:
                news_article = NewsArticle(
                    session_id=session_id,
                    title=article.get('title', ''),
                    url=article.get('url', ''),
                    source=article.get('source', ''),
                    snippet=article.get('snippet', ''),
                    found_at=datetime.now()
                )
                session.add(news_article)
            session.commit()
            logger.info(f"Stored {len(articles)} articles for session {session_id}")
        finally:
            session.close()
    
    def store_report(
        self,
        session_id: int,
        analysis: str,
        article_count: int
    ):
        """
        Store a monitoring report.
        
        Args:
            session_id: Monitoring session ID
            analysis: Analysis text
            article_count: Number of articles found
        """
        session = self.Session()
        try:
            report = MonitoringReport(
                session_id=session_id,
                analysis=analysis,
                created_at=datetime.now(),
                article_count=article_count
            )
            session.add(report)
            session.commit()
            logger.info(f"Stored report for session {session_id}")
        finally:
            session.close()
    
    def get_session_articles(
        self,
        session_id: int,
        since: Optional[datetime] = None
    ) -> List[List[Dict[str, Any]]]:
        """
        Get all articles for a session, grouped by time periods.
        
        Args:
            session_id: Monitoring session ID
            since: Only get articles after this time
            
        Returns:
            List of article lists (one per monitoring run)
        """
        session = self.Session()
        try:
            query = session.query(NewsArticle).filter_by(session_id=session_id)
            if since:
                query = query.filter(NewsArticle.found_at >= since)
            
            articles = query.order_by(NewsArticle.found_at).all()
            
            # Group by hour (approximate monitoring runs)
            grouped = []
            current_group = []
            last_time = None
            
            for article in articles:
                if last_time and (article.found_at - last_time).total_seconds() > 1800:  # 30 min gap
                    if current_group:
                        grouped.append(current_group)
                    current_group = []
                
                current_group.append({
                    'title': article.title,
                    'url': article.url,
                    'source': article.source,
                    'snippet': article.snippet,
                    'found_at': article.found_at
                })
                last_time = article.found_at
            
            if current_group:
                grouped.append(current_group)
            
            return grouped
        finally:
            session.close()
    
    def get_session_reports(self, session_id: int) -> List[str]:
        """Get all analysis reports for a session."""
        session = self.Session()
        try:
            reports = session.query(MonitoringReport).filter_by(
                session_id=session_id
            ).order_by(MonitoringReport.created_at).all()
            
            return [r.analysis for r in reports]
        finally:
            session.close()
    
    def cleanup_old_data(self, days: int = 30):
        """
        Clean up data older than specified days.
        
        Args:
            days: Keep data from last N days
        """
        session = self.Session()
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Delete old articles
            session.query(NewsArticle).filter(
                NewsArticle.found_at < cutoff_date
            ).delete()
            
            # Delete old reports
            session.query(MonitoringReport).filter(
                MonitoringReport.created_at < cutoff_date
            ).delete()
            
            session.commit()
            logger.info(f"Cleaned up data older than {days} days")
        finally:
            session.close()
