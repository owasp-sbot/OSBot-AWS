from functools import wraps


def catch(function):
    @wraps(function)
    def wrapper(*args,**kwargs):
        try:
            return function(*args,**kwargs)
        except Exception as error:
            return {'error': error }
    return wrapper

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