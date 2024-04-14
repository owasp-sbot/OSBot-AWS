from osbot_aws.aws.bedrock.cache.html.Bedrock_Cache__Html import Bedrock_Cache__Html
from osbot_utils.helpers.html.Tag__Base import Tag__Base
from osbot_utils.helpers.html.Tag__H import Tag__H
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Json import json_loads, json_dumps
from osbot_utils.utils.Misc import list_set, word_wrap, timestamp_to_str_date


class Bedrock_Cache__Html_Table(Bedrock_Cache__Html):

    def __init__(self):
        super().__init__()
        self.title            = 'AWS Bedrock Cached Data'
        self.sub_title        = 'all entries'
        self.table_headers    = ['model', 'task_type', 'prompt', 'response', 'comments', 'timestamp']
        self.debug_mode       = True
        self.target_file      = '/tmp/tmp-bedrock-table.html'

    def create_table(self, headers, rows):
        tag__table      = Tag__Base(tag_name='table', tag_classes=["table", "table-striped", "table-bordered", "table-hover",'table-dark'])
        tag__thead      = Tag__Base(tag_name='thead')
        tag__tbody      = Tag__Base(tag_name='tbody')

        tag__tr__header = Tag__Base(tag_name='tr')

        for header in headers:
            tag__td = Tag__Base(tag_name='td', inner_html=header)
            tag__tr__header.append(tag__td)

        for row in rows:
            tag__tr = Tag__Base(tag_name='tr')
            for header in headers:
                td_value =  row.get(header)
                tag__td = Tag__Base(tag_name='td', inner_html=td_value)
                tag__tr.append(tag__td)
            tag__tbody.append(tag__tr)

        tag__thead.append(tag__tr__header)
        tag__table.append(tag__thead)
        tag__table.append(tag__tbody)

        self.row_elements.append(tag__table)


    def table_rows(self):
        # if self.debug_mode:
        #     self.table_headers.append('request_body')

        rows    = []
        #pprint(self.table.fields_names__cached())
        for row in self.table.rows():
            comments          = row.get('comments' )
            timestamp         = row.get('timestamp')
            response_data_str = row.get('response_data')
            response_data     = json_loads(response_data_str)
            request_data_str  = row.get('request_data')
            request_data      = json_loads(request_data_str )
            request_body      = request_data.get('body'   , {})
            if not request_body:
                continue
            request_body_str  = json_dumps(request_body)
            model             = request_data.get('model'  ) or request_data.get('model_id'  )       #todo
            task_type         = self.extract_task_type_from_request_body(model, request_body)
            prompt            = self.extract_prompt_from_request_data   (model, request_body)
            response          = self.extract_response_from_response_data(model, response_data)
            if timestamp:
                timestamp_str = timestamp_to_str_date(timestamp)
            else:
                timestamp_str = 'NA'
            if response is None:
                self.extract_response_from_response_data(model, response_data)
                pass
            item = dict(model        = model                                                 ,
                        prompt       = f'<pre>{word_wrap(prompt  .strip(), 40)}</pre>',
                        response     = f'<pre>{word_wrap(response.strip(), 40)}</pre>',
                        task_type    = task_type                                             ,
                        timestamp    = timestamp_str                                         ,
                        comments     = comments                                              )
                        #request_body = f'<pre>{word_wrap(request_body_str, 40)}</pre>')
            # todo: find better way to do this, where we don't see the image base64 string on the html page
            # if self.debug_mode:
            #     item['request_body'] = f'<pre>{word_wrap(request_body_str, 40)}</pre>'
            rows.append(item)
            #pprint(list_set(row))

        return rows

    def extract_task_type_from_request_body(self, model, request_body):
        if 'taskType' in request_body:
            return request_body.get('taskType')
        if model in ['amazon.titan-tg1-large', 'amazon.titan-text-lite-v1']:
            return 'amazon text model'
        if model in ['anthropic.claude-instant-v1','anthropic.claude-v2', 'anthropic.claude-v2:1',
                     "anthropic.claude-3-haiku-20240307-v1:0","anthropic.claude-3-sonnet-20240229-v1:0"]:
            if "prompt" in request_body:
                return "claude text completion"
            if "messages" in request_body:
                return "claude messages"
        #pprint(model, request_body)
        return 'NA'

    def extract_prompt_from_request_data(self, model, request_body):
        if model=='amazon.titan-image-generator-v1':
            task_type = request_body.get('taskType')
            text_params = {}
            if task_type == 'TEXT_IMAGE':
                text_params = request_body.get('textToImageParams'   , {})
            elif task_type == 'IMAGE_VARIATION':
                text_params = request_body.get('imageVariationParams', {})
            if text_params:
                text          = text_params.get('text'            , '')
                negative_text = text_params.get('negativeText'    , '')
                if negative_text:
                    return f'{text}   \n\nnegative_text: {negative_text}'
                return text
            return f'in amazon.titan-image-generator-v1 , unsupported task_type: {task_type}'
        if model in ['amazon.titan-text-lite-v1', 'amazon.titan-tg1-large']:
            return request_body.get('inputText', '')
        if model in ['anthropic.claude-instant-v1','anthropic.claude-v2', 'anthropic.claude-v2:1',
                     "anthropic.claude-3-haiku-20240307-v1:0","anthropic.claude-3-sonnet-20240229-v1:0"]:
            if "prompt" in request_body:
                return request_body.get('prompt', '')
            if "messages" in request_body:
                messages = request_body.get('messages')
                system   = request_body.get('system')
                return f'{messages} \n\nsystem: {system}'
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
            if type(response_data) is list:
                output_text = ""
                for chunk in response_data:
                    output_text += chunk.get('outputText')
                return output_text
            results = response_data.get('results')
            if len(results) ==1:
                result = results[0]
                output_text = result.get('outputText')
                return output_text
            return f'error: response_data should only have one result and it had {len(results)}'

        if model in ['anthropic.claude-instant-v1','anthropic.claude-v2', 'anthropic.claude-v2:1',
                     "anthropic.claude-3-haiku-20240307-v1:0", "anthropic.claude-3-sonnet-20240229-v1:0"]:
            if "completion" in response_data:
                return response_data.get('completion')
            if "content"  in response_data:
                return f"{response_data.get('content')}"
            if type(response_data) is list:
                completions = ""
                for chunk in response_data:
                    completions += chunk.get('completion')
                return completions

        # if model in ["anthropic.claude-3-haiku-20240307-v1:0", "anthropic.claude-3-sonnet-20240229-v1:0"]:
        #     return f"{response_data.get('content')}"

        return f'unsupported model: {model}'

    def create(self):
        rows    = self.table_rows()
        headers = self.table_headers
        self.create_table(headers, rows)


        #self.append(div_h1)

        self.create_html_file()