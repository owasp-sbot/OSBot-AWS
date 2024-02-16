class Boto_Helpers:

    @staticmethod
    def invoke_using_paginator(api, method, field_id, **kwargs):
            paginator = api.get_paginator(method)
            for page in paginator.paginate(**kwargs):
                if page:
                    for id in page.get(field_id):
                        yield id
                else:
                    yield page

