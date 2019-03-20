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
        # 计划上路时间
        self.ptime=ptime
        # 上路时间
        self.stime=None 
        self.start=None
        self.end = None
        self.state = CarState.Null
        self.currentRoad = None
        self.Path=None
        self.PathTemp=[]
        self.PathPassing = list([])
        self.CurrentCross =None

        self.isComplate = False


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
        if actionType == "normal":
            self.waitingTime = 0

        self.Think()

    def PrintPath(self):
        for ii in self.PathTemp:
            sstr=""
            for pathNode in ii:
                sstr+=" "+str(pathNode.ID)
            print(sstr+"  当前节点：%d"%self.CurrentCross.ID+ "  当前道路：%d——%d" %(self.currentRoad.startID,self.currentRoad.endID))

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
                self.AddBlocking(self.currentRoad.ID)

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
            if p ==None:
                return
            self.Path= p 
            self.PathTemp.append(self.Path.copy())
            p=False
            if p:
                self.PrintPath()

    def NextCross(self):
        if len(self.Path)==0:
            return None,True
        # if self.CurrentCross.ID == self.Path[0].ID:
            # self.PrintPath()
        return self.Path[0],False
    
    def NextRoad(self):
        frontCross,end =self.NextCross()
        if end :
            return None
        
        return self.CurrentCross.GetRoadByEndID(frontCross.ID)
        

    def EnterNewRoad(self,road):
        if self.Path == None:
            self.PathPlanning(self.GetStart())

        if self.currentRoad != None:
            self.PathPassing.append(self.currentRoad)
            # 当前道路和真实道路不等，重新规划
            # if road.startID != self.currentRoad.endID:
            #     self.PathPlanning(self.currentRoad.GetEndCross(),True)
        
        self.CurrentCross =self.Path.pop(0)
        self.currentRoad= road
        self.location = "road"
        # 进入终止状态
        self.state=CarState.ActionEnd
        self.CarAction("normal")

        # nextCross =self.Path[0]
        # road = self.CurrentCross.GetRoadByEndID(nextCross.ID)
      