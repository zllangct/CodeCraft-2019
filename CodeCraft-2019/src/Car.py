# _*_ coding: utf-8 _*_
import numpy as np
import logging
import golablData,astar

class CarState:
    Null = -1
    WaitingRun = 1
    Waiting =2
    ActionEnd = 3


class Car:
    def __init__(self,id,startID,endID,vmax,ptime):
        self.id=id
        self.startID=startID
        self.endID=endID
        self.vmax=vmax
        self.ptime=ptime

        self.start=None
        self.end = None
        self.state = CarState.Null
        self.currentRoad = None
        self.Path=None
        self.PathPassing = list([])
    
        self.isComplate = False


    def GetStart(self):
        if self.start == None:
            self.start = golablData.GlobalData.Map[self.startID]
        return self.start

    def GetEnd(self):
        if self.start == None:
            self.start = golablData.GlobalData.Map[self.endID]
        return self.end
                 
    # 规划路径
    def PathPlanning(self,currentRoad):
        self.Path = astar.astar(golablData.GlobalData.Map,currentRoad,self.end)

    def NextRoad(self):
        return self.Path[0]
    
    def EnterNewRoad(self,road):
        if self.Path == None:
            self.PathPlanning(self.GetStart())

        if self.currentRoad == None:
            self.currentRoad = road
        else:
            self.PathPassing.append(self.currentRoad)

        temp = self.Path.pop(1)
        if temp.ID == self.currentRoad.ID:
            temp = self.Path.pop(1)
            
        self.currentRoad= temp
        # 当前道路和真实道路不等，重新规划
        if self.currentRoad.ID != road.ID:
            self.currentRoad=road
            self.PathPlanning(self.currentRoad)
        # 进入终止状态
        self.state=CarState.ActionEnd
      