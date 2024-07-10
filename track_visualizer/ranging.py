class Range():
    def __init__(self, a=None,b=None):
        self.a = a
        self.b = b

    def __mul__(self, c):
        self.a = self.a*c if self.a is not None else None
        self.b = self.b*c if self.b is not None else None
        
    def __getitem__(self, key):
        lst = [self.a, self.b]
        return lst[key]