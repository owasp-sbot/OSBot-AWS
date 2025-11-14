from osbot_utils.type_safe.Type_Safe                           import Type_Safe
from osbot_utils.type_safe.type_safe_core.decorators.type_safe import type_safe


class Comprehend__Response_Utils(Type_Safe):

    @type_safe
    def process_batch_errors(self, aws_response: dict) -> list:
        return [dict(index         = error.get('Index')        ,
                     error_code    = error.get('ErrorCode')    ,
                     error_message = error.get('ErrorMessage'))
                for error in aws_response.get('ErrorList', [])]

    @type_safe
    def process_sentiment_score(self, sentiment_score: dict) -> dict:
        return dict(mixed    = sentiment_score.get('Mixed'   ) ,
                    neutral  = sentiment_score.get('Neutral' ) ,
                    negative = sentiment_score.get('Negative') ,
                    positive = sentiment_score.get('Positive'))

    @type_safe
    def process_sentiment_result(self, item: dict) -> dict:
        return dict(sentiment = item.get('Sentiment')                                      ,
                    score     = self.process_sentiment_score(item.get('SentimentScore', {})))

    @type_safe
    def process_batch_sentiment_result(self, item: dict) -> dict:
        return dict(index = item.get('Index')                          ,
                    **self.process_sentiment_result(item))

    @type_safe
    def process_entity(self, entity: dict) -> dict:
        return dict(text         = entity.get('Text'       ) ,
                    type         = entity.get('Type'       ) ,
                    score        = entity.get('Score'      ) ,
                    begin_offset = entity.get('BeginOffset') ,
                    end_offset   = entity.get('EndOffset'  ))

    @type_safe
    def process_entities_result(self, aws_response: dict) -> list:
        return [self.process_entity(entity)
                for entity in aws_response.get('Entities', [])]

    @type_safe
    def process_batch_entities_result(self, item: dict) -> dict:
        return dict(index    = item.get('Index')                           ,
                    entities = [self.process_entity(e) for e in item.get('Entities', [])])

    @type_safe
    def process_key_phrase(self, phrase: dict) -> dict:
        return dict(text         = phrase.get('Text'       ) ,
                    score        = phrase.get('Score'      ) ,
                    begin_offset = phrase.get('BeginOffset') ,
                    end_offset   = phrase.get('EndOffset'  ))

    @type_safe
    def process_key_phrases_result(self, aws_response: dict) -> list:
        return [self.process_key_phrase(phrase)
                for phrase in aws_response.get('KeyPhrases', [])]

    @type_safe
    def process_batch_key_phrases_result(self, item: dict) -> dict:
        return dict(index       = item.get('Index')                                        ,
                    key_phrases = [self.process_key_phrase(p) for p in item.get('KeyPhrases', [])])

    @type_safe
    def process_language(self, language: dict) -> dict:
        return dict(language_code = language.get('LanguageCode') ,
                    score         = language.get('Score'        ))

    @type_safe
    def process_dominant_language_result(self, aws_response: dict) -> list:
        return [self.process_language(lang)
                for lang in aws_response.get('Languages', [])]

    @type_safe
    def process_batch_dominant_language_result(self, item: dict) -> dict:
        return dict(index     = item.get('Index')                                  ,
                    languages = [self.process_language(l) for l in item.get('Languages', [])])

    @type_safe
    def process_pii_entity(self, entity: dict) -> dict:
        return dict(type         = entity.get('Type'       ) ,
                    score        = entity.get('Score'      ) ,
                    begin_offset = entity.get('BeginOffset') ,
                    end_offset   = entity.get('EndOffset'  ))

    @type_safe
    def process_pii_entities_result(self, aws_response: dict) -> list:
        return [self.process_pii_entity(entity)
                for entity in aws_response.get('Entities', [])]

    @type_safe
    def process_syntax_token(self, token: dict) -> dict:
        pos = token.get('PartOfSpeech', {})
        return dict(text           = token.get('Text'       ) ,
                    token_id       = token.get('TokenId'    ) ,
                    begin_offset   = token.get('BeginOffset') ,
                    end_offset     = token.get('EndOffset'  ) ,
                    part_of_speech = dict(tag   = pos.get('Tag'  ) ,
                                          score = pos.get('Score')))

    @type_safe
    def process_syntax_result(self, aws_response: dict) -> list:
        return [self.process_syntax_token(token)
                for token in aws_response.get('SyntaxTokens', [])]

    @type_safe
    def process_batch_syntax_result(self, item: dict) -> dict:
        return dict(index         = item.get('Index')                                            ,
                    syntax_tokens = [self.process_syntax_token(t) for t in item.get('SyntaxTokens', [])])

    @type_safe
    def process_toxic_content_label(self, label: dict) -> dict:
        return dict(name  = label.get('Name' ) ,
                    score = label.get('Score'))

    @type_safe
    def process_toxic_content_result(self, aws_response: dict) -> list:
        result_blocks = aws_response.get('ResultList', [])
        if not result_blocks:
            return []
        first_result = result_blocks[0]
        return [self.process_toxic_content_label(label)
                for label in first_result.get('Labels', [])]
