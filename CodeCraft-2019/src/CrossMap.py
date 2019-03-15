# _*_ coding: utf-8 _*_

class CrossMap:
    Crosses={}

    def __init__(self,crosses=None):
        if crosses != None:
            for cross in crosses:
                self.AddCross(cross)
    
    def AddCross(self,cross):
        self.Crosses[cross.ID]=cross
    
    def __getitem__(self,index):
        return self.Crosses[index]