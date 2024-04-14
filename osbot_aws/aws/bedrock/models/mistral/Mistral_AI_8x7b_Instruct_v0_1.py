from osbot_aws.aws.bedrock.models.mistral.Mistral_AI import Mistral_AI


class Mistral_AI_8x7b_Instruct_v0_1(Mistral_AI):
    model_id : str = "mistral.mixtral-8x7b-instruct-v0:1"