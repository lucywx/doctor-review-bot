"""
WhatsApp data models
"""

from pydantic import BaseModel, Field
from typing import Optional, List


class WhatsAppTextMessage(BaseModel):
    """WhatsApp text message model"""
    body: str


class WhatsAppMessage(BaseModel):
    """Incoming WhatsApp message"""
    from_: str = Field(..., alias="from")
    id: str
    timestamp: str
    type: str
    text: Optional[WhatsAppTextMessage] = None


class WhatsAppContact(BaseModel):
    """WhatsApp contact info"""
    profile: dict
    wa_id: str


class WhatsAppValue(BaseModel):
    """WhatsApp webhook value"""
    messaging_product: str
    metadata: dict
    contacts: Optional[List[WhatsAppContact]] = None
    messages: Optional[List[WhatsAppMessage]] = None


class WhatsAppChange(BaseModel):
    """WhatsApp webhook change"""
    value: WhatsAppValue
    field: str


class WhatsAppEntry(BaseModel):
    """WhatsApp webhook entry"""
    id: str
    changes: List[WhatsAppChange]


class WhatsAppWebhook(BaseModel):
    """WhatsApp webhook payload"""
    object: str
    entry: List[WhatsAppEntry]


class WhatsAppOutgoingMessage(BaseModel):
    """Outgoing message to send via WhatsApp"""
    messaging_product: str = "whatsapp"
    to: str
    type: str = "text"
    text: dict

    @classmethod
    def create_text_message(cls, to: str, message: str):
        """Create a text message"""
        return cls(
            to=to,
            text={"body": message}
        )
