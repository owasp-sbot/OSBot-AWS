from enum import Enum, auto

from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self

# class Sqlite__Bedrock__Row__Type:
#     UNIT_TEST   = 'unit_test'
#     DEV_REQUEST = 'dev_request'
#     CI_REQUEST  = 'ci_request'
#     UNDEFINED   = 'undefined'


class Sqlite__Bedrock__Row(Kwargs_To_Self):
    request_hash  : str
    request_data  : str
    response_hash : str
    response_data : str
    cache_hits    : int
    timestamp     : int
    latest        : bool
    comments      : str
    #record_type   : str  = Sqlite__Bedrock__Row__Type.UNDEFINED     # todo: see if this is really needed