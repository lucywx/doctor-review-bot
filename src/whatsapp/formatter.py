"""
Message formatting utilities for WhatsApp
"""


def format_review_response(doctor_name: str, reviews: list) -> str:
    """
    Format doctor review results for WhatsApp

    Args:
        doctor_name: Doctor's name
        reviews: List of review dicts with keys: snippet, sentiment, source, url

    Returns:
        Formatted message string
    """
    if not reviews:
        return f"❌ Sorry, no reviews found for *{doctor_name}*.\n\nPlease try:\n• Enter full name\n• Add hospital name\n• Check spelling"

    # Separate by sentiment
    positive = [r for r in reviews if r.get("sentiment") == "positive"]
    negative = [r for r in reviews if r.get("sentiment") == "negative"]
    neutral = [r for r in reviews if r.get("sentiment") == "neutral"]

    # Source emojis and names
    source_emoji = {
        "google_maps": "🗺️",
        "facebook": "👥",
        "hospital_website": "🏥",
        "other": "📄"
    }

    source_names = {
        "google_maps": "Google Maps",
        "facebook": "Facebook",
        "hospital_website": "Hospital Website",
        "other": "Other Sources"
    }

    message = f"🔍 *{doctor_name}* Review Summary\n"
    message += f"━━━━━━━━━━━━━━━\n"
    message += f"📊 Found *{len(reviews)}* reviews\n\n"

    # Positive reviews
    if positive:
        message += "✅ *Positive Reviews* ({}):\n\n".format(len(positive))
        for i, review in enumerate(positive[:5], 1):  # Show top 5
            emoji = source_emoji.get(review.get("source", ""), "📄")
            source_name = source_names.get(review.get("source", ""), "Other Sources")
            snippet = review.get("snippet", "")[:120]
            rating = review.get("rating")
            rating_str = f" ⭐{rating}" if rating else ""

            message += f"{i}. {snippet}...{rating_str}\n"
            message += f"   {emoji} {source_name}\n"

            # Add source link
            url = review.get("url", "")
            if url and len(url) > 10:
                message += f"   🔗 {url}\n"

            message += "\n"

    # Negative reviews
    if negative:
        message += "❌ *Negative Reviews* ({}):\n\n".format(len(negative))
        for i, review in enumerate(negative[:5], 1):  # Show top 5
            emoji = source_emoji.get(review.get("source", ""), "📄")
            source_name = source_names.get(review.get("source", ""), "Other Sources")
            snippet = review.get("snippet", "")[:120]
            rating = review.get("rating")
            rating_str = f" ⭐{rating}" if rating else ""

            message += f"{i}. {snippet}...{rating_str}\n"
            message += f"   {emoji} {source_name}\n"

            # Add source link
            url = review.get("url", "")
            if url and len(url) > 10:
                message += f"   🔗 {url}\n"

            message += "\n"

    # Neutral reviews
    if neutral and len(positive) + len(negative) < 5:
        message += "ℹ️ *Neutral Reviews* ({}):\n\n".format(len(neutral))
        for i, review in enumerate(neutral[:3], 1):
            emoji = source_emoji.get(review.get("source", ""), "📄")
            source_name = source_names.get(review.get("source", ""), "Other Sources")
            snippet = review.get("snippet", "")[:120]

            message += f"{i}. {snippet}...\n"
            message += f"   {emoji} {source_name}\n"

            # Add source link
            url = review.get("url", "")
            if url and len(url) > 10:
                message += f"   🔗 {url}\n"

            message += "\n"

    # Footer
    message += "━━━━━━━━━━━━━━━\n"
    message += "_Data sourced from public networks, for reference only_\n"
    message += "_For more information, please contact the hospital directly_"

    return message


def format_welcome_message() -> str:
    """Welcome message for new users"""
    return """👋 Welcome to Doctor Review Bot!

*How to use:*
Simply send a doctor's name to search for reviews

*Examples:*
• Dr. Smith
• Dr. Johnson Mayo Clinic
• Dr. Williams Cardiology

*Features:*
✅ Aggregates from Google Maps, Facebook and more
✅ Auto-categorizes positive/negative reviews
✅ Shows review sources

Enter a doctor's name to start searching 🔍"""


def format_error_message(error_type: str = "general") -> str:
    """Format error messages"""
    messages = {
        "general": "❌ Sorry, an error occurred while processing your request. Please try again later.",
        "quota_exceeded": "⚠️ You've reached your daily query limit.\nDaily limit: 50 queries\nTry again tomorrow!",
        "invalid_input": "❌ Unable to recognize your input.\nPlease send a doctor's name, e.g.: Dr. Smith",
        "no_results": "❌ No reviews found.\nSuggestions:\n• Check spelling\n• Add hospital or location\n• Use full name",
        "rate_limit": "⏳ Request too fast, please try again later."
    }

    return messages.get(error_type, messages["general"])


def format_processing_message() -> str:
    """Message shown while processing"""
    return "⏳ Searching for reviews across the web, please wait...\n\n_Estimated time: 5-10 seconds_"
