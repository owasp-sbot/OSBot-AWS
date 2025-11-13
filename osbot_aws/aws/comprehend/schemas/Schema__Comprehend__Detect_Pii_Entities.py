from typing                                                          import List
from osbot_utils.type_safe.Type_Safe                                 import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Float                import Safe_Float
from osbot_aws.aws.comprehend.schemas.Schema__Comprehend__Pii_Entity import Schema__Comprehend__Pii_Entity


class Schema__Comprehend__Detect_Pii_Entities(Type_Safe):
    entities     : List[Schema__Comprehend__Pii_Entity]
    duration     : Safe_Float