"""Temporal worker process polling the trail-safety task queue."""

import asyncio
import logging
import sys
from typing import Optional
from temporalio.client import Client, TLSConfig
from temporalio.worker import Worker

from src.config import settings
from src.temporal.activities import (
    evaluate_tabpfn_risk_activity,
    dispatch_emergency_alert_activity,
    log_trail_telemetry_activity,
)
from src.temporal.workflows import TrailSafetyWorkflow

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (%(name)s) %(message)s",
)
logger = logging.getLogger("trailsafe.worker")


import socket


def is_temporal_host_available(host_port: str, timeout_seconds: float = 0.3) -> bool:
    """Fast non-blocking check whether Temporal target port is accepting connections."""
    try:
        if ":" in host_port:
            host, port_str = host_port.split(":", 1)
            port = int(port_str)
        else:
            host, port = host_port, 7233
        with socket.create_connection((host, port), timeout=timeout_seconds):
            return True
    except Exception:
        return False


async def create_temporal_client(timeout_seconds: Optional[float] = 2.0) -> Client:
    """Creates authenticated connection to Temporal local or cloud cluster with fast-failover timeout."""
    if not settings.TEMPORAL_USE_CLOUD:
        available = await asyncio.to_thread(is_temporal_host_available, settings.TEMPORAL_TARGET_HOST, 0.3)
        if not available:
            raise ConnectionError(f"Temporal daemon {settings.TEMPORAL_TARGET_HOST} is not running.")

    tls_config = None
    if settings.TEMPORAL_USE_CLOUD:
        if settings.TEMPORAL_TLS_CERT_PATH and settings.TEMPORAL_TLS_KEY_PATH:
            with open(settings.TEMPORAL_TLS_CERT_PATH, "rb") as f:
                client_cert = f.read()
            with open(settings.TEMPORAL_TLS_KEY_PATH, "rb") as f:
                client_key = f.read()
            tls_config = TLSConfig(client_cert=client_cert, client_private_key=client_key)

    coro = Client.connect(
        target_host=settings.TEMPORAL_TARGET_HOST,
        namespace=settings.TEMPORAL_NAMESPACE,
        api_key=settings.TEMPORAL_API_KEY,
        tls=tls_config,
    )
    if timeout_seconds is not None:
        client = await asyncio.wait_for(coro, timeout=timeout_seconds)
    else:
        client = await coro
    return client


async def run_worker() -> None:
    """Initializes and runs the Temporal worker listening for hike events."""
    logger.info(
        f"Connecting to Temporal host {settings.TEMPORAL_TARGET_HOST} (namespace: {settings.TEMPORAL_NAMESPACE})..."
    )
    try:
        client = await create_temporal_client()
        logger.info("Connected to Temporal cluster successfully.")
    except Exception as e:
        logger.error(f"Failed to connect to Temporal cluster: {e}")
        logger.info("Make sure temporal server is running: 'temporal server start-dev'")
        sys.exit(1)

    worker = Worker(
        client,
        task_queue=settings.TEMPORAL_TASK_QUEUE,
        workflows=[TrailSafetyWorkflow],
        activities=[
            evaluate_tabpfn_risk_activity,
            dispatch_emergency_alert_activity,
            log_trail_telemetry_activity,
        ],
    )

    logger.info(f"TrailSafe Worker started. Polling task queue '{settings.TEMPORAL_TASK_QUEUE}'...")
    try:
        await worker.run()
    except asyncio.CancelledError:
        logger.info("Worker stopped gracefully.")


if __name__ == "__main__":
    asyncio.run(run_worker())
