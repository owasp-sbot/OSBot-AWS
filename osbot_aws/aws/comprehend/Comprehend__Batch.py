from typing                                                                                               import List
from osbot_utils.helpers.duration.decorators.capture_duration                                             import capture_duration
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                            import type_safe
from osbot_aws.aws.comprehend.Comprehend__Base                                                            import Comprehend__Base
from osbot_aws.aws.comprehend.schemas.batch.Schema__Comprehend__Batch__Detect_Sentiment                   import Schema__Comprehend__Batch__Detect_Sentiment
from osbot_aws.aws.comprehend.schemas.batch.Schema__Comprehend__Batch__Detect_Key_Phrases                 import Schema__Comprehend__Batch__Detect_Key_Phrases
from osbot_aws.aws.comprehend.schemas.batch.Schema__Comprehend__Batch__Detect_Entities                    import Schema__Comprehend__Batch__Detect_Entities
from osbot_aws.aws.comprehend.schemas.batch.Schema__Comprehend__Batch__Detect_Dominant_Language           import Schema__Comprehend__Batch__Detect_Dominant_Language
from osbot_aws.aws.comprehend.schemas.batch.Schema__Comprehend__Batch__Detect_Syntax                      import Schema__Comprehend__Batch__Detect_Syntax
from osbot_aws.aws.comprehend.schemas.enums.Enum__Comprehend__Language_Code                               import Enum__Comprehend__Language_Code
from osbot_aws.aws.comprehend.schemas.safe_str.Safe_Str__AWS_Comprehend__Text                             import Safe_Str__Comprehend__Text


class Comprehend__Batch(Comprehend__Base):


    # ============================================================================
    # BATCH SENTIMENT DETECTION
    # ============================================================================

    @type_safe
    def batch_detect_sentiment(self, text_list      : List[Safe_Str__Comprehend__Text]                                           ,
                                     language_code  : Enum__Comprehend__Language_Code = Enum__Comprehend__Language_Code.ENGLISH  ,
                                ) -> Schema__Comprehend__Batch__Detect_Sentiment:

        with capture_duration() as duration:
            result = self.client().batch_detect_sentiment(TextList     = text_list     ,
                                                          LanguageCode = language_code.value)

        # Process successful results
        result_list = []
        for item in result.get('ResultList', []):
            sentiment_score = item.get('SentimentScore', {})
            result_list.append(dict(index     = item.get('Index')                       ,
                                   sentiment = item.get('Sentiment')                    ,
                                   score     = dict(mixed    = sentiment_score.get('Mixed'   ) ,
                                                    neutral  = sentiment_score.get('Neutral' ) ,
                                                    negative = sentiment_score.get('Negative') ,
                                                    positive = sentiment_score.get('Positive'))))

        # Process errors
        error_list = []
        for error in result.get('ErrorList', []):
            error_list.append(dict(index         = error.get('Index')        ,
                                   error_code    = error.get('ErrorCode')    ,
                                   error_message = error.get('ErrorMessage')))

        return Schema__Comprehend__Batch__Detect_Sentiment(result_list = result_list    ,
                                                           error_list  = error_list     ,
                                                           duration    = duration.seconds)

    # ============================================================================
    # BATCH ENTITY DETECTION
    # ============================================================================

    @type_safe
    def batch_detect_entities(self, text_list     : List[Safe_Str__Comprehend__Text]                                           ,
                                     language_code : Enum__Comprehend__Language_Code = Enum__Comprehend__Language_Code.ENGLISH  ,
                               ) -> Schema__Comprehend__Batch__Detect_Entities:
        with capture_duration() as duration:
            result = self.client().batch_detect_entities(TextList     = text_list     ,
                                                         LanguageCode = language_code.value)

        # Process successful results
        result_list = []
        for item in result.get('ResultList', []):
            entities_list = []
            for entity in item.get('Entities', []):
                entities_list.append(dict(text         = entity.get('Text'       ) ,
                                          type         = entity.get('Type'       ) ,
                                          score        = entity.get('Score'      ) ,
                                          begin_offset = entity.get('BeginOffset') ,
                                          end_offset   = entity.get('EndOffset'  )))
            
            result_list.append(dict(index    = item.get('Index') ,
                                   entities = entities_list      ))

        # Process errors
        error_list = []
        for error in result.get('ErrorList', []):
            error_list.append(dict(index         = error.get('Index')        ,
                                  error_code    = error.get('ErrorCode')    ,
                                  error_message = error.get('ErrorMessage')))

        return Schema__Comprehend__Batch__Detect_Entities(result_list = result_list    ,
                                                          error_list  = error_list     ,
                                                          duration    = duration.seconds)

    # ============================================================================
    # BATCH KEY PHRASE DETECTION
    # ============================================================================

    @type_safe
    def batch_detect_key_phrases(self, text_list     : List[Safe_Str__Comprehend__Text]                                           ,
                                       language_code : Enum__Comprehend__Language_Code = Enum__Comprehend__Language_Code.ENGLISH  ,
                                  ) -> Schema__Comprehend__Batch__Detect_Key_Phrases:
        with capture_duration() as duration:
            result = self.client().batch_detect_key_phrases(TextList     = text_list     ,
                                                            LanguageCode = language_code.value)

        # Process successful results
        result_list = []
        for item in result.get('ResultList', []):
            key_phrases_list = []
            for phrase in item.get('KeyPhrases', []):
                key_phrases_list.append(dict(text         = phrase.get('Text'       ) ,
                                             score        = phrase.get('Score'      ) ,
                                             begin_offset = phrase.get('BeginOffset') ,
                                             end_offset   = phrase.get('EndOffset'  )))
            
            result_list.append(dict(index       = item.get('Index') ,
                                   key_phrases = key_phrases_list   ))

        # Process errors
        error_list = []
        for error in result.get('ErrorList', []):
            error_list.append(dict(index         = error.get('Index')        ,
                                  error_code    = error.get('ErrorCode')    ,
                                  error_message = error.get('ErrorMessage')))

        return Schema__Comprehend__Batch__Detect_Key_Phrases(result_list = result_list    ,
                                                             error_list  = error_list     ,
                                                             duration    = duration.seconds)

    # ============================================================================
    # BATCH DOMINANT LANGUAGE DETECTION
    # ============================================================================

    @type_safe
    def batch_detect_dominant_language(self, text_list : List[Safe_Str__Comprehend__Text]
                                        ) -> Schema__Comprehend__Batch__Detect_Dominant_Language:
        with capture_duration() as duration:
            result = self.client().batch_detect_dominant_language(TextList = text_list)

        # Process successful results
        result_list = []
        for item in result.get('ResultList', []):
            languages_list = []
            for language in item.get('Languages', []):
                languages_list.append(dict(language_code = language.get('LanguageCode') ,
                                           score         = language.get('Score'        )))
            
            result_list.append(dict(index     = item.get('Index') ,
                                    languages = languages_list     ))

        # Process errors
        error_list = []
        for error in result.get('ErrorList', []):
            error_list.append(dict(index         = error.get('Index')        ,
                                   error_code    = error.get('ErrorCode')    ,
                                   error_message = error.get('ErrorMessage')))

        return Schema__Comprehend__Batch__Detect_Dominant_Language(result_list = result_list    ,
                                                                   error_list  = error_list     ,
                                                                   duration    = duration.seconds)

    # ============================================================================
    # BATCH SYNTAX DETECTION
    # ============================================================================

    @type_safe
    def batch_detect_syntax(self, text_list     : List[Safe_Str__Comprehend__Text]                                           ,
                                  language_code : Enum__Comprehend__Language_Code = Enum__Comprehend__Language_Code.ENGLISH  ,
                             ) -> Schema__Comprehend__Batch__Detect_Syntax:

        with capture_duration() as duration:
            result = self.client().batch_detect_syntax(TextList     = text_list     ,
                                                       LanguageCode = language_code.value)

        # Process successful results
        result_list = []
        for item in result.get('ResultList', []):
            tokens_list = []
            for token in item.get('SyntaxTokens', []):
                pos = token.get('PartOfSpeech', {})
                tokens_list.append(dict(text           = token.get('Text'       ) ,
                                       token_id       = token.get('TokenId'    ) ,
                                       begin_offset   = token.get('BeginOffset') ,
                                       end_offset     = token.get('EndOffset'  ) ,
                                       part_of_speech = dict(tag   = pos.get('Tag'  ) ,
                                                             score = pos.get('Score'))))
            
            result_list.append(dict(index         = item.get('Index') ,
                                   syntax_tokens = tokens_list        ))

        # Process errors
        error_list = []
        for error in result.get('ErrorList', []):
            error_list.append(dict(index         = error.get('Index')        ,
                                  error_code    = error.get('ErrorCode')    ,
                                  error_message = error.get('ErrorMessage')))

        return Schema__Comprehend__Batch__Detect_Syntax(result_list = result_list    ,
                                                        error_list  = error_list     ,
                                                        duration    = duration.seconds)
