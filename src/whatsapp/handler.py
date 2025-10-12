"""
WhatsApp message handler
Processes incoming messages and coordinates responses
"""

import logging
from src.whatsapp.client_mock import whatsapp_client
from src.whatsapp.formatter import (
    format_welcome_message,
    format_error_message,
    format_processing_message,
    format_specialty_selection
)

logger = logging.getLogger(__name__)


class MessageHandler:
    """Handles incoming WhatsApp messages"""

    async def _handle_feedback(self, from_number: str, message_text: str) -> bool:
        """
        Handle user feedback and forward to admin

        Args:
            from_number: User's phone number
            message_text: Original message with "feedback" prefix

        Returns:
            True if feedback was handled, False otherwise
        """
        message_lower = message_text.lower().strip()

        # Check if message starts with "feedback"
        if message_lower.startswith("feedback "):
            # Extract feedback content
            feedback_content = message_text[9:].strip()  # Remove "feedback " prefix

            if not feedback_content:
                return False

            # Send to admin
            from src.config import settings
            try:
                feedback_message = f"""📬 *User Feedback*

📱 From: {from_number}
💬 Message:

{feedback_content}

---
Reply to user: Send them a message directly"""

                await whatsapp_client.send_message(settings.admin_phone_number, feedback_message)
                logger.info(f"📤 Feedback forwarded from {from_number} to admin")

                # Confirm to user
                await whatsapp_client.send_message(
                    from_number,
                    "✅ Thank you for your feedback! Your message has been sent to the administrator."
                )
                return True
            except Exception as e:
                logger.error(f"❌ Error sending feedback: {e}")
                return False

        return False

    async def _handle_admin_command(self, message_text: str) -> str:
        """
        Handle admin commands (approve/reject users)

        Returns:
            Response message or None if not an admin command
        """
        from src.models.user_approval import user_approval_manager

        message_lower = message_text.lower().strip()

        # Approve user
        if message_lower.startswith("approve "):
            phone = message_text.split()[1].strip()
            success = await user_approval_manager.approve_user(phone)
            if success:
                return f"✅ User approved: {phone}\n\nThey can now use the bot."
            else:
                return f"❌ Error approving user: {phone}"

        # Reject user
        elif message_lower.startswith("reject "):
            phone = message_text.split()[1].strip()
            success = await user_approval_manager.reject_user(phone)
            if success:
                return f"❌ User rejected: {phone}"
            else:
                return f"❌ Error rejecting user: {phone}"

        # List pending users
        elif message_lower in ["pending", "list", "users"]:
            pending = await user_approval_manager.get_pending_users()
            if not pending:
                return "No users pending approval."

            response = "📋 *Users Pending Approval:*\n\n"
            for user in pending:
                response += f"📱 {user['phone_number']}\n"
                response += f"   Requested: {user['requested_at']}\n\n"
            response += "Reply: `approve <phone>` or `reject <phone>`"
            return response

        return None  # Not an admin command

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

            # Check for admin commands first
            from src.config import settings
            if from_number == settings.admin_phone_number:
                admin_response = await self._handle_admin_command(message_text)
                if admin_response:
                    await whatsapp_client.send_message(from_number, admin_response)
                    return

            # Check for feedback command (available to all users)
            if await self._handle_feedback(from_number, message_text):
                return

            # Check user approval status
            from src.models.user_approval import user_approval_manager
            is_approved = await user_approval_manager.is_user_approved(from_number)

            if not is_approved:
                # Send notification to admin
                await user_approval_manager.send_admin_notification(from_number, message_text)

                # Inform user they need approval
                pending_message = """👋 Thank you for your interest!

⏳ Your access is pending approval.

An administrator has been notified and will review your request shortly.

You'll be able to use the bot once approved."""
                await whatsapp_client.send_message(from_number, pending_message)
                return

            # Handle commands
            if message_text.lower() in ["hi", "hello", "start", "help", "/start"]:
                response = format_welcome_message()
                await whatsapp_client.send_message(from_number, response)
                return

            # Check if user has a pending specialty selection
            from src.models.user_session import user_session_manager
            pending_search = user_session_manager.get_pending_search(from_number)

            if pending_search:
                # User is replying with specialty selection
                specialty = self._parse_specialty_input(message_text)
                doctor_name = pending_search["doctor_name"]

                # Complete the session
                user_session_manager.complete_search(from_number)

                # Check user quota
                from src.models.user import user_quota_manager
                quota_status = await user_quota_manager.check_and_update_quota(from_number)

                if not quota_status.get("allowed", True):
                    response = format_error_message("quota_exceeded")
                    await whatsapp_client.send_message(from_number, response)
                    return

                # Proceed to search with specialty (empty string if user skipped)
                await self._perform_search(from_number, doctor_name, specialty)
                return

            # No pending search - check if user provided complete input
            # Try to extract both name and specialty from message
            doctor_info = self._extract_doctor_info(message_text)
            doctor_name = doctor_info.get("name")
            specialty = doctor_info.get("specialty", "")

            # Reject single digits or single characters as doctor names
            if not doctor_name or len(doctor_name.strip()) <= 1:
                response = format_error_message("invalid_input")
                await whatsapp_client.send_message(from_number, response)
                return

            # Check user quota
            from src.models.user import user_quota_manager
            quota_status = await user_quota_manager.check_and_update_quota(from_number)

            if not quota_status.get("allowed", True):
                response = format_error_message("quota_exceeded")
                await whatsapp_client.send_message(from_number, response)
                return

            # Simple strategy: Always search directly (specialty is optional)
            await self._perform_search(from_number, doctor_name, specialty)
            return

        except Exception as e:
            logger.error(f"❌ Error processing message: {e}", exc_info=True)
            await whatsapp_client.send_message(
                from_number,
                format_error_message("general")
            )

    def _parse_specialty_input(self, text: str) -> str:
        """
        Parse specialty from user's selection response

        Handles:
        - Number selection (1-10)
        - Specialty name
        - 0 or "skip" to skip specialty

        Args:
            text: User's response

        Returns:
            Specialty name or empty string if skipped
        """
        text = text.strip().lower()

        # Specialty number mapping (all 38 specialties)
        SPECIALTY_MAP = {
            "1": "cardiology",
            "2": "dermatology",
            "3": "endocrinology & diabetes",
            "4": "gastroenterology & hepatology",
            "5": "general surgery",
            "6": "obstetrics & gynaecology",
            "7": "oncology",
            "8": "ophthalmology",
            "9": "orthopaedic surgery",
            "10": "paediatrics",
            "11": "anaesthesiology & critical care",
            "12": "cardiothoracic surgery",
            "13": "dentistry",
            "14": "ear, nose & throat",
            "15": "emergency medicine",
            "16": "geriatric medicine",
            "17": "haematology",
            "18": "infectious diseases",
            "19": "internal medicine",
            "20": "nephrology",
            "21": "neurology",
            "22": "neurosurgery",
            "23": "nuclear medicine",
            "24": "pain medicine",
            "25": "palliative medicine",
            "26": "pathology",
            "27": "plastic & reconstructive surgery",
            "28": "psychiatry",
            "29": "radiology",
            "30": "rehabilitation medicine",
            "31": "respiratory medicine",
            "32": "rheumatology",
            "33": "robotic surgery",
            "34": "spine surgery",
            "35": "sports medicine",
            "36": "transplant medicine",
            "37": "urology",
            "38": "other"
        }

        # Check if user wants to skip
        if text in ["0", "skip", "no", "none", "cancel"]:
            logger.info("User chose to skip specialty selection")
            return ""

        # Check if it's a number
        if text in SPECIALTY_MAP:
            specialty = SPECIALTY_MAP[text]
            logger.info(f"User selected specialty by number: {text} → {specialty}")
            return specialty

        # Otherwise treat as specialty name
        SPECIALTIES = [
            "cardiology", "dermatology", "endocrinology", "gastroenterology",
            "gynecology", "hematology", "neurology", "obstetrics", "oncology",
            "ophthalmology", "orthopedics", "pediatrics", "psychiatry",
            "radiology", "surgery", "urology", "anesthesiology", "pathology"
        ]

        for specialty in SPECIALTIES:
            if specialty in text:
                logger.info(f"User selected specialty by name: {specialty}")
                return specialty

        # If no match, return as-is (let OpenAI handle it)
        logger.info(f"User input not recognized, using as-is: {text}")
        return text

    async def _perform_search(self, from_number: str, doctor_name: str, specialty: str = ""):
        """
        Perform doctor review search and send results

        Args:
            from_number: User's phone number
            doctor_name: Doctor's name
            specialty: Optional specialty
        """
        try:
            # Send processing message
            await whatsapp_client.send_message(
                from_number,
                format_processing_message()
            )

            # Track search time
            import time
            start_time = time.time()

            # Search for doctor reviews
            reviews = await self._search_doctor_reviews(doctor_name, specialty)

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
                cache_hit=len(reviews) > 0 and response_time_ms < 500,
                response_time_ms=response_time_ms,
                sources_used=list(set([r.get("source") for r in reviews if r.get("source")])),
                results_count=len(reviews),
                api_calls_count=0 if response_time_ms < 500 else 2,
                estimated_cost_usd=0.0 if response_time_ms < 500 else 0.01
            )

            # Send formatted results
            await whatsapp_client.send_formatted_review(
                from_number,
                doctor_name,
                reviews
            )

        except Exception as e:
            logger.error(f"❌ Error performing search: {e}", exc_info=True)
            await whatsapp_client.send_message(
                from_number,
                format_error_message("general")
            )

    def _extract_doctor_info(self, text: str) -> dict:
        """
        Extract doctor name and specialty from user input

        Supported formats:
        1. "Dr Smith, Cardiology"
        2. "Dr Smith | Cardiology"
        3. "Dr Smith - Cardiology"
        4. "Dr Smith Cardiology"
        5. "Dr Smith"

        Args:
            text: User input text

        Returns:
            Dict with 'name' and 'specialty' keys
        """
        # List of common medical specialties (English) - keep lowercase for matching
        SPECIALTIES = [
            "cardiology", "dermatology", "endocrinology", "gastroenterology",
            "gynecology", "hematology", "neurology", "obstetrics", "oncology",
            "ophthalmology", "orthopedics", "pediatrics", "psychiatry",
            "radiology", "surgery", "urology", "anesthesiology", "pathology",
            "plastic surgery", "emergency medicine", "family medicine",
            "internal medicine", "general practice", "gp"
        ]

        # Keep original text for doctor name, but create lowercase version for specialty matching
        original_text = text.strip()
        text_lower = text.lower().strip()

        # Remove common prefixes (case insensitive)
        for prefix in ["doctor", "dr.", "dr", "prof.", "prof"]:
            if text_lower.startswith(prefix):
                # Remove prefix from original text, preserving case
                prefix_len = len(prefix)
                original_text = original_text[prefix_len:].strip()
                text_lower = text_lower[prefix_len:].strip()
                break

        specialty = ""
        doctor_name = original_text  # Keep original case

        # Try to extract specialty using delimiters (case insensitive matching)
        for delimiter in [",", "|", "-", "/"]:
            if delimiter in text_lower:
                parts = text_lower.split(delimiter, 1)
                doctor_name_part = parts[0].strip()
                potential_specialty = parts[1].strip()

                # Check if it's a known specialty (case insensitive)
                if any(spec in potential_specialty for spec in SPECIALTIES):
                    specialty = potential_specialty
                    # Extract doctor name from original text
                    original_parts = original_text.split(delimiter, 1)
                    doctor_name = original_parts[0].strip()
                    break

        # If no delimiter, try to find specialty in text (case insensitive)
        if not specialty:
            for spec in SPECIALTIES:
                if spec in text_lower:
                    # Found specialty in text
                    # Remove specialty from original text, preserving case
                    specialty = spec
                    # Find the specialty in original text (case insensitive)
                    import re
                    pattern = re.compile(re.escape(spec), re.IGNORECASE)
                    doctor_name = pattern.sub("", original_text).strip()
                    break

        # Clean up doctor name - remove extra spaces
        doctor_name = " ".join(doctor_name.split())

        return {
            "name": doctor_name if doctor_name else "",
            "specialty": specialty
        }

    async def _search_doctor_reviews(self, doctor_name: str, specialty: str = "") -> list:
        """
        Search for doctor reviews using real search engines

        Args:
            doctor_name: Doctor's name
            specialty: Optional medical specialty

        Returns:
            List of review dicts
        """
        from src.search.aggregator import search_aggregator

        if specialty:
            logger.info(f"🔍 Searching for reviews: {doctor_name} ({specialty})")
        else:
            logger.info(f"🔍 Searching for reviews: {doctor_name}")

        # Use search aggregator with specialty
        result = await search_aggregator.search_doctor_reviews(
            doctor_name=doctor_name,
            specialty=specialty
        )

        return result.get("reviews", [])


# Global message handler instance
message_handler = MessageHandler()
