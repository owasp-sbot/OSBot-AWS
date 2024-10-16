from osbot_utils.helpers.flows.models.Flow_Run__Event import Flow_Run__Event
from osbot_utils.utils.Json import from_json_str

from osbot_aws.flows.Flow_Events__To__S3                            import Flow_Events__To__S3
from osbot_local_stack.testing.TestCase__Local_Stack__Temp_Bucket   import TestCase__Local_Stack__Temp_Bucket
from osbot_utils.helpers.flows.models.Flow_Run__Config              import Flow_Run__Config
from osbot_utils.helpers.flows.decorators.task                      import task
from osbot_utils.helpers.flows                                      import Flow
from osbot_utils.helpers.flows.decorators.flow                      import flow


class test_Flow_Events__To__S3(TestCase__Local_Stack__Temp_Bucket):

    def test_event_listener(self):
        temp_bucket = self.s3_bucket
        with Flow_Events__To__S3(s3_bucket=temp_bucket) as _:
            test_flow = an_flow_1()
            test_flow.execute_flow()

        s3_key = _.s3().find_files(temp_bucket)
        for s3_key in s3_key:
            flow_event_json = from_json_str(_.s3().file_contents(temp_bucket, s3_key))
            flow_event  = Flow_Run__Event.from_json(flow_event_json)
            assert flow_event.json() == flow_event_json
            assert flow_event.event_data.flow_run_id == test_flow.flow_id


flow_config = Flow_Run__Config(logging_enabled=False, log_to_console=True)

@flow(flow_config=flow_config)
def an_flow_1() -> Flow:
    print('inside the flow')
    an_task_1()
    return "flow return value"


@task()
def an_task_1():
    print('inside the task')