from typing                                                      import List
from osbot_utils.type_safe.Type_Safe                             import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Float            import Safe_Float
from osbot_aws.aws.comprehend.schemas.Schema__Comprehend__Entity import Schema__Comprehend__Entity


class Schema__Comprehend__Detect_Entities(Type_Safe):
    entities     : List[Schema__Comprehend__Entity]
    duration     : Safe_Float