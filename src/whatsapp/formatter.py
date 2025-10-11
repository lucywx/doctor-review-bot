"""
Message formatting utilities for WhatsApp
"""


def format_review_response(doctor_name: str, reviews: list) -> str:
    """
    Format doctor review results for WhatsApp

    Args:
        doctor_name: Doctor's name
        reviews: List of review dicts with keys: snippet, source, url, author_name, review_date

    Returns:
        Formatted message string
    """
    if not reviews:
        return f"❌ Sorry, no reviews found for *{doctor_name}*.\n\nPlease try:\n• Enter full name\n• Add hospital name\n• Check spelling"

    # Sort reviews by date (newest first)
    def parse_date(review):
        """Extract date for sorting"""
        date_str = review.get("review_date", "")
        if not date_str:
            return "1900-01-01"  # Put undated reviews at end
        return date_str

    sorted_reviews = sorted(reviews, key=parse_date, reverse=True)

    # Build header
    message = f"🔍 *{doctor_name}* Review Summary\n\n"

    # Show reviews (limit to 8)
    display_reviews = sorted_reviews[:8]

    for i, review in enumerate(display_reviews, 1):
        # Limit to ~2 lines on mobile (approx 75 chars)
        snippet = review.get("snippet", "")[:75]
        author = review.get("author_name", "")
        date = review.get("review_date", "")
        url = review.get("url", "")
        rating = review.get("rating")

        # Format review content with quotes
        message += f'{i}. "{snippet}..."\n'

        # Compact metadata line with emojis and pipe separator
        metadata_parts = []
        if author and author != "Anonymous":
            metadata_parts.append(f"👤 {author}")
        if date:
            metadata_parts.append(f"📅 {date}")
        if rating and rating > 0:
            metadata_parts.append(f"⭐ {rating}")

        if metadata_parts:
            message += f"    {' | '.join(metadata_parts)}\n"

        # Add URL with emoji - disable WhatsApp link preview
        if url and len(url) > 10:
            # Remove http(s):// prefix to prevent link preview
            clean_url = url.replace("https://", "").replace("http://", "")
            message += f"    🔗 {clean_url}\n"

        # Empty line between reviews
        message += "\n"

    # Show count if more reviews available
    if len(reviews) > 8:
        message += f"_... and {len(reviews) - 8} more reviews_\n\n"

    # Footer
    message += "━━━━━━━━━━━━━━━\n"
    message += "_Data sourced from public networks, for reference only_\n"
    message += "_For more information, please contact the hospital directly_"

    return message


def format_welcome_message() -> str:
    """Welcome message for new users"""
    return """👋 Welcome to Doctor Review Bot!

*How to use:*
Send doctor's name + specialty for better results

*Format:*
`Dr. [Name], [Specialty]`

*Examples:*
• Dr. Smith, Cardiology
• Dr. Johnson | Pediatrics
• Dr. Williams - Dermatology
• Dr. Lee Oncology

*Common Specialties:*
Cardiology, Dermatology, Endocrinology, Gastroenterology, Gynecology, Hematology, Neurology, Obstetrics, Oncology, Ophthalmology, Orthopedics, Pediatrics, Psychiatry, Surgery, Urology

*Features:*
✅ Aggregates from Google Maps, Facebook and more
✅ More accurate results with specialty
✅ Shows review sources

💡 *Tip:* Adding specialty improves search accuracy and reduces search time!"""


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
    return "🔍 Searching... it takes 15-30 seconds"


def format_specialty_selection(doctor_name: str) -> str:
    """
    Format specialty selection menu

    Args:
        doctor_name: Doctor's name

    Returns:
        Formatted specialty selection message
    """
    return f"""📋 *Select Specialty for {doctor_name}*

Please reply with the specialty number or name:

*Common Specialties:*
1️⃣ Cardiology (Heart)
2️⃣ Dermatology (Skin)
3️⃣ Pediatrics (Children)
4️⃣ Orthopedics (Bones)
5️⃣ Gynecology (Women)
6️⃣ Oncology (Cancer)
7️⃣ Psychiatry (Mental Health)
8️⃣ Neurology (Brain)
9️⃣ Gastroenterology (Digestive)
🔟 Surgery

*More Specialties:*
• Endocrinology • Hematology
• Obstetrics • Ophthalmology
• Radiology • Urology
• Anesthesiology • Pathology

💡 *Tips:*
• Reply with number (e.g., `1`) or name (e.g., `Cardiology`)
• Or reply `0` to skip specialty

⏰ Session expires in 5 minutes"""
