from unittest import TestCase

from osbot_aws.utils.AWS_Sanitization import str_to_valid_s3_bucket_name


class test_AWS_Sanitization(TestCase):
    def test_str_to_valid_s3_bucket_name(self):
        assert str_to_valid_s3_bucket_name('valid-bucket-name'    ) == 'valid-bucket-name'     # Use case 1: Valid bucket name remains the same
        assert str_to_valid_s3_bucket_name('ValidBucketName'      ) == 'validbucketname'       # Use case 2: Uppercase characters converted to lowercase
        assert str_to_valid_s3_bucket_name('Invalid_Bucket@Name!' ) == 'invalidbucketname'     # Use case 3: Invalid characters removed
        assert str_to_valid_s3_bucket_name('.invalid.bucket.name-') == 'invalidbucketname'     # Use case 4: Leading and trailing dots or hyphens removed
        assert str_to_valid_s3_bucket_name('invalid..bucket--name') == 'invalidbucket--name'   # Use case 5: Dots removed but double hyphen remains

        try:                                                                                   # Use case 6: Empty string should raise ValueError
            str_to_valid_s3_bucket_name('')
        except ValueError as e:
            assert str(e) == "[osbot_aws.utils.AWS_Sanitization] in str_to_valid_s3_bucket_name, could not create a valid name from: "  # Verify that the correct error message is raised

        try:                                                                                    # Use case 7: Name with only invalid characters should raise ValueError
            str_to_valid_s3_bucket_name('@#$%^&')
        except ValueError as e:
            assert str(e) == "[osbot_aws.utils.AWS_Sanitization] in str_to_valid_s3_bucket_name, could not create a valid name from: @#$%^&"  # Verify that the correct error message is raised
