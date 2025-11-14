from osbot_utils.type_safe.Type_Safe                                                      import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                                      import Safe_UInt
from osbot_aws.aws.comprehend.schemas.detect.Schema__Comprehend__Detect_Sentiment__Score  import Schema__Comprehend__Detect_Sentiment__Score
from osbot_aws.aws.comprehend.schemas.enums.Enum__Comprehend__Detect_Sentiment__Sentiment import Enum__Comprehend__Detect_Sentiment__Sentiment


class Schema__Comprehend__Batch_Item__Detect_Sentiment(Type_Safe):         # Result for a single document in BatchDetectSentiment operation
    index     : Safe_UInt                                                  # Position in the input TextList (0-based)
    sentiment : Enum__Comprehend__Detect_Sentiment__Sentiment              # Overall sentiment classification
    score     : Schema__Comprehend__Detect_Sentiment__Score                # Confidence scores for each sentiment