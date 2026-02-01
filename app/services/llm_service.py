"""
LLM service for generating focused summaries using Groq API.
Uses Qwen model to extract relevant information from fatwa answers.
"""

from groq import Groq
from loguru import logger
from typing import Optional

from app.config import settings


class LLMService:
    """Service for LLM-powered summarization using Groq API."""

    def __init__(self):
        """Initialize Groq client."""
        try:
            self.client = Groq(api_key=settings.groq_api_key)
            self.model = "llama-3.1-70b-versatile"  # Good for Arabic
            logger.info("Groq LLM client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {e}")
            self.client = None

    def generate_focused_summary(
        self,
        user_question: str,
        fatwa_answer: str
    ) -> Optional[str]:
        """
        Generate a focused summary that directly answers the user's question.

        Args:
            user_question: The user's original question
            fatwa_answer: The complete fatwa answer text

        Returns:
            Focused summary text, or None if generation fails
        """
        if not self.client:
            logger.warning("Groq client not initialized, skipping summary generation")
            return None

        try:
            # Build the prompt
            prompt = self._build_extraction_prompt(user_question, fatwa_answer)

            # Call Groq API
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "أنت مساعد متخصص في استخلاص المعلومات من الفتاوى الشرعية بدقة وأمانة."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Low temperature for accuracy
                max_tokens=2048,
                top_p=0.9,
                stream=False
            )

            summary = completion.choices[0].message.content
            logger.info("Successfully generated focused summary")
            return summary

        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return None

    def _build_extraction_prompt(self, user_question: str, fatwa_answer: str) -> str:
        """
        Build the extraction prompt for the LLM.

        Args:
            user_question: The user's question
            fatwa_answer: The complete fatwa answer

        Returns:
            Formatted prompt string
        """
        prompt = f"""أنت مساعد متخصص في تلخيص الفتاوى الشرعية.

المهمة:
استخلص من الفتوى الكاملة الأجزاء التي تجيب مباشرة على سؤال المستخدم.

القواعد المهمة:
1. استخدم النص الأصلي فقط - لا تضيف معلومات من عندك
2. ركز على الأجزاء المتعلقة بسؤال المستخدم
3. احتفظ بأسلوب الشيخ ولغته الأصلية
4. إذا كان الجواب يحتوي على أدلة أو آيات، اذكرها
5. رتب المعلومات بوضوح: الحكم أولاً، ثم التفاصيل
6. لا تكتب عناوين أو مقدمات، ابدأ مباشرة بالإجابة

سؤال المستخدم:
{user_question}

الفتوى الكاملة:
{fatwa_answer}

اكتب الآن الخلاصة المركزة التي تجيب على سؤال المستخدم مباشرة:"""

        return prompt


# Global instance
llm_service = LLMService()
