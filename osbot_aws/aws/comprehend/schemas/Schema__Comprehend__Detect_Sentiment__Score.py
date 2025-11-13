from osbot_utils.type_safe.Type_Safe                                               import Type_Safe
from osbot_aws.aws.comprehend.schemas.safe_float.Safe_Float__Comprehend__Sentiment import Safe_Float__Comprehend__Sentiment


class Schema__Comprehend__Detect_Sentiment__Score(Type_Safe):
    mixed    : Safe_Float__Comprehend__Sentiment
    negative : Safe_Float__Comprehend__Sentiment
    neutral  : Safe_Float__Comprehend__Sentiment
    positive : Safe_Float__Comprehend__Sentiment