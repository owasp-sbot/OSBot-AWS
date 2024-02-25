#assert list_set(models_amazon__text       ) == [
# 'amazon.titan-text-express-v1'    ,                   # current adding this one
# 'amazon.titan-text-express-v1:0:8k' ,
# 'amazon.titan-text-lite-v1'    ,
# 'amazon.titan-text-lite-v1:0:4k',
# 'amazon.titan-tg1-large'                                                                                                    ]
from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self


class Amazon_Titan_Text_Express_V1(Kwargs_To_Self):
    pass