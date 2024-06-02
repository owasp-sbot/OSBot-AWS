from osbot_aws.aws.bedrock.cache.Bedrock__Cache import Bedrock__Cache
from osbot_utils.helpers.html.Tag__Base import Tag__Base
from osbot_utils.helpers.html.Tag__Div import Tag__Div
from osbot_utils.helpers.html.Tag__H import Tag__H
from osbot_utils.helpers.html.Tag__HR import Tag__HR
from osbot_utils.helpers.html.Tag__Head import Tag__Head
from osbot_utils.helpers.html.Tag__Html import Tag__Html


class Bedrock_Cache__Html:

    def __init__(self):
        self.cache        = Bedrock__Cache()
        self.table        = self.cache.cache_table
        self.target_file  = '/tmp/tmp-bedrock-cache.html'
        self.html_tag     = Tag__Html()
        self.title        = 'Html Page with Bedrock_Cache_Data'
        self.sub_title    = '....'
        self.row_elements = []

    def append(self, element):
        self.row_elements.append(element)
        return self

    def create_page(self):
        div_container = Tag__Div(tag_classes=['container-fluid','my-5'])
        h_title       = Tag__H(1, self.title)
        hr            = Tag__HR()
        div_subtitle  = Tag__Div(tag_classes=['badge', 'bg-dark'], inner_html=self.sub_title)
        div_row       = Tag__Div(tag_classes=['row'], elements=self.row_elements)
        div_container.append(h_title,
                             div_subtitle,
                             hr,
                             div_row)

        css_data             = { ".base64-image"  : { "width"         : "200px"           ,
                                                      "height"        : "auto"            ,
                                                      "margin-bottom" : "1rem"            },
                                 ".col"           : { "border"        : "2px solid #C0C0FF",
                                                      "padding"       : "10px"            },
                                 ".bg-dark"       : { "font-size"     : "15px"            },
                                 ".var_name"      : {"font-size"      : "12px"            },
                                 ".comments_value": {"font-size"      : "12px"            }}

        head_style     = Tag__Base(tag_name='style')
        head_tag       = Tag__Head(elements= [head_style])
        head_tag.title = self.title
        head_tag.add_css_bootstrap()
        head_tag.style.set_css(css_data)

        self.html_tag.head  = head_tag
        self.html_tag.body.append(div_container )

    def create_html_file(self):
        self.create_page()
        self.html_tag.save(self.target_file)