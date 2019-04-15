from pbx_gs_python_utils.utils.Misc import Misc


class Temp_Misc:

    @staticmethod
    def get_field(target, field, default=None):
        if target is not None:
            try:
                value = getattr(target, field)
                if value is not None:
                    return value
            except:
                pass
        return default

    @staticmethod
    def get_missing_fields(target,field):
        missing_fields = []
        for field in field:
            if Temp_Misc.get_field(target, field) is None:
                missing_fields.append(field)
        return missing_fields

    @staticmethod
    def last_letter(text):
        if text and (type(text) is str) and len(text) > 0:
            return text[-1]

    @staticmethod
    def random_text(prefix=None,length=12):
        if prefix is None: prefix = 'text_'
        if Temp_Misc.last_letter(prefix) != '_':
            prefix += '_'
        return Misc.random_string_and_numbers(length=length, prefix=prefix)
