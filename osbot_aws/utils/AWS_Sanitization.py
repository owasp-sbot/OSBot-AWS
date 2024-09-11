import re


def str_to_valid_s3_bucket_name(value):

    s3_bucket_name = re.sub(r'[^a-z0-9-]', '', value.lower()).strip('.-')     # Replace invalid characters with a hyphen and ensure the name does not start or end with invalid characters

    if s3_bucket_name.endswith('-'):
        s3_bucket_name = s3_bucket_name[:-1]                    # Remove trailing hyphen if present
    if not s3_bucket_name:
        raise ValueError(f"[osbot_aws.utils.AWS_Sanitization] in str_to_valid_s3_bucket_name, could not create a valid name from: {value}")
    return s3_bucket_name
