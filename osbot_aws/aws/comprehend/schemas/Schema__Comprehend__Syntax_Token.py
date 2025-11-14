from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                            import Safe_UInt
from osbot_aws.aws.comprehend.schemas.Schema__Comprehend__Part_Of_Speech        import Schema__Comprehend__Part_Of_Speech
from osbot_aws.aws.comprehend.schemas.safe_str.Safe_Str__AWS_Comprehend__Text   import Safe_Str__Comprehend__Text


class Schema__Comprehend__Syntax_Token(Type_Safe):
    text          : Safe_Str__Comprehend__Text
    token_id      : Safe_UInt
    begin_offset  : Safe_UInt
    end_offset    : Safe_UInt
    part_of_speech: Schema__Comprehend__Part_Of_Speech