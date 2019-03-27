#!/usr/bin/python
# -*- coding: utf-8 -*-
import textio 
from golablData import GlobalData
import CrossMap
import dijkstra
import time
import copy,sys

def Process(car_path, road_path, cross_path, answer_path):
    # print("program start...")
    sys.setrecursionlimit(1000000)
    # Read input data
    input = textio.TextIO(car_path, road_path, cross_path, answer_path)
    GlobalData.roads, GlobalData.cars, GlobalData.crosses = input.ReadAll()

    for road in GlobalData.roads:
        GlobalData.roadsByID[road.ID]=road
    for car in GlobalData.cars:
        GlobalData.carsByID[car.ID]=car
    for cross in GlobalData.crosses: 
        GlobalData.crossesByID[cross.ID]=cross

    # GenMap
    for road in GlobalData.roads:
        count = 0
        for cross in GlobalData.crosses:
            if cross.ID == road.startID:
                cross.InitRoad(road.endID, road)
                road.InitCross(cross.ID, cross)
                count += 1
            elif cross.ID == road.endID:
                road.InitCross(cross.ID, cross)
                cross.InitRoad(road.startID, road)
                count += 1

            if count >= 2:
                break

    GlobalData.Map = CrossMap.CrossMap(GlobalData.crosses)

    # calculate distance
    GlobalData.DistancePre = dijkstra.CalDistance(GlobalData.Map)

    # cars enter garage
    for car in GlobalData.cars:
        start = car.GetStart()
        start.EnterGarage(car)

    # garage sort
    for cross in GlobalData.crosses:
        cross.GarageSort()
    # Main logic loop
    Loop()

    # checking
    for car in GlobalData.cars:
        if car.isComplate ==False:
            print(car.ID)

    timeTotal = 0 
    # Write output data
    result = "#(carId,StartTime,RoadId...)\n"
    for car in GlobalData.cars:
        result += car.PathToString()
        timeTotal+= car.etime-car.ptime
    GlobalData.Result = result
    print("总调度时间：%d" % timeTotal)


    input.Write(GlobalData.Result)


def Loop():
    RunV = 0.0
    CompPre = 0
    CarMax = 0

    GlobalData.State = 1
    GlobalData.CurrentTime = 0
    startTime = time.time()

    while GlobalData.State == 1:

        for road in GlobalData.roads:
            road.TempFrame()
        for cross in GlobalData.crosses:
            cross.TempFrame()
        GlobalData.TempFrame()

        GlobalData.CurrentTime += 1
        status = Frame()
        if status==-1:
            # 直行回滚操作
            for road in GlobalData.roads:
                road.BackFrame()
            for car in GlobalData.cars:
                car.BackFrame()
            for cross in GlobalData.crosses:
                cross.BackFrame()
            GlobalData.BackFrame()


        # 信息统计
        roadCarCount = 0
        for road in GlobalData.roads:
            for d in road.CarCount.values():
                roadCarCount+=d
        GlobalData.Car_Road = roadCarCount

        crossCarCount = 0
        for cross in GlobalData.crosses:
            crossCarCount+=len(cross.Garage)
        GlobalData.Car_Garage = crossCarCount

        v = GlobalData.ComplateCount-CompPre
        if v > RunV:
            CarMax = roadCarCount
            RunV = v
        CompPre = GlobalData.ComplateCount

        print("当前道路中的车辆：%d" % roadCarCount)
        print("车库中的车辆：%d" % crossCarCount)
        print("到达终点车辆：%d" % GlobalData.ComplateCount)
        print("到达量：%d  最大值：%d  最大值时道路承载量：%d  车辆综合检查: %d" % (v, RunV, CarMax, roadCarCount+crossCarCount+GlobalData.ComplateCount))
        print("程序运行时间：%f" % time.time().__sub__(startTime))
        print("调度时间:"+str(GlobalData.CurrentTime))
       

def Frame():    
    status=HandleRoad()
    if status==-1:return status
    status=HandleCross()
    if status==-1:return status
    status=HandleGarage()
    if status==-1:return status
        
    return 0

def HandleRoad():
    for road in GlobalData.roads:
        status=road.CarRun(True)
        if status==-1:return status
    return 0


def HandleCross():
    for cross in GlobalData.crosses:
        cross.FrameComplete=False

    complete = len(GlobalData.crosses)
    count=0
    while(complete>0):
        count+=1
        for cross in GlobalData.crosses:
            if cross.FrameComplete:
                continue
            status=cross.CarRun(count)
            if status==-1:return status
            if cross.FrameComplete:
                complete-=1


def HandleGarage():
    max = 500 - GlobalData.Car_Road
    if GlobalData.Car_Road > 500:
        max = 0
    else:
        if max <= 0:
            max = 64

    every = int(max / 64.0)

    # if GlobalData.ComplateCount > len(GlobalData.cars) * 0.8:
    #     every+=100

    for cross in GlobalData.crosses:
        status=cross.GoRoad(every)
        if status==-1:return status
