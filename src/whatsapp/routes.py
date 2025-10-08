"""
WhatsApp webhook routes
"""

from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import PlainTextResponse
import logging

from src.config import settings
from src.whatsapp.models import WhatsAppWebhook
from src.whatsapp.handler import message_handler

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/whatsapp")
async def verify_webhook(request: Request):
    """
    Verify WhatsApp webhook
    Meta will call this endpoint to verify the webhook
    """
    # Get query parameters
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    logger.info(f"Webhook verification request: mode={mode}, token={token}")

    # Verify the token
    if mode == "subscribe" and token == settings.verify_token:
        logger.info("✅ Webhook verified successfully")
        return PlainTextResponse(content=challenge)

    logger.warning("❌ Webhook verification failed")
    raise HTTPException(status_code=403, detail="Verification token mismatch")


@router.post("/whatsapp")
async def receive_webhook(request: Request):
    """
    Receive WhatsApp webhook events
    Handle incoming messages from users (supports both Meta and Twilio formats)
    """
    try:
        # Check content type to determine format
        content_type = request.headers.get("content-type", "")
        
        if "application/x-www-form-urlencoded" in content_type:
            # Twilio format
            form_data = await request.form()
            from_number = form_data.get("From", "").replace("whatsapp:", "")
            message_text = form_data.get("Body", "")
            
            logger.info(f"📬 Received Twilio webhook: From={from_number}, Body={message_text}")
            
            if from_number and message_text:
                # Process message asynchronously
                import asyncio
                asyncio.create_task(
                    message_handler.process_message(from_number, message_text)
                )
            
            return {"status": "received"}
            
        else:
            # Meta format (JSON)
            body = await request.json()
            logger.info(f"📬 Received Meta webhook: {body}")

            # Parse webhook payload
            webhook = WhatsAppWebhook(**body)

            # Process each entry
            for entry in webhook.entry:
                for change in entry.changes:
                    value = change.value

                    # Check if there are messages
                    if value.messages:
                        for message in value.messages:
                            # Only process text messages
                            if message.type == "text" and message.text:
                                from_number = message.from_
                                message_text = message.text.body

                                # Process message asynchronously
                                import asyncio
                                asyncio.create_task(
                                    message_handler.process_message(from_number, message_text)
                                )

            return {"status": "ok"}

    except Exception as e:
        logger.error(f"❌ Error processing webhook: {e}", exc_info=True)
        # Still return 200 to prevent retries
        return {"status": "error", "message": str(e)}


@router.post("/whatsapp/test")
async def test_webhook(request: Request):
    """
    Test endpoint for simulating WhatsApp messages
    For local testing without actual WhatsApp setup
    """
    try:
        body = await request.json()
        from_number = body.get("from", "test_user")
        message = body.get("message", "")

        logger.info(f"🧪 Test message from {from_number}: {message}")

        # Process the test message
        await message_handler.process_message(from_number, message)

        return {
            "status": "ok",
            "message": "Test message processed"
        }

    except Exception as e:
        logger.error(f"❌ Test webhook error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
