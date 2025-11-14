from osbot_aws.aws.comprehend.Comprehend                    import Comprehend
from osbot_aws.aws.comprehend.Comprehend__IAM__Temp_Role    import Comprehend__IAM__Temp_Role

class Comprehend__with_temp_role(Comprehend__IAM__Temp_Role, Comprehend):
    pass