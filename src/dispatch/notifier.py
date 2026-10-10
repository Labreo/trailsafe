"""Emergency dispatch notification handlers for Telegram and SMS.

Orchestrates multi-channel escalation alerts when a solo hiker misses
a checkpoint window or triggers an urgent SOS.
"""

from datetime import datetime, timezone
import json
import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import requests

from src.config import settings

logger = logging.getLogger("trailsafe.dispatch")


class EmergencyDispatchMessage(BaseModel):
    """Structured emergency alert payload."""

    hiker_id: str
    trail_name: str
    last_checkpoint_id: str
    last_checkpoint_name: str
    latitude: float
    longitude: float
    hours_elapsed: float
    reason: str
    hazard_probability: float
    water_remaining_ml: float
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class EmergencyDispatcher:
    """Multi-channel emergency dispatcher with verifiable audit records."""

    def __init__(self) -> None:
        self.telegram_bot_token = settings.TELEGRAM_BOT_TOKEN
        self.telegram_chat_id = settings.effective_telegram_chat_id
        self.twilio_sid = settings.TWILIO_ACCOUNT_SID
        self.twilio_token = settings.TWILIO_AUTH_TOKEN
        self.twilio_from = settings.effective_twilio_from
        self.emergency_contact = settings.effective_emergency_phone

    def format_alert_text(self, msg: EmergencyDispatchMessage) -> str:
        """Formats alert message."""
        maps_url = f"https://www.google.com/maps?q={msg.latitude:.5f},{msg.longitude:.5f}"
        return (
            f"TRAILSAFE RESCUE ALERT\n"
            f"Hiker: {msg.hiker_id}\n"
            f"Trail: {msg.trail_name}\n"
            f"Status: DEAD-MAN SWITCH TIMEOUT / SOS\n"
            f"Last Confirmed Waypoint: {msg.last_checkpoint_name} ({msg.last_checkpoint_id})\n"
            f"GPS Coordinates: {msg.latitude:.5f}, {msg.longitude:.5f}\n"
            f"Map Link: {maps_url}\n"
            f"Active Duration: {msg.hours_elapsed:.1f} hours\n"
            f"Prior Labs TabPFN Hazard Risk: {msg.hazard_probability * 100:.1f}%\n"
            f"Water Remaining: {msg.water_remaining_ml:.0f} mL\n"
            f"Reason: {msg.reason}\n"
            f"Timestamp: {msg.timestamp}"
        )

    def dispatch_telegram(self, text: str) -> Dict[str, Any]:
        """Dispatches alert via Telegram Bot API."""
        if not self.telegram_bot_token or not self.telegram_chat_id:
            return {
                "channel": "telegram",
                "status": "skipped",
                "detail": "TELEGRAM_BOT_TOKEN or TELEGRAM_EMERGENCY_CHAT_ID not configured",
            }

        url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
        payload = {"chat_id": self.telegram_chat_id, "text": text}
        try:
            resp = requests.post(url, json=payload, timeout=10)
            if resp.status_code == 200:
                return {"channel": "telegram", "status": "delivered", "response": resp.json()}
            return {"channel": "telegram", "status": "failed", "code": resp.status_code, "body": resp.text}
        except Exception as e:
            logger.error(f"Telegram dispatch error: {e}")
            return {"channel": "telegram", "status": "error", "error": str(e)}

    def dispatch_sms(self, text: str) -> Dict[str, Any]:
        """Dispatches alert via Twilio SMS API."""
        if not (self.twilio_sid and self.twilio_token and self.twilio_from and self.emergency_contact):
            return {
                "channel": "twilio_sms",
                "status": "skipped",
                "detail": "Twilio credentials or EMERGENCY_CONTACT_PHONE not configured",
            }

        url = f"https://api.twilio.com/2010-04-01/Accounts/{self.twilio_sid}/Messages.json"
        data = {
            "From": self.twilio_from,
            "To": self.emergency_contact,
            "Body": text[:1500],
        }
        try:
            resp = requests.post(url, data=data, auth=(self.twilio_sid, self.twilio_token), timeout=10)
            if resp.status_code in (200, 201):
                return {"channel": "twilio_sms", "status": "delivered", "sid": resp.json().get("sid")}
            return {"channel": "twilio_sms", "status": "failed", "code": resp.status_code, "body": resp.text}
        except Exception as e:
            logger.error(f"Twilio SMS dispatch error: {e}")
            return {"channel": "twilio_sms", "status": "error", "error": str(e)}

    def dispatch(self, msg: EmergencyDispatchMessage) -> Dict[str, Any]:
        """Fires all configured channels and returns verifiable audit record."""
        alert_text = self.format_alert_text(msg)
        tg_res = self.dispatch_telegram(alert_text)
        sms_res = self.dispatch_sms(alert_text)

        audit_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "hiker_id": msg.hiker_id,
            "trail_name": msg.trail_name,
            "reason": msg.reason,
            "channels": [tg_res, sms_res],
            "alert_body": alert_text,
        }
        logger.warning(f"EMERGENCY DISPATCH EXECUTED: {audit_entry}")
        return audit_entry
