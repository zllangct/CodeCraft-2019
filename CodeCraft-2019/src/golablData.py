# _*_ coding: utf-8 _*_

import CrossMap

class globalData:
    State = -1
    cars = None
    crosses =None
    roads = None
    CurrentTime=0
    ComplateCount = 0

    Map = CrossMap.CrossMap()
    DistancePre = {}
    
    Result = list([])

    def CarComplate(self,car):
        self.ComplateCount+=1
        if self.ComplateCount == len(self.cars):
            self.State = 0

GlobalData = globalData()