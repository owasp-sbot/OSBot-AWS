from osbot_aws.helpers.Lambda_Layer_Create import Lambda_Layer_Create


class Lambda_Layers_OSBot:

    PACKAGE__OSBOT_UTILS = "git+https://github.com/owasp-sbot/OSBot-Utils.git@dev"
    PACKAGE__OSBOT_AWS   = 'git+https://github.com/owasp-sbot/OSBot-AWS.git@dev'

    def __init(self):
        pass

    def osbot_aws(self):
        packages = [self.PACKAGE__OSBOT_UTILS, self.PACKAGE__OSBOT_AWS,
                    #'boto3'        ,
                    'python-dotenv' ]
        with Lambda_Layer_Create('layer_for__osbot_aws') as _:
            _.add_packages(packages)
            return _.create()

    def osbot_utils(self):
        with Lambda_Layer_Create('layer_for__osbot_utils') as _:
            _.add_package(self.PACKAGE__OSBOT_UTILS)
            _.add_package('python-dotenv')
            return _.create()                                   # will return _.arn_latest() if already exists
        #return layer_osbot_utils.installed_packages_names()

