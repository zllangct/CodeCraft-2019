#!/usr/bin/python
# -*- coding: utf-8 -*-
import textio 
from golablData import GlobalData
from Global import Global
import CrossMap
import dijkstra
import time
import copy,sys
import simulator.processing as PP 

sys.setrecursionlimit(1000000)
simulate =False

def Process(car_path, road_path, cross_path, answer_path):
    # print("program start...")

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
    # simulator
    PP.Process(car_path, road_path, cross_path, answer_path)

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

    if simulate:
        PP_timeTotal = 0
        for car in PP.GlobalData.cars:
            PP_timeTotal+= car.etime-car.ptime
        GlobalData.Result = result
        print("PP总调度时间：%d" % PP_timeTotal)

    input.Write(GlobalData.Result)


def Loop():
    RunV = 0.0
    CompPre = 0
    CarMax = 0

    PP_RunV = 0.0
    PP_CompPre = 0
    PP_CarMax = 0

    GlobalData.State = 1
    GlobalData.CurrentTime = 0
    startTime = time.time()

    PP.GlobalData.State = 1
    PP.GlobalData.CurrentTime = 0
    
    while GlobalData.State == 1:
        GlobalData.CurrentTime += 1
        Global.FrameTime = GlobalData.CurrentTime

        PP.GlobalData.CurrentTime += 1
        PP.Global.FrameTime = GlobalData.CurrentTime

        Frame()

        # 信息统计
        roadInfo = GlobalData.StateInfo["RoadInfo"]["CarInGarage"]
        roadCarCount = 0
        for _carCount in roadInfo.values():
            roadCarCount += _carCount
        GlobalData.Car_Road = roadCarCount

        crossInfo = GlobalData.StateInfo["CrossInfo"]["CarInGarage"]
        crossCarCount = 0
        for _carCount in crossInfo.values():
            crossCarCount += _carCount
        GlobalData.Car_Garage = crossCarCount
        # simulator ------------------------------------------
        if simulate:
            PP_roadInfo = PP.GlobalData.StateInfo["RoadInfo"]["CarInGarage"]
            PP_roadCarCount = 0
            for _carCount in PP_roadInfo.values():
                PP_roadCarCount += _carCount
            PP.GlobalData.Car_Road = PP_roadCarCount

            PP_crossInfo = PP.GlobalData.StateInfo["CrossInfo"]["CarInGarage"]
            PP_crossCarCount = 0
            for _carCount in PP_crossInfo.values():
                PP_crossCarCount += _carCount
            PP.GlobalData.Car_Garage = PP_crossCarCount
        # ------------------------------------------
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
       
        # simulator ------------------------------------------
        if simulate:
            PP_v = PP.GlobalData.ComplateCount-PP_CompPre
            if PP_v > PP_RunV:
                PP_CarMax = PP_roadCarCount
                PP_RunV = PP_v
            PP_CompPre = PP.GlobalData.ComplateCount

            print("PP当前道路中的车辆：%d" % PP_roadCarCount)
            print("PP车库中的车辆：%d" % PP_crossCarCount)
            print("PP到达终点车辆：%d" % PP.GlobalData.ComplateCount)
            print("PP到达量：%d  最大值：%d  最大值时道路承载量：%d  车辆综合检查: %d" % (PP_v, PP_RunV, PP_CarMax, PP_roadCarCount+crossCarCount+PP.GlobalData.ComplateCount))
            print("PP程序运行时间：%f" % time.time().__sub__(startTime))
            print("PP调度时间:"+str(PP.GlobalData.CurrentTime))

def Frame():    
    HandleRoad()
    if simulate:
        PP.HandleRoad()
        Checking()
    HandleCross()
    if simulate:
        PP.HandleCross()
        Checking()
        Checking_car()
    HandleGarage()
    if simulate:
        PP.HandleGarage()
        Checking()

def Checking_car():
    for carID in GlobalData.carsByID:
        car1= GlobalData.carsByID[carID]
        car2=PP.GlobalData.carsByID[carID]
        if car1.etime != car2.etime:
            print(carID)

def Checking():
    for roadID in GlobalData.roadsByID: 
        road1=GlobalData.roadsByID[roadID]
        road2=PP.GlobalData.roadsByID[roadID]
        if  road1.GetHash() != road2.GetHash():
            for roaddir in road1.channels:
                road1.RoadPrint(roaddir,True)
                road2.RoadPrint(roaddir,True)
                
            # raise RuntimeError("not sync") 

def HandleRoad():
    # # print("handle roads")
    for road in GlobalData.roads:
        road.CarRun(True)


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
            cross.CarRun(count)
            if cross.FrameComplete:
                complete-=1


def HandleGarage():
    max = 700 - GlobalData.Car_Road
    if GlobalData.Car_Road > 700:
        max = 0
    else:
        if max <= 0:
            max = 64

    every = int(max / 64.0)

    # if GlobalData.ComplateCount > len(GlobalData.cars) * 0.8:
    #     every+=100

    for cross in GlobalData.crosses:
        cross.GoRoad(every)
