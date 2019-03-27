#!/usr/bin/python
# -*- coding:utf-8 -*-

import CrossMap
import copy

class globalData:
    Debug = False
    State = -1
    cars = None
    crosses = None
    roads = None
    carsByID = {}
    crossesByID = {}
    roadsByID = {}

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
    LastFrame = None

    def CarComplete(self, car):
        self.ComplateCount += 1
        if self.ComplateCount == len(self.cars):
            self.State = 0

    def TempFrame(self):
        if self.LastFrame == None:
            self.LastFrame =copy.copy(self)

        self.LastFrame.CurrentTime =self.CurrentTime
        self.LastFrame.ComplateCount = self.ComplateCount
        self.LastFrame.Car_Road = self.Car_Road
        self.LastFrame.Car_Garage = self.Car_Garage
    
    def BackFrame(self):
        self.CurrentTime =self.LastFrame.CurrentTime
        self.ComplateCount = self.LastFrame.ComplateCount
        self.Car_Road = self.LastFrame.Car_Road
        self.Car_Garage = self.LastFrame.Car_Garage

GlobalData = globalData()
