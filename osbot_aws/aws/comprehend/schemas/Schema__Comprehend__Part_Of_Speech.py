from osbot_utils.type_safe.Type_Safe                                                               import Type_Safe
from osbot_aws.aws.comprehend.schemas.enums.Enum__Comprehend__Part_Of_Speech_Tag                   import Enum__Comprehend__Part_Of_Speech_Tag
from osbot_utils.type_safe.primitives.domains.numerical.safe_float.Safe_Float__Probability_Score   import Safe_Float__Probability_Score

class Schema__Comprehend__Part_Of_Speech(Type_Safe):
    tag   : Enum__Comprehend__Part_Of_Speech_Tag
    score : Safe_Float__Probability_Score