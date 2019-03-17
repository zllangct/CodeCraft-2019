# _*_ coding: utf-8 _*_
import numpy as np
import logging
import golablData,astar

class CarState:
    Null = -1
    WaitingRun = 1
    ActionEnd = 2


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
        self.PathTemp=None
        self.PathPassing = list([])
    
        self.isComplate = False


    def GetStart(self):
        if self.start == None:
            self.start = golablData.GlobalData.Map[self.startID]
        return self.start

    def GetEnd(self):
        if self.end == None:
            self.end = golablData.GlobalData.Map[self.endID]
        return self.end
                 
    # 规划路径
    def PathPlanning(self,currentCross,rePlan = False):
        if self.Path ==None or rePlan:
            self.Path = astar.astar(golablData.GlobalData.Map,currentCross,self.GetEnd())
            self.PathTemp = self.Path

    def NextRoad(self):
        if len(self.Path)==0:
            return None,True
        return self.Path[0],False
    
    def EnterNewRoad(self,road):
        if self.Path == None:
            self.PathPlanning(self.GetStart())

        if self.currentRoad != None:
            self.PathPassing.append(self.currentRoad)
            # 当前道路和真实道路不等，重新规划
            # if road.startID != self.currentRoad.endID:
            #     self.PathPlanning(self.currentRoad.GetEndCross(),True)
        
        self.Path.pop(0)
        self.currentRoad= road
        
        # 进入终止状态
        self.state=CarState.ActionEnd
      