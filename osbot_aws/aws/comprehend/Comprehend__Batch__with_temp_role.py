from osbot_aws.aws.comprehend.Comprehend__Batch                 import Comprehend__Batch
from osbot_aws.aws.comprehend.Comprehend__IAM__Temp_Role        import Comprehend__IAM__Temp_Role

class Comprehend__Batch__with_temp_role(Comprehend__IAM__Temp_Role, Comprehend__Batch):
    pass