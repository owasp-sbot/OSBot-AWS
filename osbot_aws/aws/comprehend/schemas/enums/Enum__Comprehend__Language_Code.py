from enum                                                import Enum


class Enum__Comprehend__Language_Code(str, Enum):
    """
    AWS Comprehend supported language codes (RFC 5646 format).

    IMPORTANT: AWS Comprehend has TWO different language lists:
    1. Languages that can be DETECTED (100+) - via detect_dominant_language
    2. Languages that can be ANALYZED (70+) - for sentiment, entities, etc.

    This enum covers languages supported for ANALYSIS operations.

    For detect_dominant_language results, use Safe_Str__RFC5646__Language_Code
    which accepts ANY valid RFC 5646 code that AWS might return.

    Amazon Comprehend supports analysis in the following languages:
    - Uses ISO 639-1 2-letter codes when available
    - Falls back to ISO 639-2 3-letter codes when needed
    """

    # Most commonly used languages (supported for all operations)
    ENGLISH            = "en"       # English
    SPANISH            = "es"       # Spanish
    FRENCH             = "fr"       # French
    GERMAN             = "de"       # German (Deutsch)
    ITALIAN            = "it"       # Italian
    PORTUGUESE         = "pt"       # Portuguese

    # Asian languages
    JAPANESE           = "ja"       # Japanese
    KOREAN             = "ko"       # Korean
    CHINESE_SIMPLIFIED = "zh"       # Chinese (Simplified)
    CHINESE_TRADITIONAL= "zh-TW"    # Chinese (Traditional)
    HINDI              = "hi"       # Hindi

    # Middle Eastern languages
    ARABIC             = "ar"       # Arabic

    # Additional supported languages (varies by API operation)
    AFRIKAANS          = "af"       # Afrikaans
    ALBANIAN           = "sq"       # Albanian
    AMHARIC            = "am"       # Amharic
    ARMENIAN           = "hy"       # Armenian
    AZERBAIJANI        = "az"       # Azerbaijani
    BENGALI            = "bn"       # Bengali
    BOSNIAN            = "bs"       # Bosnian
    BULGARIAN          = "bg"       # Bulgarian
    CATALAN            = "ca"       # Catalan
    CROATIAN           = "hr"       # Croatian
    CZECH              = "cs"       # Czech
    DANISH             = "da"       # Danish
    DARI               = "fa-AF"    # Dari
    DUTCH              = "nl"       # Dutch
    ESTONIAN           = "et"       # Estonian
    FARSI              = "fa"       # Farsi (Persian)
    FILIPINO           = "tl"       # Filipino/Tagalog
    FINNISH            = "fi"       # Finnish
    GEORGIAN           = "ka"       # Georgian
    GREEK              = "el"       # Greek
    GUJARATI           = "gu"       # Gujarati
    HAUSA              = "ha"       # Hausa
    HEBREW             = "he"       # Hebrew
    HUNGARIAN          = "hu"       # Hungarian
    INDONESIAN         = "id"       # Indonesian
    IRISH              = "ga"       # Irish
    KANNADA            = "kn"       # Kannada
    KAZAKH             = "kk"       # Kazakh
    LATVIAN            = "lv"       # Latvian
    LITHUANIAN         = "lt"       # Lithuanian
    MACEDONIAN         = "mk"       # Macedonian
    MALAY              = "ms"       # Malay
    MALAYALAM          = "ml"       # Malayalam
    MALTESE            = "mt"       # Maltese
    MARATHI            = "mr"       # Marathi
    MONGOLIAN          = "mn"       # Mongolian
    NEPALI             = "ne"       # Nepali
    NORWEGIAN          = "no"       # Norwegian
    PASHTO             = "ps"       # Pashto
    POLISH             = "pl"       # Polish
    PUNJABI            = "pa"       # Punjabi
    ROMANIAN           = "ro"       # Romanian
    RUSSIAN            = "ru"       # Russian
    SERBIAN            = "sr"       # Serbian
    SINHALA            = "si"       # Sinhala
    SLOVAK             = "sk"       # Slovak
    SLOVENIAN          = "sl"       # Slovenian
    SOMALI             = "so"       # Somali
    SWAHILI            = "sw"       # Swahili
    SWEDISH            = "sv"       # Swedish
    TAMIL              = "ta"       # Tamil
    TELUGU             = "te"       # Telugu
    THAI               = "th"       # Thai
    TURKISH            = "tr"       # Turkish
    UKRAINIAN          = "uk"       # Ukrainian
    URDU               = "ur"       # Urdu
    UZBEK              = "uz"       # Uzbek
    VIETNAMESE         = "vi"       # Vietnamese
    WELSH              = "cy"       # Welsh

    # Special marker for unsupported languages detected by AWS
    UNSUPPORTED        = "unsupported"  # AWS detected a language not in this enum