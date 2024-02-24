from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self

# for details see  https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-claude.html

class Anthropic__Claude_Instant_V1(Kwargs_To_Self):
    # config vars
    model_id            : str = 'anthropic.claude-instant-v1'
    prompt_format       : str = "\n\nHuman:{prompt}\n\nAssistant:"
    # prompt vars
    prompt              : str
    temperature         : float = 0.0
    top_p               : int   = 1
    top_k               : int   = 0
    max_tokens_to_sample: int   = 1024
    stop_sequences      : list

    def body(self):
        anthropic_prompt = self.prompt_format.format(prompt=self.prompt)
        return  { "prompt"               : anthropic_prompt          ,
                  "temperature"          : self.temperature          ,
                  "top_p"                : self.top_p                ,
                  "top_k"                : self.top_k                ,
                  "max_tokens_to_sample" : self.max_tokens_to_sample ,
                  "stop_sequences"       : self.stop_sequences       }