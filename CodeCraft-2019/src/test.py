import copy

class Test:
    def __init__(self):
        self.T = []
        self.T.append(self)


t1 = Test()

t2 = copy.deepcopy(t1)
print(t2)

