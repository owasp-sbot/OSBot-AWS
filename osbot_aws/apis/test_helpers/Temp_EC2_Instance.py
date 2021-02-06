from osbot_aws.helpers.EC_Instance import EC2_Instance


class Temp_EC2_Instance:

    def __init__(self):
        self.ec2_instance = None

    def __enter__(self):
        self.ec2_instance = EC2_Instance()
        self.ec2_instance.create()
        return self.ec2_instance

    def __exit__(self, type, value, traceback):
        return self.ec2_instance.delete()