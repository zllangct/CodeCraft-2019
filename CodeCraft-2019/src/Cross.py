# _*_ coding: utf-8 _*_
import numpy as np
import logging
import Car,golablData
           

class Cross:
    
    # 前：0 左：1 右：2
    D=0
    L=1
    R=2
    I2Dir={
        0:{1:1,2:0,3:2},
        1:{2:1,3:0,0:2},
        2:{3:1,0:0,1:2},
        3:{0:1,1:0,2:2}
    }
    Dir2I= {
        0:{1:1,0:2,2:3},
        1:{1:2,0:3,2:0},
        2:{1:3,0:0,2:1},
        3:{1:0,0:1,2:2},
    }
    def __init__(self,ID,road1,road2,road3,road4):
        self.ID=ID
        self.RoadIDs = list([])
        self.RoadIDs.append(road1)
        self.RoadIDs.append(road2)
        self.RoadIDs.append(road3)
        self.RoadIDs.append(road4)

        self.Garage = list([])

        self.Roads = None
        self.Neighbor = None
    # 初始化道路对象
    def InitRoad(self,roadID,road):
        if self.Roads == None:
            self.Roads={}

        self.Roads[roadID]=road

    def EnterGarage(self,car):
        self.Garage.append(car)

    def sortkey(self,item):
        return (item.ptime,item.id)

    def GarageSort(self):
        self.Garage.sort(key=self.sortkey,reverse=True)

    def GetRoad(self,roadID):
        if roadID in self.RoadIDs:
            return True,self.Roads[roadID]
        else:
            return False,None

    def GetNeighbor(self):
        if self.Neighbor == None:
            self.Neighbor={}
            for roadID in self.Roads.keys():
                road=self.Roads[roadID]
                if road.startID == self.ID:
                    self.Neighbor[roadID]=road.Cross[road.endID]
                elif road.endID == self.ID and road.isBothway==1:
                    self.Neighbor[roadID]=road.Cross[road.startID]

        return self.Neighbor
    
    def GetRoadLength(self,targetID):
        for roadID in self.Roads:
            road=self.Roads[roadID]
            if road.endID == targetID or (road.startID == targetID and road.isBothway ==1):
                return road.len
    
    def GetDir(self,currentRoadID,targetRoadID):
        index_source = self.RoadIDs.index(currentRoadID)
        index_target = self.RoadIDs.index(targetRoadID)
        return self.I2Dir[index_source][index_target]

    def GetRoadByEndID(self,crossID):
        for road in self.Roads.values():
            if road.endID == crossID or road.isBothway == 1 and road.startID == crossID:
                return road
        return None

    def GetRoadByRoadID(self,roadID):
        for road in self.Roads.values():
            if road.ID == roadID:
                return road
        return None

    def GetRoadByDir(self,currentRoadID,dir):
        index_source = self.RoadIDs.index(currentRoadID)
        index_target = self.Dir2I[index_source][dir]
        id = self.RoadIDs[index_target]
        if id == -1:
            return None
        for road in self.Roads.values():
            if road.ID == id:
                return road

    def CarRun(self):
        roadList =sorted(list(self.RoadIDs))
        handleLen=len(self.Roads)
        handledList=list([])
       
        

        # 从小到大遍历道路
        while handleLen>0:
            for roadIndex in range(0,len(roadList)):
                roadID = roadList[roadIndex]
                if roadID == -1 or roadID in handledList:
                    continue
                road=self.GetRoadByRoadID(roadID)
                if road ==None:
                    handleLen-=1
                    handledList.append(roadID)
                    continue
                # 调度这条道路 
                canRun = True
                while canRun:
                    # 获取调度车辆 
                    car_waiting,restLength,chan,chanIndex = road.GetCarWaiting(self.ID)
                    if car_waiting == None:
                        handleLen-=1
                        break
           
                    targetCross,end =car_waiting.NextCross() 
                    if end :
                        chan[road.len-restLength-1]=None
                        car_waiting.state = Car.CarState.ActionEnd
                        car_waiting.isComplate=True
                        if car_waiting.currentRoad != None:
                            car_waiting.PathPassing.append(car_waiting.currentRoad)
                            car_waiting.currentRoad = None
                        golablData.GlobalData.CarComplate(car_waiting)
                        continue
                    if targetCross.ID == self.ID:
                        car_waiting.Path.pop(0)
                        targetCross,end =car_waiting.NextCross()

                    targetRoad = self.GetRoadByEndID(targetCross.ID)
                    targetRoadID = targetRoad.ID
                    direction = self.GetDir(road.ID, targetRoadID)
                    # 检查冲突车辆
                    if direction == self.D:
                        # 直行，优先不用检查
                        pass
                    elif direction == self.L:
                        # 左转，检查直行车辆
                        roadR = self.GetRoadByDir(road.ID,self.R)
                        if roadR !=None and roadR.CheckingOutDir(self.ID,targetRoadID):
                            # 如果有冲突，则暂时调度，切换到下一条道路
                            break
                    elif direction == self.R:
                        # 右转，检查左方直行车辆
                        roadL = self.GetRoadByDir(road.ID,self.L)
                        if roadL!=None and roadL.CheckingOutDir(self.ID,targetRoadID):
                            # 如果有冲突，则暂时调度，切换到下一条道路
                            break
                        # 检查前方左转车辆
                        roadD = self.GetRoadByDir(road.ID,self.D)
                        if roadD != None and roadD.CheckingOutDir(self.ID,targetRoadID):
                            # 如果有冲突，则暂时调度，切换到下一条道路
                            break
                    # 没有冲突，行驶车辆,过路口
                    tmaxv=targetRoad.MaxV(car_waiting)
                    maxLen= tmaxv-restLength if tmaxv-restLength>0 else 0
                    ok= targetRoad.CarEnter(car_waiting,maxLen,targetCross.ID)
                    if not ok :
                        # 过路口失败，说明对面车道拥堵，行驶到路口最后位置
                        carIndex = road.len-restLength-1
                        road.Move(car_waiting, carIndex, road.len-carIndex-1, chan)
                        if road.len-carIndex-1 == 0:
                            car_waiting.CarAction("wait")
                        car_waiting.state = Car.CarState.ActionEnd
                        break

                    road.CarOut(self.ID,chanIndex,road.len-restLength-1)
                    car_waiting.EnterNewRoad(targetRoad) 

        # 行驶剩余等待状态车辆
        for road in self.Roads.values():
            road.RunRest(self)

    def GoRoad(self,count):
        waitCars =list([])
        roadCount = len(self.Roads)
        roadBlock= list([])
        now=0
        while now < count and roadCount and len(self.Garage)>0 and self.Garage[-1].ptime<=golablData.GlobalData.CurrentTime:
            car = self.Garage.pop(-1)
            # 规划路线
            car.PathPlanning(car.GetStart())
            crossTemp = car.Path[0]
            car.CurrentCross = self

            if crossTemp.ID == self.ID:
                car.Path.pop(0)
                crossTemp = car.Path[0]

            road = self.GetRoadByEndID(crossTemp.ID)
            if road == None:
                logging.error("car go road wrong,invalid start cross")
                continue

            if (road.ID in roadBlock):
                waitCars.append(car)
                continue

            canEnter=road.CarEnter(car,road.MaxV(car),crossTemp.ID)
            if not canEnter:
                roadCount-=1
                roadBlock.append(road.ID)
                waitCars.append(car)
                continue

            car.EnterNewRoad(road)
            car.location = "road"
            now+=1

        for w in waitCars[::-1]:
            self.Garage.append(w)    
        
        if not "CarCount" in golablData.GlobalData.StateInfo["CrossInfo"]:
            golablData.GlobalData.StateInfo["CrossInfo"]["CarCount"]={}

        golablData.GlobalData.StateInfo["CrossInfo"]["CarCount"][self.ID] = len(self.Garage)