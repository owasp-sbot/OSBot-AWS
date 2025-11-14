from osbot_utils.type_safe.Type_Safe                                                              import Type_Safe
from osbot_utils.type_safe.primitives.domains.numerical.safe_float.Safe_Float__Probability_Score  import Safe_Float__Probability_Score
from osbot_aws.aws.comprehend.schemas.safe_str.Safe_Str__RFC_5646__Language_Code                  import Safe_Str__RFC_5646__Language_Code


class Schema__Comprehend__Language(Type_Safe):
    language_code : Safe_Str__RFC_5646__Language_Code
    score         : Safe_Float__Probability_Score