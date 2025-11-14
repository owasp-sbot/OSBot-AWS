from osbot_utils.type_safe.Type_Safe                                                             import Type_Safe
from osbot_utils.type_safe.primitives.domains.numerical.safe_float.Safe_Float__Probability_Score import Safe_Float__Probability_Score


class Schema__Comprehend__Detect_Sentiment__Score(Type_Safe):
    mixed    : Safe_Float__Probability_Score
    negative : Safe_Float__Probability_Score
    neutral  : Safe_Float__Probability_Score
    positive : Safe_Float__Probability_Score