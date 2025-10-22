"""
Mock WhatsApp client for testing without real API
"""

import logging

logger = logging.getLogger(__name__)


class MockWhatsAppClient:
    """Mock client for testing"""

    async def send_message(self, to: str, message: str) -> dict:
        """Mock send message"""
        logger.info(f"📤 [MOCK] Sending message to {to}")
        logger.info(f"Message content:\n{message}")
        logger.info("─" * 50)

        return {
            "messaging_product": "whatsapp",
            "contacts": [{"input": to, "wa_id": to}],
            "messages": [{"id": "mock_message_id"}]
        }


# Export based on environment and provider
from src.config import settings

def get_whatsapp_client():
    """Get the appropriate WhatsApp client based on configuration"""

    # Check if we should use mock client
    if (settings.environment == "development" or
        settings.twilio_account_sid == "your_twilio_account_sid"):

        logger.info("🧪 Using Mock WhatsApp Client for testing")
        return MockWhatsAppClient()

    # Use Twilio WhatsApp client
    from src.whatsapp.twilio_client import TwilioWhatsAppClient
    logger.info("📱 Using Twilio WhatsApp Client")
    return TwilioWhatsAppClient()

# Global WhatsApp client instance
whatsapp_client = get_whatsapp_client()
