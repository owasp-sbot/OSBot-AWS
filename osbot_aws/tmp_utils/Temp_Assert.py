import datetime

from osbot_utils.utils.Assert import Assert

# todo : move to OSBot_Utils Assert class
class Temp_Assert:

    def __init__(self,target):
        self._assert = Assert(target)

    def is_today(self):
        assert type(self._assert.target) == datetime.datetime
        assert str(self._assert.target.date())  == str(datetime.datetime.utcnow().date())