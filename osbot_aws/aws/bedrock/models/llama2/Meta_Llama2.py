from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self

class Meta_Llama2(Kwargs_To_Self):
    model_id          : str
    prompt            : str
    temperature       : float    = 0.0
    top_p             : float    = 1.0
    max_gen_len       : int      = 1024

    def body(self):
        return dict(prompt        = self.prompt      ,
                    temperature   = self.temperature ,
                    top_p         = self.top_p       ,
                    max_gen_len   = self.max_gen_len )
