from osbot_aws.aws.iam.IAM_Role import IAM_Role


class Temp_IAM_Role:
    def __init__(self, role_name=None, delete_on_exit=True):
        self.role_name      = role_name
        self.iam_role       = IAM_Role(role_name=role_name)
        self.delete_on_exit = delete_on_exit


    def __enter__(self):
        self.iam_role.create_for__lambda()
        return self.iam_role

    def __exit__(self, type, value, traceback):
        if self.delete_on_exit:
            self.iam_role.delete()
