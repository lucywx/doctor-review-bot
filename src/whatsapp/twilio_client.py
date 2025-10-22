"""
Twilio WhatsApp API client for sending messages
"""

import httpx
import logging
from src.config import settings
from src.whatsapp.models import WhatsAppOutgoingMessage

logger = logging.getLogger(__name__)


class TwilioWhatsAppClient:
    """Client for interacting with Twilio WhatsApp API"""

    def __init__(self):
        self.account_sid = settings.twilio_account_sid
        self.auth_token = settings.twilio_auth_token
        self.whatsapp_number = settings.twilio_whatsapp_number
        self.base_url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Messages.json"

    async def send_message(self, to: str, message: str) -> dict:
        """
        Send a text message via Twilio WhatsApp

        Args:
            to: Recipient phone number (with country code, e.g., +1234567890)
            message: Message text to send

        Returns:
            API response dict
        """
        try:
            # Twilio uses Basic Auth
            import base64
            credentials = f"{self.account_sid}:{self.auth_token}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()

            headers = {
                "Authorization": f"Basic {encoded_credentials}",
                "Content-Type": "application/x-www-form-urlencoded"
            }

            # Twilio API format
            data = {
                "From": f"whatsapp:{self.whatsapp_number}",
                "To": f"whatsapp:{to}",
                "Body": message
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.base_url,
                    data=data,
                    headers=headers
                )

                response.raise_for_status()
                result = response.json()

                logger.info(f"✅ Twilio message sent to {to}")
                logger.debug(f"Twilio response: {result}")
                return result

        except httpx.HTTPStatusError as e:
            logger.error(f"❌ Twilio API error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"❌ Failed to send Twilio message: {e}")
            raise

    async def send_media_message(self, to: str, media_url: str, caption: str = "") -> dict:
        """
        Send media message via Twilio WhatsApp

        Args:
            to: Recipient phone number
            media_url: URL of the media file
            caption: Optional caption text

        Returns:
            API response dict
        """
        try:
            import base64
            credentials = f"{self.account_sid}:{self.auth_token}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()

            headers = {
                "Authorization": f"Basic {encoded_credentials}",
                "Content-Type": "application/x-www-form-urlencoded"
            }

            data = {
                "From": f"whatsapp:{self.whatsapp_number}",
                "To": f"whatsapp:{to}",
                "MediaUrl": media_url
            }
            
            if caption:
                data["Body"] = caption

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.base_url,
                    data=data,
                    headers=headers
                )

                response.raise_for_status()
                result = response.json()

                logger.info(f"✅ Twilio media message sent to {to}")
                return result

        except Exception as e:
            logger.error(f"❌ Failed to send Twilio media message: {e}")
            raise


# Global Twilio WhatsApp client instance
twilio_whatsapp_client = TwilioWhatsAppClient()
