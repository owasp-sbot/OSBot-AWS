from unittest                                                                    import TestCase

import pytest

from osbot_aws.aws.comprehend.schemas.safe_str.Safe_Str__RFC_5646__Language_Code import Safe_Str__RFC_5646__Language_Code


class test_Safe_Str__RFC_5646__Language_Code(TestCase):      # Test that Safe_Str accepts any valid RFC 5646 language code

    def test__valid_2_letter_codes(self):                                       # Test standard 2-letter ISO 639-1 codes
        assert Safe_Str__RFC_5646__Language_Code('en')   == 'en'                 # English
        assert Safe_Str__RFC_5646__Language_Code('lo')   == 'lo'                 # Lao (not in analysis enum)
        assert Safe_Str__RFC_5646__Language_Code('my')   == 'my'                 # Burmese (not in analysis enum)
        assert Safe_Str__RFC_5646__Language_Code('km')   == 'km'                 # Khmer (not in analysis enum)
        assert Safe_Str__RFC_5646__Language_Code('es')   == 'es'                 # Spanish
        assert Safe_Str__RFC_5646__Language_Code('fr')   == 'fr'                 # French

    def test__valid_3_letter_codes(self):                                       # Test 3-letter ISO 639-2 codes
        assert Safe_Str__RFC_5646__Language_Code('eng') == 'eng'                 # English (3-letter form)
        assert Safe_Str__RFC_5646__Language_Code('spa') == 'spa'                 # Spanish (3-letter form)

    def test__valid_codes_with_region(self):                                    # Test codes with regional subtags
        assert Safe_Str__RFC_5646__Language_Code('en-US')  == 'en-US'            # US English
        assert Safe_Str__RFC_5646__Language_Code('en-GB')  == 'en-GB'            # British English
        assert Safe_Str__RFC_5646__Language_Code('zh-TW')  == 'zh-TW'            # Traditional Chinese
        assert Safe_Str__RFC_5646__Language_Code('pt-BR')  == 'pt-BR'            # Brazilian Portuguese

    def test__valid_codes_with_script(self):                                    # Test codes with script subtags
        assert Safe_Str__RFC_5646__Language_Code('zh-Hans') == 'zh-Hans'         # Simplified Chinese
        assert Safe_Str__RFC_5646__Language_Code('zh-Hant') == 'zh-Hant'         # Traditional Chinese

    def test__invalid_codes(self):                                              # Test that invalid codes are rejected
        with pytest.raises(ValueError):
            Safe_Str__RFC_5646__Language_Code('e')                               # Too short
        
        with pytest.raises(ValueError):
            Safe_Str__RFC_5646__Language_Code('english')                         # Too long for base code
        
        with pytest.raises(ValueError):
            Safe_Str__RFC_5646__Language_Code('en_US')                           # Invalid separator (underscore)
        
        with pytest.raises(ValueError):
            Safe_Str__RFC_5646__Language_Code('123')    