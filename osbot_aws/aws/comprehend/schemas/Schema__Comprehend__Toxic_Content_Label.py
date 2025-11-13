from osbot_utils.type_safe.Type_Safe                                                             import Type_Safe
from osbot_aws.aws.comprehend.schemas.enums.Enum__Comprehend__Toxic_Content_Label                import Enum__Comprehend__Toxic_Content_Label
from osbot_utils.type_safe.primitives.domains.numerical.safe_float.Safe_Float__Probability_Score import Safe_Float__Probability_Score


class Schema__Comprehend__Toxic_Content_Label(Type_Safe):
    name  : Enum__Comprehend__Toxic_Content_Label
    score : Safe_Float__Probability_Score