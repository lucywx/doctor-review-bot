"""
WhatsApp API client for sending messages
"""

import httpx
import logging
from src.config import settings
from src.whatsapp.models import WhatsAppOutgoingMessage

logger = logging.getLogger(__name__)


class WhatsAppClient:
    """Client for interacting with WhatsApp Business Cloud API"""

    def __init__(self):
        self.phone_number_id = settings.whatsapp_phone_number_id
        self.access_token = settings.whatsapp_access_token
        self.base_url = f"https://graph.facebook.com/v18.0/{self.phone_number_id}/messages"

    async def send_message(self, to: str, message: str) -> dict:
        """
        Send a text message via WhatsApp

        Args:
            to: Recipient phone number (with country code)
            message: Message text to send

        Returns:
            API response dict
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }

            payload = WhatsAppOutgoingMessage.create_text_message(to, message)

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.base_url,
                    json=payload.model_dump(),
                    headers=headers
                )

                response.raise_for_status()
                result = response.json()

                logger.info(f"✅ Message sent to {to}")
                return result

        except httpx.HTTPStatusError as e:
            logger.error(f"❌ WhatsApp API error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"❌ Failed to send message: {e}")
            raise

    async def send_formatted_review(self, to: str, doctor_name: str, reviews: list) -> dict:
        """
        Send formatted doctor review results

        Args:
            to: Recipient phone number
            doctor_name: Doctor's name
            reviews: List of review dicts

        Returns:
            API response dict
        """
        from src.whatsapp.formatter import format_review_response

        formatted_message = format_review_response(doctor_name, reviews)
        return await self.send_message(to, formatted_message)


# Global WhatsApp client instance
whatsapp_client = WhatsAppClient()
