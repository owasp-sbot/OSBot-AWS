#assert list_set(models_amazon__text       ) == [
# 'amazon.titan-text-express-v1'    ,                   # current adding this one
# 'amazon.titan-text-express-v1:0:8k' ,
# 'amazon.titan-text-lite-v1'    ,
# 'amazon.titan-text-lite-v1:0:4k',
# 'amazon.titan-tg1-large'                                                                                                    ]
from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self

# for details on this model see https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-titan-text.html

class Amazon_Titan_Text_Express_V1(Kwargs_To_Self):
    # config vars
    model_id     : str = 'amazon.titan-text-express-v1'
    #model_id     : str = 'amazon.titan-text-express-v1:0:8k'        # fails validation
    #model_id     : str = 'amazon.titan-text-lite-v1'
    #model_id: str = 'amazon.titan-tg1-large'
    # prompt vars
    input_text     : str    = ""
    temperature    : float  = 0.0
    topP           : int    = 1
    max_token_count: int    = 1024
    stop_sequences : list

    def body(self, prompt=None):
        if prompt:
            self.input_text = prompt
        return   { "inputText"           : self.input_text,
                   "textGenerationConfig": { "temperature"  : self.temperature     ,
                                             "topP"         : self.topP            ,
                                             "maxTokenCount": self.max_token_count ,
                                             "stopSequences": self.stop_sequences  }}