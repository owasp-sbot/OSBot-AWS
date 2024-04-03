from osbot_aws.aws.bedrock.cache.html.Bedrock_Cache__Html import Bedrock_Cache__Html
from osbot_utils.helpers.html.Tag__Base import Tag__Base
from osbot_utils.helpers.html.Tag__H import Tag__H
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Json import json_loads, json_dumps
from osbot_utils.utils.Misc import list_set, word_wrap, timestamp_to_str_date


class Bedrock_Cache__Html_Table(Bedrock_Cache__Html):

    def __init__(self):
        super().__init__()
        self.title         = 'AWS Bedrock Cached Data'
        self.sub_title     = 'all entries'
        self.table_headers = ['model', 'prompt', 'response', 'task_type', 'timestamp', 'cache_hits']

    def create_table(self, headers, rows):
        tag__table      = Tag__Base(tag_name='table', tag_classes=["table", "table-striped", "table-bordered", "table-hover"])
        tag__thead      = Tag__Base(tag_name='thead')
        tag__tbody      = Tag__Base(tag_name='tbody')

        tag__tr__header = Tag__Base(tag_name='tr')

        for header in self.table_headers:
            tag__td = Tag__Base(tag_name='td', inner_html=header)
            tag__tr__header.append(tag__td)

        for row in rows:
            tag__tr = Tag__Base(tag_name='tr')
            for header in self.table_headers:
                td_value =  row.get(header)
                tag__td = Tag__Base(tag_name='td', inner_html=td_value)
                tag__tr.append(tag__td)
            tag__tbody.append(tag__tr)

        tag__thead.append(tag__tr__header)
        tag__table.append(tag__thead)
        tag__table.append(tag__tbody)

        self.row_elements.append(tag__table)


    def table_rows(self):
        rows    = []
        #pprint(self.table.fields_names__cached())
        for row in self.table.rows():
            cache_hits        = row.get('cache_hits')
            timestamp         = row.get('timestamp')
            response_data_str = row.get('response_data')
            response_data     = json_loads(response_data_str)
            request_data_str  = row.get('request_data')
            request_data      = json_loads(request_data_str )
            request_body      = request_data.get('body'   , {})
            if not request_body:
                continue
            request_body_str  = json_dumps(request_body)
            model             = request_data.get('model'  )
            task_type         = request_body.get('taskType')
            prompt            = self.extract_prompt_from_request_data(model, request_body)
            response          = self.extract_response_from_response_data(model, response_data)
            if timestamp:
                timestamp_str = timestamp_to_str_date(timestamp)
            else:
                timestamp_str = 'NA'

            #pprint(request_body_str)
            item = dict(model        = model          ,
                        prompt       = f'<pre>{word_wrap(prompt  .strip(), 40)}</pre>',
                        response     = f'<pre>{word_wrap(response.strip(), 40)}</pre>',
                        task_type    = task_type      ,
                        timestamp    = timestamp_str  ,
                        cache_hits   = str(cache_hits))
                        #request_body = f'<pre>{word_wrap(request_body_str, 40)}</pre>')
            rows.append(item)
            #pprint(list_set(row))

        return rows

    def extract_prompt_from_request_data(self, model, request_body):
        if model=='amazon.titan-image-generator-v1':
            text_to_image_params = request_body.get('textToImageParams')
            text          = text_to_image_params.get('text'            )
            negative_text = text_to_image_params.get('negativeText'  )
            if negative_text:
                return f'{text}   \n\nnegative_text: {negative_text}'
            return text
        if model in ['amazon.titan-text-lite-v1', 'amazon.titan-tg1-large']:
            return request_body.get('inputText')
        if model == 'anthropic.claude-instant-v1':
            return request_body.get('prompt')
        if model is None:
            return 'NA'
        return f'unsupported model: {model}'

    def extract_response_from_response_data(self, model, response_data):
        if model == 'amazon.titan-image-generator-v1':
            images = list_set(response_data.get('images'))
            if len(images) ==1:
                image = images[0]
                return f'{len(image):,} - image size'
            return f'error: response_data should only have one image and it had {len(images)}'
        if model in ['amazon.titan-text-lite-v1', 'amazon.titan-tg1-large']:
            results = response_data.get('results')
            if len(results) ==1:
                result = results[0]
                output_text = result.get('outputText')
                return output_text
            return f'error: response_data should only have one result and it had {len(results)}'

        if model == 'anthropic.claude-instant-v1':
            return response_data.get('completion')

        return f'unsupported model: {model}'

    def create(self):
        rows    = self.table_rows()
        headers = self.table_headers
        self.create_table(headers, rows)


        #self.append(div_h1)

        self.create_html_file()