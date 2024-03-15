from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Json import json_md5


class Bedrock__Cache(Kwargs_To_Self):
    enabled : bool = True

    def model_invoke(self, bedrock, model_id, body):
        pprint('------- in  Bedrock__Cache ------ ')
        # pprint(model_id)
        # pprint(json_md5(body))
        # pprint(body)
        return bedrock.model_invoke(model_id, body)
        # return {'inputTextTokenCount': 3, 'results': [
        #     {'completionReason': 'FINISH', 'outputText': '\n\nBot: Hello! How can I help you?', 'tokenCount': 12}]}