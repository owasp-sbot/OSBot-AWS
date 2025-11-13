from osbot_utils.type_safe.Type_Safe                                                              import Type_Safe
from osbot_aws.aws.comprehend.schemas.enums.Enum__Comprehend__Language_Code                       import Enum__Comprehend__Language_Code
from osbot_utils.type_safe.primitives.domains.numerical.safe_float.Safe_Float__Probability_Score  import Safe_Float__Probability_Score


class Schema__Comprehend__Language(Type_Safe):
    language_code : Enum__Comprehend__Language_Code
    score         : Safe_Float__Probability_Score