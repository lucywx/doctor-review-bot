"""
User session management for multi-step input flow
Tracks pending doctor searches waiting for specialty selection
"""

import logging
from typing import Optional, Dict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class UserSessionManager:
    """Manages user sessions for multi-step input"""

    def __init__(self):
        # In-memory session store (phone_number -> session_data)
        # For production, consider using Redis
        self._sessions: Dict[str, dict] = {}
        self._session_timeout = timedelta(minutes=5)  # Sessions expire after 5 min

    def create_pending_search(self, phone_number: str, doctor_name: str):
        """
        Create a pending search session waiting for specialty selection

        Args:
            phone_number: User's phone number
            doctor_name: Doctor name entered by user
        """
        self._sessions[phone_number] = {
            "doctor_name": doctor_name,
            "created_at": datetime.now(),
            "state": "waiting_for_specialty",
            "menu_expanded": False  # Track if user has expanded the full menu
        }
        logger.info(f"📝 Created pending search session for {phone_number}: {doctor_name}")

    def expand_menu(self, phone_number: str) -> bool:
        """
        Mark the menu as expanded for this session

        Args:
            phone_number: User's phone number

        Returns:
            True if session exists and was expanded, False otherwise
        """
        session = self._sessions.get(phone_number)
        if session:
            session["menu_expanded"] = True
            logger.info(f"📋 Expanded specialty menu for {phone_number}")
            return True
        return False

    def is_menu_expanded(self, phone_number: str) -> bool:
        """
        Check if menu is expanded for this session

        Args:
            phone_number: User's phone number

        Returns:
            True if menu is expanded
        """
        session = self._sessions.get(phone_number)
        return session.get("menu_expanded", False) if session else False

    def get_pending_search(self, phone_number: str) -> Optional[dict]:
        """
        Get pending search session for user

        Args:
            phone_number: User's phone number

        Returns:
            Session data or None if not found/expired
        """
        session = self._sessions.get(phone_number)

        if not session:
            return None

        # Check if expired
        elapsed = datetime.now() - session["created_at"]
        if elapsed > self._session_timeout:
            logger.info(f"⏰ Session expired for {phone_number}")
            del self._sessions[phone_number]
            return None

        return session

    def complete_search(self, phone_number: str) -> Optional[str]:
        """
        Complete the search and return doctor name

        Args:
            phone_number: User's phone number

        Returns:
            Doctor name or None if no pending search
        """
        session = self._sessions.pop(phone_number, None)
        if session:
            logger.info(f"✅ Completed search session for {phone_number}")
            return session.get("doctor_name")
        return None

    def cancel_search(self, phone_number: str):
        """
        Cancel pending search session

        Args:
            phone_number: User's phone number
        """
        if phone_number in self._sessions:
            del self._sessions[phone_number]
            logger.info(f"❌ Cancelled search session for {phone_number}")

    def has_pending_search(self, phone_number: str) -> bool:
        """
        Check if user has a pending search

        Args:
            phone_number: User's phone number

        Returns:
            True if pending search exists and not expired
        """
        return self.get_pending_search(phone_number) is not None


# Global instance
user_session_manager = UserSessionManager()
