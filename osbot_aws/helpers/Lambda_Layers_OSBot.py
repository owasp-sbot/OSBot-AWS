from osbot_aws.helpers.Lambda_Layer_Create import Lambda_Layer_Create


class Lambda_Layers_OSBot:

    PACKAGE__OSBOT_UTILS = "git+https://github.com/owasp-sbot/OSBot-Utils.git@dev"
    PACKAGE__OSBOT_AWS   = 'git+https://github.com/owasp-sbot/OSBot-AWS.git@dev'

    def __init(self):
        pass

    def create__fastapi(self):
        packages = ['fastapi', 'uvicorn']
        with Lambda_Layer_Create('layer_for__fastapi') as _:
            _.add_packages(packages)
            _.recreate()
            return _.arn_latest()

    def create__flask(self):
        packages = ['flask', 'serverless_wsgi']
        with Lambda_Layer_Create('layer_for__flask') as _:
            _.add_packages(packages)
            _.create()
            return _.arn_latest()

    def create__llms(self):
        packages = ['openai']
        with Lambda_Layer_Create('layer_for__llms') as _:
            _.delete_local_layer_folder()
            _.add_packages(packages)
            _.recreate()
            return _.arn_latest()

    def create__mangum(self):       # todo: refactor all these create__xxx methods
        packages = ['mangum']
        with Lambda_Layer_Create('layer_for__mangum') as _:
            _.add_packages(packages)
            _.recreate()
            return _.arn_latest()

    def create__osbot_aws(self):
        packages = [self.PACKAGE__OSBOT_UTILS   ,
                    self.PACKAGE__OSBOT_AWS     ,
                    'python-dotenv'             ]
        with Lambda_Layer_Create('layer_for__osbot_aws') as _:
            _.installed_packages_reset()                                # todo: add way to only reset a couple specific packages
            _.add_packages(packages)
            _.recreate()
            return _.arn_latest()

    def create__osbot_utils(self):
        packages = [self.PACKAGE__OSBOT_UTILS, 'python-dotenv' ]
        with Lambda_Layer_Create('layer_for__osbot_utils') as _:
            _.add_packages(packages)
            _.recreate()
            return _.arn_latest()

    def fastapi(self):
        return Lambda_Layer_Create('layer_for__fastapi').arn_latest()

    def flask(self):
        return Lambda_Layer_Create('layer_for__flask').arn_latest()

    def llms(self):
        return Lambda_Layer_Create('layer_for__llms').arn_latest()

    def mangum(self):
        return Lambda_Layer_Create('layer_for__mangum').arn_latest()

    def osbot_aws(self):
        return Lambda_Layer_Create('layer_for__osbot_aws').arn_latest()

    def osbot_utils(self):
        with Lambda_Layer_Create('layer_for__osbot_utils') as _:
            _.add_package(self.PACKAGE__OSBOT_UTILS)
            _.add_package('python-dotenv')
            return _.create()                                   # will return _.arn_latest() if already exists
        #return layer_osbot_utils.installed_packages_names()

