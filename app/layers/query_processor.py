"""
Layer 1: Query Processor
Cleans and normalizes Arabic text, converts dialect to formal Arabic.
"""

import re
from typing import Dict
import pyarabic.araby as araby
from loguru import logger


class QueryProcessor:
    """Processes and normalizes Arabic queries."""

    # Limited dialect to formal Arabic mapping (15-20 common words)
    DIALECT_MAP: Dict[str, str] = {
        # Question words
        "وش": "ما",
        "ايش": "ما",
        "شنو": "ما",
        "ليش": "لماذا",
        "ليه": "لماذا",
        "وين": "أين",
        "فين": "أين",
        "كيف": "كيف",

        # Relative pronouns
        "اللي": "الذي",
        "الي": "الذي",

        # Verbs (want/need)
        "ابي": "أريد",
        "ابغى": "أريد",
        "ودي": "أريد",
        "بغيت": "أريد",

        # Negation
        "مو": "ليس",
        "مب": "ليس",
        "ما": "لا",

        # Demonstratives
        "هذي": "هذه",
        "ذي": "هذه",
        "كذا": "هكذا",
    }

    def __init__(self):
        """Initialize query processor."""
        logger.info("Query processor initialized")

    def clean_text(self, text: str) -> str:
        """
        Clean Arabic text by removing diacritics and normalizing.

        Args:
            text: Raw Arabic text

        Returns:
            Cleaned text
        """
        if not text:
            return ""

        # Remove tashkeel (diacritics)
        text = araby.strip_tashkeel(text)

        # Remove tatweel (elongation character)
        text = araby.strip_tatweel(text)

        # Normalize hamza variations
        text = re.sub(r'[إأآا]', 'ا', text)

        # Normalize ta marbuta at end of words
        text = re.sub(r'ة\b', 'ه', text)

        # Normalize alef maksura
        text = re.sub(r'ى', 'ي', text)

        # Remove duplicate punctuation
        text = re.sub(r'([?.!,،؛])\1+', r'\1', text)

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)

        # Trim
        text = text.strip()

        return text

    def convert_dialect(self, text: str) -> str:
        """
        Convert common dialect words to formal Arabic.
        Only handles limited, high-frequency words.

        Args:
            text: Arabic text (may contain dialect)

        Returns:
            Text with dialect words converted to formal
        """
        words = text.split()
        converted_words = []

        for word in words:
            # Check if word is in dialect map (case-insensitive)
            formal_word = self.DIALECT_MAP.get(word, word)
            converted_words.append(formal_word)

        return " ".join(converted_words)

    def process(self, query: str) -> str:
        """
        Main processing pipeline: clean -> convert dialect.

        Args:
            query: Raw user query

        Returns:
            Processed query ready for embedding
        """
        logger.debug(f"Original query: {query}")

        # Step 1: Clean text
        cleaned = self.clean_text(query)
        logger.debug(f"After cleaning: {cleaned}")

        # Step 2: Convert dialect
        processed = self.convert_dialect(cleaned)
        logger.debug(f"After dialect conversion: {processed}")

        return processed


# Global instance
query_processor = QueryProcessor()
