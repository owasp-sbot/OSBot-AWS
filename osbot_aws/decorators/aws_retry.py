# from functools import wraps
#
#
# class aws_retry:
#
#     """retries the call (required for some cases where data is not consistent yet in AWS"""
#     def __init__(self, fields):
#         self.fields = fields                                        # field to inject
#
#     def __call__(self, function):
#         pass
#         #code from aws_inject
#         # from osbot_aws.AWS_Config import AWS_Config
#         # @wraps(function)                                            # makes __name__ work ok
#         # def wrapper(*args,**kwargs):                                # wrapper function
#         #     for field in self.fields.split(','):                    # split value provided by comma
#         #         if field == 'region'    : kwargs[field] = AWS_Config().aws_session_region_name()
#         #         if field == 'account_id': kwargs[field] = AWS_Config().aws_session_account_id()
#         #     return function(*args,**kwargs)
#         #return wrapper