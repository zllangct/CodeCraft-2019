#!/usr/bin/python
# -*- coding: utf-8 -*-
import numpy as np
import logging
import golablData
import astar
import copy


class CarState:
    Null = -1
    WaitingRun = 1
    ActionEnd = 2


class Car:
    def __init__(self, id, startID, endID, vmax, ptime):
        # 不变的
        self.ID = id
        self.startID = startID
        self.endID = endID
        self.vmax = vmax
        self.ptime = ptime
        self.start = None
        self.end = None

        # 变化的
        self.stime = None
        self.etime = None
        self.state = CarState.Null
        self.isComplate = False
        self.ChanIndex = 0
        self.CarIndex = 0
        self.FrontDir = 0
        self.waitingTime = 0
        self.location = "garage"
        self.CurrentRoad = None
        self.CurrentCross = None
        self.RefCount =0
        
        self.Path = None
        self.PathPassing = []
        self.CrossPassing = []
        self.uniqueInfo = {}       
        self.vpassing = []  
           
        self.LastFrame = None
        self.LastFrameTime = -1
    
    def TempFrame(self):
        if self.LastFrame ==None: 
            self.LastFrame=copy.copy(self)

        self.LastFrame.stime =        self.stime  
        self.LastFrame.etime =        self.etime  
        self.LastFrame.state =        self.state 
        self.LastFrame.isComplate =   self.isComplate 
        self.LastFrame.ChanIndex =    self.ChanIndex  
        self.LastFrame.CarIndex =     self.CarIndex 
        self.LastFrame.FrontDir =     self.FrontDir  
        self.LastFrame.waitingTime =  self.waitingTime 
        self.LastFrame.location =     self.location 
        self.LastFrame.CurrentRoad =  self.CurrentRoad 
        self.LastFrame.CurrentCross = self.CurrentCross
        self.LastFrame.LastFrameTime = self.LastFrameTime
        self.LastFrame.RefCount =self.RefCount

        self.LastFrame.Path = copy.copy(self.Path)
        self.LastFrame.PathPassing = copy.copy(self.PathPassing)
        self.LastFrame.CrossPassing = copy.copy(self.CrossPassing)
        self.LastFrame.uniqueInfo = copy.deepcopy(self.uniqueInfo)
        self.LastFrame.vpassing = copy.copy(self.vpassing)


    def BackFrame(self):
            self.stime =        self.LastFrame.stime  
            self.etime =        self.LastFrame.etime  
            self.state =        self.LastFrame.state 
            self.isComplate =   self.LastFrame.isComplate 
            self.ChanIndex =    self.LastFrame.ChanIndex  
            self.CarIndex =     self.LastFrame.CarIndex 
            self.FrontDir =     self.LastFrame.FrontDir  
            self.waitingTime =  self.LastFrame.waitingTime 
            self.location =     self.LastFrame.location 
            self.CurrentRoad =  self.LastFrame.CurrentRoad 
            self.CurrentCross = self.LastFrame.CurrentCross
            self.LastFrameTime = self.LastFrame.LastFrameTime
            self.RefCount =     self.LastFrame.RefCount

            self.Path = self.LastFrame.Path
            self.PathPassing = self.LastFrame.PathPassing
            self.CrossPassing = self.LastFrame.CrossPassing
            self.uniqueInfo =  self.LastFrame.uniqueInfo
            self.vpassing = self.LastFrame.vpassing

    def PathToString(self):
        sstr = "("+str(self.ID)+"," + str(self.stime)
        for road in self.PathPassing:
            sstr += (","+str(road.ID))
        sstr += ")\n"
        return sstr

    def AddVPassing(self, v):
        if len(self.vpassing) > 4:
            self.vpassing.pop(0)
        self.vpassing.append(v)
        self.vaverage = np.mean(self.vpassing)

    def ChangeState(self, state):
        if self.state != state:
            self.state = state

    def CarAction(self, actionType, *args):
        if actionType == "wait":
            self.waitingTime += 1
        else:
            self.waitingTime = 0

    def AddBlocking(self, roadID):
        if not "block" in self.uniqueInfo:
            self.uniqueInfo["block"] = []
        self.uniqueInfo["block"].append(roadID)

    def AddCongeestion(self, roadID):
        if not "congestion" in self.uniqueInfo:
            self.uniqueInfo["congestion"] = []
        self.uniqueInfo["congestion"].append(roadID)

    def GetStart(self):
        if self.start == None:
            self.start = golablData.GlobalData.Map[self.startID]
        return self.start

    def GetEnd(self):
        if self.end == None:
            self.end = golablData.GlobalData.Map[self.endID]
        return self.end

    # 规划路径
    def PathPlanning(self, currentCross, rePlan=False):
        if self.Path == None or rePlan:
            if len(self.PathPassing) > 0:
                for path in self.PathPassing:
                    self.AddBlocking(path.ID)
                # self.AddBlocking(self.PathPassing[-1].ID)

            p = astar.astar(golablData.GlobalData.Map, currentCross,
                            self.GetEnd(), self, self.uniqueInfo)
            self.uniqueInfo["block"] = []
            self.uniqueInfo["congestion"] = []
            if p == None:
                return
            self.Path = p

    def NextCross(self):
        if len(self.Path) > 0:
            if self.CurrentCross and self.Path[0].ID == self.CurrentCross.ID:
                self.Path.pop(0)
            if len(self.Path) > 0:
                return self.Path[0]
        return None

    def NextRoad(self):
        frontCross = self.NextCross()
        if frontCross == None:
            return None
        return self.CurrentCross.GetRoadByEndID(frontCross.ID)

    def Move(self, v):
        chan = self.CurrentRoad.GetChannel(self.FrontDir, self.ChanIndex)
        chan[self.CarIndex] = None
        self.CarIndex += v
        chan[self.CarIndex] = self
        self.CurrentRoad.Cars[self.ID] = (
            self.FrontDir, self.ChanIndex, self.CarIndex)

        self.AddVPassing(v)
        self.ChangeState(CarState.ActionEnd)

        self.CarAction("move")


    def EnterRoad(self, road, dir, chanIndex, carIndex):
        # 离开之前道路
        self.OutRoad()

        # 进入新道路
        self.CurrentRoad = road
        self.FrontDir = dir
        self.ChanIndex = chanIndex
        self.CarIndex = carIndex
        self.CurrentCross = road.Cross[dir]

        self.location = "road"
        self.CarAction("EnterRoad")

        # 进入终止状态
        self.state = CarState.ActionEnd
        self.RefCount =0

    def OutRoad(self):
        if self.CurrentRoad != None:
            self.PathPassing.append(self.CurrentRoad)
        if self.CurrentCross !=None:
            self.CrossPassing.append(self.CurrentCross)

        self.CurrentRoad = None
        self.FrontDir = None
        self.ChanIndex = None
        self.CarIndex = None

        self.location = "None"
        self.CarAction("OutRoad")

    def CheckingFrontCar(self):
        v = self.CurrentRoad.MaxV(self)
        chan = self.CurrentRoad.GetChannel(self.FrontDir, self.ChanIndex)
        s = v if self.CarIndex+v < self.CurrentRoad.len else self.CurrentRoad.len-self.CarIndex - 1
        for p in range(self.CarIndex+1, self.CarIndex+s+1):
            if chan[p] != None:
                return True, p, chan[p].state
        return False, None, None

    def CheckingFrontCross(self):
        if self.CurrentRoad.MaxV(self) + self.CarIndex >= self.CurrentRoad.len:
            self.location = "cross"
            return True

        self.location = "road"
        return False

    def CheckingDestination(self):
        if self.endID == self.CurrentCross.ID:
            return True
        return False

    def CarComplete(self):
        # 车辆离开最后道路
        self.CurrentRoad.CarOut(self)

        self.ChangeState(CarState.ActionEnd)
        self.isComplate = True

        self.OutRoad()
        self.etime = golablData.GlobalData.CurrentTime
        self.LastFrameTime = golablData.GlobalData.CurrentTime
        golablData.GlobalData.CarComplete(self)
