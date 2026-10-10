"""TrailSafe configuration management backed by Pydantic."""

from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Base paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = BASE_DIR / "data"

    # Temporal Orchestration
    TEMPORAL_TARGET_HOST: str = "localhost:7233"
    TEMPORAL_NAMESPACE: str = "default"
    TEMPORAL_USE_CLOUD: bool = False
    TEMPORAL_API_KEY: Optional[str] = None
    TEMPORAL_TLS_CERT_PATH: Optional[str] = None
    TEMPORAL_TLS_KEY_PATH: Optional[str] = None
    TEMPORAL_TASK_QUEUE: str = "trail-safety-task-queue"

    # Prior Labs TabPFN
    TABPFN_MODE: str = "local"  # 'local' or 'cloud'
    TABPFN_API_KEY: Optional[str] = None
    TABPFN_TOKEN: Optional[str] = None
    TABPFN_DEVICE: str = "cpu"  # 'cpu', 'cuda', 'mps'
    TABPFN_N_ESTIMATORS: int = 2  # 1-2 for fast CPU forward passes, 8 for high-compute ensembles

    # Emergency Dispatch
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_EMERGENCY_CHAT_ID: Optional[str] = None
    TELEGRAM_CHAT_ID: Optional[str] = None
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_FROM_PHONE: Optional[str] = None
    TWILIO_WHATSAPP_FROM: Optional[str] = None
    EMERGENCY_CONTACT_PHONE: Optional[str] = None
    TWILIO_WHATSAPP_TO: Optional[str] = None

    @property
    def effective_tabpfn_key(self) -> Optional[str]:
        return self.TABPFN_API_KEY or self.TABPFN_TOKEN

    @property
    def effective_telegram_chat_id(self) -> Optional[str]:
        return self.TELEGRAM_EMERGENCY_CHAT_ID or self.TELEGRAM_CHAT_ID

    @property
    def effective_twilio_from(self) -> Optional[str]:
        return self.TWILIO_FROM_PHONE or (self.TWILIO_WHATSAPP_FROM.replace("whatsapp:", "") if self.TWILIO_WHATSAPP_FROM else None)

    @property
    def effective_emergency_phone(self) -> Optional[str]:
        return self.EMERGENCY_CONTACT_PHONE or (self.TWILIO_WHATSAPP_TO.replace("whatsapp:", "") if self.TWILIO_WHATSAPP_TO else None)

    # Trail & Safety Thresholds
    DEFAULT_CHECKPOINT_TIMEOUT_MINUTES: int = 45
    SAFETY_GRACE_PERIOD_MINUTES: int = 10
    HAZARD_PROBABILITY_THRESHOLD: float = 0.70

    # API / Web Server
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000


settings = Settings()
