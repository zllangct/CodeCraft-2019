#!/usr/bin/python
# -*- coding: utf-8 -*-
import textio 
from golablData import GlobalData
import CrossMap
import dijkstra
import time


def Process(car_path, road_path, cross_path, answer_path):
    # print("program start...")

    # Read input data
    input = textio.TextIO(car_path, road_path, cross_path, answer_path)
    GlobalData.roads, GlobalData.cars, GlobalData.crosses = input.ReadAll()

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
    RunV = 0.0
    CompPre = 0
    CarMax = 0

    GlobalData.State = 1
    frameCount = 0
    startTime = time.time()
    while GlobalData.State == 1:
        frameCount += 1
        GlobalData.CurrentTime = frameCount
        Frame()

        # 信息统计
        roadInfo = GlobalData.StateInfo["RoadInfo"]["CarInGarage"]
        roadCarCount = 0
        for _carCount in roadInfo.values():
            roadCarCount += _carCount
        GlobalData.Car_Road = roadCarCount
        print("当前道路中的车辆：%d" % roadCarCount)

        crossInfo = GlobalData.StateInfo["CrossInfo"]["CarInGarage"]
        crossCarCount = 0
        for _carCount in crossInfo.values():
            crossCarCount += _carCount
        GlobalData.Car_Garage = crossCarCount

        print("车库中的车辆：%d" % crossCarCount)

        print("到达终点车辆：%d" % GlobalData.ComplateCount)

        v = GlobalData.ComplateCount-CompPre
        if v > RunV:
            CarMax = roadCarCount
            RunV = v
        CompPre = GlobalData.ComplateCount

        print("到达量：%d  最大值：%d  最大值时道路承载量：%d  车辆综合检查: %d" % (v, RunV, CarMax, roadCarCount+crossCarCount+GlobalData.ComplateCount))

        print("程序运行时间：%f" % time.time().__sub__(startTime))

    # Write output data
    result = "#(carId,StartTime,RoadId...)\n"
    for car in GlobalData.cars:
        result += car.PathToString()

    GlobalData.Result = result
    input.Write(GlobalData.Result)


def Frame():
    print("调度时间:"+str(GlobalData.CurrentTime))

    HandleRoad()
    HandleCross()
    HandleGarage()


def HandleRoad():
    # # print("handle roads")
    for road in GlobalData.roads:
        road.CarRun(True)


def HandleCross():

    for cross in GlobalData.crosses:
        cross.CarRun()


def HandleGarage():
    max = 640 - GlobalData.Car_Road
    if GlobalData.Car_Road > 100:
        max = 0
    else:
        if max <= 0:
            max = 64

    every = int(max / 64.0)

    # every = 5000

    for cross in GlobalData.crosses:
        cross.GoRoad(every)
