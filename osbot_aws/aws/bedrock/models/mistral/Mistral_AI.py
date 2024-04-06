from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self

class Mistral_AI(Kwargs_To_Self):
    model_id          : str
    prompt            : str
    temperature       : float    = 0.0
    top_p             : float    = 1.0
    top_k             : int      = 1
    max_tokens        : int      = 1024
    stop              : list




    def body(self):
        return dict(prompt        = self.prompt         ,
                    temperature   = self.temperature    ,
                    top_p         = self.top_p          ,
                    top_k         = self.top_k          ,
                    max_tokens    = self.max_tokens     ,
                    stop          = self.stop           )
