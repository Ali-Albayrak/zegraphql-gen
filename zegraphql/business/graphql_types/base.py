class BaseType:

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_") and not callable(v)}
