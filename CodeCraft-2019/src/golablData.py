# _*_ coding: utf-8 _*_

import CrossMap


class globalData:
    Debug = False
    State = -1
    cars = None
    crosses = None
    roads = None
    CurrentTime = 0
    # 已到达车辆
    ComplateCount = 0
    # 当前道路车辆
    Car_Road = 0
    # 当前车库车辆
    Car_Garage = 0

    Map = CrossMap.CrossMap()
    DistancePre = {}

    Result = list([])

    StateInfo = {"RoadInfo": {}, "CrossInfo": {}}

    def CarComplete(self, car):
        self.ComplateCount += 1
        if self.ComplateCount == len(self.cars):
            self.State = 0


GlobalData = globalData()
