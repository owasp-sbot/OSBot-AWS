import re
import botocore
from botocore.exceptions import ClientError, ParamValidationError
from functools import wraps
from osbot_utils.utils.Dev import pprint

class Capture_Boto3_Error:
    def __init__(self):
        self.error_details = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val:                                                              # Check if an exception occurred
            if isinstance(exc_val, ClientError):                                # If it's a Boto3 ClientError, process it
                self.process_client_error(exc_val)
                return True
            elif isinstance(exc_val, ParamValidationError):                     # If it's a Boto3 ParamValidationError, process it
                self.process_param_validation_error(exc_val)
                return True
        return False  # Return False to allow any exceptions not handled here to propagate

    def process_client_error(self, exc_val):
        error_code = exc_val.response['Error']['Code']
        error_message = exc_val.response['Error']['Message']

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

    def process_param_validation_error(self, exc_val):
        # Here you can parse exc_val's report attribute if needed
        error_message = str(exc_val)
        self.error_details = {
            'error_code': 'ParamValidationError',
            'error_message': error_message
        }

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
            try:
                return_value = func(*args, **kwargs)
            except Exception as e:
                raise e
        if error_capture.error_details:
            print()
            pprint('****** BOTO3 ERROR DETECTED ******')
            pprint(error_capture.error_details)
        return return_value

    return wrapper
