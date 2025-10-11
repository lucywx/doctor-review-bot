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


def format_specialty_selection(doctor_name: str, show_full: bool = True) -> str:
    """
    Format specialty selection menu with all 38 specialties

    Args:
        doctor_name: Doctor's name
        show_full: Kept for backward compatibility (always shows full list)

    Returns:
        Formatted specialty selection message
    """

    # All 38 specialties with skip option
    all_specialties = [
        "0. Skip (No specialty)",
        "1. Cardiology",
        "2. Dermatology",
        "3. Endocrinology & Diabetes",
        "4. Gastroenterology & Hepatology",
        "5. General Surgery",
        "6. Obstetrics & Gynaecology",
        "7. Oncology",
        "8. Ophthalmology",
        "9. Orthopaedic Surgery",
        "10. Paediatrics",
        "11. Anaesthesiology & Critical Care",
        "12. Cardiothoracic Surgery",
        "13. Dentistry",
        "14. Ear, Nose & Throat (ENT)",
        "15. Emergency Medicine",
        "16. Geriatric Medicine",
        "17. Haematology",
        "18. Infectious Diseases",
        "19. Internal Medicine",
        "20. Nephrology",
        "21. Neurology",
        "22. Neurosurgery",
        "23. Nuclear Medicine",
        "24. Pain Medicine",
        "25. Palliative Medicine",
        "26. Pathology",
        "27. Plastic & Reconstructive Surgery",
        "28. Psychiatry",
        "29. Radiology",
        "30. Rehabilitation Medicine",
        "31. Respiratory Medicine",
        "32. Rheumatology",
        "33. Robotic Surgery",
        "34. Spine Surgery",
        "35. Sports Medicine",
        "36. Transplant Medicine",
        "37. Urology",
        "38. Other"
    ]

    specialties_text = "\n".join(all_specialties)
    return f"""📋 *{doctor_name} - Select specialty by number*

{specialties_text}"""
