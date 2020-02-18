from osbot_aws.apis.Queue import Queue
from pbx_gs_python_utils.utils.Misc import Misc


class Temp_Queue:
    def __init__(self):
        self.name_prefix = 'unit_tests_temp_queue_'
        self.queue_name  = Misc.random_string_and_numbers(prefix=self.name_prefix)
        self.queue       = None

    def __enter__(self):
        self.queue = Queue(self.queue_name).create()
        return self

    def __exit__(self, type, value, traceback):
        assert self.queue.delete() is True