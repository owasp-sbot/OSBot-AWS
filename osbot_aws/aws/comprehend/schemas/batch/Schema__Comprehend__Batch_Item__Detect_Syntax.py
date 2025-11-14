from typing                                                            import List
from osbot_utils.type_safe.Type_Safe                                   import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Int                    import Safe_Int
from osbot_aws.aws.comprehend.schemas.Schema__Comprehend__Syntax_Token import Schema__Comprehend__Syntax_Token


class Schema__Comprehend__Batch_Item__Detect_Syntax(Type_Safe):             # Result for a single document in BatchDetectSyntax operation"""
    index         : Safe_Int                                                # Position in the input TextList (0-based)
    syntax_tokens : List[Schema__Comprehend__Syntax_Token]                  # Syntax tokens with part-of-speech tags
