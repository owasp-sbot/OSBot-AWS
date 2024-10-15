from osbot_utils.utils.Dev import pprint

from osbot_aws.aws.s3.S3__Key_Generator                 import S3__Key_Generator
from osbot_utils.utils.Json                             import  to_json_str
from osbot_utils.decorators.methods.cache_on_self       import cache_on_self
from osbot_aws.aws.s3.S3                                import S3
from osbot_utils.helpers.flows.models.Flow_Run__Event   import Flow_Run__Event
from osbot_utils.base_classes.Type_Safe                 import Type_Safe
from osbot_utils.helpers.flows.Flow__Events             import flow_events

S3_Folder_NAME__EVENTS_TO_PROCESS = 'events_to_process'
#S3_Folder_NAME__EVENTS_PROCESSED  = 'events_processed'

class Flow_Events__To__S3(Type_Safe):
    s3_bucket        : str = None
    s3_folder        : str = None
    s3_key_generator : S3__Key_Generator

    def __enter__(self):
        return self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def add_event_listener(self):
        flow_events.event_listeners.append(self.event_listener)

    def enabled(self):
        return self.s3_bucket is not None                   # todo: add more checks here

    def event_listener(self, flow_event: Flow_Run__Event):
        if self.enabled():
            s3_key        = self.s3_key_for_flow_event(flow_event)
            file_contents = to_json_str(flow_event.json())
            self.s3().file_create_from_string(bucket=self.s3_bucket, key=s3_key, file_contents=file_contents)

    def remove_event_listener(self):
        flow_events.event_listeners.remove(self.event_listener)

    @cache_on_self
    def s3(self):
        return S3()

    def s3_key_for_flow_event(self, flow_event: Flow_Run__Event):
        event_type   = flow_event.event_type.value
        flow_run_id  = flow_event.event_data.flow_run_id
        task_run_id  = flow_event.event_data.task_run_id
        path_elements = self.s3_key_generator.create_path_elements__from_when()
        path_elements.append(flow_run_id)
        if task_run_id:
            path_elements.append(task_run_id)
        path_elements.append(event_type)
        file_id       = flow_event.event_id
        s3_key        = self.s3_key_generator.create_s3_key(path_elements=path_elements, file_id=file_id)
        return s3_key

    def setup(self):
        self.s3_key_generator.root_folder = S3_Folder_NAME__EVENTS_TO_PROCESS
        return self

    def start(self):
        self.setup()
        self.add_event_listener()
        return self

    def stop(self):
        self.remove_event_listener()
        return self