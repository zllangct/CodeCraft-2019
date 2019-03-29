#!/usr/bin/python
# -*- coding:utf-8 -*- 
import numpy as np
import logging
import Car
import golablData
import copy,random


class Cross:

    # 前：0 左：1 右：2
    D = 0
    L = 1
    R = 2
    I2Dir = {
        0: {1: 1, 2: 0, 3: 2},
        1: {2: 1, 3: 0, 0: 2},
        2: {3: 1, 0: 0, 1: 2},
        3: {0: 1, 1: 0, 2: 2}
    }
    Dir2I = {
        0: {1: 1, 0: 2, 2: 3},
        1: {1: 2, 0: 3, 2: 0},
        2: {1: 3, 0: 0, 2: 1},
        3: {1: 0, 0: 1, 2: 2},
    }

    def __init__(self, ID, road1, road2, road3, road4):
        self.ID = ID
        self.RoadIDs = list([])
        self.RoadIDs.append(road1)
        self.RoadIDs.append(road2)
        self.RoadIDs.append(road3)
        self.RoadIDs.append(road4)
        self.Roads = None
        self.Neighbor = None
        
        self.CarsOut =[]
        self.Garage = []
        self.FrameComplete =False

        self.LastFrame = None
    
    def TempFrame(self):
        if self.LastFrame ==None: 
            self.LastFrame=copy.copy(self)

        self.LastFrame.FrameComplete = self.FrameComplete  

        self.LastFrame.Garage = copy.copy(self.Garage)
        self.LastFrame.CarsOut = copy.copy(self.CarsOut)

    def BackFrame(self):
        self.FrameComplete = self.LastFrame.FrameComplete

        self.Garage = self.LastFrame.Garage
        self.CarsOut = self.LastFrame.CarsOut

    def InitRoad(self, roadID, road):
        if self.Roads == None:
            self.Roads = {}

        self.Roads[roadID] = road

    def EnterGarage(self, car):
        self.Garage.append(car)

    def sortkey(self, item):
        return (item.ptime, item.ID)

    def GarageSort(self):
        self.Garage.sort(key=self.sortkey, reverse=True)

    def GetRoad(self, roadID):
        if roadID in self.RoadIDs:
            return True, self.Roads[roadID]
        else:
            return False, None

    

    def GetNeighbor(self):
        if self.Neighbor == None:
            self.Neighbor = {}
            for roadID in self.Roads.keys():
                road = self.Roads[roadID]
                if road.startID == self.ID:
                    self.Neighbor[roadID] = road.Cross[road.endID]
                elif road.endID == self.ID and road.isBothway == 1:
                    self.Neighbor[roadID] = road.Cross[road.startID]

        return self.Neighbor

    def GetRoadLength(self, targetID):
        for roadID in self.Roads:
            road = self.Roads[roadID]
            if road.endID == targetID or (road.startID == targetID and road.isBothway == 1):
                return road.len

    def GetDir(self, CurrentRoadID, targetRoadID):
        index_source = self.RoadIDs.index(CurrentRoadID)
        index_target = self.RoadIDs.index(targetRoadID)
        return self.I2Dir[index_source][index_target]

    def GetRoadByEndID(self, crossID):
        for road in self.Roads.values():
            if road.endID == crossID or road.isBothway == 1 and road.startID == crossID:
                return road
        return None

    def GetRoadByRoadID(self, roadID):
        for road in self.Roads.values():
            if road.ID == roadID:
                return road
        return None

    def GetRoadByDir(self, CurrentRoadID, dir):
        index_source = self.RoadIDs.index(CurrentRoadID)
        index_target = self.Dir2I[index_source][dir]
        id = self.RoadIDs[index_target]
        if id == -1:
            return None
        for road in self.Roads.values():
            if road.ID == id and (road.endID == self.ID or road.startID == self.ID and road.isBothway == 1):
                return road

    def CarRun(self,count):
        roadList = sorted(list(self.RoadIDs))
        # 从小到大遍历道路
        for roadIndex in range(0, len(roadList)):
            roadID = roadList[roadIndex]
            if roadID == -1 :
                continue
            road = self.GetRoadByRoadID(roadID)
            if road == None:
                continue
            # 调度这条道路
            canRun = True
            while canRun:
                # 获取调度车辆
                car_waiting, restLength = road.GetCarWaiting(self.ID)
                if car_waiting == None:
                    break
                
                # 检查是否出路口
                isOut = car_waiting.CheckingFrontCross()
                if not isOut:
                    road.ChanRun(road.GetChannel(self.ID,car_waiting.ChanIndex))
                    break

                # 检查是否到达终点
                isDestination = car_waiting.CheckingDestination()
                if isDestination:
                    _index =car_waiting.ChanIndex
                    car_waiting.CarComplete()
                    road.ChanRun(road.GetChannel(self.ID,_index))
                    continue

                targetCross = car_waiting.NextCross()
                targetRoad = self.GetRoadByEndID(targetCross.ID)

                # if targetRoad.CarCount[targetCross.ID] > targetRoad.chanCount * targetRoad.len / 1.5:  # 1.5 最佳
                #     car_waiting.AddBlocking(targetRoad.ID)
                #     car_waiting.PathPlanning(
                #         car_waiting.CurrentCross, True)

                #     targetCross = car_waiting.NextCross()
                #     targetRoad = self.GetRoadByEndID(targetCross.ID)

                targetRoadID = targetRoad.ID
                direction = self.GetDir(road.ID, targetRoadID)

                car_waiting.RefCount +=1
                # 检查冲突车辆
                if direction == self.D:
                    # 直行，优先不用检查
                    pass
                elif direction == self.L:
                    # 左转，检查直行车辆
                    roadR = self.GetRoadByDir(road.ID, self.R)
                    if roadR != None and roadR.CheckingOutDir(self, targetCross.ID):
                        # 如果有冲突，则暂时调度，切换到下一条道路            
                        break
                elif direction == self.R:
                    # 右转，检查左方直行车辆
                    roadL = self.GetRoadByDir(road.ID, self.L)
                    if roadL != None and roadL.CheckingOutDir(self, targetCross.ID):
                        # 如果有冲突，则暂时调度，切换到下一条道路
                        break
                    # 检查前方左转车辆
                    roadD = self.GetRoadByDir(road.ID, self.D)
                    if roadD != None and roadD.CheckingOutDir(self, targetCross.ID):
                        # 如果有冲突，则暂时调度，切换到下一条道路
                        break

                # 记录车辆所在车道
                chanIndex = car_waiting.ChanIndex
                # 没有冲突，行驶车辆,过路口
                ok,needWait = targetRoad.CarEnter(
                    car_waiting, targetCross.ID, restLength)
                if not ok and not needWait:
                    # 过路口失败，且不需要等待，说明对面车道拥堵，行驶到路口最后位置
                    car_waiting.Move(road.len-car_waiting.CarIndex-1)
                    # 调度一次该车道的其他车辆
                    road.ChanRun(road.GetChannel(self.ID,chanIndex))
                    car_waiting.CarAction("wait")
                    continue

                elif not ok and needWait:        
                    if count>20:
                        print("\ndead lock: %d \n" % self.ID)
                        return -1
                    break
                # 离开老路
                road.CarOut(car_waiting)
                # 调度一次该车道的其他车辆
                road.ChanRun(road.GetChannel(self.ID,chanIndex))

                  
        carWaiting=False
        for roadIndex in range(0, len(roadList)):
            roadID = roadList[roadIndex]
            if roadID == -1:
                continue
            road = self.GetRoadByRoadID(roadID)
            if road == None:
                continue
            carWaiting= road.CheckingHasActionWaiting(self.ID)
            if carWaiting:
                break
       

        if not carWaiting :
            self.FrameComplete =True

    def GoRoad(self, count):
        waitCars = list([])
        roadCount = len(self.Roads)
        roadBlock = list([])
        now = 0

        def _key(car):
            if car.ptime<=golablData.GlobalData.CurrentTime:
                ptime = 0
            else:
                ptime = car.ptime 
            return (ptime, car.ID)

        # self.Garage.sort(key=_key, reverse=True)
        random.shuffle(self.Garage)
        ready = []
        for car in self.Garage:
            if car.ptime <= golablData.GlobalData.CurrentTime:
                ready.append(car)
                if len(ready)== count:
                    break
        
        for car in ready:
            self.Garage.remove(car)
        
        ready.sort(key=lambda x:x.ID,reverse=True)

        while now < count and roadCount and len(ready) > 0:
            car = ready.pop(-1)
            # if car.ptime != ptime:
            #     waitCars.append(car)
            #     break
            if car.startID != self.ID:
                raise RuntimeError("invalid car") 
            if car.ID in golablData.GlobalData.ChangeTemp:
                car.AddBlocking(golablData.GlobalData.ChangeTemp[car.ID])
                car.PathPlanning(car.GetStart(), True)

            # 规划路线
            car.PathPlanning(car.GetStart(), True)
            crossTemp = car.Path[0]
            if crossTemp.ID == self.ID:
                car.Path.pop(0)
                crossTemp = car.Path[0]

            # car.CurrentCross = crossTemp
            road = self.GetRoadByEndID(crossTemp.ID)
            if road == None:
                raise RuntimeError("invalid car")

            if (road.ID in roadBlock):
                waitCars.append(car)
                continue

            # 判断是否合适上路
            value = 0.6 

            count, maxCount = road.GetEmpty(crossTemp.ID, car)
            if count / maxCount < value:  
                roadCount -= 1 
                roadBlock.append(road.ID)
                waitCars.append(car)
                break 

            # 进入道路
            canEnter,neenWait = road.CarEnter(car, crossTemp.ID)
            if not canEnter or neenWait:
                roadCount -= 1
                roadBlock.append(road.ID)
                waitCars.append(car)
                break

            # 上路时间
            car.stime = golablData.GlobalData.CurrentTime
            self.CarsOut.append(car.ID)
            now += 1
            continue

        for w in waitCars[::-1]:
            self.Garage.append(w)

        for w in ready:
            self.Garage.append(w)
        
