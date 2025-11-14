from typing                                                                                          import List
from osbot_utils.type_safe.Type_Safe                                                                 import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Float                                                import Safe_Float
from osbot_aws.aws.comprehend.schemas.batch.Schema__Comprehend__Batch_Error                          import Schema__Comprehend__Batch_Error
from osbot_aws.aws.comprehend.schemas.batch.Schema__Comprehend__Batch_Item__Detect_Entities          import Schema__Comprehend__Batch_Item__Detect_Entities

class Schema__Comprehend__Batch__Detect_Entities(Type_Safe):
    """
    Response from BatchDetectEntities operation.

    Contains named entity recognition results for successfully processed documents
    and error information for failed documents.
    """
    result_list : List[Schema__Comprehend__Batch_Item__Detect_Entities]    # Successfully processed documents
    error_list  : List[Schema__Comprehend__Batch_Error]                    # Failed documents with error details
    duration    : Safe_Float                                                # Total operation duration in seconds
