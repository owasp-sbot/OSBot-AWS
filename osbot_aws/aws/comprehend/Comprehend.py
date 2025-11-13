from osbot_utils.helpers.duration.decorators.capture_duration                 import capture_duration
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                import type_safe
from osbot_aws.apis.Session                                                   import Session
from osbot_aws.aws.comprehend.schemas.Schema__Comprehend__Detect_Sentiment    import Schema__Comprehend__Detect_Sentiment
from osbot_aws.aws.comprehend.schemas.enums.Enum__Comprehend__Language_Code   import Enum__Comprehend__Language_Code
from osbot_aws.aws.comprehend.schemas.safe_str.Safe_Str__AWS_Comprehend__Text import Safe_Str__Comprehend__Text
from osbot_aws.aws.session.Session__Kwargs                                    import Session__Kwargs
from osbot_utils.decorators.methods.cache_on_self                             import cache_on_self
from osbot_utils.type_safe.Type_Safe                                          import Type_Safe


class Comprehend(Type_Safe):
    session_kwargs      : Session__Kwargs

    @cache_on_self
    def client(self):
        return self.session().client(service_name = 'comprehend'                     ,
                                     region_name  = self.session_kwargs.region_name  ,
                                     endpoint_url =  self.session_kwargs.endpoint_url)


    def session(self):
        return Session()

    @type_safe
    def detect_sentiment(self, text           : Safe_Str__Comprehend__Text                                              ,
                               language_code : Enum__Comprehend__Language_Code = Enum__Comprehend__Language_Code.ENGLISH,
                          ) -> Schema__Comprehend__Detect_Sentiment:
        with capture_duration() as duration:
            result = self.client().detect_sentiment(Text         = text         ,
                                                    LanguageCode = language_code)
        sentiment       = result.get('Sentiment')
        sentiment_score = result.get('SentimentScore')

        detect_sentiment = Schema__Comprehend__Detect_Sentiment(duration  = duration.seconds,
                                                                sentiment = sentiment      ,
                                                                score     = dict(mixed    = sentiment_score.get('Mixed'   ),
                                                                                 neutral  = sentiment_score.get('Neutral' ),
                                                                                 negative = sentiment_score.get('Negative'),
                                                                                 positive = sentiment_score.get('Positive')))
        return detect_sentiment