#!/usr/bin/env python3
"""
News Aggregation System with DeepSeek API

A comprehensive news monitoring and reporting system using LangChain agents
and DeepSeek API to search the web and deliver email reports.
"""

import sys
import logging
import signal
from pathlib import Path
from datetime import datetime
import click
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TextColumn

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.config.config_manager import ConfigManager
from src.api.api_client import DeepSeekClient
from src.agents.news_agent import NewsAgent
from src.reporters.report_generator import ReportGenerator
from src.reporters.email_reporter import EmailReporter
from src.scheduler.scheduler import NewsScheduler
from src.scheduler.data_manager import DataManager

console = Console()
logger = logging.getLogger(__name__)

# Global scheduler instance for cleanup
scheduler_instance = None


def setup_logging(log_level: str = "INFO"):
    """Setup logging configuration."""
    logging.basicConfig(
        level=log_level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, console=console)]
    )


def signal_handler(sig, frame):
    """Handle shutdown signals."""
    console.print("\n[yellow]Shutting down gracefully...[/yellow]")
    if scheduler_instance:
        scheduler_instance.stop()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def run_monitoring_cycle(
    session_id: int,
    prompt: str,
    email_to: str,
    config: ConfigManager,
    data_manager: DataManager
):
    """
    Run a single monitoring cycle.
    
    Args:
        session_id: Monitoring session ID
        prompt: Search prompt
        email_to: Email recipient
        config: Configuration manager
        data_manager: Data manager
    """
    try:
        logger.info(f"Running monitoring cycle for session {session_id}")
        
        # Initialize components
        deepseek = DeepSeekClient(
            api_key=config.deepseek_api_key,
            base_url=config.deepseek_base_url,
            model=config.deepseek_model,
            temperature=config.deepseek_temperature,
            max_tokens=config.deepseek_max_tokens
        )
        
        agent = NewsAgent(
            api_key=config.deepseek_api_key,
            base_url=config.deepseek_base_url,
            model=config.deepseek_model,
            temperature=config.deepseek_temperature,
            search_tool=config.search_default_tool,
            max_results=config.search_max_results
        )
        
        # Search for news
        articles = agent.search_news(prompt)
        
        # Analyze with context-aware agent
        analysis = agent.analyze_results(prompt, articles)
        
        # Store data
        data_manager.store_articles(session_id, articles)
        data_manager.store_report(session_id, analysis, len(articles))
        data_manager.update_session_run(session_id)
        
        # Generate and send report
        report_gen = ReportGenerator()
        html_report = report_gen.generate_html_report(
            articles, analysis, prompt, "scheduled"
        )
        text_report = report_gen.generate_text_report(
            articles, analysis, prompt, "scheduled"
        )
        
        email_reporter = EmailReporter(
            smtp_server=config.email_smtp_server,
            smtp_port=config.email_smtp_port,
            from_address=config.email_from,
            password=config.email_password,
            use_tls=config.email_use_tls
        )
        
        email_reporter.send_scheduled_report(email_to, prompt, html_report, text_report)
        
        logger.info(f"Monitoring cycle completed for session {session_id}")
        
    except Exception as e:
        logger.error(f"Error in monitoring cycle: {e}")


@click.group()
def cli():
    """News Aggregation System - AI-powered news monitoring and reporting."""
    pass


@cli.command()
@click.option('--prompt', '-p', required=True, help='Search query/topic')
@click.option('--email', '-e', required=True, help='Email address to send report')
@click.option('--config', '-c', default=None, help='Path to config file')
def instant(prompt: str, email: str, config: str):
    """Generate and send an instant news report."""
    
    console.print("[bold blue]📰 News Aggregation System - Instant Report[/bold blue]\n")
    
    # Load configuration
    cfg = ConfigManager(config)
    setup_logging(cfg.log_level)
    
    # Validate configuration
    is_valid, missing = cfg.validate_required()
    if not is_valid:
        console.print("[bold red]Error: Missing required configuration:[/bold red]")
        for key in missing:
            console.print(f"  - {key}")
        console.print("\nPlease set these in .env file or config.yaml")
        sys.exit(1)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        # Initialize components
        task = progress.add_task("Initializing...", total=None)
        
        deepseek = DeepSeekClient(
            api_key=cfg.deepseek_api_key,
            base_url=cfg.deepseek_base_url,
            model=cfg.deepseek_model,
            temperature=cfg.deepseek_temperature,
            max_tokens=cfg.deepseek_max_tokens
        )
        
        agent = NewsAgent(
            api_key=cfg.deepseek_api_key,
            base_url=cfg.deepseek_base_url,
            model=cfg.deepseek_model,
            temperature=cfg.deepseek_temperature,
            search_tool=cfg.search_default_tool,
            max_results=cfg.search_max_results
        )
        
        # Search for news
        progress.update(task, description=f"Searching for news about: {prompt}")
        articles = agent.search_news(prompt)
        
        console.print(f"[green]✓[/green] Found {len(articles)} articles")
        
        # Analyze with context-aware agent
        progress.update(task, description="Analyzing news with context-aware agent...")
        analysis = agent.analyze_results(prompt, articles)
        
        console.print("[green]✓[/green] Analysis complete")
        
        # Generate report
        progress.update(task, description="Generating report...")
        report_gen = ReportGenerator()
        html_report = report_gen.generate_html_report(articles, analysis, prompt, "instant")
        text_report = report_gen.generate_text_report(articles, analysis, prompt, "instant")
        
        # Send email
        progress.update(task, description=f"Sending report to {email}...")
        email_reporter = EmailReporter(
            smtp_server=cfg.email_smtp_server,
            smtp_port=cfg.email_smtp_port,
            from_address=cfg.email_from,
            password=cfg.email_password,
            use_tls=cfg.email_use_tls
        )
        
        success = email_reporter.send_instant_report(email, prompt, html_report, text_report)
        
        if success:
            console.print(f"\n[bold green]✓ Report sent successfully to {email}![/bold green]")
        else:
            console.print(f"\n[bold red]✗ Failed to send report[/bold red]")
            sys.exit(1)


@cli.command()
@click.option('--prompt', '-p', required=True, help='Search query/topic')
@click.option('--email', '-e', required=True, help='Email address to send reports')
@click.option('--interval', '-i', type=int, required=True, help='Monitoring interval in hours')
@click.option('--config', '-c', default=None, help='Path to config file')
def schedule(prompt: str, email: str, interval: int, config: str):
    """Start scheduled news monitoring (runs every N hours)."""
    
    global scheduler_instance
    
    console.print("[bold blue]🔔 News Aggregation System - Scheduled Monitoring[/bold blue]\n")
    
    # Load configuration
    cfg = ConfigManager(config)
    setup_logging(cfg.log_level)
    
    # Validate configuration
    is_valid, missing = cfg.validate_required()
    if not is_valid:
        console.print("[bold red]Error: Missing required configuration:[/bold red]")
        for key in missing:
            console.print(f"  - {key}")
        sys.exit(1)
    
    # Initialize data manager
    data_manager = DataManager(cfg.database_path)
    
    # Create monitoring session
    session_id = data_manager.create_session(prompt, interval, email)
    
    console.print(f"[green]✓[/green] Created monitoring session #{session_id}")
    console.print(f"[cyan]Prompt:[/cyan] {prompt}")
    console.print(f"[cyan]Interval:[/cyan] Every {interval} hours")
    console.print(f"[cyan]Email:[/cyan] {email}\n")
    
    # Initialize scheduler
    scheduler_instance = NewsScheduler(cfg.scheduler_timezone)
    
    # Schedule monitoring
    scheduler_instance.schedule_monitoring(
        session_id=session_id,
        interval_hours=interval,
        callback=run_monitoring_cycle,
        prompt=prompt,
        email_to=email,
        config=cfg,
        data_manager=data_manager
    )
    
    scheduler_instance.start()
    
    console.print("[bold green]✓ Monitoring started![/bold green]")
    console.print(f"[yellow]Press Ctrl+C to stop[/yellow]\n")
    
    # Keep running
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Stopping monitoring...[/yellow]")
        data_manager.stop_session(session_id)
        scheduler_instance.stop()
        console.print("[green]✓ Monitoring stopped[/green]")


@cli.command()
@click.option('--session-id', '-s', type=int, help='Specific session ID')
@click.option('--all', 'all_sessions', is_flag=True, help='Aggregate all sessions')
@click.option('--email', '-e', required=True, help='Email address to send report')
@click.option('--config', '-c', default=None, help='Path to config file')
def aggregate(session_id: int, all_sessions: bool, email: str, config: str):
    """Generate an aggregate report from monitoring history."""
    
    console.print("[bold blue]📊 News Aggregation System - Aggregate Report[/bold blue]\n")
    
    if not session_id and not all_sessions:
        console.print("[bold red]Error: Specify either --session-id or --all[/bold red]")
        sys.exit(1)
    
    # Load configuration
    cfg = ConfigManager(config)
    setup_logging(cfg.log_level)
    
    # Validate configuration
    is_valid, missing = cfg.validate_required()
    if not is_valid:
        console.print("[bold red]Error: Missing required configuration:[/bold red]")
        for key in missing:
            console.print(f"  - {key}")
        sys.exit(1)
    
    # Initialize components
    data_manager = DataManager(cfg.database_path)
    deepseek = DeepSeekClient(
        api_key=cfg.deepseek_api_key,
        base_url=cfg.deepseek_base_url,
        model=cfg.deepseek_model,
        temperature=cfg.deepseek_temperature,
        max_tokens=cfg.deepseek_max_tokens
    )
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        task = progress.add_task("Retrieving data...", total=None)
        
        # Get session data
        if session_id:
            session_data = data_manager.get_session(session_id)
            if not session_data:
                console.print(f"[bold red]Error: Session {session_id} not found[/bold red]")
                sys.exit(1)
            sessions_to_aggregate = [session_data]
        else:
            sessions_to_aggregate = data_manager.get_active_sessions()
        
        if not sessions_to_aggregate:
            console.print("[yellow]No sessions found[/yellow]")
            sys.exit(0)
        
        # Collect all data
        all_articles = []
        all_reports = []
        prompt = sessions_to_aggregate[0]['prompt']
        start_date = min(s['started_at'] for s in sessions_to_aggregate)
        end_date = datetime.now()
        
        for session in sessions_to_aggregate:
            sid = session['id']
            articles_grouped = data_manager.get_session_articles(sid)
            all_articles.extend(articles_grouped)
            reports = data_manager.get_session_reports(sid)
            all_reports.extend(reports)
        
        console.print(f"[green]✓[/green] Retrieved data from {len(sessions_to_aggregate)} session(s)")
        console.print(f"[green]✓[/green] Total articles: {sum(len(group) for group in all_articles)}")
        
        # Generate aggregate analysis
        progress.update(task, description="Creating aggregate analysis...")
        aggregate_analysis = deepseek.create_aggregate_summary(all_reports) if all_reports else "No previous reports found."
        
        # Generate report
        progress.update(task, description="Generating aggregate report...")
        report_gen = ReportGenerator()
        html_report = report_gen.generate_aggregate_report(
            all_articles, aggregate_analysis, prompt, start_date, end_date
        )
        
        # Send email
        progress.update(task, description=f"Sending report to {email}...")
        email_reporter = EmailReporter(
            smtp_server=cfg.email_smtp_server,
            smtp_port=cfg.email_smtp_port,
            from_address=cfg.email_from,
            password=cfg.email_password,
            use_tls=cfg.email_use_tls
        )
        
        success = email_reporter.send_aggregate_report(email, prompt, html_report)
        
        if success:
            console.print(f"\n[bold green]✓ Aggregate report sent to {email}![/bold green]")
        else:
            console.print(f"\n[bold red]✗ Failed to send report[/bold red]")
            sys.exit(1)


@cli.command()
@click.option('--config', '-c', default=None, help='Path to config file')
def status(config: str):
    """Show status of monitoring sessions."""
    
    cfg = ConfigManager(config)
    data_manager = DataManager(cfg.database_path)
    
    active_sessions = data_manager.get_active_sessions()
    
    if not active_sessions:
        console.print("[yellow]No active monitoring sessions[/yellow]")
        return
    
    console.print("[bold blue]Active Monitoring Sessions:[/bold blue]\n")
    
    for session in active_sessions:
        console.print(f"[cyan]Session #{session['id']}[/cyan]")
        console.print(f"  Prompt: {session['prompt']}")
        console.print(f"  Interval: Every {session['interval_hours']} hours")
        console.print(f"  Started: {session['started_at']}")
        console.print(f"  Last run: {session['last_run_at'] or 'Not yet run'}")
        console.print(f"  Email: {session['email_to']}\n")


if __name__ == '__main__':
    cli()
