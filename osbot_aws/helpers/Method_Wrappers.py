from functools import wraps

def catch(function):
    @wraps(function)
    def wrapper(*args,**kwargs):
        try:
            return function(*args,**kwargs)
        except Exception as error:
            return {'error': error }
    return wrapper

# returns the list indexed by the key provided in index_by param
def index_by(function):
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

# returns the list grouped by the key provided in index_by param
def group_by(function):
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
