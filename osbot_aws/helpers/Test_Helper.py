import  logging
from    unittest                import TestCase
from    osbot_utils.utils       import Png
from    osbot_utils.utils.Dev   import Dev, pprint



class Test_Helper(TestCase):

    def setUp(self): #-> OSBot_Setup:
        logging.getLogger().addHandler(logging.StreamHandler())
        self.result     = None
        self.png_data   = None
        self.png_file   = '/tmp/unit-test.png'
        print()
        #return self.osbot_setup()

    #def osbot_setup(self,profile_name = None, account_id=None, region=None) -> OSBot_Setup:
        #return OSBot_Setup(profile_name=profile_name, account_id=account_id, region_name=region)

    def tearDown(self):
        if hasattr(self, 'result'):
            if self.result is not None:
                pprint(self.result)
        if hasattr(self, 'png_data'):
            if hasattr(self, 'png_data') is False:
                self.png_file = '/tmp/unit-test.png'
            self.save_png(self.png_data, self.png_file)
        #else:
        #    pprint("**** TEST HELPER WARNING - super().setUp() was not called from the current setUp override method **** ")

    # def lambda_package(self, lambda_name, profile_name = None, account_id=None, region=None):
    #     return self.osbot_setup(profile_name=profile_name,account_id=account_id,region=region).lambda_package(lambda_name)

    @staticmethod
    def print(result):
        if result is not None:
            pprint(result)

    @staticmethod
    def save_png(png_data, target_file):
        Png.save_png_base64_to_file(png_data, target_file)
