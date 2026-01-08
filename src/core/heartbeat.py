"""
Heartbeat Monitor for long-running analysis operations (v2.6.1)

Provides periodic progress feedback during long-running analyses
to indicate the process is still alive.
"""

import asyncio
from datetime import datetime
from typing import Optional

from src.core.config import HEARTBEAT_INTERVAL_SECONDS
from src.core.logger import log_print


class HeartbeatMonitor:
    """Monitor that displays periodic heartbeat messages during long operations.

    The heartbeat starts after the first interval (default 10 minutes) and
    continues every interval until stopped.

    Usage:
        monitor = HeartbeatMonitor(interval_seconds=600)
        await monitor.start()
        # ... long running operation ...
        await monitor.stop()
    """

    def __init__(self, interval_seconds: int = HEARTBEAT_INTERVAL_SECONDS):
        """Initialize the heartbeat monitor.

        Args:
            interval_seconds: Seconds between heartbeat messages (default: 600 = 10 min)
        """
        self.interval_seconds = interval_seconds
        self._task: Optional[asyncio.Task] = None
        self._start_time: Optional[datetime] = None
        self._running = False
        self._heartbeat_count = 0

    async def start(self) -> None:
        """Start the heartbeat monitor in the background.

        The first heartbeat appears after interval_seconds, then repeats.
        """
        if self._running:
            return

        self._running = True
        self._start_time = datetime.now()
        self._heartbeat_count = 0
        self._task = asyncio.create_task(self._heartbeat_loop())

    async def stop(self) -> None:
        """Stop the heartbeat monitor.

        Cancels the background task and cleans up.
        """
        self._running = False

        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    async def _heartbeat_loop(self) -> None:
        """Internal loop that emits heartbeat messages."""
        try:
            while self._running:
                # Wait for the interval
                await asyncio.sleep(self.interval_seconds)

                if not self._running:
                    break

                self._heartbeat_count += 1
                elapsed = self._format_elapsed()

                # Display heartbeat message
                log_print(
                    f"💓 Heartbeat #{self._heartbeat_count}: Analysis in progress... ({elapsed})"
                )

        except asyncio.CancelledError:
            # Normal cancellation, don't log error
            pass

    def _format_elapsed(self) -> str:
        """Format elapsed time as human-readable string."""
        if self._start_time is None:
            return "0s"

        elapsed_seconds = (datetime.now() - self._start_time).total_seconds()

        if elapsed_seconds >= 3600:
            hours = int(elapsed_seconds // 3600)
            minutes = int((elapsed_seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
        elif elapsed_seconds >= 60:
            minutes = int(elapsed_seconds // 60)
            seconds = int(elapsed_seconds % 60)
            return f"{minutes}m {seconds}s"
        else:
            return f"{int(elapsed_seconds)}s"

    @property
    def is_running(self) -> bool:
        """Check if the heartbeat monitor is currently running."""
        return self._running

    @property
    def elapsed_seconds(self) -> float:
        """Get elapsed seconds since start."""
        if self._start_time is None:
            return 0.0
        return (datetime.now() - self._start_time).total_seconds()
