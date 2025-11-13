from osbot_utils.type_safe.Type_Safe                                                             import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                                             import Safe_UInt
from osbot_aws.aws.comprehend.schemas.enums.Enum__Comprehend__Pii_Entity_Type                    import Enum__Comprehend__Pii_Entity_Type
from osbot_utils.type_safe.primitives.domains.numerical.safe_float.Safe_Float__Probability_Score import Safe_Float__Probability_Score


class Schema__Comprehend__Pii_Entity(Type_Safe):
    type         : Enum__Comprehend__Pii_Entity_Type
    score        : Safe_Float__Probability_Score
    begin_offset : Safe_UInt
    end_offset   : Safe_UInt