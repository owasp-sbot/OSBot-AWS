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