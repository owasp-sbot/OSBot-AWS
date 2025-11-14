from typing                                                             import List
from osbot_utils.type_safe.Type_Safe                                    import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Float                   import Safe_Float
from osbot_aws.aws.comprehend.schemas.Schema__Comprehend__Syntax_Token  import Schema__Comprehend__Syntax_Token


class Schema__Comprehend__Detect_Syntax(Type_Safe):
    syntax_tokens : List[Schema__Comprehend__Syntax_Token]
    duration      : Safe_Float