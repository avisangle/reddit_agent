"""
Reddit Comment Engagement Agent - Main Entry Point

This is the main entry point for running the agent.
"""
import sys
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config import get_settings, Settings
from models.database import init_db, get_session_local
from utils.logging import get_logger, configure_logging
from utils.monitoring import get_metrics_collector

logger = get_logger(__name__)


def create_services(settings: Settings, session):
    """Create all service instances."""
    from services.reddit_client import RedditClient
    from services.context_builder import ContextBuilder
    from services.rule_engine import RuleEngine, RuleCache
    from services.prompt_manager import PromptManager
    from services.state_manager import StateManager
    from services.notifiers import get_notifier
    from agents.generator import DraftGenerator
    
    # LLM setup (using LangChain)
    try:
        if settings.openai_api_key:
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(
                api_key=settings.openai_api_key,
                model="gpt-4o-mini",
                temperature=0.7
            )
        elif settings.anthropic_api_key:
            from langchain_anthropic import ChatAnthropic
            llm = ChatAnthropic(
                api_key=settings.anthropic_api_key,
                model="claude-3-haiku-20240307",
                temperature=0.7
            )
        elif settings.gemini_api_key:
            from langchain_google_genai import ChatGoogleGenerativeAI
            llm = ChatGoogleGenerativeAI(
                google_api_key=settings.gemini_api_key,
                model="gemini-2.5-flash",
                temperature=0.7
            )
        else:
            logger.warning("No LLM API key configured, using mock")
            llm = None
    except ImportError as e:
        logger.warning(f"LLM import failed: {e}, using mock")
        llm = None
    
    # Create notifier based on config
    notifier = get_notifier(
        notification_type=settings.notification_type,
        webhook_url=settings.webhook_url,
        webhook_secret=settings.webhook_secret,
        public_url=settings.public_url,
        telegram_bot_token=settings.telegram_bot_token,
        telegram_chat_id=settings.telegram_chat_id,
        slack_webhook_url=settings.slack_webhook_url,
        slack_channel=settings.slack_channel
    )

    # Performance tracker (Phase 3 - Historical Learning)
    performance_tracker = None
    if settings.learning_enabled:
        from services.performance_tracker import PerformanceTracker
        performance_tracker = PerformanceTracker(
            session=session,
            settings=settings
        )
        logger.info("historical_learning_enabled")
    else:
        logger.info("historical_learning_disabled")

    # Quality scoring (optional, controlled by feature flag)
    quality_scorer = None
    if settings.quality_scoring_enabled:
        from services.quality_scorer import QualityScorer
        quality_scorer = QualityScorer(
            settings=settings,
            performance_tracker=performance_tracker  # Phase 3: Inject PerformanceTracker
        )
        logger.info("quality_scoring_enabled")
    else:
        logger.info("quality_scoring_disabled")

    return {
        "reddit_client": RedditClient(),
        "context_builder": ContextBuilder(max_tokens=2000),
        "rule_engine": RuleEngine(cache=RuleCache()),
        "prompt_manager": PromptManager(),
        "generator": DraftGenerator(llm=llm),
        "state_manager": StateManager(
            session=session,
            max_daily=settings.max_comments_per_day,
            cooldown_hours=settings.rising_cooldown_hours,
            inbox_cooldown_hours=settings.inbox_cooldown_hours
        ),
        "notifier": notifier,
        "quality_scorer": quality_scorer
    }


def run_agent(dry_run: bool = False, single_run: bool = True):
    """
    Run the agent workflow.
    
    Args:
        dry_run: If True, don't actually post or notify
        single_run: If True, run once and exit
    """
    configure_logging()
    logger.info("agent_starting", dry_run=dry_run)
    
    try:
        # Load settings
        settings = get_settings()
        logger.info("settings_loaded")
        
        # Initialize database
        init_db()
        SessionLocal = get_session_local()
        session = SessionLocal()
        logger.info("database_initialized")
        
        # Create services
        services = create_services(settings, session)
        logger.info("services_created")
        
        # Create workflow runner
        from workflow.runner import WorkflowRunner
        
        runner = WorkflowRunner(
            **services,
            settings=settings,
            min_jitter=settings.min_jitter_seconds,
            max_jitter=settings.max_jitter_seconds,
            max_per_run=settings.max_comments_per_run,
            dry_run=dry_run
        )
        
        # Run workflow
        result = runner.run()
        
        # Update metrics
        collector = get_metrics_collector()
        collector.increment("drafts_generated", result.processed_count)
        collector.mark_run()
        
        if result.error_count > 0:
            collector.mark_error()
        else:
            collector.mark_success()
        
        logger.info(
            "agent_completed",
            processed=result.processed_count,
            errors=result.error_count,
            duration=result.duration_seconds
        )
        
        return result
        
    except Exception as e:
        logger.error("agent_failed", error=str(e))
        raise
    finally:
        if 'session' in locals():
            session.close()


def run_callback_server(host: str = "0.0.0.0", port: int = 8000, auto_publish: bool = True):
    """
    Run the HITL callback server.
    
    Args:
        host: Server host
        port: Server port
        auto_publish: If True, auto-publish approved drafts to Reddit
    """
    import uvicorn
    from api.callback_server import create_callback_app
    from models.database import get_session_local, init_db
    from services.state_manager import StateManager
    from services.reddit_client import RedditClient
    from services.poster import CommentPoster
    
    from pathlib import Path

    configure_logging()

    # Check if .env file exists
    env_file = Path(".env")

    if not env_file.exists():
        # No .env file - start minimal server with setup wizard only
        logger.info("no_env_file_starting_setup_mode")
        app = create_callback_app(
            state_manager=None,
            secret=None,
            poster=None,
            auto_publish=False
        )
        logger.info(
            "callback_server_starting_setup_mode",
            host=host,
            port=port,
            message="Access setup wizard at http://{}:{}/setup".format(host if host != "0.0.0.0" else "localhost", port)
        )
        uvicorn.run(app, host=host, port=port)
        return

    # .env exists - load settings and initialize normally
    settings = get_settings()

    # Initialize database
    init_db()
    SessionLocal = get_session_local()
    session = SessionLocal()

    state_manager = StateManager(
        session=session,
        max_daily=settings.max_comments_per_day,
        cooldown_hours=settings.rising_cooldown_hours,
        inbox_cooldown_hours=settings.inbox_cooldown_hours
    )

    # Create poster for auto-publish if enabled
    poster = None
    if auto_publish:
        try:
            reddit_client = RedditClient()
            poster = CommentPoster(
                reddit_client=reddit_client,
                state_manager=state_manager,
                min_jitter=5,  # Short jitter for responsiveness
                max_jitter=15,
                dry_run=settings.dry_run
            )
            logger.info("auto_publish_enabled")
        except Exception as e:
            logger.warning("auto_publish_disabled", error=str(e))
            poster = None

    app = create_callback_app(
        state_manager=state_manager,
        secret=settings.webhook_secret,
        poster=poster,
        auto_publish=auto_publish
    )

    logger.info(
        "callback_server_starting",
        host=host,
        port=port,
        auto_publish=poster is not None
    )
    uvicorn.run(app, host=host, port=port)


def publish_approved_drafts(limit: int = 3, dry_run: bool = False):
    """
    Publish approved drafts to Reddit.
    
    Args:
        limit: Maximum drafts to publish
        dry_run: If True, don't actually post
    """
    configure_logging()
    logger.info("publish_starting", limit=limit, dry_run=dry_run)
    
    try:
        settings = get_settings()
        
        # Initialize database
        init_db()
        SessionLocal = get_session_local()
        session = SessionLocal()
        
        # Create services
        from services.reddit_client import RedditClient
        from services.state_manager import StateManager
        from services.poster import CommentPoster
        
        reddit_client = RedditClient()
        state_manager = StateManager(
            session=session,
            max_daily=settings.max_comments_per_day,
            cooldown_hours=settings.rising_cooldown_hours,
            inbox_cooldown_hours=settings.inbox_cooldown_hours
        )

        poster = CommentPoster(
            reddit_client=reddit_client,
            state_manager=state_manager,
            min_jitter=settings.min_jitter_seconds // 10,
            max_jitter=settings.max_jitter_seconds // 10,
            dry_run=dry_run
        )
        
        # Publish
        results = poster.publish_approved(limit=limit)
        
        # Summary
        success_count = sum(1 for r in results if r.success)
        logger.info(
            "publish_completed",
            total=len(results),
            success=success_count,
            failed=len(results) - success_count
        )
        
        # Print results
        for result in results:
            status = "✅" if result.success else "❌"
            print(f"{status} {result.draft_id}: {result.error or result.comment_id or 'dry-run'}")
        
    except Exception as e:
        logger.error("publish_failed", error=str(e))
        raise
    finally:
        if 'session' in locals():
            session.close()


def check_engagement_metrics(limit: int = 50):
    """
    Check engagement metrics for published comments after 24h.

    Args:
        limit: Maximum drafts to check
    """
    configure_logging()
    logger.info("engagement_check_starting", limit=limit)

    try:
        settings = get_settings()

        # Initialize database
        init_db()
        SessionLocal = get_session_local()
        session = SessionLocal()

        # Create services
        from services.reddit_client import RedditClient
        from services.state_manager import StateManager
        from services.engagement_checker import EngagementChecker

        reddit_client = RedditClient()
        state_manager = StateManager(
            session=session,
            max_daily=settings.max_comments_per_day,
            cooldown_hours=settings.rising_cooldown_hours,
            inbox_cooldown_hours=settings.inbox_cooldown_hours
        )

        engagement_checker = EngagementChecker(
            session=session,
            reddit_client=reddit_client,
            state_manager=state_manager,
            settings=settings
        )

        # Check engagement
        results = engagement_checker.check_pending_engagements(limit=limit)

        # Summary
        logger.info(
            "engagement_check_completed",
            checked=results["checked"],
            success=results["success"],
            failed=results["failed"]
        )

        # Print results
        print(f"✅ Checked: {results['checked']}")
        print(f"✅ Success: {results['success']}")
        print(f"❌ Failed: {results['failed']}")

    except Exception as e:
        logger.error("engagement_check_failed", error=str(e))
        raise
    finally:
        if 'session' in locals():
            session.close()


def main():
    """Main entry point with CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Reddit Comment Engagement Agent"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Run command
    run_parser = subparsers.add_parser("run", help="Run the agent")
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without posting or notifying"
    )
    run_parser.add_argument(
        "--once",
        action="store_true",
        default=True,
        help="Run once and exit (default)"
    )
    
    # Server command
    server_parser = subparsers.add_parser("server", help="Run callback server")
    server_parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Server host (default: 0.0.0.0)"
    )
    server_parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Server port (default: 8000)"
    )
    server_parser.add_argument(
        "--no-auto-publish",
        action="store_true",
        help="Disable auto-publishing approved drafts"
    )
    
    # Health command
    health_parser = subparsers.add_parser("health", help="Show health status")
    
    # Publish command
    publish_parser = subparsers.add_parser("publish", help="Publish approved drafts")
    publish_parser.add_argument(
        "--limit",
        type=int,
        default=3,
        help="Maximum drafts to publish (default: 3)"
    )
    publish_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without actually posting"
    )

    # Check-engagement command (Phase 4)
    engagement_parser = subparsers.add_parser(
        "check-engagement",
        help="Check engagement metrics for published comments"
    )
    engagement_parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Maximum drafts to check (default: 50)"
    )

    args = parser.parse_args()
    
    if args.command == "run":
        result = run_agent(dry_run=args.dry_run)
        sys.exit(0 if result.error_count == 0 else 1)
        
    elif args.command == "server":
        run_callback_server(
            host=args.host,
            port=args.port,
            auto_publish=not args.no_auto_publish
        )
        
    elif args.command == "health":
        collector = get_metrics_collector()
        status = collector.get_health_status()
        print(f"Status: {status['status']}")
        if status['warnings']:
            print("Warnings:")
            for w in status['warnings']:
                print(f"  - {w}")
    
    elif args.command == "publish":
        publish_approved_drafts(limit=args.limit, dry_run=args.dry_run)

    elif args.command == "check-engagement":
        check_engagement_metrics(limit=args.limit)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
