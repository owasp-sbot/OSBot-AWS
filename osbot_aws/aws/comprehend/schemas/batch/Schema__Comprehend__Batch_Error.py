from osbot_utils.type_safe.Type_Safe                            import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Int             import Safe_Int
from osbot_utils.type_safe.primitives.core.Safe_Str             import Safe_Str


class Schema__Comprehend__Batch_Error(Type_Safe):
    """
    Error information for a single document in a batch operation.
    
    AWS Comprehend batch operations return errors for documents that failed processing.
    Each error includes the document's index in the input list, an error code, and a message.
    """
    index         : Safe_Int      # Position in the input TextList (0-based)
    error_code    : Safe_Str      # AWS error code (e.g., "InternalServerException", "InvalidRequestException")
    error_message : Safe_Str      # Human-readable error description
