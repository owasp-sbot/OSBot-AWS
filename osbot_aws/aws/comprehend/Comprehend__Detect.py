from botocore.client                                                                        import BaseClient
from osbot_utils.helpers.duration.decorators.capture_duration                               import capture_duration
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                              import type_safe
from osbot_aws.aws.comprehend.schemas.detect.Schema__Comprehend__Detect_Sentiment           import Schema__Comprehend__Detect_Sentiment
from osbot_aws.aws.comprehend.schemas.detect.Schema__Comprehend__Detect_Key_Phrases         import Schema__Comprehend__Detect_Key_Phrases
from osbot_aws.aws.comprehend.schemas.detect.Schema__Comprehend__Detect_Entities            import Schema__Comprehend__Detect_Entities
from osbot_aws.aws.comprehend.schemas.detect.Schema__Comprehend__Detect_Dominant_Language   import Schema__Comprehend__Detect_Dominant_Language
from osbot_aws.aws.comprehend.schemas.detect.Schema__Comprehend__Detect_Pii_Entities        import Schema__Comprehend__Detect_Pii_Entities
from osbot_aws.aws.comprehend.schemas.detect.Schema__Comprehend__Detect_Syntax              import Schema__Comprehend__Detect_Syntax
from osbot_aws.aws.comprehend.schemas.detect.Schema__Comprehend__Detect_Toxic_Content       import Schema__Comprehend__Detect_Toxic_Content
from osbot_aws.aws.comprehend.schemas.enums.Enum__Comprehend__Language_Code                 import Enum__Comprehend__Language_Code
from osbot_aws.aws.comprehend.schemas.safe_str.Safe_Str__AWS_Comprehend__Text               import Safe_Str__Comprehend__Text
from osbot_utils.type_safe.Type_Safe                                                        import Type_Safe



class Comprehend__Detect(Type_Safe):
    client : BaseClient

    @type_safe
    def detect_sentiment(self, text          : Safe_Str__Comprehend__Text                                              ,
                               language_code : Enum__Comprehend__Language_Code = Enum__Comprehend__Language_Code.ENGLISH,
                          ) -> Schema__Comprehend__Detect_Sentiment:
        with capture_duration() as duration:
            result = self.client.detect_sentiment(Text         = text         ,
                                                  LanguageCode = language_code.value)

        sentiment       = result.get('Sentiment')
        sentiment_score = result.get('SentimentScore')

        detect_sentiment = Schema__Comprehend__Detect_Sentiment(duration  = duration.seconds,
                                                                sentiment = sentiment      ,
                                                                score     = dict(mixed    = sentiment_score.get('Mixed'   ),
                                                                                 neutral  = sentiment_score.get('Neutral' ),
                                                                                 negative = sentiment_score.get('Negative'),
                                                                                 positive = sentiment_score.get('Positive')))
        return detect_sentiment

    @type_safe
    def detect_key_phrases(self, text          : Safe_Str__Comprehend__Text                                              ,
                                 language_code : Enum__Comprehend__Language_Code = Enum__Comprehend__Language_Code.ENGLISH,
                            ) -> Schema__Comprehend__Detect_Key_Phrases:
        with capture_duration() as duration:
            result = self.client.detect_key_phrases(Text         = text         ,
                                                    LanguageCode = language_code)

        key_phrases_list = []
        for phrase in result.get('KeyPhrases', []):
            key_phrases_list.append(dict(text         = phrase.get('Text'       ),
                                         score        = phrase.get('Score'      ),
                                         begin_offset = phrase.get('BeginOffset'),
                                         end_offset   = phrase.get('EndOffset'  )))

        return Schema__Comprehend__Detect_Key_Phrases(
            key_phrases = key_phrases_list,
            duration    = duration.seconds
        )

    @type_safe
    def detect_entities(self, text          : Safe_Str__Comprehend__Text                                              ,
                              language_code : Enum__Comprehend__Language_Code = Enum__Comprehend__Language_Code.ENGLISH,
                         ) -> Schema__Comprehend__Detect_Entities:
        with capture_duration() as duration:
            result = self.client.detect_entities(Text         = text         ,
                                                 LanguageCode = language_code)

        entities_list = []
        for entity in result.get('Entities', []):
            entities_list.append(dict(text         = entity.get('Text'       ),
                                      type         = entity.get('Type'       ),
                                      score        = entity.get('Score'      ),
                                      begin_offset = entity.get('BeginOffset'),
                                      end_offset   = entity.get('EndOffset'  )))

        return Schema__Comprehend__Detect_Entities(entities = entities_list   ,
                                                   duration = duration.seconds)

    @type_safe
    def detect_dominant_language(self, text: Safe_Str__Comprehend__Text
                                  ) -> Schema__Comprehend__Detect_Dominant_Language:
        with capture_duration() as duration:
            result = self.client.detect_dominant_language(Text = text)

        languages_list = []
        for language in result.get('Languages', []):
            languages_list.append(dict(language_code = language.get('LanguageCode'),
                                       score         = language.get('Score')))

        return Schema__Comprehend__Detect_Dominant_Language(languages = languages_list  ,
                                                            duration  = duration.seconds)

    @type_safe
    def detect_pii_entities(self, text          : Safe_Str__Comprehend__Text                                              ,
                                  language_code : Enum__Comprehend__Language_Code = Enum__Comprehend__Language_Code.ENGLISH,
                             ) -> Schema__Comprehend__Detect_Pii_Entities:
        with capture_duration() as duration:
            result = self.client.detect_pii_entities(Text         = text         ,
                                                     LanguageCode = language_code)

        entities_list = []
        for entity in result.get('Entities', []):
            entities_list.append(dict(type         = entity.get('Type'       ),
                                      score        = entity.get('Score'      ),
                                      begin_offset = entity.get('BeginOffset'),
                                      end_offset   = entity.get('EndOffset'  )))

        return Schema__Comprehend__Detect_Pii_Entities(entities = entities_list   ,
                                                       duration = duration.seconds)

    @type_safe
    def detect_syntax(self, text          : Safe_Str__Comprehend__Text                                              ,
                            language_code : Enum__Comprehend__Language_Code = Enum__Comprehend__Language_Code.ENGLISH,
                       ) -> Schema__Comprehend__Detect_Syntax:
        with capture_duration() as duration:
            result = self.client.detect_syntax(Text         = text         ,
                                               LanguageCode = language_code)

        tokens_list = []
        for token in result.get('SyntaxTokens', []):
            pos = token.get('PartOfSpeech', {})
            tokens_list.append(dict(text           = token.get('Text'       ),
                                    token_id       = token.get('TokenId'    ),
                                    begin_offset   = token.get('BeginOffset'),
                                    end_offset     = token.get('EndOffset'  ),
                                    part_of_speech = dict(tag   = pos.get('Tag'  ),
                                                          score = pos.get('Score'))))

        return Schema__Comprehend__Detect_Syntax(syntax_tokens = tokens_list     ,
                                                 duration      = duration.seconds)

    @type_safe
    def detect_toxic_content(self, text          : Safe_Str__Comprehend__Text                                              ,
                                   language_code : Enum__Comprehend__Language_Code = Enum__Comprehend__Language_Code.ENGLISH,
                              ) -> Schema__Comprehend__Detect_Toxic_Content:
        with capture_duration() as duration:
            result = self.client.detect_toxic_content(TextSegments = [{'Text': text}],
                                                      LanguageCode = language_code)


        result_blocks = result.get('ResultList', [])
        labels_list   = []

        if result_blocks:
            first_result = result_blocks[0]
            for label in first_result.get('Labels', []):
                labels_list.append(dict(name  = label.get('Name' ),
                                        score = label.get('Score')))

        return Schema__Comprehend__Detect_Toxic_Content(labels   = labels_list     ,
                                                        duration = duration.seconds)