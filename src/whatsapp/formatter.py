"""
Message formatting utilities for WhatsApp
"""


def format_no_results(doctor_name: str, remaining: int = None, quota: int = None) -> str:
    """
    Format 'no results' message with quota display

    Args:
        doctor_name: Doctor's name
        remaining: Remaining searches this month (optional)
        quota: Monthly quota limit (optional)

    Returns:
        Formatted message string
    """
    message = ""

    # Show quota at the top
    if remaining is not None and quota is not None:
        message += f"📊 Monthly quota: {remaining}/{quota} searches remaining\n\n"

    message += f"""❌ No reviews found for *{doctor_name}*

This doctor may have limited online presence. This can happen when:
• Doctor is relatively new or practices in smaller clinics
• Patients haven't posted online reviews yet
• Information is only available offline

_We search: Google Maps, Facebook, forums, and Malaysian healthcare sites_"""

    return message


def format_review_batch(batch: list, start_num: int, batch_num: int = None, total_batches: int = None,
                        doctor_name: str = "", total_count: int = 0, filtered_count: int = 0,
                        remaining: int = None, quota: int = None) -> str:
    """
    Format a batch of reviews for WhatsApp with header and footer

    Args:
        batch: List of review dicts
        start_num: Starting number for this batch
        batch_num: Current batch number (optional, None for single batch)
        total_batches: Total number of batches (optional, None for single batch)
        doctor_name: Doctor's name for header
        total_count: Total number of valid reviews
        filtered_count: Number of filtered/invalid reviews
        remaining: Remaining searches this month (optional)
        quota: Monthly quota limit (optional)

    Returns:
        Formatted message string
    """
    # Header with quota progress (only on first part or if single message)
    if batch_num == 1 or batch_num is None:
        message = ""
        # Show quota at the top
        if remaining is not None and quota is not None:
            message += f"📊 Monthly quota: {remaining}/{quota} searches remaining\n\n"

        message += f"🔍 *{doctor_name}*\n"
        message += f"Found {total_count} reviews"
        if filtered_count > 0:
            message += f" ({filtered_count} removed)"
        message += "\n\n"
    else:
        message = ""

    # Part indicator (only if multiple parts)
    if batch_num and total_batches and total_batches > 1:
        message += f"📋 *Part {batch_num}/{total_batches}*\n\n"

    # Reviews
    for i, review in enumerate(batch, start=start_num):
        snippet = review.get("snippet", "")
        url = review.get("url", "")
        review_date = review.get("review_date", "")

        # Truncate snippet to ~80 chars (2 lines on mobile, ~40 chars per line)
        max_length = 80
        if len(snippet) > max_length:
            truncated_snippet = snippet[:max_length].rstrip()
            last_space = truncated_snippet.rfind(' ')
            if last_space > max_length - 20:
                truncated_snippet = truncated_snippet[:last_space]
            snippet_display = f"{truncated_snippet}..."
        else:
            snippet_display = snippet

        # Format review entry
        message += f'{i}. "{snippet_display}"\n'

        # Add date and URL (no extra spacing)
        if review_date:
            message += f"   📅 {review_date}\n"

        if url and len(url) > 10:
            # Always include full URL for WhatsApp to parse correctly
            # WhatsApp will auto-convert it to a clickable link
            message += f"   🔗 {url}\n"

        # No blank line between reviews to save space

    # Footer (on last part or if single message)
    if batch_num == total_batches or batch_num is None:
        message += "_Sources: Google, Facebook, forums_"

    return message.rstrip()


def format_welcome_message(remaining: int = None, quota: int = 50) -> str:
    """
    Welcome message for new users

    Args:
        remaining: Remaining searches this month (optional)
        quota: Monthly quota limit
    """
    message = """🧑‍⚕️ Meet Your New Doctor Review Assistant!

*How to use:*
1. Search any doctor by name. For example, "Dr. Sarah Johnson". We will try to find patients' reviews about this doctor. 
2. You get maximum 50 searches monthly. 
3. At the moment, our search results only include doctors in Malaysia.
4. Please be aware that not every doctor has reviews.

📢*Important!!*
We gather reviews from Google, Facebook, forums (not our views!). We're not connected to any hospitals. Always talk to real doctors for medical advice!

Wanna understand better about any doctor? Let's go!"""

    return message


def format_error_message(error_type: str = "general") -> str:
    """Format error messages"""
    messages = {
        "general": "❌ Sorry, an error occurred while processing your request. Please try again later.",
        "quota_exceeded": "⚠️ You've reached your daily query limit.\nDaily limit: 10 queries\nTry again tomorrow!",
        "invalid_input": "❌ Unable to recognize your input.\nPlease send a doctor's name, e.g.: Dr. Smith",
        "no_results": "❌ No reviews found.\nSuggestions:\n• Check spelling\n• Add hospital or location\n• Use full name",
        "rate_limit": "⏳ Request too fast, please try again later."
    }

    return messages.get(error_type, messages["general"])


def format_processing_message() -> str:
    """Message shown while processing"""
    return "🔍 Searching... it takes 15-30 seconds"
