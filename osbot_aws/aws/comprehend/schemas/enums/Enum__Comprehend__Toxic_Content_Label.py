from enum import Enum


class Enum__Comprehend__Toxic_Content_Label(str, Enum):
    """
    AWS Comprehend toxicity detection label types.

    These labels identify different categories of toxic or harmful content
    that may violate community guidelines or terms of service.
    """
    PROFANITY           = "PROFANITY"              # Swear words, curses, obscene language
    HATE_SPEECH         = "HATE_SPEECH"            # Attacks on protected groups (race, religion, etc.)
    INSULT              = "INSULT"                 # Personal attacks, name-calling
    GRAPHIC             = "GRAPHIC"                # Violent, gory, or disturbing content
    HARASSMENT_OR_ABUSE = "HARASSMENT_OR_ABUSE"    # Bullying, threats, intimidation
    SEXUAL              = "SEXUAL"                 # Sexual content or innuendo
    VIOLENCE_OR_THREAT  = "VIOLENCE_OR_THREAT"     # Threats of violence or harm