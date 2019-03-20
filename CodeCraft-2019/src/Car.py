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
        self.ID=id
        self.startID=startID
        self.endID=endID
        self.vmax=vmax
        # 计划上路时间
        self.ptime=ptime
        # 上路时间
        self.stime=None 
        self.start=None
        self.end = None
        self.state = CarState.Null
        self.CurrentRoad = None
        self.Path=None
        self.PathTemp=[]
        self.PathPassing = list([])
        self.CurrentCross =None

        self.isComplate = False

        self.ChanIndex = 0
        self.CarIndex = 0
        self.FrontDir = 0

        # 用于决策
        self.waitingTime = 0
        self.location = "garage"
        self.uniqueInfo ={}
        self.vpassing=[]
        self.vaverage=0

    def AddVPassing(self,v):
        if len(self.vpassing)>4:
            self.vpassing.pop(0)
        self.vpassing.append(v)
        self.vaverage = np.mean(self.vpassing)
        
    def ChangeState(self,state):
        if self.state != state:
            self.state = state

    def CarAction(self, actionType,*args):
        if actionType == "wait":
            self.waitingTime +=1
        else:
            self.waitingTime = 0

        self.Think()

    def PrintPath(self):
        for ii in self.PathTemp:
            sstr=""
            for pathNode in ii:
                sstr+=" "+str(pathNode.ID)
            print(sstr+"  当前节点：%d"%self.CurrentCross.ID+ "  当前道路：%d——%d" %(self.CurrentRoad.startID,self.CurrentRoad.endID))

    def AddBlocking(self,roadID):
        if not "block" in self.uniqueInfo:
            self.uniqueInfo["block"]=[]
        self.uniqueInfo["block"].append(roadID)

    def AddCongeestion(self,roadID):
        if not "congestion" in self.uniqueInfo:
            self.uniqueInfo["congestion"]=[]
        self.uniqueInfo["congestion"].append(roadID)

    def Think(self):
        if self.location == "cross":
            if self.waitingTime > 5:
                nextNode,end=self.NextCross()
                nextRoad= self.NextRoad() 
                if end:
                    return

                self.AddCongeestion(nextRoad.ID)
                self.AddBlocking(self.CurrentRoad.ID)

                self.PathPlanning(self.CurrentCross,True)

                self.uniqueInfo["block"]=[]
                self.uniqueInfo["congestion"]=[]
                    
                self.waitingTime=0

            # if len(self.vpassing) > 4 and self.vaverage < 1.5 :               
                
            #     nextRoad= self.NextRoad() 
            #     if nextRoad ==None:
            #         return
            #     self.AddBlocking(nextRoad.ID)
            #     self.PathPlanning(self.CurrentCross,True)

            #     self.uniqueInfo["block"]=[]
            #     self.uniqueInfo["congestion"]=[]

            nextRoad= self.NextRoad() 
            nextNode,end=self.NextCross()
            if end or nextRoad ==None:
                return
            if nextRoad.CarCount[nextNode.ID] > nextRoad.chanCount * nextRoad.len / 3:
                self.AddBlocking(nextRoad.ID)
                self.PathPlanning(self.CurrentCross,True)

                self.uniqueInfo["block"]=[]
                self.uniqueInfo["congestion"]=[]

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
            if len(self.PathPassing)>0:
                self.AddBlocking(self.PathPassing[-1].ID)
            
            p = astar.astar(golablData.GlobalData.Map,currentCross,self.GetEnd(),self,self.uniqueInfo)
            self.uniqueInfo["block"]=[]
            self.uniqueInfo["congestion"]=[]
            if p ==None:
                return
            self.Path= p 
            self.PathTemp.append(self.Path.copy())
            

            # debug TODO
            debugPrint=False
            if debugPrint:
                self.PrintPath()

            

    def NextCross(self):
        if self.CurrentCross and self.Path[0].ID == self.CurrentCross.ID:
            self.Path.pop(0)
        return self.Path[0]
    
    def NextRoad(self):
        frontCross,end =self.NextCross()
        if end :
            return None
        
        return self.CurrentCross.GetRoadByEndID(frontCross.ID)
    
    def Move(self,v):
        chan = self.CurrentRoad.GetChanel()
        chan[self.CarIndex] = None
        chan[self.CarIndex+v] = self

        self.AddVPassing(v)
        self.ChangeState(CarState.ActionEnd)
        self.CarAction("move")


    def EnterRoad(self,road,dir,chanIndex,carIndex):
        # 离开之前道路
        self.OutRoad()

        # 进入新道路
        self.CurrentRoad= road
        self.FrontDir = dir
        self.ChanIndex=chanIndex
        self.CarIndex = carIndex

        self.location = "road"
        self.CarAction("EnterRoad")    

        # 进入终止状态
        self.state=CarState.ActionEnd

    def OutRoad(self):
        if self.CurrentRoad != None:
            self.PathPassing.append(self.CurrentRoad)
        
        self.CurrentRoad= None
        self.FrontDir = None
        self.ChanIndex=None
        self.CarIndex = None

        self.location = "None"
        self.CarAction("OutRoad")

    def CheckingFrontCar(self):
        v=self.CurrentRoad.MaxV(self)
        chan = self.CurrentRoad.GetChanel(self.FrontDir,self.ChanIndex)
        s = v if self.CarIndex+v < self.CurrentRoad.len else self.CurrentRoad.len-self.CarIndex -1
        for p in range(self.CarIndex+1, self.CarIndex+s+1):
            if chan[p] != None:
                return True, p, chan[p].state
        return False, None, None
    
    def CheckingFrontCross(self):
        if self.CurrentRoad.MaxV(self) + self.CarIndex >= self.CurrentRoad.len:
            self.location="cross"
            return True

        self.location="road"
        return False
    
    def CheckingDestination(self):
        if len(self.Path)==0:
            return True
    
    def CarComplate(self):
        # 车辆离开最后道路
        self.CurrentRoad.CarOut(self)

        self.ChangeState(CarState.ActionEnd)
        self.isComplate=True 

        self.OutRoad()
            
        golablData.GlobalData.CarComplate(self)