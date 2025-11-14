import pytest
from unittest                                                                                       import TestCase
from osbot_utils.testing.__                                                                         import __, __LESS_THAN__, __GREATER_THAN__, __SKIP__
from osbot_utils.utils.Env                                                                          import in_github_action
from osbot_utils.utils.Objects                                                                      import type_full_name, base_types
from osbot_utils.type_safe.Type_Safe                                                                import Type_Safe
from osbot_aws.aws.comprehend.Comprehend__Base                                                      import Comprehend__Base
from osbot_aws.aws.comprehend.Comprehend__Batch                                                     import Comprehend__Batch
from osbot_aws.aws.comprehend.Comprehend__Batch__with_temp_role                                     import Comprehend__Batch__with_temp_role
from osbot_aws.aws.comprehend.Comprehend__IAM__Temp_Role import Comprehend__IAM__Temp_Role
from osbot_aws.aws.comprehend.schemas.batch.Schema__Comprehend__Batch__Detect_Sentiment             import Schema__Comprehend__Batch__Detect_Sentiment
from osbot_aws.aws.comprehend.schemas.batch.Schema__Comprehend__Batch__Detect_Entities              import Schema__Comprehend__Batch__Detect_Entities
from osbot_aws.aws.comprehend.schemas.batch.Schema__Comprehend__Batch__Detect_Key_Phrases           import Schema__Comprehend__Batch__Detect_Key_Phrases
from osbot_aws.aws.comprehend.schemas.batch.Schema__Comprehend__Batch__Detect_Dominant_Language     import Schema__Comprehend__Batch__Detect_Dominant_Language
from osbot_aws.aws.comprehend.schemas.batch.Schema__Comprehend__Batch__Detect_Syntax                import Schema__Comprehend__Batch__Detect_Syntax
from osbot_aws.aws.comprehend.schemas.enums.Enum__Comprehend__Language_Code                         import Enum__Comprehend__Language_Code


class test_Comprehend__Batch(TestCase):

    @classmethod
    def setUpClass(cls):
        if in_github_action():
            pytest.skip("Doesn't work when running all tests")              # todo: fix issue caused by the use of localstack as a target
        cls.comprehend_batch = Comprehend__Batch__with_temp_role()

    def test__init__(self):                                                 # Test basic initialization and inheritance
        with self.comprehend_batch as _:
            assert type(_)         is Comprehend__Batch__with_temp_role
            assert base_types(_)   == [Comprehend__IAM__Temp_Role,
                                       Comprehend__Batch         ,
                                       Type_Safe                 , object,
                                       Comprehend__Base          ,
                                       Type_Safe                 , object]

    def test_client(self):                                                  # Test client creation
        with self.comprehend_batch as _:
            client = _.client()
            assert type_full_name(client) == 'botocore.client.Comprehend'

    # ============================================================================
    # BATCH SENTIMENT DETECTION TESTS
    # ============================================================================

    def test_batch_detect_sentiment(self):                                  # Test batch sentiment analysis with multiple documents
        with self.comprehend_batch as _:
            text_list = ['Hello World'      ,                               # Positive
                         'This is terrible' ,                               # Negative
                         'The sky is blue'  ]                               # Neutral
            
            result = _.batch_detect_sentiment(text_list)

            assert result.obj() == __(result_list = [ __(index    = 0                          ,
                                                         sentiment = 'Positive'                 ,
                                                         score     = __(mixed    = __LESS_THAN__   (0.01)  ,    # 0.0010159355588257313
                                                                        negative = __LESS_THAN__   (0.01)  ,    # 0.0015335445059463382
                                                                        neutral  = __GREATER_THAN__(0.4 )  ,    # 0.42408183217048645
                                                                        positive = __GREATER_THAN__(0.5 ))),    # 0.5733687281608582

                                                       __(index    = 1                          ,
                                                          sentiment = 'Negative'                 ,
                                                          score     = __(mixed    = __LESS_THAN__   (0.01)  ,    # 6.76e-05
                                                                         negative = __GREATER_THAN__(0.99)  ,    # 0.9993947744369507
                                                                         neutral  = __LESS_THAN__   (0.01)  ,    # 0.00041700719157233834
                                                                         positive = __LESS_THAN__   (0.01))),    # 0.00012057989806635305

                                                       __(index    = 2                          ,
                                                          sentiment = 'Neutral'                  ,
                                                          score     = __(mixed    = __LESS_THAN__   (0.01)  ,    # 0.004692689049988985
                                                                         negative = __LESS_THAN__   (0.01)  ,    # 0.007945283316075802
                                                                         neutral  = __GREATER_THAN__(0.8)   ,    # 0.8721814751625061
                                                                         positive = __GREATER_THAN__(0.1)))],    # 0.11518055200576782
                                       error_list  = []                                                     ,
                                       duration    = __SKIP__                                               )



            assert type(result) is Schema__Comprehend__Batch__Detect_Sentiment
            assert len(result.result_list) == 3                                     # All documents processed successfully
            assert len(result.error_list)  == 0                                     # No errors

            assert result.result_list[0].index     == 0                             # Verify first document (positive sentiment)
            assert result.result_list[0].sentiment == 'Positive'
            assert result.result_list[0].score.positive > 0.5

            assert result.result_list[1].index     == 1                             # Verify second document (negative sentiment)
            assert result.result_list[1].sentiment == 'Negative'
            assert result.result_list[1].score.negative > 0.9
            
            # Verify duration tracking
            assert result.duration < 0.5                                    # Should complete in reasonable time

    def test_batch_detect_sentiment__single_document(self):                # Test batch operation with single document
        with self.comprehend_batch as _:
            text_list = ['I am very happy today!']
            result    = _.batch_detect_sentiment(text_list)
            
            assert type(result)            is Schema__Comprehend__Batch__Detect_Sentiment
            assert len(result.result_list) == 1
            assert len(result.error_list)  == 0
            assert result.result_list[0].obj().contains(__(index=0, sentiment='Positive'))

    def test_batch_detect_sentiment__with_language_code(self):             # Test batch sentiment with non-English text
        with self.comprehend_batch as _:
            text_list       = ['Hola mundo', 'Buenos días']
            language_code   = Enum__Comprehend__Language_Code.SPANISH
            result          = _.batch_detect_sentiment(text_list, language_code=language_code)
            
            assert type(result)            is Schema__Comprehend__Batch__Detect_Sentiment
            assert len(result.result_list) == 2
            assert len(result.error_list)  == 0
            assert result.obj()            == __(result_list = [ __( index    = 0                          ,
                                                                     sentiment = 'Neutral'                  ,
                                                                     score     = __(mixed    = __LESS_THAN__    (0.03) ,    # 0.026481686159968376
                                                                                    negative = __LESS_THAN__    (0.03) ,    # 0.022698430344462395
                                                                                    neutral  = __GREATER_THAN__ (0.8) ,    # 0.8512195944786072
                                                                                    positive = __GREATER_THAN__ (0.09))) ,  # 0.09960027784109116

                                                                   __(index    = 1                          ,
                                                                     sentiment = 'Positive'                 ,
                                                                     score     = __(mixed    = __LESS_THAN__    (0.01) ,    # 0.0019052064744755626
                                                                                    negative = __LESS_THAN__    (0.01) ,    # 0.001504825777374208
                                                                                    neutral  = __GREATER_THAN__ (0.03),    # 0.03418412059545517
                                                                                    positive = __GREATER_THAN__ (0.9)))] ,  # 0.9624059200286865
                                                   error_list  = []                                                                                          ,
                                                   duration    = __SKIP__                                                                                    )


    # ============================================================================
    # BATCH ENTITY DETECTION TESTS
    # ============================================================================

    def test_batch_detect_entities(self):                                   # Test batch named entity recognition
        with self.comprehend_batch as _:
            text_list = [
                'Amazon was founded by Jeff Bezos in Seattle',              # Multiple entity types
                'Microsoft is located in Redmond, Washington',              # Organization and location
                'The meeting is on January 15, 2024'                        # Date entity
            ]
            
            result = _.batch_detect_entities(text_list)
            
            assert type(result)            is Schema__Comprehend__Batch__Detect_Entities
            assert len(result.result_list) == 3
            assert len(result.error_list)  == 0
            
            # Verify first document has multiple entities
            first_doc_entities = result.result_list[0]
            assert first_doc_entities.index == 0
            assert len(first_doc_entities.entities) > 0
            
            # Check for expected entity types
            entity_types = {e.type for e in first_doc_entities.entities}
            assert 'ORGANIZATION' in entity_types or 'PERSON' in entity_types

    def test_batch_detect_entities__locations(self):                        # Test batch detection of location entities
        with self.comprehend_batch as _:
            text_list = [
                'I traveled from Paris to Tokyo',
                'London is a beautiful city'
            ]
            
            result = _.batch_detect_entities(text_list)
            
            assert type(result)            is Schema__Comprehend__Batch__Detect_Entities
            assert len(result.result_list) == 2
            assert len(result.error_list)  == 0
            
            # Both documents should have location entities
            for doc_result in result.result_list:
                assert len(doc_result.entities) > 0

    # ============================================================================
    # BATCH KEY PHRASE DETECTION TESTS
    # ============================================================================

    def test_batch_detect_key_phrases(self):                                # Test batch key phrase extraction
        with self.comprehend_batch as _:
            text_list = [
                'AWS Lambda is a serverless compute service',
                'Amazon S3 provides object storage',
                'Machine learning models require training data'
            ]
            
            result = _.batch_detect_key_phrases(text_list)
            
            assert type(result)            is Schema__Comprehend__Batch__Detect_Key_Phrases
            assert len(result.result_list) == 3
            assert len(result.error_list)  == 0
            
            # Each document should have key phrases extracted
            for doc_result in result.result_list:
                assert len(doc_result.key_phrases) > 0
                # Verify key phrase structure
                for phrase in doc_result.key_phrases:
                    assert hasattr(phrase, 'text')
                    assert hasattr(phrase, 'score')
                    assert phrase.score > 0

    def test_batch_detect_key_phrases__simple_text(self):                   # Test batch key phrases with simple text
        with self.comprehend_batch as _:
            text_list = [
                'The quick brown fox jumps over the lazy dog',
                'Hello world'
            ]
            
            result = _.batch_detect_key_phrases(text_list)
            
            assert type(result)            is Schema__Comprehend__Batch__Detect_Key_Phrases
            assert len(result.result_list) == 2
            assert len(result.error_list)  == 0

    # ============================================================================
    # BATCH DOMINANT LANGUAGE DETECTION TESTS
    # ============================================================================

    def test_batch_detect_dominant_language(self):                          # Test batch automatic language detection
        with self.comprehend_batch as _:
            text_list = [ 'Hello World'        ,                                      # English
                          'Hola mundo'         ,                                      # Spanish
                          'Bonjour le monde'    ]                                      # French
            
            result = _.batch_detect_dominant_language(text_list)
            
            assert type(result)            is Schema__Comprehend__Batch__Detect_Dominant_Language
            assert len(result.result_list) == 3
            assert len(result.error_list)  == 0

            assert result.obj() == __(result_list = [ __(index    = 0 ,
                                                         languages = [ __(language_code = 'en' , score = __GREATER_THAN__(0.9)) ]) ,    # 0.9798225164413452
                                                       __(index    = 1 ,
                                                         languages = [ __(language_code = 'es' , score = __GREATER_THAN__(0.9)) ]) ,    # 0.943865180015564
                                                       __(index    = 2 ,
                                                         languages = [ __(language_code = 'fr' , score = __GREATER_THAN__(0.9)) ])] ,   # 0.9318777322769165
                                       error_list  = []                                                                                 ,
                                       duration    = __SKIP__                                                                           )


            # Verify language detection
            assert result.result_list[0].languages[0].language_code == 'en' # English
            assert result.result_list[1].languages[0].language_code == 'es' # Spanish
            assert result.result_list[2].languages[0].language_code == 'fr' # French
            
            # Verify confidence scores
            for doc_result in result.result_list:
                assert doc_result.languages[0].score > 0.8                  # High confidence

    def test_batch_detect_dominant_language__mixed_languages(self):         # Test detection with mixed-language documents
        with self.comprehend_batch as _:
            text_list = [
                'Hola my friend, como estas today?',                        # Mixed Spanish-English
                'Bonjour, how are you?'                                     # Mixed French-English
            ]
            
            result = _.batch_detect_dominant_language(text_list)
            
            assert type(result)            is Schema__Comprehend__Batch__Detect_Dominant_Language
            assert len(result.result_list) == 2
            assert len(result.error_list)  == 0
            
            # Each document should detect at least one language
            for doc_result in result.result_list:
                assert len(doc_result.languages) > 0

    # ============================================================================
    # BATCH SYNTAX DETECTION TESTS
    # ============================================================================

    def test_batch_detect_syntax(self):                                     # Test batch part-of-speech tagging
        with self.comprehend_batch as _:
            text_list = [
                'The quick brown fox jumps',
                'The cat sleeps quietly'
            ]
            
            result = _.batch_detect_syntax(text_list)
            
            assert type(result)            is Schema__Comprehend__Batch__Detect_Syntax
            assert len(result.result_list) == 2
            assert len(result.error_list)  == 0
            
            # Verify syntax tokens exist
            for doc_result in result.result_list:
                assert len(doc_result.syntax_tokens) > 0
                
                # Verify token structure
                for token in doc_result.syntax_tokens:
                    assert hasattr(token, 'text')
                    assert hasattr(token, 'token_id')
                    assert hasattr(token, 'part_of_speech')
                    assert hasattr(token.part_of_speech, 'tag')

    def test_batch_detect_syntax__token_offsets(self):                      # Test that batch syntax returns correct token offsets
        with self.comprehend_batch as _:
            text_list = ['Hello world', 'Goodbye moon']
            result    = _.batch_detect_syntax(text_list)
            
            assert type(result)            is Schema__Comprehend__Batch__Detect_Syntax
            assert len(result.result_list) == 2
            
            # Verify offsets are valid for each document
            for i, doc_result in enumerate(result.result_list):
                original_text = text_list[i]
                for token in doc_result.syntax_tokens:
                    assert token.begin_offset < token.end_offset
                    assert token.end_offset <= len(original_text)

    # ============================================================================
    # BATCH SIZE AND LIMITS TESTS
    # ============================================================================

    def test_batch_detect_sentiment__max_batch_size(self):                  # Test batch processing with 25 documents (AWS limit)
        with self.comprehend_batch as _:
            # Create 25 documents (maximum allowed)
            text_list = [f'This is test document number {i}' for i in range(25)]
            result    = _.batch_detect_sentiment(text_list)
            
            assert type(result)            is Schema__Comprehend__Batch__Detect_Sentiment
            assert len(result.result_list) == 25                            # All documents processed
            assert len(result.error_list)  == 0                             # No errors

    def test_batch_operations__consistency(self):                           # Test that all batch operations work with same input
        with self.comprehend_batch as _:
            text_list = ['Amazon Web Services', 'Microsoft Azure', 'Google Cloud']

            # Run all batch operations on same data
            sentiment_result = _.batch_detect_sentiment         (text_list)
            entities_result  = _.batch_detect_entities          (text_list)
            phrases_result   = _.batch_detect_key_phrases       (text_list)
            language_result  = _.batch_detect_dominant_language (text_list)
            syntax_result    = _.batch_detect_syntax            (text_list)
            
            # All should successfully process all documents
            assert len(sentiment_result.result_list) == 3
            assert len(entities_result.result_list)  == 3
            assert len(phrases_result.result_list)   == 3
            assert len(language_result.result_list)  == 3
            assert len(syntax_result.result_list)    == 3
            
            # No errors for any operation
            assert len(sentiment_result.error_list) == 0
            assert len(entities_result.error_list)  == 0
            assert len(phrases_result.error_list)   == 0
            assert len(language_result.error_list)  == 0
            assert len(syntax_result.error_list)    == 0

    # ============================================================================
    # EDGE CASES AND VALIDATION TESTS
    # ============================================================================

    def test_batch_detect_sentiment__minimal_text(self):                    # Test batch with very short texts
        with self.comprehend_batch as _:
            text_list = ['Hi', 'OK', 'Yes']
            result    = _.batch_detect_sentiment(text_list)
            
            assert type(result) is Schema__Comprehend__Batch__Detect_Sentiment
            # AWS may return results or errors for very short text
            assert len(result.result_list) + len(result.error_list) == 3

    def test_batch_detect_entities__no_entities(self):                      # Test batch with text containing no entities
        with self.comprehend_batch as _:
            text_list = ['It was nice', 'Everything is good']
            result    = _.batch_detect_entities(text_list)
            
            assert type(result)            is Schema__Comprehend__Batch__Detect_Entities
            assert len(result.result_list) == 2
            # Documents may have zero entities - this is valid

    def test_batch_operations__duration_tracking(self):                     # Test that all batch operations track duration
        with self.comprehend_batch as _:
            text_list = ['Test text for duration tracking']
            
            sentiment_result = _.batch_detect_sentiment(text_list)
            entities_result  = _.batch_detect_entities(text_list)
            phrases_result   = _.batch_detect_key_phrases(text_list)
            language_result  = _.batch_detect_dominant_language(text_list)
            syntax_result    = _.batch_detect_syntax(text_list)
            
            # All operations should track duration
            assert sentiment_result.duration > 0
            assert entities_result.duration  > 0
            assert phrases_result.duration   > 0
            assert language_result.duration  > 0
            assert syntax_result.duration    > 0
            
            # Duration should be reasonable (< 10 seconds for single document)
            assert sentiment_result.duration < 10.0
            assert entities_result.duration  < 10.0
            assert phrases_result.duration   < 10.0
            assert language_result.duration  < 10.0
            assert syntax_result.duration    < 10.0
