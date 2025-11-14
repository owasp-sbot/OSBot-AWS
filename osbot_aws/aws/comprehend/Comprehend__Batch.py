from typing                                                                                               import List
from botocore.client                                                                                      import BaseClient
from osbot_utils.helpers.duration.decorators.capture_duration                                             import capture_duration
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                            import type_safe
from osbot_utils.type_safe.Type_Safe                                                                      import Type_Safe
from osbot_aws.aws.comprehend.Comprehend__Response_Utils                                                  import Comprehend__Response_Utils
from osbot_aws.aws.comprehend.schemas.batch.Schema__Comprehend__Batch__Detect_Sentiment                   import Schema__Comprehend__Batch__Detect_Sentiment
from osbot_aws.aws.comprehend.schemas.batch.Schema__Comprehend__Batch__Detect_Key_Phrases                 import Schema__Comprehend__Batch__Detect_Key_Phrases
from osbot_aws.aws.comprehend.schemas.batch.Schema__Comprehend__Batch__Detect_Entities                    import Schema__Comprehend__Batch__Detect_Entities
from osbot_aws.aws.comprehend.schemas.batch.Schema__Comprehend__Batch__Detect_Dominant_Language           import Schema__Comprehend__Batch__Detect_Dominant_Language
from osbot_aws.aws.comprehend.schemas.batch.Schema__Comprehend__Batch__Detect_Syntax                      import Schema__Comprehend__Batch__Detect_Syntax
from osbot_aws.aws.comprehend.schemas.enums.Enum__Comprehend__Language_Code                               import Enum__Comprehend__Language_Code
from osbot_aws.aws.comprehend.schemas.safe_str.Safe_Str__AWS_Comprehend__Text                             import Safe_Str__Comprehend__Text



class Comprehend__Batch(Type_Safe):
    client         : BaseClient
    response_utils : Comprehend__Response_Utils

    @type_safe
    def batch_detect_sentiment(self, text_list     : List[Safe_Str__Comprehend__Text]                                           ,
                                     language_code : Enum__Comprehend__Language_Code = Enum__Comprehend__Language_Code.ENGLISH  ,
                                ) -> Schema__Comprehend__Batch__Detect_Sentiment:
        with capture_duration() as duration:
            result = self.client.batch_detect_sentiment(TextList     = text_list            ,
                                                        LanguageCode = language_code.value)

        return Schema__Comprehend__Batch__Detect_Sentiment(result_list = [self.response_utils.process_batch_sentiment_result(item)
                                                                          for item in result.get('ResultList', [])]             ,
                                                            error_list  = self.response_utils.process_batch_errors(result)        ,
                                                            duration    = duration.seconds)

    @type_safe
    def batch_detect_entities(self, text_list     : List[Safe_Str__Comprehend__Text]                                           ,
                                     language_code : Enum__Comprehend__Language_Code = Enum__Comprehend__Language_Code.ENGLISH  ,
                               ) -> Schema__Comprehend__Batch__Detect_Entities:
        with capture_duration() as duration:
            result = self.client.batch_detect_entities(TextList     = text_list            ,
                                                       LanguageCode = language_code.value)

        return Schema__Comprehend__Batch__Detect_Entities(result_list = [self.response_utils.process_batch_entities_result(item)
                                                                         for item in result.get('ResultList', [])]             ,
                                                           error_list  = self.response_utils.process_batch_errors(result)        ,
                                                           duration    = duration.seconds)

    @type_safe
    def batch_detect_key_phrases(self, text_list     : List[Safe_Str__Comprehend__Text]                                           ,
                                       language_code : Enum__Comprehend__Language_Code = Enum__Comprehend__Language_Code.ENGLISH  ,
                                  ) -> Schema__Comprehend__Batch__Detect_Key_Phrases:
        with capture_duration() as duration:
            result = self.client.batch_detect_key_phrases(TextList     = text_list            ,
                                                          LanguageCode = language_code.value)

        return Schema__Comprehend__Batch__Detect_Key_Phrases(result_list = [self.response_utils.process_batch_key_phrases_result(item)
                                                                            for item in result.get('ResultList', [])]             ,
                                                               error_list  = self.response_utils.process_batch_errors(result)        ,
                                                               duration    = duration.seconds)

    @type_safe
    def batch_detect_dominant_language(self, text_list : List[Safe_Str__Comprehend__Text]
                                        ) -> Schema__Comprehend__Batch__Detect_Dominant_Language:
        with capture_duration() as duration:
            result = self.client.batch_detect_dominant_language(TextList = text_list)

        return Schema__Comprehend__Batch__Detect_Dominant_Language(result_list = [self.response_utils.process_batch_dominant_language_result(item)
                                                                                  for item in result.get('ResultList', [])]           ,
                                                                    error_list  = self.response_utils.process_batch_errors(result)      ,
                                                                    duration    = duration.seconds)

    @type_safe
    def batch_detect_syntax(self, text_list     : List[Safe_Str__Comprehend__Text]                                           ,
                                  language_code : Enum__Comprehend__Language_Code = Enum__Comprehend__Language_Code.ENGLISH  ,
                             ) -> Schema__Comprehend__Batch__Detect_Syntax:
        with capture_duration() as duration:
            result = self.client.batch_detect_syntax(TextList     = text_list            ,
                                                     LanguageCode = language_code.value)

        return Schema__Comprehend__Batch__Detect_Syntax(result_list = [self.response_utils.process_batch_syntax_result(item)
                                                                       for item in result.get('ResultList', [])]             ,
                                                         error_list  = self.response_utils.process_batch_errors(result)        ,
                                                         duration    = duration.seconds)
