import re
from osbot_utils.type_safe.primitives.core.Safe_Str import Safe_Str
from osbot_utils.type_safe.primitives.core.enums.Enum__Safe_Str__Regex_Mode import Enum__Safe_Str__Regex_Mode


class Safe_Str__RFC_5646__Language_Code(Safe_Str):
    """
    RFC 5646 Language Code (flexible for AWS Comprehend detect_dominant_language).

    AWS Comprehend's detect_dominant_language can return 100+ language codes
    following RFC 5646 format. This type accepts ANY valid RFC 5646 code.

    Valid formats:
    - 2-letter ISO 639-1: "en", "es", "fr", "lo", "my", etc.
    - 3-letter ISO 639-2: "aar", "abk", etc.
    - With region subtag: "en-US", "zh-TW", "pt-BR"
    - With script: "zh-Hans", "zh-Hant"

    Examples:
    - "en" → English
    - "es" → Spanish
    - "lo" → Lao
    - "my" → Burmese
    - "km" → Khmer
    - "zh-TW" → Traditional Chinese
    - "pt-BR" → Brazilian Portuguese

    Note: This is more permissive than Enum__Comprehend__Language_Code
    which only includes languages supported for analysis operations.
    """

    # RFC 5646 pattern: language code (2-3 letters) optionally followed by subtags
    # Examples: en, en-US, zh-Hans, zh-Hans-CN
    regex             = re.compile(r'^[a-z]{2,3}(-[A-Za-z]{2,8})*$', re.IGNORECASE)
    regex_mode        = Enum__Safe_Str__Regex_Mode.MATCH
    max_length        = 35                                                  # RFC 5646 allows fairly long codes with multiple subtags
    min_length        = 2                                                   # Minimum is 2-letter code like "en"
    strict_validation = True