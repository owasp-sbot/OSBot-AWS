from osbot_utils.type_safe.Type_Safe                                                              import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                                              import Safe_UInt
from osbot_aws.aws.comprehend.schemas.enums.Enum__Comprehend__Entity_Type                         import Enum__Comprehend__Entity_Type
from osbot_utils.type_safe.primitives.domains.numerical.safe_float.Safe_Float__Probability_Score  import Safe_Float__Probability_Score
from osbot_aws.aws.comprehend.schemas.safe_str.Safe_Str__AWS_Comprehend__Text                     import Safe_Str__Comprehend__Text


class Schema__Comprehend__Entity(Type_Safe):
    text         : Safe_Str__Comprehend__Text
    type         : Enum__Comprehend__Entity_Type
    score        : Safe_Float__Probability_Score
    begin_offset : Safe_UInt
    end_offset   : Safe_UInt