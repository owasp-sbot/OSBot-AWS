from enum import Enum


class Enum__Comprehend__Part_Of_Speech_Tag(str, Enum):
    ADJ   = "ADJ"      # Adjective
    ADP   = "ADP"      # Adposition
    ADV   = "ADV"      # Adverb
    AUX   = "AUX"      # Auxiliary
    CCONJ = "CCONJ"    # Coordinating conjunction
    DET   = "DET"      # Determiner
    INTJ  = "INTJ"     # Interjection
    NOUN  = "NOUN"     # Noun
    NUM   = "NUM"      # Numeral
    PART  = "PART"     # Particle
    PRON  = "PRON"     # Pronoun
    PROPN = "PROPN"    # Proper noun
    PUNCT = "PUNCT"    # Punctuation
    SCONJ = "SCONJ"    # Subordinating conjunction
    SYM   = "SYM"      # Symbol
    VERB  = "VERB"     # Verb
    OTHER = "O"        # Other