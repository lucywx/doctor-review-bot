"""
WhatsApp message handler
Processes incoming messages and coordinates responses
"""

import logging
from src.whatsapp.client_mock import whatsapp_client
from src.whatsapp.formatter import (
    format_welcome_message,
    format_error_message,
    format_processing_message
)

logger = logging.getLogger(__name__)


class MessageHandler:
    """Handles incoming WhatsApp messages"""

    async def process_message(self, from_number: str, message_text: str):
        """
        Process incoming message and send response

        Args:
            from_number: Sender's phone number
            message_text: Message content
        """
        logger.info(f"📨 Received message from {from_number}: {message_text}")

        try:
            # Clean input
            message_text = message_text.strip()

            # Handle commands
            if message_text.lower() in ["hi", "hello", "你好", "开始", "帮助", "/start"]:
                response = format_welcome_message()
                await whatsapp_client.send_message(from_number, response)
                return

            # Check user quota
            from src.models.user import user_quota_manager
            quota_status = await user_quota_manager.check_and_update_quota(from_number)

            if not quota_status.get("allowed", True):
                response = format_error_message("quota_exceeded")
                await whatsapp_client.send_message(from_number, response)
                return

            # Extract doctor name
            doctor_name = self._extract_doctor_name(message_text)

            if not doctor_name:
                response = format_error_message("invalid_input")
                await whatsapp_client.send_message(from_number, response)
                return

            # Send processing message
            await whatsapp_client.send_message(
                from_number,
                format_processing_message()
            )

            # Track search time
            import time
            start_time = time.time()

            # Search for doctor reviews
            reviews = await self._search_doctor_reviews(doctor_name)

            # Calculate response time
            response_time_ms = int((time.time() - start_time) * 1000)

            # Log search
            from src.models.search_log import search_logger
            from src.cache.manager import cache_manager

            doctor_id = cache_manager.generate_doctor_id(doctor_name)
            await search_logger.log_search(
                user_id=from_number,
                doctor_name=doctor_name,
                doctor_id=doctor_id,
                cache_hit=len(reviews) > 0 and response_time_ms < 500,  # Heuristic
                response_time_ms=response_time_ms,
                sources_used=list(set([r.get("source") for r in reviews if r.get("source")])),
                results_count=len(reviews),
                api_calls_count=0 if response_time_ms < 500 else 2,  # Estimate
                estimated_cost_usd=0.0 if response_time_ms < 500 else 0.01
            )

            # Send formatted results
            await whatsapp_client.send_formatted_review(
                from_number,
                doctor_name,
                reviews
            )

        except Exception as e:
            logger.error(f"❌ Error processing message: {e}", exc_info=True)
            await whatsapp_client.send_message(
                from_number,
                format_error_message("general")
            )

    def _extract_doctor_name(self, text: str) -> str:
        """
        Extract doctor name from user input

        Args:
            text: User input text

        Returns:
            Extracted doctor name
        """
        # Simple extraction for now
        # Remove common words
        text = text.replace("医生", "").replace("大夫", "").strip()

        # TODO: Add more sophisticated name extraction logic
        # - Handle titles (主任, 教授, etc.)
        # - Extract hospital name separately
        # - Handle location

        return text if len(text) > 0 else ""

    async def _search_doctor_reviews(self, doctor_name: str) -> list:
        """
        Search for doctor reviews using real search engines

        Args:
            doctor_name: Doctor's name

        Returns:
            List of review dicts
        """
        from src.search.aggregator import search_aggregator

        logger.info(f"🔍 Searching for reviews: {doctor_name}")

        # Use search aggregator
        result = await search_aggregator.search_doctor_reviews(doctor_name)

        return result.get("reviews", [])


# Global message handler instance
message_handler = MessageHandler()
