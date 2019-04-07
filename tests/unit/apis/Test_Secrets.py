from aws.secrets import *

class Test_Lamda_Ip_Details(unittest.TestCase):

    def setUp(self):
        self.id    = 'an_secret'
        self.value = 'goes here'
        self.secrets = Secrets(self.id)

    def _test_create_value(self):
        if (self.secrets.exists() is False and self.secrets.deleted() is False):
            assert self.secrets.create() is True

    def test_deleted(self):
        assert self.secrets.deleted(       ) is True
        assert Secrets('aaaa').deleted(    ) is False

    def test_details(self):
        details = self.secrets.details()
        assert details.get('Name') == self.id

    def test_exists(self):
        assert Secrets('aaaaa').exists()     is False
        self.secrets.undelete()
        assert self.secrets.exists() is True

        self.secrets.delete()
        assert self.secrets.exists() is False

    def test_value(self):
        self.secrets.undelete()
        value = self.secrets.value()
        value.get('SecretString') == self.value
        self.secrets.delete()

if __name__ == '__main__':
    unittest.main()