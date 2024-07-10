class Data():
    def __get__(self, instance, owner):
        if instance.to_be_masked:
            return instance.masked(instance._data)
        else:
            return instance._data
