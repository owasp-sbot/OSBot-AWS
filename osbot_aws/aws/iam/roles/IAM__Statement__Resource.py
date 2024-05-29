from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self


class IAM__Statement__Resource(Kwargs_To_Self):
    actions  : list
    effect   : str
    resource : str

    def validate_data(self):
        return self.actions and self.effect and self.resource

    def statement(self):
        if self.validate_data():
            action = [action for action in self.actions]
            return {"Effect"  : self.effect,
                    "Action"  : action,
                    "Resource": self.resource}