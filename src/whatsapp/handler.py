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

            # User sent a doctor name - search directly (no specialty selection needed)
            doctor_name = message_text.strip()

            # Reject single digits or single characters as doctor names
            if len(doctor_name) <= 1:
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

            # Search directly - no specialty needed
            await self._perform_search(from_number, doctor_name)
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

    async def _perform_search(self, from_number: str, doctor_name: str):
        """
        Perform doctor review search and send results

        Args:
            from_number: User's phone number
            doctor_name: Doctor's name
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

            # Search for doctor reviews using Google + OpenAI
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
                cache_hit=len(reviews) > 0 and response_time_ms < 500,
                response_time_ms=response_time_ms,
                sources_used=list(set([r.get("source") for r in reviews if r.get("source")])),
                results_count=len(reviews),
                api_calls_count=0 if response_time_ms < 500 else 2,
                estimated_cost_usd=0.0 if response_time_ms < 500 else 0.01
            )

            # Send results in batches to show all reviews
            # Each message can hold ~5 reviews within 1600 char limit
            await self._send_reviews_in_batches(from_number, doctor_name, reviews)

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

    async def _send_reviews_in_batches(self, from_number: str, doctor_name: str, reviews: list):
        """
        Send reviews in multiple messages to show all results

        Args:
            from_number: User's phone number
            doctor_name: Doctor's name
            reviews: List of all reviews
        """
        from src.whatsapp.formatter import format_review_batch

        if not reviews:
            from src.whatsapp.formatter import format_review_response
            no_results = format_review_response(doctor_name, [])
            await whatsapp_client.send_message(from_number, no_results)
            return

        # Validate and filter URLs first
        logger.info(f"Validating {len(reviews)} review URLs...")
        valid_reviews = await self._filter_valid_reviews(reviews)
        logger.info(f"Kept {len(valid_reviews)} reviews with valid URLs")

        if not valid_reviews:
            await whatsapp_client.send_message(
                from_number,
                f"❌ Found {len(reviews)} reviews but all URLs are invalid or broken."
            )
            return

        # Limit to 2 parts maximum (10 reviews per part)
        max_reviews = 20  # Show max 20 reviews total
        display_reviews = valid_reviews[:max_reviews]

        # Calculate batch size to fit in 2 parts
        if len(display_reviews) <= 10:
            # 1 part if 10 or fewer
            batch_size = len(display_reviews)
            total_batches = 1
        else:
            # 2 parts if more than 10
            batch_size = (len(display_reviews) + 1) // 2  # Split evenly
            total_batches = 2

        # Send all batches with header and footer in each message
        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, len(display_reviews))
            batch = display_reviews[start_idx:end_idx]

            # Format batch message with header
            message = format_review_batch(
                batch=batch,
                start_num=start_idx + 1,
                batch_num=batch_num + 1 if total_batches > 1 else None,
                total_batches=total_batches if total_batches > 1 else None,
                doctor_name=doctor_name,
                total_count=len(valid_reviews),
                filtered_count=len(reviews) - len(valid_reviews) if len(reviews) != len(valid_reviews) else 0
            )

            # Send batch
            await whatsapp_client.send_message(from_number, message)

            # Small delay between messages
            import asyncio
            await asyncio.sleep(0.3)

    async def _filter_valid_reviews(self, reviews: list) -> list:
        """
        Filter out reviews with invalid URLs and official hospital content

        Args:
            reviews: List of review dicts

        Returns:
            List of genuine patient reviews with valid URLs
        """
        import httpx

        valid_reviews = []

        # Patterns that indicate official hospital/doctor content (not patient reviews)
        official_patterns = [
            '/videos',  # Hospital videos
            '/posts/',  # Official posts
            '/photos/',  # Photo posts (usually official)
            'medicalcentre/videos',
            'medicalcentre/posts',
            'medicalcentre/photos',
            'MNCC.MALAYSIA',  # Medical organization pages (removed leading /)
            'gleneagles',
            'hospital/',
            'clinic/',
            'medical-centre',
            'aestheticsadvisor.com',  # Doctor directories (not real reviews)
        ]

        # Patterns that indicate genuine patient reviews
        review_patterns = [
            '/groups/',  # Facebook groups (patient discussions)
            '/reviews',  # Review pages
            'forum',  # Forum discussions
            'cari.com.my',
            'lowyat.net',
            'google.com/maps',  # Google Maps reviews
            'maps.google.com'
        ]

        async with httpx.AsyncClient(timeout=5.0, follow_redirects=True) as client:
            for review in reviews:
                url = review.get("url", "")
                snippet = review.get("snippet", "").lower()

                if not url or len(url) < 10:
                    continue

                # Filter out official hospital content
                url_lower = url.lower()
                is_official = any(pattern in url_lower for pattern in official_patterns)
                is_review = any(pattern in url_lower for pattern in review_patterns)

                if is_official and not is_review:
                    logger.debug(f"Filtered official content: {url[:60]}...")
                    continue

                # Additional content-based filtering
                # Filter out empty/placeholder content
                if any(phrase in snippet for phrase in [
                    'not yet rated',
                    '0 reviews',
                    'no reviews',
                    'profile photo',
                    'address:',
                    'google ... dr.',  # Google search result snippet
                    'mbbs',  # Just doctor credentials
                ]):
                    logger.debug(f"Filtered empty/non-review content: {snippet[:50]}...")
                    continue

                # Skip if snippet sounds like official announcement
                if any(word in snippet for word in ['consultant', 'obstetrician & gynaecologist', 'services']):
                    # But keep if it also has review keywords
                    if not any(word in snippet for word in ['she did', 'he did', 'experience', 'visited', 'recommend', 'delivered']):
                        logger.debug(f"Filtered promotional content: {snippet[:50]}...")
                        continue

                try:
                    # Use GET to check actual page content (not just HEAD)
                    # Some sites return 200 for HEAD but page is actually 404
                    response = await client.get(url, timeout=3.0)

                    # Check status code
                    if not (200 <= response.status_code < 400):
                        logger.debug(f"Invalid URL (status {response.status_code}): {url[:60]}...")
                        continue

                    # Check if page content indicates 404/error
                    content_text = response.text.lower()
                    if any(error in content_text for error in [
                        'page not found',
                        '404',
                        'content not found',
                        'this page isn\'t available',
                        'sorry, this page isn\'t available'
                    ]):
                        logger.debug(f"Page not found (200 but 404 content): {url[:60]}...")
                        continue

                    valid_reviews.append(review)

                except Exception as e:
                    logger.debug(f"Broken URL: {url[:60]}... - {str(e)[:50]}")
                    continue

        return valid_reviews

    async def _search_doctor_reviews(self, doctor_name: str) -> list:
        """
        Search for doctor reviews using Google Custom Search

        Args:
            doctor_name: Doctor's name

        Returns:
            List of review dicts
        """
        from src.search.aggregator import search_aggregator

        logger.info(f"🔍 Searching for reviews: {doctor_name}")

        # Use search aggregator (no specialty needed)
        result = await search_aggregator.search_doctor_reviews(
            doctor_name=doctor_name
        )

        return result.get("reviews", [])


# Global message handler instance
message_handler = MessageHandler()
