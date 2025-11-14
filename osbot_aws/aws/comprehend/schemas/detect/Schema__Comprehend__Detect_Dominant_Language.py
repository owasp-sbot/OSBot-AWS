from typing                                                        import List
from osbot_utils.type_safe.Type_Safe                               import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Float              import Safe_Float
from osbot_aws.aws.comprehend.schemas.Schema__Comprehend__Language import Schema__Comprehend__Language


class Schema__Comprehend__Detect_Dominant_Language(Type_Safe):
    languages     : List[Schema__Comprehend__Language]  # Sorted by confidence
    duration      : Safe_Float
