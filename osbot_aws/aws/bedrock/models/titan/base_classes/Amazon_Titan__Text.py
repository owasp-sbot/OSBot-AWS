from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self

# for details on this model see https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-titan-text.html
# 'amazon.titan-text-express-v1'    # working on this
# 'amazon.titan-text-lite-v1'   ,
# 'amazon.titan-tg1-large'
class Amazon_Titan__Text(Kwargs_To_Self):
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