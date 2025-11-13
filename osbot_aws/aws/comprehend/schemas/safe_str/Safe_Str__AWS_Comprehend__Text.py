import re

from osbot_utils.type_safe.primitives.core.Safe_Str import Safe_Str


class Safe_Str__Comprehend__Text(Safe_Str):
    """
    Text input for AWS Comprehend APIs with minimal validation.

    AWS Comprehend analyzes natural language text and needs to receive it unmodified.
    This type ONLY enforces the AWS API byte size limit and allows ALL characters:

    - All UTF-8 characters (any language: English, Spanish, Chinese, Arabic, etc.)
    - All punctuation and symbols (!, @, #, $, %, etc.)
    - All whitespace (spaces, tabs, newlines, etc.)
    - Emojis and special Unicode characters
    - HTML tags, code snippets, URLs
    - ANY text that someone might want to analyze

    AWS Comprehend API Limits:
    - DetectSentiment: 5000 bytes max
    - DetectEntities: 5000 bytes max
    - DetectKeyPhrases: 5000 bytes max
    - DetectDominantLanguage: 5000 bytes max
    - DetectSyntax: 5000 bytes max
    - DetectPiiEntities: 5000 bytes max

      """

    regex           = re.compile(r'[\x00\x01-\x08\x0B\x0C\x0E-\x1F\x7F]')   # allow ALL characters except some control ones
    max_length      = 5000                                                  # AWS Comprehend 5KB limit (conservative char estimate)
