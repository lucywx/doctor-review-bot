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
        return f"""❌ No reviews found for *{doctor_name}*

This doctor may have limited online presence. This can happen when:
• Doctor is relatively new or practices in smaller clinics
• Patients haven't posted online reviews yet
• Information is only available offline

_We search: Google Maps, Facebook, forums, and Malaysian healthcare sites_"""

    # Sort reviews by date (newest first)
    def parse_date(review):
        """Extract date for sorting"""
        date_str = review.get("review_date", "")
        if not date_str:
            return "1900-01-01"  # Put undated reviews at end
        return date_str

    sorted_reviews = sorted(reviews, key=parse_date, reverse=True)

    # Build header
    message = f"🔍 *{doctor_name}*\nFound {len(reviews)} reviews\n\n"

    # WhatsApp limit: 1600 characters
    # Strategy: Show fewer reviews with shorter snippets to stay under limit
    MAX_MESSAGE_LENGTH = 1500  # Leave buffer
    display_reviews = sorted_reviews[:5]  # Reduce from 8 to 5

    for i, review in enumerate(display_reviews, 1):
        snippet = review.get("snippet", "")
        date = review.get("review_date", "")
        url = review.get("url", "")

        # Truncate snippet to 80 chars (about 1 line)
        max_length = 80
        if len(snippet) > max_length:
            truncated_snippet = snippet[:max_length].rstrip()
            # Ensure we don't cut in the middle of a word
            last_space = truncated_snippet.rfind(' ')
            if last_space > max_length - 20:
                truncated_snippet = truncated_snippet[:last_space]
            snippet_display = f"{truncated_snippet}..."
        else:
            snippet_display = snippet

        # Format review entry
        review_entry = f'{i}. "{snippet_display}"\n'

        # Add URL - send full URL so WhatsApp can parse correctly
        if url and len(url) > 10:
            # WhatsApp will auto-convert full URLs to clickable links
            review_entry += f"   🔗 {url}\n"

        review_entry += "\n"

        # Check if adding this review would exceed limit
        if len(message) + len(review_entry) > MAX_MESSAGE_LENGTH:
            break

        message += review_entry

    # Show count summary (no "more reviews" text - avoid false expectations)
    message += f"\n_Showing {i}/{len(reviews)} reviews_\n"
    message += "_Sources: Google, Facebook, forums_"

    return message


def format_review_batch(batch: list, start_num: int, batch_num: int = None, total_batches: int = None,
                        doctor_name: str = "", total_count: int = 0, filtered_count: int = 0) -> str:
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

    Returns:
        Formatted message string
    """
    # Header with doctor name and count (only on first part or if single message)
    if batch_num == 1 or batch_num is None:
        message = f"🔍 *{doctor_name}*\n"
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
        message += "_Sources: Google, Facebook, forums_\n\n"
        message += "⚠️ _Note: Results may not include private Facebook posts or content requiring login. Always verify with official sources._"

    return message.rstrip()


def format_welcome_message() -> str:
    """Welcome message for new users"""
    return """👋 Welcome to Doctor Review Bot!

📝 *How to use:*
Simply send the doctor's full name

*Examples:*
• Dr. Tang Boon Nee
• Dr. Smith
• Dr. Johnson

🔍 We'll search Google Maps, Facebook, forums, and healthcare sites for patient reviews.

⚡ *Daily limit:* 10 searches"""


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
