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
        3:{1:1,2:0,2:2},
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
        return item.ptime

    def GarageSort(self):
        self.Garage=self.Garage.sort(key=self.sortkey)

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
                return road.GetWeight(targetID)
    
    def GetDir(self,currentRoadID,targetRoadID):
        index_source = self.RoadIDs.index(currentRoadID)
        index_target = self.RoadIDs.index(targetRoadID)
        return self.I2Dir[index_source][index_target]

    def GetRoadByEndID(self,crossID):
        for road in self.Roads:
            if road.endID == crossID or road.isBothway == 1 and road.startID == crossID:
                return road
        return None

    def GetRoadByDir(self,currentRoadID,dir):
        index_source = self.RoadIDs.index(currentRoadID)
        index_target = self.Dir2I[index_source][dir]
        return self.Roads[self.RoadIDs[index_target]]

    def ThroughCross(self,car,restLength,sourceRoad,targetRoad):
        # 下一段路可行驶的最大路程
        maxLen= targetRoad.MaxV(car)-restLength
        return targetRoad.CarEnter(car,maxLen)

    def CarRun(self):
        roadList = list(self.RoadIDs.sort(reverse=True))
        # 从小到大遍历道路
        while len(roadList)>0:
            for roadIndex in roadList:
                road=self.Roads[roadIndex]
                # 获取调度车辆 
                car_waiting,restLength,chan,out = road.GetCarWaiting(self.ID)
                if car_waiting == None:
                    roadList.pop(roadIndex)
                    continue
                if not out:
                    road.Move(car_waiting,road.len-restLength,road.MaxV(car_waiting),chan)
                    car_waiting.state = Car.CarState.ActionEnd
                    continue

                targetRoad,end =car_waiting.NextRoad() 
                if end :
                    chan[road.len-restLength]=None
                    car_waiting.state = Car.CarState.ActionEnd
                    car_waiting.isComplate=True
                    golablData.GlobalData.CarComplate(car_waiting)
                targetRoadID = targetRoad.ID
                direction = self.GetDir(road.ID, targetRoadID)
                # 检查冲突车辆
                if direction == self.D:
                    # 直行，优先不用检查
                    pass
                elif direction == self.L:
                    # 左转，检查直行车辆
                    roadR = self.GetRoadByDir(road.ID,self.R)
                    if roadR.CheckingOutDir(self.ID,targetRoadID):
                        # 如果有冲突，则暂时调度，切换到下一条道路
                        continue
                elif direction == self.R:
                    # 右转，检查左方直行车辆
                    roadL = self.GetRoadByDir(road.ID,self.L)
                    if roadL.CheckingOutDir(self.ID,targetRoadID):
                        # 如果有冲突，则暂时调度，切换到下一条道路
                        continue
                    # 检查前方左转车辆
                    roadD = self.GetRoadByDir(road.ID,self.D)
                    if roadL.CheckingOutDir(self.ID,targetRoadID):
                        # 如果有冲突，则暂时调度，切换到下一条道路
                        continue
                # 没有冲突，行驶车辆 TODO
                ok= self.ThroughCross(car_waiting,restLength,road,targetRoad)
                if not ok :
                    continue

        # 行驶剩余等待状态车辆
        for road in self.Roads:
            road.RunRest(self)

    def GoRoad(self):
        canEnter =True
        while len(self.Garage)>0 and self.Garage[0].ptime>=golablData.GlobalData.CurrentTime and canEnter:
            car = self.Garage[0]
            # 规划路线
            car.PathPlanning(car.GetStart())
            crossTemp = car.Path.pop(0)
            if crossTemp.ID != self.ID:
                logging.error("car go road wrong,invalid start cross") 
                continue
            road = self.GetRoadByEndID(crossTemp.ID)
            if road == None:
                logging.error("car go road wrong,invalid start cross")
                continue
            canEnter=road.CarEnter(car,road.MaxV(car))