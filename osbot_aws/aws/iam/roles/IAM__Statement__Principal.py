from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self

class IAM__Statement__Principal(Kwargs_To_Self):
    action         : str
    principal_type : str
    principal_value: str
    effect         : str

    def validate_data(self):
        return self.action and self.principal_type and self.principal_value and self.effect

    def statement(self):
        if self.validate_data():
            return   {'Action'   : self.action                                ,
                      'Effect'   : self.effect                                ,
                      'Principal': {self.principal_type: self.principal_value }}
