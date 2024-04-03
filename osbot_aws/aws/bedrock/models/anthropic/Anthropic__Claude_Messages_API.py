from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self


class Anthropic__Claude_Messages_API(Kwargs_To_Self):
    anthropic_version   : str = "bedrock-2023-05-31"
    max_tokens          : int   = 1024
    messages            : list
    model_id            : str
    system              : str
    temperature         : float = 0.0
    top_p               : int   = 1
    top_k               : int   = 0
    stop_sequences      : list