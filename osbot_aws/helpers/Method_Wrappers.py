from functools import wraps

# todo: create signature based on request params so that we don't cache when the params are different
def cache(function):
    @wraps(function)
    def wrapper(*args,**kwargs):
        if hasattr(function, 'return_value') is False:                  # check if return_value has been set
            function.return_value  = function(*args,**kwargs)           # invoke function and capture the return value
        return function.return_value                                    # return the return value
    return wrapper


def catch(function):
    """Catches any errors and returns an object with the error"""
    @wraps(function)                                                    # so that when we call the __name__ of the called we get the correct name (for example self.aws_lambda.alias.__name__)
    def wrapper(*args,**kwargs):
        try:
            return function(*args,**kwargs)
        except Exception as error:
            return {'error': error }
    return wrapper


class remove:
    """removes the field from the return value of the function (if it exists"""
    def __init__(self, field_name):
        self.field_name = field_name                                # field to remove

    def __call__(self, function):
        @wraps(function)                                            # makes __name__ work ok
        def wrapper(*args,**kwargs):                                # wrapper function
            data = function(*args,**kwargs)                         # calls wrapped function with original params
            if data and data.get(self.field_name) is not None:      # check if field_name exists in data
                del data[self.field_name]                           # if it does, delete it
            return data                                             # return data received
        return wrapper                                              # return wrapper function

#todo: refactor with group_by (simplify these two methods and remove duplicate code)
def index_by(function):                                 # returns the list provided indexed by the key provided in index_by
    @wraps(function)
    def wrapper(*args,**kwargs):
        key = None
        if 'index_by' in kwargs:
            key = kwargs.get('index_by')
            del kwargs['index_by']
        values = function(*args,**kwargs)
        if key:
            results = {}
            for item in values:
                results[item.get(key)] = item
            return results
        return values
    return wrapper

#todo: refactor with index_by
def group_by(function):                                 # returns the list provided grouped by the key provided in group_by
    @wraps(function)
    def wrapper(*args,**kwargs):
        key = None
        if 'group_by' in kwargs:
            key = kwargs.get('group_by')
            del kwargs['group_by']
        values = function(*args,**kwargs)
        if key:
            results = {}
            for item in values:
                value = item.get(key)
                if results.get(value) is None: results[value] = []
                results[value].append(item)
            return results
        return values
    return wrapper