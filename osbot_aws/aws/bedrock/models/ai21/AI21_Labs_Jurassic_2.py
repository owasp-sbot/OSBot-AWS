from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self

class AI21_Labs_Jurassic_2(Kwargs_To_Self):
    model_id          : str
    prompt            : str
    temperature       : float    = 0.0
    top_p             : float    = 1.0
    max_tokens        : int      = 1024
    stop_sequences    : list
    #countPenalty     : dict #{ "scale": float }
    #presencePenalty  : dict #{"scale": float },
    #frequencyPenalty : dict # {"scale": float }


    def body(self):
        return dict(prompt        = self.prompt         ,
                    temperature   = self.temperature    ,
                    topP          = self.top_p          ,
                    maxTokens     = self.max_tokens     ,
                    stopSequences = self.stop_sequences )
