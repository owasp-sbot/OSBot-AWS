from botocore.client                                                                        import BaseClient
from osbot_utils.helpers.duration.decorators.capture_duration                               import capture_duration
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                              import type_safe
from osbot_utils.type_safe.Type_Safe                                                        import Type_Safe
from osbot_aws.aws.comprehend.Comprehend__Response_Utils                                    import Comprehend__Response_Utils
from osbot_aws.aws.comprehend.schemas.detect.Schema__Comprehend__Detect_Sentiment           import Schema__Comprehend__Detect_Sentiment
from osbot_aws.aws.comprehend.schemas.detect.Schema__Comprehend__Detect_Key_Phrases         import Schema__Comprehend__Detect_Key_Phrases
from osbot_aws.aws.comprehend.schemas.detect.Schema__Comprehend__Detect_Entities            import Schema__Comprehend__Detect_Entities
from osbot_aws.aws.comprehend.schemas.detect.Schema__Comprehend__Detect_Dominant_Language   import Schema__Comprehend__Detect_Dominant_Language
from osbot_aws.aws.comprehend.schemas.detect.Schema__Comprehend__Detect_Pii_Entities        import Schema__Comprehend__Detect_Pii_Entities
from osbot_aws.aws.comprehend.schemas.detect.Schema__Comprehend__Detect_Syntax              import Schema__Comprehend__Detect_Syntax
from osbot_aws.aws.comprehend.schemas.detect.Schema__Comprehend__Detect_Toxic_Content       import Schema__Comprehend__Detect_Toxic_Content
from osbot_aws.aws.comprehend.schemas.enums.Enum__Comprehend__Language_Code                 import Enum__Comprehend__Language_Code
from osbot_aws.aws.comprehend.schemas.safe_str.Safe_Str__AWS_Comprehend__Text               import Safe_Str__Comprehend__Text



class Comprehend__Detect(Type_Safe):
    client         : BaseClient
    response_utils : Comprehend__Response_Utils

    @type_safe
    def detect_sentiment(self, text          : Safe_Str__Comprehend__Text                                              ,
                               language_code : Enum__Comprehend__Language_Code = Enum__Comprehend__Language_Code.ENGLISH,
                          ) -> Schema__Comprehend__Detect_Sentiment:
        with capture_duration() as duration:
            result = self.client.detect_sentiment(Text         = text                ,
                                                  LanguageCode = language_code.value)

        return Schema__Comprehend__Detect_Sentiment(duration = duration.seconds,
                                                    **self.response_utils.process_sentiment_result(result))

    @type_safe
    def detect_key_phrases(self, text          : Safe_Str__Comprehend__Text                                              ,
                                 language_code : Enum__Comprehend__Language_Code = Enum__Comprehend__Language_Code.ENGLISH,
                            ) -> Schema__Comprehend__Detect_Key_Phrases:
        with capture_duration() as duration:
            result = self.client.detect_key_phrases(Text         = text         ,
                                                    LanguageCode = language_code)

        return Schema__Comprehend__Detect_Key_Phrases(key_phrases = self.response_utils.process_key_phrases_result(result),
                                                      duration    = duration.seconds)

    @type_safe
    def detect_entities(self, text          : Safe_Str__Comprehend__Text                                              ,
                              language_code : Enum__Comprehend__Language_Code = Enum__Comprehend__Language_Code.ENGLISH,
                         ) -> Schema__Comprehend__Detect_Entities:
        with capture_duration() as duration:
            result = self.client.detect_entities(Text         = text         ,
                                                 LanguageCode = language_code)

        return Schema__Comprehend__Detect_Entities(entities = self.response_utils.process_entities_result(result),
                                                   duration = duration.seconds)

    @type_safe
    def detect_dominant_language(self, text: Safe_Str__Comprehend__Text
                                  ) -> Schema__Comprehend__Detect_Dominant_Language:
        with capture_duration() as duration:
            result = self.client.detect_dominant_language(Text = text)

        return Schema__Comprehend__Detect_Dominant_Language(languages = self.response_utils.process_dominant_language_result(result),
                                                            duration  = duration.seconds)

    @type_safe
    def detect_pii_entities(self, text          : Safe_Str__Comprehend__Text                                              ,
                                  language_code : Enum__Comprehend__Language_Code = Enum__Comprehend__Language_Code.ENGLISH,
                             ) -> Schema__Comprehend__Detect_Pii_Entities:
        with capture_duration() as duration:
            result = self.client.detect_pii_entities(Text         = text         ,
                                                     LanguageCode = language_code)

        return Schema__Comprehend__Detect_Pii_Entities(entities = self.response_utils.process_pii_entities_result(result),
                                                       duration = duration.seconds)

    @type_safe
    def detect_syntax(self, text          : Safe_Str__Comprehend__Text                                              ,
                            language_code : Enum__Comprehend__Language_Code = Enum__Comprehend__Language_Code.ENGLISH,
                       ) -> Schema__Comprehend__Detect_Syntax:
        with capture_duration() as duration:
            result = self.client.detect_syntax(Text         = text         ,
                                               LanguageCode = language_code)

        return Schema__Comprehend__Detect_Syntax(syntax_tokens = self.response_utils.process_syntax_result(result),
                                                 duration      = duration.seconds)

    @type_safe
    def detect_toxic_content(self, text          : Safe_Str__Comprehend__Text                                              ,
                                   language_code : Enum__Comprehend__Language_Code = Enum__Comprehend__Language_Code.ENGLISH,
                              ) -> Schema__Comprehend__Detect_Toxic_Content:
        with capture_duration() as duration:
            result = self.client.detect_toxic_content(TextSegments = [{'Text': text}],
                                                      LanguageCode = language_code)

        return Schema__Comprehend__Detect_Toxic_Content(labels   = self.response_utils.process_toxic_content_result(result),
                                                        duration = duration.seconds)
