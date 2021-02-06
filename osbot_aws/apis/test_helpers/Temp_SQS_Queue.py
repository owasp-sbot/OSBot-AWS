from osbot_utils.utils.Misc import random_string

from osbot_aws.helpers.SQS_Queue import SQS_Queue
from osbot_utils.utils import Misc


class Temp_SQS_Queue:
    def __init__(self , queue_name=None, attributes=None, fifo=True):
        self.attributes = attributes
        self.fifo       = fifo
        self.queue      = None
        self.queue_name = queue_name or random_string(prefix='unit_tests_temp_queue_')
        if fifo and self.queue_name.endswith('.fifo') is False:
            self.queue_name += '.fifo'


    def __enter__(self):
        self.queue = SQS_Queue(self.queue_name)
        if self.fifo:
            self.queue.create_fifo(attributes=self.attributes)
        else:
            self.queue.create(attributes=self.attributes)

        return self.queue

    def __exit__(self, type, value, traceback):
        assert self.queue.delete() is True