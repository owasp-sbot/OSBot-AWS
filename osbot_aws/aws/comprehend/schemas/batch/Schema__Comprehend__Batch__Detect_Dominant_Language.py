from typing                                                                                          import List
from osbot_utils.type_safe.Type_Safe                                                                 import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Float                                                import Safe_Float
from osbot_aws.aws.comprehend.schemas.batch.Schema__Comprehend__Batch_Error                          import Schema__Comprehend__Batch_Error
from osbot_aws.aws.comprehend.schemas.batch.Schema__Comprehend__Batch_Item__Detect_Dominant_Language import Schema__Comprehend__Batch_Item__Detect_Dominant_Language

class Schema__Comprehend__Batch__Detect_Dominant_Language(Type_Safe):
    """
    Response from BatchDetectDominantLanguage operation.

    Contains language detection results for successfully processed documents
    and error information for failed documents.

    Note: This is the only batch operation that does NOT require a language_code parameter.
    """
    result_list : List[Schema__Comprehend__Batch_Item__Detect_Dominant_Language] # Successfully processed documents
    error_list  : List[Schema__Comprehend__Batch_Error]                          # Failed documents with error details
    duration    : Safe_Float                                                     # Total operation duration in seconds
