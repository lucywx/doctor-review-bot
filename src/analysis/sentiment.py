"""
Sentiment analysis using OpenAI API
Classifies reviews as positive, negative, or neutral
"""

import json
import logging
from typing import List, Dict
from openai import AsyncOpenAI
from src.config import settings

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """Analyze sentiment of doctor reviews using OpenAI"""

    def __init__(self):
        self.use_mock = (
            settings.environment == "development" and
            settings.openai_api_key == "your_openai_api_key"
        )

        if not self.use_mock:
            self.client = AsyncOpenAI(api_key=settings.openai_api_key)
            self.model = settings.openai_model
        else:
            logger.info("🧪 Using MOCK sentiment analyzer")

    async def analyze_reviews(self, reviews: List[Dict]) -> List[Dict]:
        """
        Analyze sentiment for a list of reviews

        Args:
            reviews: List of review dicts

        Returns:
            Reviews with sentiment field added
        """
        if not reviews:
            return []

        # Use mock analyzer if no API key
        if self.use_mock:
            return await self._mock_analyze(reviews)

        try:
            # Batch analyze for efficiency
            if len(reviews) <= 10:
                return await self._batch_analyze(reviews)
            else:
                # Process in chunks
                analyzed = []
                for i in range(0, len(reviews), 10):
                    chunk = reviews[i:i+10]
                    chunk_analyzed = await self._batch_analyze(chunk)
                    analyzed.extend(chunk_analyzed)
                return analyzed

        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            # Return reviews with default sentiment
            for review in reviews:
                review["sentiment"] = "neutral"
            return reviews

    async def _batch_analyze(self, reviews: List[Dict]) -> List[Dict]:
        """
        Analyze a batch of reviews (up to 10)

        Args:
            reviews: List of review dicts

        Returns:
            Reviews with sentiment added
        """
        try:
            # Build prompt
            reviews_text = ""
            for i, review in enumerate(reviews, 1):
                snippet = review.get("snippet", "")[:200]
                reviews_text += f"{i}. {snippet}\n\n"

            prompt = f"""请分析以下 {len(reviews)} 条医生评价的情感倾向。
对每条评价，判断为：positive（正面）、negative（负面）或 neutral（中性）。

评价内容：
{reviews_text}

请返回 JSON 数组格式：
[
  {{"id": 1, "sentiment": "positive"}},
  {{"id": 2, "sentiment": "negative"}},
  ...
]

注意：
- positive: 表扬、推荐、满意
- negative: 批评、抱怨、不满
- neutral: 中立描述、事实陈述"""

            # Build API call parameters
            api_params = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "你是一个专业的医疗评价分析助手。"},
                    {"role": "user", "content": prompt}
                ],
                "response_format": {"type": "json_object"}
            }

            # GPT-5 uses different parameter names
            if "gpt-5" in self.model.lower():
                api_params["max_completion_tokens"] = 500
            else:
                api_params["temperature"] = 0.3
                api_params["max_tokens"] = 500

            response = await self.client.chat.completions.create(**api_params)

            # Parse response
            result_text = response.choices[0].message.content
            result = json.loads(result_text)

            # Extract sentiment array
            sentiments = result.get("sentiments", result.get("results", []))

            # Apply sentiment to reviews
            for i, review in enumerate(reviews):
                if i < len(sentiments):
                    sentiment_data = sentiments[i]
                    review["sentiment"] = sentiment_data.get("sentiment", "neutral")
                else:
                    review["sentiment"] = "neutral"

            logger.info(f"✅ Analyzed {len(reviews)} reviews")
            return reviews

        except Exception as e:
            logger.error(f"Error in batch analysis: {e}")
            # Fallback: assign neutral
            for review in reviews:
                review["sentiment"] = "neutral"
            return reviews

    async def analyze_single(self, text: str) -> str:
        """
        Analyze sentiment for a single text

        Args:
            text: Review text

        Returns:
            Sentiment: positive, negative, or neutral
        """
        try:
            prompt = f"""分析这条医生评价的情感倾向（positive/negative/neutral）：

"{text}"

只返回一个词：positive、negative 或 neutral"""

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是情感分析专家。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=10
            )

            sentiment = response.choices[0].message.content.strip().lower()

            # Validate
            if sentiment in ["positive", "negative", "neutral"]:
                return sentiment
            return "neutral"

        except Exception as e:
            logger.error(f"Error analyzing single review: {e}")
            return "neutral"

    async def _mock_analyze(self, reviews: List[Dict]) -> List[Dict]:
        """
        Mock sentiment analysis using simple keyword matching

        Args:
            reviews: List of review dicts

        Returns:
            Reviews with sentiment added
        """
        logger.info(f"🧪 [MOCK] Analyzing {len(reviews)} reviews")

        positive_keywords = ["好", "推荐", "专业", "负责", "满意", "不错", "优秀", "精湛"]
        negative_keywords = ["差", "不满", "态度", "等待", "沟通", "失望"]

        for review in reviews:
            snippet = review.get("snippet", "").lower()

            # Count positive and negative keywords
            positive_count = sum(1 for kw in positive_keywords if kw in snippet)
            negative_count = sum(1 for kw in negative_keywords if kw in snippet)

            # Determine sentiment
            if positive_count > negative_count:
                review["sentiment"] = "positive"
            elif negative_count > positive_count:
                review["sentiment"] = "negative"
            else:
                review["sentiment"] = "neutral"

        logger.info("✅ [MOCK] Sentiment analysis complete")
        return reviews


# Global instance
sentiment_analyzer = SentimentAnalyzer()
