# _*_ coding: utf-8 _*_
import numpy as np
import logging
import Car,golablData


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
        self.Cars = {}
        self.CarCount ={self.startID: 0, self.endID: 0}

        # 初始化车道里面的车车
        self.channels = {self.startID: list([]), self.endID: list([])}
        for roaddir in self.channels:
            for _ in range(0, self.chanCount):
                self.channels[roaddir].append([None for i in range(self.len)])

        # print("")

    def InitCross(self, ID, cross):
        self.Cross[ID] = cross

    def GetEndCross(self):
        return self.Cross[self.endID]

    def GetStartCross(self):
        return self.Cross[self.startID]

    # 返回车道数据 index 从1开始
    def GetChannel(self, dir, index):
        if index >= self.chanCount or  not (dir in self.channels):
            logging.error("index wrong")
            return
        return self.channels[dir][index]

    def GetEmpty(self,dir,car):
        maxLen=self.MaxV(car)
        count=0
        maxCount = self.chanCount * maxLen
        # 遍历车道
        for chanIndex in range(0, self.chanCount):
            chan = self.channels[dir][chanIndex]
            # 遍历车辆,从出口向入口遍历
            for carIndex in range(0, maxLen):
                if chan[carIndex]!=None:
                    break
                if chan[carIndex] == None:
                    count+=1
                    continue

        return count,maxCount

    def GetCarPosition(self,car):
        if car.ID in self.Cars:
            return self.Cars[car.ID]
                      

    # 计算道路权值
    def GetWeight(self,source,target,car):
        # 初始权值
        initWeight = self.len*2

        # 承载量
        if self.CarCount[target.ID] > self.len*self.chanCount * 0.6:
            initWeight += int(self.CarCount[target.ID] - self.len*self.chanCount / 2.0) ** 2

        # 车道数量
        initWeight += (5 - self.chanCount) * 3

        # 车道中的最慢车速
        for chan in self.channels[target.ID]:
            minV = self.vmax
            for _car in chan:
                if _car != None and _car.vmax < minV:
                    minV = _car.vmax
            initWeight+=self.vmax-minV
        
        return initWeight

    def RoadPrint(self,dir,temp=False):
        if not golablData.GlobalData.Debug and not temp:
            return
        start = self.startID if dir==self.endID else self.endID
        print("=======起点：%d========道路ID：%d=====终点：%d==========================================================" % (start,self.ID,dir))
        for _chanIndex in range(0, self.chanCount):
            _sstr = "车道 [ %d ] :" %(_chanIndex+1)
            _chan = self.channels[self.endID][_chanIndex]
            for _car in _chan:
                _sstr += ("% 6d" %_car.ID) if _car != None else "% 6d" % 0
            print(_sstr)
        print("======================================================================================================")
    
    def GetLane(self,dir):
        return self.channels[dir]

    def MaxV(self, car):
        return min(car.vmax, self.vmax)

    def CarRun(self,isNewFrame=False):
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

                    if isNewFrame:
                        car.state=Car.CarState.WaitingRun

                    if car.state == Car.CarState.ActionEnd:
                        continue
                        
                    # 检查前面是否有车辆
                    isFront, frontIndex, frontState = car.CheckingFrontCar()
                    # 检查是否出路口
                    isOut = car.CheckingFrontCross()

                    # 检查是否到达终点
                    isDestination = car.CheckingDestination()
                    if isDestination and not isFront and isOut:
                        car.CarComplete()

                    # 正常行驶
                    if not isFront:
                        # 没有前车
                        if not isOut:
                            # 没有前车 且 不出路口
                            car.Move(self.MaxV(car))
                            # 标记为终止状态
                            car.ChangeState(Car.CarState.ActionEnd)
                        elif isOut:
                            # 没有前车 且 可以出路口
                            car.ChangeState(Car.CarState.WaitingRun)
                    else:
                        # 有前车
                        if frontState == Car.CarState.ActionEnd:
                            # 如果前车终止
                            v = min(frontIndex-carIndex-1, self.MaxV(car))
                            car.Move( v)
                        elif frontState == Car.CarState.WaitingRun:
                            # 前车等待状态
                            car.ChangeState(Car.CarState.WaitingRun)
                    

        # 遍历双向车道,统计道路信息
        carCount=0
        for roaddir in self.channels:
            self.RoadPrint(roaddir,False)
            # 遍历车道
            for chanIndex in range(0, self.chanCount):
                chan = self.channels[roaddir][chanIndex]
                # 遍历车辆,从出口向入口遍历
                for carIndex in range(0, len(chan))[::-1]:
                     # 遍历
                    car = chan[carIndex]
                    if car != None:
                        carCount+=1

        if not "CarInGarage" in golablData.GlobalData.StateInfo["RoadInfo"]:
            golablData.GlobalData.StateInfo["RoadInfo"]["CarInGarage"]={}

        golablData.GlobalData.StateInfo["RoadInfo"]["CarInGarage"][self.ID] = carCount               

    # 检查是否有向某个方向行驶的车辆
    def CheckingOutDir(self,crossID,dir):
        car,_ = self.GetCarWaiting(crossID)
        if car ==None:
            return False
        nextCross=car.NextCross()
        if nextCross !=None and nextCross.ID == dir:
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
                car = chan[self.len-row-1]
                # 停止状态的车道 或者 有不出路口的首车 此车道不再遍历
                if car != None :
                    if car.state == Car.CarState.ActionEnd :
                        skip.append(index)
                        continue
                    elif car.state == Car.CarState.WaitingRun:
                        return car,row
                
        return None,None

    # 车辆进入道路
    def CarEnter(self,car,dir,restLength=0):
        # 计算在新道路上能行驶的最大距离
        tmaxv=self.MaxV(car)
        maxLen= tmaxv-restLength if tmaxv-restLength>0 else 0

        targetChan=None
        targetIndex=None
        # 遍历车道
        for chanIndex in range(0, self.chanCount):
            chan = self.channels[dir][chanIndex]
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

        chan[targetIndex]=car
        self.CarCount[dir]+=1
        self.Cars[car.ID] = (dir,chanIndex,targetIndex)

        car.EnterRoad(self,dir,chanIndex,targetIndex)
        return True
        
    def CarOut(self,car):
        dir,chanIndex,index=self.GetCarPosition(car)
        self.channels[dir][chanIndex][index]=None
        self.CarCount[dir]-=1

        self.Cars.pop(car.ID)