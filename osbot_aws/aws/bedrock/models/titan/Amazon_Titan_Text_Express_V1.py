from osbot_aws.aws.bedrock.models.titan.base_classes.Amazon_Titan__Text import Amazon_Titan__Text

# for details on this model see https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-titan-text.html

class Amazon_Titan_Text_Express_V1(Amazon_Titan__Text):
    # config vars
    model_id     : str = 'amazon.titan-text-express-v1'
