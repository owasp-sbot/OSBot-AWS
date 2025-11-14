from typing                                                      import List
from osbot_utils.type_safe.Type_Safe                             import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Int              import Safe_Int
from osbot_aws.aws.comprehend.schemas.Schema__Comprehend__Entity import Schema__Comprehend__Entity


class Schema__Comprehend__Batch_Item__Detect_Entities(Type_Safe):           # Result for a single document in BatchDetectEntities operation
    index    : Safe_Int                                                     # Position in the input TextList (0-based)
    entities : List[Schema__Comprehend__Entity]                             # Named entities found in the document
