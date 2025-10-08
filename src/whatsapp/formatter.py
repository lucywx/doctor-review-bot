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
        return f"❌ 抱歉，未找到关于 *{doctor_name}* 的评价信息。\n\n请尝试：\n• 输入完整姓名\n• 添加医院名称\n• 检查拼写"

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
        "hospital_website": "医院官网",
        "other": "其他来源"
    }

    message = f"🔍 *{doctor_name}* 的评价汇总\n"
    message += f"━━━━━━━━━━━━━━━\n"
    message += f"📊 共找到 *{len(reviews)}* 条评价\n\n"

    # Positive reviews
    if positive:
        message += "✅ *正面评价* ({}):\n\n".format(len(positive))
        for i, review in enumerate(positive[:5], 1):  # Show top 5
            emoji = source_emoji.get(review.get("source", ""), "📄")
            source_name = source_names.get(review.get("source", ""), "其他来源")
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
        message += "❌ *负面评价* ({}):\n\n".format(len(negative))
        for i, review in enumerate(negative[:5], 1):  # Show top 5
            emoji = source_emoji.get(review.get("source", ""), "📄")
            source_name = source_names.get(review.get("source", ""), "其他来源")
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
        message += "ℹ️ *中性评价* ({}):\n\n".format(len(neutral))
        for i, review in enumerate(neutral[:3], 1):
            emoji = source_emoji.get(review.get("source", ""), "📄")
            source_name = source_names.get(review.get("source", ""), "其他来源")
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
    message += "_数据来源于公开网络，仅供参考_\n"
    message += "_如需更多信息，请直接联系医院_"

    return message


def format_welcome_message() -> str:
    """Welcome message for new users"""
    return """👋 欢迎使用医生评价查询机器人！

*使用方法：*
直接发送医生姓名即可查询评价

*示例：*
• 张医生
• 李医生 北京协和
• 王医生 心内科

*功能特点：*
✅ 聚合 Google Maps、Facebook 等多个平台
✅ 自动分类正面/负面评价
✅ 标注评价来源

请输入医生姓名开始查询 🔍"""


def format_error_message(error_type: str = "general") -> str:
    """Format error messages"""
    messages = {
        "general": "❌ 抱歉，处理您的请求时出现错误。请稍后重试。",
        "quota_exceeded": "⚠️ 您今日的查询次数已用完。\n每日限额：50次\n明天再来吧！",
        "invalid_input": "❌ 无法识别您的输入。\n请发送医生姓名，例如：张医生",
        "no_results": "❌ 未找到相关评价。\n建议：\n• 检查拼写\n• 添加医院或地区\n• 使用完整姓名",
        "rate_limit": "⏳ 请求过快，请稍后再试。"
    }

    return messages.get(error_type, messages["general"])


def format_processing_message() -> str:
    """Message shown while processing"""
    return "⏳ 正在搜索全网评价，请稍候...\n\n_预计需要 5-10 秒_"
