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

    def GetWeight(self,Dir):
        # TODO 此处权值需要重新计算
        return self.Weight[Dir]

    def RoadPrint(self,dir,temp=False):
        if not golablData.GlobalData.Debug and not temp:
            return
        start = self.startID if dir==self.endID else self.endID
        print("=======起点：%d========道路ID：%d=====终点：%d==========================================================" % (start,self.ID,dir))
        for _chanIndex in range(0, self.chanCount):
            _sstr = "车道 [ %d ] :" %(_chanIndex+1)
            _chan = self.channels[self.endID][_chanIndex]
            for _car in _chan:
                _sstr += ("% 6d" %_car.id) if _car != None else "% 6d" % 0
            print(_sstr)
        print("======================================================================================================")
    
    def GetLane(self,dir):
        return self.channels[dir]

    def MaxV(self, car):
        return min(car.vmax, self.vmax)

    def CheckingFrontCar(self, index, v, chan):
        chanLen=len(chan)
        s = v if index+v < chanLen else chanLen-index -1
        for p in range(index+1, index+s+1):
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
        if index + s >= len(chan):
            print("move array out of index")
        # if golablData.GlobalData.Debug:
        #     print("car %d move : %d" %(car.id,s))
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
                    isFront, frontIndex, frontState = self.CheckingFrontCar(carIndex, self.MaxV(car), chan)
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
                    

        # 遍历双向车道,统计道路信息
        carCount=0
        for roaddir in self.channels:
            self.RoadPrint(roaddir)
            # 遍历车道
            for chanIndex in range(0, self.chanCount):
                chan = self.channels[roaddir][chanIndex]
                # 遍历车辆,从出口向入口遍历
                for carIndex in range(0, len(chan))[::-1]:
                     # 遍历
                    car = chan[carIndex]
                    if car != None:
                        carCount+=1

        if not "CarCount" in golablData.GlobalData.StateInfo["RoadInfo"]:
            golablData.GlobalData.StateInfo["RoadInfo"]["CarCount"]={}

        golablData.GlobalData.StateInfo["RoadInfo"]["CarCount"][self.ID] = carCount               

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

                # 检查是否出路口
                isOut = self.CheckingFrontCross(car, carIndex, chan)
                # 检查前面是否有车辆
                isFront, frontIndex, _ = self.CheckingFrontCar(carIndex, self.MaxV(car), chan)
                if not isFront:
                    if isOut:
                        self.Move(car, carIndex, self.len-carIndex-1, chan)
                    else:
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
        # 遍历所有车道，找到可以过路口的第一排等待车辆
        for chanIndex in range(0, self.chanCount):
            chan = self.channels[crossID][chanIndex]
            for carIndex in range(0, len(chan))[::-1]:
                car = chan[carIndex]
                if car != None and car.state == Car.CarState.WaitingRun:
                    if self.CheckingFrontCross(car,carIndex,chan):
                        nextCross,end=car.NextRoad()
                        if nextCross !=None and nextCross.ID == dir and not end:
                            return True
                        else:
                            continue
                    break
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
                if chan == None:
                    chan=self.GetChannel(crossID, index)
                    print("GetCarWaiting wrong")
                    continue
                car = chan[self.len-row-1]
                # 停止状态的车道 或者 有不出路口的首车 此车道不再遍历
                if car != None :
                    if car.state == Car.CarState.ActionEnd or not self.CheckingFrontCross(car,self.len-row,chan):
                        skip.append(index)
                        continue
                    elif car.state == Car.CarState.WaitingRun:
                        return car,row,chan,index
                
        return None,None,None,None

    # 车辆进入道路
    def CarEnter(self,car,maxLen,dir):
        targetChan=None
        targetIndex=None
        # 遍历车道
        for chanIndex in range(0, self.chanCount):
            chan = self.channels[dir][chanIndex]
            # 遍历车辆,从出口向入口遍历
            for carIndex in range(0, maxLen+1):
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
        return True
        
    def CarOut(self,dir,chanIndex,index):
        self.channels[dir][chanIndex][index]=None
        self.CarCount[dir]-=1