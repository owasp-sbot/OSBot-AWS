from functools               import wraps
from datetime                import datetime
from osbot_utils.utils.Files import folder_create, path_combine
from osbot_utils.utils.Json import json_save


def save_event_in_tmp_folder(event):
    now_str       = datetime.now().strftime("%Y-%m-%d__%H-%M-%S__%f")
    target_folder = folder_create('/tmp/event_logs')
    file_name     = f'{now_str}.json'
    target_file = path_combine(target_folder, file_name)

    return json_save(target_file, event)

def lambda_save_event(function):
    @wraps(function)
    def wrapper(event, context=None):
        save_event_in_tmp_folder(event)
        return function(event, context)
    return wrapper