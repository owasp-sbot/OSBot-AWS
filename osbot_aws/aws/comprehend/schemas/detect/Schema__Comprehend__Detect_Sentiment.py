from osbot_utils.type_safe.primitives.core.Safe_Float                                       import Safe_Float
from osbot_utils.type_safe.Type_Safe                                                        import Type_Safe
from osbot_aws.aws.comprehend.schemas.detect.Schema__Comprehend__Detect_Sentiment__Score    import Schema__Comprehend__Detect_Sentiment__Score
from osbot_aws.aws.comprehend.schemas.enums.Enum__Comprehend__Detect_Sentiment__Sentiment   import Enum__Comprehend__Detect_Sentiment__Sentiment


class Schema__Comprehend__Detect_Sentiment(Type_Safe):
    sentiment : Enum__Comprehend__Detect_Sentiment__Sentiment
    score     : Schema__Comprehend__Detect_Sentiment__Score
    duration  : Safe_Float