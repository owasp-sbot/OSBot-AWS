import pytest
from unittest                                                                                       import TestCase
from osbot_utils.type_safe.primitives.domains.numerical.safe_float.Safe_Float__Probability_Score    import Safe_Float__Probability_Score
from osbot_utils.testing.__                                                                         import __, __LESS_THAN__, __GREATER_THAN__, __BETWEEN__, __CLOSE_TO__, __SKIP__
from osbot_utils.utils.Env                                                                          import in_github_action
from osbot_aws.aws.comprehend.Comprehend                                                            import Comprehend
from osbot_aws.aws.comprehend.Comprehend__with_temp_role                                            import Comprehend__with_temp_role
from osbot_aws.aws.comprehend.schemas.Schema__Comprehend__Detect_Sentiment                          import Schema__Comprehend__Detect_Sentiment
from osbot_aws.aws.comprehend.schemas.Schema__Comprehend__Detect_Key_Phrases                        import Schema__Comprehend__Detect_Key_Phrases
from osbot_aws.aws.comprehend.schemas.Schema__Comprehend__Detect_Entities                           import Schema__Comprehend__Detect_Entities
from osbot_aws.aws.comprehend.schemas.Schema__Comprehend__Detect_Dominant_Language                  import Schema__Comprehend__Detect_Dominant_Language
from osbot_aws.aws.comprehend.schemas.Schema__Comprehend__Detect_Pii_Entities                       import Schema__Comprehend__Detect_Pii_Entities
from osbot_aws.aws.comprehend.schemas.Schema__Comprehend__Detect_Syntax                             import Schema__Comprehend__Detect_Syntax
from osbot_aws.aws.comprehend.schemas.Schema__Comprehend__Detect_Toxic_Content                      import Schema__Comprehend__Detect_Toxic_Content
from osbot_aws.aws.comprehend.schemas.enums.Enum__Comprehend__Entity_Type                           import Enum__Comprehend__Entity_Type
from osbot_aws.aws.comprehend.schemas.enums.Enum__Comprehend__Language_Code                         import Enum__Comprehend__Language_Code
from osbot_aws.aws.comprehend.schemas.enums.Enum__Comprehend__Part_Of_Speech_Tag                    import Enum__Comprehend__Part_Of_Speech_Tag
from osbot_aws.aws.comprehend.schemas.enums.Enum__Comprehend__Toxic_Content_Label                   import Enum__Comprehend__Toxic_Content_Label
from osbot_utils.type_safe.Type_Safe                                                                import Type_Safe
from osbot_utils.utils.Objects                                                                      import type_full_name, base_types
from osbot_aws.aws.comprehend.schemas.enums.Enum__Comprehend__Detect_Sentiment__Sentiment           import Enum__Comprehend__Detect_Sentiment__Sentiment
from osbot_aws.aws.comprehend.schemas.safe_str.Safe_Str__AWS_Comprehend__Text                       import Safe_Str__Comprehend__Text


class test_Comprehend(TestCase):

    @classmethod
    def setUpClass(cls):
        if in_github_action():
            pytest.skip("Doesn't work when running all tests")              # todo: fix issue caused by the use of localstack has a target
        cls.comprehend = Comprehend__with_temp_role()

    def test__init__(self):
        with self.comprehend as _:
            assert type(_) is Comprehend__with_temp_role
            assert base_types(_) == [Comprehend, Type_Safe, object]

    def test_client(self):
        with self.comprehend as _:
            client = _.client()
            assert type_full_name(client) == 'botocore.client.Comprehend'

    # ============================================================================
    # SENTIMENT DETECTION TESTS
    # ============================================================================

    def test_detect_sentiment(self):                                                        # Validate AWS Comprehend sentiment detection
        with self.comprehend as _:
            result = _.detect_sentiment('Hello World')
            assert type(result) is Schema__Comprehend__Detect_Sentiment

            result.print_obj()
            assert result.obj() == __(duration  = __LESS_THAN__(0.5)                ,
                                      sentiment = 'Positive'                         ,
                                      score     = __(mixed    = __CLOSE_TO__(0.001 , tolerance=0.0005) ,   # 0.0010159355588257313     ,
                                                     negative = __CLOSE_TO__(0.001 , tolerance=0.001 ) ,   # 0.0015335445059463382
                                                     neutral  = __CLOSE_TO__(0.424 , tolerance=0.01  ) ,   # 0.42408183217048645
                                                     positive = __CLOSE_TO__(0.573 , tolerance=0.01  ) ))  # 0.5733687281608582


    def test_detect_sentiment__type_conversion(self):                                      # Test auto-conversion of raw types
        with self.comprehend as _:
            result = _.detect_sentiment('test text')
            assert type(result.sentiment) is Enum__Comprehend__Detect_Sentiment__Sentiment
            assert type(result.score.positive) is Safe_Float__Probability_Score
            assert result.sentiment   == 'Neutral'
            assert result.score.obj() == __(mixed    = __BETWEEN__(0.0, 0.1),           # 0.03685488551855087
                                            negative = __BETWEEN__(0.0, 0.1),           # 0.01417419034987688
                                            neutral  = __BETWEEN__(0.9, 1.0),           # 0.9331376552581787
                                            positive = __BETWEEN__(0.0, 0.1))           # 0.0158331710845232

    def test_detect_sentiment__negative(self):                                             # Test detection of negative sentiment
        with self.comprehend as _:
            text   = 'This is terrible and awful'
            result = _.detect_sentiment(text=text)

            assert result.sentiment == Enum__Comprehend__Detect_Sentiment__Sentiment.NEGATIVE
            assert result.obj()     == __(sentiment = 'Negative',
                                          score     = __(mixed    = __CLOSE_TO__(0.000, tolerance=0.001)  , #1.9338171114213765e-05,
                                                         negative = __CLOSE_TO__(0.999, tolerance=0.001)  , #0.9996902942657471,
                                                         neutral  = __CLOSE_TO__(0.000, tolerance=0.001)  , #0.00021977175492793322,
                                                         positive = __CLOSE_TO__(0.000, tolerance=0.001)) , #7.066388207022101e-05),
                                          duration  = __SKIP__    )

    def test_detect_sentiment__with_language_code(self):                                   # Test sentiment detection with explicit language code
        with self.comprehend as _:
            result = _.detect_sentiment('Hola mundo', language_code=Enum__Comprehend__Language_Code.SPANISH)
            assert type(result)     is Schema__Comprehend__Detect_Sentiment
            assert result.sentiment == 'Neutral'
            assert result.obj().contains(__(duration = __LESS_THAN__(0.5)))

    # ============================================================================
    # KEY PHRASES DETECTION TESTS
    # ============================================================================

    def test_detect_key_phrases(self):                                                     # Test extraction of key phrases from text
        with self.comprehend as _:
            text   = "AWS Lambda is a serverless compute service that runs code in response to events."
            result = _.detect_key_phrases(text)

            assert type(result) == Schema__Comprehend__Detect_Key_Phrases
            assert result.obj() == __(key_phrases = [__(text         = 'AWS Lambda'                   ,
                                                        score        = 0.9999691843986511             ,
                                                        begin_offset = 0                              ,
                                                        end_offset   = 10                             ) ,
                                                     __(text         = 'a serverless compute service' ,
                                                        score        = 0.999631941318512              ,
                                                        begin_offset = 14                             ,
                                                        end_offset   = 42                             ),
                                                     __(text         = 'code'                          ,
                                                        score        = 0.9999337196350098              ,
                                                        begin_offset = 53                              ,
                                                        end_offset   = 57                              ),
                                                     __(text         = 'response'                      ,
                                                        score        = 0.9999071359634399              ,
                                                        begin_offset = 61                              ,
                                                        end_offset   = 69                              ),
                                                     __(text         = 'events'                        ,
                                                        score        = 0.9999898672103882              ,
                                                        begin_offset = 73                              ,
                                                        end_offset   = 79                              )],
                                      duration    = __SKIP__                                            )


    def test_detect_key_phrases__simple_text(self):                                        # Test key phrase detection with simple text
        with self.comprehend as _:
            result = _.detect_key_phrases("The quick brown fox jumps over the lazy dog.")
            assert type(result)            is Schema__Comprehend__Detect_Key_Phrases
            assert result.obj()            == __(key_phrases = [__(text         = 'The quick brown fox'     ,
                                                                  score        = __GREATER_THAN__(0.9)      ,        # 0.999984085559845
                                                                  begin_offset = 0                          ,
                                                                  end_offset   = 19                         ) ,
                                                               __(text         = 'the lazy dog'             ,
                                                                  score        = __GREATER_THAN__(0.9)      ,        # 0.9999595880508423
                                                                  begin_offset = 31                         ,
                                                                  end_offset   = 43                         )] ,
                                                duration     = __SKIP__                                       )



            phrases_text = [phrase.text for phrase in result.key_phrases]

            assert phrases_text == [ Safe_Str__Comprehend__Text('The quick brown fox'),
                                     Safe_Str__Comprehend__Text('the lazy dog'       )]

    # ============================================================================
    # ENTITY DETECTION TESTS
    # ============================================================================

    def test_detect_entities(self):                                                        # Test named entity recognition (NER)
        with self.comprehend as _:
            text   = "Amazon Web Services was founded by Jeff Bezos in Seattle, Washington in 2006."
            result = _.detect_entities(text)

            assert type(result)   is Schema__Comprehend__Detect_Entities
            assert result.obj()   == __(entities = [__(text         = 'Amazon Web Services'     ,
                                                       type         = 'ORGANIZATION'            ,
                                                       score        = __GREATER_THAN__(0.9)     ,    # 0.9937301278114319
                                                       begin_offset = 0                         ,
                                                       end_offset   = 19                        ) ,
                                                    __(text         = 'Jeff Bezos'              ,
                                                       type         = 'PERSON'                  ,
                                                       score        = __GREATER_THAN__(0.9)     ,    # 0.9987561702728271
                                                       begin_offset = 35                        ,
                                                       end_offset   = 45                        ) ,
                                                    __(text         = 'Seattle, Washington'     ,
                                                       type         = 'LOCATION'                ,
                                                       score        = __GREATER_THAN__(0.9)     ,    # 0.9910624027252197
                                                       begin_offset = 49                        ,
                                                       end_offset   = 68                        ) ,
                                                    __(text         = '2006'                    ,
                                                       type         = 'DATE'                    ,
                                                       score        = __GREATER_THAN__(0.9)     ,    # 0.9991124272346497
                                                       begin_offset = 72                        ,
                                                       end_offset   = 76                        )] ,
                                        duration = __SKIP__                                        )


    def test_detect_entities__locations(self):                                             # Test detection of location entities
        with self.comprehend as _:
            text      = "I traveled from Paris to Tokyo through London."
            result    = _.detect_entities(text)

            assert result.obj() == __(entities = [__( text         = 'Paris'                  ,
                                                      type         = 'LOCATION'               ,
                                                      score        = __GREATER_THAN__(0.9)    ,    # 0.9988693594932556
                                                      begin_offset = 16                       ,
                                                      end_offset   = 21                       ) ,
                                                   __(text         = 'Tokyo'                  ,
                                                      type         = 'LOCATION'               ,
                                                      score        = __GREATER_THAN__(0.9)    ,    # 0.9982354640960693
                                                      begin_offset = 25                       ,
                                                      end_offset   = 30                       ) ,
                                                   __(text         = 'London'                 ,
                                                      type         = 'LOCATION'               ,
                                                      score        = __GREATER_THAN__(0.9)    ,    # 0.9975361824035645
                                                      begin_offset = 39                       ,
                                                      end_offset   = 45                       )] ,
                                       duration = __SKIP__                                       )


    def test_detect_entities__dates_and_quantities(self):                                  # Test detection of dates and quantities
        with self.comprehend as _:
            text         = "On January 15, 2024, we sold 100 units for $50 each."
            result       = _.detect_entities(text)

            assert result.obj() == __(entities = [__( text         = 'January 15, 2024'        ,
                                                      type         = 'DATE'                    ,
                                                      score        = __GREATER_THAN__(0.9)     ,    # 0.9990227222442627
                                                      begin_offset = 3                         ,
                                                      end_offset   = 19                        ) ,
                                                   __(text         = '100 units'               ,
                                                      type         = 'QUANTITY'                ,
                                                      score        = __GREATER_THAN__(0.9)     ,    # 0.998943030834198
                                                      begin_offset = 29                        ,
                                                      end_offset   = 38                        ) ,
                                                   __(text         = '$50 each'                ,
                                                      type         = 'QUANTITY'                ,
                                                      score        = __GREATER_THAN__(0.9)     ,    # 0.9567936062812805
                                                      begin_offset = 43                        ,
                                                      end_offset   = 51                        )] ,
                                       duration = __SKIP__                                      )


            entity_types = {e.type for e in result.entities}

            assert Enum__Comprehend__Entity_Type.DATE     in entity_types or \
                   Enum__Comprehend__Entity_Type.QUANTITY in entity_types

    # ============================================================================
    # DOMINANT LANGUAGE DETECTION TESTS
    # ============================================================================

    def test_detect_dominant_language(self):                                               # Test automatic language detection
        with self.comprehend as _:
            result = _.detect_dominant_language("Hello World")

            assert type(result)  is Schema__Comprehend__Detect_Dominant_Language

            assert result.obj()  == __(languages = [__(language_code = 'en'                    ,
                                                       score         = __GREATER_THAN__(0.9) )],   # 0.9798225164413452
                                       duration  = __SKIP__                                    )


    def test_detect_dominant_language__spanish(self):                                      # Test language detection for Spanish text
        with self.comprehend as _:
            result = _.detect_dominant_language("Hola mundo, ¿cómo estás?")

            assert type(result)                      is Schema__Comprehend__Detect_Dominant_Language
            assert result.languages[0].language_code == Enum__Comprehend__Language_Code.SPANISH
            assert result.obj()                      == __(languages = [__(language_code = 'es'                   ,
                                                                           score         = __GREATER_THAN__(0.9) )],    # 0.9850438237190247
                                                           duration  = __SKIP__                                    )



    def test_detect_dominant_language__french(self):                                       # Test language detection for French text
        with self.comprehend as _:
            result         = _.detect_dominant_language("Bonjour le monde, comment allez-vous?")
            first_language = result.languages[0]

            assert result.obj() == __(languages = [__(language_code = 'fr'                  ,
                                                      score         = __GREATER_THAN__(0.9) ,    # 0.9459766149520874
                                                     )]                                      ,
                                      duration  = __SKIP__                                    )




            assert first_language.language_code == Enum__Comprehend__Language_Code.FRENCH
            assert first_language.score          > 0.8

    def test_detect_dominant_language__multi_candidate(self):                              # Test language detection returns multiple candidates sorted by confidence
        with self.comprehend as _:
            result = _.detect_dominant_language("Hola my friend, como estas today?")
            assert result.obj() == __(languages = [ __(language_code = 'en'                    ,
                                                       score         = __GREATER_THAN__(0.8))  ,    # 0.8779959082603455
                                                    __(language_code = 'es'                    ,
                                                       score         = __GREATER_THAN__(0.1))] ,    # 0.11907429248094559
                                       duration  = __SKIP__                                    )


    # ============================================================================
    # PII DETECTION TESTS
    # ============================================================================

    def test_detect_pii_entities(self):                                                    # Test PII detection for privacy compliance
        with self.comprehend as _:
            text   = "My email is john.doe@example.com and my phone is 555-1234."
            result = _.detect_pii_entities(text)

            assert type(result)    is Schema__Comprehend__Detect_Pii_Entities

            assert result.obj() == __(entities = [__( type         = 'EMAIL' ,
                                                      score        = __GREATER_THAN__(0.9) ,
                                                      begin_offset = 12                    ,
                                                      end_offset   = 32                    ),
                                                   __(type         = 'PHONE' ,
                                                      score        = __GREATER_THAN__(0.9) ,
                                                      begin_offset = 49                    ,
                                                      end_offset   = 57                    )],
                                       duration = __SKIP__)




    def test_detect_pii_entities__financial_info(self):                                    # Test detection of financial PII
        with self.comprehend as _:
            text   = "Credit card: 4532-1234-5678-9010"
            result = _.detect_pii_entities(text)

            assert type(result) is Schema__Comprehend__Detect_Pii_Entities
            assert result.obj() == __(entities = [__( type         = 'CREDIT_DEBIT_NUMBER' ,
                                                      score        = __GREATER_THAN__(0.9) ,      # 0.9998716115951538
                                                      begin_offset = 13                    ,
                                                      end_offset   = 32                    )],
                                       duration = __SKIP__)

    def test_detect_pii_entities__ssn(self):                                               # Test detection of SSN
        with self.comprehend as _:
            text   = "My SSN is 123-45-6789"
            result = _.detect_pii_entities(text)

            assert type(result) is Schema__Comprehend__Detect_Pii_Entities
            if len(result.entities) > 0:
                entity_types = {e.type for e in result.entities}
                assert len(entity_types) > 0

            assert result.obj() == __(entities = [__( type         = 'SSN' ,
                                                      score        = __GREATER_THAN__(0.9) ,      # 0.999262273311615
                                                      begin_offset = 10                 ,
                                                      end_offset   = 21                 )],
                                       duration = __SKIP__)


    def test_detect_pii_entities__no_pii(self):                                            # Test text with no PII returns empty list
        with self.comprehend as _:
            text   = "The weather is nice today."
            result = _.detect_pii_entities(text)

            assert type(result)         is Schema__Comprehend__Detect_Pii_Entities
            assert len(result.entities) == 0

            assert result.obj() == __(entities = []      ,
                                      duration = __SKIP__)

    # ============================================================================
    # SYNTAX DETECTION TESTS
    # ============================================================================

    def test_detect_syntax(self):                                                          # Test part-of-speech tagging
        with self.comprehend as _:
            text   = "The quick brown fox jumps."
            result = _.detect_syntax(text)

            assert type(result)  is Schema__Comprehend__Detect_Syntax

            assert result.obj()  == __(syntax_tokens = [__(text          = 'The'  ,
                                                           token_id      = 1      ,
                                                           begin_offset  = 0      ,
                                                           end_offset    = 3      ,
                                                           part_of_speech = __(tag   = 'DET' ,
                                                                                score = __GREATER_THAN__(0.9))) ,      # 1.0

                                                         __(text          = 'quick' ,
                                                           token_id      = 2       ,
                                                           begin_offset  = 4       ,
                                                           end_offset    = 9       ,
                                                           part_of_speech = __(tag   = 'ADJ' ,
                                                                                score = __GREATER_THAN__(0.9))) ,      # 1.0

                                                         __(text          = 'brown' ,
                                                           token_id      = 3       ,
                                                           begin_offset  = 10      ,
                                                           end_offset    = 15      ,
                                                           part_of_speech = __(tag   = 'ADJ' ,
                                                                                score = __GREATER_THAN__(0.9))) ,      # 1.0

                                                         __(text          = 'fox'  ,
                                                           token_id      = 4      ,
                                                           begin_offset  = 16     ,
                                                           end_offset    = 19     ,
                                                           part_of_speech = __(tag   = 'NOUN' ,
                                                                                score = __GREATER_THAN__(0.99))) ,     # 0.9999991655349731

                                                         __(text          = 'jumps' ,
                                                           token_id      = 5       ,
                                                           begin_offset  = 20      ,
                                                           end_offset    = 25      ,
                                                           part_of_speech = __(tag   = 'VERB' ,
                                                                                score = __GREATER_THAN__(0.9))) ,      # 1.0

                                                         __(text          = '.'  ,
                                                           token_id      = 6     ,
                                                           begin_offset  = 25    ,
                                                           end_offset    = 26    ,
                                                           part_of_speech = __(tag   = 'PUNCT' ,
                                                                                score = __GREATER_THAN__(0.9)))] ,     # 1.0
                                       duration      = __SKIP__)


            for token in result.syntax_tokens:
                assert hasattr(token, 'text')
                assert hasattr(token, 'token_id')
                assert hasattr(token, 'part_of_speech')
                assert type(token.part_of_speech.tag) is Enum__Comprehend__Part_Of_Speech_Tag

    def test_detect_syntax__pos_tags(self):                                                # Test that common POS tags are detected correctly
        with self.comprehend as _:
            text     = "The cat sleeps quietly."
            result   = _.detect_syntax(text)
            pos_tags = [token.part_of_speech.tag for token   in result.syntax_tokens]

            assert Enum__Comprehend__Part_Of_Speech_Tag.DET  in pos_tags  or \
                   Enum__Comprehend__Part_Of_Speech_Tag.NOUN in pos_tags or \
                   Enum__Comprehend__Part_Of_Speech_Tag.VERB in pos_tags

            assert result.obj() == __(syntax_tokens = [__( text           = 'The'  ,
                                                           token_id       = 1      ,
                                                           begin_offset   = 0      ,
                                                           end_offset     = 3      ,
                                                           part_of_speech = __(tag   = 'DET' ,
                                                                                score = __GREATER_THAN__(0.9))) ,      # 1.0

                                                         __(text           = 'cat'  ,
                                                           token_id       = 2      ,
                                                           begin_offset   = 4      ,
                                                           end_offset     = 7      ,
                                                           part_of_speech = __(tag   = 'NOUN' ,
                                                                                score = __GREATER_THAN__(0.9))) ,      # 1.0

                                                         __(text           = 'sleeps' ,
                                                           token_id       = 3       ,
                                                           begin_offset   = 8       ,
                                                           end_offset     = 14      ,
                                                           part_of_speech = __(tag   = 'VERB' ,
                                                                                score = __GREATER_THAN__(0.9))) ,      # 1.0

                                                         __(text           = 'quietly' ,
                                                           token_id       = 4        ,
                                                           begin_offset   = 15       ,
                                                           end_offset     = 22       ,
                                                           part_of_speech = __(tag   = 'ADV' ,
                                                                                score = __GREATER_THAN__(0.9))) ,      # 1.0

                                                         __(text           = '.'  ,
                                                           token_id       = 5     ,
                                                           begin_offset   = 22    ,
                                                           end_offset     = 23    ,
                                                           part_of_speech = __(tag   = 'PUNCT' ,
                                                                                score = __GREATER_THAN__(0.9)))] ,     # 1.0
                                       duration       = __SKIP__)


    def test_detect_syntax__token_offsets(self):                                           # Test that token offsets are correct
        with self.comprehend as _:
            text   = "Hello world"
            result = _.detect_syntax(text)

            for token in result.syntax_tokens:
                assert token.begin_offset < token.end_offset
                assert token.end_offset <= len(text)
                extracted = text[token.begin_offset:token.end_offset]
                assert extracted.lower() == token.text.lower() or \
                       extracted.lower().startswith(token.text.lower())

            assert result.obj() == __(syntax_tokens = [__( text           = 'Hello' ,
                                                           token_id       = 1       ,
                                                           begin_offset   = 0       ,
                                                           end_offset     = 5       ,
                                                           part_of_speech = __(tag   = 'VERB' ,
                                                                                score = __GREATER_THAN__(0.9))) ,      # 0.9362348318099976

                                                         __(text           = 'world' ,
                                                           token_id       = 2       ,
                                                           begin_offset   = 6       ,
                                                           end_offset     = 11      ,
                                                           part_of_speech = __(tag   = 'NOUN' ,
                                                                                score = __GREATER_THAN__(0.9)))] ,     # 1.0
                                       duration       = __SKIP__)



    # ============================================================================
    # TOXIC CONTENT DETECTION TESTS
    # ============================================================================

    def test_detect_toxic_content(self):                                                   # Test toxic content detection for content moderation
        with self.comprehend as _:
            text   = "You are an doughnut and I don't like you."
            result = _.detect_toxic_content(text)

            assert type(result)    is Schema__Comprehend__Detect_Toxic_Content

            assert result.obj() == __(labels   = [ __(name  = 'PROFANITY'            ,
                                                      score = __GREATER_THAN__(0.2)  ) ,     # 0.27570000290870667

                                                   __(name  = 'HATE_SPEECH'         ,
                                                      score = __GREATER_THAN__(0.1)  ) ,     # 0.1979999989271164

                                                   __(name  = 'INSULT'              ,
                                                      score = __GREATER_THAN__(0.9)  ) ,     # 0.9319999814033508

                                                   __(name  = 'GRAPHIC'             ,
                                                      score = __GREATER_THAN__(0.0)  ) ,     # 0.019500000402331352

                                                   __(name  = 'HARASSMENT_OR_ABUSE' ,
                                                      score = __GREATER_THAN__(0.1)  ) ,     # 0.1590999960899353

                                                   __(name  = 'SEXUAL'              ,
                                                      score = __GREATER_THAN__(0.1)  ) ,     # 0.13590000569820404

                                                   __(name  = 'VIOLENCE_OR_THREAT'  ,
                                                      score = __GREATER_THAN__(0.0))] ,      # 0.040699999779462814
                                       duration = __SKIP__)


            if len(result.labels) > 0:
                for label in result.labels:
                    assert type(label.name) is Enum__Comprehend__Toxic_Content_Label

    def test_detect_toxic_content__clean_text(self):                                       # Test that clean text has low/no toxicity scores
        with self.comprehend as _:
            text   = "The weather is beautiful today. I hope you have a great day!"
            result = _.detect_toxic_content(text)

            assert type(result) is Schema__Comprehend__Detect_Toxic_Content
            assert result.obj() == __(labels   = [__( name  = 'PROFANITY'            ,
                                                      score = __GREATER_THAN__(0.05) ) ,      # 0.06040000170469284

                                                     __(name  = 'HATE_SPEECH'         ,
                                                      score = __GREATER_THAN__(0.07) ) ,      # 0.07970000058412552

                                                     __(name  = 'INSULT'              ,
                                                      score = __GREATER_THAN__(0.08) ) ,      # 0.0908999964594841

                                                     __(name  = 'GRAPHIC'             ,
                                                      score = __GREATER_THAN__(0.05) ) ,      # 0.05389999970793724

                                                     __(name  = 'HARASSMENT_OR_ABUSE' ,
                                                      score = __GREATER_THAN__(0.1)  ) ,      # 0.1111999973654747

                                                     __(name  = 'SEXUAL'              ,
                                                      score = __GREATER_THAN__(0.3)  ) ,      # 0.3215000033378601

                                                     __(name  = 'VIOLENCE_OR_THREAT'  ,
                                                      score = __GREATER_THAN__(0.04))] ,      # 0.040699999779462814
                                       duration = __SKIP__)


            if len(result.labels) > 0:
                high_confidence_toxic = [l for l in result.labels if l.score > 0.5]
                assert len(high_confidence_toxic) == 0

    def test_detect_toxic_content__profanity(self):                                        # Test detection of profanity
        with self.comprehend as _:
            text   = "This is absolutely cr*p."
            result = _.detect_toxic_content(text)

            assert result.obj() == __(labels   = [__(name  = 'PROFANITY'            ,
                                                  score = __GREATER_THAN__(0.4) ) ,      # 0.41110000014305115

                                                 __(name  = 'HATE_SPEECH'         ,
                                                  score = __GREATER_THAN__(0.1) ) ,      # 0.17090000212192535

                                                 __(name  = 'INSULT'              ,
                                                  score = __GREATER_THAN__(0.5) ) ,      # 0.5311999917030334

                                                 __(name  = 'GRAPHIC'             ,
                                                  score = __GREATER_THAN__(0.05)) ,      # 0.05389999970793724

                                                 __(name  = 'HARASSMENT_OR_ABUSE' ,
                                                  score = __GREATER_THAN__(0.1) ) ,      # 0.13819999992847443

                                                 __(name  = 'SEXUAL'              ,
                                                  score = __GREATER_THAN__(0.29)) ,      # 0.2994999885559082

                                                 __(name  = 'VIOLENCE_OR_THREAT'  ,
                                                  score = __GREATER_THAN__(0.04))] ,     # 0.040699999779462814
                                   duration = __SKIP__)


            assert type(result) is Schema__Comprehend__Detect_Toxic_Content

    # ============================================================================
    # EDGE CASES AND ERROR HANDLING
    # ============================================================================

    def test_detect_sentiment__empty_like_text(self):                                      # Test handling of minimal text
        with self.comprehend as _:
            result = _.detect_sentiment("Hi")
            assert type(result) is Schema__Comprehend__Detect_Sentiment

    def test_detect_key_phrases__single_word(self):                                        # Test key phrase detection with single word
        with self.comprehend as _:
            result = _.detect_key_phrases("Hello")
            assert type(result) is Schema__Comprehend__Detect_Key_Phrases

    def test_detect_entities__no_entities(self):                                           # Test entity detection with text containing no named entities
        with self.comprehend as _:
            text   = "It was nice."
            result = _.detect_entities(text)
            assert type(result) is Schema__Comprehend__Detect_Entities

    def test_multiple_operations_on_same_text(self):                                       # Test running multiple operations on the same text
        with self.comprehend as _:
            text = "Amazon was founded by Jeff Bezos in Seattle."

            sentiment_result = _.detect_sentiment(text)
            entities_result  = _.detect_entities(text)
            phrases_result   = _.detect_key_phrases(text)
            language_result  = _.detect_dominant_language(text)

            assert type(sentiment_result) is Schema__Comprehend__Detect_Sentiment
            assert type(entities_result)  is Schema__Comprehend__Detect_Entities
            assert type(phrases_result)   is Schema__Comprehend__Detect_Key_Phrases
            assert type(language_result)  is Schema__Comprehend__Detect_Dominant_Language