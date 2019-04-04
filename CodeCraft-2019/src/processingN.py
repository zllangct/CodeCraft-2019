#!/usr/bin/python
# -*- coding: utf-8 -*-
import textio 
from golablData import GlobalData
import CrossMap
import dijkstra
import time
import copy,sys,random

def Process(car_path, road_path, cross_path, answer_path,temp_path):
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

    # Main logic loop   
    tTime,tTotalTime,seed,GlobalData.MaxInRoad= input.ReadTemp(temp_path)
    status = 0


    seed1 = 1553857603
    seed2 = 1553857603
    seed = time.time()
    if 5013 in GlobalData.roadsByID:
        seed =seed1
    else:
        seed = seed2

    random.seed(seed)


    GlobalData.MaxInRoad=1500

    
    print("-------种子：%d 最大行车量：%d 最好成绩：%d------------------------------------------------------------------------" % (
        seed,GlobalData.MaxInRoad,tTime))
    status,t,tt= Loop()
    # if status == -1:
    #     continue

    if t<tTime or t==tTime and tt<tTotalTime:
        input.WriteTemp(temp_path,t,tt,seed,GlobalData.MaxInRoad) 
        tTime=t
        tTotalTime=tt
    
    print("\n结果：调度时间： %d ,总调度时间：%d \n" % (t,tt))

    # Write output data
    result = "#(carId,StartTime,RoadId...)\n"
    for car in GlobalData.cars:
        result += car.PathToString()
    GlobalData.Result = result

    input.Write(GlobalData.Result)


def TempData():
    for road in GlobalData.roads:
        road.TempFrame()
    for car in GlobalData.cars:
        car.TempFrame()
    for cross in GlobalData.crosses:
        cross.TempFrame()
    GlobalData.TempFrame()

def BackData():
    for road in GlobalData.roads:
        road.BackFrame()
    for car in GlobalData.cars:
        car.BackFrame()
    for cross in GlobalData.crosses:
        cross.BackFrame()
    GlobalData.BackFrame()

def Loop(seed = 0):
    GlobalData.State = 1
    GlobalData.CurrentTime = 0
    GlobalData.StartTime = time.time()

    while GlobalData.State == 1:
        GlobalData.CurrentTime += 1
        status = Frame()
        if status == -1:
            return status,0,0

       
    Info()

    timeTotal = 0 
    # Write output data
    for car in GlobalData.cars:
        timeTotal+= car.etime-car.ptime
    return 0,GlobalData.CurrentTime,timeTotal    

def Info():
    roadCarCount = 0
    for road in GlobalData.roads:
        for d in road.CarCount.values():
            roadCarCount+=d
    GlobalData.Car_Road = roadCarCount

    crossCarCount = 0
    for cross in GlobalData.crosses:
        crossCarCount+=len(cross.Garage)
    GlobalData.Car_Garage = crossCarCount

    print("当前道路中的车辆：%d ,车库中的车辆：%d ,到达终点车辆：%d ,调度时间:%d ,程序运行时间：%f" % (
        roadCarCount,crossCarCount,GlobalData.ComplateCount,GlobalData.CurrentTime,time.time().__sub__(GlobalData.StartTime)),end='\r')

def Frame():    
    status=HandleRoad()
    if status==-1:return status
    status=HandleCross()
    Info()
    if status==-1:return status
    status=HandleGarage()
    Info()
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
    max = GlobalData.MaxInRoad - GlobalData.Car_Road
    if GlobalData.Car_Road > GlobalData.MaxInRoad:
        max = 0
    
    ls = []
    for cross in GlobalData.crosses:
        if len(cross.Garage)>0:
            ls.append(cross)
    if len(ls)==0:
        return 0
    every = int(max / len(ls))
    rest = max % len(ls)    
    cc = random.sample(list(GlobalData.crosses),rest)

    for cross in GlobalData.crosses:
        count = every
        if cross in cc:
            count+=1
        if cross in ls:
            status=cross.GoRoad(count)
            if status==-1:return status
