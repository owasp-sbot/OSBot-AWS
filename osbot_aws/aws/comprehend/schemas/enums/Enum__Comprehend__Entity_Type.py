from enum import Enum


class Enum__Comprehend__Entity_Type(str, Enum):
    PERSON          = "PERSON"
    LOCATION        = "LOCATION"
    ORGANIZATION    = "ORGANIZATION"
    COMMERCIAL_ITEM = "COMMERCIAL_ITEM"
    EVENT           = "EVENT"
    DATE            = "DATE"
    QUANTITY        = "QUANTITY"
    TITLE           = "TITLE"
    OTHER           = "OTHER"