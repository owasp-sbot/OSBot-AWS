from osbot_aws.utils.Version import Version, version
from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self
from osbot_utils.utils.Misc import date_time_now


class WS__Connection(Kwargs_To_Self):
    # auto populated
    id                  : str  # to be set by Dynamo_DB__Table
    timestamp           : int  # to be set by the request
    version             : str  # set in __init__

    # indexes
    date                : str          # also populated in __init__
    status              : str = 'NA'

    # other fields
    env                 : str
    events              : list
    timestamp_disconnect: int

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.date    = self.date_today()   # make sure date field is set
        self.version = version             # make all requests capture the code version

    def date_today(self):
        return date_time_now(date_time_format='%Y-%m-%d')