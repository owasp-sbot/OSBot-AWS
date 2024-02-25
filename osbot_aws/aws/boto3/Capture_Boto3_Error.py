import re
import botocore
from botocore.exceptions import ClientError
from functools import wraps
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Objects import obj_info


class Capture_Boto3_Error:
    error_details: dict

    def __enter__(self):
        # Initialize or reset error details
        self.error_details = None
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Check if an exception occurred
        if exc_val:
            # If it's a Boto3 ClientError, process it
            #if isinstance(exc_val, botocore.exceptions.ClientError):
            if isinstance(exc_val, ClientError):
                error_code = exc_val.response['Error']['Code']
                error_message = exc_val.response['Error']['Message']

                # Handle specific error types here, e.g., ValidationException
                if error_code == 'ValidationException':
                    self.error_details = {
                        'error_code': error_code,
                        'error_message': error_message,
                        'details': self.extract_validation_details(error_message)
                    }
                else:
                    self.error_details = {
                        'error_code': error_code,
                        'error_message': error_message
                    }
                # Return True to prevent the exception from propagating
                return True
        # Return False to allow any exceptions not handled here to propagate
        return False

    @staticmethod
    def extract_validation_details(error_message):
        # Implement logic to extract details from the ValidationException message
        details_match = re.search(r"An error occurred \(ValidationException\) when calling the (.+) operation: (.+)", error_message)
        if details_match:
            operation, detail_message = details_match.groups()
            return {'operation': operation, 'detail_message': detail_message}
        return {'error_message': error_message}

def capture_boto3_error(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return_value = None
        with Capture_Boto3_Error() as error_capture:
            return_value = func(*args, **kwargs)

        if error_capture.error_details:
            print()
            pprint('****** BOTO3 ERROR DETECTED ******')
            pprint(error_capture.error_details)
        return return_value

    return wrapper
