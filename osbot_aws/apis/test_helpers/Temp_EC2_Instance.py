from osbot_aws.aws.ec2.EC2_Instance import EC2_Instance


class Temp_EC2_Instance:

    def __init__(self, create_kwargs=None, delete_on_exit=True):
        self.ec2_instance   = None
        self.create_kwargs  = create_kwargs
        self.delete_on_exit = delete_on_exit

    def __enter__(self):
        self.ec2_instance = EC2_Instance(create_kwargs=self.create_kwargs)
        self.ec2_instance.create()
        return self.ec2_instance

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.delete_on_exit:
            self.ec2_instance.delete()
        if exc_type is not None:
            raise exc_val
