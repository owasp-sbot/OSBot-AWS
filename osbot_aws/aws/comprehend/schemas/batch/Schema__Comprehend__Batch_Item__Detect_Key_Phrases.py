from typing                                                          import List
from osbot_utils.type_safe.Type_Safe                                 import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Int                  import Safe_Int
from osbot_aws.aws.comprehend.schemas.Schema__Comprehend__Key_Phrase import Schema__Comprehend__Key_Phrase


class Schema__Comprehend__Batch_Item__Detect_Key_Phrases(Type_Safe):        # Result for a single document in BatchDetectKeyPhrases operation"""
    index       : Safe_Int                                                  # Position in the input TextList (0-based)
    key_phrases : List[Schema__Comprehend__Key_Phrase]                      # Key phrases extracted from the document
