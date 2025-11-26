"""Email client for sending reports."""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

logger = logging.getLogger(__name__)


class EmailReporter:
    """Handles sending email reports."""
    
    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        from_address: str,
        password: str,
        use_tls: bool = True
    ):
        """
        Initialize email reporter.
        
        Args:
            smtp_server: SMTP server address
            smtp_port: SMTP port
            from_address: Sender email address
            password: Email password or app password
            use_tls: Whether to use TLS
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.from_address = from_address
        self.password = password
        self.use_tls = use_tls
        
        logger.info(f"EmailReporter initialized with {smtp_server}:{smtp_port}")
    
    def send_report(
        self,
        to_address: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        Send an email report.
        
        Args:
            to_address: Recipient email address
            subject: Email subject
            html_content: HTML email body
            text_content: Plain text alternative (optional)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_address
            msg['To'] = to_address
            
            # Add text part if provided
            if text_content:
                part1 = MIMEText(text_content, 'plain')
                msg.attach(part1)
            
            # Add HTML part
            part2 = MIMEText(html_content, 'html')
            msg.attach(part2)
            
            # Send email
            logger.info(f"Sending email to {to_address}")
            
            if self.use_tls:
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.from_address, self.password)
                    server.send_message(msg)
            else:
                with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                    server.login(self.from_address, self.password)
                    server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_address}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def send_instant_report(
        self,
        to_address: str,
        prompt: str,
        html_report: str,
        text_report: Optional[str] = None
    ) -> bool:
        """
        Send an instant news report.
        
        Args:
            to_address: Recipient email
            prompt: Search prompt
            html_report: HTML report content
            text_report: Text report content
            
        Returns:
            Success status
        """
        subject = f"📰 News Report: {prompt}"
        return self.send_report(to_address, subject, html_report, text_report)
    
    def send_scheduled_report(
        self,
        to_address: str,
        prompt: str,
        html_report: str,
        text_report: Optional[str] = None
    ) -> bool:
        """
        Send a scheduled monitoring report.
        
        Args:
            to_address: Recipient email
            prompt: Search prompt
            html_report: HTML report content
            text_report: Text report content
            
        Returns:
            Success status
        """
        subject = f"🔔 Scheduled News Update: {prompt}"
        return self.send_report(to_address, subject, html_report, text_report)
    
    def send_aggregate_report(
        self,
        to_address: str,
        prompt: str,
        html_report: str,
        text_report: Optional[str] = None
    ) -> bool:
        """
        Send an aggregate report.
        
        Args:
            to_address: Recipient email
            prompt: Search prompt
            html_report: HTML report content
            text_report: Text report content
            
        Returns:
            Success status
        """
        subject = f"📊 Aggregate News Report: {prompt}"
        return self.send_report(to_address, subject, html_report, text_report)
