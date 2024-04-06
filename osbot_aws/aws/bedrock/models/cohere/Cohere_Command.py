from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self

class Cohere_Command(Kwargs_To_Self):
    model_id           : str
    prompt             : str
    temperature        : float    = 0.0
    p                  : float    = 1.0
    k                  : int      = 0
    max_tokens         : int      = 1024
    stop_sequences     : list
    return_likelihoods : str      = 'NONE' #"GENERATION|ALL|NONE",
    stream             : bool     = False
    num_generations    : int      = 1
    truncate           : str      = "NONE"      # NONE|START|END"
    #logit_bias        : dict       #    {token_id: bias},



    def body(self):
        return dict(prompt             = self.prompt             ,
                    temperature        = self.temperature        ,
                    p                  = self.p                  ,
                    k                  = self.k                  ,
                    max_tokens         = self.max_tokens         ,
                    stop_sequences     = self.stop_sequences     ,
                    return_likelihoods = self.return_likelihoods ,
                    stream             = self.stream             ,
                    num_generations    = self.num_generations    ,
                    truncate           = self.truncate           )
