"""Sentry error monitoring and performance tracking integration."""

import os
from typing import Any
from src.utils.helpers import get_logger

logger = get_logger(__name__)


class SentryMonitor:
    """Manages Sentry SDK initialization and error event reporting."""

    def __init__(self, dsn: str | None = None, environment: str | None = None) -> None:
        """Initialize Sentry monitor and auto-detect credentials.

        Args:
            dsn: Sentry Data Source Name URL. Auto-detected from SENTRY_DSN if None.
            environment: Deployment environment (e.g. production, development).
        """
        self.dsn = dsn or os.getenv("SENTRY_DSN", "https://3d2c524dcc9821570dc0d47c89c0b095@o4512221731749888.ingest.de.sentry.io/4512221744595024")
        self.environment = environment or os.getenv("SENTRY_ENVIRONMENT", os.getenv("APP_ENV", "development"))
        self.traces_sample_rate = float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "1.0"))
        self.profile_session_sample_rate = float(os.getenv("SENTRY_PROFILE_SESSION_SAMPLE_RATE", "1.0"))
        self.enabled = False
        self._init_sentry()

    def _init_sentry(self) -> None:
        """Initialize sentry_sdk client if DSN is configured."""
        if not self.dsn:
            logger.info("SENTRY_DSN not set. Exception monitoring disabled.")
            return

        try:
            import sentry_sdk

            sentry_sdk.init(
                dsn=self.dsn,
                environment=self.environment,
                send_default_pii=True,
                enable_logs=True,
                traces_sample_rate=self.traces_sample_rate,
                profile_session_sample_rate=self.profile_session_sample_rate,
                profile_lifecycle="trace",
            )
            self.enabled = True
            logger.info(f"Sentry error & performance monitoring initialized ({self.environment}).")
        except ImportError:
            logger.warning("sentry-sdk package not installed. Run: pip install sentry-sdk")
        except Exception as exc:
            logger.warning(f"Sentry initialization failed: {exc}")


    def capture_exception(self, exc: Exception, tags: dict[str, Any] | None = None) -> str | None:
        """Report an exception to Sentry with optional tags.

        Args:
            exc: Exception instance to report.
            tags: Key-value dictionary of contextual tags.

        Returns:
            Sentry event ID string if sent, else None.
        """
        if not self.enabled:
            return None

        try:
            import sentry_sdk

            with sentry_sdk.push_scope() as scope:
                if tags:
                    for key, val in tags.items():
                        scope.set_tag(key, str(val))
                event_id = sentry_sdk.capture_exception(exc)
                logger.info(f"Exception reported to Sentry [Event ID: {event_id}]")
                return event_id
        except Exception as err:
            logger.error(f"Failed to send exception to Sentry: {err}")
            return None

    def capture_message(self, message: str, level: str = "info") -> str | None:
        """Report a custom message to Sentry.

        Args:
            message: Text message to capture.
            level: Event severity level (info, warning, error).

        Returns:
            Sentry event ID string if sent, else None.
        """
        if not self.enabled:
            return None

        try:
            import sentry_sdk

            event_id = sentry_sdk.capture_message(message, level=level)
            return event_id
        except Exception as err:
            logger.error(f"Failed to send message to Sentry: {err}")
            return None
