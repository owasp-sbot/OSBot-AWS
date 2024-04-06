from osbot_aws.aws.bedrock.models.titan.base_classes.Amazon_Titan__Text import Amazon_Titan__Text

# for details on this model see https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-titan-text.html

class Amazon_Titan_Tg1_Large(Amazon_Titan__Text):
    model_id     : str = 'amazon.titan-tg1-large'
