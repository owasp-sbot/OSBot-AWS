import re
from functools                               import wraps
from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self
from osbot_utils.utils.Dev                   import pprint


def capture_iam_exception(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return_value = None
        with Capture_IAM_Exception() as _:
            return_value = func(*args, **kwargs)
        if _.permission_required.get('status')=='ok':
            print()
            pprint('****** IAM PERMISSION REQUIRED ******')
            del _.permission_required['status']                         # this value can be consuming
            pprint(_.permission_required)
        return return_value

    return wrapper

class Capture_IAM_Exception(Kwargs_To_Self):
    permission_required : dict

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.permission_required = { 'event'     : 'no IAM exception triggered' ,
                                     'status'    : 'error'                  }
        # pprint(exc_type)
        # if exc_type is ClientError:
        if exc_val:
            error_code = exc_val.response.get('Error', {}).get('Code')
            if error_code == 'AccessDeniedException':
                error_message = exc_val.response['Error']['Message']

                user_arn_match = re.search(r"User: arn:aws:iam::(\d+):user/([^ ]+) is not authorized", error_message)
                required_permission_match = re.search(r"because no identity-based policy allows the ([^:]+):([^ ]+) action", error_message)

                if user_arn_match and required_permission_match:
                    account_id, user = user_arn_match.groups()
                    service, action = required_permission_match.groups()

                    self.permission_required = { 'event'     : 'IAM exception triggered' ,
                                                 'status'    : 'ok'                      ,
                                                 'service'   : service                   ,
                                                 'action'    : action                    ,
                                                 'account_id': account_id                ,
                                                 'user'      : user                      }

                return True
        return False
