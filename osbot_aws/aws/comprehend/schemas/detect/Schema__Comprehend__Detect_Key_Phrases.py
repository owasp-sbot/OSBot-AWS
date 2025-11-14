from typing                                                             import List
from osbot_utils.type_safe.Type_Safe                                    import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Float                   import Safe_Float
from osbot_aws.aws.comprehend.schemas.Schema__Comprehend__Key_Phrase    import Schema__Comprehend__Key_Phrase


class Schema__Comprehend__Detect_Key_Phrases(Type_Safe):
    key_phrases  : List[Schema__Comprehend__Key_Phrase]
    duration     : Safe_Float