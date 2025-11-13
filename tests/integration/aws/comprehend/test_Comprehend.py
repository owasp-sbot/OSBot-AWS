from unittest                                                                             import TestCase
from osbot_utils.testing.__                                                               import __, __SKIP__
from osbot_aws.aws.comprehend.Comprehend                                                  import Comprehend
from osbot_aws.aws.comprehend.Comprehend__with_temp_role                                  import Comprehend__with_temp_role
from osbot_aws.aws.comprehend.schemas.Schema__Comprehend__Detect_Sentiment                import Schema__Comprehend__Detect_Sentiment
from osbot_utils.type_safe.Type_Safe                                                      import Type_Safe
from osbot_utils.utils.Objects                                                            import type_full_name, base_types
from osbot_aws.aws.comprehend.schemas.enums.Enum__Comprehend__Detect_Sentiment__Sentiment import Enum__Comprehend__Detect_Sentiment__Sentiment


class test_Comprehend(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.comprehend = Comprehend__with_temp_role()

    def test__init__(self):
        with self.comprehend as _:
            assert type(_) is Comprehend__with_temp_role
            assert base_types(_) == [Comprehend, Type_Safe, object]

    def test_client(self):
        with self.comprehend as _:
            client = _.client()
            assert type_full_name(client) == 'botocore.client.Comprehend'


    def test_detect_sentiment(self):                                                        # Validate AWS Comprehend sentiment detection
        with self.comprehend as _:
            result = _.detect_sentiment('Hello World')
            assert type(result) is Schema__Comprehend__Detect_Sentiment                    # Returns proper schema type

            assert result.obj() == __(duration  = __SKIP__   ,
                                      sentiment = 'positive' ,                               # it will be interesting to see if these values continue to be deterministic over time
                                      score     = __(mixed    = 0.0010159355588257313 ,
                                                     negative = 0.0                   ,
                                                     neutral  = 0.42408183217048645   ,
                                                     positive = 0.5733687281608582    ))

            assert result.duration < 0.5                                                    # on dev laptop and wifi this is usually between 0.2 and 0.4 seconds

    def test_detect_sentiment__type_conversion(self):                           # Test auto-conversion of raw types
        with self.comprehend as _:
            result = _.detect_sentiment('test text')                            # Raw string
            assert type(result.sentiment) is Enum__Comprehend__Detect_Sentiment__Sentiment

            # Test scores are bounded 0.0 to 1.0
            assert 0.0 <= result.score.positive <= 1.0
            assert 0.0 <= result.score.negative <= 1.0
            assert 0.0 <= result.score.neutral  <= 1.0
            assert 0.0 <= result.score.mixed    <= 1.0