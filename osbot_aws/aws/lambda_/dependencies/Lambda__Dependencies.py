import os
import warnings

from osbot_aws.aws.lambda_.dependencies.Lambda__Dependency__Inside_Lambda import Lambda__Dependency__Inside_Lambda


# Legacy helper class (will be removed in a future version)

class Lambda__Dependencies():
    def __init__(self, *args, **kwargs):
        warnings.warn("Lambda__Dependencies class is deprecated and will be removed in a future version.", DeprecationWarning,   2,)

    def load_dependencies(self, targets):
        if type(targets) is list:
            for target in targets:
                self.load_dependency(target)
            return
        for target in targets.split(','):
            self.load_dependency(target.strip())

    def load_dependency(self, target):
        if os.getenv('AWS_REGION') is None:
            return
        Lambda__Dependency__Inside_Lambda(package_name=target).load()


# Legacy Static helpers
def load_dependencies(targets):
    Lambda__Dependencies().load_dependencies(targets)

def load_dependency(target):
    Lambda__Dependencies().load_dependency(target)

# def pip_install_dependency(target, target_aws_lambda=True):
#     Lambda__Dependencies().pip_install_dependency(target, target_aws_lambda)
#
# def upload_dependency(target):
#     Lambda__Dependencies().upload_dependency(target)
