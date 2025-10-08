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

    async def send_formatted_review(self, to: str, doctor_name: str, reviews: list) -> dict:
        """Mock send formatted review"""
        from src.whatsapp.formatter import format_review_response

        formatted_message = format_review_response(doctor_name, reviews)
        return await self.send_message(to, formatted_message)


# Export based on environment and provider
from src.config import settings

def get_whatsapp_client():
    """Get the appropriate WhatsApp client based on configuration"""
    
    # Check if we should use mock client
    if (settings.environment == "development" or 
        settings.whatsapp_provider == "mock" or
        (settings.whatsapp_provider == "meta" and settings.whatsapp_access_token == "your_access_token") or
        (settings.whatsapp_provider == "twilio" and settings.twilio_account_sid == "your_twilio_account_sid")):
        
        logger.info("🧪 Using Mock WhatsApp Client for testing")
        return MockWhatsAppClient()
    
    # Use real clients based on provider
    if settings.whatsapp_provider == "twilio":
        from src.whatsapp.twilio_client import TwilioWhatsAppClient
        logger.info("📱 Using Twilio WhatsApp Client")
        return TwilioWhatsAppClient()
    
    elif settings.whatsapp_provider == "meta":
        from src.whatsapp.client import WhatsAppClient
        logger.info("📱 Using Meta WhatsApp Client")
        return WhatsAppClient()
    
    else:
        logger.warning("⚠️ Unknown WhatsApp provider, using Mock client")
        return MockWhatsAppClient()

# Global WhatsApp client instance
whatsapp_client = get_whatsapp_client()
