from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self


class Anthropic__Claude_Messages_API(Kwargs_To_Self):
    anthropic_version   : str = "bedrock-2023-05-31"
    max_tokens          : int   = 1024
    messages            : list
    model_id            : str
    #system              : str
    temperature         : float = 0.0
    top_p               : int   = 1
    top_k               : int   = 0
    stop_sequences      : list

    def body(self, messages, system=''):
        return dict(anthropic_version = self.anthropic_version  ,
                    max_tokens        = self.max_tokens         ,
                    messages          = messages                ,
                    temperature       = self.temperature        ,
                    top_p             = self.top_p              ,
                    top_k             = self.top_k              ,
                    stop_sequences    = self.stop_sequences     ,
                    system           = system

                    )