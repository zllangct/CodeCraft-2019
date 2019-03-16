# _*_ coding: utf-8 _*_
import numpy as np
import logging
import Car


class Road:
    def __init__(self, id, len, vmax, chanCount, startID, endID, isBothway):
        self.Cross = {}
        self.Weight = {}

        self.ID = id
        self.len = len
        # 权重默认为长度
        self.Weight[startID] = len
        self.Weight[endID] = len
        self.vmax = vmax
        self.chanCount = chanCount
        self.startID = startID
        self.endID = endID
        self.isBothway = isBothway
        

        # 初始化车道里面的车车
        self.channels = {self.startID: list([]), self.endID: list([])}
        for roaddir in self.channels:
            for _ in range(0, self.chanCount):
                self.channels[roaddir].append([None for i in range(self.len)])

        # print("")

    def InitCross(self, ID, cross):
        self.Cross[ID] = cross

    # 返回车道数据 index 从1开始
    def GetChannel(self, dir, index):
        if index > self.chanCount or index > len(self.channels):
            logging.error("index wrong")
            return
        return self.channels[dir][index]

    def GetWeight(self,Dir):
        # TODO 此处权值需要重新计算
        return self.Weight[Dir]

    def GetLane(self,dir):
        return self.channels[dir]

    def MaxV(self, car):
        return min(car.vmax, self.vmax)

    def CheckingFrontCar(self, index, v, chan):
        for p in range(index+1, chan.len+v):
            if chan[p] != None:
                return True, p, chan[p].state
            return False, None, None

    def CheckingFrontCross(self, car, index, chan):
        if self.MaxV(car) + index >= self.len:
            return True
        return False

    def Move(self, car, index, s, chan):
        if s == 0:
            return
        chan[index] = None
        chan[index+s] = car

    def CarRun(self):
        # 遍历双向车道
        for roaddir in self.channels:
            # 遍历车道
            for chanIndex in range(0, self.chanCount):
                chan = self.channels[roaddir][chanIndex]
                # 遍历车辆,从出口向入口遍历
                for carIndex in range(0, len(chan))[::-1]:
                    # 遍历
                    car = chan[carIndex]
                    if car == None:
                        continue

                    # 检查前面是否有车辆
                    isFront, frontIndex, frontState = self.CheckingFrontCar(
                        carIndex, self.MaxV(car), chan)
                    # 检查是否出路口
                    isOut = self.CheckingFrontCross(car, carIndex, chan)

                    if not isFront:
                        # 没有前车
                        if not isOut:
                            # 没有前车 且 不出路口
                            self.Move(car, carIndex, self.MaxV(car), chan)
                            # 标记为终止状态
                            car.state = Car.CarState.ActionEnd
                        elif isOut:
                            # 没有前车 且 可以出路口
                            car.state = Car.CarState.WaitingRun
                    else:
                        # 有前车
                        if frontState == Car.CarState.ActionEnd:
                            # 如果前车终止
                            v = min(frontIndex-carIndex-1, self.MaxV(car))
                            self.Move(car, carIndex, v, chan)
                            car.state = Car.CarState.ActionEnd
                        elif frontState == Car.CarState.WaitingRun:
                            # 前车等待状态
                            car.state = Car.CarState.WaitingRun
    
    # 此时没有出路口的车辆
    def RunRest(self,cross):
        # 遍历车道
        for chanIndex in range(0, self.chanCount):
            chan = self.channels[cross.ID][chanIndex]
            # 遍历车辆,从出口向入口遍历
            for carIndex in range(0, len(chan))[::-1]:
                # 遍历
                car = chan[carIndex]
                if car == None:
                    continue

                # 检查前面是否有车辆
                isFront, frontIndex, _ = self.CheckingFrontCar(carIndex, self.MaxV(car), chan)
                if not isFront:
                    # 没有前车
                    self.Move(car, carIndex, self.MaxV(car), chan)
                    # 标记为终止状态
                    car.state = Car.CarState.ActionEnd
                else:
                    # 有前车
                    v = min(frontIndex-carIndex-1, self.MaxV(car))
                    self.Move(car, carIndex, v, chan)
                    car.state = Car.CarState.ActionEnd

    # 检查是否有向某个方向行驶的车辆
    def CheckingOutDir(self,crossID,dir):
        firstRow=list([])
        # 遍历所有车道，找到可以过路口的第一排等待车辆
        for chanIndex in range(0, self.chanCount):
            chan = self.channels[crossID][chanIndex]
            for carIndex in range(0, len(chan))[::-1]:
                car = chan[carIndex]
                if car != None and car.state == Car.CarState.Waiting:
                    if self.CheckingFrontCross(car,carIndex,chan):
                        firstRow.append(car.NextRoad().ID)
                    break
        if dir in firstRow:
            return True
        return False

    # 按照优先顺序获取可以出路口的车辆
    def GetCarWaiting(self,crossID):
        skip=list([])
        for row  in range(0,self.len):
            if len(skip)>=self.chanCount:
                break 
            for index in range(0,self.chanCount):
                if index in skip:
                    continue
                chan=self.GetChannel(crossID, index)
                car = chan[self.len-row]
                # 停止状态的车道 或者 有不出路口的首车 此车道不再遍历
                if car.state == Car.CarState.ActionEnd:
                    skip.append(index)
                    continue
                elif car.state == Car.CarState.Waiting:
                    if car != None :
                        return car,row,chan,self.CheckingFrontCross(car,self.len-row,chan)
                
        return None,None,None,None

    # 车辆进入道路
    def CarEnter(self,car,maxLen):
        targetChan=None
        targetIndex=None
        # 遍历车道
        for chanIndex in range(0, self.chanCount):
            chan = self.channels[self.endID][chanIndex]
            # 遍历车辆,从出口向入口遍历
            for carIndex in range(0, maxLen):
                if chan[carIndex]!=None:
                    break
                if chan[carIndex] == None:
                    targetChan=chan
                    targetIndex=carIndex
                    continue
            if targetChan!=None and targetIndex!=None:
                break
        # 如果没有位置可以停车，则返回失败
        if targetChan==None and targetIndex==None:
            return False
        chan[carIndex]=car
        car.EnterNewRoad(self)
        return True